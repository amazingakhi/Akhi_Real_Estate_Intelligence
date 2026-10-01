"""
Akhi Real Estate Intelligence — Razorpay Payment Integration
Handles subscription checkout via Razorpay Payment Links API.
No SDK required — uses stdlib urllib / http.client.
"""
from __future__ import annotations

import base64
import json
import ssl
import urllib.request
import urllib.error
from typing import Any

try:
    from config.settings import RAZORPAY_KEY, RAZORPAY_SECRET, PLATFORM_NAME, razorpay_is_configured
except ImportError:
    import os
    RAZORPAY_KEY = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    PLATFORM_NAME = "Akhi Real Estate Intelligence"

    def razorpay_is_configured() -> bool:
        return bool(RAZORPAY_KEY and RAZORPAY_SECRET
                    and "placeholder" not in (RAZORPAY_KEY or "").lower())


# ── Subscription Plans ────────────────────────────────────────────────────────

SUBSCRIPTION_PLANS: list[dict[str, Any]] = [
    {
        "id": "free",
        "name": "Free Explorer",
        "price_inr": 0,
        "period": "Forever",
        "badge_color": "#64748b",
        "badge_bg": "#f1f5f9",
        "features": [
            "Browse property listings",
            "Basic price estimates",
            "Market overview",
            "3 shortlists",
        ],
        "cta": "Start Free",
        "highlight": False,
    },
    {
        "id": "pro",
        "name": "Pro Investor",
        "price_inr": 999,
        "period": "per month",
        "badge_color": "#0369a1",
        "badge_bg": "#dbeafe",
        "features": [
            "Everything in Free",
            "G-REPI™ Index access",
            "FairValue AVM™ valuations",
            "CapYield™ & IRR projections",
            "Unlimited shortlists",
            "Property dossier PDF export",
            "Priority email support",
        ],
        "cta": "Subscribe — ₹999/mo",
        "highlight": True,
        "razorpay_plan_name": "AREI Pro Investor Monthly",
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price_inr": 4999,
        "period": "per month",
        "badge_color": "#7c3aed",
        "badge_bg": "#ede9fe",
        "features": [
            "Everything in Pro",
            "Bulk data export (CSV/JSON)",
            "Corridor Quadrant™ deep-dive",
            "Custom micro-market reports",
            "White-label dossiers",
            "API access (coming soon)",
            "Dedicated relationship manager",
        ],
        "cta": "Contact for Enterprise",
        "highlight": False,
    },
]


def _rzp_api_call(
    endpoint: str,
    method: str = "POST",
    payload: dict | None = None,
) -> tuple[bool, dict[str, Any]]:
    """
    Makes an authenticated call to the Razorpay REST API.
    Returns (success, response_dict).
    """
    if not razorpay_is_configured():
        return False, {"error": "Razorpay not configured"}

    url = f"https://api.razorpay.com/v1/{endpoint.lstrip('/')}"
    credentials = base64.b64encode(f"{RAZORPAY_KEY}:{RAZORPAY_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

    body = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return True, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        try:
            return False, json.loads(error_body)
        except Exception:
            return False, {"error": error_body}
    except Exception as exc:
        return False, {"error": str(exc)}


def create_payment_link(
    amount_inr: int,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    plan_name: str,
    description: str = "",
    callback_url: str = "",
) -> tuple[bool, str]:
    """
    Creates a Razorpay Payment Link and returns (success, short_url | error_message).
    The link can be opened in a browser to complete payment.
    """
    payload = {
        "amount": amount_inr * 100,  # paise
        "currency": "INR",
        "accept_partial": False,
        "description": description or f"{PLATFORM_NAME} — {plan_name}",
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "contact": f"+91{customer_phone.lstrip('+').lstrip('91').lstrip('0')}"
        },
        "notify": {
            "sms": True,
            "email": True,
        },
        "reminder_enable": True,
        "notes": {
            "plan": plan_name,
            "platform": PLATFORM_NAME,
        },
    }

    if callback_url:
        payload["callback_url"] = callback_url
        payload["callback_method"] = "get"

    ok, response = _rzp_api_call("payment_links", "POST", payload)

    if ok and "short_url" in response:
        return True, response["short_url"]
    else:
        error = response.get("error", {})
        if isinstance(error, dict):
            return False, error.get("description", str(response))
        return False, str(error or response)


def get_razorpay_checkout_html(
    amount_inr: int,
    plan_name: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
) -> str:
    """
    Returns an embedded Razorpay checkout HTML snippet for use inside
    st.components.v1.html(). Works when Razorpay JS SDK is allowed.
    Falls back to payment link if SDK is blocked.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
      <style>
        body {{ margin: 0; padding: 16px; font-family: 'Segoe UI', sans-serif;
               background: transparent; display: flex; justify-content: center; }}
        .pay-btn {{
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          color: white; border: none; border-radius: 12px;
          padding: 14px 32px; font-size: 16px; font-weight: 700;
          cursor: pointer; box-shadow: 0 8px 24px rgba(14,165,233,0.35);
          transition: transform 0.2s ease;
        }}
        .pay-btn:hover {{ transform: translateY(-2px); }}
      </style>
    </head>
    <body>
      <button class="pay-btn" onclick="openCheckout()">
        💳 Pay ₹{amount_inr:,} Securely
      </button>
      <script>
        function openCheckout() {{
          var options = {{
            key: "{RAZORPAY_KEY}",
            amount: {amount_inr * 100},
            currency: "INR",
            name: "{PLATFORM_NAME}",
            description: "{plan_name}",
            prefill: {{
              name: "{customer_name}",
              email: "{customer_email}",
              contact: "91{customer_phone}"
            }},
            theme: {{ color: "#0ea5e9" }},
            handler: function(response) {{
              window.parent.postMessage({{
                type: "razorpay_success",
                payment_id: response.razorpay_payment_id
              }}, "*");
            }}
          }};
          var rzp = new Razorpay(options);
          rzp.on("payment.failed", function(resp) {{
            window.parent.postMessage({{
              type: "razorpay_failed",
              error: resp.error.description
            }}, "*");
          }});
          rzp.open();
        }}
      </script>
    </body>
    </html>
    """
