import pandas as pd

from src.price_prediction import prepare_model_data, train_property_price_model


def test_prepare_model_data_returns_expected_columns():
    df = pd.DataFrame(
        {
            "Price": [1000000, 2000000],
            "Area": [800, 1000],
            "BHK_Count": [2, 3],
            "Locality": ["Sector 56", "Sector 72"],
            "Property Type": ["Apartment", "Apartment"],
        }
    )

    prepared = prepare_model_data(df)

    assert {"Price", "Area", "BHK_Count", "Locality", "Property Type"}.issubset(set(prepared.columns))
    assert prepared["Price"].notna().all()


def test_train_property_price_model_returns_metrics():
    df = pd.DataFrame(
        {
            "Price": [1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000],
            "Area": [800, 1000, 1300, 1500, 1800, 2000, 2200, 2400, 2600, 3000],
            "BHK_Count": [2, 3, 3, 4, 3, 4, 4, 5, 5, 5],
            "Locality": ["Sector 56", "Sector 72", "Sector 57", "Sector 75", "Sector 56", "Sector 72", "Sector 57", "Sector 75", "Sector 56", "Sector 72"],
            "Property Type": ["Apartment", "Apartment", "Villa", "Villa", "Apartment", "Villa", "Apartment", "Villa", "Apartment", "Villa"],
        }
    )

    result = train_property_price_model(df)

    assert "model" in result
    assert "metrics" in result
    assert isinstance(result["metrics"]["r2_score"], float)
    assert result["metrics"]["mae"] >= 0
