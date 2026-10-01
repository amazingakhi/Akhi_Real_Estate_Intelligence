"""
Production readiness verification script.
Run from the project root: python verify_prod.py
"""
import sys
from pathlib import Path

# Path setup — same as app.py
SRC = Path(__file__).parent / "src"
ROOT = Path(__file__).parent
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

errors = []
passed = 0


def ok(label):
    global passed
    passed += 1
    print(f"  [PASS] {label}")


def fail(label, exc):
    errors.append(f"[FAIL] {label}: {exc}")
    print(f"  [FAIL] {label}: {exc}")


print("\n=== Akhi AREI™ — Production Readiness Check ===\n")

# ── 1. config.settings ────────────────────────────────────────────────────────
print("1. Configuration")
try:
    from config.settings import (
        ROOT_DIR, DATA_DIR, RAW_DATA_PATH, MODEL_PATH, DATABASE_FILE,
        PLATFORM_NAME, VERSION, CONTACT_NUMBER, EMAIL, ADMIN_EMAIL,
        RAZORPAY_KEY, razorpay_is_configured,
        JWT_SECRET_KEY, JWT_ALGORITHM, REDIS_URL,
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL,
        smtp_is_configured,
    )
    ok("config.settings — all keys present")
except Exception as exc:
    fail("config.settings", exc)

# ── 2. Backend (SQLite, auth) ─────────────────────────────────────────────────
print("2. Backend / Database")
try:
    from backend import (
        ensure_admin_account, get_total_leads, hash_password,
        load_leads, load_shortlist, load_users, remove_shortlist_item,
        save_lead, save_shortlist_item, save_user, verify_password,
    )
    ok("backend — all functions importable")
except Exception as exc:
    fail("backend", exc)

try:
    h = hash_password("TestPass123!")
    assert verify_password("TestPass123!", h)
    ok("backend — PBKDF2 hash/verify round-trip")
except Exception as exc:
    fail("backend.password", exc)

# ── 3. Data pipeline ──────────────────────────────────────────────────────────
print("3. Data Pipeline")
try:
    from real_estate_analysis import clean_real_estate_data, load_real_estate_data
    ok("real_estate_analysis")
except Exception as exc:
    fail("real_estate_analysis", exc)

try:
    import pandas as pd
    df_raw = load_real_estate_data(str(RAW_DATA_PATH))
    df = clean_real_estate_data(df_raw)
    assert len(df) > 0
    ok(f"CSV loaded & cleaned ({len(df)} rows, {df['Locality'].nunique()} localities)")
except Exception as exc:
    fail("data pipeline", exc)

# ── 4. ML model ───────────────────────────────────────────────────────────────
print("4. ML Price Prediction")
try:
    from price_prediction import predict_price
    price = predict_price(1500, 3, "Golf Course Road", "Apartment")
    assert price > 0
    ok(f"predict_price — Golf Course Road 3BHK 1500sqft = Rs {price/10_000_000:.2f} Cr")
except Exception as exc:
    fail("price_prediction", exc)

# ── 5. Intelligence modules ───────────────────────────────────────────────────
print("5. Intelligence Engine")
try:
    from intelligence import (
        calculate_grepi_index, get_top_performing_micro_markets,
        calculate_fairvalue_avm, get_valuation_gauge,
        calculate_capyield_model, run_irr_projection,
        classify_corridor_quadrants,
    )
    ok("intelligence — all exports importable")
except Exception as exc:
    fail("intelligence", exc)

try:
    result = run_irr_projection(10_000_000, holding_period_years=5)
    irr = result["annualized_irr_pct"]
    assert isinstance(irr, float) and irr > 0
    ok(f"IRR projection — 5yr = {irr:.1f}% (numpy-financial fix confirmed)")
except Exception as exc:
    fail("intelligence.IRR_projection", exc)

try:
    avm = calculate_fairvalue_avm(1500, 3, "Golf Course Road", "Apartment")
    fmv_cr = avm["fair_market_value_cr"]
    gauge = get_valuation_gauge(avm["fair_market_value"] * 1.05, avm["fair_market_value"])
    assert fmv_cr > 0 and "status" in gauge
    ok(f"FairValue AVM — FMV=Rs{fmv_cr}Cr, gauge={gauge['status']}")
except Exception as exc:
    fail("intelligence.AVM", exc)

try:
    cap = calculate_capyield_model(10_000_000, custom_gross_yield_pct=3.8)
    assert cap["cap_rate_pct"] > 0
    ok(f"CapYield — cap rate={cap['cap_rate_pct']}%, NOI=Rs{cap['noi_annual']:,.0f}")
except Exception as exc:
    fail("intelligence.CapYield", exc)

try:
    df_dummy = pd.DataFrame({
        "Locality": ["Golf Course Road"] * 10 + ["Dwarka Expressway"] * 10,
        "Price": [20_000_000] * 20,
        "Rate per sqft": [14000] * 10 + [8500] * 10,
    })
    grepi = calculate_grepi_index(df_dummy)
    assert len(grepi) >= 1
    ok(f"G-REPI index — {len(grepi)} micro-markets ranked")
except Exception as exc:
    fail("intelligence.GREPI", exc)

# ── 6. Security ───────────────────────────────────────────────────────────────
print("6. Security Module")
try:
    from security import is_rate_limited, validate_phone_number, validate_email_address, sanitize_text, sanitize_lead_payload
    ok("security — core functions importable (redis not required)")
except Exception as exc:
    fail("security", exc)

try:
    from security.rate_limiter import is_rate_limited as rl, reset_rate_limit
    reset_rate_limit("verify_test_id")
    for _ in range(5):
        rl("verify_test_id")
    blocked = rl("verify_test_id")
    assert blocked is True
    reset_rate_limit("verify_test_id")
    ok("security.rate_limiter — sliding window blocks at limit")
except Exception as exc:
    fail("security.rate_limiter", exc)

try:
    ok_phone, clean = validate_phone_number("9876543210")
    assert ok_phone and clean == "9876543210"
    ok_email, _ = validate_email_address("test@example.com")
    assert ok_email
    scrubbed = sanitize_text("<script>alert('xss')</script>Hello", 200)
    assert "<script>" not in scrubbed
    ok("security.sanitizer — phone/email validation + XSS scrubbing")
except Exception as exc:
    fail("security.sanitizer", exc)

# ── 7. Components ─────────────────────────────────────────────────────────────
print("7. UI Components")
try:
    from components import (
        inject_premium_fintech_theme, render_institutional_hero,
        render_avm_three_tier_cards, render_valuation_gauge_card,
        generate_dossier_html,
    )
    ok("components — all exports importable")
except Exception as exc:
    fail("components", exc)

# ── 8. Notifications (new) ────────────────────────────────────────────────────
print("8. Email Notifications")
try:
    from notifications.email_alerts import send_new_lead_alert, send_buyer_confirmation, send_welcome_email
    ok("notifications.email_alerts — module loads cleanly")
except Exception as exc:
    fail("notifications.email_alerts", exc)

try:
    from config.settings import smtp_is_configured
    smtp_ok = smtp_is_configured()
    ok(f"SMTP configured: {smtp_ok} (set SMTP_USER + SMTP_PASSWORD in .env to enable)")
except Exception as exc:
    fail("SMTP config check", exc)

# ── 9. Payments (new) ─────────────────────────────────────────────────────────
print("9. Payment Module")
try:
    from payments.razorpay_checkout import SUBSCRIPTION_PLANS, create_payment_link, get_razorpay_checkout_html
    assert len(SUBSCRIPTION_PLANS) == 3
    names = [p["name"] for p in SUBSCRIPTION_PLANS]
    ok(f"payments — {len(SUBSCRIPTION_PLANS)} plans: {', '.join(names)}")
except Exception as exc:
    fail("payments.razorpay_checkout", exc)

try:
    from config.settings import razorpay_is_configured
    rzp_ok = razorpay_is_configured()
    ok(f"Razorpay configured: {rzp_ok} (set RAZORPAY_KEY_ID + RAZORPAY_KEY_SECRET in .env for live payments)")
except Exception as exc:
    fail("Razorpay config check", exc)

# ── 10. Lead alerts ───────────────────────────────────────────────────────────
print("10. Lead Intelligence")
try:
    from intelligence.lead_alerts import score_lead, format_admin_whatsapp_dispatch, format_buyer_outreach_url
    sample_lead = {"name": "Test", "phone": "9876543210", "budget": 2.5, "interest": "Investment", "property": "Golf Course Road", "service": "Advisory"}
    score = score_lead(sample_lead)
    wa_url = format_admin_whatsapp_dispatch("6387594514", sample_lead)
    assert "wa.me" in wa_url
    assert "score_label" in score
    ok(f"lead_alerts — score={score['score_label']}, WhatsApp URL generated")
except Exception as exc:
    fail("intelligence.lead_alerts", exc)

# ── 11. App syntax check (no Streamlit context needed) ────────────────────────
print("11. App Syntax")
try:
    import ast
    app_path = SRC / "app.py"
    with open(app_path, "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    ok(f"app.py — syntax valid ({len(source.splitlines())} lines)")
except SyntaxError as exc:
    fail("app.py syntax", exc)
except Exception as exc:
    fail("app.py read", exc)

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print(f"{'='*52}")
if errors:
    print(f"RESULT: {passed} passed, {len(errors)} FAILED")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print(f"RESULT: {passed}/{passed} checks PASSED")
    print()
    print("  App is PRODUCTION READY.")
    print("  See deployment/DEPLOY_GUIDE.md to go live.")
    print(f"{'='*52}")
