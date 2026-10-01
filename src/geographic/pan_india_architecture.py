"""
Akhi Real Estate Intelligence - Pan-India Geographic Architecture
Multi-city scalable system with regional load balancing and localization
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import math


class CityTier(Enum):
    """City classification tiers"""
    TIER_1 = "tier_1"  # Major metros (Mumbai, Delhi, Bangalore, etc.)
    TIER_2 = "tier_2"  # State capitals and major cities
    TIER_3 = "tier_3"  # Emerging cities


class Region(Enum):
    """Geographic regions of India"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTRAL = "central"
    NORTH_EAST = "north_east"


class Language(Enum):
    """Supported languages for pan-India coverage"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"


class CityData:
    """Complete city data structure"""
    
    def __init__(self, city_id: int, name: str, state: str, tier: CityTier,
                 region: Region, population: int, latitude: Decimal, 
                 longitude: Decimal, primary_language: Language):
        self.city_id = city_id
        self.name = name
        self.state = state
        self.tier = tier
        self.region = region
        self.population = population
        self.latitude = latitude
        self.longitude = longitude
        self.primary_language = primary_language
        
        # Economic indicators
        self.gdp_per_capita = Decimal("0")
        self.avg_property_price = Decimal("0")
        self.avg_price_per_sqft = Decimal("0")
        self.grepi_city_score = 0.0
        
        # Infrastructure scores
        self.connectivity_score = 0.0
        self.infrastructure_score = 0.0
        self.livability_score = 0.0
        
        # Real estate metrics
        self.total_properties = 0
        self.active_listings = 0
        self.market_growth_rate = 0.0


class IndianCitiesDatabase:
    """Comprehensive database of Indian cities with real estate data"""
    
    def __init__(self):
        self.cities = self._initialize_cities()
        self.city_mappings = self._create_city_mappings()
        self.language_mappings = self._create_language_mappings()
    
    def _initialize_cities(self) -> Dict[str, CityData]:
        """Initialize major Indian cities with real estate data"""
        cities = {}
        
        # Tier 1 Cities
        cities['mumbai'] = CityData(
            city_id=1, name="Mumbai", state="Maharashtra", tier=CityTier.TIER_1,
            region=Region.WEST, population=18400000,
            latitude=Decimal("19.0760"), longitude=Decimal("72.8777"),
            primary_language=Language.MARATHI
        )
        cities['delhi'] = CityData(
            city_id=2, name="Delhi", state="Delhi", tier=CityTier.TIER_1,
            region=Region.NORTH, population=16700000,
            latitude=Decimal("28.7041"), longitude=Decimal("77.1025"),
            primary_language=Language.HINDI
        )
        cities['bangalore'] = CityData(
            city_id=3, name="Bangalore", state="Karnataka", tier=CityTier.TIER_1,
            region=Region.SOUTH, population=8440000,
            latitude=Decimal("12.9716"), longitude=Decimal("77.5946"),
            primary_language=Language.KANNADA
        )
        cities['chennai'] = CityData(
            city_id=4, name="Chennai", state="Tamil Nadu", tier=CityTier.TIER_1,
            region=Region.SOUTH, population=7040000,
            latitude=Decimal("13.0827"), longitude=Decimal("80.2707"),
            primary_language=Language.TAMIL
        )
        cities['kolkata'] = CityData(
            city_id=5, name="Kolkata", state="West Bengal", tier=CityTier.TIER_1,
            region=Region.EAST, population=4490000,
            latitude=Decimal("22.5726"), longitude=Decimal("88.3639"),
            primary_language=Language.BENGALI
        )
        cities['hyderabad'] = CityData(
            city_id=6, name="Hyderabad", state="Telangana", tier=CityTier.TIER_1,
            region=Region.SOUTH, population=6800000,
            latitude=Decimal("17.3850"), longitude=Decimal("78.4867"),
            primary_language=Language.TELUGU
        )
        
        # Tier 2 Cities
        cities['gurugram'] = CityData(
            city_id=7, name="Gurugram", state="Haryana", tier=CityTier.TIER_2,
            region=Region.NORTH, population=876000,
            latitude=Decimal("28.4595"), longitude=Decimal("77.0266"),
            primary_language=Language.HINDI
        )
        cities['noida'] = CityData(
            city_id=8, name="Noida", state="Uttar Pradesh", tier=CityTier.TIER_2,
            region=Region.NORTH, population=637000,
            latitude=Decimal("28.5355"), longitude=Decimal("77.3910"),
            primary_language=Language.HINDI
        )
        cities['pune'] = CityData(
            city_id=9, name="Pune", state="Maharashtra", tier=CityTier.TIER_2,
            region=Region.WEST, population=3120000,
            latitude=Decimal("18.5204"), longitude=Decimal("73.8567"),
            primary_language=Language.MARATHI
        )
        cities['ahmedabad'] = CityData(
            city_id=10, name="Ahmedabad", state="Gujarat", tier=CityTier.TIER_2,
            region=Region.WEST, population=5570000,
            latitude=Decimal("23.0225"), longitude=Decimal("72.5714"),
            primary_language=Language.GUJARAT
        )
        cities['jaipur'] = CityData(
            city_id=11, name="Jaipur", state="Rajasthan", tier=CityTier.TIER_2,
            region=Region.NORTH, population=3070000,
            latitude=Decimal("26.9124"), longitude=Decimal("75.7873"),
            primary_language=Language.HINDI
        )
        cities['lucknow'] = CityData(
            city_id=12, name="Lucknow", state="Uttar Pradesh", tier=CityTier.TIER_2,
            region=Region.NORTH, population=2800000,
            latitude=Decimal("26.8467"), longitude=Decimal("80.9462"),
            primary_language=Language.HINDI
        )
        cities['chandigarh'] = CityData(
            city_id=13, name="Chandigarh", state="Chandigarh", tier=CityTier.TIER_2,
            region=Region.NORTH, population=1100000,
            latitude=Decimal("30.7333"), longitude=Decimal("76.7794"),
            primary_language=Language.PUNJABI
        )
        cities['kochi'] = CityData(
            city_id=14, name="Kochi", state="Kerala", tier=CityTier.TIER_2,
            region=Region.SOUTH, population=601000,
            latitude=Decimal("9.9312"), longitude=Decimal("76.2673"),
            primary_language=Language.MALAYALAM
        )
        
        # Tier 3 Cities (sample)
        cities['indore'] = CityData(
            city_id=15, name="Indore", state="Madhya Pradesh", tier=CityTier.TIER_3,
            region=Region.CENTRAL, population=1900000,
            latitude=Decimal("22.7196"), longitude=Decimal("75.8577"),
            primary_language=Language.HINDI
        )
        cities['coimbatore'] = CityData(
            city_id=16, name="Coimbatore", state="Tamil Nadu", tier=CityTier.TIER_3,
            region=Region.SOUTH, population=1600000,
            latitude=Decimal("11.0168"), longitude=Decimal("76.9558"),
            primary_language=Language.TAMIL
        )
        
        # Set default values for all cities
        for city in cities.values():
            city.gdp_per_capita = self._estimate_gdp_per_capita(city.tier)
            city.avg_property_price = self._estimate_avg_property_price(city.tier)
            city.avg_price_per_sqft = self._estimate_avg_price_per_sqft(city.tier)
            city.connectivity_score = self._estimate_connectivity_score(city.tier)
            city.infrastructure_score = self._estimate_infrastructure_score(city.tier)
            city.livability_score = self._estimate_livability_score(city.tier)
        
        return cities
    
    def _estimate_gdp_per_capita(self, tier: CityTier) -> Decimal:
        """Estimate GDP per capita based on city tier"""
        gdp_estimates = {
            CityTier.TIER_1: Decimal("250000"),
            CityTier.TIER_2: Decimal("150000"),
            CityTier.TIER_3: Decimal("80000")
        }
        return gdp_estimates.get(tier, Decimal("80000"))
    
    def _estimate_avg_property_price(self, tier: CityTier) -> Decimal:
        """Estimate average property price based on city tier"""
        price_estimates = {
            CityTier.TIER_1: Decimal("15000000"),  # 1.5 Cr
            CityTier.TIER_2: Decimal("8000000"),   # 80 Lakhs
            CityTier.TIER_3: Decimal("4000000")   # 40 Lakhs
        }
        return price_estimates.get(tier, Decimal("4000000"))
    
    def _estimate_avg_price_per_sqft(self, tier: CityTier) -> Decimal:
        """Estimate average price per sqft based on city tier"""
        price_estimates = {
            CityTier.TIER_1: Decimal("12000"),
            CityTier.TIER_2: Decimal("7000"),
            CityTier.TIER_3: Decimal("4000")
        }
        return price_estimates.get(tier, Decimal("4000"))
    
    def _estimate_connectivity_score(self, tier: CityTier) -> float:
        """Estimate connectivity score based on city tier"""
        score_estimates = {
            CityTier.TIER_1: 85.0,
            CityTier.TIER_2: 70.0,
            CityTier.TIER_3: 55.0
        }
        return score_estimates.get(tier, 55.0)
    
    def _estimate_infrastructure_score(self, tier: CityTier) -> float:
        """Estimate infrastructure score based on city tier"""
        score_estimates = {
            CityTier.TIER_1: 90.0,
            CityTier.TIER_2: 75.0,
            CityTier.TIER_3: 60.0
        }
        return score_estimates.get(tier, 60.0)
    
    def _estimate_livability_score(self, tier: CityTier) -> float:
        """Estimate livability score based on city tier"""
        score_estimates = {
            CityTier.TIER_1: 80.0,
            CityTier.TIER_2: 70.0,
            CityTier.TIER_3: 60.0
        }
        return score_estimates.get(tier, 60.0)
    
    def _create_city_mappings(self) -> Dict[str, List[str]]:
        """Create various city name mappings for search"""
        return {
            'mumbai': ['mumbai', 'bombay', 'mumbai city'],
            'delhi': ['delhi', 'new delhi', 'nct delhi'],
            'bangalore': ['bangalore', 'bengaluru', 'bangaluru'],
            'chennai': ['chennai', 'madras'],
            'kolkata': ['kolkata', 'calcutta'],
            'hyderabad': ['hyderabad', 'hyderabad city'],
            'gurugram': ['gurugram', 'gurgaon'],
            'noida': ['noida', 'new okhla industrial development area']
        }
    
    def _create_language_mappings(self) -> Dict[Region, List[Language]]:
        """Map regions to primary languages"""
        return {
            Region.NORTH: [Language.HINDI, Language.PUNJABI],
            Region.SOUTH: [Language.TAMIL, Language.TELUGU, Language.KANNADA, Language.MALAYALAM],
            Region.EAST: [Language.BENGALI, Language.HINDI],
            Region.WEST: [Language.MARATHI, Language.GUJARATI, Language.HINDI],
            Region.CENTRAL: [Language.HINDI],
            Region.NORTH_EAST: [Language.BENGALI, Language.HINDI]
        }
    
    def get_city(self, city_name: str) -> Optional[CityData]:
        """Get city data by name"""
        city_name_lower = city_name.lower().strip()
        
        # Check direct match
        if city_name_lower in self.cities:
            return self.cities[city_name_lower]
        
        # Check alternate names
        for standard_name, alternate_names in self.city_mappings.items():
            if city_name_lower in [name.lower() for name in alternate_names]:
                return self.cities[standard_name]
        
        return None
    
    def get_cities_by_tier(self, tier: CityTier) -> List[CityData]:
        """Get all cities of a specific tier"""
        return [city for city in self.cities.values() if city.tier == tier]
    
    def get_cities_by_region(self, region: Region) -> List[CityData]:
        """Get all cities in a specific region"""
        return [city for city in self.cities.values() if city.region == region]
    
    def get_nearby_cities(self, city_name: str, radius_km: int = 100) -> List[CityData]:
        """Get cities within a specified radius"""
        city = self.get_city(city_name)
        if not city:
            return []
        
        nearby_cities = []
        for other_city in self.cities.values():
            if other_city.city_id == city.city_id:
                continue
            
            distance = self._calculate_distance(
                city.latitude, city.longitude,
                other_city.latitude, other_city.longitude
            )
            
            if distance <= radius_km:
                nearby_cities.append((other_city, distance))
        
        # Sort by distance
        nearby_cities.sort(key=lambda x: x[1])
        
        return [city for city, distance in nearby_cities]
    
    def _calculate_distance(self, lat1: Decimal, lon1: Decimal, 
                          lat2: Decimal, lon2: Decimal) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        # Convert to float for calculation
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        
        # Earth radius in km
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance


class RegionalLoadBalancer:
    """Regional load balancing for multi-region deployment"""
    
    def __init__(self):
        self.regions = {
            Region.NORTH: {
                'primary_datacenter': 'delhi',
                'secondary_datacenter': 'mumbai',
                'cities': ['delhi', 'gurugram', 'noida', 'jaipur', 'lucknow', 'chandigarh'],
                'server_capacity': 10000,
                'current_load': 2500
            },
            Region.SOUTH: {
                'primary_datacenter': 'bangalore',
                'secondary_datacenter': 'chennai',
                'cities': ['bangalore', 'chennai', 'hyderabad', 'kochi', 'coimbatore'],
                'server_capacity': 8000,
                'current_load': 1800
            },
            Region.WEST: {
                'primary_datacenter': 'mumbai',
                'secondary_datacenter': 'pune',
                'cities': ['mumbai', 'pune', 'ahmedabad'],
                'server_capacity': 7000,
                'current_load': 1500
            },
            Region.EAST: {
                'primary_datacenter': 'kolkata',
                'secondary_datacenter': 'delhi',
                'cities': ['kolkata'],
                'server_capacity': 3000,
                'current_load': 400
            },
            Region.CENTRAL: {
                'primary_datacenter': 'delhi',
                'secondary_datacenter': 'mumbai',
                'cities': ['indore'],
                'server_capacity': 2000,
                'current_load': 300
            }
        }
    
    def get_region_for_city(self, city_name: str) -> Optional[Region]:
        """Get the region for a given city"""
        cities_db = IndianCitiesDatabase()
        city = cities_db.get_city(city_name)
        
        if city:
            return city.region
        
        return None
    
    def get_optimal_datacenter(self, city_name: str) -> str:
        """Get the optimal datacenter for a city based on load balancing"""
        region = self.get_region_for_city(city_name)
        
        if not region:
            return 'delhi'  # Default fallback
        
        region_config = self.regions[region]
        
        # Check load and choose primary or secondary
        load_percentage = (region_config['current_load'] / region_config['server_capacity']) * 100
        
        if load_percentage > 80:
            return region_config['secondary_datacenter']
        else:
            return region_config['primary_datacenter']
    
    def get_server_capacity(self, region: Region) -> Dict[str, Any]:
        """Get server capacity information for a region"""
        if region not in self.regions:
            return None
        
        config = self.regions[region]
        load_percentage = (config['current_load'] / config['server_capacity']) * 100
        
        return {
            'region': region.value,
            'primary_datacenter': config['primary_datacenter'],
            'secondary_datacenter': config['secondary_datacenter'],
            'server_capacity': config['server_capacity'],
            'current_load': config['current_load'],
            'load_percentage': round(load_percentage, 2),
            'available_capacity': config['server_capacity'] - config['current_load'],
            'status': 'healthy' if load_percentage < 80 else 'high_load'
        }


class LocalizationManager:
    """Multi-language support and localization"""
    
    def __init__(self):
        self.translations = self._initialize_translations()
        self.language_data = self._initialize_language_data()
    
    def _initialize_translations(self) -> Dict[str, Dict[str, str]]:
        """Initialize translations for supported languages"""
        return {
            'en': {
                'search_properties': 'Search Properties',
                'buy': 'Buy',
                'rent': 'Rent',
                'price': 'Price',
                'location': 'Location',
                'bedrooms': 'Bedrooms',
                'bathrooms': 'Bathrooms',
                'area': 'Area',
                'contact': 'Contact',
                'more_details': 'More Details',
                'welcome': 'Welcome to Akhi Real Estate',
                'search_placeholder': 'Search by city, locality, or landmark...'
            },
            'hi': {
                'search_properties': 'गुण खोजें',
                'buy': 'खरीदें',
                'rent': 'किराए पर लें',
                'price': 'कीमत',
                'location': 'स्थान',
                'bedrooms': 'बेडरूम',
                'bathrooms': 'बाथरूम',
                'area': 'क्षेत्र',
                'contact': 'संपर्क करें',
                'more_details': 'अधिक विवरण',
                'welcome': 'अखी रियल एस्टेट में आपका स्वागत है',
                'search_placeholder': 'शहर, इलाका, या पहचान से खोजें...'
            },
            'ta': {
                'search_properties': 'சொத்துகளைத் தேடுங்கள்',
                'buy': 'வாங்குங்கள்',
                'rent': 'வாடகைக்கு எடுங்கள்',
                'price': 'விலை',
                'location': 'இடம்',
                'bedrooms': 'படுக்கைகள்',
                'bathrooms': 'குளியறைகள்',
                'area': 'பரப்பளவு',
                'contact': 'தொடர்பு கொள்ளுங்கள்',
                'more_details': 'மேலும் விவரங்கள்',
                'welcome': 'அகி ரியல் எஸ்டேட்டிற்கு வரவேற்றுகிறோம்',
                'search_placeholder': 'நகரம், பகுதி, அல்லது அடையாளத்தின் மூலம் தேடுங்கள்...'
            }
        }
    
    def _initialize_language_data(self) -> Dict[Language, Dict[str, Any]]:
        """Initialize language-specific data"""
        return {
            Language.ENGLISH: {
                'name': 'English',
                'native_name': 'English',
                'direction': 'ltr',
                'date_format': 'DD/MM/YYYY',
                'number_format': '1,234.56',
                'currency_symbol': '₹'
            },
            Language.HINDI: {
                'name': 'Hindi',
                'native_name': 'हिंदी',
                'direction': 'ltr',
                'date_format': 'DD/MM/YYYY',
                'number_format': '1,234.56',
                'currency_symbol': '₹'
            },
            Language.TAMIL: {
                'name': 'Tamil',
                'native_name': 'தமிழ்',
                'direction': 'ltr',
                'date_format': 'DD/MM/YYYY',
                'number_format': '1,234.56',
                'currency_symbol': '₹'
            }
        }
    
    def get_translation(self, key: str, language: Language = Language.ENGLISH) -> str:
        """Get translation for a key in specified language"""
        lang_code = language.value
        if lang_code in self.translations and key in self.translations[lang_code]:
            return self.translations[lang_code][key]
        else:
            # Fallback to English
            return self.translations.get('en', {}).get(key, key)
    
    def get_language_for_city(self, city_name: str) -> Language:
        """Get primary language for a city"""
        cities_db = IndianCitiesDatabase()
        city = cities_db.get_city(city_name)
        
        if city:
            return city.primary_language
        
        return Language.ENGLISH  # Default fallback
    
    def format_currency(self, amount: Decimal, language: Language = Language.ENGLISH) -> str:
        """Format currency according to language conventions"""
        lang_data = self.language_data.get(language, self.language_data[Language.ENGLISH])
        symbol = lang_data['currency_symbol']
        
        # Format with Indian numbering system (lakhs, crores)
        amount_float = float(amount)
        
        if amount_float >= 10000000:  # 1 Crore
            return f"{symbol} {amount_float/10000000:.2f} Cr"
        elif amount_float >= 100000:  # 1 Lakh
            return f"{symbol} {amount_float/100000:.2f} L"
        else:
            return f"{symbol} {amount_float:,.2f}"
    
    def format_date(self, date_obj: date, language: Language = Language.ENGLISH) -> str:
        """Format date according to language conventions"""
        lang_data = self.language_data.get(language, self.language_data[Language.ENGLISH])
        date_format = lang_data['date_format']
        
        # Simple date formatting
        return date_obj.strftime('%d/%m/%Y')


class GeographicSearchEngine:
    """Advanced geographic search and filtering"""
    
    def __init__(self):
        self.cities_db = IndianCitiesDatabase()
        self.load_balancer = RegionalLoadBalancer()
        self.localization = LocalizationManager()
    
    def search_properties_by_location(self, location_query: str, 
                                     search_radius_km: int = 50) -> Dict[str, Any]:
        """
        Search properties by location with geographic intelligence
        """
        # Parse location query
        city = self.cities_db.get_city(location_query)
        
        if not city:
            return {
                'success': False,
                'message': f'City "{location_query}" not found',
                'suggestions': self._get_city_suggestions(location_query)
            }
        
        # Get nearby cities
        nearby_cities = self.cities_db.get_nearby_cities(location_query, search_radius_km)
        
        # Get optimal datacenter
        datacenter = self.load_balancer.get_optimal_datacenter(location_query)
        
        # Get language for location
        language = self.localization.get_language_for_city(location_query)
        
        return {
            'success': True,
            'primary_city': {
                'name': city.name,
                'state': city.state,
                'tier': city.tier.value,
                'coordinates': {
                    'latitude': str(city.latitude),
                    'longitude': str(city.longitude)
                },
                'avg_price_per_sqft': str(city.avg_price_per_sqft),
                'primary_language': language.value
            },
            'nearby_cities': [
                {
                    'name': nearby_city.name,
                    'distance_km': round(distance, 2),
                    'state': nearby_city.state
                }
                for nearby_city, distance in nearby_cities[:5]  # Top 5 nearby cities
            ],
            'search_region': city.region.value,
            'optimal_datacenter': datacenter,
            'total_cities_in_search': len(nearby_cities) + 1,
            'search_radius_km': search_radius_km
        }
    
    def _get_city_suggestions(self, query: str) -> List[str]:
        """Get city suggestions based on partial match"""
        query_lower = query.lower()
        suggestions = []
        
        for city_name in self.cities_db.cities.keys():
            if query_lower in city_name:
                suggestions.append(city_name.title())
        
        return suggestions[:5]  # Top 5 suggestions
    
    def compare_cities(self, city1: str, city2: str) -> Dict[str, Any]:
        """
        Compare two cities across various parameters
        """
        city1_data = self.cities_db.get_city(city1)
        city2_data = self.cities_db.get_city(city2)
        
        if not city1_data or not city2_data:
            return {
                'success': False,
                'message': 'One or both cities not found'
            }
        
        comparison = {
            'success': True,
            'cities': [
                {
                    'name': city1_data.name,
                    'tier': city1_data.tier.value,
                    'avg_price_per_sqft': str(city1_data.avg_price_per_sqft),
                    'connectivity_score': city1_data.connectivity_score,
                    'infrastructure_score': city1_data.infrastructure_score,
                    'livability_score': city1_data.livability_score
                },
                {
                    'name': city2_data.name,
                    'tier': city2_data.tier.value,
                    'avg_price_per_sqft': str(city2_data.avg_price_per_sqft),
                    'connectivity_score': city2_data.connectivity_score,
                    'infrastructure_score': city2_data.infrastructure_score,
                    'livability_score': city2_data.livability_score
                }
            ],
            'comparison': {
                'price_difference_pct': self._calculate_percentage_difference(
                    city1_data.avg_price_per_sqft, city2_data.avg_price_per_sqft
                ),
                'better_connectivity': city1_data.name if city1_data.connectivity_score > city2_data.connectivity_score else city2_data.name,
                'better_infrastructure': city1_data.name if city1_data.infrastructure_score > city2_data.infrastructure_score else city2_data.name,
                'better_livability': city1_data.name if city1_data.livability_score > city2_data.livability_score else city2_data.name
            }
        }
        
        return comparison
    
    def _calculate_percentage_difference(self, value1: Decimal, value2: Decimal) -> float:
        """Calculate percentage difference between two values"""
        if value2 == 0:
            return 0.0
        
        difference = float(value1 - value2)
        percentage = (difference / float(value2)) * 100
        return round(percentage, 2)


class PanIndiaArchitecture:
    """
    Main pan-India architecture system
    """
    
    def __init__(self):
        self.cities_db = IndianCitiesDatabase()
        self.load_balancer = RegionalLoadBalancer()
        self.localization = LocalizationManager()
        self.search_engine = GeographicSearchEngine()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status across all regions"""
        regional_status = {}
        
        for region in Region:
            status = self.load_balancer.get_server_capacity(region)
            if status:
                regional_status[region.value] = status
        
        total_capacity = sum(s['server_capacity'] for s in regional_status.values())
        total_load = sum(s['current_load'] for s in regional_status.values())
        overall_load_percentage = (total_load / total_capacity) * 100 if total_capacity > 0 else 0
        
        return {
            'system_status': 'operational',
            'overall_load_percentage': round(overall_load_percentage, 2),
            'total_cities_covered': len(self.cities_db.cities),
            'regions_active': len(regional_status),
            'regional_status': regional_status,
            'supported_languages': [lang.value for lang in Language],
            'last_updated': datetime.now().isoformat()
        }
    
    def get_city_statistics(self, city_name: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a city"""
        city = self.cities_db.get_city(city_name)
        
        if not city:
            return {
                'success': False,
                'message': f'City "{city_name}" not found'
            }
        
        region_status = self.load_balancer.get_server_capacity(city.region)
        language = self.localization.get_language_for_city(city_name)
        
        return {
            'success': True,
            'city_details': {
                'name': city.name,
                'state': city.state,
                'tier': city.tier.value,
                'region': city.region.value,
                'population': city.population,
                'coordinates': {
                    'latitude': str(city.latitude),
                    'longitude': str(city.longitude)
                }
            },
            'economic_indicators': {
                'gdp_per_capita': str(city.gdp_per_capita),
                'avg_property_price': self.localization.format_currency(city.avg_property_price, language),
                'avg_price_per_sqft': str(city.avg_price_per_sqft)
            },
            'infrastructure_scores': {
                'connectivity': city.connectivity_score,
                'infrastructure': city.infrastructure_score,
                'livability': city.livability_score
            },
            'real estate_metrics': {
                'total_properties': city.total_properties,
                'active_listings': city.active_listings,
                'market_growth_rate': city.market_growth_rate
            },
            'system_info': {
                'primary_language': language.value,
                'optimal_datacenter': self.load_balancer.get_optimal_datacenter(city_name),
                'region_status': region_status
            }
        }


# Initialize global instances
indian_cities_db = IndianCitiesDatabase()
regional_load_balancer = RegionalLoadBalancer()
localization_manager = LocalizationManager()
geographic_search_engine = GeographicSearchEngine()
pan_india_architecture = PanIndiaArchitecture()