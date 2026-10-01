from __future__ import annotations

import html
import re
from typing import Any


PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
DANGEROUS_TAGS_REGEX = re.compile(r"<(script|iframe|object|embed|style|meta)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)


def sanitize_text(text: str | None, max_length: int = 500) -> str:
    """
    Sanitizes arbitrary text input by removing dangerous tags,
    escaping HTML entities, and trimming to a safe length.
    """
    if not text:
        return ""

    text = str(text).strip()
    # Strip dangerous executable HTML tags
    cleaned = DANGEROUS_TAGS_REGEX.sub("", text)
    # Remove all remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    # Escape entities
    safe_text = html.escape(cleaned)
    return safe_text[:max_length]


def validate_phone_number(phone: str) -> tuple[bool, str]:
    """
    Validates a 10-digit Indian phone number.
    Returns (is_valid, cleaned_phone_or_error).
    """
    cleaned = re.sub(r"\D", "", str(phone or "")).strip()
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]

    if not PHONE_REGEX.match(cleaned):
        return False, "Please enter a valid 10-digit Indian phone number (starting with 6-9)."
    return True, cleaned


def validate_email_address(email: str) -> tuple[bool, str]:
    """
    Validates email format.
    Returns (is_valid, cleaned_email_or_error).
    """
    cleaned = str(email or "").strip().lower()
    if not EMAIL_REGEX.match(cleaned):
        return False, "Please enter a valid email address."
    return True, cleaned


def sanitize_lead_payload(raw_lead: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitizes all fields of an inquiry or lead dictionary.
    """
    name = sanitize_text(raw_lead.get("name", ""), max_length=100)
    phone_valid, phone = validate_phone_number(raw_lead.get("phone", ""))
    if not phone_valid:
        phone = sanitize_text(raw_lead.get("phone", ""), max_length=15)

    email_valid, email = validate_email_address(raw_lead.get("email", ""))
    if not email_valid:
        email = sanitize_text(raw_lead.get("email", "N/A"), max_length=100)

    try:
        budget = float(raw_lead.get("budget", 0) or 0)
        budget = max(0.0, min(100_000.0, budget))  # Cap at 1,000 Cr in Lakhs
    except (ValueError, TypeError):
        budget = 0.0

    return {
        "name": name,
        "phone": phone,
        "email": email,
        "budget": budget,
        "interest": sanitize_text(raw_lead.get("interest", "Buy"), max_length=50),
        "message": sanitize_text(raw_lead.get("message", ""), max_length=1000),
        "property": sanitize_text(raw_lead.get("property", "N/A"), max_length=150),
        "service": sanitize_text(raw_lead.get("service", "General Consultation"), max_length=100),
        "timestamp": sanitize_text(raw_lead.get("timestamp", ""), max_length=50),
    }
