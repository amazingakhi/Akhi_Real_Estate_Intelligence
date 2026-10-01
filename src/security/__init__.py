"""
Akhi Real Estate Intelligence - Security Module
Advanced authentication, authorization, and data protection.

Heavy optional dependencies (jwt, redis) are wrapped with try/except inside
their respective modules so a missing package never crashes the Streamlit app.
"""

# --- Core security functions always available ---
from .sanitizer import (
    sanitize_text,
    validate_phone_number,
    validate_email_address,
    sanitize_lead_payload,
)

from .rate_limiter import (
    is_rate_limited,
    reset_rate_limit,
)

# --- Advanced auth (JWT / RBAC / Redis) — optional, import defensively ---
try:
    from .advanced_auth import (
        UserRole,
        Permission,
        JWTManager,
        RBACManager,
        EncryptionManager,
        AdvancedAuthManager,
        CSRFProtection,
        AdvancedRateLimiter,
        require_permission,
        require_role,
    )
    _ADVANCED_AUTH_AVAILABLE = True
except Exception:  # pragma: no cover
    _ADVANCED_AUTH_AVAILABLE = False

__all__ = [
    # Always available
    "sanitize_text",
    "validate_phone_number",
    "validate_email_address",
    "sanitize_lead_payload",
    "is_rate_limited",
    "reset_rate_limit",
    # Advanced auth (available when PyJWT is installed)
    "UserRole",
    "Permission",
    "JWTManager",
    "RBACManager",
    "EncryptionManager",
    "AdvancedAuthManager",
    "CSRFProtection",
    "AdvancedRateLimiter",
    "require_permission",
    "require_role",
]
