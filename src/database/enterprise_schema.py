"""
Akhi Real Estate Intelligence - Enterprise Database Schema
Pan-India scalable database architecture with PostgreSQL
"""

from __future__ import annotations

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime, 
    Text, ForeignKey, Index, JSON, Enum, DECIMAL, Date, BigInteger,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class SubscriptionStatus(enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAYMENT_FAILED = "payment_failed"


class PropertyStatus(enum.Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RENTED = "rented"
    UNDER_CONSTRUCTION = "under_construction"
    WITHDRAWN = "withdrawn"


class TransactionType(enum.Enum):
    SALE = "sale"
    RENT = "rent"
    LEASE = "lease"


# ============ GEOGRAPHIC DATA MODELS ============

class City(Base):
    """Cities across India"""
    __tablename__ = "cities"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False)
    country = Column(String(50), default="India")
    tier_level = Column(Integer)  # Tier 1, 2, 3 cities
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    is_active = Column(Boolean, default=True)
    population = Column(BigInteger)
    gdp_per_capita = Column(Float)
    property_count = Column(Integer, default=0)
    avg_price_per_sqft = Column(Float)
    grepi_city_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    localities = relationship("Locality", back_populates="city", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_city_state', 'state', 'name'),
        Index('idx_city_tier', 'tier_level'),
    )


class Locality(Base):
    """Localities/Micro-markets within cities"""
    __tablename__ = "localities"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    city_id = Column(BigInteger, ForeignKey("cities.id"), nullable=False)
    name = Column(String(200), nullable=False)
    pincode = Column(String(10))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    properties_count = Column(Integer, default=0)
    avg_price_per_sqft = Column(Float)
    grepi_score = Column(Float)
    institutional_grade = Column(String(10))
    development_score = Column(Float)  # Infrastructure development score
    connectivity_score = Column(Float)  # Transport connectivity
    livability_score = Column(Float)  # Overall livability index
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    city = relationship("City", back_populates="localities")
    properties = relationship("Property", back_populates="locality")
    
    __table_args__ = (
        Index('idx_locality_city', 'city_id', 'name'),
        Index('idx_locality_pincode', 'pincode'),
        UniqueConstraint('city_id', 'name', name='uq_city_locality'),
    )


# ============ USER AND AUTHENTICATION MODELS ============

class User(Base):
    """Enterprise user management"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(50), default="free_user")  # admin, enterprise_user, premium_user, agent, free_user
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    
    # Profile information
    company_name = Column(String(200))
    gstin = Column(String(15))  # GST identification number
    pan_number = Column(String(10))
    aadhaar_verified = Column(Boolean, default=False)
    kyc_verified = Column(Boolean, default=False)
    kyc_document_type = Column(String(50))
    kyc_document_number = Column(String(100))
    
    # Address information (encrypted)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    postal_code = Column(String(10))
    
    # Security settings
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(100))
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    last_password_change = Column(DateTime)
    
    # Session management
    current_session_token = Column(String(255))
    refresh_token = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)  # Soft delete
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="assigned_agent", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_role_status', 'role', 'status'),
        Index('idx_user_company', 'company_name'),
    )


class APIKey(Base):
    """API key management for enterprise clients"""
    __tablename__ = "api_keys"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(200))  # Friendly name for the key
    key_hash = Column(String(255), unique=True, nullable=False)  # Hashed API key
    permissions = Column(JSONB)  # List of permissions
    rate_limit = Column(Integer)  # Custom rate limit
    allowed_ips = Column(JSONB)  # List of allowed IP addresses
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    last_used = Column(DateTime)
    usage_count = Column(BigInteger, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    usage_logs = relationship("APIUsageLog", back_populates="api_key", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_apikey_user', 'user_id', 'is_active'),
    )


class APIUsageLog(Base):
    """API usage tracking for billing and analytics"""
    __tablename__ = "api_usage_logs"
    
    id = Column(BigInteger, primary_key=True)
    api_key_id = Column(BigInteger, ForeignKey("api_keys.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10))  # GET, POST, PUT, DELETE
    response_code = Column(Integer)
    response_time_ms = Column(Integer)
    request_size = Column(BigInteger)  # in bytes
    response_size = Column(BigInteger)  # in bytes
    ip_address = Column(INET)
    user_agent = Column(String(500))
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    api_key = relationship("APIKey", back_populates="usage_logs")


# ============ SUBSCRIPTION AND BILLING MODELS ============

class SubscriptionPlan(Base):
    """Subscription plans for different tiers"""
    __tablename__ = "subscription_plans"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    plan_type = Column(String(50))  # free, professional, enterprise, institutional
    
    # Pricing
    price_monthly = Column(DECIMAL(10, 2))
    price_yearly = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="INR")
    
    # Limits and features
    features = Column(JSONB)  # Detailed feature list
    api_call_limit = Column(Integer)  # Per month
    concurrent_users = Column(Integer)
    data_retention_days = Column(Integer)
    property_listing_limit = Column(Integer)
    support_level = Column(String(50))  # basic, priority, dedicated
    
    # Trial configuration
    trial_days = Column(Integer, default=0)
    trial_features = Column(JSONB)
    
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """User subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("subscription_plans.id"), nullable=False)
    
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    
    # Billing period
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    trial_end_date = Column(Date)
    
    # Payment details
    payment_method_id = Column(String(100))  # Reference to payment gateway
    razorpay_subscription_id = Column(String(100))
    stripe_subscription_id = Column(String(100))
    
    auto_renew = Column(Boolean, default=True)
    
    # Usage tracking
    current_api_calls = Column(Integer, default=0)
    current_property_listings = Column(Integer, default=0)
    
    # Custom enterprise features
    custom_features = Column(JSONB)
    enterprise_license_key = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_subscription_user', 'user_id', 'status'),
        Index('idx_subscription_dates', 'start_date', 'end_date'),
    )


class Invoice(Base):
    """GST-compliant invoicing system"""
    __tablename__ = "invoices"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    subscription_id = Column(BigInteger, ForeignKey("subscriptions.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    
    # Amounts
    subtotal = Column(DECIMAL(15, 2), nullable=False)
    cgst_amount = Column(DECIMAL(15, 2))  # Central GST
    sgst_amount = Column(DECIMAL(15, 2))  # State GST
    igst_amount = Column(DECIMAL(15, 2))  # Integrated GST
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    
    # GST details
    gst_rate = Column(DECIMAL(5, 2))  # GST percentage
    customer_gstin = Column(String(15))
    place_of_supply = Column(String(100))
    
    # Payment
    status = Column(String(50), default="pending")  # pending, paid, cancelled, overdue
    payment_date = Column(DateTime)
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    
    # Additional details
    notes = Column(Text)
    terms = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    """Individual items in an invoice"""
    __tablename__ = "invoice_items"
    
    id = Column(BigInteger, primary_key=True)
    invoice_id = Column(BigInteger, ForeignKey("invoices.id"), nullable=False)
    
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    discount = Column(DECIMAL(10, 2), default=0)
    gst_rate = Column(DECIMAL(5, 2))
    total = Column(DECIMAL(15, 2), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")


# ============ PROPERTY MODELS ============

class Property(Base):
    """Main property listing with pan-India support"""
    __tablename__ = "properties"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Geographic information
    city_id = Column(BigInteger, ForeignKey("cities.id"), nullable=False)
    locality_id = Column(BigInteger, ForeignKey("localities.id"))
    
    # Basic property details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    property_type = Column(String(50), nullable=False)  # Apartment, Villa, Plot, Commercial, etc.
    listing_type = Column(String(50))  # sale, rent, lease
    
    # Property specifications
    bhk_count = Column(Integer)
    bathroom_count = Column(Integer)
    balcony_count = Column(Integer)
    area_sqft = Column(DECIMAL(10, 2), nullable=False)
    area_unit = Column(String(20), default="sqft")
    plot_area_sqft = Column(DECIMAL(10, 2))
    carpet_area_sqft = Column(DECIMAL(10, 2))
    built_up_area_sqft = Column(DECIMAL(10, 2))
    
    # Pricing
    price = Column(DECIMAL(15, 2), nullable=False)
    price_per_sqft = Column(DECIMAL(10, 2))
    expected_price = Column(DECIMAL(15, 2))
    price_negotiable = Column(Boolean, default=True)
    
    # Location details
    address = Column(Text)
    landmark = Column(String(200))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    floor_number = Column(Integer)
    total_floors = Column(Integer)
    
    # Property condition and features
    property_age = Column(Integer)  # in years
    furnishing_status = Column(String(50))  # furnished, semi_furnished, unfurnished
    possession_status = Column(String(50))  # ready_to_move, under_construction
    possession_date = Column(Date)
    completion_date = Column(Date)
    
    # Amenities
    amenities = Column(JSONB)  # List of amenities
    amenities_score = Column(Float)  # Computed score based on amenities
    
    # RERA and regulatory
    rera_number = Column(String(100))
    rera_registered = Column(Boolean, default=False)
    builder_name = Column(String(200))
    project_name = Column(String(200))
    
    # Ownership and contact
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    seller_type = Column(String(50))  # owner, builder, agent
    contact_name = Column(String(200))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    
    # Status and verification
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    verification_status = Column(String(50), default="pending")  # pending, verified, rejected
    featured = Column(Boolean, default=False)
    premium_listing = Column(Boolean, default=False)
    
    # Analytics and intelligence
    view_count = Column(Integer, default=0)
    inquiry_count = Column(Integer, default=0)
    shortlist_count = Column(Integer, default=0)
    grepi_property_score = Column(Float)
    avm_fair_value = Column(DECIMAL(15, 2))
    avm_liquidation_value = Column(DECIMAL(15, 2))
    avm_premium_value = Column(DECIMAL(15, 2))
    
    # Data source and quality
    data_source = Column(String(50))  # manual, api, scraping, user_generated
    source_reference = Column(String(200))
    data_quality_score = Column(Float)
    last_verified = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)  # Soft delete
    
    # Relationships
    city = relationship("City")
    locality = relationship("Locality", back_populates="properties")
    owner = relationship("User", back_populates="properties")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    documents = relationship("PropertyDocument", back_populates="property", cascade="all, delete-orphan")
    price_history = relationship("PropertyPriceHistory", back_populates="property", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_property_city_type', 'city_id', 'property_type'),
        Index('idx_property_price', 'price'),
        Index('idx_property_area', 'area_sqft'),
        Index('idx_property_location', 'latitude', 'longitude'),
        Index('idx_property_status', 'status', 'verification_status'),
        Index('idx_property_features', 'featured', 'premium_listing'),
    )


class PropertyImage(Base):
    """Property images with metadata"""
    __tablename__ = "property_images"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    property_id = Column(BigInteger, ForeignKey("properties.id"), nullable=False)
    
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    caption = Column(String(200))
    image_type = Column(String(50))  # interior, exterior, amenities, floor_plan
    
    # Image metadata
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(BigInteger)
    format = Column(String(10))
    
    # AI analysis
    ai_tags = Column(JSONB)  # AI-generated tags
    quality_score = Column(Float)
    authenticity_score = Column(Float)  # AI-generated authenticity score
    
    display_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="images")


class PropertyDocument(Base):
    """Property documents (legal, approvals, etc.)"""
    __tablename__ = "property_documents"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    property_id = Column(BigInteger, ForeignKey("properties.id"), nullable=False)
    
    document_type = Column(String(50), nullable=False)  # title_deed, approval, floor_plan, etc.
    document_name = Column(String(200), nullable=False)
    document_url = Column(String(500), nullable=False)
    
    # Document verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(BigInteger, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="documents")


class PropertyPriceHistory(Base):
    """Property price tracking over time"""
    __tablename__ = "property_price_history"
    
    id = Column(BigInteger, primary_key=True)
    property_id = Column(BigInteger, ForeignKey("properties.id"), nullable=False)
    
    price = Column(DECIMAL(15, 2), nullable=False)
    price_per_sqft = Column(DECIMAL(10, 2))
    change_type = Column(String(50))  # price_increase, price_decrease, new_listing
    change_percentage = Column(Float)
    
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    recorded_by = Column(String(50))  # system, user, api
    
    # Relationships
    property = relationship("Property", back_populates="price_history")
    
    __table_args__ = (
        Index('idx_price_history_property_date', 'property_id', 'recorded_at'),
    )


# ============ LEAD AND CRM MODELS ============

class Lead(Base):
    """Real estate leads and inquiries"""
    __tablename__ = "leads"
    
    id = Column(BigInteger, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Lead information
    name = Column(String(200), nullable=False)
    email = Column(String(255))
    phone = Column(String(20), nullable=False, index=True)
    
    # Requirements
    budget_min = Column(DECIMAL(15, 2))
    budget_max = Column(DECIMAL(15, 2))
    preferred_cities = Column(JSONB)  # List of city IDs
    preferred_localities = Column(JSONB)  # List of locality IDs
    property_types = Column(JSONB)  # List of property types
    bhk_requirements = Column(JSONB)  # BHK preferences
    area_min = Column(DECIMAL(10, 2))
    area_max = Column(DECIMAL(10, 2))
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType))
    timeline = Column(String(50))  # immediate, 1-3 months, 3-6 months, etc.
    financing = Column(String(50))  # self_funded, loan_required
    
    # Property of interest
    property_id = Column(BigInteger, ForeignKey("properties.id"))
    
    # Lead management
    source = Column(String(50))  # website, referral, advertising, etc.
    medium = Column(String(50))  # organic, paid, social, etc.
    campaign = Column(String(100))
    
    # AI scoring
    lead_score = Column(Float)  # AI-generated lead quality score
    lead_temperature = Column(String(50))  # hot, warm, cold
    conversion_probability = Column(Float)
    estimated_value = Column(DECIMAL(15, 2))
    
    # Assignment
    assigned_agent_id = Column(BigInteger, ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    
    # Status
    status = Column(String(50), default="new")  # new, contacted, qualified, proposal, negotiation, closed, lost
    follow_up_date = Column(DateTime)
    
    # Additional information
    message = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property")
    assigned_agent = relationship("User", back_populates="leads")
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_lead_phone', 'phone'),
        Index('idx_lead_status', 'status', 'lead_score'),
        Index('idx_lead_agent', 'assigned_agent_id', 'status'),
    )


class LeadActivity(Base):
    """Lead activity tracking"""
    __tablename__ = "lead_activities"
    
    id = Column(BigInteger, primary_key=True)
    lead_id = Column(BigInteger, ForeignKey("leads.id"), nullable=False)
    
    activity_type = Column(String(50), nullable=False)  # call, email, meeting, note, etc.
    description = Column(Text)
    outcome = Column(String(50))
    next_follow_up = Column(DateTime)
    
    performed_by = Column(BigInteger, ForeignKey("users.id"))
    performed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="activities")


# ============ ANALYTICS AND ACTIVITY LOGGING ============

class ActivityLog(Base):
    """User activity logging for security and analytics"""
    __tablename__ = "activity_logs"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))  # property, user, subscription, etc.
    entity_id = Column(BigInteger)
    
    ip_address = Column(INET)
    user_agent = Column(String(500))
    request_url = Column(String(500))
    request_method = Column(String(10))
    
    additional_data = Column(JSONB)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    
    __table_args__ = (
        Index('idx_activity_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_activity_action', 'action', 'timestamp'),
    )


class SystemMetrics(Base):
    """System performance and business metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(BigInteger, primary_key=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # counter, gauge, histogram
    
    dimensions = Column(JSONB)  # Additional dimensions for filtering
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'metric_name', 'timestamp'),
    )


# ============ COMPLIANCE MODELS ============

class GSTCompliance(Base):
    """GST compliance tracking"""
    __tablename__ = "gst_compliance"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    gstin = Column(String(15), unique=True, nullable=False)
    registration_date = Column(Date)
    status = Column(String(50))  # active, cancelled, suspended
    
    # GST return filing
    gstr1_filed = Column(Boolean, default=False)
    gstr1_last_filed = Column(Date)
    gstr3b_filed = Column(Boolean, default=False)
    gstr3b_last_filed = Column(Date)
    
    # Compliance checks
    compliance_score = Column(Float)
    last_audit_date = Column(Date)
    next_audit_due = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RERACompliance(Base):
    """RERA compliance tracking"""
    __tablename__ = "rera_compliance"
    
    id = Column(BigInteger, primary_key=True)
    property_id = Column(BigInteger, ForeignKey("properties.id"), nullable=False)
    
    rera_number = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    registration_date = Column(Date)
    
    # Project details
    project_status = Column(String(50))  # ongoing, completed, delayed
    completion_date = Column(Date)
    extended_date = Column(Date)
    
    # Compliance checks
    quarterly_returns_filed = Column(Boolean, default=False)
    last_filing_date = Column(Date)
    complaints_count = Column(Integer, default=0)
    violations_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataConsent(Base):
    """DPDP Act - Data consent management"""
    __tablename__ = "data_consent"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    consent_purpose = Column(String(200), nullable=False)
    consent_description = Column(Text)
    data_categories = Column(JSONB)  # Categories of data consented to
    
    consent_given = Column(Boolean, default=True)
    consent_date = Column(DateTime, default=datetime.utcnow)
    withdrawal_date = Column(DateTime)
    
    legal_basis = Column(String(100))  # contract, legal_obligation, legitimate_interest, consent
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database connection and session management
class DatabaseManager:
    """Enterprise database manager with connection pooling"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or "postgresql://user:password@localhost/akhi_realestate"
        self.engine = create_engine(
            self.database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution)"""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def init_db(self):
        """Initialize database with default data"""
        session = self.get_session()
        try:
            # Create default subscription plans
            default_plans = [
                {
                    "name": "Free Tier",
                    "plan_type": "free",
                    "price_monthly": 0,
                    "price_yearly": 0,
                    "features": ["Basic property search", "Limited analytics", "100 API calls/month"],
                    "api_call_limit": 100,
                    "concurrent_users": 1,
                    "data_retention_days": 30,
                    "support_level": "basic"
                },
                {
                    "name": "Professional",
                    "plan_type": "professional",
                    "price_monthly": 2999,
                    "price_yearly": 29990,
                    "features": ["Advanced analytics", "AVM reports", "Unlimited shortlists", "10,000 API calls/month"],
                    "api_call_limit": 10000,
                    "concurrent_users": 5,
                    "data_retention_days": 365,
                    "support_level": "priority"
                },
                {
                    "name": "Enterprise",
                    "plan_type": "enterprise",
                    "price_monthly": 9999,
                    "price_yearly": 99990,
                    "features": ["Unlimited API access", "White-label options", "Custom integrations", "Dedicated support"],
                    "api_call_limit": 100000,
                    "concurrent_users": 50,
                    "data_retention_days": 1825,
                    "support_level": "dedicated"
                }
            ]
            
            for plan_data in default_plans:
                plan = SubscriptionPlan(**plan_data)
                session.add(plan)
            
            session.commit()
            print("Database initialized with default plans")
            
        except Exception as e:
            session.rollback()
            print(f"Error initializing database: {e}")
        finally:
            session.close()


# Initialize database manager
db_manager = DatabaseManager()

if __name__ == "__main__":
    # Create tables
    db_manager.create_tables()
    print("Database tables created successfully")
    
    # Initialize with default data
    db_manager.init_db()