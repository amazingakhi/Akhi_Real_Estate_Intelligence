"""
Akhi Real Estate Intelligence - GST Compliance Framework
Complete GST calculation, invoicing, and reporting system for Indian real estate
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class GSTRate(Enum):
    """GST rates for different real estate categories"""
    AFFORDABLE_HOUSING = Decimal("0.01")  # 1% for affordable housing
    RESIDENTIAL_UNDER_45L = Decimal("0.01")  # 1% for residential < 45L
    RESIDENTIAL_ABOVE_45L = Decimal("0.05")  # 5% for residential > 45L
    COMMERCIAL = Decimal("0.18")  # 18% for commercial
    SERVICES = Decimal("0.18")  # 18% for services
    EXEMPTED = Decimal("0.00")  # 0% for exempted categories


class SupplyType(Enum):
    """Type of supply for GST determination"""
    INTRA_STATE = "intra_state"  # Within same state - CGST + SGST
    INTER_STATE = "inter_state"  # Different states - IGST
    EXPORT = "export"  # Export of services


class HSNCode(Enum):
    """Harmonized System of Nomenclature codes for real estate"""
    RESIDENTIAL_CONSTRUCTION = "998511"
    COMMERCIAL_CONSTRUCTION = "998513"
    REAL_ESTATE_SERVICES = "998541"
    PROPERTY_MANAGEMENT = "998543"
    REAL_ESTATE_AGENT_SERVICES = "998551"


class GSTCalculationEngine:
    """
    GST calculation engine for real estate transactions
    Compliant with Indian GST regulations
    """
    
    def __init__(self):
        self.gst_rates = {
            'affordable_housing': GSTRate.AFFORDABLE_HOUSING.value,
            'residential_under_45l': GSTRate.RESIDENTIAL_UNDER_45L.value,
            'residential_above_45l': GSTRate.RESIDENTIAL_ABOVE_45L.value,
            'commercial': GSTRate.COMMERCIAL.value,
            'services': GSTRate.SERVICES.value,
            'exempted': GSTRate.EXEMPTED.value
        }
    
    def determine_gst_rate(self, property_type: str, property_value: Decimal, 
                          is_affordable: bool = False) -> GSTRate:
        """
        Determine applicable GST rate based on property type and value
        """
        if is_affordable:
            return GSTRate.AFFORDABLE_HOUSING
        
        if property_type.lower() in ['commercial', 'office', 'retail', 'warehouse']:
            return GSTRate.COMMERCIAL
        
        if property_type.lower() in ['apartment', 'villa', 'house', 'residential']:
            if property_value <= Decimal("4500000"):  # 45 Lakhs
                return GSTRate.RESIDENTIAL_UNDER_45L
            else:
                return GSTRate.RESIDENTIAL_ABOVE_45L
        
        if property_type.lower() in ['plot', 'land']:
            return GSTRate.EXEMPTED  # Land sales are generally exempted
        
        return GSTRate.SERVICES  # Default to services rate
    
    def determine_supply_type(self, supplier_state: str, recipient_state: str) -> SupplyType:
        """
        Determine supply type (intra-state vs inter-state)
        """
        if supplier_state.lower() == recipient_state.lower():
            return SupplyType.INTRA_STATE
        elif recipient_state.lower() == 'foreign':
            return SupplyType.EXPORT
        else:
            return SupplyType.INTER_STATE
    
    def calculate_gst(self, taxable_value: Decimal, gst_rate: GSTRate, 
                      supply_type: SupplyType) -> Dict[str, Decimal]:
        """
        Calculate GST breakdown based on rate and supply type
        """
        gst_amount = taxable_value * gst_rate.value
        
        if supply_type == SupplyType.INTRA_STATE:
            # Split into CGST and SGST (50-50)
            cgst_amount = gst_amount / 2
            sgst_amount = gst_amount / 2
            igst_amount = Decimal("0.00")
        elif supply_type == SupplyType.INTER_STATE or supply_type == SupplyType.EXPORT:
            # IGST for inter-state and exports
            igst_amount = gst_amount
            cgst_amount = Decimal("0.00")
            sgst_amount = Decimal("0.00")
        else:
            # Default to IGST
            igst_amount = gst_amount
            cgst_amount = Decimal("0.00")
            sgst_amount = Decimal("0.00")
        
        return {
            "taxable_value": taxable_value,
            "gst_rate": gst_rate.value,
            "gst_amount": gst_amount,
            "cgst_amount": cgst_amount,
            "sgst_amount": sgst_amount,
            "igst_amount": igst_amount,
            "total_amount": taxable_value + gst_amount
        }
    
    def calculate_property_transaction_gst(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete GST calculation for property transaction
        """
        property_type = property_data.get('property_type', 'residential')
        property_value = Decimal(str(property_data.get('property_value', 0)))
        is_affordable = property_data.get('is_affordable', False)
        
        supplier_state = property_data.get('supplier_state', 'Haryana')
        recipient_state = property_data.get('recipient_state', 'Haryana')
        
        # Determine GST rate
        gst_rate = self.determine_gst_rate(property_type, property_value, is_affordable)
        
        # Determine supply type
        supply_type = self.determine_supply_type(supplier_state, recipient_state)
        
        # Calculate GST
        gst_breakdown = self.calculate_gst(property_value, gst_rate, supply_type)
        
        # Add additional information
        result = {
            **gst_breakdown,
            "property_type": property_type,
            "property_value": property_value,
            "is_affordable": is_affordable,
            "supply_type": supply_type.value,
            "hsn_code": self.get_hsn_code(property_type).value,
            "calculation_date": datetime.now().isoformat()
        }
        
        return result
    
    def get_hsn_code(self, property_type: str) -> HSNCode:
        """Get appropriate HSN code for property type"""
        property_type_lower = property_type.lower()
        
        if property_type_lower in ['apartment', 'villa', 'house', 'residential']:
            return HSNCode.RESIDENTIAL_CONSTRUCTION
        elif property_type_lower in ['commercial', 'office', 'retail']:
            return HSNCode.COMMERCIAL_CONSTRUCTION
        elif property_type_lower in ['services', 'consulting', 'advisory']:
            return HSNCode.REAL_ESTATE_SERVICES
        elif property_type_lower in ['management', 'maintenance']:
            return HSNCode.PROPERTY_MANAGEMENT
        else:
            return HSNCode.REAL_ESTATE_AGENT_SERVICES


class GSTInvoiceGenerator:
    """
    GST-compliant invoice generation
    As per GST invoice format and requirements
    """
    
    def __init__(self):
        self.calculation_engine = GSTCalculationEngine()
    
    def generate_invoice_number(self, sequence: int = 1) -> str:
        """
        Generate GST-compliant invoice number
        Format: AKHI/YYYY-YYYY/0001
        """
        financial_year = self.get_financial_year()
        return f"AKHI/{financial_year}/{sequence:04d}"
    
    def get_financial_year(self) -> str:
        """Get current financial year"""
        now = datetime.now()
        if now.month >= 4:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def generate_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete GST-compliant invoice
        """
        # Extract invoice details
        customer_details = invoice_data.get('customer', {})
        invoice_items = invoice_data.get('items', [])
        invoice_date = invoice_data.get('invoice_date', date.today())
        due_date = invoice_data.get('due_date', invoice_date)
        
        # Calculate GST for each item
        calculated_items = []
        total_taxable_value = Decimal("0.00")
        total_gst_amount = Decimal("0.00")
        total_cgst = Decimal("0.00")
        total_sgst = Decimal("0.00")
        total_igst = Decimal("0.00")
        
        for item in invoice_items:
            item_value = Decimal(str(item.get('amount', 0)))
            property_type = item.get('property_type', 'services')
            
            # Determine GST rate
            gst_rate = self.calculation_engine.determine_gst_rate(
                property_type, item_value, item.get('is_affordable', False)
            )
            
            # Determine supply type
            supply_type = self.calculation_engine.determine_supply_type(
                invoice_data.get('supplier_state', 'Haryana'),
                customer_details.get('state', 'Haryana')
            )
            
            # Calculate GST
            gst_calculation = self.calculation_engine.calculate_gst(
                item_value, gst_rate, supply_type
            )
            
            calculated_item = {
                **item,
                **gst_calculation,
                "hsn_code": self.calculation_engine.get_hsn_code(property_type).value
            }
            
            calculated_items.append(calculated_item)
            
            # Update totals
            total_taxable_value += item_value
            total_gst_amount += gst_calculation['gst_amount']
            total_cgst += gst_calculation['cgst_amount']
            total_sgst += gst_calculation['sgst_amount']
            total_igst += gst_calculation['igst_amount']
        
        # Generate invoice
        invoice = {
            "invoice_number": self.generate_invoice_number(),
            "invoice_date": invoice_date.isoformat(),
            "due_date": due_date.isoformat() if isinstance(due_date, date) else due_date,
            
            # Supplier details
            "supplier": {
                "name": "Akhi Real Estate Intelligence Pvt Ltd",
                "gstin": "06AAACAA1234F1Z5",  # Example GSTIN
                "address": "Gurugram, Haryana",
                "state": "Haryana",
                "contact": "6387594514",
                "email": "iamakv01@gmail.com"
            },
            
            # Customer details
            "customer": {
                "name": customer_details.get('name', ''),
                "gstin": customer_details.get('gstin', ''),
                "address": customer_details.get('address', ''),
                "state": customer_details.get('state', ''),
                "contact": customer_details.get('contact', ''),
                "email": customer_details.get('email', '')
            },
            
            # Invoice items
            "items": calculated_items,
            
            # Summary
            "summary": {
                "total_taxable_value": total_taxable_value,
                "total_gst_amount": total_gst_amount,
                "total_cgst": total_cgst,
                "total_sgst": total_sgst,
                "total_igst": total_igst,
                "round_off": Decimal("0.00"),
                "total_amount": total_taxable_value + total_gst_amount,
                "amount_in_words": self.number_to_words(total_taxable_value + total_gst_amount)
            },
            
            # Payment details
            "payment": {
                "bank_name": "HDFC Bank",
                "account_number": "50100234567890",
                "ifsc_code": "HDFC0001234",
                "account_type": "Current Account"
            },
            
            # Terms and conditions
            "terms": [
                "Payment due within 30 days from invoice date.",
                "Interest @18% p.a. will be charged on overdue payments.",
                "Subject to Haryana jurisdiction.",
                "Goods once sold will not be taken back."
            ],
            
            # Metadata
            "generated_at": datetime.now().isoformat(),
            "generated_by": "Akhi Real Estate Intelligence System"
        }
        
        return invoice
    
    def number_to_words(self, amount: Decimal) -> str:
        """Convert amount to Indian rupees in words"""
        # Simplified implementation - in production use proper library
        amount_float = float(amount)
        return f"Rupees {amount_float:.2f} Only"
    
    def generate_invoice_qr_code(self, invoice: Dict[str, Any]) -> str:
        """
        Generate QR code for invoice as per GST requirements
        Contains: GSTIN, Invoice Number, Date, Total Amount, HSN/SAC
        """
        try:
            import qrcode
            from io import BytesIO
            import base64
            
            # Create QR code data
            qr_data = f"{invoice['supplier']['gstin']}|{invoice['invoice_number']}|{invoice['invoice_date']}|{invoice['summary']['total_amount']}|{invoice['items'][0]['hsn_code']}"
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Convert to base64
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except ImportError:
            # Return placeholder if qrcode library not available
            return "QR_CODE_PLACEHOLDER"


class GSTReportingService:
    """
    GST return filing and reporting services
    GSTR-1, GSTR-3B reporting
    """
    
    def __init__(self):
        self.invoice_generator = GSTInvoiceGenerator()
    
    def generate_gstr1_report(self, period_start: date, period_end: date, 
                            transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate GSTR-1 report for outward supplies
        """
        gstr1_data = {
            "gstr1": {
                "period": f"{period_start.strftime('%b%y')}",
                "tax_period": {
                    "from": period_start.isoformat(),
                    "to": period_end.isoformat()
                },
                "supplied_details": {
                    "b2b": [],  # B2B invoices
                    "b2cl": [],  # B2C Large invoices
                    "b2cs": [],  # B2C Small invoices
                    "cdnr": [],  # Credit/Debit Notes (Registered)
                    "cdnur": [],  # Credit/Debit Notes (Unregistered)
                    "exp": [],   # Exports
                    "at": [],    # Advances Received
                    "txpd": [],  # Advances Adjusted
                    "nil": [],   # Nil-Rated/Exempted/Non-GST
                    "doc_issue": []  # Document Issued Details
                }
            }
        }
        
        # Categorize transactions
        for transaction in transactions:
            invoice = transaction.get('invoice', {})
            customer = invoice.get('customer', {})
            
            if customer.get('gstin'):
                # B2B - Registered customer
                gstr1_data["gstr1"]["supplied_details"]["b2b"].append({
                    "invoice_number": invoice['invoice_number'],
                    "invoice_date": invoice['invoice_date'],
                    "invoice_value": invoice['summary']['total_amount'],
                    "customer_gstin": customer['gstin'],
                    "customer_name": customer['name'],
                    "pos": customer['state'],  # Place of Supply
                    "reverse_charge": "N",
                    "invoice_type": "Regular",
                    "ecommerce_gstin": "",
                    "taxable_value": invoice['summary']['total_taxable_value'],
                    "cgst_amount": invoice['summary']['total_cgst'],
                    "sgst_amount": invoice['summary']['total_sgst'],
                    "igst_amount": invoice['summary']['total_igst'],
                    "cess_amount": 0
                })
            else:
                # B2C - Unregistered customer
                if invoice['summary']['total_amount'] > Decimal("250000"):
                    gstr1_data["gstr1"]["supplied_details"]["b2cl"].append({
                        "invoice_number": invoice['invoice_number'],
                        "invoice_date": invoice['invoice_date'],
                        "invoice_value": invoice['summary']['total_amount'],
                        "pos": customer['state'],
                        "customer_name": customer['name'],
                        "taxable_value": invoice['summary']['total_taxable_value'],
                        "cgst_amount": invoice['summary']['total_cgst'],
                        "sgst_amount": invoice['summary']['total_sgst'],
                        "igst_amount": invoice['summary']['total_igst'],
                        "cess_amount": 0
                    })
                else:
                    gstr1_data["gstr1"]["supplied_details"]["b2cs"].append({
                        "invoice_type": "Inter-State" if invoice['summary']['total_igst'] > 0 else "Intra-State",
                        "pos": customer['state'],
                        "taxable_value": invoice['summary']['total_taxable_value'],
                        "cgst_amount": invoice['summary']['total_cgst'],
                        "sgst_amount": invoice['summary']['total_sgst'],
                        "igst_amount": invoice['summary']['total_igst'],
                        "cess_amount": 0,
                        "total_amount": invoice['summary']['total_amount']
                    })
        
        # Calculate summary
        summary = self.calculate_gstr1_summary(gstr1_data["gstr1"]["supplied_details"])
        gstr1_data["summary"] = summary
        
        return gstr1_data
    
    def calculate_gstr1_summary(self, supplied_details: Dict[str, List]) -> Dict[str, Any]:
        """Calculate GSTR-1 summary totals"""
        summary = {
            "total_taxable_value": Decimal("0.00"),
            "total_igst": Decimal("0.00"),
            "total_cgst": Decimal("0.00"),
            "total_sgst": Decimal("0.00"),
            "total_cess": Decimal("0.00"),
            "total_invoice_value": Decimal("0.00")
        }
        
        # Sum up all categories
        for category in supplied_details.values():
            for item in category:
                summary["total_taxable_value"] += Decimal(str(item.get('taxable_value', 0)))
                summary["total_igst"] += Decimal(str(item.get('igst_amount', 0)))
                summary["total_cgst"] += Decimal(str(item.get('cgst_amount', 0)))
                summary["total_sgst"] += Decimal(str(item.get('sgst_amount', 0)))
                summary["total_cess"] += Decimal(str(item.get('cess_amount', 0)))
                summary["total_invoice_value"] += Decimal(str(item.get('invoice_value', item.get('total_amount', 0))))
        
        return summary
    
    def generate_gstr3b_report(self, period_start: date, period_end: date,
                              outward_supplies: List[Dict[str, Any]],
                              inward_supplies: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate GSTR-3B summary report
        """
        inward_supplies = inward_supplies or []
        
        # Calculate outward supplies
        outward_total = Decimal("0.00")
        outward_igst = Decimal("0.00")
        outward_cgst = Decimal("0.00")
        outward_sgst = Decimal("0.00")
        
        for supply in outward_supplies:
            invoice = supply.get('invoice', {})
            outward_total += invoice['summary']['total_taxable_value']
            outward_igst += invoice['summary']['total_igst']
            outward_cgst += invoice['summary']['total_cgst']
            outward_sgst += invoice['summary']['total_sgst']
        
        # Calculate inward supplies (simplified)
        inward_total = Decimal("0.00")
        inward_igst = Decimal("0.00")
        inward_cgst = Decimal("0.00")
        inward_sgst = Decimal("0.00")
        
        for supply in inward_supplies:
            inward_total += Decimal(str(supply.get('taxable_value', 0)))
            inward_igst += Decimal(str(supply.get('igst_amount', 0)))
            inward_cgst += Decimal(str(supply.get('cgst_amount', 0)))
            inward_sgst += Decimal(str(supply.get('sgst_amount', 0)))
        
        # Calculate tax liability
        total_igst_liability = outward_igst - inward_igst
        total_cgst_liability = outward_cgst - inward_cgst
        total_sgst_liability = outward_sgst - inward_sgst
        total_tax_liability = total_igst_liability + total_cgst_liability + total_sgst_liability
        
        gstr3b_data = {
            "gstr3b": {
                "period": f"{period_start.strftime('%b%y')}",
                "tax_period": {
                    "from": period_start.isoformat(),
                    "to": period_end.isoformat()
                },
                
                # Part A - Details of outward supplies
                "part_a": {
                    "total_taxable_value": outward_total,
                    "total_igst": outward_igst,
                    "total_cgst": outward_cgst,
                    "total_sgst": outward_sgst
                },
                
                # Part B - Details of inward supplies ( attracts reverse charge )
                "part_b": {
                    "total_taxable_value": inward_total,
                    "total_igst": inward_igst,
                    "total_cgst": inward_cgst,
                    "total_sgst": inward_sgst
                },
                
                # Part C - Details of eligible input tax credit
                "part_c": {
                    "total_itc_available": inward_cgst + inward_sgst + inward_igst,
                    "itc_available_cgst": inward_cgst,
                    "itc_available_sgst": inward_sgst,
                    "itc_available_igst": inward_igst
                },
                
                # Part D - Details of tax paid
                "part_d": {
                    "total_tax_paid": total_tax_liability,
                    "igst_paid": total_igst_liability,
                    "cgst_paid": total_cgst_liability,
                    "sgst_paid": total_sgst_liability
                },
                
                # Summary
                "summary": {
                    "total_tax_liability": total_tax_liability,
                    "total_igst_liability": total_igst_liability,
                    "total_cgst_liability": total_cgst_liability,
                    "total_sgst_liability": total_sgst_liability
                }
            }
        }
        
        return gstr3b_data
    
    def export_gstr_json(self, gstr_data: Dict[str, Any], filename: str) -> str:
        """
        Export GSTR data to JSON format for GST portal upload
        """
        try:
            with open(filename, 'w') as f:
                json.dump(gstr_data, f, indent=2, default=str)
            return filename
        except Exception as e:
            raise Exception(f"Error exporting GSTR data: {e}")


class GSTComplianceManager:
    """
    Main GST compliance management system
    """
    
    def __init__(self):
        self.calculation_engine = GSTCalculationEngine()
        self.invoice_generator = GSTInvoiceGenerator()
        self.reporting_service = GSTReportingService()
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete GST processing for a transaction
        """
        # Calculate GST
        gst_calculation = self.calculation_engine.calculate_property_transaction_gst(transaction_data)
        
        # Generate invoice
        invoice_data = {
            'customer': transaction_data.get('customer', {}),
            'items': [{
                'description': transaction_data.get('description', 'Real Estate Service'),
                'amount': transaction_data.get('property_value', 0),
                'property_type': transaction_data.get('property_type', 'services'),
                'is_affordable': transaction_data.get('is_affordable', False)
            }],
            'supplier_state': transaction_data.get('supplier_state', 'Haryana'),
            'invoice_date': transaction_data.get('invoice_date', date.today()),
            'due_date': transaction_data.get('due_date', date.today())
        }
        
        invoice = self.invoice_generator.generate_invoice(invoice_data)
        
        return {
            'gst_calculation': gst_calculation,
            'invoice': invoice,
            'compliance_status': 'compliant'
        }
    
    def validate_gst_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate transaction for GST compliance
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if required fields are present
        required_fields = ['property_value', 'property_type', 'customer']
        for field in required_fields:
            if field not in transaction_data:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Missing required field: {field}")
        
        # Validate GSTIN if provided
        customer = transaction_data.get('customer', {})
        gstin = customer.get('gstin', '')
        if gstin and not self.validate_gstin_format(gstin):
            validation_result['is_valid'] = False
            validation_result['errors'].append("Invalid GSTIN format")
        
        # Validate property value
        property_value = transaction_data.get('property_value', 0)
        if property_value <= 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Property value must be positive")
        
        return validation_result
    
    def validate_gstin_format(self, gstin: str) -> bool:
        """
        Validate GSTIN format (Indian GST identification number)
        Format: 22AAAAA0000A1Z5
        """
        if len(gstin) != 15:
            return False
        
        # Check if first 2 characters are digits (state code)
        if not gstin[:2].isdigit():
            return False
        
        # Check if next 10 characters are alphanumeric (PAN)
        pan_part = gstin[2:12]
        if not pan_part.isalnum():
            return False
        
        # Check if 13th character is alphanumeric (entity code)
        if not gstin[12].isalnum():
            return False
        
        # Check if last character is 'Z' (check digit indicator)
        if gstin[13] != 'Z':
            return False
        
        # Check if last character is digit (check digit)
        if not gstin[14].isdigit():
            return False
        
        return True


# Initialize global instances
gst_engine = GSTCalculationEngine()
gst_invoice_generator = GSTInvoiceGenerator()
gst_reporting_service = GSTReportingService()
gst_compliance_manager = GSTComplianceManager()