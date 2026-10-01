from __future__ import annotations

import datetime
import hashlib
from typing import Any


def generate_dossier_html(
    locality: str,
    bhk: int,
    area_sqft: float,
    property_type: str,
    avm_result: dict[str, Any],
    cap_result: dict[str, Any],
    irr_result: dict[str, Any],
    grepi_rating: str = "AA (High Investment Grade)",
    asking_price: float | None = None,
    client_name: str = "Institutional Investor",
) -> str:
    """
    Generates an official, print-ready Institutional Due-Diligence Dossier™ (HTML/PDF).
    Formatted with luxury typography, appraisal seals, and financial schedules.
    """
    now_str = datetime.datetime.now().strftime("%d %B %Y, %H:%M IST")
    unique_seed = f"{locality}-{bhk}-{area_sqft}-{datetime.datetime.now().timestamp()}"
    report_id = f"AREI-VAL-2026-{hashlib.md5(unique_seed.encode()).hexdigest()[:6].upper()}"

    fmv_cr = avm_result.get("fair_market_value_cr", 0.0)
    liq_cr = avm_result.get("liquidation_value_cr", 0.0)
    prem_cr = avm_result.get("premium_value_cr", 0.0)
    rate_sqft = avm_result.get("effective_rate_sqft", 0.0)
    confidence = avm_result.get("confidence_tier", "Grade A")

    # IRR Schedule Rows
    schedule_df = irr_result.get("schedule_df")
    schedule_rows_html = ""
    if schedule_df is not None and not schedule_df.empty:
        for _, row in schedule_df.iterrows():
            schedule_rows_html += f"""
            <tr>
                <td style="padding:8px 12px; border-bottom:1px solid #E2E8F0;">{row['Year']}</td>
                <td style="padding:8px 12px; border-bottom:1px solid #E2E8F0; text-align:right; font-family:monospace;">₹{row['Asset Value (₹ Cr)']} Cr</td>
                <td style="padding:8px 12px; border-bottom:1px solid #E2E8F0; text-align:right; font-family:monospace;">₹{row['Annual Rent (₹ Lakh)']} L</td>
                <td style="padding:8px 12px; border-bottom:1px solid #E2E8F0; text-align:right; font-family:monospace; color:#10B981; font-weight:600;">₹{row['Net Cash Flow (₹ Lakh)']} L</td>
            </tr>
            """

    # Asking price comparison
    barometer_section = ""
    if asking_price and asking_price > 0:
        diff_pct = ((asking_price - avm_result["fair_market_value"]) / avm_result["fair_market_value"]) * 100.0
        color = "#10B981" if diff_pct <= 0 else "#EF4444"
        verdict = "BELOW FAIR VALUE (ATTRACTIVE BUY)" if diff_pct <= 0 else "SELLER PREMIUM DETECTED"
        barometer_section = f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:15px 20px; margin:20px 0;">
            <div style="font-size:0.8rem; text-transform:uppercase; color:#64748B; font-weight:700;">Asking Price Audit</div>
            <div style="font-size:1.4rem; font-weight:800; color:#0F172A; margin:4px 0;">
                ₹{asking_price/10_000_000:.2f} Cr 
                <span style="font-size:1rem; color:{color}; font-weight:700;">({diff_pct:+.1f}% vs FMV • {verdict})</span>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Due-Diligence Dossier • {report_id}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');
            @media print {{
                body {{ -webkit-print-color-adjust: exact; }}
                .no-print {{ display: none !important; }}
            }}
            body {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                color: #0F172A;
                background: #FFFFFF;
                margin: 0;
                padding: 40px;
                line-height: 1.5;
            }}
            .dossier-container {{
                max-width: 850px;
                margin: 0 auto;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
            }}
            .header-bar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #0B132B;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .title {{
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.8rem;
                font-weight: 700;
                color: #0B132B;
                margin: 0;
            }}
            .meta-id {{
                font-family: monospace;
                font-size: 0.85rem;
                color: #64748B;
            }}
            .seal-badge {{
                background: #0B132B;
                color: #00E5FF;
                padding: 6px 14px;
                border-radius: 999px;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}
            .asset-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 25px;
            }}
            .grid-item-label {{
                font-size: 0.75rem;
                color: #64748B;
                text-transform: uppercase;
                font-weight: 700;
            }}
            .grid-item-val {{
                font-size: 1.05rem;
                font-weight: 700;
                color: #0F172A;
                margin-top: 3px;
            }}
            .val-cards {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
            }}
            .v-card {{
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #E2E8F0;
            }}
            .v-liq {{ border-top: 4px solid #64748B; }}
            .v-fmv {{ border-top: 4px solid #0284C7; background: #F0F9FF; }}
            .v-prem {{ border-top: 4px solid #D4AF37; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                font-size: 0.9rem;
            }}
            th {{
                background: #F1F5F9;
                padding: 10px 12px;
                text-align: left;
                font-size: 0.75rem;
                text-transform: uppercase;
                color: #475569;
            }}
            .print-btn {{
                background: #0284C7;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 700;
                cursor: pointer;
                font-size: 0.95rem;
                margin-bottom: 25px;
            }}
            .disclaimer {{
                font-size: 0.75rem;
                color: #94A3B8;
                border-top: 1px solid #E2E8F0;
                padding-top: 20px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="no-print" style="text-align:center;">
            <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF Dossier</button>
        </div>

        <div class="dossier-container">
            <div class="header-bar">
                <div>
                    <h1 class="title">AKHI REAL ESTATE INTELLIGENCE</h1>
                    <div style="font-size:0.9rem; color:#0284C7; font-weight:600; margin-top:2px;">Institutional Due-Diligence & Automated Valuation Dossier</div>
                    <div class="meta-id">REPORT REF: {report_id} • ISSUED: {now_str}</div>
                </div>
                <div style="text-align:right;">
                    <span class="seal-badge">OFFICIAL VALUATION</span>
                    <div style="font-size:0.8rem; color:#64748B; margin-top:6px;">Client: <b>{client_name}</b></div>
                </div>
            </div>

            <div class="asset-grid">
                <div>
                    <div class="grid-item-label">Locality / Sector</div>
                    <div class="grid-item-val">{locality}</div>
                </div>
                <div>
                    <div class="grid-item-label">Configuration</div>
                    <div class="grid-item-val">{bhk} BHK • {property_type}</div>
                </div>
                <div>
                    <div class="grid-item-label">Carpet Area</div>
                    <div class="grid-item-val">{area_sqft:,.0f} sqft</div>
                </div>
                <div>
                    <div class="grid-item-label">G-REPI™ Rating</div>
                    <div class="grid-item-val" style="color:#0284C7;">{grepi_rating}</div>
                </div>
            </div>

            <h3 style="margin:25px 0 10px 0; font-family:'Space Grotesk', sans-serif;">1. Three-Tier Valuation Appraisal Certificate</h3>
            <div class="val-cards">
                <div class="v-card v-liq">
                    <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">Liquidation (P15)</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0F172A; margin:4px 0;">₹{liq_cr:.2f} Cr</div>
                    <div style="font-size:0.75rem; color:#64748B;">30-Day Cash Liquidation Target</div>
                </div>
                <div class="v-card v-fmv">
                    <div style="font-size:0.75rem; color:#0284C7; text-transform:uppercase; font-weight:700;">Fair Market Value (FMV - P50)</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0284C7; margin:4px 0;">₹{fmv_cr:.2f} Cr</div>
                    <div style="font-size:0.75rem; color:#0284C7;">Arm's Length Equilibrium (₹{rate_sqft:,.0f}/sqft)</div>
                </div>
                <div class="v-card v-prem">
                    <div style="font-size:0.75rem; color:#B45309; text-transform:uppercase; font-weight:700;">Premium Asset Ceiling (P85)</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#B45309; margin:4px 0;">₹{prem_cr:.2f} Cr</div>
                    <div style="font-size:0.75rem; color:#B45309;">Turnkey / Luxury Finished Ceiling</div>
                </div>
            </div>

            {barometer_section}

            <h3 style="margin:25px 0 10px 0; font-family:'Space Grotesk', sans-serif;">2. Institutional Financial & Yield Underwriting</h3>
            <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:15px; margin-bottom:15px;">
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 16px; border-radius:10px;">
                    <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">Gross Rental Yield</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#0F172A;">{cap_result.get('gross_yield_pct', 3.8):.2f}%</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 16px; border-radius:10px;">
                    <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">Net Cap Rate</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#0F172A;">{cap_result.get('cap_rate_pct', 2.9):.2f}%</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 16px; border-radius:10px;">
                    <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">5-Yr Annualized IRR</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#10B981;">{irr_result.get('annualized_irr_pct', 11.5):.1f}%</div>
                </div>
            </div>

            <h3 style="margin:25px 0 5px 0; font-family:'Space Grotesk', sans-serif;">3. 5-Year DCF Cash-Flow & Capital Gain Schedule</h3>
            <table>
                <thead>
                    <tr>
                        <th>Horizon</th>
                        <th style="text-align:right;">Projected Asset Value</th>
                        <th style="text-align:right;">Gross Annual Rent</th>
                        <th style="text-align:right;">Net Annual Cash Flow</th>
                    </tr>
                </thead>
                <tbody>
                    {schedule_rows_html}
                </tbody>
            </table>

            <div class="disclaimer">
                <b>Regulatory & Compliance Disclaimer:</b> This document is an automated analytical valuation produced by the Akhi Real Estate Intelligence (AREI™) proprietary statistical model based on registered transaction benchmarks, median locality distributions, and Random Forest regressors. It does not constitute a legal title search, structural audit, or mandatory credit commitment. Users are advised to conduct physical title due diligence and RERA registration verification prior to transaction finalization.
                <br/><br/>
                <b>AREI™ Institutional Research Division • Gurugram, India</b>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content
