"""
Akhi Real Estate Intelligence - DPDP Act Compliance Framework
Digital Personal Data Protection Act compliance for Indian data privacy
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
import secrets
import hashlib


class DataCategory(Enum):
    """Categories of personal data as per DPDP Act"""
    BASIC = "basic"  # Name, contact details
    SENSITIVE = "sensitive"  # Financial, health, biometric
    CRITICAL = "critical"  # Genetic data, religious beliefs


class LegalBasis(Enum):
    """Legal basis for data processing under DPDP Act"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_INTEREST = "public_interest"
    LEGITIMATE_INTEREST = "legitimate_interest"


class DataPurpose(Enum):
    """Purposes for data processing"""
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    SECURITY = "security"
    LEGAL_COMPLIANCE = "legal_compliance"
    IMPROVEMENT = "improvement"


class ConsentStatus(Enum):
    """Status of user consent"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class DataSubjectRequest(Enum):
    """Types of data subject requests"""
    ACCESS = "access"
    DELETION = "deletion"
    CORRECTION = "correction"
    PORTABILITY = "portability"
    OBJECTION = "objection"


class DataRetentionPolicy(Enum):
    """Data retention policies"""
    ESSENTIAL = "essential"  # Keep only what's essential
    STANDARD = "standard"  # Standard retention period
    EXTENDED = "extended"  # Extended retention for legal requirements
    INDEFINITE = "indefinite"  # Keep indefinitely (rare)


class ConsentManager:
    """
    Manage user consent for data processing
    """
    
    def __init__(self):
        self.consent_records = {}  # In production, this would be database-backed
    
    def create_consent_request(self, user_id: str, data_categories: List[DataCategory],
                              purposes: List[DataPurpose], legal_basis: LegalBasis,
                              retention_period: int = 365) -> Dict[str, Any]:
        """
        Create a new consent request
        """
        consent_request = {
            'consent_id': self.generate_consent_id(),
            'user_id': user_id,
            'data_categories': [cat.value for cat in data_categories],
            'purposes': [purpose.value for purpose in purposes],
            'legal_basis': legal_basis.value,
            'retention_period_days': retention_period,
            'created_at': datetime.now().isoformat(),
            'status': ConsentStatus.DENIED.value,  # Default to denied until granted
            'consent_details': self.generate_consent_details(data_categories, purposes, legal_basis)
        }
        
        return consent_request
    
    def generate_consent_id(self) -> str:
        """Generate unique consent ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"CONSENT-{timestamp}-{random_str}"
    
    def generate_consent_details(self, data_categories: List[DataCategory],
                               purposes: List[DataPurpose], legal_basis: LegalBasis) -> str:
        """Generate human-readable consent details"""
        category_names = [cat.value.replace('_', ' ').title() for cat in data_categories]
        purpose_names = [purpose.value.replace('_', ' ').title() for purpose in purposes]
        
        details = f"""
        We request your consent to process the following data categories:
        {', '.join(category_names)}
        
        For the following purposes:
        {', '.join(purpose_names)}
        
        Legal basis: {legal_basis.value.replace('_', ' ').title()}
        
        You have the right to withdraw this consent at any time.
        """
        
        return details.strip()
    
    def grant_consent(self, consent_id: str, user_id: str) -> Dict[str, Any]:
        """
        Grant consent for a consent request
        """
        consent_record = {
            'consent_id': consent_id,
            'user_id': user_id,
            'status': ConsentStatus.GRANTED.value,
            'granted_at': datetime.now().isoformat(),
            'ip_address': None,  # Would be captured from request
            'user_agent': None   # Would be captured from request
        }
        
        return consent_record
    
    def withdraw_consent(self, consent_id: str, user_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Withdraw previously granted consent
        """
        withdrawal_record = {
            'consent_id': consent_id,
            'user_id': user_id,
            'status': ConsentStatus.WITHDRAWN.value,
            'withdrawn_at': datetime.now().isoformat(),
            'reason': reason,
            'data_deletion_scheduled': True,
            'data_deletion_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        return withdrawal_record
    
    def check_consent_status(self, user_id: str, data_category: DataCategory,
                           purpose: DataPurpose) -> Dict[str, Any]:
        """
        Check if consent exists for specific data category and purpose
        """
        # In production, this would query the database
        consent_status = {
            'user_id': user_id,
            'data_category': data_category.value,
            'purpose': purpose.value,
            'has_consent': True,  # Placeholder
            'consent_status': ConsentStatus.GRANTED.value,
            'granted_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=365)).isoformat()
        }
        
        return consent_status


class DataAnonymizer:
    """
    Data anonymization and pseudonymization utilities
    """
    
    def __init__(self):
        self.anonymization_salt = secrets.token_bytes(32)
    
    def anonymize_personal_data(self, data: Dict[str, Any], 
                               fields_to_anonymize: List[str] = None) -> Dict[str, Any]:
        """
        Anonymize specified fields in personal data
        """
        if fields_to_anonymize is None:
            fields_to_anonymize = ['name', 'email', 'phone', 'address', 'pan', 'aadhaar']
        
        anonymized_data = data.copy()
        
        for field in fields_to_anonymize:
            if field in anonymized_data:
                anonymized_data[field] = self.anonymize_field(anonymized_data[field], field)
        
        return anonymized_data
    
    def anonymize_field(self, value: Any, field_type: str) -> str:
        """Anonymize a specific field based on its type"""
        if value is None:
            return None
        
        value_str = str(value)
        
        # Different anonymization strategies based on field type
        if field_type in ['email']:
            return self.anonymize_email(value_str)
        elif field_type in ['phone']:
            return self.anonymize_phone(value_str)
        elif field_type in ['pan', 'aadhaar']:
            return self.anonymize_id(value_str)
        elif field_type in ['name']:
            return self.anonymize_name(value_str)
        elif field_type in ['address']:
            return self.anonymize_address(value_str)
        else:
            return self.hash_value(value_str)
    
    def anonymize_email(self, email: str) -> str:
        """Anonymize email address"""
        if '@' not in email:
            return self.hash_value(email)
        
        username, domain = email.split('@', 1)
        anonymized_username = username[:2] + '*' * (len(username) - 2)
        return f"{anonymized_username}@{domain}"
    
    def anonymize_phone(self, phone: str) -> str:
        """Anonymize phone number"""
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 4:
            return self.hash_value(phone)
        
        visible_digits = digits[:2]
        masked_digits = '*' * (len(digits) - 4)
        last_digits = digits[-2:]
        
        return f"{visible_digits}{masked_digits}{last_digits}"
    
    def anonymize_id(self, id_number: str) -> str:
        """Anonymize ID numbers (PAN, Aadhaar)"""
        if len(id_number) < 4:
            return self.hash_value(id_number)
        
        return id_number[:2] + '*' * (len(id_number) - 4) + id_number[-2:]
    
    def anonymize_name(self, name: str) -> str:
        """Anonymize names"""
        parts = name.split()
        if not parts:
            return self.hash_value(name)
        
        anonymized_parts = []
        for part in parts:
            if len(part) > 1:
                anonymized_parts.append(part[0] + '*' * (len(part) - 1))
            else:
                anonymized_parts.append(part)
        
        return ' '.join(anonymized_parts)
    
    def anonymize_address(self, address: str) -> str:
        """Anonymize addresses"""
        # Keep city and state, anonymize street details
        words = address.split()
        if len(words) <= 2:
            return self.hash_value(address)
        
        # Keep last 2 words (usually city, state)
        return ' '.join(['*' * len(word) for word in words[:-2]] + words[-2:])
    
    def hash_value(self, value: str) -> str:
        """Hash a value for irreversible anonymization"""
        salted_value = value + str(self.anonymization_salt)
        return hashlib.sha256(salted_value.encode()).hexdigest()[:16]
    
    def apply_differential_privacy(self, numeric_data: List[float], 
                                  epsilon: float = 1.0) -> List[float]:
        """
        Apply differential privacy to numeric data
        """
        import numpy as np
        
        sensitivity = 1.0  # Assume sensitivity of 1
        scale = sensitivity / epsilon
        
        noisy_data = []
        for value in numeric_data:
            noise = np.random.laplace(0, scale)
            noisy_data.append(max(0, value + noise))  # Ensure non-negative
        
        return noisy_data


class DataRetentionManager:
    """
    Manage data retention policies and automatic deletion
    """
    
    def __init__(self):
        self.retention_policies = {
            DataCategory.BASIC: DataRetentionPolicy.STANDARD,
            DataCategory.SENSITIVE: DataRetentionPolicy.ESSENTIAL,
            DataCategory.CRITICAL: DataRetentionPolicy.ESSENTIAL
        }
        
        self.retention_periods = {
            DataRetentionPolicy.ESSENTIAL: 90,      # 90 days
            DataRetentionPolicy.STANDARD: 365,     # 1 year
            DataRetentionPolicy.EXTENDED: 1825,   # 5 years
            DataRetentionPolicy.INDEFINITE: None   # No automatic deletion
        }
    
    def get_retention_period(self, data_category: DataCategory) -> int:
        """Get retention period for a data category"""
        policy = self.retention_policies.get(data_category, DataRetentionPolicy.STANDARD)
        return self.retention_periods.get(policy, 365)
    
    def schedule_data_deletion(self, user_id: str, data_categories: List[DataCategory],
                              reason: str = "user_request") -> Dict[str, Any]:
        """
        Schedule data deletion for a user
        """
        deletion_schedule = {
            'user_id': user_id,
            'scheduled_deletions': [],
            'reason': reason,
            'created_at': datetime.now().isoformat()
        }
        
        for category in data_categories:
            retention_period = self.get_retention_period(category)
            deletion_date = datetime.now() + timedelta(days=retention_period)
            
            deletion_schedule['scheduled_deletions'].append({
                'data_category': category.value,
                'retention_period_days': retention_period,
                'deletion_date': deletion_date.isoformat(),
                'status': 'scheduled'
            })
        
        return deletion_schedule
    
    def check_deletion_eligibility(self, user_id: str, data_category: DataCategory) -> bool:
        """
        Check if data is eligible for deletion
        """
        # In production, this would check the actual data timestamps
        retention_period = self.get_retention_period(data_category)
        return True  # Placeholder
    
    def execute_data_deletion(self, user_id: str, data_categories: List[DataCategory]) -> Dict[str, Any]:
        """
        Execute data deletion for specified categories
        """
        deletion_result = {
            'user_id': user_id,
            'deletion_executed_at': datetime.now().isoformat(),
            'deleted_categories': [],
            'failed_deletions': []
        }
        
        for category in data_categories:
            try:
                # In production, this would actually delete the data
                deletion_result['deleted_categories'].append({
                    'data_category': category.value,
                    'status': 'deleted',
                    'records_affected': 0  # Placeholder
                })
            except Exception as e:
                deletion_result['failed_deletions'].append({
                    'data_category': category.value,
                    'error': str(e)
                })
        
        return deletion_result


class DataSubjectRequestManager:
    """
    Manage data subject requests (access, deletion, correction, portability)
    """
    
    def __init__(self):
        self.consent_manager = ConsentManager()
        self.data_anonymizer = DataAnonymizer()
        self.retention_manager = DataRetentionManager()
    
    def create_data_access_request(self, user_id: str, request_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a data access request
        """
        request_id = self.generate_request_id(DataSubjectRequest.ACCESS)
        
        access_request = {
            'request_id': request_id,
            'user_id': user_id,
            'request_type': DataSubjectRequest.ACCESS.value,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expected_completion': (datetime.now() + timedelta(days=30)).isoformat(),  # 30 days as per DPDP
            'request_details': request_details or {}
        }
        
        return access_request
    
    def create_data_deletion_request(self, user_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Create a data deletion request (Right to be Forgotten)
        """
        request_id = self.generate_request_id(DataSubjectRequest.DELETION)
        
        deletion_request = {
            'request_id': request_id,
            'user_id': user_id,
            'request_type': DataSubjectRequest.DELETION.value,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expected_completion': (datetime.now() + timedelta(days=30)).isoformat(),
            'reason': reason,
            'data_categories': [cat.value for cat in DataCategory]  # Delete all categories
        }
        
        return deletion_request
    
    def create_data_correction_request(self, user_id: str, corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a data correction request
        """
        request_id = self.generate_request_id(DataSubjectRequest.CORRECTION)
        
        correction_request = {
            'request_id': request_id,
            'user_id': user_id,
            'request_type': DataSubjectRequest.CORRECTION.value,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expected_completion': (datetime.now() + timedelta(days=30)).isoformat(),
            'corrections': corrections
        }
        
        return correction_request
    
    def create_data_portability_request(self, user_id: str, format: str = 'json') -> Dict[str, Any]:
        """
        Create a data portability request
        """
        request_id = self.generate_request_id(DataSubjectRequest.PORTABILITY)
        
        portability_request = {
            'request_id': request_id,
            'user_id': user_id,
            'request_type': DataSubjectRequest.PORTABILITY.value,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expected_completion': (datetime.now() + timedelta(days=30)).isoformat(),
            'preferred_format': format
        }
        
        return portability_request
    
    def generate_request_id(self, request_type: DataSubjectRequest) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"DSR-{request_type.value.upper()}-{timestamp}-{random_str}"
    
    def process_data_access_request(self, request_id: str) -> Dict[str, Any]:
        """
        Process data access request and return user data
        """
        # In production, this would fetch actual user data
        user_data = {
            'personal_info': {
                'name': 'User Name',
                'email': 'user@example.com',
                'phone': '9876543210'
            },
            'activity_data': {
                'last_login': datetime.now().isoformat(),
                'total_logins': 42
            },
            'preferences': {
                'notifications': True,
                'marketing_consent': False
            }
        }
        
        return {
            'request_id': request_id,
            'status': 'completed',
            'processed_at': datetime.now().isoformat(),
            'user_data': user_data,
            'data_categories': ['personal_info', 'activity_data', 'preferences']
        }
    
    def process_data_deletion_request(self, request_id: str) -> Dict[str, Any]:
        """
        Process data deletion request
        """
        deletion_result = {
            'request_id': request_id,
            'status': 'completed',
            'processed_at': datetime.now().isoformat(),
            'deleted_categories': ['basic', 'sensitive', 'critical'],
            'data_retained': ['essential_legal_records'],
            'verification_method': 'hash_verification'
        }
        
        return deletion_result
    
    def export_user_data_portable(self, user_id: str, format: str = 'json') -> Union[str, Dict]:
        """
        Export user data in portable format
        """
        # In production, this would fetch and format actual user data
        portable_data = {
            'export_metadata': {
                'user_id': user_id,
                'export_date': datetime.now().isoformat(),
                'format': format,
                'version': '1.0'
            },
            'user_data': {
                'profile': {
                    'name': 'User Name',
                    'email': 'user@example.com',
                    'phone': '9876543210'
                },
                'preferences': {
                    'language': 'en',
                    'notifications': True
                },
                'activity_summary': {
                    'account_created': '2024-01-01',
                    'last_activity': datetime.now().isoformat()
                }
            }
        }
        
        if format == 'json':
            return json.dumps(portable_data, indent=2, default=str)
        else:
            return portable_data


class DPDPComplianceManager:
    """
    Main DPDP Act compliance management system
    """
    
    def __init__(self):
        self.consent_manager = ConsentManager()
        self.data_anonymizer = DataAnonymizer()
        self.retention_manager = DataRetentionManager()
        self.request_manager = DataSubjectRequestManager()
    
    def register_data_fiduciary(self, fiduciary_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register as data fiduciary (data controller)
        """
        registration = {
            'fiduciary_id': self.generate_fiduciary_id(),
            'organisation_name': fiduciary_details.get('organisation_name', 'Akhi Real Estate Intelligence'),
            'registration_number': fiduciary_details.get('registration_number', 'N/A'),
            'data_principal_contact': fiduciary_details.get('contact_person', 'N/A'),
            'registered_at': datetime.now().isoformat(),
            'compliance_officer': fiduciary_details.get('compliance_officer', 'N/A'),
            'data_protection_officer': fiduciary_details.get('dpo', 'N/A')
        }
        
        return registration
    
    def generate_fiduciary_id(self) -> str:
        """Generate unique fiduciary ID"""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_str = secrets.token_hex(4)
        return f"DF-{timestamp}-{random_str}"
    
    def conduct_privacy_impact_assessment(self, processing_activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct privacy impact assessment for data processing activities
        """
        assessment = {
            'assessment_id': self.generate_assessment_id(),
            'processing_activity': processing_activity.get('activity_name', 'N/A'),
            'conducted_at': datetime.now().isoformat(),
            
            'risk_assessment': {
                'data_volume': processing_activity.get('data_volume', 'medium'),
                'sensitivity_level': processing_activity.get('sensitivity', 'medium'),
                'number_of_data_principals': processing_activity.get('affected_users', 0),
                'cross_border_transfer': processing_activity.get('cross_border', False)
            },
            
            'compliance_check': {
                'has_consent': processing_activity.get('has_consent', True),
                'legal_basis': processing_activity.get('legal_basis', 'consent'),
                'data_minimization': processing_activity.get('data_minimization', True),
                'purpose_limitation': processing_activity.get('purpose_limitation', True)
            },
            
            'risk_level': self.calculate_risk_level(processing_activity),
            'mitigation_measures': self.suggest_mitigation_measures(processing_activity),
            'recommendations': self.generate_recommendations(processing_activity)
        }
        
        return assessment
    
    def generate_assessment_id(self) -> str:
        """Generate unique assessment ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = secrets.token_hex(4)
        return f"PIA-{timestamp}-{random_str}"
    
    def calculate_risk_level(self, processing_activity: Dict[str, Any]) -> str:
        """Calculate risk level based on processing activity"""
        risk_score = 0
        
        # Data volume risk
        volume = processing_activity.get('data_volume', 'medium')
        if volume == 'high':
            risk_score += 3
        elif volume == 'medium':
            risk_score += 2
        else:
            risk_score += 1
        
        # Sensitivity risk
        sensitivity = processing_activity.get('sensitivity', 'medium')
        if sensitivity == 'critical':
            risk_score += 3
        elif sensitivity == 'sensitive':
            risk_score += 2
        else:
            risk_score += 1
        
        # Cross-border transfer risk
        if processing_activity.get('cross_border', False):
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 7:
            return 'high'
        elif risk_score >= 4:
            return 'medium'
        else:
            return 'low'
    
    def suggest_mitigation_measures(self, processing_activity: Dict[str, Any]) -> List[str]:
        """Suggest mitigation measures based on risk assessment"""
        measures = []
        
        if processing_activity.get('sensitivity') == 'critical':
            measures.append('Implement enhanced encryption for critical data')
            measures.append('Require explicit consent for processing')
            measures.append('Implement strict access controls')
        
        if processing_activity.get('cross_border', False):
            measures.append('Ensure adequacy decision for cross-border transfers')
            measures.append('Implement standard contractual clauses')
        
        if processing_activity.get('data_volume') == 'high':
            measures.append('Implement data minimization techniques')
            measures.append('Consider anonymization/pseudonymization')
        
        return measures
    
    def generate_recommendations(self, processing_activity: Dict[str, Any]) -> List[str]:
        """Generate recommendations for compliance improvement"""
        recommendations = []
        
        if not processing_activity.get('has_consent', True):
            recommendations.append('Obtain explicit user consent before processing')
        
        if not processing_activity.get('data_minimization', True):
            recommendations.append('Implement data minimization principles')
        
        if not processing_activity.get('purpose_limitation', True):
            recommendations.append('Ensure data is used only for stated purposes')
        
        recommendations.append('Regularly review and update consent records')
        recommendations.append('Implement data subject request handling process')
        recommendations.append('Conduct regular privacy impact assessments')
        
        return recommendations
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate overall DPDP compliance report
        """
        report = {
            'report_type': 'DPDP_COMPLIANCE_REPORT',
            'generated_at': datetime.now().isoformat(),
            'reporting_period': {
                'from': (datetime.now() - timedelta(days=90)).isoformat(),
                'to': datetime.now().isoformat()
            },
            
            'consent_statistics': {
                'total_consent_requests': 0,
                'granted_consents': 0,
                'withdrawn_consents': 0,
                'pending_consents': 0
            },
            
            'data_subject_requests': {
                'access_requests': 0,
                'deletion_requests': 0,
                'correction_requests': 0,
                'portability_requests': 0,
                'average_response_time_hours': 0
            },
            
            'data_retention': {
                'total_data_records': 0,
                'records_scheduled_for_deletion': 0,
                'records_deleted': 0
            },
            
            'compliance_score': 85,  # Placeholder
            'compliance_level': 'high',
            'recommendations': [
                'Continue monitoring consent management',
                'Optimize data subject request response times',
                'Regular privacy impact assessments'
            ]
        }
        
        return report


# Initialize global instances
consent_manager = ConsentManager()
data_anonymizer = DataAnonymizer()
data_retention_manager = DataRetentionManager()
data_subject_request_manager = DataSubjectRequestManager()
dpdp_compliance_manager = DPDPComplianceManager()