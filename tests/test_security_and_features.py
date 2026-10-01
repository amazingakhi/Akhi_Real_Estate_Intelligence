from __future__ import annotations

import pytest

from src.security.sanitizer import (
    sanitize_text,
    validate_phone_number,
    validate_email_address,
    sanitize_lead_payload,
)
from src.security.rate_limiter import is_rate_limited, reset_rate_limit
from src.intelligence.lead_alerts import (
    score_lead,
    format_admin_whatsapp_dispatch,
    format_buyer_outreach_url,
)
from src.components.dossier_generator import generate_dossier_html
from src.intelligence.valuation_avm import calculate_fairvalue_avm
from src.intelligence.financial_engine import calculate_capyield_model, run_irr_projection


def test_input_sanitization_strips_xss():
    dirty_input = "<script>alert('hack');</script><b>Hello World</b>"
    cleaned = sanitize_text(dirty_input)
    assert "<script>" not in cleaned
    assert "alert('hack')" not in cleaned
    assert "Hello World" in cleaned


def test_phone_number_validation():
    valid, phone = validate_phone_number("9876543210")
    assert valid is True
    assert phone == "9876543210"

    valid, phone = validate_phone_number("+91 98765 43210")
    assert valid is True
    assert phone == "9876543210"

    invalid, err = validate_phone_number("12345")
    assert invalid is False

    invalid, err = validate_phone_number("abcd123456")
    assert invalid is False


def test_email_validation():
    valid, email = validate_email_address("investor@example.com")
    assert valid is True
    assert email == "investor@example.com"

    invalid, _ = validate_email_address("bad-email-format")
    assert invalid is False


def test_rate_limiter_throttles_excess_requests():
    test_id = "test_user_ip_123"
    reset_rate_limit(test_id)

    # First 3 requests must pass
    for _ in range(3):
        assert is_rate_limited(test_id, max_requests=3, window_seconds=60) is False

    # 4th request must be throttled
    assert is_rate_limited(test_id, max_requests=3, window_seconds=60) is True

    # Reset
    reset_rate_limit(test_id)
    assert is_rate_limited(test_id, max_requests=3, window_seconds=60) is False


def test_lead_scoring_and_whatsapp_dispatch():
    hot_lead = {
        "name": "Rajesh Malhotra",
        "phone": "9811223344",
        "email": "rajesh@invest.in",
        "budget": 250.0,  # 2.5 Cr
        "service": "Private Advisory",
        "property": "Sector 54",
        "message": "Looking for ready-to-move luxury unit.",
        "timestamp": "2026-09-03 10:00:00 IST",
    }

    scoring = score_lead(hot_lead)
    assert "Hot Lead" in scoring["score_label"]
    assert scoring["is_high_ticket"] is True

    wa_url = format_admin_whatsapp_dispatch("6387594514", hot_lead)
    assert "wa.me/916387594514" in wa_url
    assert "Rajesh" in wa_url

    buyer_url = format_buyer_outreach_url("9811223344", "Rajesh", "Sector 54")
    assert "wa.me/919811223344" in buyer_url


def test_dossier_html_generation():
    avm = calculate_fairvalue_avm(area_sqft=2000, bhk=3, locality="Sector 54", property_type="Apartment")
    cap = calculate_capyield_model(property_price=avm["fair_market_value"])
    irr = run_irr_projection(property_price=avm["fair_market_value"])

    html_report = generate_dossier_html(
        locality="Sector 54",
        bhk=3,
        area_sqft=2000,
        property_type="Apartment",
        avm_result=avm,
        cap_result=cap,
        irr_result=irr,
        asking_price=avm["fair_market_value"] * 1.05,
    )

    assert "AREI-VAL-2026-" in html_report
    assert "AKHI REAL ESTATE INTELLIGENCE" in html_report
    assert "Fair Market Value" in html_report
    assert "Liquidation (P15)" in html_report
    assert "5-Year DCF Cash-Flow" in html_report
    assert "window.print()" in html_report
