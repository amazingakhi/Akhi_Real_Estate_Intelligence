"""
Akhi Real Estate Intelligence - Premium UI/UX Components
Advanced dashboard components with premium styling and professional design
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
import json


class PremiumTheme:
    """Premium theme configuration with professional color schemes"""
    
    def __init__(self):
        self.themes = {
            'enterprise_blue': {
                'primary': '#0F4C81',
                'secondary': '#1E3A5F',
                'accent': '#00A8E8',
                'success': '#2ECC71',
                'warning': '#F39C12',
                'danger': '#E74C3C',
                'light': '#ECF0F1',
                'dark': '#2C3E50',
                'background': '#F8F9FA',
                'surface': '#FFFFFF',
                'text_primary': '#2C3E50',
                'text_secondary': '#7F8C8D',
                'border': '#E1E8ED'
            },
            'modern_purple': {
                'primary': '#6C5CE7',
                'secondary': '#4834D4',
                'accent': '#A29BFE',
                'success': '#00B894',
                'warning': '#FDcb6E',
                'danger': '#FF7675',
                'light': '#DFE6E9',
                'dark': '#2D3436',
                'background': '#F5F6FA',
                'surface': '#FFFFFF',
                'text_primary': '#2D3436',
                'text_secondary': '#636E72',
                'border': '#E0E0E0'
            },
            'luxury_gold': {
                'primary': '#D4AF37',
                'secondary': '#1A1A1A',
                'accent': '#C5A028',
                'success': '#27AE60',
                'warning': '#F39C12',
                'danger': '#C0392B',
                'light': '#F5F5F5',
                'dark': '#1A1A1A',
                'background': '#FAFAFA',
                'surface': '#FFFFFF',
                'text_primary': '#1A1A1A',
                'text_secondary': '#666666',
                'border': '#E5E5E5'
            }
        }
        
        self.current_theme = 'enterprise_blue'
    
    def get_theme(self, theme_name: str = None) -> Dict[str, str]:
        """Get theme configuration"""
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes['enterprise_blue'])
    
    def get_css_variables(self, theme_name: str = None) -> str:
        """Generate CSS variables for theme"""
        theme = self.get_theme(theme_name)
        
        css_vars = []
        for key, value in theme.items():
            css_key = f"--{key.replace('_', '-')}"
            css_vars.append(f"{css_key}: {value};")
        
        return "\n".join(css_vars)
    
    def generate_theme_css(self, theme_name: str = None) -> str:
        """Generate complete CSS for theme"""
        theme = self.get_theme(theme_name)
        
        css = f"""
        :root {{
            {self.get_css_variables(theme_name)}
        }}
        
        body {{
            background-color: {theme['background']};
            color: {theme['text_primary']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .premium-card {{
            background: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            padding: 24px;
            margin-bottom: 24px;
        }}
        
        .premium-button {{
            background: {theme['primary']};
            color: {theme['surface']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .premium-button:hover {{
            background: {theme['secondary']};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .premium-input {{
            background: {theme['surface']};
            border: 2px solid {theme['border']};
            border-radius: 8px;
            padding: 12px 16px;
            color: {theme['text_primary']};
            transition: border-color 0.3s ease;
        }}
        
        .premium-input:focus {{
            outline: none;
            border-color: {theme['primary']};
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-success {{ background: {theme['success']}; color: white; }}
        .badge-warning {{ background: {theme['warning']}; color: white; }}
        .badge-danger {{ background: {theme['danger']}; color: white; }}
        .badge-primary {{ background: {theme['primary']}; color: white; }}
        """
        
        return css


class DashboardComponents:
    """Premium dashboard components"""
    
    def __init__(self):
        self.theme = PremiumTheme()
    
    def generate_stat_card(self, title: str, value: str, change: str = None,
                         icon: str = None, color: str = None) -> str:
        """Generate premium statistics card"""
        theme = self.theme.get_theme()
        card_color = color or theme['primary']
        
        return f"""
        <div class="premium-card stat-card">
            <div class="stat-header">
                <span class="stat-title">{title}</span>
                {f'<span class="stat-icon">{icon}</span>' if icon else ''}
            </div>
            <div class="stat-value" style="color: {card_color}; font-size: 32px; font-weight: 700;">
                {value}
            </div>
            {f'<div class="stat-change {change.replace("+", "").replace("-", "")}">{change}</div>' if change else ''}
        </div>
        """
    
    def generate_chart_container(self, chart_id: str, title: str, 
                              chart_type: str = 'line') -> str:
        """Generate premium chart container"""
        return f"""
        <div class="premium-card chart-container">
            <div class="chart-header">
                <h3 class="chart-title">{title}</h3>
                <div class="chart-controls">
                    <button class="chart-control" data-period="7d">7D</button>
                    <button class="chart-control active" data-period="30d">30D</button>
                    <button class="chart-control" data-period="90d">90D</button>
                </div>
            </div>
            <div class="chart-body">
                <canvas id="{chart_id}"></canvas>
            </div>
        </div>
        """
    
    def generate_property_card(self, property_data: Dict[str, Any]) -> str:
        """Generate premium property listing card"""
        theme = self.theme.get_theme()
        
        return f"""
        <div class="premium-card property-card">
            <div class="property-image">
                <img src="{property_data.get('image', 'placeholder.jpg')}" alt="{property_data.get('title', 'Property')}">
                <div class="property-badge badge-primary">Featured</div>
            </div>
            <div class="property-content">
                <h3 class="property-title">{property_data.get('title', 'Property Title')}</h3>
                <div class="property-location">
                    <span class="location-icon">📍</span>
                    {property_data.get('location', 'Location')}
                </div>
                <div class="property-specs">
                    <div class="spec-item">
                        <span class="spec-icon">🏠</span>
                        <span class="spec-value">{property_data.get('bhk', 3)} BHK</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-icon">📐</span>
                        <span class="spec-value">{property_data.get('area_sqft', 1500)} sqft</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-icon">🚿</span>
                        <span class="spec-value">{property_data.get('bathrooms', 2)} Baths</span>
                    </div>
                </div>
                <div class="property-price">
                    <span class="price-amount">{property_data.get('price', '₹85 Lakhs')}</span>
                    <span class="price-per-sqft">₹{property_data.get('price_per_sqft', 7500)}/sqft</span>
                </div>
                <div class="property-actions">
                    <button class="premium-button primary-action">View Details</button>
                    <button class="premium-button secondary-action">Contact</button>
                </div>
            </div>
        </div>
        """
    
    def generate_analytics_dashboard(self, analytics_data: Dict[str, Any]) -> str:
        """Generate comprehensive analytics dashboard"""
        theme = self.theme.get_theme()
        
        return f"""
        <div class="premium-dashboard">
            <div class="dashboard-header">
                <h1 class="dashboard-title">Analytics Dashboard</h1>
                <div class="dashboard-controls">
                    <select class="premium-input period-selector">
                        <option value="7d">Last 7 Days</option>
                        <option value="30d" selected>Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                        <option value="1y">Last Year</option>
                    </select>
                    <button class="premium-button export-button">Export Report</button>
                </div>
            </div>
            
            <div class="stats-grid">
                {self.generate_stat_card("Total Views", analytics_data.get('total_views', '12,345'), "+15%", "👁️")}
                {self.generate_stat_card("Lead Generation", analytics_data.get('leads', '234'), "+8%", "📈", theme['success'])}
                {self.generate_stat_card("Conversion Rate", analytics_data.get('conversion_rate', '12.5%'), "+2.3%", "🎯", theme['accent'])}
                {self.generate_stat_card("Revenue", analytics_data.get('revenue', '₹45.2L'), "+18%", "💰", theme['primary'])}
            </div>
            
            <div class="charts-row">
                {self.generate_chart_container('trendChart', 'Market Trends', 'line')}
                {self.generate_chart_container('distributionChart', 'Property Distribution', 'doughnut')}
            </div>
            
            <div class="table-section">
                <div class="premium-card data-table-card">
                    <div class="table-header">
                        <h3>Recent Inquiries</h3>
                        <button class="premium-button view-all">View All</button>
                    </div>
                    <table class="premium-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Property</th>
                                <th>Budget</th>
                                <th>Status</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self.generate_table_rows(analytics_data.get('inquiries', []))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
    
    def generate_table_rows(self, inquiries: List[Dict[str, Any]]) -> str:
        """Generate table rows for inquiries"""
        rows = []
        
        for inquiry in inquiries[:5]:  # Show first 5
            status_class = {
                'new': 'badge-primary',
                'contacted': 'badge-warning',
                'qualified': 'badge-success',
                'closed': 'badge-success'
            }.get(inquiry.get('status', 'new'), 'badge-primary')
            
            rows.append(f"""
            <tr>
                <td>{inquiry.get('name', 'Unknown')}</td>
                <td>{inquiry.get('property', 'N/A')}</td>
                <td>{inquiry.get('budget', 'N/A')}</td>
                <td><span class="badge {status_class}">{inquiry.get('status', 'new').title()}</span></td>
                <td>{inquiry.get('date', 'N/A')}</td>
                <td>
                    <button class="table-action-btn">View</button>
                    <button class="table-action-btn">Contact</button>
                </td>
            </tr>
            """)
        
        return "\n".join(rows)


class NavigationComponents:
    """Premium navigation components"""
    
    def __init__(self):
        self.theme = PremiumTheme()
    
    def generate_sidebar(self, current_page: str = 'dashboard', 
                       user_name: str = 'User') -> str:
        """Generate premium sidebar navigation"""
        theme = self.theme.get_theme()
        
        menu_items = [
            {'id': 'dashboard', 'label': 'Dashboard', 'icon': '📊'},
            {'id': 'properties', 'label': 'Properties', 'icon': '🏠'},
            {'id': 'analytics', 'label': 'Analytics', 'icon': '📈'},
            {'id': 'intelligence', 'label': 'AI Intelligence', 'icon': '🤖'},
            {'id': 'leads', 'label': 'Leads', 'icon': '👥'},
            {'id': 'reports', 'label': 'Reports', 'icon': '📑'},
            {'id': 'settings', 'label': 'Settings', 'icon': '⚙️'}
        ]
        
        menu_html = []
        for item in menu_items:
            active_class = 'active' if item['id'] == current_page else ''
            menu_html.append(f"""
            <a href="/{item['id']}" class="nav-item {active_class}">
                <span class="nav-icon">{item['icon']}</span>
                <span class="nav-label">{item['label']}</span>
            </a>
            """)
        
        return f"""
        <div class="premium-sidebar">
            <div class="sidebar-header">
                <div class="logo">
                    <span class="logo-icon">🏛️</span>
                    <span class="logo-text">Akhi Real Estate</span>
                </div>
            </div>
            
            <nav class="sidebar-nav">
                {"".join(menu_html)}
            </nav>
            
            <div class="sidebar-footer">
                <div class="user-profile">
                    <div class="user-avatar">U</div>
                    <div class="user-info">
                        <span class="user-name">{user_name}</span>
                        <span class="user-role">Premium User</span>
                    </div>
                </div>
                <button class="logout-btn">Logout</button>
            </div>
        </div>
        """
    
    def generate_top_bar(self, title: str, user_name: str = 'User') -> str:
        """Generate premium top navigation bar"""
        theme = self.theme.get_theme()
        
        return f"""
        <div class="premium-topbar">
            <div class="topbar-left">
                <button class="menu-toggle">☰</button>
                <h1 class="page-title">{title}</h1>
            </div>
            
            <div class="topbar-right">
                <div class="search-bar">
                    <input type="text" class="premium-input search-input" placeholder="Search...">
                    <button class="search-button">🔍</button>
                </div>
                
                <div class="notification-bell">
                    <span class="bell-icon">🔔</span>
                    <span class="notification-count">3</span>
                </div>
                
                <div class="user-menu">
                    <button class="user-avatar-btn">U</button>
                    <div class="user-dropdown">
                        <div class="dropdown-item">Profile</div>
                        <div class="dropdown-item">Settings</div>
                        <div class="dropdown-item">Logout</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def generate_breadcrumb(self, items: List[str]) -> str:
        """Generate breadcrumb navigation"""
        breadcrumb_items = []
        
        for i, item in enumerate(items):
            if i == len(items) - 1:
                breadcrumb_items.append(f'<span class="breadcrumb-item current">{item}</span>')
            else:
                breadcrumb_items.append(f'<a href="#" class="breadcrumb-item">{item}</a>')
                breadcrumb_items.append('<span class="breadcrumb-separator">/</span>')
        
        return f"""
        <div class="breadcrumb-nav">
            {"".join(breadcrumb_items)}
        </div>
        """


class FormComponents:
    """Premium form components with validation"""
    
    def __init__(self):
        self.theme = PremiumTheme()
    
    def generate_form_field(self, field_type: str, field_name: str, 
                           label: str, placeholder: str = None,
                           required: bool = False, options: List[str] = None) -> str:
        """Generate premium form field"""
        theme = self.theme.get_theme()
        required_mark = '*' if required else ''
        
        if field_type == 'text':
            return f"""
            <div class="form-group">
                <label class="form-label">{label} {required_mark}</label>
                <input type="text" name="{field_name}" class="premium-input form-input" 
                       placeholder="{placeholder or label}" required={required}>
            </div>
            """
        elif field_type == 'email':
            return f"""
            <div class="form-group">
                <label class="form-label">{label} {required_mark}</label>
                <input type="email" name="{field_name}" class="premium-input form-input" 
                       placeholder="{placeholder or 'email@example.com'}" required={required}>
            </div>
            """
        elif field_type == 'select':
            options_html = []
            for option in options or []:
                options_html.append(f'<option value="{option}">{option}</option>')
            
            return f"""
            <div class="form-group">
                <label class="form-label">{label} {required_mark}</label>
                <select name="{field_name}" class="premium-input form-select" required={required}>
                    <option value="">Select {label}</option>
                    {"".join(options_html)}
                </select>
            </div>
            """
        elif field_type == 'textarea':
            return f"""
            <div class="form-group">
                <label class="form-label">{label} {required_mark}</label>
                <textarea name="{field_name}" class="premium-input form-textarea" 
                          placeholder="{placeholder or label}" rows="4" required={required}></textarea>
            </div>
            """
        elif field_type == 'number':
            return f"""
            <div class="form-group">
                <label class="form-label">{label} {required_mark}</label>
                <input type="number" name="{field_name}" class="premium-input form-input" 
                       placeholder="{placeholder or '0'}" required={required}>
            </div>
            """
        else:
            return f"""
            <div class="form-group">
                <label class="form-label">{label} {required_mark}</label>
                <input type="{field_type}" name="{field_name}" class="premium-input form-input" 
                       placeholder="{placeholder or label}" required={required}>
            </div>
            """
    
    def generate_contact_form(self) -> str:
        """Generate premium contact form"""
        return f"""
        <div class="premium-card contact-form-card">
            <h2 class="form-title">Get in Touch</h2>
            <form class="premium-form">
                {self.generate_form_field('text', 'name', 'Full Name', 'Enter your name', True)}
                {self.generate_form_field('email', 'email', 'Email Address', required=True)}
                {self.generate_form_field('tel', 'phone', 'Phone Number', 'Enter 10-digit number', True)}
                {self.generate_form_field('select', 'property_interest', 'Property Interest', 
                                        options=['Apartment', 'Villa', 'Plot', 'Commercial'], required=True)}
                {self.generate_form_field('select', 'budget_range', 'Budget Range',
                                        options=['Under 50 Lakhs', '50-1 Crore', '1-3 Crore', '3+ Crores'])}
                {self.generate_form_field('textarea', 'message', 'Message', 'Tell us about your requirements')}
                
                <div class="form-actions">
                    <button type="submit" class="premium-button submit-button">Send Message</button>
                    <button type="reset" class="premium-button reset-button">Clear</button>
                </div>
            </form>
        </div>
        """
    
    def generate_property_search_form(self) -> str:
        """Generate premium property search form"""
        return f"""
        <div class="premium-card search-form-card">
            <h2 class="form-title">Find Your Dream Property</h2>
            <form class="premium-form search-form">
                <div class="form-row">
                    {self.generate_form_field('select', 'city', 'City', 
                                            options=['Gurugram', 'Delhi', 'Mumbai', 'Bangalore', 'Pune'], required=True)}
                    {self.generate_form_field('select', 'property_type', 'Property Type',
                                            options=['Apartment', 'Villa', 'Plot', 'Commercial'], required=True)}
                </div>
                
                <div class="form-row">
                    {self.generate_form_field('select', 'bhk', 'BHK',
                                            options=['1 BHK', '2 BHK', '3 BHK', '4+ BHK'])}
                    {self.generate_form_field('number', 'min_price', 'Min Price (Lakhs)')}
                    {self.generate_form_field('number', 'max_price', 'Max Price (Lakhs)')}
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="premium-button search-button">🔍 Search Properties</button>
                    <button type="reset" class="premium-button reset-button">Reset Filters</button>
                </div>
            </form>
        </div>
        """


class ModalComponents:
    """Premium modal and dialog components"""
    
    def __init__(self):
        self.theme = PremiumTheme()
    
    def generate_modal(self, modal_id: str, title: str, content: str,
                     size: str = 'medium') -> str:
        """Generate premium modal"""
        size_classes = {
            'small': 'modal-sm',
            'medium': 'modal-md',
            'large': 'modal-lg',
            'fullscreen': 'modal-fullscreen'
        }
        
        size_class = size_classes.get(size, 'modal-md')
        
        return f"""
        <div id="{modal_id}" class="premium-modal {size_class}">
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">{title}</h3>
                    <button class="modal-close" data-dismiss="modal">&times;</button>
                </div>
                <div class="modal-body">
                    {content}
                </div>
                <div class="modal-footer">
                    <button class="premium-button modal-cancel" data-dismiss="modal">Cancel</button>
                    <button class="premium-button modal-confirm">Confirm</button>
                </div>
            </div>
        </div>
        """
    
    def generate_property_detail_modal(self, property_data: Dict[str, Any]) -> str:
        """Generate property detail modal"""
        content = f"""
        <div class="property-detail-content">
            <div class="property-gallery">
                <img src="{property_data.get('image', 'placeholder.jpg')}" alt="Property">
            </div>
            <div class="property-info">
                <h2 class="property-modal-title">{property_data.get('title', 'Property Title')}</h2>
                <div class="property-modal-price">{property_data.get('price', '₹85 Lakhs')}</div>
                
                <div class="property-modal-specs">
                    <div class="spec-item">
                        <span class="spec-label">Area:</span>
                        <span class="spec-value">{property_data.get('area_sqft', 1500)} sqft</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">BHK:</span>
                        <span class="spec-value">{property_data.get('bhk', 3)}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Location:</span>
                        <span class="spec-value">{property_data.get('location', 'Sector 56, Gurugram')}</span>
                    </div>
                </div>
                
                <div class="property-modal-description">
                    <h4>Description</h4>
                    <p>{property_data.get('description', 'Luxurious apartment with modern amenities and excellent connectivity.')}</p>
                </div>
                
                <div class="property-modal-amenities">
                    <h4>Amenities</h4>
                    <div class="amenities-list">
                        {"".join([f'<span class="amenity-tag">{amenity}</span>' for amenity in property_data.get('amenities', ['Parking', 'Gym', 'Pool', 'Security'])])}
                    </div>
                </div>
            </div>
        </div>
        """
        
        return self.generate_modal('propertyDetailModal', 'Property Details', content, 'large')


class PremiumUIComponents:
    """
    Main premium UI components system
    """
    
    def __init__(self):
        self.theme = PremiumTheme()
        self.dashboard = DashboardComponents()
        self.navigation = NavigationComponents()
        self.forms = FormComponents()
        self.modals = ModalComponents()
    
    def generate_complete_layout(self, page: str = 'dashboard', title: str = 'Dashboard',
                               user_name: str = 'User', content: str = '') -> str:
        """Generate complete premium layout"""
        theme = self.theme.get_theme()
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} | Akhi Real Estate Intelligence</title>
            <style>
                {self.theme.generate_theme_css()}
                
                /* Additional layout styles */
                .premium-layout {{
                    display: flex;
                    min-height: 100vh;
                    background: {theme['background']};
                }}
                
                .premium-sidebar {{
                    width: 280px;
                    background: {theme['surface']};
                    border-right: 1px solid {theme['border']};
                    position: fixed;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                
                .main-content {{
                    flex: 1;
                    margin-left: 280px;
                    padding: 24px;
                }}
                
                .premium-topbar {{
                    background: {theme['surface']};
                    border-bottom: 1px solid {theme['border']};
                    padding: 16px 24px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: -24px -24px 24px -24px;
                }}
                
                @media (max-width: 768px) {{
                    .premium-sidebar {{
                        transform: translateX(-100%);
                        transition: transform 0.3s ease;
                    }}
                    .premium-sidebar.open {{
                        transform: translateX(0);
                    }}
                    .main-content {{
                        margin-left: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="premium-layout">
                {self.navigation.generate_sidebar(page, user_name)}
                
                <div class="main-content">
                    {self.navigation.generate_top_bar(title, user_name)}
                    
                    <div class="page-content">
                        {content}
                    </div>
                </div>
            </div>
            
            <script>
                // Mobile menu toggle
                document.querySelector('.menu-toggle')?.addEventListener('click', function() {{
                    document.querySelector('.premium-sidebar').classList.toggle('open');
                }});
                
                // User dropdown toggle
                document.querySelector('.user-avatar-btn')?.addEventListener('click', function() {{
                    document.querySelector('.user-dropdown').classList.toggle('show');
                }});
            </script>
        </body>
        </html>
        """
    
    def generate_premium_stylesheet(self) -> str:
        """Generate complete premium stylesheet"""
        theme = self.theme.get_theme()
        
        return f"""
        /* Akhi Real Estate Intelligence - Premium Stylesheet */
        /* Generated: {datetime.now().isoformat()} */
        
        {self.theme.generate_theme_css()}
        
        /* Animation utilities */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(-100%); }}
            to {{ transform: translateX(0); }}
        }}
        
        .animate-fade-in {{
            animation: fadeIn 0.3s ease-out;
        }}
        
        .animate-slide-in {{
            animation: slideIn 0.3s ease-out;
        }}
        
        /* Responsive utilities */
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .charts-row {{
                flex-direction: column;
            }}
            
            .premium-sidebar {{
                transform: translateX(-100%);
            }}
        }}
        
        /* Loading states */
        .loading {{
            opacity: 0.6;
            pointer-events: none;
        }}
        
        .loading::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin: -10px 0 0 -10px;
            border: 2px solid {theme['primary']};
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Success/Error states */
        .success-state {{
            border-color: {theme['success']} !important;
            background: rgba(46, 204, 113, 0.1);
        }}
        
        .error-state {{
            border-color: {theme['danger']} !important;
            background: rgba(231, 76, 60, 0.1);
        }}
        
        /* Tooltip styles */
        [data-tooltip] {{
            position: relative;
        }}
        
        [data-tooltip]:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: {theme['dark']};
            color: {theme['surface']};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
        }}
        """


# Initialize global instances
premium_theme = PremiumTheme()
dashboard_components = DashboardComponents()
navigation_components = NavigationComponents()
form_components = FormComponents()
modal_components = ModalComponents()
premium_ui_components = PremiumUIComponents()