from __future__ import annotations

import json
import urllib.parse
from typing import Any


def score_lead(lead: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluates buyer lead quality and assigns an institutional priority score:
    - 🔥 Hot Lead: Budget >= ₹1.5 Cr or Private Advisory
    - ⚡ Warm Lead: Budget >= ₹75 Lakhs
    - 📋 Standard Lead: < ₹75 Lakhs or General Inquiry
    """
    budget = float(lead.get("budget", 0) or 0)
    service = str(lead.get("service", "")).lower()

    if budget >= 150.0 or "advisory" in service or "investor" in service:
        score = "🔥 Hot Lead (Priority Close)"
        color = "#EF4444"
        urgency = "Contact within 15 minutes"
    elif budget >= 75.0:
        score = "⚡ Warm Lead (High Value)"
        color = "#F59E0B"
        urgency = "Contact within 2 hours"
    else:
        score = "📋 Standard Inquiry"
        color = "#0284C7"
        urgency = "Contact same-day"

    return {
        "score_label": score,
        "color": color,
        "urgency": urgency,
        "is_high_ticket": budget >= 150.0,
    }


def format_admin_whatsapp_dispatch(admin_phone: str, lead: dict[str, Any]) -> str:
    """
    Generates a pre-formatted WhatsApp alert URL for the Admin.
    Tapping this link immediately opens WhatsApp with the full lead details.
    """
    cleaned_admin_phone = "".join(c for c in admin_phone if c.isdigit())
    if not cleaned_admin_phone.startswith("91") and len(cleaned_admin_phone) == 10:
        cleaned_admin_phone = f"91{cleaned_admin_phone}"

    scoring = score_lead(lead)
    budget = lead.get("budget", 0)
    budget_str = f"₹{budget:.1f} Lakhs" if budget < 100 else f"₹{budget/100:.2f} Cr"

    message = (
        f"🚨 *AREI™ INSTANT LEAD DISPATCH*\n\n"
        f"👤 *Client Name:* {lead.get('name', 'N/A')}\n"
        f"📞 *Phone:* +91-{lead.get('phone', 'N/A')}\n"
        f"📧 *Email:* {lead.get('email', 'N/A')}\n"
        f"💰 *Budget:* {budget_str}\n"
        f"🏷️ *Priority:* {scoring['score_label']}\n"
        f"⏰ *Action:* {scoring['urgency']}\n"
        f"🏘️ *Subject Property:* {lead.get('property', 'General Market')}\n"
        f"💼 *Service:* {lead.get('service', 'Consultation')}\n"
        f"📝 *Note:* {lead.get('message', 'None')}\n"
        f"📅 *Timestamp:* {lead.get('timestamp', 'Just now')}\n\n"
        f"_Sent via Akhi Real Estate Intelligence System_"
    )

    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{cleaned_admin_phone}?text={encoded}"


def format_buyer_outreach_url(buyer_phone: str, client_name: str, property_name: str) -> str:
    """
    Generates a 1-click WhatsApp outreach URL for the admin to initiate chat with the buyer.
    """
    cleaned_buyer = "".join(c for c in buyer_phone if c.isdigit())
    if not cleaned_buyer.startswith("91") and len(cleaned_buyer) == 10:
        cleaned_buyer = f"91{cleaned_buyer}"

    text = (
        f"Hello {client_name},\n\n"
        f"Thank you for reaching out to *Akhi Real Estate Intelligence (AREI™)* regarding *{property_name}*.\n\n"
        f"I have reviewed your requirement and prepared our verified micro-market intelligence and fair valuation data. "
        f"When would be a convenient time for a brief 5-minute call today?"
    )
    encoded = urllib.parse.quote(text)
    return f"https://wa.me/{cleaned_buyer}?text={encoded}"
