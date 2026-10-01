"""
Akhi Real Estate Intelligence - Enterprise Licensing System
Complete subscription management, API keys, and billing system
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum
import secrets
import hashlib
import json


class SubscriptionTier(Enum):
    """Subscription tiers for different user levels"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    INSTITUTIONAL = "institutional"


class SubscriptionStatus(Enum):
    """Subscription status states"""
    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAYMENT_FAILED = "payment_failed"
    SUSPENDED = "suspended"


class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"


class LicenseType(Enum):
    """Types of enterprise licenses"""
    STANDARD = "standard"
    WHITE_LABEL = "white_label"
    OEM = "oem"
    CUSTOM = "custom"


class SubscriptionPlan:
    """Subscription plan configuration"""
    
    def __init__(self, tier: SubscriptionTier, name: str, description: str,
                 monthly_price: Decimal, yearly_price: Decimal,
                 features: List[str], limits: Dict[str, int]):
        self.tier = tier
        self.name = name
        self.description = description
        self.monthly_price = monthly_price
        self.yearly_price = yearly_price
        self.features = features
        self.limits = limits
        
        # Calculate yearly discount
        self.yearly_discount = ((monthly_price * 12) - yearly_price) / (monthly_price * 12) * 100


class SubscriptionPlanManager:
    """Manage subscription plans"""
    
    def __init__(self):
        self.plans = self._initialize_default_plans()
    
    def _initialize_default_plans(self) -> Dict[SubscriptionTier, SubscriptionPlan]:
        """Initialize default subscription plans"""
        return {
            SubscriptionTier.FREE: SubscriptionPlan(
                tier=SubscriptionTier.FREE,
                name="Free Tier",
                description="Basic property search and limited analytics",
                monthly_price=Decimal("0"),
                yearly_price=Decimal("0"),
                features=[
                    "Basic property search",
                    "Limited market analytics",
                    "3 property shortlists",
                    "100 API calls/month",
                    "Community support",
                    "Basic AVM reports"
                ],
                limits={
                    "api_calls_per_month": 100,
                    "property_listings": 0,
                    "concurrent_users": 1,
                    "data_retention_days": 30,
                    "advanced_analytics": False,
                    "market_reports": 5
                }
            ),
            
            SubscriptionTier.PROFESSIONAL: SubscriptionPlan(
                tier=SubscriptionTier.PROFESSIONAL,
                name="Professional",
                description="Advanced analytics and unlimited property access",
                monthly_price=Decimal("2999"),
                yearly_price=Decimal("29990"),
                features=[
                    "Unlimited property search",
                    "Advanced market analytics",
                    "Unlimited shortlists",
                    "10,000 API calls/month",
                    "Priority email support",
                    "Detailed AVM reports",
                    "Price trend analysis",
                    "Market reports",
                    "Lead management"
                ],
                limits={
                    "api_calls_per_month": 10000,
                    "property_listings": 10,
                    "concurrent_users": 5,
                    "data_retention_days": 365,
                    "advanced_analytics": True,
                    "market_reports": 50
                }
            ),
            
            SubscriptionTier.ENTERPRISE: SubscriptionPlan(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise",
                description="Full-featured platform with API access",
                monthly_price=Decimal("9999"),
                yearly_price=Decimal("99990"),
                features=[
                    "Everything in Professional",
                    "Unlimited API access",
                    "White-label options",
                    "Custom integrations",
                    "Dedicated account manager",
                    "Priority phone support",
                    "Custom report templates",
                    "Bulk data export",
                    "API documentation",
                    "SLA guarantee"
                ],
                limits={
                    "api_calls_per_month": 100000,
                    "property_listings": 100,
                    "concurrent_users": 50,
                    "data_retention_days": 1825,
                    "advanced_analytics": True,
                    "market_reports": 999,
                    "white_label": True,
                    "custom_integrations": True
                }
            ),
            
            SubscriptionTier.INSTITUTIONAL: SubscriptionPlan(
                tier=SubscriptionTier.INSTITUTIONAL,
                name="Institutional",
                description="Enterprise-grade solution for large organizations",
                monthly_price=Decimal("24999"),
                yearly_price=Decimal("249990"),
                features=[
                    "Everything in Enterprise",
                    "Unlimited property listings",
                    "Multi-user collaboration",
                    "Advanced AI/ML models",
                    "Custom development",
                    "On-premise deployment option",
                    "24/7 dedicated support",
                    "Custom SLA",
                    "Training and onboarding",
                    "Account-based pricing"
                ],
                limits={
                    "api_calls_per_month": 1000000,
                    "property_listings": -1,  # Unlimited
                    "concurrent_users": -1,  # Unlimited
                    "data_retention_days": 3650,  # 10 years
                    "advanced_analytics": True,
                    "market_reports": -1,  # Unlimited
                    "white_label": True,
                    "custom_integrations": True,
                    "custom_development": True
                }
            )
        }
    
    def get_plan(self, tier: SubscriptionTier) -> SubscriptionPlan:
        """Get subscription plan by tier"""
        return self.plans.get(tier)
    
    def get_all_plans(self) -> List[SubscriptionPlan]:
        """Get all available plans"""
        return list(self.plans.values())
    
    def calculate_pricing(self, tier: SubscriptionTier, billing_cycle: BillingCycle,
                        quantity: int = 1) -> Dict[str, Any]:
        """Calculate pricing for subscription"""
        plan = self.get_plan(tier)
        
        if billing_cycle == BillingCycle.MONTHLY:
            base_price = plan.monthly_price
        elif billing_cycle == BillingCycle.YEARLY:
            base_price = plan.yearly_price
        else:  # Quarterly
            base_price = plan.monthly_price * 3
        
        total_price = base_price * quantity
        
        return {
            "tier": tier.value,
            "billing_cycle": billing_cycle.value,
            "quantity": quantity,
            "base_price": base_price,
            "total_price": total_price,
            "currency": "INR",
            "yearly_discount": plan.yearly_discount if billing_cycle == BillingCycle.YEARLY else 0
        }


class LicenseManager:
    """Manage enterprise licenses"""
    
    def __init__(self):
        self.licenses = {}  # In production, this would be database-backed
    
    def generate_license_key(self, tier: SubscriptionTier, user_id: str,
                           license_type: LicenseType = LicenseType.STANDARD,
                           expiry_months: int = 12) -> Dict[str, Any]:
        """
        Generate enterprise license key
        """
        license_key = self._generate_license_key_string()
        
        license_data = {
            'license_key': license_key,
            'license_id': self._generate_license_id(),
            'user_id': user_id,
            'tier': tier.value,
            'license_type': license_type.value,
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=expiry_months * 30)).isoformat(),
            'status': 'active',
            'features': self._get_license_features(tier, license_type),
            'restrictions': self._get_license_restrictions(tier, license_type)
        }
        
        self.licenses[license_key] = license_data
        
        return license_data
    
    def _generate_license_key_string(self) -> str:
        """Generate license key string"""
        # Format: AKHI-XXXXX-XXXXX-XXXXX-XXXXX
        parts = [
            "AKHI",
            secrets.token_hex(2).upper(),
            secrets.token_hex(2).upper(),
            secrets.token_hex(2).upper(),
            secrets.token_hex(2).upper()
        ]
        return "-".join(parts)
    
    def _generate_license_id(self) -> str:
        """Generate unique license ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"LIC-{timestamp}-{random_str}"
    
    def _get_license_features(self, tier: SubscriptionTier, 
                             license_type: LicenseType) -> List[str]:
        """Get features based on tier and license type"""
        plan_manager = SubscriptionPlanManager()
        plan = plan_manager.get_plan(tier)
        
        features = plan.features.copy()
        
        if license_type == LicenseType.WHITE_LABEL:
            features.extend([
                "Custom branding",
                "White-label dashboard",
                "Custom domain",
                "Removal of Akhi branding"
            ])
        elif license_type == LicenseType.OEM:
            features.extend([
                "OEM licensing",
                "Reseller rights",
                "Custom pricing",
                "Volume discounts"
            ])
        elif license_type == LicenseType.CUSTOM:
            features.extend([
                "Custom development",
                "Dedicated support",
                "Custom integrations",
                "SLA guarantees"
            ])
        
        return features
    
    def _get_license_restrictions(self, tier: SubscriptionTier,
                                license_type: LicenseType) -> Dict[str, Any]:
        """Get restrictions based on tier and license type"""
        plan_manager = SubscriptionPlanManager()
        plan = plan_manager.get_plan(tier)
        
        restrictions = {
            "max_users": plan.limits.get("concurrent_users", 1),
            "max_api_calls": plan.limits.get("api_calls_per_month", 100),
            "max_property_listings": plan.limits.get("property_listings", 0),
            "data_retention_days": plan.limits.get("data_retention_days", 30)
        }
        
        if license_type == LicenseType.WHITE_LABEL:
            restrictions["branding_restriction"] = False
            restrictions["custom_domain"] = True
        
        return restrictions
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """
        Validate license key and return license details
        """
        license_data = self.licenses.get(license_key)
        
        if not license_data:
            return {
                'valid': False,
                'reason': 'License key not found'
            }
        
        # Check if license is expired
        expires_at = datetime.fromisoformat(license_data['expires_at'])
        if datetime.now() > expires_at:
            return {
                'valid': False,
                'reason': 'License has expired'
            }
        
        # Check if license is active
        if license_data['status'] != 'active':
            return {
                'valid': False,
                'reason': f'License is {license_data["status"]}'
            }
        
        return {
            'valid': True,
            'license_data': license_data
        }
    
    def revoke_license(self, license_key: str, reason: str = None) -> Dict[str, Any]:
        """Revoke a license"""
        if license_key not in self.licenses:
            return {
                'success': False,
                'reason': 'License key not found'
            }
        
        self.licenses[license_key]['status'] = 'revoked'
        self.licenses[license_key]['revoked_at'] = datetime.now().isoformat()
        self.licenses[license_key]['revocation_reason'] = reason
        
        return {
            'success': True,
            'revoked_at': self.licenses[license_key]['revoked_at']
        }
    
    def renew_license(self, license_key: str, extension_months: int = 12) -> Dict[str, Any]:
        """Renew a license"""
        if license_key not in self.licenses:
            return {
                'success': False,
                'reason': 'License key not found'
            }
        
        current_expiry = datetime.fromisoformat(self.licenses[license_key]['expires_at'])
        new_expiry = current_expiry + timedelta(days=extension_months * 30)
        
        self.licenses[license_key]['expires_at'] = new_expiry.isoformat()
        self.licenses[license_key]['renewed_at'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'new_expiry': new_expiry.isoformat()
        }


class APIKeyManager:
    """Manage API keys for enterprise clients"""
    
    def __init__(self):
        self.api_keys = {}  # In production, this would be database-backed
    
    def generate_api_key(self, user_id: str, permissions: List[str],
                        rate_limit: int = None, name: str = None) -> Dict[str, Any]:
        """
        Generate API key for user
        """
        api_key = self._generate_api_key_string()
        api_key_hash = self._hash_api_key(api_key)
        
        api_key_data = {
            'api_key': api_key,
            'api_key_id': self._generate_api_key_id(),
            'api_key_hash': api_key_hash,
            'user_id': user_id,
            'name': name or f"API Key {datetime.now().strftime('%Y%m%d')}",
            'permissions': permissions,
            'rate_limit': rate_limit or 1000,  # Default 1000 requests/hour
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'usage_count': 0,
            'is_active': True
        }
        
        self.api_keys[api_key_hash] = api_key_data
        
        return api_key_data
    
    def _generate_api_key_string(self) -> str:
        """Generate API key string"""
        # Format: akhi_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        prefix = "akhi_live_"
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}{random_part}"
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _generate_api_key_id(self) -> str:
        """Generate unique API key ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"API-{timestamp}-{random_str}"
    
    def validate_api_key(self, api_key: str, required_permission: str = None) -> Dict[str, Any]:
        """
        Validate API key and check permissions
        """
        api_key_hash = self._hash_api_key(api_key)
        api_key_data = self.api_keys.get(api_key_hash)
        
        if not api_key_data:
            return {
                'valid': False,
                'reason': 'Invalid API key'
            }
        
        # Check if API key is active
        if not api_key_data['is_active']:
            return {
                'valid': False,
                'reason': 'API key is inactive'
            }
        
        # Check permissions if required
        if required_permission and required_permission not in api_key_data['permissions']:
            return {
                'valid': False,
                'reason': f'API key does not have permission: {required_permission}'
            }
        
        # Update usage statistics
        api_key_data['last_used'] = datetime.now().isoformat()
        api_key_data['usage_count'] += 1
        
        return {
            'valid': True,
            'user_id': api_key_data['user_id'],
            'permissions': api_key_data['permissions'],
            'rate_limit': api_key_data['rate_limit']
        }
    
    def revoke_api_key(self, api_key: str, reason: str = None) -> Dict[str, Any]:
        """Revoke an API key"""
        api_key_hash = self._hash_api_key(api_key)
        
        if api_key_hash not in self.api_keys:
            return {
                'success': False,
                'reason': 'API key not found'
            }
        
        self.api_keys[api_key_hash]['is_active'] = False
        self.api_keys[api_key_hash]['revoked_at'] = datetime.now().isoformat()
        self.api_keys[api_key_hash]['revocation_reason'] = reason
        
        return {
            'success': True,
            'revoked_at': self.api_keys[api_key_hash]['revoked_at']
        }
    
    def get_api_key_usage(self, api_key: str) -> Dict[str, Any]:
        """Get usage statistics for API key"""
        api_key_hash = self._hash_api_key(api_key)
        api_key_data = self.api_keys.get(api_key_hash)
        
        if not api_key_data:
            return {
                'found': False
            }
        
        return {
            'found': True,
            'usage_count': api_key_data['usage_count'],
            'last_used': api_key_data['last_used'],
            'created_at': api_key_data['created_at'],
            'is_active': api_key_data['is_active']
        }


class UsageTracker:
    """Track usage for billing and limits"""
    
    def __init__(self):
        self.usage_records = {}  # In production, this would be database-backed
    
    def record_api_usage(self, user_id: str, endpoint: str, response_time_ms: int,
                        status_code: int, api_key: str = None) -> Dict[str, Any]:
        """
        Record API usage for tracking and billing
        """
        usage_record = {
            'usage_id': self._generate_usage_id(),
            'user_id': user_id,
            'api_key': api_key,
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to user's usage records
        if user_id not in self.usage_records:
            self.usage_records[user_id] = []
        
        self.usage_records[user_id].append(usage_record)
        
        return usage_record
    
    def _generate_usage_id(self) -> str:
        """Generate unique usage ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"USAGE-{timestamp}-{random_str}"
    
    def get_user_usage(self, user_id: str, period_start: date = None,
                     period_end: date = None) -> Dict[str, Any]:
        """
        Get usage statistics for a user
        """
        if user_id not in self.usage_records:
            return {
                'user_id': user_id,
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'average_response_time_ms': 0,
                'period': {
                    'start': period_start.isoformat() if period_start else None,
                    'end': period_end.isoformat() if period_end else None
                }
            }
        
        user_records = self.usage_records[user_id]
        
        # Filter by period if specified
        if period_start or period_end:
            filtered_records = []
            for record in user_records:
                record_date = datetime.fromisoformat(record['timestamp']).date()
                if period_start and record_date < period_start:
                    continue
                if period_end and record_date > period_end:
                    continue
                filtered_records.append(record)
            user_records = filtered_records
        
        # Calculate statistics
        total_calls = len(user_records)
        successful_calls = sum(1 for r in user_records if 200 <= r['status_code'] < 300)
        failed_calls = total_calls - successful_calls
        
        if total_calls > 0:
            avg_response_time = sum(r['response_time_ms'] for r in user_records) / total_calls
        else:
            avg_response_time = 0
        
        return {
            'user_id': user_id,
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'average_response_time_ms': round(avg_response_time, 2),
            'period': {
                'start': period_start.isoformat() if period_start else None,
                'end': period_end.isoformat() if period_end else None
            }
        }
    
    def check_usage_limits(self, user_id: str, limits: Dict[str, int]) -> Dict[str, Any]:
        """
        Check if user has exceeded their usage limits
        """
        current_month = date.today().replace(day=1)
        usage_stats = self.get_user_usage(user_id, current_month, date.today())
        
        limit_status = {
            'user_id': user_id,
            'within_limits': True,
            'limits': {},
            'current_usage': {}
        }
        
        for limit_name, limit_value in limits.items():
            if limit_value == -1:  # Unlimited
                limit_status['limits'][limit_name] = 'unlimited'
                limit_status['current_usage'][limit_name] = 'unlimited'
                continue
            
            current_usage = usage_stats.get('total_calls', 0) if limit_name == 'api_calls' else 0
            
            limit_status['limits'][limit_name] = limit_value
            limit_status['current_usage'][limit_name] = current_usage
            
            if current_usage >= limit_value:
                limit_status['within_limits'] = False
                limit_status['exceeded_limits'] = limit_status.get('exceeded_limits', [])
                limit_status['exceeded_limits'].append(limit_name)
        
        return limit_status


class BillingManager:
    """Manage billing and payments"""
    
    def __init__(self):
        self.invoices = {}  # In production, this would be database-backed
        self.payments = {}
    
    def create_invoice(self, user_id: str, subscription_tier: SubscriptionTier,
                      billing_cycle: BillingCycle, quantity: int = 1) -> Dict[str, Any]:
        """
        Create invoice for subscription
        """
        plan_manager = SubscriptionPlanManager()
        pricing = plan_manager.calculate_pricing(subscription_tier, billing_cycle, quantity)
        
        invoice = {
            'invoice_id': self._generate_invoice_id(),
            'user_id': user_id,
            'subscription_tier': subscription_tier.value,
            'billing_cycle': billing_cycle.value,
            'quantity': quantity,
            
            # Pricing details
            'subtotal': pricing['total_price'],
            'cgst': pricing['total_price'] * Decimal('0.09'),  # 9% CGST
            'sgst': pricing['total_price'] * Decimal('0.09'),  # 9% SGST
            'total_amount': pricing['total_price'] * Decimal('1.18'),  # 18% GST
            
            # Invoice details
            'invoice_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=15)).isoformat(),
            'status': 'pending',
            
            # Additional details
            'currency': 'INR',
            'description': f"{subscription_tier.value.title()} subscription - {billing_cycle.value}",
            'created_at': datetime.now().isoformat()
        }
        
        self.invoices[invoice['invoice_id']] = invoice
        
        return invoice
    
    def _generate_invoice_id(self) -> str:
        """Generate unique invoice ID"""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_str = secrets.token_hex(4)
        return f"INV-{timestamp}-{random_str}"
    
    def process_payment(self, invoice_id: str, payment_method: str,
                      payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment for invoice
        """
        if invoice_id not in self.invoices:
            return {
                'success': False,
                'reason': 'Invoice not found'
            }
        
        invoice = self.invoices[invoice_id]
        
        payment = {
            'payment_id': self._generate_payment_id(),
            'invoice_id': invoice_id,
            'amount': invoice['total_amount'],
            'payment_method': payment_method,
            'payment_details': payment_details,
            'status': 'processing',
            'created_at': datetime.now().isoformat()
        }
        
        # Simulate payment processing
        # In production, this would integrate with payment gateways
        payment['status'] = 'completed'
        payment['completed_at'] = datetime.now().isoformat()
        
        # Update invoice status
        invoice['status'] = 'paid'
        invoice['paid_at'] = payment['completed_at']
        invoice['payment_id'] = payment['payment_id']
        
        self.payments[payment['payment_id']] = payment
        
        return {
            'success': True,
            'payment_id': payment['payment_id'],
            'amount': payment['amount'],
            'completed_at': payment['completed_at']
        }
    
    def _generate_payment_id(self) -> str:
        """Generate unique payment ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"PAY-{timestamp}-{random_str}"
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice details"""
        return self.invoices.get(invoice_id, {'found': False})
    
    def get_user_invoices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all invoices for a user"""
        return [inv for inv in self.invoices.values() if inv['user_id'] == user_id]


class EnterpriseLicensingSystem:
    """
    Main enterprise licensing system
    """
    
    def __init__(self):
        self.plan_manager = SubscriptionPlanManager()
        self.license_manager = LicenseManager()
        self.api_key_manager = APIKeyManager()
        self.usage_tracker = UsageTracker()
        self.billing_manager = BillingManager()
    
    def setup_enterprise_subscription(self, user_id: str, tier: SubscriptionTier,
                                     billing_cycle: BillingCycle,
                                     license_type: LicenseType = LicenseType.STANDARD) -> Dict[str, Any]:
        """
        Setup complete enterprise subscription
        """
        # Generate license
        license_data = self.license_manager.generate_license_key(
            tier, user_id, license_type
        )
        
        # Generate API key
        plan = self.plan_manager.get_plan(tier)
        permissions = self._get_default_permissions(tier)
        api_key_data = self.api_key_manager.generate_api_key(
            user_id, permissions, plan.limits.get("api_calls_per_month", 1000)
        )
        
        # Create first invoice
        invoice = self.billing_manager.create_invoice(
            user_id, tier, billing_cycle
        )
        
        return {
            'subscription_setup': 'successful',
            'license': license_data,
            'api_key': api_key_data,
            'invoice': invoice,
            'plan': {
                'name': plan.name,
                'tier': tier.value,
                'features': plan.features,
                'limits': plan.limits
            }
        }
    
    def _get_default_permissions(self, tier: SubscriptionTier) -> List[str]:
        """Get default permissions based on tier"""
        permissions_map = {
            SubscriptionTier.FREE: [
                'properties.read',
                'analytics.basic',
                'api.basic'
            ],
            SubscriptionTier.PROFESSIONAL: [
                'properties.read',
                'properties.write',
                'analytics.advanced',
                'reports.generate',
                'api.advanced'
            ],
            SubscriptionTier.ENTERPRISE: [
                'properties.read',
                'properties.write',
                'properties.delete',
                'analytics.advanced',
                'reports.generate',
                'reports.custom',
                'api.unlimited',
                'white_label.access',
                'integrations.custom'
            ],
            SubscriptionTier.INSTITUTIONAL: [
                'properties.read',
                'properties.write',
                'properties.delete',
                'analytics.advanced',
                'reports.generate',
                'reports.custom',
                'api.unlimited',
                'white_label.access',
                'integrations.custom',
                'ml.advanced',
                'support.priority'
            ]
        }
        
        return permissions_map.get(tier, permissions_map[SubscriptionTier.FREE])
    
    def upgrade_subscription(self, user_id: str, current_tier: SubscriptionTier,
                          new_tier: SubscriptionTier) -> Dict[str, Any]:
        """
        Upgrade user subscription
        """
        # Revoke old license
        # (In production, you'd find the user's current license first)
        
        # Setup new subscription
        return self.setup_enterprise_subscription(
            user_id, new_tier, BillingCycle.MONTHLY
        )
    
    def get_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete subscription status for user
        """
        # In production, this would query the database
        return {
            'user_id': user_id,
            'subscription_active': True,
            'current_tier': 'professional',
            'license_valid': True,
            'api_keys_count': 2,
            'current_usage': {
                'api_calls_this_month': 1234,
                'property_listings': 5
            },
            'limits': {
                'api_calls_per_month': 10000,
                'property_listings': 10
            },
            'next_billing_date': (date.today() + timedelta(days=30)).isoformat()
        }


# Initialize global instances
subscription_plan_manager = SubscriptionPlanManager()
license_manager = LicenseManager()
api_key_manager = APIKeyManager()
usage_tracker = UsageTracker()
billing_manager = BillingManager()
enterprise_licensing_system = EnterpriseLicensingSystem()