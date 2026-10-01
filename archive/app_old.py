from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from backend import ensure_admin_account, get_total_leads, load_leads, load_users, save_lead, save_user
from real_estate_analysis import clean_real_estate_data, load_real_estate_data

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Akhi Properties | Gurugram Real Estate",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Business Constants
CONTACT_NUMBER = "6387594514"
INSTAGRAM = "https://instagram.com/youknow_akhi"
WEBSITE = "https://yourwebsite.com"
WHATSAPP = "https://wa.me/916387594514"
EMAIL = "contact@akhi-properties.com"

# Global Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"], .main {
        background: linear-gradient(135deg, #0f172a 0%, #1a2a47 50%, #111827 100%) !important;
        color: #e5e7eb !important;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.98) !important;
        border-right: 1px solid rgba(96, 165, 250, 0.2);
    }
    
    .main .block-container {
        max-width: 1400px;
        padding: 2rem 1rem;
    }
    
    h1, h2, h3, h4 {
        color: #f0f9ff !important;
        font-weight: 700;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(96,165,250,0.15), rgba(59,130,246,0.1));
        border: 1px solid rgba(96,165,250,0.3);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .property-card {
        background: linear-gradient(135deg, rgba(17,24,39,0.98), rgba(30,41,59,0.98));
        border: 1px solid rgba(96,165,250,0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(15,23,42,0.4);
    }
    
    .property-card:hover {
        border-color: rgba(96,165,250,0.5);
        box-shadow: 0 8px 25px rgba(96,165,250,0.15);
        transform: translateY(-4px);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 1px solid rgba(96,165,250,0.2);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        color: white !important;
        border: none;
    }
    
    .lead-item {
        background: rgba(96,165,250,0.08);
        border-left: 4px solid #60a5fa;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 8px;
    }
    
    .stTabs [role="tablist"] {
        background: rgba(17, 24, 39, 0.95);
        border-bottom: 1px solid rgba(96,165,250,0.2);
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom: 2px solid #60a5fa !important;
    }
    
    a {
        color: #93c5fd !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #bfdbfe !important;
        text-decoration: underline;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7cb3f6, #4c9aff) !important;
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
        return "₹0.00"
    return f"₹{float(value):,.2f}"


def init_session_state():
    if "users" not in st.session_state:
        st.session_state.users = ensure_admin_account()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "page" not in st.session_state:
        st.session_state.page = "home"


init_session_state()


def show_landing_page():
    st.markdown(
        """
        <div class="hero-banner">
            <h1>🏠 Akhi Properties</h1>
            <p style="font-size: 1.3rem; margin: 1rem 0; color: #bfdbfe;">
                Your Premium Gurugram Real Estate Advisor
            </p>
            <p style="color: #cbd5e1; margin-bottom: 2rem;">
                Expert guidance for buyers, investors, and families in Gurugram. 
                Smart deals. Better profits. Professional service.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">14K+</h3>
                <p style="color: #9ca3af; margin: 0;">Properties</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">100+</h3>
                <p style="color: #9ca3af; margin: 0;">Localities</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">500+</h3>
                <p style="color: #9ca3af; margin: 0;">Happy Clients</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">₹1000Cr</h3>
                <p style="color: #9ca3af; margin: 0;">Deals Closed</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Why Choose Akhi Properties?")
        st.markdown(
            """
            ✓ **Expert Market Analysis** - Real-time data-driven insights
            
            ✓ **Verified Listings** - Only authentic properties from trusted sources
            
            ✓ **Profit Sharing** - Transparent deal structures & profit participation
            
            ✓ **Personal Guidance** - 1-on-1 consultation for your investment goals
            
            ✓ **Discount Support** - Help negotiate 2-5% discounts on properties
            
            ✓ **Quick Closure** - Fast-tracked property transactions
            """
        )

    with col2:
        st.subheader("Quick Connect")
        st.markdown(
            f"""
            <div style="background: rgba(96,165,250,0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #60a5fa;">
                <p style="margin: 0.5rem 0;"><b>📞 Call:</b> <a href="tel:{CONTACT_NUMBER}">{CONTACT_NUMBER}</a></p>
                <p style="margin: 0.5rem 0;"><b>💬 WhatsApp:</b> <a href="{WHATSAPP}" target="_blank">Chat Now</a></p>
                <p style="margin: 0.5rem 0;"><b>📸 Instagram:</b> <a href="{INSTAGRAM}" target="_blank">@youknow_akhi</a></p>
                <p style="margin: 0.5rem 0;"><b>🌐 Website:</b> <a href="{WEBSITE}" target="_blank">{WEBSITE}</a></p>
                <p style="margin: 0.5rem 0;"><b>📧 Email:</b> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("Featured Services")

    service_col1, service_col2, service_col3 = st.columns(3)

    with service_col1:
        st.markdown(
            """
            <div class="property-card">
                <h4>🎯 Buyer Guidance</h4>
                <p>Smart property selection based on your budget and goals. 
                Get expert recommendations tailored to your needs.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with service_col2:
        st.markdown(
            """
            <div class="property-card">
                <h4>💼 Investment Plans</h4>
                <p>Profit-sharing investment strategies with ROI projections. 
                Maximize returns with professional guidance.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with service_col3:
        st.markdown(
            """
            <div class="property-card">
                <h4>🤝 Deal Negotiation</h4>
                <p>Expert negotiation support to get you the best price. 
                Typical savings: 2-5% on property value.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if st.button("📊 Explore Properties Now", use_container_width=True, type="primary"):
        st.session_state.page = "explore"
        st.rerun()


def show_property_cards(df: object):
    st.subheader("🏘️ Featured Properties")

    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_property_type = st.selectbox(
            "Property Type",
            ["All"] + sorted(df["Property Type"].dropna().unique().tolist()),
            key="explore_type",
        )
    with col2:
        selected_bhk = st.selectbox(
            "BHK",
            ["All"] + sorted([int(x) for x in df["BHK_Count"].dropna().unique()]),
            key="explore_bhk",
        )
    with col3:
        min_price, max_price = st.select_slider(
            "Price Range (Cr)",
            options=range(int(df["Price"].min() / 10000000), int(df["Price"].max() / 10000000) + 1),
            value=(
                int(df["Price"].min() / 10000000),
                int(df["Price"].max() / 10000000),
            ),
            key="explore_price",
        )
    with col4:
        selected_locality = st.selectbox(
            "Locality",
            ["All"] + sorted(df["Locality"].dropna().unique().tolist())[:50],
            key="explore_locality",
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

    # Display as cards
    for idx, row in filtered.head(12).iterrows():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1], gap="medium")

        with col1:
            st.markdown(
                f"""
                <div class="property-card">
                    <h4 style="margin-top: 0; color: #60a5fa;">{row['Locality']}</h4>
                    <p style="margin: 0.5rem 0; font-size: 0.95rem;">
                        <b>{int(row['BHK_Count'])} BHK</b> • {int(row['Area'])} sqft • {row['Property Type']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div style="background: rgba(96,165,250,0.1); padding: 1rem; border-radius: 10px; text-align: center;">
                    <p style="margin: 0; font-size: 0.85rem; color: #9ca3af;">Price</p>
                    <h4 style="margin: 0.5rem 0; color: #60a5fa;">₹{row['Price']/10000000:.1f} Cr</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div style="background: rgba(96,165,250,0.1); padding: 1rem; border-radius: 10px; text-align: center;">
                    <p style="margin: 0; font-size: 0.85rem; color: #9ca3af;">Rate/sqft</p>
                    <h4 style="margin: 0.5rem 0; color: #93c5fd;">₹{row.get('Rate per sqft', 0):,.0f}</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col4:
            if st.button("📞 Inquire", key=f"inquire_{idx}", use_container_width=True):
                st.session_state.page = "inquiry"
                st.session_state.selected_property = row.to_dict()
                st.rerun()


def show_inquiry_form(property_data=None):
    st.subheader("📋 Buyer Consultation Request")

    if property_data:
        st.info(
            f"📍 Property: {property_data['Locality']} | "
            f"{int(property_data['BHK_Count'])} BHK | "
            f"₹{property_data['Price']/10000000:.1f} Cr"
        )

    with st.form("inquiry_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *", key="inquiry_name")
            phone = st.text_input("Phone Number *", key="inquiry_phone", placeholder="10-digit mobile number")

        with col2:
            email = st.text_input("Email (Optional)", key="inquiry_email")
            budget = st.number_input("Budget (₹ Crore) *", min_value=5.0, max_value=500.0, value=50.0, key="inquiry_budget")

        interest = st.selectbox(
            "Primary Interest *",
            ["Property Buying", "Investment", "Rental Income", "Lease", "Commercial"],
            key="inquiry_interest",
        )

        message = st.text_area(
            "Additional Details (Tell us about your preferences, timeline, etc.)",
            placeholder="e.g., Looking for 2-3 BHK near metro, family of 4, need by March 2025",
            height=100,
            key="inquiry_message",
        )

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("📤 Submit Inquiry", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

    if cancel:
        st.session_state.page = "explore"
        st.rerun()

    if submit:
        if not name or not phone or not budget:
            st.error("Please fill all required fields marked with *")
        elif len(phone) != 10 or not phone.isdigit():
            st.error("Please enter a valid 10-digit phone number")
        else:
            lead = {
                "name": name,
                "phone": phone,
                "email": email or "N/A",
                "budget": float(budget),
                "interest": interest,
                "message": message,
                "property": property_data["Locality"] if property_data else "N/A",
            }
            save_lead(lead)
            st.success("✅ Your inquiry has been submitted! I'll contact you within 24 hours.")
            st.balloons()

            if st.button("Return to Explore"):
                st.session_state.page = "explore"
                st.rerun()


def show_admin_dashboard():
    st.subheader("👨‍💼 Admin Dashboard")

    admin_col1, admin_col2, admin_col3 = st.columns(3)

    total_leads = get_total_leads()
    registered_users = len(st.session_state.users)

    with admin_col1:
        st.markdown(
            f"""
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">{total_leads}</h3>
                <p style="color: #9ca3af; margin: 0;">Active Leads</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with admin_col2:
        st.markdown(
            f"""
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">{registered_users}</h3>
                <p style="color: #9ca3af; margin: 0;">Registered Users</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with admin_col3:
        st.markdown(
            f"""
            <div class="stat-box">
                <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">📊</h3>
                <p style="color: #9ca3af; margin: 0;">Pipeline Status</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    admin_tabs = st.tabs(["📌 All Leads", "👥 Users", "⚙️ Settings"])

    with admin_tabs[0]:
        st.subheader("Buyer Leads")
        leads = load_leads()

        if not leads:
            st.info("No leads yet. Leads will appear here when buyers submit inquiries.")
        else:
            for i, lead in enumerate(leads[::-1], 1):
                st.markdown(
                    f"""
                    <div class="lead-item">
                        <b>#{i}. {lead.get('name', 'N/A')}</b> | {lead.get('interest', 'N/A')}<br>
                        📞 {lead.get('phone', 'N/A')} | 💰 ₹{lead.get('budget', 'N/A')} Cr<br>
                        📍 Property: {lead.get('property', 'Not Specified')} | 📧 {lead.get('email', 'N/A')}<br>
                        📝 {lead.get('message', 'No message')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with admin_tabs[1]:
        st.subheader("Registered Users")
        if not st.session_state.users:
            st.info("No registered users yet.")
        else:
            users_df = pd.DataFrame.from_dict(st.session_state.users, orient="index")
            st.dataframe(users_df[["name", "email", "phone"]], use_container_width=True)

    with admin_tabs[2]:
        st.subheader("Settings")
        st.info("📞 Contact: " + CONTACT_NUMBER)
        st.info("📸 Instagram: " + INSTAGRAM)
        st.info("💬 WhatsApp: " + WHATSAPP)

        if st.button("🚪 Logout from Admin"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.current_user = ""
            st.session_state.page = "home"
            st.rerun()


def show_auth_sidebar():
    with st.sidebar:
        st.header("🔐 Access Portal")

        if not st.session_state.logged_in:
            auth_tabs = st.tabs(["Login", "Register"])

            with auth_tabs[0]:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")

                if st.button("🔓 Login", use_container_width=True, type="primary"):
                    user = st.session_state.users.get(email)
                    if user and user.get("password") == password:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user["name"]
                        st.session_state.is_admin = email == "iamakv01@gmail.com"
                        st.success(f"Welcome, {user['name']}!" + (" 🛡️ (Admin Mode)" if st.session_state.is_admin else ""))
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            with auth_tabs[1]:
                name = st.text_input("Full Name", key="register_name")
                email = st.text_input("Email", key="register_email")
                phone = st.text_input("Phone", key="register_phone")
                password = st.text_input("Password", type="password", key="register_password")

                if st.button("✅ Create Account", use_container_width=True, type="primary"):
                    if not name or not email or not phone or not password:
                        st.warning("Please fill all fields")
                    elif email in st.session_state.users:
                        st.warning("Email already registered")
                    else:
                        user = {"name": name, "email": email, "phone": phone, "password": password}
                        st.session_state.users[email] = user
                        save_user(user)
                        st.success("Account created! Please login.")
                        st.rerun()
        else:
            st.markdown(f"**👤 {st.session_state.current_user}**")

            if st.session_state.is_admin:
                st.markdown("**🛡️ ADMIN MODE**")

                if st.button("📊 Admin Dashboard"):
                    st.session_state.page = "admin"
                    st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏠 Home"):
                    st.session_state.page = "home"
                    st.rerun()
            with col2:
                if st.button("📤 Logout"):
                    st.session_state.logged_in = False
                    st.session_state.is_admin = False
                    st.session_state.current_user = ""
                    st.session_state.page = "home"
                    st.rerun()


def main():
    show_auth_sidebar()

    if st.session_state.page == "home":
        show_landing_page()
    elif st.session_state.page == "explore":
        df = get_clean_data()
        show_property_cards(df)
    elif st.session_state.page == "inquiry":
        property_data = st.session_state.get("selected_property")
        show_inquiry_form(property_data)
    elif st.session_state.page == "admin":
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            st.error("Access Denied. Admin privileges required.")
            if st.button("Back to Home"):
                st.session_state.page = "home"
                st.rerun()


if __name__ == "__main__":
    main()
