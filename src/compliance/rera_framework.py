"""
Akhi Real Estate Intelligence - RERA Compliance Framework
Real Estate Regulatory Authority compliance system for Indian real estate
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import re


class RERAState(Enum):
    """Indian states with RERA authorities"""
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHHATTISGARH = "Chhattisgarh"
    DELHI = "Delhi"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"
    CHANDIGARH = "Chandigarh"
    JAMMU_KASHMIR = "Jammu and Kashmir"
    PUDUCHERRY = "Puducherry"


class ProjectStatus(Enum):
    """RERA project status categories"""
    ONGOING = "ongoing"
    COMPLETED = "completed"
    DELAYED = "delayed"
    STALLED = "stalled"
    CANCELLED = "cancelled"


class RegistrationType(Enum):
    """RERA registration types"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    PLOT = "plot"
    RENOVATION = "renovation"


class ComplaintStatus(Enum):
    """RERA complaint status"""
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    HEARING_SCHEDULED = "hearing_scheduled"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    WITHDRAWN = "withdrawn"


class RERAValidator:
    """
    RERA validation and compliance checker
    """
    
    def __init__(self):
        # RERA state authority URLs (simplified)
        self.state_authorities = {
            RERAState.HARYANA: "https://harera.gov.in",
            RERAState.DELHI: "https://delhirera.gov.in",
            RERAState.MAHARASHTRA: "https://maharera.mahaonline.gov.in",
            RERAState.KARNATAKA: "https://rera.karnataka.gov.in",
            RERAState.TAMIL_NADU: "https://tnrera.gov.in",
            RERAState.TELANGANA: "https://rerat.telangana.gov.in",
            RERAState.GUJARAT: "https://gujarat-rera.com",
            RERAState.UTTAR_PRADESH: "https://up-rera.in",
            RERAState.WEST_BENGAL: "https://wb-rera.in",
        }
    
    def validate_rera_number_format(self, rera_number: str, state: RERAState) -> bool:
        """
        Validate RERA number format based on state pattern
        General format: P-[STATE CODE]-XXXXX-XXXX-XXXX
        """
        if not rera_number:
            return False
        
        # Get state code
        state_code = self.get_state_code(state)
        
        # Pattern varies by state, but generally follows:
        # RERA/[STATE]/[PROJECT ID]/[YEAR]
        pattern = rf"RERA/{state_code}/\w+/\d{{4}}"
        
        return bool(re.match(pattern, rera_number, re.IGNORECASE))
    
    def get_state_code(self, state: RERAState) -> str:
        """Get state code for RERA number"""
        state_codes = {
            RERAState.HARYANA: "HR",
            RERAState.DELHI: "DL",
            RERAState.MAHARASHTRA: "MH",
            RERAState.KARNATAKA: "KA",
            RERAState.TAMIL_NADU: "TN",
            RERAState.TELANGANA: "TS",
            RERAState.GUJARAT: "GJ",
            RERAState.UTTAR_PRADESH: "UP",
            RERAState.WEST_BENGAL: "WB",
        }
        return state_codes.get(state, "XX")
    
    def validate_project_compliance(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate project against RERA compliance requirements
        """
        validation_result = {
            'is_compliant': True,
            'compliance_score': 0,
            'missing_requirements': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check RERA registration
        if not project_data.get('rera_number'):
            validation_result['is_compliant'] = False
            validation_result['missing_requirements'].append("RERA registration number")
        else:
            validation_result['compliance_score'] += 20
        
        # Check project details
        required_fields = [
            'project_name', 'builder_name', 'project_address',
            'total_area', 'units_count', 'completion_date'
        ]
        
        for field in required_fields:
            if not project_data.get(field):
                validation_result['compliance_score'] += 5
                validation_result['missing_requirements'].append(f"Missing: {field}")
            else:
                validation_result['compliance_score'] += 10
        
        # Check legal documents
        legal_documents = [
            'title_deed', 'approval_plan', 'commencement_certificate',
            'environment_clearance', 'fire_safety_certificate'
        ]
        
        missing_docs = [doc for doc in legal_documents 
                      if not project_data.get(f'{doc}_available')]
        
        if missing_docs:
            validation_result['warnings'].append(
                f"Missing legal documents: {', '.join(missing_docs)}"
            )
            validation_result['compliance_score'] -= len(missing_docs) * 5
        else:
            validation_result['compliance_score'] += 25
        
        # Check project status timeline
        completion_date = project_data.get('completion_date')
        if completion_date:
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            
            if completion_date < date.today():
                validation_result['warnings'].append("Project completion date has passed")
                validation_result['compliance_score'] -= 10
            else:
                validation_result['compliance_score'] += 15
        
        # Check financial status
        if project_data.get('financial_status') == 'healthy':
            validation_result['compliance_score'] += 10
        else:
            validation_result['warnings'].append("Financial status needs verification")
        
        # Ensure score is within bounds
        validation_result['compliance_score'] = max(0, min(100, validation_result['compliance_score']))
        
        # Final compliance determination
        if validation_result['compliance_score'] >= 80:
            validation_result['compliance_level'] = "High Compliance"
        elif validation_result['compliance_score'] >= 60:
            validation_result['compliance_level'] = "Moderate Compliance"
        else:
            validation_result['compliance_level'] = "Low Compliance"
            validation_result['is_compliant'] = False
        
        return validation_result
    
    def check_builder_reputation(self, builder_name: str) -> Dict[str, Any]:
        """
        Check builder reputation and track record
        """
        # This would integrate with external databases and RERA records
        # Placeholder implementation
        reputation_data = {
            'builder_name': builder_name,
            'total_projects': 0,
            'completed_projects': 0,
            'delayed_projects': 0,
            'complaints_count': 0,
            'reputation_score': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        return reputation_data


class RERADisclosureGenerator:
    """
    Generate RERA-mandated disclosures for properties
    """
    
    def __init__(self):
        self.validator = RERAValidator()
    
    def generate_project_disclosure(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete RERA disclosure for a project
        """
        disclosure = {
            'disclosure_type': 'RERA_PROJECT_DISCLOSURE',
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'Akhi Real Estate Intelligence System',
            
            # Project Identification
            'project_details': {
                'rera_number': project_data.get('rera_number', 'N/A'),
                'project_name': project_data.get('project_name', 'N/A'),
                'builder_name': project_data.get('builder_name', 'N/A'),
                'builder_rera_id': project_data.get('builder_rera_id', 'N/A'),
                'project_address': project_data.get('project_address', 'N/A'),
                'state': project_data.get('state', 'Haryana'),
                'district': project_data.get('district', 'Gurugram'),
                'pincode': project_data.get('pincode', 'N/A')
            },
            
            # Project Specifications
            'project_specifications': {
                'registration_type': project_data.get('registration_type', 'residential'),
                'total_land_area': project_data.get('total_area', 'N/A'),
                'total_units': project_data.get('units_count', 0),
                'unit_types': project_data.get('unit_types', []),
                'commercial_area': project_data.get('commercial_area', 'N/A'),
                'open_space_area': project_data.get('open_space_area', 'N/A'),
                'car_parking_spaces': project_data.get('car_parking', 0)
            },
            
            # Timeline Information
            'timeline': {
                'registration_date': project_data.get('registration_date', 'N/A'),
                'commencement_date': project_data.get('commencement_date', 'N/A'),
                'completion_date': project_data.get('completion_date', 'N/A'),
                'current_status': project_data.get('project_status', 'ongoing'),
                'completion_percentage': project_data.get('completion_percentage', 0)
            },
            
            # Financial Information
            'financial_details': {
                'total_project_cost': project_data.get('total_cost', 'N/A'),
                'cost_per_sqft': project_data.get('cost_per_sqft', 'N/A'),
                'payment_schedule': project_data.get('payment_schedule', []),
                'bank_approvals': project_data.get('bank_approvals', []),
                'financial_status': project_data.get('financial_status', 'unknown')
            },
            
            # Legal Approvals
            'legal_approvals': {
                'title_deed_available': project_data.get('title_deed_available', False),
                'approval_plan_available': project_data.get('approval_plan_available', False),
                'commencement_certificate': project_data.get('commencement_certificate', 'N/A'),
                'environment_clearance': project_data.get('environment_clearance', 'N/A'),
                'fire_safety_certificate': project_data.get('fire_safety_certificate', 'N/A'),
                'building_plan_approval': project_data.get('building_plan_approval', 'N/A')
            },
            
            # Infrastructure and Amenities
            'infrastructure': {
                'water_supply': project_data.get('water_supply', 'N/A'),
                'electricity': project_data.get('electricity', 'N/A'),
                'roads': project_data.get('roads', 'N/A'),
                'sewage': project_data.get('sewage', 'N/A'),
                'amenities': project_data.get('amenities', [])
            },
            
            # Compliance Status
            'compliance_status': self.validator.validate_project_compliance(project_data),
            
            # Contact Information
            'contact_details': {
                'builder_contact': project_data.get('builder_contact', 'N/A'),
                'rera_authority_contact': self.get_rera_authority_contact(project_data.get('state', 'Haryana')),
                'complaint_officer': project_data.get('complaint_officer', 'N/A')
            },
            
            # Disclaimer
            'disclaimer': self.get_rera_disclaimer()
        }
        
        return disclosure
    
    def get_rera_authority_contact(self, state: str) -> Dict[str, str]:
        """Get RERA authority contact information for state"""
        # Simplified contact information
        state_contacts = {
            'Haryana': {
                'authority': 'Haryana Real Estate Regulatory Authority (HARERA)',
                'address': 'HUDA Complex, Sector 14, Gurugram',
                'phone': '0124-2339100',
                'email': 'info@harera.gov.in',
                'website': 'https://harera.gov.in'
            },
            'Delhi': {
                'authority': 'Delhi Real Estate Regulatory Authority (DRERA)',
                'address': 'AWAS Bhawan, Rajendra Nagar, New Delhi',
                'phone': '011-25782554',
                'email': 'info@delhirera.gov.in',
                'website': 'https://delhirera.gov.in'
            }
        }
        
        return state_contacts.get(state, {
            'authority': 'State RERA Authority',
            'address': 'N/A',
            'phone': 'N/A',
            'email': 'N/A',
            'website': 'N/A'
        })
    
    def get_rera_disclaimer(self) -> str:
        """Get standard RERA disclaimer"""
        return """
        DISCLAIMER: This information is provided for informational purposes only and 
        should not be considered as legal advice. Buyers are advised to verify all 
        information directly with the RERA authority and the builder. The company 
        assumes no liability for any discrepancies or inaccuracies in the provided 
        information. Please visit the official RERA website for the most up-to-date 
        and official information.
        """
    
    def generate_property_disclosure(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate RERA disclosure for individual property
        """
        disclosure = {
            'disclosure_type': 'RERA_PROPERTY_DISCLOSURE',
            'generated_at': datetime.now().isoformat(),
            
            'property_details': {
                'property_id': property_data.get('property_id', 'N/A'),
                'title': property_data.get('title', 'N/A'),
                'rera_project_number': property_data.get('rera_project_number', 'N/A'),
                'unit_number': property_data.get('unit_number', 'N/A'),
                'floor': property_data.get('floor', 'N/A'),
                'total_floors': property_data.get('total_floors', 'N/A'),
                'area': property_data.get('area_sqft', 'N/A'),
                'carpet_area': property_data.get('carpet_area', 'N/A'),
                'built_up_area': property_data.get('built_up_area', 'N/A'),
                'price': property_data.get('price', 'N/A'),
                'price_per_sqft': property_data.get('price_per_sqft', 'N/A')
            },
            
            'project_reference': {
                'project_name': property_data.get('project_name', 'N/A'),
                'builder_name': property_data.get('builder_name', 'N/A'),
                'completion_date': property_data.get('completion_date', 'N/A'),
                'possession_status': property_data.get('possession_status', 'N/A')
            },
            
            'legal_status': {
                'title_clear': property_data.get('title_clear', False),
                'encumbrance_free': property_data.get('encumbrance_free', False),
                'approvals_obtained': property_data.get('approvals_obtained', []),
                'pending_approvals': property_data.get('pending_approvals', [])
            },
            
            'compliance_check': {
                'rera_registered': property_data.get('rera_registered', False),
                'compliance_status': 'compliant' if property_data.get('rera_registered') else 'non_compliant'
            }
        }
        
        return disclosure


class RERAComplaintManager:
    """
    RERA complaint management and tracking system
    """
    
    def __init__(self):
        self.complaint_categories = [
            'delay_in_possession',
            'quality_defects',
            'deviation_from_approved_plan',
            'refund_issues',
            'amenities_not_provided',
            'maintenance_issues',
            'documentation_issues',
            'other'
        ]
    
    def file_complaint(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        File a new RERA complaint
        """
        complaint = {
            'complaint_id': self.generate_complaint_id(),
            'filing_date': datetime.now().isoformat(),
            
            # Complainant details
            'complainant': {
                'name': complaint_data.get('complainant_name', 'N/A'),
                'contact': complaint_data.get('complainant_contact', 'N/A'),
                'email': complaint_data.get('complainant_email', 'N/A'),
                'address': complaint_data.get('complainant_address', 'N/A')
            },
            
            # Project details
            'project': {
                'rera_number': complaint_data.get('rera_number', 'N/A'),
                'project_name': complaint_data.get('project_name', 'N/A'),
                'builder_name': complaint_data.get('builder_name', 'N/A'),
                'unit_number': complaint_data.get('unit_number', 'N/A')
            },
            
            # Complaint details
            'complaint_details': {
                'category': complaint_data.get('category', 'other'),
                'sub_category': complaint_data.get('sub_category', 'N/A'),
                'description': complaint_data.get('description', 'N/A'),
                'relief_sought': complaint_data.get('relief_sought', 'N/A'),
                'supporting_documents': complaint_data.get('documents', [])
            },
            
            # Status tracking
            'status': ComplaintStatus.FILED.value,
            'status_history': [{
                'status': ComplaintStatus.FILED.value,
                'date': datetime.now().isoformat(),
                'remarks': 'Complaint filed successfully'
            }],
            
            # Hearing information
            'hearing_details': {
                'scheduled_date': None,
                'venue': None,
                'officer_assigned': None
            },
            
            # Resolution
            'resolution': {
                'outcome': None,
                'orders': None,
                'compliance_deadline': None
            }
        }
        
        return complaint
    
    def generate_complaint_id(self) -> str:
        """Generate unique complaint ID"""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_id = ''.join([str(i) for i in range(6)])
        return f"RERA-CMP-{timestamp}-{random_id}"
    
    def update_complaint_status(self, complaint_id: str, new_status: ComplaintStatus, 
                               remarks: str = None) -> Dict[str, Any]:
        """
        Update complaint status
        """
        status_update = {
            'complaint_id': complaint_id,
            'new_status': new_status.value,
            'updated_at': datetime.now().isoformat(),
            'remarks': remarks
        }
        
        return status_update
    
    def schedule_hearing(self, complaint_id: str, hearing_date: date, 
                       venue: str, officer: str) -> Dict[str, Any]:
        """
        Schedule hearing for complaint
        """
        hearing_details = {
            'complaint_id': complaint_id,
            'hearing_date': hearing_date.isoformat(),
            'venue': venue,
            'officer_assigned': officer,
            'scheduled_at': datetime.now().isoformat()
        }
        
        return hearing_details
    
    def generate_compliance_report(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate RERA compliance report for a project
        """
        validator = RERAValidator()
        compliance_result = validator.validate_project_compliance(project_data)
        
        report = {
            'report_type': 'RERA_COMPLIANCE_REPORT',
            'generated_at': datetime.now().isoformat(),
            'project': {
                'rera_number': project_data.get('rera_number', 'N/A'),
                'project_name': project_data.get('project_name', 'N/A'),
                'builder_name': project_data.get('builder_name', 'N/A')
            },
            'compliance_assessment': compliance_result,
            'recommendations': self.generate_compliance_recommendations(compliance_result),
            'builder_reputation': validator.check_builder_reputation(project_data.get('builder_name', ''))
        }
        
        return report
    
    def generate_compliance_recommendations(self, compliance_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on compliance assessment"""
        recommendations = []
        
        if compliance_result['missing_requirements']:
            recommendations.append(
                f"Immediately address missing requirements: {', '.join(compliance_result['missing_requirements'])}"
            )
        
        if compliance_result['warnings']:
            recommendations.append(
                f"Review and resolve warnings: {', '.join(compliance_result['warnings'])}"
            )
        
        if compliance_result['compliance_score'] < 80:
            recommendations.append(
                "Overall compliance level needs improvement. Focus on missing legal documents and project timeline adherence."
            )
        
        if compliance_result['compliance_score'] >= 80:
            recommendations.append(
                "Maintain current compliance level and regularly update project information."
            )
        
        return recommendations


class RERAIntegrationService:
    """
    Integration service with state RERA portals
    """
    
    def __init__(self):
        self.validator = RERAValidator()
        self.disclosure_generator = RERADisclosureGenerator()
        self.complaint_manager = RERAComplaintManager()
    
    def verify_rera_registration(self, rera_number: str, state: RERAState) -> Dict[str, Any]:
        """
        Verify RERA registration with state authority
        """
        # This would make API calls to state RERA portals
        # Placeholder implementation
        verification_result = {
            'rera_number': rera_number,
            'state': state.value,
            'is_valid': self.validator.validate_rera_number_format(rera_number, state),
            'verified_at': datetime.now().isoformat(),
            'project_details': None,
            'authority_url': self.validator.state_authorities.get(state, 'N/A')
        }
        
        return verification_result
    
    def fetch_project_details(self, rera_number: str, state: RERAState) -> Dict[str, Any]:
        """
        Fetch project details from RERA portal
        """
        # This would make API calls to state RERA portals
        # Placeholder implementation
        project_details = {
            'rera_number': rera_number,
            'project_name': 'Sample Project',
            'builder_name': 'Sample Builder',
            'status': 'ongoing',
            'fetched_at': datetime.now().isoformat()
        }
        
        return project_details
    
    def check_project_updates(self, rera_number: str, state: RERAState) -> Dict[str, Any]:
        """
        Check for updates in project status from RERA portal
        """
        # This would check for updates in project status, complaints, etc.
        # Placeholder implementation
        updates = {
            'rera_number': rera_number,
            'last_checked': datetime.now().isoformat(),
            'new_complaints': 0,
            'status_changes': [],
            'last_update_date': None
        }
        
        return updates


# Initialize global instances
rera_validator = RERAValidator()
rera_disclosure_generator = RERADisclosureGenerator()
rera_complaint_manager = RERAComplaintManager()
rera_integration_service = RERAIntegrationService()