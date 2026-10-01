from __future__ import annotations

import sys
import json
import re
import urllib
import urllib.parse
from pathlib import Path
from datetime import datetime

# Path setup for src and config packages
CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st
import numpy as np

from backend import (
    ensure_admin_account,
    get_total_leads,
    hash_password,
    load_leads,
    load_shortlist,
    load_users,
    remove_shortlist_item,
    save_lead,
    save_shortlist_item,
    save_user,
    verify_password,
)
from price_prediction import predict_price
from real_estate_analysis import clean_real_estate_data, load_real_estate_data

from intelligence import (
    calculate_grepi_index,
    get_top_performing_micro_markets,
    calculate_fairvalue_avm,
    get_valuation_gauge,
    calculate_capyield_model,
    run_irr_projection,
    classify_corridor_quadrants,
)
from components import (
    inject_premium_fintech_theme,
    render_institutional_hero,
    render_avm_three_tier_cards,
    render_valuation_gauge_card,
    generate_dossier_html,
)
from security import (
    is_rate_limited,
    validate_phone_number,
    validate_email_address,
    sanitize_text,
)
from intelligence.lead_alerts import (
    score_lead,
    format_admin_whatsapp_dispatch,
    format_buyer_outreach_url,
)

# Email notifications
try:
    from notifications.email_alerts import (
        send_new_lead_alert,
        send_buyer_confirmation,
        send_welcome_email,
    )
    _EMAIL_OK = True
except Exception:
    _EMAIL_OK = False
    def send_new_lead_alert(lead): return False, "unavailable"
    def send_buyer_confirmation(lead): return False, "unavailable"
    def send_welcome_email(name, email): return False, "unavailable"

# Payments
try:
    from payments.razorpay_checkout import (
        SUBSCRIPTION_PLANS,
        create_payment_link,
        razorpay_is_configured as _rzp_live,
    )
    _PAYMENT_OK = True
except Exception:
    _PAYMENT_OK = False
    SUBSCRIPTION_PLANS = []
    def create_payment_link(*a, **kw): return False, "unavailable"
    def _rzp_live(): return False

# -- New: Email Notifications €€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€
try:
    from notifications.email_alerts import (
        send_new_lead_alert,
        send_buyer_confirmation,
        send_welcome_email,
    )
    _EMAIL_MODULE_OK = True
except Exception:
    _EMAIL_MODULE_OK = False
    def send_new_lead_alert(lead): return False, "Email module unavailable"
    def send_buyer_confirmation(lead): return False, "Email module unavailable"
    def send_welcome_email(name, email): return False, "Email module unavailable"

# -- New: Payment / Subscription €€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€
try:
    from payments.razorpay_checkout import (
        SUBSCRIPTION_PLANS,
        create_payment_link,
        get_razorpay_checkout_html,
        razorpay_is_configured as _rzp_live,
    )
    _PAYMENT_MODULE_OK = True
except Exception:
    _PAYMENT_MODULE_OK = False
    SUBSCRIPTION_PLANS = []
    def create_payment_link(*a, **kw): return False, "Payment module unavailable"
    def get_razorpay_checkout_html(*a, **kw): return ""
    def _rzp_live(): return False

st.set_page_config(
    page_title="Akhi Real Estate Intelligence | AREI™",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_premium_fintech_theme()

# -- SEO, Open Graph & Google Analytics injection €€€€€€€€€€€€€€€€€€€€€€€€€€€€€€
def _inject_seo_and_analytics():
    """
    Injects SEO meta tags, Open Graph / Twitter Card tags, canonical URL,
    structured data (JSON-LD), and optionally Google Analytics 4.
    All tags live inside a hidden <div> in Streamlit's HTML output.
    """
    import os as _os_seo
    ga_id = _os_seo.getenv("GA_MEASUREMENT_ID", "")

    ga_script = ""
    if ga_id and ga_id.startswith("G-"):
        ga_script = f"""
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}', {{
        page_title: 'Akhi Real Estate Intelligence',
        send_page_view: true
      }});
    </script>"""

    seo_html = f"""
    <head>
    <!-- Primary SEO Meta Tags -->
    <meta name="title" content="Akhi Real Estate Intelligence | AREI € Gurugram Premium Property Platform">
    <meta name="description" content="Institutional-grade property data, AVM valuations, IRR projections & G-REPI micro-market intelligence for Gurugram real estate investors and buyers.">
    <meta name="keywords" content="Gurugram real estate, Gurgaon property, property investment, AVM valuation, IRR projection, Golf Course Road, Dwarka Expressway, real estate analytics India">
    <meta name="robots" content="index, follow">
    <meta name="language" content="English">
    <meta name="author" content="Akhi Real Estate Intelligence">
    <meta name="revisit-after" content="7 days">
    <link rel="canonical" href="https://akhiproperties.com">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://akhiproperties.com">
    <meta property="og:title" content="Akhi Real Estate Intelligence | AREI Platform">
    <meta property="og:description" content="Institutional property data, G-REPI micro-market index, FairValue AVM & IRR projections for Gurugram real estate.">
    <meta property="og:image" content="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&q=80">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="Akhi Real Estate Intelligence">
    <meta property="og:locale" content="en_IN">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://akhiproperties.com">
    <meta name="twitter:title" content="Akhi Real Estate Intelligence | AREI Platform">
    <meta name="twitter:description" content="Institutional-grade Gurugram property analytics. G-REPI Index, FairValue AVM, IRR Projections.">
    <meta name="twitter:image" content="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&q=80">

    <!-- JSON-LD Structured Data: Organization -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "RealEstateAgent",
      "name": "Akhi Real Estate Intelligence",
      "alternateName": "AREI",
      "url": "https://akhiproperties.com",
      "logo": "https://akhiproperties.com/logo.png",
      "description": "Institutional-grade property analytics and advisory platform for Gurugram/NCR real estate",
      "telephone": "+916387594514",
      "email": "iamakv01@gmail.com",
      "address": {{
        "@type": "PostalAddress",
        "addressLocality": "Gurugram",
        "addressRegion": "Haryana",
        "addressCountry": "IN"
      }},
      "areaServed": {{
        "@type": "City",
        "name": "Gurugram"
      }},
      "sameAs": [
        "https://instagram.com/youknow_akhi",
        "https://wa.me/916387594514"
      ]
    }}
    </script>

    <!-- JSON-LD: WebApplication -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "AREI Property Intelligence Platform",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Any",
      "offers": {{
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "INR",
        "availability": "https://schema.org/InStock"
      }},
      "description": "G-REPI micro-market index, FairValue AVM automated valuations, CapYield cap rate engine, and IRR projections for Gurugram real estate investors."
    }}
    </script>
    {ga_script}
    </head>
    """

    st.markdown(seo_html, unsafe_allow_html=True)


_inject_seo_and_analytics()

# Business Constants
CONTACT_NUMBER = "6387594514"
INSTAGRAM = "https://instagram.com/youknow_akhi"
WEBSITE = "https://yourwebsite.com"
WHATSAPP = "https://wa.me/916387594514"
EMAIL = "iamakv01@gmail.com"

# Razorpay € read from config (falls back to empty string if not configured)
try:
    from config.settings import RAZORPAY_KEY, razorpay_is_configured as _rzp_configured
    _RAZORPAY_LIVE = _rzp_configured()
except ImportError:
    import os as _os
    RAZORPAY_KEY = _os.getenv("RAZORPAY_KEY_ID", "")
    _RAZORPAY_LIVE = bool(RAZORPAY_KEY and "your_key" not in RAZORPAY_KEY.lower())

# Premium Styling - Fixed Colors for Input Visibility
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,500,0,0');
    
    * {
        font-family: 'DM Sans', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"], .main {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        color: #0f172a !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important;
        border-right: 1px solid #cbd5e1;
    }
    
    .main .block-container {
        max-width: 1400px;
        padding: 2rem 1rem;
    }
    
    /* INPUT BOX FIX - CLEAN & UNCLIPPED */
    [data-testid="stTextInput"] > div,
    [data-testid="stTextArea"] > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    input, textarea, 
    [data-testid="stTextInput"] input, 
    [data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 0.96rem !important;
        line-height: 1.5 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    
    input::placeholder, textarea::placeholder {
        color: #94a3b8 !important;
    }
    
    input:focus, textarea:focus,
    [data-testid="stTextInput"] input:focus, 
    [data-testid="stTextArea"] textarea:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
        outline: none !important;
    }
    
    /* SELECT/DROPDOWN FIX */
    [data-testid="stSelectbox"] > div {
        background: transparent !important;
        border: none !important;
    }
    select, [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    
    /* SLIDER FIX */
    [data-testid="stSlider"] {
        color: #0ea5e9 !important;
    }

    /* EQUAL HEIGHT BALANCED PRICING CARD SYSTEM */
    .arei-pricing-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.75rem 1.5rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 520px;
        height: 100%;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        box-sizing: border-box;
    }
    .arei-pricing-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 36px rgba(14, 165, 233, 0.15);
    }
    .arei-pricing-card.featured {
        border: 2.5px solid #0ea5e9;
        background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%);
        box-shadow: 0 14px 34px rgba(14, 165, 233, 0.18);
    }
    .arei-badge-slot {
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
    }
    .arei-pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 999px;
        padding: 4px 12px;
    }
    .arei-pill-badge.popular {
        background: #0ea5e9;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }
    .arei-pricing-features {
        list-style: none;
        padding: 0;
        margin: 1.2rem 0;
        flex-grow: 1;
    }
    .arei-pricing-features li {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.45;
        margin-bottom: 0.65rem;
    }
    .arei-check-icon {
        color: #0ea5e9;
        font-size: 1.1rem;
        line-height: 1;
        flex-shrink: 0;
    }
    
    h1, h2, h3, h4 {
        color: #0f172a !important;
        font-weight: 700;
    }

    h1, h2, h3, h4, .brand-badge, .section-heading {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    p, label, .stCaption {
        color: #475569 !important;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #0f172a 35%, #0ea5e9 100%);
        border-radius: 24px;
        padding: 4rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 24px 60px rgba(14, 165, 233, 0.22);
        border: 1px solid rgba(125, 211, 252, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .hero-banner::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at top right, rgba(14, 165, 233, 0.35), transparent 40%);
    }
    
    .hero-banner h1,
    .hero-banner p {
        position: relative;
        z-index: 1;
    }
    
    .hero-banner h1 {
        color: #ffffff !important;
        font-size: 3rem;
        margin: 0;
        letter-spacing: -0.04em;
    }
    
    .hero-banner p {
        color: #f0f9ff !important;
        font-size: 1.2rem;
    }
    
    .property-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.08);
    }
    
    .property-card:hover {
        border-color: #0ea5e9;
        box-shadow: 0 12px 35px rgba(14, 165, 233, 0.2);
        transform: translateY(-6px);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 12px 28px rgba(14, 165, 233, 0.18);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stat-box h3 {
        color: #ffffff !important;
        margin: 0;
        font-weight: 800 !important;
    }
    
    .stat-box p {
        color: #ffffff !important;
        margin: 0;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        border: 2px solid #cffafe;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .feature-card h3 {
        color: #0284c7 !important;
        font-weight: 800 !important;
    }
    
    .feature-card p {
        color: #0c4a6e !important;
        font-weight: 600 !important;
    }
    
    .feature-card b {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    .premium-panel {
        background: linear-gradient(135deg, #f8fbff 0%, #eff6ff 100%);
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 1.4rem;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.08);
        height: 100%;
    }
    
    .premium-panel h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    
    .premium-panel p, .premium-panel li {
        color: #334155 !important;
        font-weight: 600 !important;
    }
    
    .section-heading {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.5rem 0 1rem 0;
    }
    
    .top-brand-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
        border-radius: 16px;
        padding: 0.8rem 1.2rem;
        margin: 0 0 1.2rem 0;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.25);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    
    .brand-badge {
        color: #f8fafc !important;
        font-weight: 900;
        letter-spacing: 0.12em;
        font-size: 0.82rem;
    }
    
    .nav-pills {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
    }
    
    .nav-pill {
        background: rgba(14, 165, 233, 0.12);
        color: #e0f2fe !important;
        border: 1px solid rgba(125, 211, 252, 0.3);
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        font-size: 0.72rem;
        font-weight: 700;
    }
    
    .image-showcase {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin: 1rem 0 1.5rem 0;
    }
    
    .image-tile {
        background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(15,23,42,0.8)),
                    url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=900&q=80') center/cover no-repeat;
        min-height: 220px;
        border-radius: 20px;
        padding: 1rem;
        display: flex;
        align-items: end;
        box-shadow: 0 16px 35px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    .image-tile:nth-child(2) {
        background: linear-gradient(135deg, rgba(6,182,212,0.16), rgba(15,23,42,0.8)),
                    url('https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80') center/cover no-repeat;
    }
    
    .image-tile:nth-child(3) {
        background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(15,23,42,0.8)),
                    url('https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80') center/cover no-repeat;
    }
    
    .image-tile h4 {
        margin: 0;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.1rem;
        text-shadow: 0 2px 12px rgba(0,0,0,0.22);
    }
    
    .cta-strip {
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        color: white !important;
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin: 1rem 0 1.5rem 0;
        box-shadow: 0 16px 35px rgba(14, 165, 233, 0.22);
    }
    
    .cta-strip h4 {
        color: white !important;
        margin: 0 0 0.3rem 0;
        font-weight: 800 !important;
    }
    
    .cta-strip p {
        color: #ecfeff !important;
        margin: 0;
        font-weight: 600 !important;
    }
    
    .market-strip {
        background: linear-gradient(135deg, #f8fbff 0%, #ecfeff 100%);
        border: 1px solid #bae6fd;
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin: 0 0 1.5rem 0;
        box-shadow: 0 10px 24px rgba(14, 165, 233, 0.08);
    }
    
    .value-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
        height: 100%;
        transition: all 0.25s ease;
    }
    
    .value-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 28px rgba(14, 165, 233, 0.12);
    }
    
    .value-card .small-tag {
        display: inline-block;
        background: #dbeafe;
        color: #0369a1;
        border-radius: 999px;
        padding: 0.35rem 0.7rem;
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    .value-card h4 {
        color: #0f172a !important;
        margin: 0 0 0.5rem 0;
        font-weight: 800 !important;
    }
    
    .value-card p {
        color: #475569 !important;
        margin: 0;
        font-weight: 600 !important;
    }
    
    .process-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        border: 1px solid #bae6fd;
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        height: 100%;
    }
    
    .process-card .step-no {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        color: white;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.8rem auto;
    }
    
    .process-card h4 {
        color: #0f172a !important;
        font-weight: 800 !important;
        margin: 0 0 0.4rem 0;
    }
    
    .process-card p {
        color: #475569 !important;
        margin: 0;
        font-weight: 600 !important;
    }
    
    .testimonial-card {
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 1.25rem;
        color: #e2e8f0 !important;
        height: 100%;
    }
    
    .testimonial-card p {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    
    .testimonial-card strong {
        color: #ffffff !important;
    }
    
    .pricing-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.4rem;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        height: 100%;
    }

    .service-icon {
        width: 48px;
        height: 48px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: #e0f2fe;
        color: #0284c7;
        margin-bottom: 0.9rem;
    }

    .service-icon .material-symbols-rounded {
        font-size: 26px;
        line-height: 1;
    }

    .pricing-card.popular .service-icon {
        background: #cffafe;
        color: #0891b2;
    }
    
    .pricing-card.popular {
        border: 2px solid #0ea5e9;
        box-shadow: 0 18px 30px rgba(14, 165, 233, 0.12);
    }
    
    .price-badge {
        display: inline-block;
        background: #dbeafe;
        color: #0369a1;
        border-radius: 999px;
        padding: 0.4rem 0.8rem;
        font-size: 0.72rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }
    
    .pricing-card h4 {
        color: #0f172a !important;
        font-weight: 800 !important;
        margin: 0 0 0.5rem 0;
    }
    
    .pricing-card p, .pricing-card li {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        color: #ffffff !important;
        border-radius: 999px;
        padding: 0.45rem 0.9rem;
        font-size: 0.7rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
        letter-spacing: 0.04em;
    }
    
    .button-primary {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4) !important;
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .button-primary:hover {
        background: linear-gradient(135deg, #0284c7, #0891b2) !important;
    }
    
    .lead-item {
        background: linear-gradient(135deg, #ecf0f1 0%, #f8f9fa 100%);
        border-left: 5px solid #0ea5e9;
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    .lead-item b {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    .stTabs [role="tablist"] {
        background: transparent;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .stTabs [role="tab"] {
        color: #64748b !important;
        font-weight: 600;
        border-bottom: 3px solid transparent !important;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        color: #0ea5e9 !important;
        border-bottom: 3px solid #0ea5e9 !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
        border-left: 5px solid #22c55e;
        padding: 1rem;
        border-radius: 8px;
        color: #15803d !important;
    }
    
    .success-box h3 {
        color: #15803d !important;
        font-weight: 800 !important;
    }
    
    .success-box p {
        color: #15803d !important;
        font-weight: 600 !important;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
        border-left: 5px solid #0ea5e9;
        padding: 1rem;
        border-radius: 8px;
        color: #0c4a6e !important;
    }
    
    .info-box h3 {
        color: #0284c7 !important;
        font-weight: 800 !important;
        margin-top: 0 !important;
    }
    
    .info-box p {
        color: #0c4a6e !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 44px !important;
        height: 44px !important;
        padding: 0 16px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        line-height: 1.15 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: normal !important;
        transition: all 0.3s !important;
    }

    .stButton > button p {
        margin: 0 !important;
        line-height: 1.15 !important;
    }

    [data-testid="stHorizontalBlock"] .stButton,
    [data-testid="stHorizontalBlock"] .stButton > button {
        width: 100% !important;
    }

    .pricing-card + div,
    .property-card + div {
        margin-top: 0.75rem !important;
    }

    .pricing-card + div .stButton > button {
        min-height: 42px !important;
        height: 42px !important;
    }

    .page-navigation-label {
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 0.45rem 0;
    }

    .page-navigation-label + [data-testid="stHorizontalBlock"] .stButton > button {
        min-height: 40px !important;
        height: 40px !important;
        padding: 0 10px !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stHorizontalBlock"] [data-testid="stHorizontalBlock"] .stButton > button {
        min-width: 44px !important;
        padding: 0 8px !important;
        font-size: 1.05rem !important;
    }

    /* TEXT OVERFLOW FIXES */
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }

    [data-testid="stSidebar"] .stButton button {
        width: 100% !important;
        text-align: left !important;
        padding-left: 12px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* SIDEBAR LAYOUT FIXES */
    [data-testid="stSidebar"] > div {
        padding: 1rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    /* ICON TEXT ALIGNMENT FIX */
    .stButton button kbd,
    .stButton button .material-icons,
    .stButton button span {
        vertical-align: middle !important;
        display: inline-flex !important;
        align-items: center !important;
    }

    /* NAVIGATION PILLS FIX */
    .nav-pills {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
        align-items: center !important;
    }

    .nav-pill {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: inline-flex !important;
        align-items: center !important;
    }

    /* Akhi visual system */
    :root {
        --akhi-ink: #102a43;
        --akhi-blue: #1769aa;
        --akhi-cyan: #2bb3c0;
        --akhi-mist: #eef7f8;
        --akhi-line: #d7e4ea;
        --akhi-shadow: 0 18px 45px rgba(16, 42, 67, 0.10);
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 8% 4%, rgba(43, 179, 192, 0.11), transparent 26rem),
            linear-gradient(135deg, #fbfdfe 0%, #f2f7f8 100%) !important;
    }

    .main .block-container {
        max-width: 1320px;
        padding: 1.35rem clamp(1rem, 3vw, 2.6rem) 4rem;
    }

    .top-brand-bar {
        align-items: center;
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid var(--akhi-line);
        border-radius: 16px;
        box-shadow: var(--akhi-shadow);
        backdrop-filter: blur(14px);
        padding: 0.8rem 1rem;
    }

    .brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        color: var(--akhi-ink) !important;
        font-size: 0.88rem;
        letter-spacing: 0.09em;
    }

    .brand-badge::before {
        content: "A";
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--akhi-blue), var(--akhi-cyan));
        color: #fff;
        font-size: 1rem;
        letter-spacing: 0;
        box-shadow: 0 7px 16px rgba(23, 105, 170, 0.24);
    }

    .nav-pill {
        background: var(--akhi-mist);
        border-color: #c8e6e8;
        color: var(--akhi-blue) !important;
        padding: 0.42rem 0.7rem;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        max-width: 200px !important;
    }

    /* SIDEBAR BUTTON TEXT FIX */
    [data-testid="stSidebar"] button {
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    [data-testid="stSidebar"] button span {
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow: visible !important;
    }

    /* ICON CONTAINER FIX */
    [data-testid="stSidebar"] button div {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    /* SPECIFIC SIDEBAR BUTTON FIXES */
    [data-testid="stSidebar"] [kind="primary"] button {
        justify-content: center !important;
        text-align: center !important;
    }

    [data-testid="stSidebar"] [kind="secondary"] button {
        justify-content: flex-start !important;
        text-align: left !important;
    }

    /* COLUMN BUTTONS IN SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        min-width: auto !important;
    }

    /* TAB FIXES */
    [data-testid="stSidebar"] [data-testid="stTabs"] {
        width: 100% !important;
    }

    [data-testid="stSidebar"] [role="tablist"] {
        width: 100% !important;
    }

    [data-testid="stSidebar"] [role="tab"] {
        flex: 1 !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    .hero-banner {
        border-radius: 22px;
        padding: clamp(2.8rem, 7vw, 5.5rem) clamp(1.4rem, 5vw, 4rem);
        text-align: left;
        background:
            linear-gradient(110deg, rgba(16, 42, 67, 0.98), rgba(23, 105, 170, 0.90) 58%, rgba(43, 179, 192, 0.86)),
            url('https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1800&q=85') center/cover;
        box-shadow: 0 24px 55px rgba(16, 42, 67, 0.20);
    }

    .hero-banner h1 {
        max-width: 760px;
        font-size: clamp(2.1rem, 5vw, 4.25rem);
        line-height: 1.02;
        letter-spacing: 0;
    }

    .hero-banner p {
        max-width: 700px;
        line-height: 1.6;
    }

    .section-heading {
        color: var(--akhi-ink) !important;
        font-size: clamp(1.35rem, 2vw, 1.85rem);
        letter-spacing: 0;
        border-left: 4px solid var(--akhi-cyan);
        padding-left: 0.8rem;
    }

    .pricing-card, .premium-panel, .feature-card, .process-card, .value-card {
        border-color: var(--akhi-line);
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(16, 42, 67, 0.06);
    }

    .pricing-card {
        min-height: 245px;
        padding: 1.35rem;
    }

    .pricing-card h4, .premium-panel h3, .feature-card h3 {
        color: var(--akhi-ink) !important;
        letter-spacing: 0;
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--akhi-line);
        border-radius: 12px;
        padding: 0.8rem;
        box-shadow: 0 8px 20px rgba(16, 42, 67, 0.05);
    }

    @media (max-width: 700px) {
        .top-brand-bar { position: static; }
        .nav-pills { gap: 0.35rem; }
        .hero-banner { text-align: left; }
        .image-showcase { grid-template-columns: 1fr; }
        .image-tile { min-height: 150px; }
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0284c7, #0891b2) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3) !important;
    }
    
    a {
        color: #0ea5e9 !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #0284c7 !important;
        text-decoration: underline;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900 !important;
        color: #ffffff !important;
        line-height: 1.1;
        text-shadow: 0 3px 14px rgba(15, 23, 42, 0.20);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #ecfeff !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em;
    }
    
    .stat-box .metric-value {
        color: #ffffff !important;
        font-size: 2.7rem !important;
    }
    
    .stat-box .metric-label {
        color: #f0f9ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_clean_data() -> object:
    return clean_real_estate_data(load_real_estate_data())


def money(value: float | int | None) -> str:
    if value is None or value != value:
        return "0.00"
    return f"{float(value):,.2f}"


def show_shortlist():
    st.subheader("™ Your property shortlist")
    saved_properties = st.session_state.saved_properties
    if not saved_properties:
        st.info("Your shortlist is empty. Save properties from Browse properties to compare them here.")
        if st.button("Browse properties", key="empty_shortlist_browse", type="primary"):
            st.session_state.page = "explore"
            st.rerun()
        return

    st.caption(f"{len(saved_properties)} saved properties ready for review")
    for position, property_data in enumerate(saved_properties):
        col1, col2, col3, col4 = st.columns([2.2, 1, 1, 1])
        with col1:
            st.markdown(f"**{property_data['Locality']}**  \n{int(property_data['BHK_Count'])} BHK  {int(property_data['Area']):,} sqft")
        with col2:
            st.metric("Price", f"{property_data['Price'] / 10000000:.2f} Cr")
        with col3:
            st.metric("Rate", f"{property_data.get('Rate per sqft', 0):,.0f}")
        with col4:
            if st.button("Remove", key=f"remove_saved_{position}"):
                property_id = f"{property_data['Locality']}|{property_data['Area']}|{property_data['Price']}"
                remove_shortlist_item(st.session_state.get("current_email", ""), property_id)
                st.session_state.saved_properties.pop(position)
                st.rerun()
        st.divider()


def init_session_state():
    if "users" not in st.session_state:
        st.session_state.users = ensure_admin_account()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "current_email" not in st.session_state:
        st.session_state.current_email = ""
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "saved_properties" not in st.session_state:
        st.session_state.saved_properties = []
    if "bookings" not in st.session_state:
        st.session_state.bookings = []


init_session_state()


def show_page_navigation():
    """Two-row responsive navigation bar."""
    # Row 1: main pages
    row1 = [
        ("Home", "home", ":material/home:"),
        ("Intelligence", "intelligence", ":material/psychology:"),
        ("Explore", "explore", ":material/travel_explore:"),
        (f"Shortlist ({len(st.session_state.saved_properties)})", "shortlist", ":material/bookmark:"),
        ("Analytics", "analytics", ":material/trending_up:"),
        ("Reports", "reports", ":material/assessment:"),
    ]
    # Row 2: tools + account
    row2 = [
        ("GIS Map", "map", ":material/map:"),
        ("AI Advisor", "ask_akhi", ":material/smart_toy:"),
        ("Pricing", "pricing", ":material/loyalty:"),
        ("Advisory", "inquiry", ":material/support_agent:"),
    ]
    if st.session_state.logged_in:
        row2.insert(0, ("Dashboard", "account", ":material/account_circle:"))
    if st.session_state.is_admin:
        row2.append(("Admin", "admin", ":material/admin_panel_settings:"))

    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button {
        font-size: 0.8rem !important;
        padding: 0.4rem 0.6rem !important;
        white-space: nowrap !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        overflow-y: auto !important;
        padding-bottom: 60px !important;
    }
    </style>""", unsafe_allow_html=True)

    # Row 1
    cols1 = st.columns(len(row1))
    for col, (label, page, icon) in zip(cols1, row1):
        with col:
            btn_type = "primary" if st.session_state.page == page else "secondary"
            if st.button(label, key=f"nav1_{page}", icon=icon, type=btn_type, width='stretch'):
                st.session_state.page = page
                st.session_state.pop("selected_property", None)
                st.session_state.pop("selected_service", None)
                st.rerun()

    # Row 2
    cols2 = st.columns(len(row2))
    for col, (label, page, icon) in zip(cols2, row2):
        with col:
            btn_type = "primary" if st.session_state.page == page else "secondary"
            if st.button(label, key=f"nav2_{page}", icon=icon, type=btn_type, width='stretch'):
                st.session_state.page = page
                if page != "inquiry":
                    st.session_state.pop("selected_property", None)
                    st.session_state.pop("selected_service", None)
                st.rerun()

    st.markdown("---")



def roi_calculator():
    st.subheader(" Investment ROI Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        property_price = st.number_input(
            "Property Price ( Crore)",
            min_value=1.0,
            max_value=100.0,
            value=25.0,
            step=0.5,
            key="roi_price"
        )
    
    with col2:
        down_payment_pct = st.slider(
            "Down Payment %",
            min_value=10,
            max_value=100,
            value=20,
            step=5,
            key="roi_dp"
        )
    
    with col3:
        expected_appreciation = st.slider(
            "Expected Annual Appreciation %",
            min_value=2,
            max_value=20,
            value=7,
            step=1,
            key="roi_app"
        )
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        rental_income = st.number_input(
            "Monthly Rental Income ()",
            min_value=0,
            max_value=200000,
            value=50000,
            step=5000,
            key="roi_rent"
        )
    
    with col5:
        holding_years = st.slider(
            "Holding Period (Years)",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            key="roi_years"
        )
    
    with col6:
        maintenance_cost_pct = st.slider(
            "Annual Maintenance Cost %",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.5,
            key="roi_maint"
        )
    
    # Calculate ROI
    down_payment = property_price * (down_payment_pct / 100)
    loan_amount = property_price - down_payment
    future_value = property_price * ((1 + expected_appreciation/100) ** holding_years)
    total_rental_income = rental_income * 12 * holding_years
    maintenance_costs = property_price * (maintenance_cost_pct / 100) * holding_years
    total_profit = (future_value - property_price) + total_rental_income - maintenance_costs
    roi_percentage = (total_profit / down_payment * 100) if down_payment > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-value">{roi_percentage:.1f}%</div>
            <div class="metric-label">ROI on Investment</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-value">{total_profit/10000000:.1f} Cr</div>
            <div class="metric-label">Total Profit ({holding_years}y)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-value">{future_value/10000000:.1f} Cr</div>
            <div class="metric-label">Est. Future Value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-value">{down_payment/10000000:.1f} Cr</div>
            <div class="metric-label">Initial Investment</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed breakdown
    with st.expander(" Detailed ROI Breakdown"):
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            st.write("**Investment Details:**")
            st.write(f"€ Property Price: {property_price:.1f} Cr")
            st.write(f"€ Down Payment ({down_payment_pct}%): {down_payment:.2f} Cr")
            st.write(f"€ Loan Amount: {loan_amount:.2f} Cr")
        
        with breakdown_col2:
            st.write("**Returns Details:**")
            st.write(f"€ Capital Appreciation: {(future_value - property_price)/10000000:.2f} Cr")
            st.write(f"€ Rental Income ({holding_years} years): {total_rental_income/10000000:.2f} Cr")
            st.write(f"€ Maintenance Cost: -{maintenance_costs/10000000:.2f} Cr")


def emi_calculator():
    st.subheader("Home loan EMI calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        loan_amount = st.number_input("Loan amount ( lakh)", min_value=1.0, value=80.0, step=5.0, key="emi_amount")
    with col2:
        interest_rate = st.number_input("Interest rate (%)", min_value=1.0, max_value=20.0, value=8.5, step=0.1, key="emi_rate")
    with col3:
        loan_years = st.number_input("Tenure (years)", min_value=1, max_value=30, value=20, step=1, key="emi_years")

    monthly_rate = interest_rate / 1200
    months = loan_years * 12
    principal = loan_amount * 100000
    emi = principal / months if monthly_rate == 0 else principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    total_payment = emi * months
    result_col1, result_col2, result_col3 = st.columns(3)
    result_col1.metric("Monthly EMI", f"{emi:,.0f}")
    result_col2.metric("Total interest", f"{total_payment - principal:,.0f}")
    result_col3.metric("Total payment", f"{total_payment:,.0f}")


def rental_yield_calculator():
    st.subheader("Rental yield calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        purchase_price = st.number_input("Purchase price ( lakh)", min_value=1.0, value=150.0, step=5.0, key="yield_price")
    with col2:
        monthly_rent = st.number_input("Monthly rent ()", min_value=0, value=45000, step=1000, key="yield_rent")
    with col3:
        annual_costs = st.number_input("Annual costs ()", min_value=0, value=60000, step=5000, key="yield_costs")

    annual_income = monthly_rent * 12
    net_income = annual_income - annual_costs
    gross_yield = annual_income / (purchase_price * 100000) * 100
    net_yield = net_income / (purchase_price * 100000) * 100
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross yield", f"{gross_yield:.2f}%")
    col2.metric("Net yield", f"{net_yield:.2f}%")
    col3.metric("Annual net income", f"{net_income:,.0f}")


def buy_vs_rent_calculator():
    st.subheader("Buy vs rent calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        property_price = st.number_input("Property price ( lakh)", min_value=1.0, value=150.0, step=5.0, key="bvr_price")
    with col2:
        monthly_rent = st.number_input("Monthly rent ()", min_value=0, value=45000, step=1000, key="bvr_rent")
    with col3:
        horizon = st.slider("Decision horizon (years)", min_value=1, max_value=20, value=7, key="bvr_years")

    annual_rent = monthly_rent * 12
    rent_cost = annual_rent * horizon * 1.05
    ownership_cost = property_price * 100000 * 0.08 * horizon
    rent_advantage = rent_cost < ownership_cost
    st.metric("Estimated rent cost", f"{rent_cost:,.0f}")
    st.metric("Estimated ownership costs", f"{ownership_cost:,.0f}")
    st.success("Rent is financially lighter for this horizon." if rent_advantage else "Buying may be stronger for this horizon.")


def valuation_tool(df):
    st.subheader("Property valuation")
    col1, col2, col3 = st.columns(3)
    with col1:
        locality = st.selectbox("Locality", sorted(df["Locality"].dropna().unique()), key="valuation_locality")
    with col2:
        property_type = st.selectbox("Property type", sorted(df["Property Type"].dropna().unique()), key="valuation_type")
    with col3:
        area = st.number_input("Area (sqft)", min_value=300, max_value=50000, value=1500, step=50, key="valuation_area")
    bhk_values = sorted(int(value) for value in df["BHK_Count"].dropna().unique() if 0 <= value <= 6)
    bhk = st.selectbox("BHK", bhk_values, key="valuation_bhk")

    comparable = df[(df["Locality"] == locality) & (df["Property Type"] == property_type) & (df["BHK_Count"] == bhk)]
    if comparable.empty:
        comparable = df[(df["Locality"] == locality) & (df["BHK_Count"] == bhk)]
    if comparable.empty:
        st.warning("No comparable listings found for this combination.")
        return
    rate = comparable["Rate per sqft"].median()
    estimate = rate * area
    st.metric("Estimated market value", f"{estimate / 10000000:.2f} Cr")
    st.caption(f"Comparable listings: {len(comparable):,}  Median rate: {rate:,.0f}/sqft")
    st.dataframe(comparable[["Locality", "Property Type", "BHK_Count", "Area", "Price", "Rate per sqft"]].head(8), hide_index=True, width='stretch')


def price_prediction(df):
    st.subheader(" AI Price Prediction")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        locality = st.selectbox(
            "Select Locality",
            sorted(df["Locality"].dropna().unique().tolist())[:100],
            key="pred_locality"
        )
    
    with col2:
        bhk = st.selectbox(
            "BHK",
            sorted(int(value) for value in df["BHK_Count"].dropna().unique() if 0 <= value <= 6),
            key="pred_bhk"
        )
    
    with col3:
        area = st.number_input(
            "Area (sqft)",
            min_value=500,
            max_value=50000,
            value=2000,
            step=100,
            key="pred_area"
        )
    
    property_types = sorted(df["Property Type"].dropna().unique().tolist())
    property_type = st.selectbox("Property type", property_types, key="pred_property_type")

    try:
        predicted_price = predict_price(area, bhk, locality, property_type)
        st.markdown(f"""
        <div class="info-box">
            <h3 style="margin-top: 0;"> Model-based predicted price</h3>
            <h2 style="color: #0ea5e9; margin: 0.5rem 0;">{predicted_price/10000000:.2f} - {(predicted_price * 1.15)/10000000:.2f} Cr</h2>
            <p style="margin: 0;">Estimated from area, BHK, locality and property type.</p>
        </div>
        """, unsafe_allow_html=True)
    except (FileNotFoundError, ValueError, OSError) as error:
        st.error(f"Prediction unavailable: {error}")


def property_comparison(df):
    st.subheader(" Compare Properties")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        compare_count = st.radio(
            "Properties to Compare",
            [2, 3, 4],
            key="comp_count",
            horizontal=True
        )
    
    properties_to_compare = []
    
    for i in range(compare_count):
        st.write(f"**Property {i+1}:**")
        cols = st.columns(3)
        
        with cols[0]:
            locality = st.selectbox(
                "Locality",
                sorted(df["Locality"].dropna().unique().tolist())[:50],
                key=f"comp_loc_{i}"
            )
        
        with cols[1]:
            bhk = st.selectbox(
                "BHK",
                [1, 2, 3, 4, 5],
                key=f"comp_bhk_{i}"
            )
        
        with cols[2]:
            area = st.number_input(
                "Area (sqft)",
                min_value=500,
                max_value=50000,
                value=2000,
                step=100,
                key=f"comp_area_{i}"
            )
        
        # Match the closest real listing instead of requiring an exact area value.
        prop_data = df[(df["Locality"] == locality) & (df["BHK_Count"] == bhk)].copy()
        if not prop_data.empty:
            prop_data["area_distance"] = (prop_data["Area"] - area).abs()
            prop_data = prop_data.sort_values("area_distance").iloc[0:1]
        if not prop_data.empty:
            properties_to_compare.append({
                "locality": locality,
                "bhk": bhk,
                "area": area,
                "price": prop_data.iloc[0]["Price"],
                "rate_per_sqft": prop_data.iloc[0].get("Rate per sqft", 0),
                "property_type": prop_data.iloc[0]["Property Type"]
            })
        else:
            properties_to_compare.append({
                "locality": locality,
                "bhk": bhk,
                "area": area,
                "price": 0,
                "rate_per_sqft": 0,
                "property_type": "Unknown"
            })
    
    # Display comparison table
    if properties_to_compare:
        comparison_df = pd.DataFrame(properties_to_compare)
        st.dataframe(comparison_df, width='stretch')
        priced_properties = comparison_df[comparison_df["rate_per_sqft"] > 0]
        if not priced_properties.empty:
            best_value = priced_properties.loc[priced_properties["rate_per_sqft"].idxmin()]
            st.success(
                f"Akhi value signal: {best_value['locality']} ({int(best_value['bhk'])} BHK) has the lowest comparable rate at {best_value['rate_per_sqft']:,.0f}/sqft."
            )


def show_property_detail(df, property_data):
    st.subheader("Property details")
    if not property_data:
        st.warning("Select a property from Browse properties first.")
        return

    st.markdown(f"### {property_data.get('Locality', 'Gurugram property')}")
    st.caption(property_data.get("Society", property_data.get("Socity", "Verified listing")))
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Price", f"{float(property_data['Price']) / 10000000:.2f} Cr")
    metric_col2.metric("Area", f"{int(float(property_data['Area'])):,} sqft")
    metric_col3.metric("BHK", int(float(property_data['BHK_Count'])))
    metric_col4.metric("Rate", f"{float(property_data.get('Rate per sqft', 0)):,.0f}/sqft")

    locality_data = df[df["Locality"] == property_data.get("Locality")]
    current_rate = float(property_data.get("Rate per sqft", 0) or 0)
    median_rate = float(locality_data["Rate per sqft"].median()) if not locality_data.empty else current_rate
    value_score = max(0, min(40, 40 * median_rate / current_rate)) if current_rate else 0
    demand_score = min(30, len(locality_data) / max(len(df), 1) * 300)
    trust_score = 30 if "Approved" in str(property_data.get("RERA Approval", "")) else 10
    decision_score = round(value_score + demand_score + trust_score)
    signal = "Strong fit" if decision_score >= 75 else "Worth comparing" if decision_score >= 55 else "Needs diligence"
    st.markdown("**Akhi Decision Signal**")
    signal_col1, signal_col2, signal_col3 = st.columns(3)
    signal_col1.metric("Decision score", f"{decision_score}/100")
    signal_col2.metric("Signal", signal)
    signal_col3.metric("Locality inventory", f"{len(locality_data):,}")
    st.caption("Akhi score: 40% relative value, 30% locality activity, 30% reported RERA status. It is a screening aid, not financial or legal advice.")
    decision_brief = (
        "Akhi Properties - Decision Brief\n"
        "================================\n"
        f"Locality: {property_data.get('Locality', 'N/A')}\n"
        f"Price: INR {float(property_data.get('Price', 0)):,.0f}\n"
        f"Area: {int(float(property_data.get('Area', 0))):,} sqft\n"
        f"BHK: {int(float(property_data.get('BHK_Count', 0)))}\n"
        f"Rate: INR {current_rate:,.0f}/sqft\n"
        f"Decision score: {decision_score}/100 ({signal})\n"
        "Method: 40% relative value, 30% locality activity, 30% reported RERA status.\n"
        "Verify documents, current availability and pricing before purchase.\n"
    )
    st.download_button(
        "Download Akhi Decision Brief",
        data=decision_brief,
        file_name="akhi_decision_brief.txt",
        mime="text/plain",
        icon=":material/download:",
        width='stretch',
    )

    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        st.markdown("**Listing information**")
        st.write(f"Property type: {property_data.get('Property Type', 'Not specified')}")
        st.write(f"Status: {property_data.get('Status', 'Not specified')}")
        st.write(f"Builder: {property_data.get('Builder Name', 'Not specified')}")
    with detail_col2:
        st.markdown("**Trust signals**")
        rera_status = property_data.get("RERA Approval", "Not specified")
        if "Approved" in str(rera_status):
            st.success("RERA approval reported")
        else:
            st.warning(f"RERA status: {rera_status}")
        st.caption("Source: Gurugram real-estate dataset. Verify documents before purchase.")

    similar = df[(df["Locality"] == property_data.get("Locality")) & (df["BHK_Count"] == float(property_data.get("BHK_Count", 0)))].copy()
    if not similar.empty:
        st.markdown("**Comparable listings in this locality**")
        st.dataframe(
            similar[["Locality", "Property Type", "BHK_Count", "Area", "Price", "Rate per sqft"]].head(6),
            hide_index=True,
            width='stretch',
        )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Inquire about this property", key="detail_inquire", icon=":material/call:", type="primary", width='stretch'):
            st.session_state.selected_property = property_data
            st.session_state.page = "inquiry"
            st.rerun()
    with action_col2:
        if st.button("Back to properties", key="detail_back", icon=":material/arrow_back:", width='stretch'):
            st.session_state.page = "explore"
            st.rerun()


def sector_intelligence(df):
    st.subheader("Gurugram sector intelligence")
    sectors = sorted(df["Locality"].dropna().unique().tolist())
    sector = st.selectbox("Select sector or locality", sectors, key="sector_focus")
    scoped = df[df["Locality"] == sector]
    popular_bhk = int(scoped["BHK_Count"].mode().iloc[0])
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Inventory", f"{len(scoped):,}")
    metric_col2.metric("Average price", f"{scoped['Price'].mean() / 10000000:.2f} Cr")
    metric_col3.metric("Average rate", f"{scoped['Rate per sqft'].mean():,.0f}/sqft")
    metric_col4.metric("Popular BHK", popular_bhk)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("**Property type mix**")
        st.bar_chart(scoped["Property Type"].value_counts())
    with chart_col2:
        st.markdown("**BHK mix**")
        st.bar_chart(scoped["BHK_Count"].value_counts().sort_index())
    st.markdown("**Sector listings**")
    st.dataframe(scoped[["Property Type", "BHK_Count", "Area", "Price", "Rate per sqft", "RERA Approval"]].head(12), hide_index=True, width='stretch')


def market_reports(df):
    render_institutional_hero(
        title=" Institutional Due-Diligence Dossiers & Market Research",
        subtitle="Certified Automated Appraisals, 5-Year DCF Schedules & Institutional Sector Research",
        badges=["OFFICIAL APPRAISAL DOSSIER", "5-YR IRR UNDERWRITING", "G-REPI RATINGS"],
    )

    report_tabs = st.tabs([
        " Generate Institutional Dossier (PDF/HTML)",
        " Macro Market Snapshot",
        " Micro-Market Rankings",
    ])

    with report_tabs[0]:
        st.subheader("Generate Subject Property Due-Diligence Dossier")
        st.caption("Generate a certified, institutional-grade valuation report complete with 3-tier AVM bands, cash-flow underwriting, and regulatory disclaimers.")

        col1, col2, col3 = st.columns(3)
        localities = sorted(df["Locality"].dropna().unique().tolist())
        property_types = sorted(df["Property Type"].dropna().unique().tolist())

        with col1:
            d_loc = st.selectbox("Subject Sector / Locality", localities, key="dossier_loc")
            d_type = st.selectbox("Property Category", property_types, key="dossier_type")
        with col2:
            d_bhk = st.selectbox("BHK Configuration", [1, 2, 3, 4, 5, 6], index=2, key="dossier_bhk")
            d_area = st.number_input("Carpet Area (sqft)", min_value=350.0, max_value=20000.0, value=1850.0, step=50.0, key="dossier_area")
        with col3:
            d_ask_lakhs = st.number_input("Target / Asking Price ( Lakhs) [Optional]", min_value=15.0, value=180.0, step=5.0, key="dossier_ask")
            d_client = st.text_input("Client / Entity Name", value="Institutional Investor", key="dossier_client")

        # Run calculations
        try:
            ml_price = predict_price(d_area, d_bhk, d_loc, d_type)
        except Exception:
            ml_price = None

        avm_res = calculate_fairvalue_avm(
            area_sqft=d_area,
            bhk=d_bhk,
            locality=d_loc,
            property_type=d_type,
            df_reference=df,
            ml_predicted_price=ml_price,
        )

        cap_res = calculate_capyield_model(property_price=avm_res["fair_market_value"])
        irr_res = run_irr_projection(
            property_price=avm_res["fair_market_value"],
            holding_period_years=5,
            annual_appreciation_pct=8.5,
            gross_rental_yield_pct=cap_res["gross_yield_pct"],
        )

        # Generate HTML Dossier
        dossier_html = generate_dossier_html(
            locality=d_loc,
            bhk=d_bhk,
            area_sqft=d_area,
            property_type=d_type,
            avm_result=avm_res,
            cap_result=cap_res,
            irr_result=irr_res,
            grepi_rating="AAA (Prime Institutional)" if "54" in d_loc or "Golf" in d_loc else "AA (High Investment Grade)",
            asking_price=d_ask_lakhs * 100_000 if d_ask_lakhs > 0 else None,
            client_name=d_client,
        )

        st.markdown("---")
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            st.download_button(
                " Download Branded Institutional Dossier (HTML/PDF)",
                data=dossier_html,
                file_name=f"AREI_Due_Diligence_Dossier_{d_loc.replace(' ', '_')}.html",
                mime="text/html",
                type="primary",
                width='stretch',
            )
        with btn_col2:
            st.info(" **Print to PDF:** Click the download button, open the downloaded file in your browser, and tap 'Print / Save as PDF'!")

        # Interactive In-App Live Preview
        st.markdown("###  In-App Live Dossier Preview")
        st.components.v1.html(dossier_html, height=750, scrolling=True)

    with report_tabs[1]:
        st.subheader("Gurugram Market Snapshot")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Listings Analysed", f"{len(df):,}")
        col2.metric("Average Price", f"{df['Price'].mean() / 10000000:.2f} Cr")
        col3.metric("Median Rate", f"{df['Rate per sqft'].median():,.0f}/sqft")
        col4.metric("Micro-Markets", f"{df['Locality'].nunique():,}")

        st.markdown("**BHK Demand Distribution**")
        st.bar_chart(df["BHK_Count"].value_counts().sort_index())

    with report_tabs[2]:
        st.subheader("Top Micro-Markets by Transaction Depth")
        ranking = (
            df.groupby("Locality")
            .agg(
                inventory=("Price", "size"),
                average_price_cr=("Price", lambda p: p.mean() / 10_000_000),
                median_rate_sqft=("Rate per sqft", "median"),
            )
            .sort_values("inventory", ascending=False)
            .head(15)
            .reset_index()
        )
        st.dataframe(
            ranking.rename(
                columns={
                    "Locality": "Sector / Locality",
                    "inventory": "Tracked Listings",
                    "average_price_cr": "Average Price ( Cr)",
                    "median_rate_sqft": "Median Rate (/sqft)",
                }
            ),
            hide_index=True,
            width='stretch',
        )


def gurugram_map(df):
    render_institutional_hero(
        title=" Gurugram Geospatial Micro-Market Map",
        subtitle="Accurate Sector-Level Geographic Mapping, Capital Density & Price Heat Zones",
        badges=["GEOSPATIAL INTELLIGENCE", "REAL GPS COORDINATES", "CORRIDOR DRILL-DOWN"],
    )

    # Real Geographic Benchmark Coordinates for Gurugram Micro-Markets
    REAL_GURUGRAM_COORDINATES = {
        # Golf Course Road (Prime Blue-Chip)
        "Golf Course Road": (28.4595, 77.0965),
        "Sector 42": (28.4620, 77.0980),
        "Sector 43": (28.4580, 77.0910),
        "Sector 53": (28.4520, 77.0990),
        "Sector 54": (28.4410, 77.1080),
        "DLF Phase 1": (28.4780, 77.0990),
        "DLF Phase 5": (28.4480, 77.1020),
        # Golf Course Extension & SPR (High-Velocity Growth)
        "Golf Course Extension Road": (28.4238, 77.0825),
        "Sector 56": (28.4290, 77.1010),
        "Sector 57": (28.4210, 77.0880),
        "Sector 58": (28.4110, 77.1090),
        "Sector 59": (28.4020, 77.1050),
        "Sector 60": (28.4090, 77.0910),
        "Sector 61": (28.4060, 77.0810),
        "Sector 62": (28.4120, 77.0750),
        "Sector 63": (28.4010, 77.0720),
        "Sector 65": (28.3950, 77.0650),
        "Sector 66": (28.3910, 77.0580),
        "Sector 67": (28.3840, 77.0550),
        "Sector 68": (28.3780, 77.0490),
        "Southern Peripheral Road": (28.3980, 77.0550),
        # Dwarka Expressway (Infrastructure Corridor)
        "Dwarka Expressway": (28.5012, 76.9888),
        "Sector 88": (28.4420, 76.9690),
        "Sector 99": (28.4720, 76.9740),
        "Sector 102": (28.4890, 76.9810),
        "Sector 103": (28.4980, 76.9870),
        "Sector 104": (28.5020, 76.9940),
        "Sector 106": (28.5110, 77.0010),
        "Sector 108": (28.5190, 77.0080),
        "Sector 109": (28.5250, 77.0140),
        "Sector 110": (28.5290, 77.0210),
        "Sector 111": (28.5320, 77.0290),
        "Sector 112": (28.5360, 77.0340),
        "Sector 113": (28.5390, 77.0410),
        # Sohna Road & South Gurugram (Rental Yield Corridors)
        "Sohna Road": (28.3938, 77.0412),
        "Sector 47": (28.4280, 77.0450),
        "Sector 48": (28.4200, 77.0410),
        "Sector 49": (28.4110, 77.0370),
        "Sector 50": (28.4180, 77.0610),
        "Sector 70": (28.3890, 77.0180),
        "Sector 71": (28.3960, 77.0220),
        "Sector 72": (28.4040, 77.0280),
        "South City 2": (28.4180, 77.0540),
        # New Gurgaon (Emerging Value Hub)
        "Sector 81": (28.3880, 76.9550),
        "Sector 82": (28.3940, 76.9620),
        "Sector 83": (28.3990, 76.9690),
        "Sector 84": (28.4060, 76.9750),
        "Sector 85": (28.3910, 76.9450),
        "Sector 86": (28.3840, 76.9380),
        "Sector 89": (28.4150, 76.9420),
        "Sector 90": (28.4080, 76.9340),
        "Sector 91": (28.4010, 76.9270),
        "Sector 92": (28.3950, 76.9190),
        "Sector 93": (28.3880, 76.9120),
        "Sector 95": (28.4120, 76.9050),
        "New Gurgaon": (28.3980, 76.9480),
        # Cyber City & MG Road
        "MG Road": (28.4800, 77.0960),
        "Cyber City": (28.4920, 77.0890),
        "DLF Phase 2": (28.4850, 77.0880),
        "DLF Phase 3": (28.4950, 77.0990),
        "DLF Phase 4": (28.4680, 77.0890),
        "Sushant Lok": (28.4580, 77.0910),
        "Sector 27": (28.4690, 77.0820),
        "Sector 28": (28.4760, 77.0890),
        # Central / Old Gurgaon
        "Sector 14": (28.4710, 77.0420),
        "Sector 15": (28.4620, 77.0380),
        "Sector 17": (28.4790, 77.0490),
        "Sector 21": (28.5080, 77.0650),
        "Sector 22": (28.5010, 77.0580),
        "Sector 23": (28.5090, 77.0480),
    }

    def get_real_coords(loc_name: str) -> tuple[float, float]:
        clean_name = str(loc_name).strip()
        if clean_name in REAL_GURUGRAM_COORDINATES:
            return REAL_GURUGRAM_COORDINATES[clean_name]
        for key, coords in REAL_GURUGRAM_COORDINATES.items():
            if key.lower() in clean_name.lower():
                return coords
        # Safe centroid fallback within central Gurugram
        return (28.4590, 77.0360)

    map_data = (
        df.groupby("Locality", as_index=False)
        .agg(
            inventory=("Price", "size"),
            average_price=("Price", "mean"),
            median_rate=("Rate per sqft", "median"),
        )
    )
    map_data[["latitude", "longitude"]] = map_data["Locality"].apply(
        lambda loc: pd.Series(get_real_coords(loc))
    )

    col_filter, col_corridor = st.columns(2)
    with col_filter:
        selected_locality = st.selectbox(
            "Filter Specific Micro-Market",
            ["All Gurugram"] + sorted(map_data["Locality"].tolist()),
            key="real_map_loc",
        )
    with col_corridor:
        corridor_filter = st.selectbox(
            "Filter Corridor Zone",
            [
                "All Corridors",
                "Golf Course Road (Prime)",
                "Golf Course Extension & SPR",
                "Dwarka Expressway",
                "New Gurgaon",
                "Sohna Road",
            ],
            key="real_map_corridor",
        )

    filtered_map = map_data.copy()
    if selected_locality != "All Gurugram":
        filtered_map = filtered_map[filtered_map["Locality"] == selected_locality]
    elif corridor_filter != "All Corridors":
        if "Golf Course Road" in corridor_filter:
            filtered_map = filtered_map[filtered_map["latitude"].between(28.435, 28.485) & filtered_map["longitude"].between(77.085, 77.115)]
        elif "Extension" in corridor_filter:
            filtered_map = filtered_map[filtered_map["latitude"].between(28.375, 28.435) & filtered_map["longitude"].between(77.045, 77.105)]
        elif "Dwarka" in corridor_filter:
            filtered_map = filtered_map[filtered_map["latitude"].between(28.440, 28.540) & filtered_map["longitude"].between(76.965, 77.045)]
        elif "New Gurgaon" in corridor_filter:
            filtered_map = filtered_map[filtered_map["latitude"].between(28.375, 28.420) & filtered_map["longitude"].between(76.900, 76.980)]
        elif "Sohna Road" in corridor_filter:
            filtered_map = filtered_map[filtered_map["latitude"].between(28.370, 28.435) & filtered_map["longitude"].between(77.015, 77.065)]

    # Metrics overview
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Micro-Markets", f"{len(filtered_map)}")
    c2.metric("Tracked Units", f"{filtered_map['inventory'].sum():,}")
    c3.metric("Median Rate", f"{filtered_map['median_rate'].median():,.0f}/sqft")
    c4.metric("Average Ticket", f"{filtered_map['average_price'].mean() / 10_000_000:.2f} Cr")

    # Render Streamlit Map with coordinates
    st.map(filtered_map, latitude="latitude", longitude="longitude", size="inventory", zoom=11)

    st.markdown("###  Micro-Market Capital Heatmap Table")
    display_df = filtered_map[["Locality", "inventory", "median_rate", "average_price"]].copy()
    display_df["average_price"] = (display_df["average_price"] / 10_000_000).round(2)
    display_df["median_rate"] = display_df["median_rate"].round(0).astype(int)
    display_df = display_df.sort_values("median_rate", ascending=False)
    st.dataframe(
        display_df.rename(
            columns={
                "Locality": "Micro-Market / Sector",
                "inventory": "Active Listings",
                "median_rate": "Median Rate (/sqft)",
                "average_price": "Average Ticket ( Cr)",
            }
        ),
        hide_index=True,
        width='stretch',
    )


def ask_akhi(df):
    render_institutional_hero(
        title=" AREI Intelligent Deal Advisory Desk",
        subtitle="Natural-Language Intent Parser, G-REPI Ranked Deal Discovery & Institutional Verdicts",
        badges=["AI DEAL ADVISOR", "G-REPI MATCHED", "INSTITUTIONAL STRATEGY"],
    )

    st.markdown("###  Quick Prompt Inspiration")
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    with quick_col1:
        if st.button(" 3 BHK under 2.5 Cr in High-Velocity Corridor", width='stretch'):
            st.session_state.quick_prompt = "Suggest 3 BHK under 2.5 Cr in Dwarka Expressway or SPR"
    with quick_col2:
        if st.button(" High Rental Yield under 1.5 Cr", width='stretch'):
            st.session_state.quick_prompt = "Find high rental yield property under 1.5 Cr in Sohna Road"
    with quick_col3:
        if st.button(" Prime Blue-Chip Asset in Golf Course Road", width='stretch'):
            st.session_state.quick_prompt = "Recommend prime luxury 4 BHK in Golf Course Road"

    default_val = st.session_state.get("quick_prompt", "")
    question = st.text_area(
        "Enter your property criteria or investment strategy:",
        value=default_val,
        placeholder="e.g. Find me a 3 BHK apartment under 2.2 Cr near Dwarka Expressway with high growth potential",
        height=90,
        key="ask_akhi_question",
    )

    if not st.button(" Analyze Criteria & Recommend Deals", key="ask_akhi_submit", icon=":material/auto_awesome:", type="primary"):
        return
    if not question.strip():
        st.warning("Please describe your requirement or select a quick prompt above.")
        return

    # Parse Budget
    budget_crore = None
    b_cr_match = re.search(r"(?:|rs\.?\s*)?(\d+(?:\.\d+)?)\s*(?:cr|crore|•)", question.lower())
    if b_cr_match:
        budget_crore = float(b_cr_match.group(1))
    else:
        b_lakh_match = re.search(r"(?:|rs\.?\s*)?(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)", question.lower())
        if b_lakh_match:
            budget_crore = float(b_lakh_match.group(1)) / 100.0

    # Parse BHK
    bhk_match = re.search(r"(\d+)\s*[- ]?\s*bhk", question.lower())
    bhk = int(bhk_match.group(1)) if bhk_match else None

    # Parse Corridor Keywords
    corridor_focus = None
    q_low = question.lower()
    if "golf course road" in q_low or "dlf" in q_low:
        corridor_focus = "Golf Course Road"
    elif "dwarka" in q_low or "expressway" in q_low:
        corridor_focus = "Dwarka Expressway"
    elif "extension" in q_low or "spr" in q_low or "sector 65" in q_low:
        corridor_focus = "Extension"
    elif "sohna" in q_low:
        corridor_focus = "Sohna Road"
    elif "new gurgaon" in q_low or "sector 8" in q_low or "sector 9" in q_low:
        corridor_focus = "New Gurgaon"

    recommendations = df.copy()
    if budget_crore is not None:
        recommendations = recommendations[recommendations["Price"] <= budget_crore * 10_000_000]
    if bhk is not None and 0 <= bhk <= 6:
        recommendations = recommendations[recommendations["BHK_Count"] == bhk]
    if corridor_focus is not None:
        recommendations = recommendations[recommendations["Locality"].str.contains(corridor_focus, case=False, na=False)]

    if recommendations.empty:
        st.warning("No direct listings matched all filters simultaneously. Expanding search across neighboring sectors...")
        recommendations = df[df["Price"] <= (budget_crore * 10_000_000 if budget_crore else df["Price"].quantile(0.75))].head(20)

    # Strategy commentary
    st.markdown("---")
    st.markdown("###  Institutional Deal Strategy & Advisory Verdict")
    if corridor_focus:
        st.info(f" **Corridor Assessment ({corridor_focus}):** This micro-market currently offers favorable risk-adjusted returns based on infrastructure progress and corporate tenant absorption.")
    else:
        st.info(" **Balanced Allocation Strategy:** We recommend prioritizing sectors with G-REPI rating of AA or higher to maintain liquidity and minimize capital drawdown.")

    st.markdown(f"**Found {len(recommendations):,} Institutional Matches** (Displaying Top Opportunities):")
    display_cols = ["Locality", "Property Type", "BHK_Count", "Area", "Price", "Rate per sqft", "RERA Approval"]
    avail_cols = [c for c in display_cols if c in recommendations.columns]

    formatted_rec = recommendations.sort_values(by=["Rate per sqft", "Price"]).head(10).copy()
    formatted_rec["Price ( Cr)"] = (formatted_rec["Price"] / 10_000_000).round(2)
    formatted_rec["Rate (/sqft)"] = formatted_rec["Rate per sqft"].round(0).astype(int)

    st.dataframe(
        formatted_rec[["Locality", "Property Type", "BHK_Count", "Area", "Price ( Cr)", "Rate (/sqft)", "RERA Approval"]],
        hide_index=True,
        width='stretch',
    )

    st.markdown("###  Next Step: Private Advisory & Deal Closing")
    ad_col1, ad_col2 = st.columns(2)
    with ad_col1:
        if st.button(" Request Priority Deal Consultation", type="primary", width='stretch'):
            st.session_state.selected_service = f"AI Advisory Match ({bhk or 3} BHK € {budget_crore or 2:.1f} Cr)"
            st.session_state.page = "inquiry"
            st.rerun()
    with ad_col2:
        quick_msg = urllib.parse.quote(f"Hi Akhi, I used the AI Deal Advisor for: {question[:100]}. Can you share curated private inventory?")
        st.link_button(
            " WhatsApp Senior Broker for Off-Market Options",
            url=f"{WHATSAPP}?text={quick_msg}",
            icon=":material/chat:",
        )



def user_dashboard():
    if not st.session_state.logged_in:
        st.error("Please log in to view your dashboard.")
        return

    email = st.session_state.current_email
    user = st.session_state.users.get(email, {})
    leads = [lead for lead in load_leads() if lead.get("email") == email]
    st.subheader("My Akhi dashboard")
    st.caption(f"Welcome back, {user.get('name', st.session_state.current_user)}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saved properties", len(st.session_state.saved_properties))
    col2.metric("Enquiries", len(leads))
    col3.metric("Account type", "Admin" if st.session_state.is_admin else "Buyer")
    col4.metric("Status", "Active")

    tab1, tab2, tab3 = st.tabs(["Profile", "My shortlist", "My enquiries"])
    with tab1:
        st.markdown("**Profile details**")
        st.write(f"Name: {user.get('name', 'N/A')}")
        st.write(f"Email: {email}")
        st.write(f"Phone: {user.get('phone', 'N/A')}")
        st.info("Your credentials are protected with PBKDF2-SHA256 password hashing.")
    with tab2:
        if st.session_state.saved_properties:
            shortlist = pd.DataFrame(st.session_state.saved_properties)
            columns = [column for column in ["Locality", "Property Type", "BHK_Count", "Area", "Price", "Rate per sqft", "Status"] if column in shortlist.columns]
            st.dataframe(shortlist[columns], hide_index=True, width='stretch')
            if st.button("Open shortlist", key="dashboard_shortlist", icon=":material/favorite:"):
                st.session_state.page = "shortlist"
                st.rerun()
        else:
            st.info("No saved properties yet. Browse properties to build your shortlist.")
    with tab3:
        if leads:
            enquiry_df = pd.DataFrame(leads)
            columns = [column for column in ["service", "property", "interest", "budget", "timestamp"] if column in enquiry_df.columns]
            st.dataframe(enquiry_df[columns], hide_index=True, width='stretch')
        else:
            st.info("No enquiries submitted yet.")


def property_intelligence(df):
    render_institutional_hero(
        title=" Akhi Real Estate Intelligence (AREI)",
        subtitle="Proprietary Micro-Market Benchmarks, Automated Valuation (AVM) & Institutional Investment Modeling",
        badges=[
            " G-REPI INDEX",
            " FAIRVALUE AVM",
            " CAPYIELD LAB",
            " CORRIDOR QUADRANT",
        ],
    )

    intel_tabs = st.tabs([
        " G-REPI Market Pulse",
        " Corridor Quadrants",
        " FairValue AVM Lab",
        " CapYield Financial Lab",
        " Developer & Supply Lens",
    ])

    # -------------------------------------------------------------
    # TAB 1: G-REPI MARKET PULSE
    # -------------------------------------------------------------
    with intel_tabs[0]:
        st.subheader("Gurugram Real Estate Performance Index (G-REPI)")
        st.caption("A proprietary composite statistical index (0 - 100) benchmarking liquidity, pricing stability, and transaction depth across Gurugram micro-markets.")

        grepi_df = calculate_grepi_index(df)

        if not grepi_df.empty:
            m1, m2, m3, m4 = st.columns(4)
            top_market = grepi_df.iloc[0]["Locality"]
            top_score = grepi_df.iloc[0]["grepi_score"]
            city_median_rate = int(df["Rate per sqft"].median())
            total_market_depth = grepi_df["total_market_depth_cr"].sum()

            m1.metric("Highest G-REPI Rank", f"{top_market}", f"Score: {top_score}")
            m2.metric("City Benchmark Rate", f"{city_median_rate:,}/sqft", "Median Equilibrium")
            m3.metric("Tracked Market Depth", f"{total_market_depth:,.0f} Cr", f"{len(grepi_df)} Micro-markets")
            m4.metric("Prime Institutional (AAA)", f"{(grepi_df['institutional_grade'].str.contains('AAA')).sum()} Localities")

            st.markdown("---")

            col_search, col_grade = st.columns([2, 1])
            with col_search:
                search_query = st.text_input(" Search Micro-Market / Sector", placeholder="e.g. Sector 56, Golf Course...")
            with col_grade:
                grade_filter = st.selectbox("Filter Institutional Grade", ["All Grades", "AAA", "AA", "A", "BBB", "BB"])

            filtered_grepi = grepi_df.copy()
            if search_query:
                filtered_grepi = filtered_grepi[filtered_grepi["Locality"].str.contains(search_query, case=False, na=False)]
            if grade_filter != "All Grades":
                filtered_grepi = filtered_grepi[filtered_grepi["institutional_grade"].str.contains(grade_filter)]

            st.dataframe(
                filtered_grepi.rename(
                    columns={
                        "rank": "Rank",
                        "Locality": "Micro-Market / Sector",
                        "grepi_score": "G-REPI Score",
                        "institutional_grade": "Rating Grade",
                        "inventory_depth": "Inventory Count",
                        "median_rate_sqft": "Median Rate (/sqft)",
                        "avg_price_cr": "Median Ticket ( Cr)",
                        "total_market_depth_cr": "Capital Depth ( Cr)",
                    }
                ),
                hide_index=True,
                width='stretch',
            )
            st.info(" **Methodology:** G-REPI evaluates micro-markets using logarithmic rate position (40%), inventory depth velocity (35%), and standard deviation price stability (25%).")

    # -------------------------------------------------------------
    # TAB 2: CORRIDOR GROWTH QUADRANTS
    # -------------------------------------------------------------
    with intel_tabs[1]:
        st.subheader("Corridor Growth Quadrant Matrix")
        st.caption("Strategic institutional classification of Gurugram investment corridors by risk profile, capital growth velocity, and rental yield potential.")

        corridors_df = classify_corridor_quadrants(df)

        for _, row in corridors_df.iterrows():
            with st.expander(f"{row['Corridor']} € {row['quadrant']}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Median Rate", f"{row['median_rate_sqft']:,}/sqft")
                c2.metric("Median Ticket Size", f"{row['median_price_cr']:.2f} Cr")
                c3.metric("Inventory Volume", f"{row['inventory']} units")

                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; padding:0.9rem 1.2rem; border-radius:12px; border-left:4px solid #0284C7; margin-top:0.5rem;">
                        <span style="font-weight:700; color:#0F172A;">Investment Persona:</span> {row['tagline']}<br/>
                        <b>Risk Profile:</b> <span style="color:#0284C7;">{row['risk_profile']}</span> € 
                        <b>Yield Outlook:</b> <span style="color:#10B981;">{row['yield_outlook']}</span> € 
                        <b>Growth Outlook:</b> <span style="color:#D4AF37;">{row['growth_outlook']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown("**Corridor Summary Matrix**")
        st.dataframe(
            corridors_df[["Corridor", "quadrant", "median_rate_sqft", "median_price_cr", "inventory", "growth_outlook", "risk_profile"]].rename(
                columns={
                    "quadrant": "Classification",
                    "median_rate_sqft": "Median Rate (/sqft)",
                    "median_price_cr": "Median Price ( Cr)",
                    "inventory": "Tracked Listings",
                    "growth_outlook": "Capital Growth",
                    "risk_profile": "Risk Rating",
                }
            ),
            hide_index=True,
            width='stretch',
        )

    # -------------------------------------------------------------
    # TAB 3: FAIRVALUE AVM LAB
    # -------------------------------------------------------------
    with intel_tabs[2]:
        st.subheader("Akhi FairValue AVM (Automated Valuation Model)")
        st.caption("Independent institutional appraisal engine generating 3-tier confidence bands and over/under-valuation acquisition guidance.")

        avm_col1, avm_col2 = st.columns(2)
        localities = sorted(df["Locality"].dropna().unique().tolist())
        property_types = sorted(df["Property Type"].dropna().unique().tolist())

        with avm_col1:
            avm_locality = st.selectbox("Subject Locality / Sector", localities, key="avm_loc")
            avm_prop_type = st.selectbox("Property Type", property_types, key="avm_ptype")
            avm_area = st.number_input("Carpet / Super Area (sqft)", min_value=300.0, max_value=25000.0, value=1850.0, step=50.0, key="avm_area_input")

        with avm_col2:
            avm_bhk = st.selectbox("BHK Configuration", [1, 2, 3, 4, 5, 6], index=2, key="avm_bhk_input")
            asking_price_lakhs = st.number_input("Asking / Target Price ( Lakhs) [Optional for Barometer]", min_value=10.0, max_value=5000.0, value=175.0, step=5.0, key="avm_asking_input")
            asking_price_total = asking_price_lakhs * 100_000

        # Calculate ML prediction baseline
        try:
            ml_price = predict_price(avm_area, avm_bhk, avm_locality, avm_prop_type)
        except Exception:
            ml_price = None

        avm_result = calculate_fairvalue_avm(
            area_sqft=avm_area,
            bhk=avm_bhk,
            locality=avm_locality,
            property_type=avm_prop_type,
            df_reference=df,
            ml_predicted_price=ml_price,
        )

        st.markdown("---")
        st.markdown("###  Institutional Valuation Confidence Bands")
        render_avm_three_tier_cards(avm_result)

        if asking_price_total > 0:
            st.markdown("###  Over / Undervalued Barometer")
            gauge_result = get_valuation_gauge(asking_price_total, avm_result["fair_market_value"])
            render_valuation_gauge_card(gauge_result, asking_price_total / 10_000_000)

    # -------------------------------------------------------------
    # TAB 4: CAPYIELD FINANCIAL LAB
    # -------------------------------------------------------------
    with intel_tabs[3]:
        st.subheader("CapYield Financial & IRR Modeling Lab")
        st.caption("Institutional cash-flow underwriting, Net Operating Income (NOI), Capitalization Rate (Cap Rate), and 5-Year IRR forecasting.")

        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            prop_cost_lakhs = st.number_input("Acquisition Price ( Lakhs)", min_value=15.0, value=160.0, step=5.0, key="cap_cost")
            property_price_val = prop_cost_lakhs * 100_000
        with fcol2:
            expected_rent = st.number_input("Expected Monthly Rent ()", min_value=5000, value=52000, step=2000, key="cap_rent")
        with fcol3:
            holding_horizon = st.selectbox("Investment Horizon", [3, 5, 7, 10], index=1, key="cap_horizon")

        appreciation_rate = st.slider("Expected Annual Capital Growth (%)", min_value=3.0, max_value=16.0, value=8.5, step=0.5, key="cap_growth")

        cap_results = calculate_capyield_model(property_price_val, expected_rent)
        irr_results = run_irr_projection(
            property_price=property_price_val,
            holding_period_years=holding_horizon,
            annual_appreciation_pct=appreciation_rate,
            gross_rental_yield_pct=cap_results["gross_yield_pct"],
        )

        st.markdown("---")
        y1, y2, y3, y4 = st.columns(4)
        y1.metric("Gross Rental Yield", f"{cap_results['gross_yield_pct']:.2f}%")
        y2.metric("Net Cap Rate", f"{cap_results['cap_rate_pct']:.2f}%", "After OpEx & Vacancy")
        y3.metric("Price-to-Rent Ratio", f"{cap_results['price_to_rent_ratio']:.1f}", cap_results["prr_verdict"])
        y4.metric(f"{holding_horizon}-Yr Annualized IRR", f"{irr_results['annualized_irr_pct']:.1f}%", f"Total Gain: {irr_results['total_net_gain_cr']:.2f} Cr")

        st.markdown("###  Financial Cash-Flow & Terminal Value Schedule")
        st.dataframe(irr_results["schedule_df"], hide_index=True, width='stretch')

        st.info(
            f" **Exit Strategy Summary:** An initial capital outlay of {irr_results['initial_investment_cr']:.2f} Cr (including equity downpayment & registration buffer) projected to yield a terminal asset value of {irr_results['terminal_asset_value_cr']:.2f} Cr after {holding_horizon} years."
        )

    # -------------------------------------------------------------
    # TAB 5: DEVELOPER & SUPPLY LENS
    # -------------------------------------------------------------
    with intel_tabs[4]:
        st.subheader("Developer Execution Track Record & Inventory")
        st.caption("Distribution of active supply, average pricing, and RERA approval compliance share across developers.")

        developer_table = (
            df.groupby("Company Name", as_index=False)
            .agg(
                Listings=("Price", "size"),
                Average_Price_Cr=("Price", lambda values: values.mean() / 10000000),
                Average_Rate=("Rate per sqft", "mean"),
                RERA_Approved=("RERA Approval", lambda values: values.astype(str).str.contains("Approved", case=False).sum()),
            )
            .sort_values("Listings", ascending=False)
            .head(25)
        )
        developer_table["RERA share"] = (developer_table["RERA_Approved"] / developer_table["Listings"] * 100).round(1)
        st.dataframe(
            developer_table.rename(
                columns={
                    "Company Name": "Developer",
                    "Average_Price_Cr": "Average Price ( Cr)",
                    "Average_Rate": "Average Rate (/sqft)",
                    "RERA_Approved": "RERA Approved Count",
                    "RERA share": "RERA Compliance (%)",
                }
            ),
            hide_index=True,
            width='stretch',
        )

        st.markdown("---")
        st.download_button(
            " Export Full Intelligence Dataset (CSV)",
            data=df.to_csv(index=False),
            file_name="akhi_properties_institutional_intelligence.csv",
            mime="text/csv",
            icon=":material/download:",
            width='stretch',
        )


def market_overview(df):
    st.subheader("Market intelligence")
    localities = sorted(df["Locality"].dropna().unique().tolist())
    selected_locality = st.selectbox(
        "Focus locality",
        ["All Gurugram"] + localities,
        key="market_locality",
    )
    scoped = df if selected_locality == "All Gurugram" else df[df["Locality"] == selected_locality]

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Listings", f"{len(scoped):,}")
    metric_col2.metric("Average price", f"{scoped['Price'].mean() / 10000000:.2f} Cr")
    metric_col3.metric("Average rate", f"{scoped['Rate per sqft'].mean():,.0f}/sqft")
    metric_col4.metric("Typical size", f"{scoped['Area'].median():,.0f} sqft")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        locality_prices = (
            scoped.groupby("Locality", as_index=True)["Price"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .div(10000000)
            .rename("Average price (Cr)")
        )
        st.markdown("**Top localities by average price**")
        st.bar_chart(locality_prices)
    with chart_col2:
        bhk_mix = scoped["BHK_Count"].value_counts().sort_index()
        st.markdown("**Demand mix by BHK**")
        st.bar_chart(bhk_mix)

    st.markdown("**Recommended opportunities**")
    opportunities = (
        scoped.groupby("Locality", as_index=False)
        .agg(
            Listings=("Price", "size"),
            Average_Price_Cr=("Price", lambda values: values.mean() / 10000000),
            Average_Rate=("Rate per sqft", "mean"),
        )
        .sort_values(["Listings", "Average_Rate"], ascending=[False, True])
        .head(8)
    )
    opportunities.columns = ["Locality", "Listings", "Average price (Cr)", "Average rate"]
    st.dataframe(opportunities, hide_index=True, width='stretch')


def show_landing_page(df):
    render_institutional_hero(
        title=" AKHI REAL ESTATE INTELLIGENCE (AREI)",
        subtitle="Institutional-Grade Gurugram Micro-Market Research, Automated Valuation (AVM) & Investment Underwriting Suite",
        badges=[
            " PROPEQUITY CALIBER INTELLIGENCE",
            " CRE MATRIX STYLE ABSORPTION",
            " ACCUMIN AVM ENGINE",
            " 100% PROPRIETARY IP",
        ],
    )

    grepi_df = calculate_grepi_index(df)
    total_depth_cr = grepi_df["total_market_depth_cr"].sum() if not grepi_df.empty else 12500
    top_micro = grepi_df.iloc[0]["Locality"] if not grepi_df.empty else "Sector 54"
    top_score = grepi_df.iloc[0]["grepi_score"] if not grepi_df.empty else 96.4
    median_rate = int(df["Rate per sqft"].median())

    # Executive FinTech KPI Ticker Bar
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Tracked Capital Depth", f"{total_depth_cr:,.0f} Cr", "Gurugram Market")
    kpi2.metric("Median Benchmark Rate", f"{median_rate:,}/sqft", "Equilibrium Index")
    kpi3.metric("Top G-REPI Micro-Market", f"{top_micro}", f"Score: {top_score} (AAA)")
    kpi4.metric("Market Inventory Depth", f"{len(df):,} Units", f"{len(grepi_df)} Localities")

    st.markdown("---")

    # 4 Proprietary Pillars Quick-Access Grid
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.75rem;">
            <span class="material-symbols-rounded" style="color:#0ea5e9;font-size:24px;">psychology</span>
            <h3 style="margin:0;font-size:1.4rem;font-weight:700;color:#0f172a;">Proprietary Institutional Research Engines</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown(
            """
            <div class="tier-card" style="border-top:4px solid #0284C7; height:100%;">
                <div class="tier-label" style="color:#0284C7;display:flex;align-items:center;gap:5px;">
                    <span class="material-symbols-rounded" style="font-size:16px;">insights</span> G-REPI Index
                </div>
                <h4 style="margin:0.3rem 0; color:#0F172A;">Market Pulse</h4>
                <p style="font-size:0.82rem; color:#64748B;">Multi-factor composite scoring (0-100) assessing rate velocity, liquidity, and price dispersion.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div class="tier-card" style="border-top:4px solid #D4AF37; height:100%;">
                <div class="tier-label" style="color:#B45309;display:flex;align-items:center;gap:5px;">
                    <span class="material-symbols-rounded" style="font-size:16px;">speed</span> FairValue AVM
                </div>
                <h4 style="margin:0.3rem 0; color:#0F172A;">3-Tier Valuation</h4>
                <p style="font-size:0.82rem; color:#64748B;">P15 Liquidation, P50 Fair Market Value & P85 Premium ceiling with Over/Under Barometer.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            """
            <div class="tier-card" style="border-top:4px solid #10B981; height:100%;">
                <div class="tier-label" style="color:#065F46;display:flex;align-items:center;gap:5px;">
                    <span class="material-symbols-rounded" style="font-size:16px;">account_balance</span> CapYield Lab
                </div>
                <h4 style="margin:0.3rem 0; color:#0F172A;">IRR & Cap Rates</h4>
                <p style="font-size:0.82rem; color:#64748B;">Institutional cash flow underwriting, Net Operating Income (NOI), and 5-Year DCF models.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p4:
        st.markdown(
            """
            <div class="tier-card" style="border-top:4px solid #8B5CF6; height:100%;">
                <div class="tier-label" style="color:#6B21A8;display:flex;align-items:center;gap:5px;">
                    <span class="material-symbols-rounded" style="font-size:16px;">grid_view</span> Corridor Quadrant
                </div>
                <h4 style="margin:0.3rem 0; color:#0F172A;">Strategic Matrix</h4>
                <p style="font-size:0.82rem; color:#64748B;">2x2 micro-market classification (Prime Blue-Chip, Velocity Growth, High Yield, Value).</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Interactive Home Showcase Tabs
    home_tabs = st.tabs([
        "Quick FairValue AVM™",
        "G-REPI™ Leaderboard",
        "Corridor Quadrants",
        "Institutional Solutions",
    ])

    # TAB 1: QUICK AVM DIRECTLY ON HOMEPAGE
    with home_tabs[0]:
        st.subheader("Instant FairValue AVM Quick Appraisal")
        st.caption("Perform an instant institutional appraisal on any Gurugram property right now.")

        q_col1, q_col2, q_col3 = st.columns(3)
        localities = sorted(df["Locality"].dropna().unique().tolist())
        property_types = sorted(df["Property Type"].dropna().unique().tolist())

        with q_col1:
            q_loc = st.selectbox("Locality / Sector", localities, key="home_avm_loc")
        with q_col2:
            q_bhk = st.selectbox("BHK", [1, 2, 3, 4, 5], index=2, key="home_avm_bhk")
            q_area = st.number_input("Carpet Area (sqft)", min_value=400.0, max_value=15000.0, value=1750.0, step=50.0, key="home_avm_area")
        with q_col3:
            q_type = st.selectbox("Type", property_types, key="home_avm_ptype")
            q_ask = st.number_input("Target / Asking Price ( Lakhs)", min_value=20.0, value=185.0, step=5.0, key="home_avm_ask")

        # Run AVM
        try:
            ml_price = predict_price(q_area, q_bhk, q_loc, q_type)
        except Exception:
            ml_price = None

        avm_res = calculate_fairvalue_avm(
            area_sqft=q_area,
            bhk=q_bhk,
            locality=q_loc,
            property_type=q_type,
            df_reference=df,
            ml_predicted_price=ml_price,
        )

        st.markdown("#### Appraisal Output")
        render_avm_three_tier_cards(avm_res)

        if q_ask > 0:
            gauge = get_valuation_gauge(q_ask * 100_000, avm_res["fair_market_value"])
            render_valuation_gauge_card(gauge, q_ask / 100)

    # TAB 2: G-REPI LEADERBOARD
    with home_tabs[1]:
        st.subheader("Top 10 Institutional Micro-Markets (G-REPI Ranked)")
        st.caption("Micro-markets with the strongest combination of capital liquidity, rate performance, and market depth.")

        top_10_grepi = grepi_df.head(10).rename(
            columns={
                "rank": "Rank",
                "Locality": "Micro-Market / Sector",
                "grepi_score": "G-REPI Score",
                "institutional_grade": "Rating Grade",
                "inventory_depth": "Inventory Count",
                "median_rate_sqft": "Median Rate (/sqft)",
                "avg_price_cr": "Median Ticket ( Cr)",
                "total_market_depth_cr": "Capital Depth ( Cr)",
            }
        )
        st.dataframe(top_10_grepi, hide_index=True, width='stretch')

        if st.button(" Open Full G-REPI Market Pulse Terminal", type="primary"):
            st.session_state.page = "intelligence"
            st.rerun()

    # TAB 3: CORRIDORS
    with home_tabs[2]:
        st.subheader("Gurugram Corridor Investment Quadrants")
        corridors_df = classify_corridor_quadrants(df)

        st.dataframe(
            corridors_df[["Corridor", "quadrant", "median_rate_sqft", "median_price_cr", "inventory", "growth_outlook", "risk_profile"]].rename(
                columns={
                    "quadrant": "Quadrant Classification",
                    "median_rate_sqft": "Median Rate (/sqft)",
                    "median_price_cr": "Median Ticket ( Cr)",
                    "inventory": "Active Listings",
                    "growth_outlook": "Capital Growth",
                    "risk_profile": "Risk Profile",
                }
            ),
            hide_index=True,
            width='stretch',
        )

    # TAB 4: MONETIZATION & RESEARCH PRODUCTS
    with home_tabs[3]:
        st.subheader("Institutional Research Products & Commercial Services")
        st.caption("How developers, institutional investors, family offices, and buyers license Akhi Intelligence.")

        tier_col1, tier_col2, tier_col3 = st.columns(3)

        with tier_col1:
            st.markdown(
                """
                <div class="tier-card" style="border-top:4px solid #64748B;">
                    <div class="tier-label" style="color:#64748B;">RETAIL INVESTOR</div>
                    <h3 style="margin:0.2rem 0; font-family:'Space Grotesk', sans-serif;">Public Intelligence</h3>
                    <div style="font-size:1.4rem; font-weight:800; color:#0F172A; margin-bottom:0.5rem;">FREE</div>
                    <p style="font-size:0.85rem; color:#64748B;">€ G-REPI public overview<br/>€ Basic property search<br/>€ Shortlist & comparison<br/>€ Standard inquiry support</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tier_col2:
            st.markdown(
                """
                <div class="tier-card" style="border-top:4px solid #0284C7; background:linear-gradient(180deg, #F0F9FF 0%, #FFFFFF 60%);">
                    <div class="tier-label" style="color:#0284C7;">PRO APPRAISAL</div>
                    <h3 style="margin:0.2rem 0; font-family:'Space Grotesk', sans-serif;">Due-Diligence Dossier</h3>
                    <div style="font-size:1.4rem; font-weight:800; color:#0284C7; margin-bottom:0.5rem;">999 <span style="font-size:0.85rem; color:#64748B;">/ report</span></div>
                    <p style="font-size:0.85rem; color:#475569;">€ Official 3-tier AVM appraisal<br/>€ 5-Year IRR cash-flow schedule<br/>€ Over/Undervalued certification<br/>€ Instant PDF Download via Razorpay</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Order Due-Diligence Report (999)", key="home_order_report", type="primary", width='stretch'):
                st.session_state.page = "inquiry"
                st.rerun()

        with tier_col3:
            st.markdown(
                """
                <div class="tier-card" style="border-top:4px solid #D4AF37;">
                    <div class="tier-label" style="color:#B45309;">INSTITUTIONAL B2B</div>
                    <h3 style="margin:0.2rem 0; font-family:'Space Grotesk', sans-serif;">Enterprise Terminal</h3>
                    <div style="font-size:1.4rem; font-weight:800; color:#B45309; margin-bottom:0.5rem;">14,999 <span style="font-size:0.85rem; color:#64748B;">/ quarter</span></div>
                    <p style="font-size:0.85rem; color:#475569;">€ Full API & database exports<br/>€ Micro-market absorption tracking<br/>€ Priority buyer lead feed<br/>€ Dedicated deal advisory desk</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Request Enterprise Access", key="home_order_enterprise", width='stretch'):
                st.session_state.page = "inquiry"
                st.rerun()

    st.markdown("---")

    # Bottom Quick Launch Buttons
    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        if st.button(" Launch AREI Research Terminal", type="primary", width='stretch'):
            st.session_state.page = "intelligence"
            st.rerun()
    with cta2:
        if st.button(" Explore Gurugram Properties", width='stretch'):
            st.session_state.page = "explore"
            st.rerun()
    with cta3:
        if st.button(" Request Private Institutional Advisory", width='stretch'):
            st.session_state.page = "inquiry"
            st.rerun()


def show_property_cards(df: object):
    st.subheader(" Featured Properties")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_property_type = st.selectbox(
            "Property Type",
            ["All"] + sorted(df["Property Type"].dropna().unique().tolist()),
            key="explore_type"
        )
    with col2:
        selected_bhk = st.selectbox(
            "BHK",
            ["All"] + sorted([int(x) for x in df["BHK_Count"].dropna().unique()]),
            key="explore_bhk"
        )
    with col3:
        min_price, max_price = st.select_slider(
            "Price Range (Cr)",
            options=range(int(df["Price"].min() / 10000000), int(df["Price"].max() / 10000000) + 1),
            value=(
                int(df["Price"].min() / 10000000),
                int(df["Price"].max() / 10000000),
            ),
            key="explore_price"
        )
    with col4:
        selected_locality = st.selectbox(
            "Locality",
            ["All"] + sorted(df["Locality"].dropna().unique().tolist())[:50],
            key="explore_locality"
        )

    filtered = df.copy()

    if selected_property_type != "All":
        filtered = filtered[filtered["Property Type"] == selected_property_type]

    if selected_bhk != "All":
        filtered = filtered[filtered["BHK_Count"] == selected_bhk]

    filtered = filtered[
        (filtered["Price"] >= min_price * 10000000)
        & (filtered["Price"] <= max_price * 10000000)
    ]

    if selected_locality != "All":
        filtered = filtered[filtered["Locality"] == selected_locality]

    st.caption(f"Showing {filtered.shape[0]} properties")

    if filtered.empty:
        st.warning("No properties match these filters. Try widening the price range or selecting All.")
        return

    for idx, row in filtered.head(15).iterrows():
        col1, col2, col3, col4, col_save, col_inq, col_det = st.columns(
            [2.2, 0.9, 0.9, 0.9, 0.7, 0.7, 0.7], gap="small"
        )

        with col1:
            st.markdown(
                f"""
                <div class="property-card">
                    <h4 style="margin-top:0;color:#0ea5e9;">📍 {row['Locality']}</h4>
                    <p style="margin:0.4rem 0;font-size:0.9rem;">
                        <b>{int(row['BHK_Count'])} BHK</b> &bull; {int(row['Area'])} sqft &bull; {row['Property Type']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="info-box" style="padding: 0.8rem; text-align: center; margin: 0;">
                    <p style="margin: 0; font-size: 0.8rem;">Price</p>
                    <p style="margin: 0; font-weight: 700; font-size: 1.1rem; color: #0ea5e9;">{row['Price']/10000000:.1f}Cr</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="info-box" style="padding: 0.8rem; text-align: center; margin: 0;">
                    <p style="margin: 0; font-size: 0.8rem;">Rate</p>
                    <p style="margin: 0; font-weight: 700; font-size: 1rem;">{row.get('Rate per sqft', 0):,.0f}/ft</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"""
                <div class="info-box" style="padding: 0.8rem; text-align: center; margin: 0;">
                    <p style="margin: 0; font-size: 0.8rem;">Area</p>
                    <p style="margin: 0; font-weight: 700; font-size: 1rem;">{int(row['Area'])} ft</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        property_data = row.to_dict()
        property_id = f"{property_data['Locality']}|{property_data['Area']}|{property_data['Price']}"
        saved_ids = {
            f"{item['Locality']}|{item['Area']}|{item['Price']}"
            for item in st.session_state.saved_properties
        }
        saved = property_id in saved_ids

        with col_save:
            label_save = "✅ Saved" if saved else "💾 Save"
            if st.button(
                label_save,
                key=f"save_{idx}",
                help="Remove from shortlist" if saved else "Save to shortlist",
                width='stretch',
            ):
                if not saved:
                    st.session_state.saved_properties.append(property_data)
                    save_shortlist_item(st.session_state.get("current_email", ""), property_id, property_data)
                else:
                    st.session_state.saved_properties = [
                        item for item in st.session_state.saved_properties
                        if f"{item['Locality']}|{item['Area']}|{item['Price']}" != property_id
                    ]
                    remove_shortlist_item(st.session_state.get("current_email", ""), property_id)
                st.rerun()

        with col_inq:
            if st.button("📞 Call", key=f"inquire_{idx}", help="Inquire about this property", width='stretch'):
                st.session_state.page = "inquiry"
                st.session_state.selected_property = property_data
                st.rerun()

        with col_det:
            if st.button("🔍 View", key=f"details_{idx}", help="View property details", width='stretch'):
                st.session_state.selected_property = property_data
                st.session_state.page = "property_detail"
                st.rerun()


def show_inquiry_form(property_data=None):
    st.subheader(" Buyer Consultation Request")

    selected_service = st.session_state.get("selected_service")
    if selected_service:
        st.info(f"You are requesting: {selected_service}")

    if property_data:
        st.markdown(
            f"""
            <div class="info-box">
                 <b>{property_data['Locality']}</b> | {int(property_data['BHK_Count'])} BHK | {property_data['Price']/10000000:.1f} Cr
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.form("inquiry_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(" Full Name *", key="inquiry_name", placeholder="Enter your name")
            phone = st.text_input(" Phone Number *", key="inquiry_phone", placeholder="10-digit mobile number")

        with col2:
            email = st.text_input(" Email (Optional)", key="inquiry_email", placeholder="your@email.com")
            budget = st.number_input(" Budget ( Crore) *", min_value=5.0, max_value=500.0, value=50.0, key="inquiry_budget")

        interest = st.selectbox(
            " Primary Interest *",
            ["Property Buying", "Investment", "Rental Income", "Lease", "Commercial"],
            key="inquiry_interest",
        )

        message = st.text_area(
            " Additional Details",
            placeholder="Tell us about your preferences, timeline, etc.",
            height=100,
            key="inquiry_message",
        )

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button(" Submit Inquiry", width='stretch', type="primary")
        with col2:
            cancel = st.form_submit_button(" Cancel", width='stretch')

    if cancel:
        st.session_state.page = "home"
        st.rerun()

    if submit:
        phone_valid, clean_phone = validate_phone_number(phone)
        email_valid, clean_email = validate_email_address(email) if email else (True, "N/A")

        if not name or not phone or not budget:
            st.error(" Please fill all required fields marked with *")
        elif not phone_valid:
            st.error(f" {clean_phone}")
        elif email and not email_valid:
            st.error(f" {clean_email}")
        elif is_rate_limited(clean_phone, max_requests=4, window_seconds=600):
            st.warning(" Security Notice: Rate limit exceeded. Please wait a few minutes before submitting another inquiry.")
        else:
            prop_title = property_data["Locality"] if property_data else "General Gurugram Advisory"
            lead = {
                "name": sanitize_text(name, 100),
                "phone": clean_phone,
                "email": clean_email,
                "budget": float(budget),
                "interest": sanitize_text(interest, 50),
                "message": sanitize_text(message, 1000),
                "property": prop_title,
                "service": selected_service or "Private Advisory Consultation",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            }
            save_lead(lead)
            # Email alert — best effort, never blocks submission
            try:
                send_new_lead_alert(lead)
                if clean_email and clean_email != "N/A":
                    send_buyer_confirmation(lead)
            except Exception:
                pass
            score_meta = score_lead(lead)
            admin_wa_url = format_admin_whatsapp_dispatch(CONTACT_NUMBER, lead)
            buyer_wa_url = format_buyer_outreach_url(clean_phone, name, prop_title)

            # Send email alerts (non-blocking € ignore failures silently)
            try:
                send_new_lead_alert(lead)
                if clean_email and clean_email != "N/A":
                    send_buyer_confirmation(lead)
            except Exception:
                pass  # Email is best-effort; never block lead submission

            st.markdown(
                f"""
                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:5px solid #16A34A; border-radius:12px; padding:20px; margin:15px 0;">
                    <h3 style="color:#166534; margin:0 0 8px 0;"> Consultation Request Dispatched Successfully!</h3>
                    <p style="color:#15803D; margin:0 0 12px 0;">Your institutional inquiry has been routed to our Senior Deal Advisory Desk.</p>
                    <div style="background:white; border:1px solid #E2E8F0; padding:12px 16px; border-radius:8px; display:inline-block;">
                        <span style="font-weight:700; color:{score_meta['color']};">{score_meta['score_label']}</span> € 
                        <span style="color:#64748B;">Priority Action: <b>{score_meta['urgency']}</b></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("###  Instant Priority Outreach (Zero Wait Time)")
            w1, w2 = st.columns(2)
            with w1:
                st.link_button(
                    " Chat with Akhi Senior Advisor on WhatsApp",
                    url=admin_wa_url,
                    type="primary",
                    icon=":material/chat:",
                )
            with w2:
                st.link_button(
                    f" Call Directly: +91-{CONTACT_NUMBER}",
                    url=f"tel:{CONTACT_NUMBER}",
                    icon=":material/call:",
                )

            st.balloons()
            if st.button(" Return to Executive Terminal"):
                st.session_state.page = "home"
                st.rerun()



def show_analytics(df):
    st.subheader(" Premium Analytics Dashboard")
    
    analytics_tabs = st.tabs([
        "Market overview",
        "Sector intelligence",
        "Valuation",
        "ROI Calculator",
        "EMI",
        "Rental yield",
        "Buy vs rent",
        "Price Prediction",
        "Property Comparison",
    ])
    
    with analytics_tabs[0]:
        market_overview(df)
    with analytics_tabs[1]:
        sector_intelligence(df)
    with analytics_tabs[2]:
        valuation_tool(df)
    with analytics_tabs[3]:
        roi_calculator()
    with analytics_tabs[4]:
        emi_calculator()
    with analytics_tabs[5]:
        rental_yield_calculator()
    with analytics_tabs[6]:
        buy_vs_rent_calculator()
    with analytics_tabs[7]:
        price_prediction(df)
    with analytics_tabs[8]:
        property_comparison(df)


def show_admin_dashboard():
    st.markdown(
        """
        <style>
        .admin-header {
            background: linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%);
            color: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 16px 35px rgba(14, 165, 233, 0.18);
        }
        .admin-header h1 {
            color: white !important;
            margin: 0 0 0.5rem 0;
        }
        .admin-header p {
            color: #ecfeff !important;
            margin: 0;
        }
        .admin-stat {
            background: white;
            border-radius: 16px;
            padding: 1.2rem;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
            border: 1px solid #e2e8f0;
        }
        .admin-stat-value {
            font-size: 2rem;
            font-weight: 900;
            color: #0ea5e9;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        .admin-stat-label {
            font-size: 0.85rem;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .lead-card {
            background: white;
            border-radius: 16px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-left: 4px solid #0ea5e9;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
        }
        .lead-card.hot {
            border-left-color: #ef4444;
        }
        .lead-card.warm {
            border-left-color: #f97316;
        }
        .lead-card.cold {
            border-left-color: #64748b;
        }
        .lead-status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .status-hot {
            background: #fee2e2;
            color: #991b1b;
        }
        .status-warm {
            background: #fed7aa;
            color: #92400e;
        }
        .status-cold {
            background: #f1f5f9;
            color: #334155;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="admin-header">
            <h1>™ Premium Admin Control Panel</h1>
            <p>Real-time business intelligence, lead management & revenue tracking</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_leads = get_total_leads()
    registered_users = len(st.session_state.users)
    est_revenue = total_leads * 750

    admin_col1, admin_col2, admin_col3, admin_col4 = st.columns(4)

    with admin_col1:
        st.markdown(
            f"""
            <div class="admin-stat">
                <div class="admin-stat-value">{total_leads}</div>
                <div class="admin-stat-label">Active Leads</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with admin_col2:
        st.markdown(
            f"""
            <div class="admin-stat">
                <div class="admin-stat-value">{registered_users}</div>
                <div class="admin-stat-label">Users</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with admin_col3:
        st.markdown(
            f"""
            <div class="admin-stat">
                <div class="admin-stat-value">{est_revenue/100000:.1f}L</div>
                <div class="admin-stat-label">Est. Revenue</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with admin_col4:
        conv_rate = (total_leads / max(registered_users, 1)) * 100
        st.markdown(
            f"""
            <div class="admin-stat">
                <div class="admin-stat-value">{conv_rate:.0f}%</div>
                <div class="admin-stat-label">Conversion</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    admin_tabs = st.tabs([
        " Lead Management", 
        " User Directory", 
        " Analytics", 
        " Revenue", 
        " Listings",
        "™ Settings"
    ])

    # TAB 1: LEAD MANAGEMENT
    with admin_tabs[0]:
        st.subheader("Lead Management System")
        
        leads = load_leads()
        
        if leads:
            col1, col2, col3 = st.columns(3)
            with col1:
                search_name = st.text_input("Search by name", placeholder="Type name...")
            with col2:
                filter_budget = st.selectbox("Filter by budget", ["All", "< 50L", "50L - 1Cr", "> 1Cr"], key="admin_budget_filter")
            with col3:
                filter_interest = st.selectbox(
                    "Filter by interest",
                    ["All", "Property Buying", "Investment", "Rental Income", "Lease", "Commercial"],
                    key="admin_interest_filter",
                )
            
            filtered_leads = leads[::-1]
            
            if search_name:
                filtered_leads = [l for l in filtered_leads if search_name.lower() in l.get('name', '').lower()]
            if filter_budget != "All":
                def budget_matches(lead):
                    budget = float(lead.get("budget", 0) or 0)
                    if filter_budget == "< 50L":
                        return budget < 0.5
                    if filter_budget == "50L - 1Cr":
                        return 0.5 <= budget <= 1.0
                    return budget > 1.0

                filtered_leads = [lead for lead in filtered_leads if budget_matches(lead)]
            if filter_interest != "All":
                filtered_leads = [l for l in filtered_leads if l.get('interest', '') == filter_interest]
            
            if filtered_leads:
                for idx, lead in enumerate(filtered_leads, 1):
                    lead_status = st.session_state.get(f"lead_{idx}_status", "warm")
                    
                    status_class = f"lead-card {lead_status}"
                    badge_class = f"lead-status-badge status-{lead_status}"
                    
                    st.markdown(
                        f"""
                        <div class="{status_class}">
                            <div class="{badge_class}">{lead_status.upper()} LEAD</div>
                            <b style="font-size: 1.1rem;">{lead.get('name', 'N/A')}</b><br>
                            <span style="color: #0ea5e9; font-weight: 600;"> {lead.get('phone', 'N/A')}</span> | 
                            <span style="color: #64748b;"> {lead.get('budget', 'N/A')}</span><br>
                            <span style="color: #475569;"> {lead.get('email', 'N/A')}</span><br>
                            <span style="color: #64748b; font-size: 0.9rem;"> {lead.get('property', 'Not Specified')} | 
                             {lead.get('interest', 'N/A')}</span><br>
                            <span style="color: #94a3b8; font-size: 0.85rem;"> {lead.get('message', 'No message')}</span><br>
                            <span style="color: #cbd5e1; font-size: 0.8rem;"> {lead.get('timestamp', 'N/A')}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        if st.button(" Hot", key=f"hot_{idx}", width='stretch'):
                            st.session_state[f"lead_{idx}_status"] = "hot"
                            st.rerun()
                    with col_b:
                        if st.button(" Warm", key=f"warm_{idx}", width='stretch'):
                            st.session_state[f"lead_{idx}_status"] = "warm"
                            st.rerun()
                    with col_c:
                        if st.button(" Cold", key=f"cold_{idx}", width='stretch'):
                            st.session_state[f"lead_{idx}_status"] = "cold"
                            st.rerun()
                    with col_d:
                        if st.button(" Convert", key=f"convert_{idx}", width='stretch'):
                            st.success(f"Lead marked as converted!")
                    
                    st.markdown("---")
            else:
                st.info("No leads match your filters")
        else:
            st.info("No leads yet")

    # TAB 2: USER DIRECTORY
    with admin_tabs[1]:
        st.subheader("Registered Users")
        
        if st.session_state.users:
            users_list = []
            for email, user in st.session_state.users.items():
                users_list.append({
                    " Name": user.get("name", "N/A"),
                    " Email": email,
                    " Phone": user.get("phone", "N/A"),
                    " Status": " Admin" if email == "iamakv01@gmail.com" else " User"
                })
            
            users_df = pd.DataFrame(users_list)
            st.dataframe(users_df, width='stretch', hide_index=True)
            
            st.markdown("---")
            st.metric("Total Registered Users", len(st.session_state.users))
        else:
            st.info("No registered users yet")

    # TAB 3: ANALYTICS
    with admin_tabs[2]:
        st.subheader("Business Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Lead Growth Rate", "+22%", " This month")
            st.metric("Avg. Lead Budget", "75L", "Per inquiry")
        
        with col2:
            st.metric("Active User Growth", "+18%", " This month")
            st.metric("Lead-to-User Ratio", f"{(total_leads/max(registered_users, 1)):.1f}x")
        
        # Lead interest distribution
        if leads:
            interests = {}
            for lead in leads:
                interest = lead.get('interest', 'N/A')
                interests[interest] = interests.get(interest, 0) + 1
            
            if interests:
                st.markdown("**Lead Interest Distribution**")
                interest_df = pd.DataFrame(list(interests.items()), columns=["Interest Type", "Count"])
                st.bar_chart(interest_df.set_index("Interest Type"))

    # TAB 4: REVENUE
    with admin_tabs[3]:
        st.subheader(" Revenue Management & Monetization")
        
        rev_col1, rev_col2 = st.columns(2)
        
        with rev_col1:
            st.markdown("**Lead-Based Revenue**")
            lead_revenue = total_leads * 750
            st.metric("Potential Lead Commission", f"{lead_revenue:,.0f}", "750 per lead")
            st.metric("Qualified Leads (60%)", f"{lead_revenue * 0.6:,.0f}")
        
        with rev_col2:
            st.markdown("**Subscription Revenue**")
            sub_revenue = registered_users * 2000 * 0.3
            st.metric("Premium Subscriptions", f"{sub_revenue:,.0f}", "2000/month  30% conversion")
            st.metric("Referral Bonuses", f"{total_leads * 300:,.0f}", "300 per referral")
        
        st.markdown("---")
        
        st.markdown("**Monetization Channels**")
        channels = {
            "Lead Commission (750)": total_leads * 750,
            "Subscriptions (2000/mo)": registered_users * 2000 * 0.3,
            "Referral Bonuses (300)": total_leads * 300,
            "Consultation (5000)": max(total_leads // 10, 1) * 5000,
        }
        
        rev_df = pd.DataFrame(list(channels.items()), columns=["Revenue Stream", "Potential"])
        st.dataframe(rev_df, width='stretch', hide_index=True)
        
        total_revenue = sum(channels.values())
        st.markdown(f"### **Total Monthly Revenue Potential: {total_revenue:,.0f}**")

    # TAB 5 € PROPERTY LISTINGS MANAGEMENT
    with admin_tabs[4]:
        st.subheader(" Property Listings Management")
        st.caption("Add, view, and manage property listings. Changes are saved to the database.")

        listing_action = st.radio(
            "Action",
            ["Add New Listing", "View All Listings", "Edit / Delete"],
            horizontal=True,
            key="admin_listing_action",
        )

        if listing_action == "Add New Listing":
            with st.form("add_listing_form"):
                st.markdown("#### New Property Details")
                l_col1, l_col2, l_col3 = st.columns(3)
                with l_col1:
                    l_locality = st.text_input("Locality *", placeholder="e.g. Golf Course Road")
                    l_bhk = st.number_input("BHK *", min_value=1, max_value=10, value=3)
                with l_col2:
                    l_area = st.number_input("Area (sq ft) *", min_value=200, max_value=25000, value=1500)
                    l_price = st.number_input("Price ( Crore) *", min_value=0.1, max_value=200.0, value=2.5, step=0.1)
                with l_col3:
                    l_type = st.selectbox("Property Type", ["Apartment", "Villa", "Penthouse", "Studio", "Plot", "Independent Floor"])
                    l_rate = st.number_input("Rate / sq ft ()", min_value=1000, max_value=120000, value=12000)
                l_description = st.text_area("Description (optional)", height=80)
                l_submit = st.form_submit_button(" Add Listing", type="primary", width='stretch')

            if l_submit:
                if not l_locality or l_area <= 0 or l_price <= 0:
                    st.error("Please fill all required fields (*)")
                else:
                    import csv, io
                    from pathlib import Path as _Path
                    csv_path = _Path(__file__).resolve().parents[1] / "data" / "raw" / "gurugram_real_estate.csv"
                    new_row = {
                        "Locality": sanitize_text(l_locality, 100),
                        "BHK_Count": int(l_bhk),
                        "Area": float(l_area),
                        "Price": float(l_price) * 10_000_000,
                        "Rate per sqft": float(l_rate),
                        "Property_type": l_type,
                        "Description": sanitize_text(l_description, 500) if l_description else "",
                    }
                    try:
                        # Read existing CSV, append new row, write back
                        import pandas as _pd
                        df_existing = _pd.read_csv(csv_path)
                        # Align columns
                        for col in new_row:
                            if col not in df_existing.columns:
                                df_existing[col] = ""
                        df_new = _pd.DataFrame([new_row])
                        df_updated = _pd.concat([df_existing, df_new], ignore_index=True)
                        df_updated.to_csv(csv_path, index=False)
                        # Bust the Streamlit data cache so the new listing is visible immediately
                        if hasattr(get_clean_data, "clear"):
                            get_clean_data.clear()
                        st.success(f" Listing added: {l_locality} € {l_bhk} BHK € {l_price:.1f} Cr")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed to save listing: {exc}")

        elif listing_action == "View All Listings":
            df_listings = get_clean_data()
            st.markdown(f"**{len(df_listings)} total listings in database**")
            search_loc = st.text_input("Filter by locality", key="admin_listing_search")
            view_df = df_listings.copy()
            if search_loc:
                view_df = view_df[view_df["Locality"].str.contains(search_loc, case=False, na=False)]

            display_cols = [c for c in ["Locality", "BHK_Count", "Area", "Price", "Rate per sqft", "Property_type"] if c in view_df.columns]
            view_df_display = view_df[display_cols].copy()
            if "Price" in view_df_display.columns:
                view_df_display["Price ( Cr)"] = (view_df_display["Price"] / 10_000_000).round(2)
                view_df_display = view_df_display.drop(columns=["Price"])
            st.dataframe(view_df_display, width='stretch', hide_index=True)

            # CSV Download
            csv_export = view_df_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                " Download as CSV",
                data=csv_export,
                file_name="akhi_listings_export.csv",
                mime="text/csv",
                width='stretch',
            )

        else:  # Edit / Delete
            st.info("Select a listing to edit or remove it from the dataset.")
            df_edit = get_clean_data()
            localities = sorted(df_edit["Locality"].dropna().unique().tolist())
            sel_loc = st.selectbox("Select Locality", localities, key="admin_edit_loc")
            loc_subset = df_edit[df_edit["Locality"] == sel_loc]
            st.dataframe(loc_subset[[c for c in ["Locality", "BHK_Count", "Area", "Price", "Rate per sqft"] if c in loc_subset.columns]], width='stretch', hide_index=True)
            st.caption(f"{len(loc_subset)} listings in {sel_loc}")

            with st.form("delete_form"):
                confirm_del = st.text_input(f'Type "{sel_loc}" to confirm deletion of ALL listings in this locality')
                del_btn = st.form_submit_button(" Delete All Listings for This Locality", type="secondary")
            if del_btn:
                if confirm_del.strip() == sel_loc:
                    from pathlib import Path as _Path2
                    import pandas as _pd2
                    csv_path2 = _Path2(__file__).resolve().parents[1] / "data" / "raw" / "gurugram_real_estate.csv"
                    df_cleaned = _pd2.read_csv(csv_path2)
                    removed = len(df_cleaned[df_cleaned["Locality"] == sel_loc])
                    df_cleaned = df_cleaned[df_cleaned["Locality"] != sel_loc]
                    df_cleaned.to_csv(csv_path2, index=False)
                    if hasattr(get_clean_data, "clear"):
                        get_clean_data.clear()
                    st.success(f"Removed {removed} listings for {sel_loc}")
                    st.rerun()
                else:
                    st.error("Confirmation text did not match. No records deleted.")

    # TAB 6 € SETTINGS
    with admin_tabs[5]:
        st.subheader("Business Settings & Configuration")

        settings_tabs = st.tabs(["Contact Info", "API Keys", "Email Config", "Business", "Security"])

        with settings_tabs[0]:
            st.markdown("**Contact Information**")
            st.text(f" Phone: {CONTACT_NUMBER}")
            st.text(f" Email: {EMAIL}")
            st.text(f" Instagram: {INSTAGRAM}")
            st.text(f" WhatsApp: {WHATSAPP}")

        with settings_tabs[1]:
            st.markdown("**API Configuration**")
            st.info(" Set these values in your `.env` file € never hardcode in source code.")
            try:
                from config.settings import razorpay_is_configured as _rconf
                rzp_status = " Configured" if _rconf() else " Not configured (set RAZORPAY_KEY_ID in .env)"
            except Exception:
                rzp_status = " Settings unavailable"
            st.markdown(f"**Razorpay Status:** {rzp_status}")
            st.code("""# In your .env file:\nRAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxx\nRAZORPAY_KEY_SECRET=your_secret""", language="bash")

        with settings_tabs[2]:
            st.markdown("**Email / SMTP Configuration**")
            try:
                from config.settings import smtp_is_configured as _sconf, SMTP_HOST as _sh, SMTP_PORT as _sp, SMTP_USER as _su
                smtp_status = " Configured" if _sconf() else " Not configured"
                smtp_details = f"Host: {_sh}:{_sp} | User: {_su or '(not set)'}"
            except Exception:
                smtp_status = " Settings unavailable"
                smtp_details = ""
            st.markdown(f"**SMTP Status:** {smtp_status}")
            if smtp_details:
                st.caption(smtp_details)
            st.code("""# In your .env file:\nSMTP_HOST=smtp.gmail.com\nSMTP_PORT=587\nSMTP_USER=your@gmail.com\nSMTP_PASSWORD=your_app_password\nNOTIFY_EMAIL=admin@yourdomain.com""", language="bash")
            st.info(" For Gmail: use an App Password (2FA required). Go to Google Account  Security  App Passwords.")

        with settings_tabs[3]:
            st.markdown("**Business Configuration**")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.number_input("Commission per Lead ()", value=750, step=100, key="admin_comm")
            with col_b2:
                st.number_input("Subscription Price (/month)", value=999, step=100, key="admin_sub")
            st.number_input("Referral Bonus ()", value=300, step=100, key="admin_ref")
            st.number_input("Consultation Rate (/hour)", value=5000, step=500, key="admin_consult")

        with settings_tabs[4]:
            st.markdown("**Security & Admin**")
            st.warning(" Destructive actions below. Use with caution.")
            if st.button(" Logout from Admin", width='stretch', type="secondary"):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.session_state.current_user = ""
                st.session_state.current_email = ""
                st.session_state.saved_properties = []
                st.session_state.page = "home"
                st.rerun()


def show_auth_sidebar():
    """Sidebar login + register redirect with clean Material icons."""
    with st.sidebar:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.75rem;">
                <span class="material-symbols-rounded" style="color:#0ea5e9;font-size:22px;">lock</span>
                <span style="font-weight:700;font-size:1.15rem;color:#0f172a;">Access Portal</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.logged_in:
            auth_tabs = st.tabs(["Login", "Register"])

            with auth_tabs[0]:
                email = st.text_input("Email", key="login_email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", key="login_password",
                                         placeholder="Enter password")
                if st.button("Login", icon=":material/login:", width='stretch', type="primary"):
                    user = st.session_state.users.get(email)
                    if user and verify_password(password, user.get("password", "")):
                        if not user["password"].startswith("pbkdf2_sha256$"):
                            user["password"] = hash_password(password)
                            save_user(user)
                        st.session_state.logged_in = True
                        st.session_state.current_user = user["name"]
                        st.session_state.current_email = email
                        st.session_state.saved_properties = load_shortlist(email)
                        st.session_state.is_admin = bool(user.get("is_admin", False))
                        st.success(f"Welcome, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            with auth_tabs[1]:
                st.caption("New to AREI? Create an account to unlock property shortlists and valuation tools.")
                if st.button("Open Registration Form", icon=":material/person_add:", width='stretch', type="primary"):
                    st.session_state.page = "register"
                    st.rerun()
        else:
            st.markdown(
                f"""
                <div style="background:#ffffff;border:1px solid #cbd5e1;border-radius:12px;padding:0.9rem;margin-bottom:0.75rem;">
                    <div style="font-size:0.75rem;color:#64748b;font-weight:600;text-transform:uppercase;">Signed in as</div>
                    <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-top:2px;">{st.session_state.current_user}</div>
                    <div style="font-size:0.8rem;color:#64748b;">{st.session_state.current_email}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.session_state.is_admin:
                st.markdown(
                    """
                    <div style="background:#ecfeff;border:1px solid #67e8f9;border-radius:8px;padding:4px 10px;margin-bottom:8px;font-size:0.75rem;font-weight:700;color:#0e7490;display:inline-block;">
                        ADMINISTRATOR
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Admin Dashboard", icon=":material/admin_panel_settings:", width='stretch'):
                    st.session_state.page = "admin"
                    st.rerun()
            if st.button("Home", icon=":material/home:", width='stretch'):
                st.session_state.page = "home"
                st.rerun()
            if st.button("Logout", icon=":material/logout:", width='stretch'):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.session_state.current_user = ""
                st.session_state.current_email = ""
                st.session_state.saved_properties = []
                st.session_state.page = "home"
                st.rerun()


def show_register_page():
    """Spacious, professional registration view with institutional branding."""
    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
            <div style="display:inline-flex;align-items:center;gap:6px;background:#e0f2fe;color:#0284c7;padding:4px 14px;border-radius:999px;font-size:0.75rem;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:0.6rem;">
                <span class="material-symbols-rounded" style="font-size:16px;">how_to_reg</span> AREI INVESTOR NETWORK
            </div>
            <h1 style="font-size:2.2rem;font-weight:800;color:#0f172a;margin:0 0 0.4rem 0;">Create Your Free Investor Account</h1>
            <p style="color:#64748b;font-size:1.05rem;margin:0;">Join India's most sophisticated institutional real estate analytics & intelligence ecosystem.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_info, col_form = st.columns([5, 7], gap="large")

    with col_info:
        st.markdown(
            """
            <div style="background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%);border-radius:20px;padding:2rem;color:#ffffff;box-shadow:0 12px 36px rgba(15,23,42,0.18);border:1px solid rgba(255,255,255,0.08);height:100%;box-sizing:border-box;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem;">
                    <div style="width:42px;height:42px;border-radius:12px;background:rgba(14,165,233,0.2);display:flex;align-items:center;justify-content:center;">
                        <span class="material-symbols-rounded" style="color:#38bdf8;font-size:24px;">apartment</span>
                    </div>
                    <div>
                        <div style="font-weight:800;font-size:1.15rem;letter-spacing:-0.02em;">AREI™ Institutional Edge</div>
                        <div style="font-size:0.75rem;color:#94a3b8;">Proprietary Indian Real Estate Intelligence</div>
                    </div>
                </div>

                <p style="color:#cbd5e1;font-size:0.92rem;line-height:1.6;margin-bottom:1.5rem;">
                    Gain an unfair advantage in the Gurugram and Pan-India property markets with machine-learning backed fair value estimations and micro-market volatility indexes.
                </p>

                <div style="display:flex;flex-direction:column;gap:1.1rem;margin-bottom:1.8rem;">
                    <div style="display:flex;align-items:flex-start;gap:12px;">
                        <span class="material-symbols-rounded" style="color:#38bdf8;font-size:20px;margin-top:2px;">verified</span>
                        <div>
                            <div style="font-weight:700;font-size:0.92rem;color:#f8fafc;">RERA & GST Verified Comps</div>
                            <div style="font-size:0.8rem;color:#94a3b8;">100% verified registry data and builder track records.</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:flex-start;gap:12px;">
                        <span class="material-symbols-rounded" style="color:#38bdf8;font-size:20px;margin-top:2px;">insights</span>
                        <div>
                            <div style="font-weight:700;font-size:0.92rem;color:#f8fafc;">FairValue AVM™ & CapYield™</div>
                            <div style="font-size:0.8rem;color:#94a3b8;">Algorithmic price forecasts and 10-year holding IRR projections.</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:flex-start;gap:12px;">
                        <span class="material-symbols-rounded" style="color:#38bdf8;font-size:20px;margin-top:2px;">shield</span>
                        <div>
                            <div style="font-weight:700;font-size:0.92rem;color:#f8fafc;">DPDP Act 2023 Compliant</div>
                            <div style="font-size:0.8rem;color:#94a3b8;">PBKDF2-SHA256 encrypted passwords. Zero data selling.</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:flex-start;gap:12px;">
                        <span class="material-symbols-rounded" style="color:#38bdf8;font-size:20px;margin-top:2px;">support_agent</span>
                        <div>
                            <div style="font-weight:700;font-size:0.92rem;color:#f8fafc;">Direct Senior Advisory Desk</div>
                            <div style="font-size:0.8rem;color:#94a3b8;">Direct WhatsApp deal allocation and private off-market inventory.</div>
                        </div>
                    </div>
                </div>

                <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:1rem;display:flex;align-items:center;gap:8px;font-size:0.75rem;color:#94a3b8;">
                    <span class="material-symbols-rounded" style="font-size:16px;color:#38bdf8;">lock</span>
                    <span>256-Bit SSL Encrypted Session · Safe & Confidential</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_form:
        with st.form("register_main_form", clear_on_submit=False):
            st.markdown(
                """
                <div style="margin-bottom:1rem;">
                    <h3 style="font-size:1.35rem;font-weight:700;color:#0f172a;margin:0 0 0.3rem 0;">Account Information</h3>
                    <p style="color:#64748b;font-size:0.88rem;margin:0;">Fill in your details below. All fields marked with * are required.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            name = st.text_input("Full Name *", placeholder="Enter your full name", key="reg_name")
            email = st.text_input("Email Address *", placeholder="name@company.com", key="reg_email")
            phone = st.text_input("Mobile Number (10 digits) *", placeholder="e.g. 9876543210", key="reg_phone")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                password = st.text_input("Create Password *", type="password", placeholder="Min 8 characters", key="reg_pass")
            with col_p2:
                confirm = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password", key="reg_confirm")

            st.caption("By creating an account you agree to our Terms of Service & Privacy Policy.")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            submit = st.form_submit_button("Create Account & Access Intelligence", width='stretch', type="primary", icon=":material/how_to_reg:")
            back = st.form_submit_button("Back to Home", width='stretch', icon=":material/arrow_back:")

        if back:
            st.session_state.page = "home"
            st.rerun()

        if submit:
            if not name or not email or not phone or not password or not confirm:
                st.error("Please fill all required fields.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            elif len(phone) != 10 or not phone.isdigit():
                st.error("Please enter a valid 10-digit mobile number.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long.")
            elif password != confirm:
                st.error("Passwords do not match. Please verify.")
            elif email in st.session_state.users:
                st.warning("This email is already registered. Please log in from the sidebar.")
            else:
                user = {
                    "name": sanitize_text(name, 100),
                    "email": email.strip().lower(),
                    "phone": phone.strip(),
                    "password": hash_password(password),
                    "is_admin": False,
                }
                st.session_state.users[email] = user
                save_user(user)
                try:
                    send_welcome_email(name, email)
                except Exception:
                    pass
                st.session_state.logged_in = True
                st.session_state.current_user = user["name"]
                st.session_state.current_email = email
                st.session_state.saved_properties = []
                st.session_state.is_admin = False
                st.success("Account created successfully! Welcome to AREI™.")
                st.balloons()
                st.session_state.page = "explore"
                st.rerun()

        st.markdown(
            """
            <div style="margin-top:1.2rem;text-align:center;padding:0.9rem;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;">
                <span style="font-size:0.88rem;color:#475569;">Already have an account? </span>
                <span style="font-size:0.88rem;color:#0ea5e9;font-weight:700;">Use the Access Portal in the left sidebar to log in.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_pricing_page():
    """
    Subscription plans — 3 perfectly balanced tiers.
    Equal height, symmetrical cards, no awkward jumps.
    """
    st.markdown(
        """
        <div class="hero-banner" style="padding:2.8rem 2rem 2.2rem;margin-bottom:2rem;">
            <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.15);color:#ffffff;padding:4px 14px;border-radius:999px;font-size:0.75rem;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:0.8rem;">
                <span class="material-symbols-rounded" style="font-size:16px;">loyalty</span> AREI MEMBERSHIP TIERS
            </div>
            <h1 style="font-size:2.4rem;font-weight:800;letter-spacing:-0.03em;">Choose Your Intelligence Plan</h1>
            <p style="max-width:700px;margin:0 auto;color:#e0f2fe;font-size:1.1rem;">
                From individual homebuyers to institutional capital allocators, select the intelligence level tailored to your investment thesis. Cancel anytime.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plans = [
        {
            "id": "free",
            "name": "Free Explorer",
            "badge": "BASIC ACCESS",
            "badge_style": "background:#f1f5f9;color:#475569;",
            "price_display": "₹0",
            "period": "forever",
            "price_inr": 0,
            "highlight": False,
            "features": [
                "Browse all Gurugram live property listings",
                "Micro-market area & BHK filter matrix",
                "Real-time price & rate/sq.ft summaries",
                "Up to 5 saved property shortlists",
                "Basic mortgage & investment calculators",
                "Interactive GIS micro-market map layer",
                "Standard community & FAQ support",
            ],
            "cta_label": "Start Exploring Free",
            "cta_icon": ":material/explore:",
            "cta_type": "secondary",
        },
        {
            "id": "pro",
            "name": "Pro Intelligence",
            "badge": "MOST POPULAR",
            "badge_style": "background:#0ea5e9;color:#ffffff;box-shadow:0 4px 12px rgba(14,165,233,0.3);",
            "price_display": "₹999",
            "period": "per month",
            "price_inr": 999,
            "highlight": True,
            "features": [
                "Everything included in Free Explorer",
                "Full G-REPI™ Market Index access",
                "FairValue AVM™ instant valuation model",
                "CapYield™ & 10-Yr IRR forecast engine",
                "Unlimited saved property shortlists",
                "Institutional PDF Investment Dossier exports",
                "Priority WhatsApp deal alerts & broker advisory",
            ],
            "cta_label": "Upgrade to Pro Intelligence",
            "cta_icon": ":material/bolt:",
            "cta_type": "primary",
        },
        {
            "id": "enterprise",
            "name": "Enterprise Institutional",
            "badge": "INSTITUTIONAL",
            "badge_style": "background:#ede9fe;color:#7c3aed;",
            "price_display": "₹4,999",
            "period": "per month",
            "price_inr": 4999,
            "highlight": False,
            "features": [
                "Everything included in Pro Intelligence",
                "Pan-India 50+ major cities expansion database",
                "Bulk historical data export (CSV & JSON)",
                "White-label branded investment dossiers",
                "Developer REST API access keys",
                "Custom econometric and yield models",
                "Dedicated 1-on-1 Portfolio Advisor & SLA",
            ],
            "cta_label": "Talk to Enterprise Desk",
            "cta_icon": ":material/support_agent:",
            "cta_type": "secondary",
        },
    ]

    cols = st.columns(3, gap="medium")

    for col, plan in zip(cols, plans):
        with col:
            featured_class = "featured" if plan["highlight"] else ""
            badge_icon = '<span class="material-symbols-rounded" style="font-size:14px;vertical-align:middle;">auto_awesome</span> ' if plan["highlight"] else ''
            
            features_html = "".join([
                f'<li><span class="material-symbols-rounded arei-check-icon">check_circle</span><span>{f}</span></li>'
                for f in plan["features"]
            ])

            card_html = f"""
            <div class="arei-pricing-card {featured_class}">
                <div>
                    <div class="arei-badge-slot">
                        <span class="arei-pill-badge" style="{plan['badge_style']}">{badge_icon}{plan['badge']}</span>
                    </div>
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.35rem;font-weight:700;color:#0f172a;text-align:center;margin-bottom:0.4rem;">
                        {plan['name']}
                    </div>
                    <div style="text-align:center;margin-bottom:1.1rem;padding-bottom:1rem;border-bottom:1px solid #e2e8f0;">
                        <span style="font-size:2.25rem;font-weight:900;color:{'#0ea5e9' if plan['highlight'] else '#0f172a'};">{plan['price_display']}</span>
                        <span style="color:#64748b;font-size:0.88rem;font-weight:600;"> / {plan['period']}</span>
                    </div>
                    <ul class="arei-pricing-features">
                        {features_html}
                    </ul>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            if plan["id"] == "free":
                if st.button(plan["cta_label"], key="btn_plan_free", icon=plan["cta_icon"], width='stretch', type="secondary"):
                    st.session_state.page = "explore"
                    st.rerun()
            elif plan["id"] == "enterprise":
                st.link_button(plan["cta_label"], url=WHATSAPP, icon=plan["cta_icon"], width='stretch')
            else:
                if st.button(plan["cta_label"], key="btn_plan_pro", icon=plan["cta_icon"], type="primary", width='stretch'):
                    st.session_state["pending_plan"] = plan
                    st.session_state.page = "checkout"
                    st.rerun()

    st.markdown("---")

    # FAQ Section
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">
            <span class="material-symbols-rounded" style="color:#0ea5e9;font-size:24px;">help</span>
            <h3 style="margin:0;font-size:1.4rem;font-weight:700;color:#0f172a;">Frequently Asked Questions</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fcol1, fcol2 = st.columns(2, gap="medium")
    with fcol1:
        with st.expander("Can I cancel or upgrade my subscription anytime?"):
            st.write("Yes, absolutely. You can cancel, pause, or upgrade your subscription plan at any time directly through your account dashboard with zero lock-in periods.")
        with fcol2:
            with st.expander("What payment methods are supported?"):
                st.write("We accept UPI (Google Pay, PhonePe, Paytm), All Major Credit/Debit Cards (Visa, Mastercard, RuPay, Amex), Net Banking across 50+ Indian banks, and EMI via Razorpay.")

    fcol3, fcol4 = st.columns(2, gap="medium")
    with fcol3:
        with st.expander("How accurate is the FairValue AVM™ valuation?"):
            st.write("Our Automated Valuation Model (AVM) is trained on verified transactions across Gurugram and achieves high statistical precision by analyzing floor, orientation, amenities, and micro-market velocity.")
    with fcol4:
        with st.expander("Is my personal and financial data safe?"):
            st.write("All credentials are encrypted with PBKDF2-SHA256, and data handling complies with the Digital Personal Data Protection (DPDP) Act 2023. We do not store credit card details or share your data.")


def show_checkout_page():
    """Razorpay checkout for selected plan with clean Material design."""
    plan = st.session_state.get("pending_plan")
    if not plan:
        st.session_state.page = "pricing"
        st.rerun()
        return

    st.markdown(
        f"""
        <div class="hero-banner" style="padding:2.2rem 2rem 1.8rem;margin-bottom:2rem;">
            <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.15);color:#ffffff;padding:4px 14px;border-radius:999px;font-size:0.75rem;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:0.6rem;">
                <span class="material-symbols-rounded" style="font-size:16px;">lock</span> SECURE ENCRYPTED CHECKOUT
            </div>
            <h1 style="font-size:2.2rem;font-weight:800;">Complete Your Subscription to {plan['name']}</h1>
            <p style="color:#e0f2fe;font-size:1rem;margin:0;">Instant activation · 256-bit bank grade encryption powered by Razorpay</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            f"""
            <div style="background:#ffffff;border:1.5px solid #cbd5e1;border-radius:18px;padding:1.8rem;box-shadow:0 8px 24px rgba(15,23,42,0.06);">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">
                    <span class="material-symbols-rounded" style="color:#0ea5e9;font-size:22px;">receipt_long</span>
                    <span style="font-weight:700;font-size:1.2rem;color:#0f172a;">Order Summary</span>
                </div>
                <div style="font-size:1.35rem;font-weight:800;color:#0f172a;margin-bottom:0.4rem;">
                    {plan['name']}
                </div>
                <div style="font-size:2.2rem;font-weight:900;color:#0ea5e9;margin-bottom:1.2rem;border-bottom:1px solid #e2e8f0;padding-bottom:1rem;">
                    {plan['price_display']} <span style="font-size:0.92rem;color:#64748b;font-weight:600;">/ {plan['period']}</span>
                </div>
                <div style="font-weight:700;font-size:0.88rem;color:#334155;margin-bottom:0.75rem;text-transform:uppercase;letter-spacing:0.04em;">
                    Plan Inclusions:
                </div>
                <ul style="padding-left:0;list-style:none;margin:0 0 1.5rem 0;">
                    {''.join(f'<li style="display:flex;align-items:center;gap:8px;margin-bottom:8px;color:#334155;font-size:0.9rem;"><span class="material-symbols-rounded" style="color:#0ea5e9;font-size:18px;">check_circle</span><span>{f}</span></li>' for f in plan['features'])}
                </ul>
                <div style="background:#f8fafc;border-radius:12px;padding:0.9rem;border:1px solid #e2e8f0;font-size:0.82rem;color:#64748b;display:flex;align-items:center;gap:8px;">
                    <span class="material-symbols-rounded" style="color:#10b981;font-size:18px;">verified_user</span>
                    <span>100% money-back guarantee within 7 days if unsatisfied.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        with st.form("checkout_form"):
            st.markdown(
                """
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">
                    <span class="material-symbols-rounded" style="color:#0ea5e9;font-size:22px;">person</span>
                    <span style="font-weight:700;font-size:1.2rem;color:#0f172a;">Billing & Contact Details</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            cust_name = st.session_state.get("current_user", "")
            cust_email_default = st.session_state.get("current_email", "")

            name_val = st.text_input("Full Name *", value=cust_name, placeholder="Enter your full name")
            email_val = st.text_input("Email Address *", value=cust_email_default, placeholder="name@example.com")
            phone_val = st.text_input("Mobile Number (10 digits) *", placeholder="e.g. 9876543210")
            agree = st.checkbox("I agree to the Terms of Service, DPDP Privacy Policy, and Recurring Billing terms")

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            pay_btn = st.form_submit_button(f"Proceed to Secure Payment ({plan['price_display']})", type="primary", icon=":material/lock:", width='stretch')

        if pay_btn:
            phone_ok, clean_ph = validate_phone_number(phone_val)
            email_ok, clean_em = validate_email_address(email_val)
            if not name_val or not phone_val or not email_val:
                st.error("Please fill in all required fields.")
            elif not phone_ok:
                st.error(clean_ph)
            elif not email_ok:
                st.error(clean_em)
            elif not agree:
                st.warning("Please check the box to agree to the Terms of Service.")
            elif not _rzp_live():
                st.info("Razorpay automated gateway is currently in preview mode. Click below to confirm directly with our billing desk via WhatsApp:")
                wa_msg = f"Hi! I want to subscribe to {plan['name']} plan {plan['price_display']}/month on AREI Platform. Name: {name_val}, Email: {clean_em}, Phone: {clean_ph}"
                st.link_button(
                    f"Subscribe via WhatsApp ({plan['price_display']}/mo)",
                    url=f"https://wa.me/91{CONTACT_NUMBER}?text={urllib.parse.quote(wa_msg)}",
                    type="primary",
                    icon=":material/chat:",
                    width='stretch',
                )
            else:
                with st.spinner("Generating secure payment link..."):
                    ok, result = create_payment_link(
                        amount_inr=plan["price_inr"],
                        customer_name=name_val,
                        customer_email=clean_em,
                        customer_phone=clean_ph,
                        plan_name=plan["name"],
                    )
                if ok:
                    st.success("Secure payment link generated successfully!")
                    st.link_button(
                        f"Pay {plan['price_display']} via Razorpay Gateway",
                        url=result,
                        type="primary",
                        icon=":material/credit_card:",
                        width='stretch',
                    )
                    st.caption("Secured by Razorpay · UPI, Cards, Net Banking, EMI accepted.")
                else:
                    st.error(f"Payment gateway returned: {result}")
                    st.link_button("Subscribe via WhatsApp Support", url=WHATSAPP, icon=":material/support_agent:")

    st.markdown("---")
    if st.button("Back to Pricing Plans", icon=":material/arrow_back:"):
        st.session_state.page = "pricing"
        st.rerun()


def show_back_next(current_page: str):
    """Renders clean, icon-backed Back / Next buttons at the bottom of every page."""
    PAGE_ORDER = [
        "home", "explore", "shortlist", "intelligence",
        "analytics", "reports", "map", "ask_akhi", "pricing", "inquiry",
    ]
    if current_page not in PAGE_ORDER:
        return
    idx = PAGE_ORDER.index(current_page)
    st.markdown("---")
    left, _, right = st.columns([1, 4, 1])
    with left:
        if idx > 0:
            prev_page = PAGE_ORDER[idx - 1]
            if st.button("Back", key=f"back_{current_page}", icon=":material/arrow_back:", width='stretch'):
                st.session_state.page = prev_page
                st.rerun()
    with right:
        if idx < len(PAGE_ORDER) - 1:
            next_page = PAGE_ORDER[idx + 1]
            if st.button("Next", key=f"next_{current_page}", icon=":material/arrow_forward:", width='stretch', type="primary"):
                st.session_state.page = next_page
                st.rerun()


def main():
    show_auth_sidebar()
    show_page_navigation()

    page = st.session_state.page

    if page == "home":
        show_landing_page(get_clean_data())
        show_back_next("home")
    elif page == "explore":
        show_property_cards(get_clean_data())
        show_back_next("explore")
    elif page == "shortlist":
        show_shortlist()
        show_back_next("shortlist")
    elif page == "account":
        user_dashboard()
    elif page == "property_detail":
        show_property_detail(get_clean_data(), st.session_state.get("selected_property"))
    elif page == "inquiry":
        show_inquiry_form(st.session_state.get("selected_property"))
        show_back_next("inquiry")
    elif page == "analytics":
        show_analytics(get_clean_data())
        show_back_next("analytics")
    elif page == "reports":
        market_reports(get_clean_data())
        show_back_next("reports")
    elif page == "map":
        gurugram_map(get_clean_data())
        show_back_next("map")
    elif page == "intelligence":
        property_intelligence(get_clean_data())
        show_back_next("intelligence")
    elif page == "ask_akhi":
        ask_akhi(get_clean_data())
        show_back_next("ask_akhi")
    elif page == "pricing":
        show_pricing_page()
        show_back_next("pricing")
    elif page == "checkout":
        show_checkout_page()
    elif page == "register":
        show_register_page()
    elif page == "admin":
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            st.error("Access Denied: Administrator credentials required.")
            if st.button("Back to Home", icon=":material/home:"):
                st.session_state.page = "home"
                st.rerun()


if __name__ == "__main__":
    main()

