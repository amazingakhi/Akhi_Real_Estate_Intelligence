from __future__ import annotations

import re
from typing import Any
import pandas as pd


CORRIDOR_MAPPINGS: dict[str, list[str]] = {
    "Golf Course Road (Prime Blue-Chip)": [
        "Golf Course Road",
        "Sector 42",
        "Sector 43",
        "Sector 53",
        "Sector 54",
        "DLF Phase 1",
        "DLF Phase 5",
    ],
    "Golf Course Extension & SPR (High-Velocity Growth)": [
        "Golf Course Extension Road",
        "Sector 56",
        "Sector 57",
        "Sector 58",
        "Sector 59",
        "Sector 60",
        "Sector 61",
        "Sector 62",
        "Sector 63",
        "Sector 65",
        "Sector 66",
        "Sector 67",
        "Sector 68",
        "Southern Peripheral Road",
    ],
    "Dwarka Expressway (Infrastructure Corridor)": [
        "Dwarka Expressway",
        "Sector 102",
        "Sector 103",
        "Sector 104",
        "Sector 106",
        "Sector 108",
        "Sector 109",
        "Sector 110",
        "Sector 111",
        "Sector 112",
        "Sector 113",
        "Sector 99",
        "Sector 88",
    ],
    "New Gurgaon (Emerging Value Hub)": [
        "Sector 81",
        "Sector 82",
        "Sector 83",
        "Sector 84",
        "Sector 85",
        "Sector 86",
        "Sector 89",
        "Sector 90",
        "Sector 91",
        "Sector 92",
        "Sector 93",
        "Sector 95",
        "New Gurgaon",
    ],
    "Sohna Road & South Gurugram (Rental Yield Corridors)": [
        "Sohna Road",
        "Sector 47",
        "Sector 48",
        "Sector 49",
        "Sector 50",
        "Sector 70",
        "Sector 71",
        "Sector 72",
        "South City 2",
    ],
    "Cyber Hub & MG Road (Commercial Core)": [
        "MG Road",
        "Cyber City",
        "DLF Phase 2",
        "DLF Phase 3",
        "DLF Phase 4",
        "Sushant Lok",
        "Sector 27",
        "Sector 28",
    ],
}


def map_locality_to_corridor(locality: str) -> str:
    loc_clean = str(locality).strip().lower()

    for corridor, members in CORRIDOR_MAPPINGS.items():
        for member in members:
            if member.lower() in loc_clean:
                return corridor

    sector_match = re.search(r"Sector\s*(\d+)", locality, flags=re.IGNORECASE)
    if sector_match:
        sec = int(sector_match.group(1))
        if sec in range(42, 45) or sec in (53, 54):
            return "Golf Course Road (Prime Blue-Chip)"
        if sec in range(56, 70):
            return "Golf Course Extension & SPR (High-Velocity Growth)"
        if sec in range(99, 114) or sec in (88,):
            return "Dwarka Expressway (Infrastructure Corridor)"
        if sec in range(80, 96):
            return "New Gurgaon (Emerging Value Hub)"
        if sec in range(47, 52) or sec in range(70, 75):
            return "Sohna Road & South Gurugram (Rental Yield Corridors)"
        if sec in range(24, 30):
            return "Cyber Hub & MG Road (Commercial Core)"

    return "Other Gurugram Micro-Markets"


def classify_corridor_quadrants(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies Gurugram real estate inventory into the 4 Quadrants:
    - Quadrant I: Institutional Blue-Chip (High Capital, Steady Appreciation)
    - Quadrant II: High-Velocity Growth (Rapid Infra Expansion, High Upside)
    - Quadrant III: High-Yield Cash Flow (Strong Corporate Tenant Base)
    - Quadrant IV: Value Accumulators (Affordable Entry, Long-Term Upside)
    """
    if df.empty:
        return pd.DataFrame()

    df_tagged = df.copy()
    df_tagged["Corridor"] = df_tagged["Locality"].apply(map_locality_to_corridor)

    grouped = (
        df_tagged.groupby("Corridor")
        .agg(
            inventory=("Price", "count"),
            median_rate_sqft=("Rate per sqft", "median"),
            mean_rate_sqft=("Rate per sqft", "mean"),
            median_price_cr=("Price", lambda p: p.median() / 10_000_000),
            price_std=("Rate per sqft", lambda s: s.std() if len(s) > 1 else 0.0),
        )
        .reset_index()
    )

    def assign_quadrant(row: pd.Series) -> dict[str, str]:
        corridor = row["Corridor"]
        rate = row["median_rate_sqft"]
        if "Golf Course Road" in corridor or rate > 18_000:
            return {
                "quadrant": "Quadrant I: Prime Institutional",
                "tagline": "Blue-Chip Wealth Preservation",
                "risk_profile": "Ultra-Low Risk",
                "yield_outlook": "2.8% - 3.4% (Capital Focus)",
                "growth_outlook": "7% - 9% Steady Compounder",
            }
        elif "Extension" in corridor or "Dwarka" in corridor:
            return {
                "quadrant": "Quadrant II: High-Velocity Growth",
                "tagline": "Infrastructure & Capital Acceleration",
                "risk_profile": "Moderate Risk / High Upside",
                "yield_outlook": "3.5% - 4.2% (Balanced)",
                "growth_outlook": "10% - 14% High Velocity",
            }
        elif "Sohna Road" in corridor or "Cyber Hub" in corridor:
            return {
                "quadrant": "Quadrant III: High-Yield Cash Flow",
                "tagline": "Corporate Rental Demand Powerhouse",
                "risk_profile": "Low to Moderate Risk",
                "yield_outlook": "4.2% - 5.1% (High Yield)",
                "growth_outlook": "6% - 8% Steady",
            }
        else:
            return {
                "quadrant": "Quadrant IV: Value Accumulator",
                "tagline": "Emerging Entry Point",
                "risk_profile": "Moderate Risk",
                "yield_outlook": "3.8% - 4.5%",
                "growth_outlook": "8% - 11% Long-Term",
            }

    quadrant_meta = grouped.apply(assign_quadrant, axis=1, result_type="expand")
    grouped = pd.concat([grouped, quadrant_meta], axis=1)

    grouped["median_rate_sqft"] = grouped["median_rate_sqft"].round(0).astype(int)
    grouped["median_price_cr"] = grouped["median_price_cr"].round(2)

    return grouped.sort_values(by="median_rate_sqft", ascending=False).reset_index(drop=True)


def get_corridor_metrics(df: pd.DataFrame, corridor_name: str) -> dict[str, Any]:
    quadrants = classify_corridor_quadrants(df)
    match = quadrants[quadrants["Corridor"] == corridor_name]
    if match.empty:
        return {}
    return match.iloc[0].to_dict()
