from __future__ import annotations

import streamlit as st


def inject_premium_fintech_theme() -> None:
    """
    Injects an ultra-premium Institutional FinTech design system.
    Inspired by high-end financial platforms (Bloomberg, PropEquity, PitchBook).
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');
        
        * {
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: -0.01em;
        }
        
        .font-mono {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Top Institutional Banner */
        .institutional-hero {
            background: linear-gradient(135deg, #0B132B 0%, #1C2541 60%, #0F172A 100%);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 20px;
            padding: 2.2rem 2.5rem;
            color: #ffffff;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px -15px rgba(11, 19, 43, 0.4);
            position: relative;
            overflow: hidden;
        }
        
        .institutional-hero::before {
            content: "";
            position: absolute;
            top: -50%;
            right: -20%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(0, 229, 255, 0.12) 0%, transparent 70%);
            pointer-events: none;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            color: #FFFFFF !important;
            margin: 0 0 0.4rem 0;
        }

        .hero-tagline {
            color: #94A3B8 !important;
            font-size: 1.05rem;
            margin: 0 0 1rem 0;
            font-weight: 400;
        }

        .hero-badge-row {
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .intel-badge {
            background: rgba(0, 229, 255, 0.1);
            color: #00E5FF;
            border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 0.3rem 0.8rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }

        .gold-badge {
            background: rgba(212, 175, 55, 0.15);
            color: #FACC15;
            border: 1px solid rgba(212, 175, 55, 0.4);
            padding: 0.3rem 0.8rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* 3-Tier Valuation Cards */
        .tier-card {
            border-radius: 16px;
            padding: 1.5rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .tier-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.09);
        }

        .tier-card.liquidation {
            border-top: 4px solid #64748B;
        }

        .tier-card.fmv {
            border-top: 4px solid #0284C7;
            background: linear-gradient(180deg, #F0F9FF 0%, #FFFFFF 60%);
            box-shadow: 0 10px 30px rgba(2, 132, 199, 0.12);
        }

        .tier-card.premium {
            border-top: 4px solid #D4AF37;
        }

        .tier-label {
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.4rem;
        }

        .tier-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.1;
            margin-bottom: 0.3rem;
        }

        .tier-sub {
            font-size: 0.82rem;
            color: #64748B;
        }

        /* Valuation Barometer Box */
        .barometer-card {
            border-radius: 16px;
            padding: 1.5rem;
            margin-top: 1.2rem;
            border: 1px solid #E2E8F0;
            background: #FFFFFF;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        }

        .verdict-banner {
            border-radius: 12px;
            padding: 1rem 1.4rem;
            margin: 1rem 0;
            font-weight: 600;
            font-size: 0.95rem;
        }

        /* Corridor Quadrant Badges */
        .quadrant-pill {
            display: inline-block;
            padding: 0.35rem 0.9rem;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.82rem;
            letter-spacing: 0.02em;
        }

        .q-prime {
            background: #FEF3C7;
            color: #92400E;
            border: 1px solid #FDE68A;
        }

        .q-growth {
            background: #E0F2FE;
            color: #0369A1;
            border: 1px solid #BAE6FD;
        }

        .q-yield {
            background: #D1FAE5;
            color: #065F46;
            border: 1px solid #A7F3D0;
        }

        .q-value {
            background: #F3E8FF;
            color: #6B21A8;
            border: 1px solid #E9D5FF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
