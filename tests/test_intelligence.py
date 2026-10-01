from __future__ import annotations

import pandas as pd
import pytest

from src.intelligence.grepi_index import calculate_grepi_index, get_top_performing_micro_markets
from src.intelligence.valuation_avm import calculate_fairvalue_avm, get_valuation_gauge
from src.intelligence.financial_engine import calculate_capyield_model, run_irr_projection
from src.intelligence.corridor_quadrant import classify_corridor_quadrants, map_locality_to_corridor
from src.real_estate_analysis import load_real_estate_data, clean_real_estate_data


@pytest.fixture
def sample_real_estate_data() -> pd.DataFrame:
    raw_df = load_real_estate_data()
    return clean_real_estate_data(raw_df)


def test_grepi_index_computation(sample_real_estate_data: pd.DataFrame):
    grepi_df = calculate_grepi_index(sample_real_estate_data)
    assert not grepi_df.empty
    assert {"rank", "Locality", "grepi_score", "institutional_grade", "inventory_depth"}.issubset(
        set(grepi_df.columns)
    )
    # Check score bounds
    assert (grepi_df["grepi_score"] >= 20.0).all()
    assert (grepi_df["grepi_score"] <= 100.0).all()
    # Check top performers
    top_5 = get_top_performing_micro_markets(sample_real_estate_data, limit=5)
    assert len(top_5) <= 5


def test_fairvalue_avm_confidence_bands(sample_real_estate_data: pd.DataFrame):
    avm = calculate_fairvalue_avm(
        area_sqft=1800,
        bhk=3,
        locality="Sector 56",
        property_type="Apartment",
        df_reference=sample_real_estate_data,
        ml_predicted_price=18_000_000,  # 1.8 Cr
    )

    assert "fair_market_value" in avm
    assert "liquidation_value" in avm
    assert "premium_value" in avm

    # P15 liquidation must be less than FMV, and FMV must be less than P85 premium
    assert avm["liquidation_value"] < avm["fair_market_value"]
    assert avm["fair_market_value"] < avm["premium_value"]
    assert avm["liquidity_volatility_score"] > 0


def test_valuation_gauge_under_and_overpriced():
    fmv = 15_000_000  # 1.5 Cr
    # Bargain asking price: 1.3 Cr
    gauge_cheap = get_valuation_gauge(13_000_000, fmv)
    assert gauge_cheap["diff_pct"] < 0
    assert "Bargain" in gauge_cheap["status"]

    # Overpriced asking price: 1.8 Cr
    gauge_expensive = get_valuation_gauge(18_000_000, fmv)
    assert gauge_expensive["diff_pct"] > 0
    assert "Overpriced" in gauge_expensive["status"] or "Premium" in gauge_expensive["status"]


def test_capyield_financial_engine():
    model = calculate_capyield_model(
        property_price=20_000_000,  # 2 Cr
        monthly_rent=65_000,
    )
    assert model["gross_yield_pct"] > 0
    assert model["cap_rate_pct"] > 0
    assert model["cap_rate_pct"] < model["gross_yield_pct"]  # Net cap rate is less than gross yield
    assert model["price_to_rent_ratio"] > 0


def test_irr_projection_modeling():
    irr_results = run_irr_projection(
        property_price=20_000_000,
        holding_period_years=5,
        annual_appreciation_pct=8.0,
    )
    assert irr_results["terminal_asset_value_cr"] > 2.0
    assert irr_results["annualized_irr_pct"] > 0
    assert len(irr_results["schedule_df"]) == 5


def test_corridor_quadrants(sample_real_estate_data: pd.DataFrame):
    corridors_df = classify_corridor_quadrants(sample_real_estate_data)
    assert not corridors_df.empty
    assert "Corridor" in corridors_df.columns
    assert "quadrant" in corridors_df.columns
    assert any("Prime Institutional" in q for q in corridors_df["quadrant"])

    # Test individual mapping
    c1 = map_locality_to_corridor("Sector 54 Golf Course Road")
    assert "Golf Course Road" in c1
