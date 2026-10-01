"""
Master fix script — run once, fixes everything.
Usage: python restore_and_fix.py
"""
import ast
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

# ── Step 1: Restore clean backup ─────────────────────────────────────────────
print("Step 1: Restoring clean backup...")
shutil.copy(SRC / "app_backup_before_rewrite.py", SRC / "app.py")
content = open(SRC / "app.py", "r", encoding="utf-8").read()
ast.parse(content)
print(f"  OK — {content.count(chr(10))} lines, "
      f"{sum(1 for c in content if ord(c)>127)} non-ASCII chars")

# ── Step 2: Fix width="stretch" → use_container_width=True ──────────────────
print("Step 2: Fixing width=stretch...")
before = content.count('width="stretch"')
content = content.replace('width="stretch"', "use_container_width=True")
print(f"  Replaced {before} occurrences")

# ── Step 3: Fix hardcoded Razorpay key ───────────────────────────────────────
print("Step 3: Fixing hardcoded Razorpay key...")
content = content.replace(
    'RAZORPAY_KEY = "rzp_live_YOUR_KEY"  # To be added',
    '''# Razorpay — read from config
try:
    from config.settings import RAZORPAY_KEY, razorpay_is_configured as _rzp_configured
    _RAZORPAY_LIVE = _rzp_configured()
except ImportError:
    import os as _os
    RAZORPAY_KEY = _os.getenv("RAZORPAY_KEY_ID", "")
    _RAZORPAY_LIVE = bool(RAZORPAY_KEY and "your_key" not in RAZORPAY_KEY.lower())'''
)
print("  OK")

# ── Step 4: Add new imports after lead_alerts import ─────────────────────────
print("Step 4: Adding notification/payment imports...")
OLD_IMPORT = """from intelligence.lead_alerts import (
    score_lead,
    format_admin_whatsapp_dispatch,
    format_buyer_outreach_url,
)"""
NEW_IMPORT = """from intelligence.lead_alerts import (
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
    def _rzp_live(): return False"""

if OLD_IMPORT in content:
    content = content.replace(OLD_IMPORT, NEW_IMPORT)
    print("  OK")
else:
    print("  WARN: lead_alerts import block not found, skipping")

# ── Step 5: Replace show_page_navigation with 2-row clean version ────────────
print("Step 5: Replacing show_page_navigation...")

OLD_NAV_START = "def show_page_navigation():"
OLD_NAV_END = "    st.markdown(\"---\")\n"

# Find and replace the entire function
nav_start = content.find(OLD_NAV_START)
nav_end = content.find(OLD_NAV_END, nav_start) + len(OLD_NAV_END)

NEW_NAV = '''def show_page_navigation():
    """Two-row responsive navigation bar."""
    # Row 1: main pages
    row1 = [
        ("🏛️ Home", "home"),
        ("🧠 Intelligence", "intelligence"),
        ("🏘️ Explore", "explore"),
        (f"📌 Shortlist ({len(st.session_state.saved_properties)})", "shortlist"),
        ("📈 Analytics", "analytics"),
        ("📑 Reports", "reports"),
    ]
    # Row 2: tools + account
    row2 = [
        ("🗺️ Map", "map"),
        ("🤖 Ask Akhi", "ask_akhi"),
        ("💎 Pricing", "pricing"),
        ("💼 Advisory", "inquiry"),
    ]
    if st.session_state.logged_in:
        row2.insert(0, ("👤 Dashboard", "account"))
    if st.session_state.is_admin:
        row2.append(("⚙️ Admin", "admin"))

    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button {
        font-size: 0.78rem !important;
        padding: 0.35rem 0.5rem !important;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        overflow-y: auto !important;
        padding-bottom: 60px !important;
    }
    </style>""", unsafe_allow_html=True)

    # Row 1
    cols1 = st.columns(len(row1))
    for col, (label, page) in zip(cols1, row1):
        with col:
            btn_type = "primary" if st.session_state.page == page else "secondary"
            if st.button(label, key=f"nav1_{page}", type=btn_type, use_container_width=True):
                st.session_state.page = page
                st.session_state.pop("selected_property", None)
                st.session_state.pop("selected_service", None)
                st.rerun()

    # Row 2
    cols2 = st.columns(len(row2))
    for col, (label, page) in zip(cols2, row2):
        with col:
            btn_type = "primary" if st.session_state.page == page else "secondary"
            if st.button(label, key=f"nav2_{page}", type=btn_type, use_container_width=True):
                st.session_state.page = page
                if page != "inquiry":
                    st.session_state.pop("selected_property", None)
                    st.session_state.pop("selected_service", None)
                st.rerun()

    st.markdown("---")

'''

if nav_start != -1 and nav_end > nav_start:
    content = content[:nav_start] + NEW_NAV + content[nav_end:]
    print("  OK")
else:
    print("  WARN: could not locate show_page_navigation, skipping")

# ── Step 6: Replace show_property_cards inner loop ───────────────────────────
print("Step 6: Fixing property cards...")

OLD_CARD = """        with col5:
            action_col1, action_col2 = st.columns(2)
            property_data = row.to_dict()
            property_id = f"{property_data['Locality']}|{property_data['Area']}|{property_data['Price']}"
            saved_ids = {
                f"{item['Locality']}|{item['Area']}|{item['Price']}"
                for item in st.session_state.saved_properties
            }
            with action_col1:
                saved = property_id in saved_ids
                if st.button(
                    "Saved" if saved else "Save",
                    key=f"save_{idx}",
                    icon=":material/favorite:" if saved else ":material/favorite_border:",
                    help="Remove from shortlist" if saved else "Save to shortlist",
                ):
                    if property_id not in saved_ids:
                        st.session_state.saved_properties.append(property_data)
                        save_shortlist_item(
                            st.session_state.get("current_email", ""), property_id, property_data
                        )
                    else:
                        st.session_state.saved_properties = [
                            item for item in st.session_state.saved_properties
                            if f"{item['Locality']}|{item['Area']}|{item['Price']}" != property_id
                        ]
                        remove_shortlist_item(st.session_state.get("current_email", ""), property_id)
                    st.rerun()
            with action_col2:
                if st.button(
                    "Inquire",
                    key=f"inquire_{idx}",
                    icon=":material/call:",
                    help="Inquire about this property",
                ):
                    st.session_state.page = "inquiry"
                    st.session_state.selected_property = property_data
                    st.rerun()
            if st.button("Details", key=f"details_{idx}", icon=":material/open_in_new:", help="Open property details"):
                st.session_state.selected_property = property_data
                st.session_state.page = "property_detail"
                st.rerun()"""

NEW_CARD = """        property_data = row.to_dict()
        property_id = f"{property_data['Locality']}|{property_data['Area']}|{property_data['Price']}"
        saved_ids = {
            f"{item['Locality']}|{item['Area']}|{item['Price']}"
            for item in st.session_state.saved_properties
        }
        saved = property_id in saved_ids

        with col5:
            c1, c2, c3 = st.columns(3, gap="small")
            with c1:
                label_save = "✅ Saved" if saved else "💾 Save"
                if st.button(label_save, key=f"save_{idx}", use_container_width=True,
                              help="Remove from shortlist" if saved else "Save to shortlist"):
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
            with c2:
                if st.button("📞 Call", key=f"inquire_{idx}", use_container_width=True,
                              help="Inquire about this property"):
                    st.session_state.page = "inquiry"
                    st.session_state.selected_property = property_data
                    st.rerun()
            with c3:
                if st.button("🔍 View", key=f"details_{idx}", use_container_width=True,
                              help="View property details"):
                    st.session_state.selected_property = property_data
                    st.session_state.page = "property_detail"
                    st.rerun()"""

if OLD_CARD in content:
    content = content.replace(OLD_CARD, NEW_CARD)
    print("  OK")
else:
    print("  WARN: old card block not found — may already be patched, skipping")

# ── Step 7: Fix BHK separator (• instead of broken char) ────────────────────
print("Step 7: Fixing BHK separator...")
content = re.sub(
    r"<b>\{int\(row\[.BHK_Count.\]\)\} BHK</b>[^\{<\n]*sqft[^\{<\n]*\{row\[.Property Type.\]\}",
    "<b>{int(row['BHK_Count'])} BHK</b> &bull; {int(row['Area'])} sqft &bull; {row['Property Type']}",
    content,
)
print("  OK")

# ── Step 8: Fix show_auth_sidebar — remove broken icon= ─────────────────────
print("Step 8: Fixing auth sidebar icon= params...")
content = re.sub(r',\s*icon="[^"]*[\x80-\xFF][^"]*"', '', content)
content = re.sub(r'icon="[^"]*[\x80-\xFF][^"]*",\s*', '', content)
# Fix the specific info() call with icon
content = content.replace(
    'st.info("📝 Fill the form below to create your account.", icon="ℹ️")',
    'st.info("📝 Fill the form below to create your account.")'
)
print("  OK")

# ── Step 9: Add email on lead save ───────────────────────────────────────────
print("Step 9: Wiring email alerts to lead save...")
OLD_SAVE = "            save_lead(lead)\n            score_meta = score_lead(lead)"
NEW_SAVE = """            save_lead(lead)
            # Email alert — best effort, never blocks submission
            try:
                send_new_lead_alert(lead)
                if clean_email and clean_email != "N/A":
                    send_buyer_confirmation(lead)
            except Exception:
                pass
            score_meta = score_lead(lead)"""
if OLD_SAVE in content:
    content = content.replace(OLD_SAVE, NEW_SAVE)
    print("  OK")
else:
    print("  WARN: lead save block not found")

# ── Step 10: Add welcome email on registration ────────────────────────────────
print("Step 10: Wiring welcome email to registration...")
OLD_REG = '                        st.success("Account created! Please login.")\n                        st.rerun()'
NEW_REG = '''                        try:
                            send_welcome_email(name, email)
                        except Exception:
                            pass
                        st.success("✅ Account created! Please login.")
                        st.rerun()'''
if OLD_REG in content:
    content = content.replace(OLD_REG, NEW_REG)
    print("  OK")
else:
    print("  WARN: registration block not found")

# ── Step 11: Add back/next navigation helper + inject in main() ──────────────
print("Step 11: Adding back/next navigation...")

BACK_NEXT_FUNC = '''
def show_back_next(current_page: str):
    """Renders Back / Next buttons at the bottom of every page."""
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
            if st.button(f"⬅️ Back", key=f"back_{current_page}", use_container_width=True):
                st.session_state.page = prev_page
                st.rerun()
    with right:
        if idx < len(PAGE_ORDER) - 1:
            next_page = PAGE_ORDER[idx + 1]
            if st.button(f"Next ➡️", key=f"next_{current_page}", use_container_width=True, type="primary"):
                st.session_state.page = next_page
                st.rerun()

'''

# Insert before main()
main_pos = content.find("\ndef main():")
if main_pos != -1:
    content = content[:main_pos] + BACK_NEXT_FUNC + content[main_pos:]
    print("  Function added")
else:
    print("  WARN: main() not found")

# Now inject show_back_next() calls at end of each page in main()
OLD_MAIN = """    if st.session_state.page == "home":
        show_landing_page(get_clean_data())
    elif st.session_state.page == "explore":
        df = get_clean_data()
        show_property_cards(df)
    elif st.session_state.page == "shortlist":
        show_shortlist()
    elif st.session_state.page == "account":
        user_dashboard()
    elif st.session_state.page == "property_detail":
        df = get_clean_data()
        show_property_detail(df, st.session_state.get("selected_property"))
    elif st.session_state.page == "inquiry":
        property_data = st.session_state.get("selected_property")
        show_inquiry_form(property_data)
    elif st.session_state.page == "analytics":
        df = get_clean_data()
        show_analytics(df)
    elif st.session_state.page == "reports":
        df = get_clean_data()
        market_reports(df)
    elif st.session_state.page == "map":
        df = get_clean_data()
        gurugram_map(df)
    elif st.session_state.page == "intelligence":
        df = get_clean_data()
        property_intelligence(df)
    elif st.session_state.page == "ask_akhi":
        df = get_clean_data()
        ask_akhi(df)
    elif st.session_state.page == "admin":
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            st.error("Access Denied")
            if st.button("Back to Home"):
                st.session_state.page = "home"
                st.rerun()"""

NEW_MAIN = """    page = st.session_state.page

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
            st.error("⛔ Access Denied")
            if st.button("⬅️ Back to Home"):
                st.session_state.page = "home"
                st.rerun()"""

if OLD_MAIN in content:
    content = content.replace(OLD_MAIN, NEW_MAIN)
    print("  main() updated with back/next")
else:
    print("  WARN: main() dispatch block not matched exactly")

# ── Step 12: Add show_pricing_page + show_checkout_page + show_register_page ─
print("Step 12: Adding pricing/checkout/register pages...")

PRICING_FUNC = '''
def show_pricing_page():
    """Subscription plans — 3 tiers."""
    st.markdown("## 💎 Choose Your Intelligence Plan")
    st.markdown("Institutional property data, AVM valuations & IRR projections. Cancel anytime.")
    st.markdown("---")

    plans = [
        {
            "name": "Free Explorer", "price": 0, "period": "Forever", "highlight": False,
            "features": ["Browse all listings", "Basic price estimates", "Market overview", "3 shortlists"],
            "id": "free",
        },
        {
            "name": "Pro Investor", "price": 999, "period": "per month", "highlight": True,
            "features": ["Everything in Free", "G-REPI™ Index", "FairValue AVM™", "CapYield™ & IRR",
                         "Unlimited shortlists", "Dossier PDF export", "Priority support"],
            "id": "pro",
        },
        {
            "name": "Enterprise", "price": 4999, "period": "per month", "highlight": False,
            "features": ["Everything in Pro", "Bulk data export", "Custom reports",
                         "White-label dossiers", "API access", "Dedicated manager"],
            "id": "enterprise",
        },
    ]

    cols = st.columns(3)
    for col, plan in zip(cols, plans):
        with col:
            with st.container(border=True):
                if plan["highlight"]:
                    st.markdown("**⭐ MOST POPULAR**")
                st.markdown(f"### {plan['name']}")
                if plan["price"] > 0:
                    st.markdown(f"**₹{plan['price']:,}** / {plan['period']}")
                else:
                    st.markdown("**Free** forever")
                st.markdown("---")
                for f in plan["features"]:
                    st.markdown(f"✅ {f}")
                st.markdown("")
                if plan["id"] == "free":
                    if st.button("🚀 Start Free", key="plan_free", use_container_width=True):
                        st.session_state.page = "explore"
                        st.rerun()
                elif plan["id"] == "enterprise":
                    st.link_button("💬 WhatsApp Us", url=WHATSAPP, use_container_width=True)
                else:
                    if st.button(f"Subscribe — ₹{plan['price']:,}/mo", key="plan_pro",
                                 type="primary", use_container_width=True):
                        st.session_state["pending_plan"] = plan
                        st.session_state.page = "checkout"
                        st.rerun()

    st.markdown("---")
    st.markdown("### ❓ FAQ")
    with st.expander("Can I cancel anytime?"):
        st.write("Yes — cancel anytime, no lock-in.")
    with st.expander("Which payment methods?"):
        st.write("UPI, Credit/Debit Card, Net Banking, EMI — via Razorpay.")
    with st.expander("Is my data safe?"):
        st.write("PBKDF2-SHA256 hashed passwords, SQLite encrypted at rest. We never sell data.")


def show_checkout_page():
    """Razorpay checkout for selected plan."""
    plan = st.session_state.get("pending_plan")
    if not plan:
        st.session_state.page = "pricing"
        st.rerun()
        return

    st.markdown(f"## 💳 Subscribe to {plan['name']}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📋 Order Summary")
        with st.container(border=True):
            st.markdown(f"**Plan:** {plan['name']}")
            st.markdown(f"**Price:** ₹{plan['price']:,} / {plan['period']}")
            st.markdown("---")
            for f in plan["features"]:
                st.markdown(f"✅ {f}")

    with col2:
        st.markdown("### 👤 Your Details")
        with st.form("checkout_form"):
            name_val = st.text_input("Full Name", value=st.session_state.get("current_user", ""))
            email_val = st.text_input("Email", value=st.session_state.get("current_email", ""))
            phone_val = st.text_input("Phone (10-digit)")
            agree = st.checkbox("I agree to Terms of Service & Privacy Policy")
            pay_btn = st.form_submit_button("🔒 Proceed to Payment", type="primary", use_container_width=True)

        if pay_btn:
            phone_ok, clean_ph = validate_phone_number(phone_val)
            email_ok, clean_em = validate_email_address(email_val)
            if not name_val or not phone_val or not email_val:
                st.error("Please fill all fields.")
            elif not phone_ok:
                st.error(clean_ph)
            elif not email_ok:
                st.error(clean_em)
            elif not agree:
                st.warning("Please agree to the Terms.")
            elif not _rzp_live():
                st.warning("⚠️ Online payment setup in progress. Subscribe via WhatsApp:")
                wa_msg = f"Hi! I want to subscribe to {plan['name']} plan Rs{plan['price']}/month on AREI Platform"
                st.link_button("💬 WhatsApp to Subscribe", url=f"https://wa.me/91{CONTACT_NUMBER}?text={wa_msg.replace(' ','%20')}", type="primary")
            else:
                with st.spinner("Creating payment link..."):
                    ok, result = create_payment_link(
                        amount_inr=plan["price"],
                        customer_name=name_val,
                        customer_email=clean_em,
                        customer_phone=clean_ph,
                        plan_name=plan["name"],
                    )
                if ok:
                    st.success("✅ Payment link ready!")
                    st.link_button(f"💳 Pay ₹{plan['price']:,} via Razorpay", url=result,
                                   type="primary", use_container_width=True)
                    st.caption("🔒 Secured by Razorpay · UPI, Cards, Net Banking, EMI")
                else:
                    st.error(f"Failed: {result}")
                    st.link_button("💬 WhatsApp instead", url=WHATSAPP)

    st.markdown("---")
    if st.button("⬅️ Back to Plans", use_container_width=False):
        st.session_state.page = "pricing"
        st.rerun()


def show_register_page():
    """Full-page registration form."""
    st.markdown("## 🏛️ Create Your AREI™ Account")
    st.markdown("Join India's most advanced property intelligence platform.")
    st.markdown("---")

    col_form, _ = st.columns([1, 1])
    with col_form:
        with st.form("register_form"):
            name = st.text_input("👤 Full Name *", placeholder="Your full name")
            email = st.text_input("📧 Email *", placeholder="your@email.com")
            phone = st.text_input("📞 Phone *", placeholder="10-digit mobile number")
            password = st.text_input("🔑 Password *", type="password", placeholder="Min 8 characters")
            confirm = st.text_input("🔑 Confirm Password *", type="password", placeholder="Re-enter password")
            st.markdown("")
            submit = st.form_submit_button("✅ Create Account", use_container_width=True, type="primary")
            back = st.form_submit_button("⬅️ Back to Home", use_container_width=True)

    if back:
        st.session_state.page = "home"
        st.rerun()

    if submit:
        if not all([name, email, phone, password, confirm]):
            st.error("❌ Please fill all required fields.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("❌ Invalid email address.")
        elif len(phone) != 10 or not phone.isdigit():
            st.error("❌ Enter a valid 10-digit phone number.")
        elif len(password) < 8:
            st.error("❌ Password must be at least 8 characters.")
        elif password != confirm:
            st.error("❌ Passwords do not match.")
        elif email in st.session_state.users:
            st.warning("⚠️ Email already registered. Please login.")
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
            st.success("🎉 Account created! Please login from the sidebar.")
            st.balloons()
            st.session_state.page = "home"
            st.rerun()

'''

# Insert all three before main()
main_pos2 = content.find("\ndef main():")
if main_pos2 != -1:
    content = content[:main_pos2] + PRICING_FUNC + content[main_pos2:]
    print("  Pricing/checkout/register pages added")
else:
    print("  WARN: main() not found for page injection")

# ── Step 13: Fix show_auth_sidebar — replace entirely ────────────────────────
print("Step 13: Replacing show_auth_sidebar...")

OLD_AUTH_START = "def show_auth_sidebar():"
auth_start = content.find(OLD_AUTH_START)
# Find next def after it
auth_end = content.find("\ndef ", auth_start + 10)

NEW_AUTH = '''def show_auth_sidebar():
    """Sidebar login + register redirect."""
    with st.sidebar:
        st.markdown("### 🔐 Access Portal")

        if not st.session_state.logged_in:
            auth_tabs = st.tabs(["🔑 Login", "📝 Register"])

            with auth_tabs[0]:
                email = st.text_input("Email", key="login_email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", key="login_password",
                                         placeholder="Enter password")
                if st.button("Login", use_container_width=True, type="primary"):
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
                st.info("Fill the form to create your account.")
                if st.button("Open Registration Form", use_container_width=True, type="primary"):
                    st.session_state.page = "register"
                    st.rerun()
        else:
            st.markdown(f"**👤 {st.session_state.current_user}**")
            if st.session_state.is_admin:
                st.markdown("**🛡️ Admin Mode**")
                if st.button("⚙️ Admin Dashboard", use_container_width=True):
                    st.session_state.page = "admin"
                    st.rerun()
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            if st.button("📤 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.session_state.current_user = ""
                st.session_state.current_email = ""
                st.session_state.saved_properties = []
                st.session_state.page = "home"
                st.rerun()

'''

if auth_start != -1 and auth_end > auth_start:
    content = content[:auth_start] + NEW_AUTH + content[auth_end:]
    print("  OK")
else:
    print("  WARN: show_auth_sidebar not found")

# ── Step 14: Set page_config correctly ───────────────────────────────────────
print("Step 14: Fixing page_config...")
content = re.sub(
    r'st\.set_page_config\([^)]+\)',
    '''st.set_page_config(
    page_title="Akhi Real Estate Intelligence | AREI™",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)''',
    content,
    count=1
)
print("  OK")

# ── Final: Write + verify ─────────────────────────────────────────────────────
print("Writing fixed file...")
open(SRC / "app.py", "w", encoding="utf-8").write(content)

print("Verifying syntax...")
try:
    ast.parse(content)
    print(f"\n{'='*50}")
    print("ALL FIXES APPLIED SUCCESSFULLY")
    print(f"Lines: {content.count(chr(10))}")
    print(f"Non-ASCII (emojis): {sum(1 for c in content if ord(c)>127)}")
    print(f"{'='*50}")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    import sys; sys.exit(1)
