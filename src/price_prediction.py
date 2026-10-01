from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

try:
    from .real_estate_analysis import clean_real_estate_data, load_real_estate_data
except ImportError:  # pragma: no cover
    from real_estate_analysis import clean_real_estate_data, load_real_estate_data

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "property_price_model.joblib"
MODEL_PATH.parent.mkdir(exist_ok=True)


def prepare_model_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_real_estate_data(df).copy()
    cleaned = cleaned[["Price", "Area", "BHK_Count", "Locality", "Property Type"]].dropna().copy()
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    cleaned["Area"] = pd.to_numeric(cleaned["Area"], errors="coerce")
    cleaned["BHK_Count"] = pd.to_numeric(cleaned["BHK_Count"], errors="coerce")
    return cleaned.reset_index(drop=True)


def train_property_price_model(df: pd.DataFrame) -> dict:
    prepared = prepare_model_data(df)

    if prepared.empty:
        raise ValueError("Model data is empty after cleaning.")

    X = prepared.drop(columns=["Price"])
    y = prepared["Price"]

    if len(prepared) >= 10:
        test_size = 0.2
    else:
        test_size = min(0.5, max(0.2, 2 / len(prepared)))

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
    )

    numerical_features = ["Area", "BHK_Count"]
    categorical_features = ["Locality", "Property Type"]

    numerical_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_features="sqrt",
        min_samples_leaf=2,
        random_state=42,
        n_jobs=1,
    )

    pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("model", model)]
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    r2_metric = r2_score(y_test, predictions)
    if np.isnan(r2_metric):
        r2_metric = 0.0

    metrics = {
        "mae": mean_absolute_error(y_test, predictions),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2_score": float(r2_metric),
    }

    return {"model": pipeline, "metrics": metrics}


def save_model() -> str:
    df = load_real_estate_data()
    result = train_property_price_model(df)
    import joblib

    joblib.dump(result["model"], MODEL_PATH)
    _load_model.cache_clear()
    return str(MODEL_PATH)


@lru_cache(maxsize=1)
def _load_model():
    import joblib

    if not MODEL_PATH.exists():
        save_model()
    return joblib.load(MODEL_PATH)


def predict_price(area: float, bhk: int, locality: str, property_type: str) -> float:
    model = _load_model()
    sample = pd.DataFrame(
        [
            {
                "Area": area,
                "BHK_Count": bhk,
                "Locality": locality,
                "Property Type": property_type,
            }
        ]
    )
    return float(model.predict(sample)[0])


if __name__ == "__main__":
    result = train_property_price_model(load_real_estate_data())
    print("Model trained successfully.")
    print(result["metrics"])
    print("Saved model path:", save_model())
    print("Example prediction:", predict_price(1200, 3, "Sector 56", "Apartment"))
