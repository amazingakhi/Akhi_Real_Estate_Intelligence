from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from backend import load_users, save_lead, save_user
from real_estate_analysis import build_summary, clean_real_estate_data, load_real_estate_data

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Gurugram Real Estate Dashboard",
    page_icon=":material/real_estate_agent:",
    layout="wide",
)

CONTACT_NUMBER = "6387594514"
INSTAGRAM = "https://instagram.com/youknow_akhi"
WEBSITE = "https://yourwebsite.com"
WHATSAPP = "https://wa.me/916387594514"


@st.cache_data
def get_clean_data() -> object:
    return clean_real_estate_data(load_real_estate_data())


def money(value: float | int | None) -> str:
    if value is None or value != value:
        return "₹0.00"
    return f"₹{float(value):,.2f}"


def init_session_state():
    if "users" not in st.session_state:
        st.session_state.users = load_users()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "buyer_leads" not in st.session_state:
        st.session_state.buyer_leads = []


init_session_state()


def login_register_panel():
    with st.sidebar:
        st.header("Client Access")
        auth_tab = st.tabs(["Login", "Register"])

        with auth_tab[0]:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = st.session_state.users.get(email)
                if user and user.get("password") == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user["name"]
                    st.success(f"Welcome back, {user['name']}!")
                else:
                    st.error("Invalid email or password.")

        with auth_tab[1]:
            name = st.text_input("Full Name", key="register_name")
            email = st.text_input("Email", key="register_email")
            phone = st.text_input("Phone Number", key="register_phone")
            password = st.text_input("Create Password", type="password", key="register_password")
            if st.button("Create Account"):
                if not name or not email or not phone or not password:
                    st.warning("Please fill all fields.")
                elif email in st.session_state.users:
                    st.warning("This email is already registered.")
                else:
                    user = {"name": name, "email": email, "phone": phone, "password": password}
                    st.session_state.users[email] = user
                    save_user(user)
                    st.session_state.logged_in = True
                    st.session_state.current_user = name
                    st.success(f"Account created for {name}.")

        if st.session_state.logged_in:
            st.markdown("---")
            st.caption(f"Signed in as: {st.session_state.current_user}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.current_user = ""
                st.rerun()


def filter_dataframe(df):
    with st.sidebar:
        st.header("Filters")
        st.caption("Refine the property market view")

        locality_options = sorted(df["Locality"].dropna().unique().tolist())
        property_options = sorted(df["Property Type"].dropna().unique().tolist())
        bhk_options = sorted(df["BHK_Count"].dropna().astype(int).unique().tolist())

        selected_localities = st.multiselect("Locality", locality_options, default=locality_options)
        selected_properties = st.multiselect("Property Type", property_options, default=property_options)
        selected_bhk = st.multiselect("BHK", bhk_options, default=bhk_options)

        min_price = int(df["Price"].min() / 10000000)
        max_price = int(df["Price"].max() / 10000000)
        price_range = st.slider("Price range (Cr)", min_value=min_price, max_value=max_price, value=(min_price, max_price))

        min_area = int(df["Area"].min())
        max_area = int(df["Area"].max())
        area_range = st.slider("Area range (sqft)", min_value=min_area, max_value=max_area, value=(min_area, max_area), step=100)

        st.markdown("---")
        st.caption("Quick market snapshot")
        st.metric("Listings in view", f"{df.shape[0]:,}", border=True)

    filtered = df.copy()
    filtered = filtered[filtered["Locality"].isin(selected_localities)]
    filtered = filtered[filtered["Property Type"].isin(selected_properties)]
    filtered = filtered[filtered["BHK_Count"].isin(selected_bhk)]
    filtered = filtered[
        (filtered["Price"] >= price_range[0] * 10000000)
        & (filtered["Price"] <= price_range[1] * 10000000)
    ]
    filtered = filtered[
        (filtered["Area"] >= area_range[0])
        & (filtered["Area"] <= area_range[1])
    ]

    return filtered


def buyer_help_section(df: object):
    st.subheader("Smart buying assistance")

    with st.form("buyer_form"):
        budget = st.slider("Your budget (Cr)", min_value=10, max_value=200, value=60, step=5)
        use_case = st.selectbox("Purpose", ["Investment", "Self Use", "Rental Income", "Family Home"])
        preferred_locality = st.selectbox("Preferred locality", sorted(df["Locality"].dropna().unique().tolist())[:20])
        target_bhk = st.selectbox("BHK needed", [1, 2, 3, 4, 5])
        submit = st.form_submit_button("Get my property plan")

    if submit:
        matched = df[
            (df["Locality"] == preferred_locality)
            & (df["BHK_Count"] == target_bhk)
            & (df["Price"] <= budget * 10000000)
        ].sort_values("Price").head(5)

        if matched.empty:
            st.warning("No exact match found in this range. I can suggest nearby options in premium alternatives.")
        else:
            best_option = matched.iloc[0]
            st.success(
                f"Recommended: {best_option['Locality']} • {int(best_option['BHK_Count'])} BHK • "
                f"{best_option['Area']} sqft • ₹{best_option['Price']:,.0f}"
            )
            st.write(f"Suggested strategy: buy in {preferred_locality} with a projected value increase and rental yield of 3-5%.")
            st.write(f"Estimated deal support: negotiate a 2-5% discount and share business profit structure with the seller and buyer team.")


def show_dashboard():
    df = get_clean_data()

    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], .main {
            background: linear-gradient(180deg, #0b1220 0%, #111827 100%) !important;
            color: #e5e7eb !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f3f4f6;
        }
        [data-testid="stSidebar"] {
            background: #111827 !important;
            border-right: 1px solid rgba(148, 163, 184, 0.2);
        }
        [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stContainer"], [data-testid="stDataFrame"] {
            background: rgba(17, 24, 39, 0.9) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.18);
        }
        .stTabs [role="tablist"] {
            background: rgba(17, 24, 39, 0.95);
            border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        }
        .stTabs [role="tab"] {
            color: #d1d5db;
            border-radius: 10px 10px 0 0;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            color: #ffffff;
            background: rgba(96, 165, 250, 0.12);
            border: 1px solid rgba(96, 165, 250, 0.24);
        }
        h1, h2, h3, h4, p, label, .stCaption {
            color: #e5e7eb !important;
        }
        .stMetric {
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12);
        }
        .stDataFrame, .stDataFrame > div {
            background: #111827 !important;
            color: #e5e7eb !important;
        }
        .stMarkdown, .stMarkdown p, .stMarkdown li {
            color: #e5e7eb !important;
        }
        .stPlotlyChart, .stECharts, .stBarChart, .stLineChart {
            background: transparent !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
        }
        .big-card {
            padding: 1.2rem;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(96,165,250,0.16), rgba(15,23,42,0.95));
            border: 1px solid rgba(96,165,250,0.25);
        }
        a {
            color: #93c5fd;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    login_register_panel()
    filtered_df = filter_dataframe(df)

    st.title("Gurugram Property Advisor")
    st.caption("Premium property guidance for buyers, investors, and families in Gurugram.")

    st.markdown(
        f"""
        <div class="big-card">
            <b>Connect with me</b><br>
            Instagram: <a href="{INSTAGRAM}" target="_blank">@youknow_akhi</a><br>
            Website: <a href="{WEBSITE}" target="_blank">{WEBSITE}</a><br>
            WhatsApp: <a href="{WHATSAPP}" target="_blank">{CONTACT_NUMBER}</a><br>
            Call: <a href="tel:{CONTACT_NUMBER}">{CONTACT_NUMBER}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(horizontal=True):
        st.metric("Total Listings", f"{filtered_df.shape[0]:,}", border=True)
        st.metric("Average Price", money(filtered_df["Price"].mean()), border=True)
        st.metric("Avg Rate / sqft", money(filtered_df["Rate per sqft"].mean()) if "Rate per sqft" in filtered_df.columns else "₹0.00", border=True)
        st.metric("Localities Covered", f"{filtered_df['Locality'].nunique():,}", border=True)

    st.markdown("---")

    st.subheader("Business offer")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("Buyer discounts and verified property deals")
    with col2:
        st.success("Smart profit-sharing investment guidance")
    with col3:
        st.warning("Custom recommendations based on your goal")

    if st.session_state.logged_in:
        st.success(f"Hi {st.session_state.current_user}, your buyer dashboard is active.")
    else:
        st.warning("Register or login to access premium buyer assistance and investment recommendations.")

    buyer_help_section(filtered_df)

    overview, insights = st.tabs(["Overview", "Locality insights"])

    with overview:
        localities = (
            filtered_df.groupby("Locality", as_index=False)["Price"]
            .mean()
            .sort_values("Price", ascending=False)
            .head(10)
        )

        bhk_summary = (
            filtered_df.groupby("BHK_Count", as_index=False)["Price"]
            .mean()
            .sort_values("Price", ascending=False)
        )

        property_type_summary = (
            filtered_df.groupby("Property Type", as_index=False).size().rename(columns={"size": "Count"}).sort_values("Count", ascending=False)
        )

        left_col, right_col = st.columns(2)
        with left_col:
            with st.container(border=True):
                st.subheader("Top localities by average price")
                st.bar_chart(localities.set_index("Locality")["Price"], height=320)

        with right_col:
            with st.container(border=True):
                st.subheader("Average price by BHK")
                st.bar_chart(bhk_summary.set_index("BHK_Count")["Price"], height=320)

        left_col, right_col = st.columns(2)
        with left_col:
            with st.container(border=True):
                st.subheader("Property type distribution")
                st.bar_chart(property_type_summary.set_index("Property Type")["Count"], height=320)

        with right_col:
            with st.container(border=True):
                st.subheader("Price vs Area")
                st.scatter_chart(filtered_df[["Area", "Price"]], x="Area", y="Price", height=320)

    with insights:
        top_locality_table = (
            filtered_df.groupby("Locality", as_index=False)[["Price", "Area"]]
            .mean()
            .sort_values("Price", ascending=False)
            .head(15)
            .round({"Price": 2, "Area": 2})
        )
        top_locality_table["Avg Price"] = top_locality_table["Price"].apply(money)
        top_locality_table["Avg Area"] = top_locality_table["Area"].apply(lambda x: f"{x:,.0f} sqft")

        with st.container(border=True):
            st.subheader("Locality comparison")
            st.dataframe(
                top_locality_table[["Locality", "Avg Price", "Avg Area"]],
                hide_index=True,
                use_container_width=True,
            )

        with st.container(border=True):
            st.subheader("Sample listings")
            st.dataframe(
                filtered_df[["Price", "Area", "Rate per sqft", "Locality", "Property Type", "BHK_Count"]]
                .sort_values("Price", ascending=False)
                .head(25),
                hide_index=True,
                use_container_width=True,
            )

    st.markdown("---")
    st.subheader("Lead capture")
    with st.form("lead_form"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        interest = st.selectbox("Buying goal", ["New home", "Investment", "Commercial property", "Rental property"])
        budget = st.number_input("Budget (₹ Cr)", min_value=10.0, max_value=500.0, value=60.0)
        send = st.form_submit_button("Book a consultation")

    if send:
        lead = {
            "name": name,
            "phone": phone,
            "interest": interest,
            "budget": float(budget),
        }
        save_lead(lead)
        st.session_state.buyer_leads.append(lead)
        st.success("Your consultation request has been saved successfully. I will contact you soon.")

    st.caption(
        "Market view refreshed from the Gurugram dataset • "
        f"{filtered_df.shape[0]:,} filtered listings • "
        f"Avg price: {money(filtered_df['Price'].mean())}"
    )


if __name__ == "__main__":
    show_dashboard()
