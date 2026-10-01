from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "gurugram_real_estate.csv"

try:
    from config.settings import (
        MAX_AREA_SQFT,
        MAX_PRICE_INR,
        MAX_RATE_PER_SQFT,
        MIN_AREA_SQFT,
        MIN_PRICE_INR,
        MIN_RATE_PER_SQFT,
    )
except ImportError:  # pragma: no cover
    MIN_AREA_SQFT, MAX_AREA_SQFT = 80, 25_000
    MIN_PRICE_INR, MAX_PRICE_INR = 300_000, 800_000_000
    MIN_RATE_PER_SQFT, MAX_RATE_PER_SQFT = 2_000, 120_000


def load_real_estate_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the Gurgaon real-estate dataset from the project raw-data folder."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {file_path}")

    return pd.read_csv(file_path)


def normalize_property_type(value: object) -> str:
    """Map noisy listing titles to a small product-type set for filters and ML."""
    text = str(value or "").strip().lower()
    if not text or text in {"nan", "none"}:
        return "Other"
    if "plot" in text or "land" in text:
        return "Plot"
    if "villa" in text:
        return "Villa"
    if "penthouse" in text:
        return "Penthouse"
    if "studio" in text:
        return "Studio"
    if "independent floor" in text or "builder floor" in text:
        return "Independent Floor"
    if "duplex" in text or "floor" in text:
        return "Independent Floor"
    if "apartment" in text or "flat" in text or "bhk" in text:
        return "Apartment"
    return "Other"


def clean_real_estate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean listings: numerics, type labels, and Gurugram-plausible outlier caps."""
    cleaned = df.copy()

    cleaned = cleaned.drop_duplicates()

    columns_to_clean = ["Price"]
    if "Rate per sqft" in cleaned.columns:
        columns_to_clean.append("Rate per sqft")

    for column in columns_to_clean:
        if column in cleaned.columns:
            cleaned[column] = (
                cleaned[column]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.strip()
            )

    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    if "Rate per sqft" in cleaned.columns:
        cleaned["Rate per sqft"] = pd.to_numeric(cleaned["Rate per sqft"], errors="coerce")
    cleaned["BHK_Count"] = pd.to_numeric(cleaned["BHK_Count"], errors="coerce")
    cleaned["Area"] = pd.to_numeric(cleaned["Area"], errors="coerce")

    # Values above 10 are malformed BHK counts in this dataset, not valid homes.
    cleaned.loc[cleaned["BHK_Count"] > 10, "BHK_Count"] = pd.NA

    if "Property Type" in cleaned.columns:
        cleaned["Listing Title"] = cleaned["Property Type"].astype(str)
        cleaned["Property Type"] = cleaned["Listing Title"].map(normalize_property_type)

    required_columns = ["Price", "Area", "BHK_Count"]
    if "Rate per sqft" in cleaned.columns:
        required_columns.append("Rate per sqft")

    cleaned = cleaned.dropna(subset=required_columns)

    cleaned = cleaned[
        (cleaned["Area"] >= MIN_AREA_SQFT)
        & (cleaned["Area"] <= MAX_AREA_SQFT)
        & (cleaned["Price"] >= MIN_PRICE_INR)
        & (cleaned["Price"] <= MAX_PRICE_INR)
    ]
    if "Rate per sqft" in cleaned.columns:
        cleaned = cleaned[
            (cleaned["Rate per sqft"] >= MIN_RATE_PER_SQFT)
            & (cleaned["Rate per sqft"] <= MAX_RATE_PER_SQFT)
        ]

    return cleaned.reset_index(drop=True)


def build_summary(df: pd.DataFrame) -> dict:
    """Create a small summary of the cleaned dataset for reporting and dashboard use."""
    avg_rate_per_sqft = (
        round(float(df["Rate per sqft"].mean()), 2)
        if "Rate per sqft" in df.columns
        else None
    )

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "avg_price": round(float(df["Price"].mean()), 2),
        "avg_rate_per_sqft": avg_rate_per_sqft,
        "avg_area": round(float(df["Area"].mean()), 2),
        "avg_bhk": round(float(df["BHK_Count"].mean()), 2),
        "locality_count": int(df["Locality"].nunique()),
    }


if __name__ == "__main__":
    raw_df = load_real_estate_data()
    cleaned_df = clean_real_estate_data(raw_df)
    summary = build_summary(cleaned_df)

    print("Dataset loaded successfully.")
    print("Rows:", cleaned_df.shape[0])
    print("Columns:", cleaned_df.shape[1])
    print("Summary:", summary)
