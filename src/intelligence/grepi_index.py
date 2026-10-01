from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_grepi_index(df: pd.DataFrame, min_listings: int = 3) -> pd.DataFrame:
    """
    Computes the proprietary G-REPI™ (Gurugram Real Estate Performance Index).
    A composite statistical index (0 - 100) benchmarking micro-market health,
    transaction velocity, pricing stability, and liquidity depth.
    """
    if df.empty:
        return pd.DataFrame()

    required_cols = {"Locality", "Price", "Rate per sqft"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DataFrame must contain {required_cols}")

    # Group by micro-market (Locality)
    grouped = (
        df.groupby("Locality")
        .agg(
            inventory_depth=("Price", "count"),
            median_rate=("Rate per sqft", "median"),
            mean_rate=("Rate per sqft", "mean"),
            std_rate=("Rate per sqft", lambda s: s.std() if len(s) > 1 else 0.0),
            median_price=("Price", "median"),
            total_value_cr=("Price", lambda p: p.sum() / 10_000_000),
        )
        .reset_index()
    )

    # Filter out micro-markets with insufficient data points
    grouped = grouped[grouped["inventory_depth"] >= min_listings].copy()
    if grouped.empty:
        return grouped

    grouped["std_rate"] = grouped["std_rate"].fillna(0.0)

    # 1. Price Momentum & Value Factor (40% weight) - Log-normalized rate
    rate_log = np.log1p(grouped["median_rate"])
    r_min, r_max = rate_log.min(), rate_log.max()
    score_rate = (
        ((rate_log - r_min) / (r_max - r_min) * 100)
        if r_max > r_min
        else pd.Series(50, index=grouped.index)
    )

    # 2. Liquidity & Market Depth Factor (35% weight) - Log-normalized inventory
    inv_log = np.log1p(grouped["inventory_depth"])
    i_min, i_max = inv_log.min(), inv_log.max()
    score_inv = (
        ((inv_log - i_min) / (i_max - i_min) * 100)
        if i_max > i_min
        else pd.Series(50, index=grouped.index)
    )

    # 3. Price Stability Factor (25% weight) - Low coefficient of variation = Higher stability
    cv = grouped["std_rate"] / grouped["mean_rate"].replace(0, 1)
    cv_clipped = cv.clip(0, 1)
    score_stability = (1 - cv_clipped) * 100

    # Composite G-REPI Formula
    composite = (score_rate * 0.40) + (score_inv * 0.35) + (score_stability * 0.25)
    grouped["grepi_score"] = composite.round(1).clip(20.0, 99.5)

    # Assign Institutional Grade
    def assign_grade(score: float) -> str:
        if score >= 88:
            return "AAA (Prime Institutional)"
        if score >= 78:
            return "AA (High Investment Grade)"
        if score >= 68:
            return "A (Stable Market)"
        if score >= 58:
            return "BBB (Moderate Liquidity)"
        return "BB (Emerging Micro-Market)"

    grouped["institutional_grade"] = grouped["grepi_score"].apply(assign_grade)

    # Format metrics for presentation
    grouped["avg_price_cr"] = (grouped["median_price"] / 10_000_000).round(2)
    grouped["median_rate_sqft"] = grouped["median_rate"].round(0).astype(int)
    grouped["total_market_depth_cr"] = grouped["total_value_cr"].round(1)

    # Sort descending by G-REPI score
    ranked = grouped.sort_values(by="grepi_score", ascending=False).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1

    return ranked[
        [
            "rank",
            "Locality",
            "grepi_score",
            "institutional_grade",
            "inventory_depth",
            "median_rate_sqft",
            "avg_price_cr",
            "total_market_depth_cr",
        ]
    ]


def get_top_performing_micro_markets(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Returns top N micro-markets ranked by the G-REPI™ index."""
    grepi_df = calculate_grepi_index(df)
    return grepi_df.head(limit)
