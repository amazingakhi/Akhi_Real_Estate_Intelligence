from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "gurugram_real_estate.csv"
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "property_price_model.joblib"
DATABASE_FILE = DATA_DIR / "akhi_properties.db"

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

PLATFORM_NAME = os.getenv("APP_NAME", "Akhi Real Estate Intelligence")
PLATFORM_TAGLINE = os.getenv(
    "APP_TAGLINE", "Institutional Property Data & Automated Valuation Suite"
)
VERSION = os.getenv("APP_VERSION", "2.1.0")

CONTACT_NUMBER = os.getenv("CONTACT_NUMBER", "6387594514")
EMAIL = os.getenv("CONTACT_EMAIL", "iamakv01@gmail.com")
INSTAGRAM = os.getenv("INSTAGRAM_URL", "https://instagram.com/youknow_akhi")
WHATSAPP = f"https://wa.me/{os.getenv('WHATSAPP_NUMBER', '916387594514')}"
WEBSITE = os.getenv("OFFICIAL_WEBSITE", "https://akhiproperties.com")

ANNUAL_RENTAL_YIELD_DEFAULT = 0.038
ANNUAL_CAPITAL_GROWTH_DEFAULT = 0.085
MAINTENANCE_RATIO_DEFAULT = 0.008
PROPERTY_TAX_RATIO_DEFAULT = 0.002
CAPITAL_GAINS_TAX_RATE = 0.125

ADMIN_EMAIL = os.getenv("AKHI_ADMIN_EMAIL", "iamakv01@gmail.com")
ADMIN_PASSWORD = os.getenv("AKHI_ADMIN_PASSWORD", "")

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

MIN_AREA_SQFT = 80
MAX_AREA_SQFT = 25_000
MIN_PRICE_INR = 300_000
MAX_PRICE_INR = 800_000_000
MIN_RATE_PER_SQFT = 2_000
MAX_RATE_PER_SQFT = 120_000


def razorpay_is_configured() -> bool:
    key = (RAZORPAY_KEY or "").strip()
    if not key:
        return False
    lowered = key.lower()
    return "your_key" not in lowered and "placeholder" not in lowered


# ── JWT & Session Security ───────────────────────────────────────────────────
import secrets as _secrets

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or _secrets.token_urlsafe(64)
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── Email / SMTP (for lead alert notifications) ───────────────────────────────
SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", PLATFORM_NAME)
NOTIFY_EMAIL: str = os.getenv("NOTIFY_EMAIL", ADMIN_EMAIL)


def smtp_is_configured() -> bool:
    """Returns True when SMTP credentials are present and non-placeholder."""
    return bool(SMTP_USER and SMTP_PASSWORD and "placeholder" not in SMTP_PASSWORD.lower())
