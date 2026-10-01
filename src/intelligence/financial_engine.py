from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd

# numpy-financial replaces np.irr / np.npv which were removed in NumPy 1.20
try:
    import numpy_financial as _npf
    _NPF_AVAILABLE = True
except ImportError:
    _npf = None  # type: ignore[assignment]
    _NPF_AVAILABLE = False


def calculate_capyield_model(
    property_price: float,
    monthly_rent: float | None = None,
    custom_gross_yield_pct: float = 3.8,  # Gurugram default 3.8%
    vacancy_rate_pct: float = 5.0,  # 5% vacancy allowance
    maintenance_pct: float = 0.8,  # 0.8% of asset price
    property_tax_pct: float = 0.2,  # 0.2% municipal tax
) -> dict[str, Any]:
    """
    CapYield™ Institutional Yield & Cap Rate Model.
    Computes Net Operating Income (NOI), Capitalization Rate (Cap Rate),
    Gross Rental Yield, and Price-to-Rent Ratio (PRR).
    """
    if property_price <= 0:
        raise ValueError("Property price must be positive.")

    # 1. Gross Annual Rental Income
    if monthly_rent is not None and monthly_rent > 0:
        gross_annual_rent = monthly_rent * 12.0
        gross_yield_pct = (gross_annual_rent / property_price) * 100.0
    else:
        gross_yield_pct = custom_gross_yield_pct
        gross_annual_rent = property_price * (gross_yield_pct / 100.0)
        monthly_rent = gross_annual_rent / 12.0

    # 2. Operating Expenses
    vacancy_loss = gross_annual_rent * (vacancy_rate_pct / 100.0)
    effective_gross_income = gross_annual_rent - vacancy_loss

    annual_maintenance = property_price * (maintenance_pct / 100.0)
    annual_tax = property_price * (property_tax_pct / 100.0)
    total_operating_expenses = vacancy_loss + annual_maintenance + annual_tax

    # 3. Net Operating Income (NOI)
    noi = effective_gross_income - annual_maintenance - annual_tax

    # 4. Capitalization Rate (Cap Rate)
    cap_rate_pct = (noi / property_price) * 100.0

    # 5. Price-to-Rent Ratio (PRR)
    prr = property_price / gross_annual_rent if gross_annual_rent > 0 else 0.0

    if prr < 15.0:
        prr_verdict = "Strong Buy Zone (Rental returns high relative to asset price)"
    elif 15.0 <= prr <= 20.0:
        prr_verdict = "Neutral Zone (Balanced capital growth and yield)"
    else:
        prr_verdict = "Capital Growth Focused (Yield is low; return driven by appreciation)"

    return {
        "property_price": round(property_price, 0),
        "property_price_cr": round(property_price / 10_000_000, 2),
        "monthly_rent": round(monthly_rent, 0),
        "gross_annual_rent": round(gross_annual_rent, 0),
        "gross_yield_pct": round(gross_yield_pct, 2),
        "operating_expenses_annual": round(total_operating_expenses, 0),
        "noi_annual": round(noi, 0),
        "cap_rate_pct": round(cap_rate_pct, 2),
        "price_to_rent_ratio": round(prr, 1),
        "prr_verdict": prr_verdict,
    }


def run_irr_projection(
    property_price: float,
    holding_period_years: int = 5,
    annual_appreciation_pct: float = 8.5,
    gross_rental_yield_pct: float = 3.8,
    rental_escalation_pct: float = 5.0,  # 5% rent hike every year
    downpayment_pct: float = 25.0,  # 25% equity, 75% debt
    interest_rate_pct: float = 8.75,
) -> dict[str, Any]:
    """
    Institutional 5-to-10 Year DCF & IRR Cash-Flow Projection.
    Calculates future terminal value, net rental cash flows, and
    Internal Rate of Return (IRR).
    """
    schedule = []
    current_asset_value = property_price
    current_annual_rent = property_price * (gross_rental_yield_pct / 100.0)

    # Initial equity outlay (downpayment + 6% registration & stamp duty buffer)
    initial_equity = property_price * (downpayment_pct / 100.0) + (property_price * 0.06)
    loan_amount = property_price * (1.0 - (downpayment_pct / 100.0))

    # Approximate annual EMI payment
    monthly_r = (interest_rate_pct / 100.0) / 12.0
    total_months = 20 * 12  # 20-year tenure
    if monthly_r > 0:
        monthly_emi = (
            loan_amount
            * monthly_r
            * ((1 + monthly_r) ** total_months)
            / (((1 + monthly_r) ** total_months) - 1)
        )
    else:
        monthly_emi = loan_amount / total_months
    annual_debt_service = monthly_emi * 12.0

    cumulative_net_cash_flow = 0.0
    cash_flows_for_irr = [-initial_equity]

    for year in range(1, holding_period_years + 1):
        # Asset appreciation
        current_asset_value *= 1.0 + (annual_appreciation_pct / 100.0)

        # Net rent after 15% op-ex buffer
        net_rent = current_annual_rent * 0.85
        net_cash_flow = net_rent - (annual_debt_service * 0.5)  # 50% interest portion considered cash outlay

        cumulative_net_cash_flow += net_cash_flow

        schedule.append(
            {
                "Year": f"Year {year}",
                "Asset Value (₹ Cr)": round(current_asset_value / 10_000_000, 2),
                "Annual Rent (₹ Lakh)": round(current_annual_rent / 100_000, 2),
                "Net Cash Flow (₹ Lakh)": round(net_cash_flow / 100_000, 2),
            }
        )

        if year < holding_period_years:
            cash_flows_for_irr.append(net_cash_flow)
        else:
            # Terminal exit value minus remaining loan principal estimate
            estimated_loan_balance = max(0.0, loan_amount * (1.0 - (year * 0.035)))
            net_terminal_proceeds = current_asset_value - estimated_loan_balance + net_cash_flow
            cash_flows_for_irr.append(net_terminal_proceeds)

        # Escalate rent for next year
        current_annual_rent *= 1.0 + (rental_escalation_pct / 100.0)

    # Calculate IRR using numpy-financial (np.irr was removed in NumPy 1.20)
    try:
        if _NPF_AVAILABLE:
            irr_decimal = _npf.irr(cash_flows_for_irr)
            if irr_decimal is None or (isinstance(irr_decimal, float) and np.isnan(irr_decimal)):
                raise ValueError("IRR did not converge")
            irr_pct = float(irr_decimal) * 100.0
        else:
            raise ImportError("numpy-financial not installed")
    except Exception:
        # Fallback: annualized CAGR on equity (reliable approximation)
        final_equity = current_asset_value - (loan_amount * 0.8)
        if initial_equity > 0 and final_equity > 0:
            irr_pct = (((final_equity / initial_equity) ** (1.0 / holding_period_years)) - 1.0) * 100.0
        else:
            irr_pct = annual_appreciation_pct + (gross_rental_yield_pct * 0.8)

    terminal_appreciation_gain = current_asset_value - property_price
    total_gain_cr = (terminal_appreciation_gain + cumulative_net_cash_flow) / 10_000_000

    return {
        "holding_period_years": holding_period_years,
        "initial_investment_cr": round(initial_equity / 10_000_000, 2),
        "terminal_asset_value_cr": round(current_asset_value / 10_000_000, 2),
        "capital_gain_cr": round(terminal_appreciation_gain / 10_000_000, 2),
        "cumulative_net_rent_cr": round(cumulative_net_cash_flow / 10_000_000, 2),
        "total_net_gain_cr": round(total_gain_cr, 2),
        "annualized_irr_pct": round(irr_pct, 1),
        "schedule_df": pd.DataFrame(schedule),
    }
