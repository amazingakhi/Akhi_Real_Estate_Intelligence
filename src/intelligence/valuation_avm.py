from __future__ import annotations

import math
from typing import Any
import numpy as np
import pandas as pd


def calculate_fairvalue_avm(
    area_sqft: float,
    bhk: int,
    locality: str,
    property_type: str,
    df_reference: pd.DataFrame | None = None,
    ml_predicted_price: float | None = None,
) -> dict[str, Any]:
    """
    Akhi FairValue AVM™ (Automated Valuation Model)
    Calculates 3-tier valuation confidence bands:
    - Conservative Liquidation Value (P15)
    - Fair Market Value (P50 - FMV)
    - Premium Turnkey Valuation (P85)
    along with liquidity risk and confidence metrics.
    """
    if area_sqft <= 0:
        raise ValueError("Area must be positive.")

    # 1. Determine baseline rate per sqft from reference dataset
    baseline_rate = 11_500.0  # Gurugram median default fallback
    rate_std = 2_200.0
    inventory_count = 0

    if df_reference is not None and not df_reference.empty:
        locality_subset = df_reference[
            df_reference["Locality"].astype(str).str.strip().str.lower()
            == str(locality).strip().lower()
        ]
        if not locality_subset.empty:
            baseline_rate = float(locality_subset["Rate per sqft"].median())
            std_val = locality_subset["Rate per sqft"].std()
            rate_std = float(std_val) if not math.isnan(std_val) and std_val > 0 else (baseline_rate * 0.15)
            inventory_count = len(locality_subset)
        else:
            # Fallback to city-wide rate
            baseline_rate = float(df_reference["Rate per sqft"].median())
            rate_std = float(df_reference["Rate per sqft"].std())
            inventory_count = 1

    # 2. Reconcile with ML model prediction if available
    stat_price = baseline_rate * area_sqft

    if ml_predicted_price is not None and ml_predicted_price > 0:
        # Weighted blend: 60% ML model, 40% Locality statistical median
        fair_market_value = (ml_predicted_price * 0.60) + (stat_price * 0.40)
    else:
        fair_market_value = stat_price

    # 3. Calculate Confidence Spread (Dispersion)
    dispersion_ratio = min(0.25, max(0.08, rate_std / baseline_rate if baseline_rate > 0 else 0.15))
    
    # 3-Tier Valuation Bands
    liquidation_discount = dispersion_ratio * 0.95
    premium_markup = dispersion_ratio * 1.05

    liquidation_value = fair_market_value * (1.0 - liquidation_discount)
    premium_value = fair_market_value * (1.0 + premium_markup)

    # 4. Valuation Confidence Level
    if inventory_count >= 20:
        confidence_tier = "High Institutional Confidence (Grade A)"
        confidence_pct = 92
    elif inventory_count >= 5:
        confidence_tier = "Medium Investment Confidence (Grade B)"
        confidence_pct = 78
    else:
        confidence_tier = "Estimated Benchmark (Grade C - Low Sample Size)"
        confidence_pct = 64

    # 5. Liquidity & Volatility Score (0-100, where 100 is ultra-liquid & low volatility)
    volatility_score = round(max(20, min(95, 100 - (dispersion_ratio * 250))), 1)

    return {
        "fair_market_value": round(fair_market_value, -3),  # Rounded to nearest thousand
        "fair_market_value_cr": round(fair_market_value / 10_000_000, 2),
        "liquidation_value": round(liquidation_value, -3),
        "liquidation_value_cr": round(liquidation_value / 10_000_000, 2),
        "premium_value": round(premium_value, -3),
        "premium_value_cr": round(premium_value / 10_000_000, 2),
        "effective_rate_sqft": round(fair_market_value / area_sqft, 0),
        "dispersion_band_pct": round(dispersion_ratio * 100, 1),
        "confidence_tier": confidence_tier,
        "confidence_pct": confidence_pct,
        "liquidity_volatility_score": volatility_score,
        "locality_sample_size": inventory_count,
    }


def get_valuation_gauge(asking_price: float, fair_market_value: float) -> dict[str, Any]:
    """
    Over/Undervaluation Barometer™
    Compares asking price against Fair Market Value (FMV) to identify
    under-market bargains, fair parity, or overvalued seller premiums.
    """
    if fair_market_value <= 0:
        return {"diff_pct": 0.0, "status": "Unknown", "recommendation": "Insufficient data"}

    diff_pct = ((asking_price - fair_market_value) / fair_market_value) * 100.0

    if diff_pct <= -10.0:
        status = "Strong Value Bargain"
        color = "#10B981"  # Emerald green
        verdict = f"Priced {abs(diff_pct):.1f}% BELOW institutional fair value. Favorable entry for buyers/investors."
        negotiation = "Immediate acquisition target. Minor buffer to close."
    elif -10.0 < diff_pct <= -3.0:
        status = "Mild Discount to Market"
        color = "#34D399"  # Light green
        verdict = f"Priced {abs(diff_pct):.1f}% below fair market value. Attractive value proposition."
        negotiation = "Target 3-5% further concession on closing terms."
    elif -3.0 < diff_pct <= 4.0:
        status = "Fair Market Parity"
        color = "#0284C7"  # Sky blue
        verdict = f"Priced within ±4% of institutional baseline. Reflects true equilibrium."
        negotiation = "Target standard 2-3% brokerage/stamp duty cost adjustment."
    elif 4.0 < diff_pct <= 12.0:
        status = "Moderate Seller Premium"
        color = "#F59E0B"  # Amber
        verdict = f"Priced {diff_pct:.1f}% above fair value. Justified only if high-floor or ultra-luxury specification."
        negotiation = f"Negotiate aggressively toward fair value target: ₹{fair_market_value/10_000_000:.2f} Cr."
    else:
        status = "Substantially Overpriced"
        color = "#EF4444"  # Red
        verdict = f"Priced {diff_pct:.1f}% ABOVE fair value. Significant downside capital risk."
        negotiation = "Hold or counter-offer at least 15-20% lower. High risk of capital stagnation."

    return {
        "diff_pct": round(diff_pct, 1),
        "status": status,
        "color": color,
        "verdict": verdict,
        "negotiation_guidance": negotiation,
    }
