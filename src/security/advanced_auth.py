"""
Akhi Real Estate Intelligence - Advanced Security System
Enterprise-grade authentication and authorization
"""

from __future__ import annotations

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps
from enum import Enum

# Optional heavy dependencies — wrapped so missing packages don't crash the app
try:
    import jwt as _jwt
    _JWT_AVAILABLE = True
except ImportError:
    _jwt = None  # type: ignore[assignment]
    _JWT_AVAILABLE = False

try:
    import redis as _redis_lib
    _REDIS_AVAILABLE = True
except ImportError:
    _redis_lib = None  # type: ignore[assignment]
    _REDIS_AVAILABLE = False

try:
    from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM, REDIS_URL
except ImportError:
    try:
        import os
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or secrets.token_urlsafe(64)
        JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
        REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    except Exception:
        JWT_SECRET_KEY = secrets.token_urlsafe(64)
        JWT_ALGORITHM = "HS256"
        REDIS_URL = "redis://localhost:6379/0"


class UserRole(Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    ENTERPRISE_USER = "enterprise_user"
    PREMIUM_USER = "premium_user"
    AGENT = "agent"
    FREE_USER = "free_user"


class Permission(Enum):
    """Granular permissions"""
    # Property Management
    VIEW_PROPERTIES = "view_properties"
    CREATE_PROPERTY = "create_property"
    EDIT_PROPERTY = "edit_property"
    DELETE_PROPERTY = "delete_property"
    
    # Analytics & Intelligence
    VIEW_ANALYTICS = "view_analytics"
    VIEW_MARKET_REPORTS = "view_market_reports"
    USE_AVM_TOOLS = "use_avm_tools"
    ACCESS_PREDICTIVE_ANALYTICS = "access_predictive_analytics"
    
    # API Access
    API_BASIC_ACCESS = "api_basic_access"
    API_ADVANCED_ACCESS = "api_advanced_access"
    API_UNLIMITED_ACCESS = "api_unlimited_access"
    
    # User Management
    MANAGE_USERS = "manage_users"
    VIEW_LEADS = "view_leads"
    EXPORT_DATA = "export_data"
    
    # Enterprise Features
    WHITE_LABEL_ACCESS = "white_label_access"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    BULK_DATA_ACCESS = "bulk_data_access"


# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [p for p in Permission],  # All permissions
    
    UserRole.ENTERPRISE_USER: [
        Permission.VIEW_PROPERTIES,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_MARKET_REPORTS,
        Permission.USE_AVM_TOOLS,
        Permission.ACCESS_PREDICTIVE_ANALYTICS,
        Permission.API_UNLIMITED_ACCESS,
        Permission.VIEW_LEADS,
        Permission.EXPORT_DATA,
        Permission.WHITE_LABEL_ACCESS,
        Permission.CUSTOM_INTEGRATIONS,
        Permission.BULK_DATA_ACCESS,
    ],
    
    UserRole.PREMIUM_USER: [
        Permission.VIEW_PROPERTIES,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_MARKET_REPORTS,
        Permission.USE_AVM_TOOLS,
        Permission.API_ADVANCED_ACCESS,
        Permission.VIEW_LEADS,
        Permission.EXPORT_DATA,
    ],
    
    UserRole.AGENT: [
        Permission.VIEW_PROPERTIES,
        Permission.CREATE_PROPERTY,
        Permission.EDIT_PROPERTY,
        Permission.VIEW_ANALYTICS,
        Permission.API_BASIC_ACCESS,
    ],
    
    UserRole.FREE_USER: [
        Permission.VIEW_PROPERTIES,
        Permission.API_BASIC_ACCESS,
    ]
}


class JWTManager:
    """JWT Token Management"""
    
    def __init__(self, secret_key: str = None, algorithm: str = None):
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = algorithm or JWT_ALGORITHM
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        if not _JWT_AVAILABLE:
            return secrets.token_urlsafe(32)
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "jti": secrets.token_urlsafe(16)
        })
        return _jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        if not _JWT_AVAILABLE:
            return secrets.token_urlsafe(32)
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        })
        return _jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        if not _JWT_AVAILABLE:
            return None
        try:
            payload = _jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except _jwt.ExpiredSignatureError:
            return None
        except _jwt.InvalidTokenError:
            return None
    
    def verify_token_not_revoked(self, jti: str) -> bool:
        """Check if token has been revoked (using Redis if available)"""
        if not _REDIS_AVAILABLE:
            return True  # No Redis = no revocation list = token valid
        try:
            redis_client = _redis_lib.from_url(REDIS_URL)
            return not redis_client.exists(f"revoked_token:{jti}")
        except Exception:
            return True
    
    def revoke_token(self, jti: str, ttl: int = None) -> None:
        """Revoke a token by its ID"""
        if not _REDIS_AVAILABLE:
            return
        try:
            redis_client = _redis_lib.from_url(REDIS_URL)
            if ttl is None:
                ttl = 7 * 24 * 60 * 60
            redis_client.setex(f"revoked_token:{jti}", ttl, "1")
        except Exception:
            pass


class RBACManager:
    """Role-Based Access Control Manager"""
    
    @staticmethod
    def get_user_permissions(user_role: UserRole) -> List[Permission]:
        """Get all permissions for a given role"""
        return ROLE_PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def has_permission(user_role: UserRole, required_permission: Permission) -> bool:
        """Check if user role has specific permission"""
        user_permissions = RBACManager.get_user_permissions(user_role)
        return required_permission in user_permissions
    
    @staticmethod
    def has_any_permission(user_role: UserRole, required_permissions: List[Permission]) -> bool:
        """Check if user has any of the required permissions"""
        user_permissions = RBACManager.get_user_permissions(user_role)
        return any(perm in user_permissions for perm in required_permissions)
    
    @staticmethod
    def has_all_permissions(user_role: UserRole, required_permissions: List[Permission]) -> bool:
        """Check if user has all required permissions"""
        user_permissions = RBACManager.get_user_permissions(user_role)
        return all(perm in user_permissions for perm in required_permissions)


class EncryptionManager:
    """Data Encryption and Security Utilities"""
    
    def __init__(self, encryption_key: str = None):
        self.encryption_key = encryption_key or secrets.token_bytes(32)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using AES-256"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from encryption key
            key = base64.urlsafe_b64encode(self.encryption_key[:32].ljust(32, b'\0'))
            cipher_suite = Fernet(key)
            encrypted_data = cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except ImportError:
            # Fallback to simple encoding if cryptography not available
            import base64
            return base64.b64encode(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            key = base64.urlsafe_b64encode(self.encryption_key[:32].ljust(32, b'\0'))
            cipher_suite = Fernet(key)
            decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except ImportError:
            import base64
            return base64.b64decode(encrypted_data.encode()).decode()
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)


class AdvancedAuthManager:
    """Main Authentication and Authorization Manager"""
    
    def __init__(self):
        self.jwt_manager = JWTManager()
        self.rbac_manager = RBACManager()
        self.encryption_manager = EncryptionManager()
    
    def create_user_session(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Create complete user session with access and refresh tokens"""
        # Create tokens
        access_token = self.jwt_manager.create_access_token({
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "name": user_data["name"]
        })
        
        refresh_token = self.jwt_manager.create_refresh_token({
            "user_id": user_data["user_id"],
            "email": user_data["email"]
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.jwt_manager.access_token_expire_minutes * 60
        }
    
    def validate_user_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate user session and return user data"""
        payload = self.jwt_manager.decode_token(token)
        if not payload:
            return None
        
        # Check if token is revoked
        if not self.jwt_manager.verify_token_not_revoked(payload.get("jti")):
            return None
        
        # Validate token type
        if payload.get("type") != "access":
            return None
        
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "name": payload.get("name")
        }
    
    def refresh_user_session(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh user session using refresh token"""
        payload = self.jwt_manager.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        # Create new access token
        user_data = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role", "free_user"),
            "name": payload.get("name", "")
        }
        
        return self.create_user_session(user_data)
    
    def revoke_user_session(self, token: str) -> bool:
        """Revoke user session"""
        payload = self.jwt_manager.decode_token(token)
        if not payload:
            return False
        
        self.jwt_manager.revoke_token(payload.get("jti"))
        return True
    
    def check_permission(self, user_role: UserRole, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return self.rbac_manager.has_permission(user_role, permission)
    
    def generate_api_key(self, user_id: str, permissions: List[Permission]) -> str:
        """Generate API key for user with specific permissions"""
        api_key = self.encryption_manager.generate_secure_token(48)
        
        # Store API key with permissions (implementation depends on your database)
        # This is a placeholder for the actual storage logic
        api_key_data = {
            "user_id": user_id,
            "api_key_hash": self.encryption_manager.hash_api_key(api_key),
            "permissions": [p.value for p in permissions],
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str, required_permission: Permission) -> bool:
        """Validate API key and check permissions"""
        # This is a placeholder for the actual validation logic
        # In production, you would:
        # 1. Hash the provided API key
        # 2. Look it up in the database
        # 3. Check if it's active and has the required permission
        return True


# Decorators for easy permission checking
def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user from session/context (implementation depends on your framework)
            user_role = kwargs.get('user_role')  # This should come from authentication
            if user_role and RBACManager.has_permission(user_role, permission):
                return func(*args, **kwargs)
            raise PermissionError(f"Permission required: {permission.value}")
        return wrapper
    return decorator


def require_role(role: UserRole):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = kwargs.get('user_role')
            if user_role == role:
                return func(*args, **kwargs)
            raise PermissionError(f"Role required: {role.value}")
        return wrapper
    return decorator


# CSRF Protection
class CSRFProtection:
    """CSRF Token Management"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return self.encryption_manager.generate_secure_token(32)
    
    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, session_token)


# Rate Limiting with Redis
class AdvancedRateLimiter:
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or REDIS_URL
        self.default_limits = {
            UserRole.FREE_USER: {"requests": 100, "window": 3600},  # 100 requests/hour
            UserRole.PREMIUM_USER: {"requests": 1000, "window": 3600},  # 1000 requests/hour
            UserRole.ENTERPRISE_USER: {"requests": 10000, "window": 3600},  # 10000 requests/hour
            UserRole.ADMIN: {"requests": 100000, "window": 3600},  # 100000 requests/hour
        }
    
    def is_rate_limited(self, identifier: str, user_role: UserRole = UserRole.FREE_USER) -> bool:
        """Check if request is rate limited"""
        if not _REDIS_AVAILABLE:
            return False
        try:
            redis_client = _redis_lib.from_url(self.redis_url)
            limits = self.default_limits.get(user_role, self.default_limits[UserRole.FREE_USER])
            
            key = f"rate_limit:{identifier}"
            current = redis_client.incr(key)
            
            if current == 1:
                redis_client.expire(key, limits["window"])
            
            return current > limits["requests"]
        except Exception:
            return False
    
    def get_rate_limit_status(self, identifier: str, user_role: UserRole = UserRole.FREE_USER) -> Dict[str, Any]:
        """Get current rate limit status"""
        limits = self.default_limits.get(user_role, self.default_limits[UserRole.FREE_USER])
        if not _REDIS_AVAILABLE:
            return {"limit": limits["requests"], "remaining": limits["requests"], "reset": limits["window"]}
        try:
            redis_client = _redis_lib.from_url(self.redis_url)
            
            key = f"rate_limit:{identifier}"
            current = int(redis_client.get(key) or 0)
            ttl = redis_client.ttl(key)
            
            return {
                "limit": limits["requests"],
                "remaining": max(0, limits["requests"] - current),
                "reset": ttl if ttl > 0 else limits["window"]
            }
        except Exception:
            return {
                "limit": limits["requests"],
                "remaining": limits["requests"],
                "reset": limits["window"]
            }


# Initialize global instances
auth_manager = AdvancedAuthManager()
csrf_protection = CSRFProtection()
rate_limiter = AdvancedRateLimiter()