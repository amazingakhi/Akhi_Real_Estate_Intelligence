import pandas as pd

from src.real_estate_analysis import (
    clean_real_estate_data,
    load_real_estate_data,
    normalize_property_type,
)


def test_dataset_loads_and_has_expected_columns():
    df = load_real_estate_data()

    assert isinstance(df, object)
    assert not df.empty
    assert {"Price", "Area", "Rate per sqft", "BHK_Count", "Locality"}.issubset(set(df.columns))


def test_dataset_cleaning_converts_price_and_rate_to_numeric():
    df = load_real_estate_data()
    cleaned = clean_real_estate_data(df)

    assert cleaned["Price"].dtype.kind in {"i", "f"}
    assert cleaned["Rate per sqft"].dtype.kind in {"i", "f"}
    assert cleaned["BHK_Count"].dtype.kind in {"i", "f"}
    assert cleaned["Price"].notna().all()


def test_dataset_cleaning_removes_invalid_bhk_outliers():
    df = load_real_estate_data()
    cleaned = clean_real_estate_data(df)

    assert (cleaned["BHK_Count"] <= 10).all()
    assert (cleaned["Area"] <= 25_000).all()
    assert (cleaned["Price"] <= 800_000_000).all()


def test_normalize_property_type_collapses_listing_titles():
    assert normalize_property_type("3 BHK Apartment in M3M Golf Estate") == "Apartment"
    assert normalize_property_type("4 BHK Independent Floor") == "Independent Floor"
    assert normalize_property_type("Residential Plot") == "Plot"
    assert normalize_property_type("Luxury Villa") == "Villa"


def test_clean_adds_listing_title_and_typed_category():
    df = pd.DataFrame(
        {
            "Price": ["1,200,000"],
            "Area": [1100],
            "Rate per sqft": ["12,000"],
            "BHK_Count": [2],
            "Locality": ["Sector 56"],
            "Property Type": ["2 BHK Apartment in Demo Society"],
        }
    )
    cleaned = clean_real_estate_data(df)
    assert cleaned.iloc[0]["Property Type"] == "Apartment"
    assert "Apartment in Demo Society" in cleaned.iloc[0]["Listing Title"]
