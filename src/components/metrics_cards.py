from __future__ import annotations

from typing import Any
import streamlit as st


def render_institutional_hero(title: str, subtitle: str, badges: list[str] | None = None) -> None:
    """Renders the top institutional FinTech hero banner."""
    if badges is None:
        badges = [
            "🏛️ PROPRIETARY INTELLIGENCE",
            "📊 G-REPI™ BENCHMARKED",
            "🎯 FAIRVALUE AVM™ ENABLED",
        ]

    badges_html = "".join([f'<span class="intel-badge">{b}</span>' for b in badges])

    st.markdown(
        f"""
        <div class="institutional-hero">
            <div class="hero-title">{title}</div>
            <div class="hero-tagline">{subtitle}</div>
            <div class="hero-badge-row">
                {badges_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_avm_three_tier_cards(avm_results: dict[str, Any]) -> None:
    """Renders the Accumin-style 3-tier valuation confidence bands."""
    col1, col2, col3 = st.columns(3)

    fmv_cr = avm_results.get("fair_market_value_cr", 0.0)
    liq_cr = avm_results.get("liquidation_value_cr", 0.0)
    prem_cr = avm_results.get("premium_value_cr", 0.0)
    dispersion = avm_results.get("dispersion_band_pct", 12.0)
    confidence_tier = avm_results.get("confidence_tier", "Investment Grade")

    with col1:
        st.markdown(
            f"""
            <div class="tier-card liquidation">
                <div class="tier-label" style="color: #64748B;">📉 Liquidation / Distress (P15)</div>
                <div class="tier-value">₹{liq_cr:.2f} <span style="font-size:1.1rem; color:#64748B;">Cr</span></div>
                <div class="tier-sub">30-day cash sale value & lender collateral benchmark</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="tier-card fmv">
                <div class="tier-label" style="color: #0284C7;">🎯 Fair Market Value (FMV - P50)</div>
                <div class="tier-value" style="color: #0284C7;">₹{fmv_cr:.2f} <span style="font-size:1.1rem;">Cr</span></div>
                <div class="tier-sub"><b>Arm's length equilibrium</b> • ±{dispersion}% variance band</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="tier-card premium">
                <div class="tier-label" style="color: #B45309;">💎 Turnkey / Premium Asset (P85)</div>
                <div class="tier-value" style="color: #B45309;">₹{prem_cr:.2f} <span style="font-size:1.1rem;">Cr</span></div>
                <div class="tier-sub">High-floor, bespoke luxury or designer-furnished ceiling</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(f"🛡️ **Appraisal Methodology:** {confidence_tier} • Volatility Score: {avm_results.get('liquidity_volatility_score', 80)}/100")


def render_valuation_gauge_card(gauge_results: dict[str, Any], asking_price_cr: float) -> None:
    """Renders the Over/Undervalued Barometer verdict card."""
    diff_pct = gauge_results["diff_pct"]
    status = gauge_results["status"]
    color = gauge_results["color"]
    verdict = gauge_results["verdict"]
    guidance = gauge_results["negotiation_guidance"]

    sign = "+" if diff_pct > 0 else ""

    st.markdown(
        f"""
        <div class="barometer-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-size:0.85rem; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.05em;">Asking Price Analysis</span>
                    <h3 style="margin:0.2rem 0 0 0; font-family:'Space Grotesk', sans-serif;">₹{asking_price_cr:.2f} Cr</h3>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:1.4rem; font-weight:800; color:{color}; font-family:'Space Grotesk', sans-serif;">
                        {sign}{diff_pct:.1f}%
                    </span>
                    <div style="font-size:0.8rem; font-weight:700; color:{color}; text-transform:uppercase;">{status}</div>
                </div>
            </div>
            <div class="verdict-banner" style="background: {color}15; color: {color}; border-left: 4px solid {color};">
                <b>Institutional Verdict:</b> {verdict}
            </div>
            <div style="font-size:0.88rem; color:#475569; background:#F8FAFC; padding:0.8rem 1rem; border-radius:10px; border:1px dashed #CBD5E1;">
                💼 <b>Negotiation Advisory:</b> {guidance}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_grepi_badge(grade: str) -> str:
    """Returns HTML for an institutional rating badge."""
    if "AAA" in grade:
        return '<span style="background:#DCFCE7; color:#15803D; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.8rem;">AAA Prime</span>'
    elif "AA" in grade:
        return '<span style="background:#E0F2FE; color:#0369A1; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.8rem;">AA Strong</span>'
    elif "A " in grade or "A (" in grade:
        return '<span style="background:#FEF3C7; color:#B45309; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.8rem;">A Stable</span>'
    return '<span style="background:#F1F5F9; color:#475569; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.8rem;">BBB / BB</span>'


def render_corridor_quadrant_pill(quadrant_str: str) -> str:
    """Returns styled HTML pill for corridor quadrants."""
    if "Quadrant I" in quadrant_str:
        return '<span class="quadrant-pill q-prime">👑 Quadrant I: Prime Blue-Chip</span>'
    elif "Quadrant II" in quadrant_str:
        return '<span class="quadrant-pill q-growth">🚀 Quadrant II: High Velocity</span>'
    elif "Quadrant III" in quadrant_str:
        return '<span class="quadrant-pill q-yield">💰 Quadrant III: High Yield</span>'
    return '<span class="quadrant-pill q-value">💎 Quadrant IV: Value Accumulator</span>'
