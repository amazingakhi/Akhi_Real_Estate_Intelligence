from pathlib import Path

ROOT = Path(r"d:\Akhi_Real_Estate\Gurugram_Real_Estate_Analysis")
APP = ROOT / "src" / "app.py"
UI = ROOT / "src" / "components" / "ui_styles.py"
VIEWS = ROOT / "src" / "views.py"

text = APP.read_text(encoding="utf-8")
lines = text.splitlines(True)

css_src = "".join(lines[82:847])  # 1-based 83-847
css_indented = "".join("    " + ln if ln.strip() else ln for ln in css_src.splitlines(True))
chrome_fn = (
    "\n\ndef inject_app_chrome() -> None:\n"
    '    """Light-theme shell styles for listings, hero, forms, and navigation."""\n'
    + css_indented
)
ui = UI.read_text(encoding="utf-8")
if "def inject_app_chrome" not in ui:
    ui = ui.rstrip() + chrome_fn + "\n"
    ui = ui.replace(
        "        unsafe_allow_html=True,\n    )\n",
        "        unsafe_allow_html=True,\n    )\n    inject_app_chrome()\n",
        1,
    )
    UI.write_text(ui, encoding="utf-8")

header = '''from __future__ import annotations

import json
import re
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from backend import (
    get_total_leads,
    load_leads,
    remove_shortlist_item,
    save_lead,
    save_shortlist_item,
)
from price_prediction import predict_price
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
from runtime import money, get_clean_data
from config.settings import (
    CONTACT_NUMBER,
    EMAIL,
    INSTAGRAM,
    WHATSAPP,
    WEBSITE,
    PLATFORM_NAME,
    razorpay_is_configured,
)


'''

show_shortlist = "".join(lines[860:886])
rest = "".join(lines[942:3038])
views = header + show_shortlist + "\n\n" + rest

views = views.replace(
    '        title="🤖 AREI™ Intelligent Deal Advisory Desk",\n'
    '        subtitle="Natural-Language Intent Parser, G-REPI™ Ranked Deal Discovery & Institutional Verdicts",\n'
    '        badges=["AI DEAL ADVISOR", "G-REPI™ MATCHED", "INSTITUTIONAL STRATEGY"],',
    '        title="Ask Akhi — listing matcher",\n'
    '        subtitle="Parses budget, BHK, and corridor from your text, then filters this dataset. Not a generative AI chatbot.",\n'
    '        badges=["CRITERIA PARSER", "LISTING FILTER", "G-REPI RANK"],',
)
views = views.replace(
    '            st.info("⚠️ Keep these keys secure and never share them publicly")\n'
    '            st.text_input("Razorpay Live Key", value="rzp_live_YOUR_KEY", disabled=True, type="password")\n'
    '            st.text_input("Razorpay Secret", disabled=True, type="password")',
    '            st.caption("Keys are read from environment variables. They are never shown here.")\n'
    '            if razorpay_is_configured():\n'
    '                st.success("Razorpay key is set in .env")\n'
    '            else:\n'
    '                st.warning("Razorpay is not configured. Set RAZORPAY_KEY_ID in .env to enable payments later.")\n'
    '            st.text(f"Website: {WEBSITE}")\n'
    '            st.text(f"Platform: {PLATFORM_NAME}")',
)
VIEWS.write_text(views, encoding="utf-8")

new_app = '''from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from backend import (
    ensure_admin_account,
    hash_password,
    load_shortlist,
    save_user,
    verify_password,
)
from components import inject_premium_fintech_theme
from config.settings import PLATFORM_NAME
from runtime import get_clean_data
from security import validate_email_address, validate_phone_number
from views import (
    ask_akhi,
    gurugram_map,
    market_reports,
    property_intelligence,
    show_admin_dashboard,
    show_analytics,
    show_inquiry_form,
    show_landing_page,
    show_property_cards,
    show_property_detail,
    show_shortlist,
    user_dashboard,
)

st.set_page_config(
    page_title=f"{PLATFORM_NAME} | AREI Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_premium_fintech_theme()


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
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None


init_session_state()


def show_page_navigation():
    pages = [
        ("🏛️ Executive Terminal", "home"),
        ("📊 AREI Intelligence", "intelligence"),
        ("🏘️ Explore Inventory", "explore"),
        (f"📌 Shortlist ({len(st.session_state.saved_properties)})", "shortlist"),
        ("📈 Market Analytics", "analytics"),
        ("📑 Due Diligence Reports", "reports"),
        ("🗺️ Gurugram Map", "map"),
        ("🔎 Ask Akhi", "ask_akhi"),
        ("💼 Advisory & Deals", "inquiry"),
    ]
    if st.session_state.logged_in:
        pages.insert(3, ("My dashboard", "account"))
    if st.session_state.is_admin:
        pages.append(("Admin", "admin"))

    st.markdown('<div class="page-navigation-label">Navigate</div>', unsafe_allow_html=True)
    nav_columns = st.columns(len(pages))
    for column, (label, page) in zip(nav_columns, pages):
        with column:
            button_type = "primary" if st.session_state.page == page else "secondary"
            if st.button(label, key=f"nav_{page}", type=button_type, width="stretch"):
                st.session_state.page = page
                if page != "inquiry":
                    st.session_state.pop("selected_property", None)
                    st.session_state.pop("selected_service", None)
                st.rerun()
    st.markdown("---")


def show_auth_sidebar():
    with st.sidebar:
        st.header("Access portal")

        if not st.session_state.logged_in:
            auth_tabs = st.tabs(["Login", "Register"])

            with auth_tabs[0]:
                email = st.text_input("Email", key="login_email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", key="login_password")

                if st.button("Login", width="stretch", type="primary"):
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
                name = st.text_input("Full Name", key="register_name")
                email = st.text_input("Email", key="register_email")
                phone = st.text_input("Phone", key="register_phone")
                password = st.text_input("Password", type="password", key="register_password")

                if st.button("Create account", width="stretch", type="primary"):
                    ok_email, clean_email = validate_email_address(email)
                    ok_phone, clean_phone = validate_phone_number(phone)
                    if not name or not email or not phone or not password:
                        st.warning("Please fill all fields")
                    elif not ok_email:
                        st.warning("Please enter a valid email address")
                    elif not ok_phone:
                        st.warning("Please enter a valid 10-digit phone number")
                    elif len(password) < 8:
                        st.warning("Password must contain at least 8 characters")
                    elif clean_email in st.session_state.users:
                        st.warning("Email already registered")
                    else:
                        user = {
                            "name": name,
                            "email": clean_email,
                            "phone": clean_phone,
                            "password": hash_password(password),
                        }
                        st.session_state.users[clean_email] = user
                        save_user(user)
                        st.success("Account created. Please log in.")
                        st.rerun()
        else:
            st.markdown(f"**{st.session_state.current_user}**")
            if st.session_state.is_admin:
                st.caption("Admin mode")
                if st.button("Admin dashboard", width="stretch"):
                    st.session_state.page = "admin"
                    st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Home", width="stretch"):
                    st.session_state.page = "home"
                    st.rerun()
            with col2:
                if st.button("Logout", width="stretch"):
                    st.session_state.logged_in = False
                    st.session_state.is_admin = False
                    st.session_state.current_user = ""
                    st.session_state.current_email = ""
                    st.session_state.saved_properties = []
                    st.session_state.page = "home"
                    st.rerun()


def main():
    show_auth_sidebar()
    show_page_navigation()
    page = st.session_state.page
    df = get_clean_data() if page not in {"shortlist", "account", "admin"} else None

    if page == "home":
        show_landing_page(df)
    elif page == "explore":
        show_property_cards(df)
    elif page == "shortlist":
        show_shortlist()
    elif page == "account":
        user_dashboard()
    elif page == "property_detail":
        show_property_detail(df, st.session_state.get("selected_property"))
    elif page == "inquiry":
        show_inquiry_form(st.session_state.get("selected_property"))
    elif page == "analytics":
        show_analytics(df)
    elif page == "reports":
        market_reports(df)
    elif page == "map":
        gurugram_map(df)
    elif page == "intelligence":
        property_intelligence(df)
    elif page == "ask_akhi":
        ask_akhi(df)
    elif page == "admin":
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            st.error("Access denied")
            if st.button("Back to home"):
                st.session_state.page = "home"
                st.rerun()


if __name__ == "__main__":
    main()
'''
APP.write_text(new_app, encoding="utf-8")
print("wrote", APP, "lines", new_app.count("\\n")+1)
print("wrote", VIEWS, "bytes", VIEWS.stat().st_size)
print("ui_styles", UI.stat().st_size)
