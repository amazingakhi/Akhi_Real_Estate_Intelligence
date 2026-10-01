"""
Akhi Real Estate Intelligence - Enterprise API Platform
RESTful API with authentication, rate limiting, and comprehensive documentation
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import secrets
import hashlib
from functools import wraps


class APIVersion(Enum):
    """API version management"""
    V1 = "v1"
    V2 = "v2"
    LATEST = "v2"


class APIEndpoint(Enum):
    """API endpoint categories"""
    PROPERTIES = "properties"
    ANALYTICS = "analytics"
    INTELLIGENCE = "intelligence"
    SUBSCRIPTIONS = "subscriptions"
    USERS = "users"
    REPORTS = "reports"
    WEBHOOKS = "webhooks"


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ResponseStatus(Enum):
    """API response status codes"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class APIResponse:
    """Standard API response format"""
    
    def __init__(self, status: ResponseStatus, data: Any = None, 
                 message: str = None, errors: List[str] = None,
                 metadata: Dict[str, Any] = None):
        self.status = status.value
        self.data = data
        self.message = message
        self.errors = errors or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'status': self.status,
            'data': self.data,
            'message': self.message,
            'errors': self.errors,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert response to JSON"""
        return json.dumps(self.to_dict(), default=str)


class APIRateLimiter:
    """Advanced API rate limiting with tier-based limits"""
    
    def __init__(self):
        self.tier_limits = {
            'free': {'requests_per_minute': 10, 'requests_per_hour': 100},
            'professional': {'requests_per_minute': 30, 'requests_per_hour': 1000},
            'enterprise': {'requests_per_minute': 100, 'requests_per_hour': 10000},
            'institutional': {'requests_per_minute': 500, 'requests_per_hour': 100000}
        }
        
        self.request_history = {}  # In production, use Redis
    
    def check_rate_limit(self, api_key: str, user_tier: str = 'free') -> Dict[str, Any]:
        """
        Check if API request is within rate limits
        """
        limits = self.tier_limits.get(user_tier, self.tier_limits['free'])
        
        current_time = datetime.now()
        minute_key = current_time.strftime('%Y%m%d%H%M')
        hour_key = current_time.strftime('%Y%m%d%H')
        
        # Initialize request history if not exists
        if api_key not in self.request_history:
            self.request_history[api_key] = {}
        
        # Clean old entries
        self._clean_old_entries(api_key)
        
        # Get current request counts
        minute_count = self.request_history[api_key].get(minute_key, 0)
        hour_count = self.request_history[api_key].get(hour_key, 0)
        
        # Check limits
        minute_limit_exceeded = minute_count >= limits['requests_per_minute']
        hour_limit_exceeded = hour_count >= limits['requests_per_hour']
        
        if minute_limit_exceeded or hour_limit_exceeded:
            return {
                'allowed': False,
                'reason': 'minute_limit' if minute_limit_exceeded else 'hour_limit',
                'retry_after': self._calculate_retry_after(current_time, minute_limit_exceeded),
                'limits': limits,
                'current_usage': {
                    'minute_requests': minute_count,
                    'hour_requests': hour_count
                }
            }
        
        # Increment counters
        self.request_history[api_key][minute_key] = minute_count + 1
        self.request_history[api_key][hour_key] = hour_count + 1
        
        return {
            'allowed': True,
            'limits': limits,
            'current_usage': {
                'minute_requests': minute_count + 1,
                'hour_requests': hour_count + 1
            },
            'remaining': {
                'minute_requests': limits['requests_per_minute'] - (minute_count + 1),
                'hour_requests': limits['requests_per_hour'] - (hour_count + 1)
            }
        }
    
    def _clean_old_entries(self, api_key: str):
        """Clean old request history entries"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=1)
        
        if api_key in self.request_history:
            keys_to_remove = []
            for key in self.request_history[api_key].keys():
                try:
                    key_time = datetime.strptime(key, '%Y%m%d%H%M') if len(key) == 12 else \
                              datetime.strptime(key, '%Y%m%d%H')
                    if key_time < cutoff_time:
                        keys_to_remove.append(key)
                except ValueError:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.request_history[api_key][key]
    
    def _calculate_retry_after(self, current_time: datetime, minute_limit: bool) -> int:
        """Calculate seconds until rate limit resets"""
        if minute_limit:
            # Reset at next minute
            next_minute = (current_time.replace(second=0, microsecond=0) + 
                          timedelta(minutes=1))
            return int((next_minute - current_time).total_seconds())
        else:
            # Reset at next hour
            next_hour = (current_time.replace(minute=0, second=0, microsecond=0) + 
                         timedelta(hours=1))
            return int((next_hour - current_time).total_seconds())


class APIAuthentication:
    """API authentication and authorization"""
    
    def __init__(self):
        self.api_keys = {}  # In production, use database
    
    def register_api_key(self, user_id: str, tier: str = 'free',
                        permissions: List[str] = None) -> Dict[str, Any]:
        """Register new API key"""
        api_key = self._generate_api_key()
        api_key_hash = self._hash_api_key(api_key)
        
        api_key_data = {
            'api_key': api_key,
            'api_key_hash': api_key_hash,
            'user_id': user_id,
            'tier': tier,
            'permissions': permissions or ['read'],
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'usage_count': 0,
            'is_active': True
        }
        
        self.api_keys[api_key_hash] = api_key_data
        
        return {
            'api_key': api_key,
            'tier': tier,
            'permissions': api_key_data['permissions'],
            'created_at': api_key_data['created_at']
        }
    
    def _generate_api_key(self) -> str:
        """Generate cryptographically secure API key"""
        prefix = "akhi_"
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}{random_part}"
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate API key and return user information"""
        api_key_hash = self._hash_api_key(api_key)
        api_key_data = self.api_keys.get(api_key_hash)
        
        if not api_key_data:
            return {
                'valid': False,
                'reason': 'Invalid API key'
            }
        
        if not api_key_data['is_active']:
            return {
                'valid': False,
                'reason': 'API key is inactive'
            }
        
        # Update usage statistics
        api_key_data['last_used'] = datetime.now().isoformat()
        api_key_data['usage_count'] += 1
        
        return {
            'valid': True,
            'user_id': api_key_data['user_id'],
            'tier': api_key_data['tier'],
            'permissions': api_key_data['permissions'],
            'usage_count': api_key_data['usage_count']
        }
    
    def check_permission(self, api_key: str, required_permission: str) -> bool:
        """Check if API key has required permission"""
        validation = self.validate_api_key(api_key)
        
        if not validation['valid']:
            return False
        
        permissions = validation.get('permissions', [])
        return required_permission in permissions or 'admin' in permissions


class APIEndpointRegistry:
    """Registry for API endpoints and their metadata"""
    
    def __init__(self):
        self.endpoints = {}
        self._register_default_endpoints()
    
    def _register_default_endpoints(self):
        """Register default API endpoints"""
        
        # Property endpoints
        self.register_endpoint(
            endpoint='/properties',
            method=HTTPMethod.GET,
            description='Search properties with filters',
            parameters={
                'city': {'type': 'string', 'required': False, 'description': 'City name'},
                'min_price': {'type': 'number', 'required': False, 'description': 'Minimum price'},
                'max_price': {'type': 'number', 'required': False, 'description': 'Maximum price'},
                'bhk': {'type': 'integer', 'required': False, 'description': 'BHK count'},
                'page': {'type': 'integer', 'required': False, 'description': 'Page number'}
            },
            response={'properties': 'array', 'total': 'integer', 'page': 'integer'},
            authentication_required=True,
            rate_limit_weight=1
        )
        
        self.register_endpoint(
            endpoint='/properties/{id}',
            method=HTTPMethod.GET,
            description='Get property details by ID',
            parameters={
                'id': {'type': 'string', 'required': True, 'description': 'Property ID'}
            },
            response={'property': 'object'},
            authentication_required=True,
            rate_limit_weight=1
        )
        
        # Analytics endpoints
        self.register_endpoint(
            endpoint='/analytics/market-trends',
            method=HTTPMethod.GET,
            description='Get market trend analysis',
            parameters={
                'city': {'type': 'string', 'required': True, 'description': 'City name'},
                'period': {'type': 'string', 'required': False, 'description': 'Time period (6m, 1y, 2y)'}
            },
            response={'trend': 'string', 'data': 'array'},
            authentication_required=True,
            required_permission='analytics',
            rate_limit_weight=2
        )
        
        # Intelligence endpoints
        self.register_endpoint(
            endpoint='/intelligence/price-prediction',
            method=HTTPMethod.POST,
            description='Get AI-powered price prediction',
            parameters={
                'area_sqft': {'type': 'number', 'required': True},
                'bhk_count': {'type': 'integer', 'required': True},
                'locality': {'type': 'string', 'required': True},
                'property_type': {'type': 'string', 'required': True}
            },
            response={'predicted_price': 'number', 'confidence': 'number'},
            authentication_required=True,
            required_permission='intelligence',
            rate_limit_weight=3
        )
        
        # Subscription endpoints
        self.register_endpoint(
            endpoint='/subscriptions',
            method=HTTPMethod.GET,
            description='Get user subscription details',
            parameters={},
            response={'subscription': 'object'},
            authentication_required=True,
            rate_limit_weight=1
        )
    
    def register_endpoint(self, endpoint: str, method: HTTPMethod, 
                        description: str, parameters: Dict[str, Dict],
                        response: Dict[str, str], 
                        authentication_required: bool = True,
                        required_permission: str = None,
                        rate_limit_weight: int = 1):
        """Register a new API endpoint"""
        endpoint_key = f"{method.value} {endpoint}"
        
        self.endpoints[endpoint_key] = {
            'endpoint': endpoint,
            'method': method.value,
            'description': description,
            'parameters': parameters,
            'response': response,
            'authentication_required': authentication_required,
            'required_permission': required_permission,
            'rate_limit_weight': rate_limit_weight,
            'registered_at': datetime.now().isoformat()
        }
    
    def get_endpoint(self, method: HTTPMethod, endpoint: str) -> Optional[Dict]:
        """Get endpoint metadata"""
        endpoint_key = f"{method.value} {endpoint}"
        return self.endpoints.get(endpoint_key)
    
    def get_all_endpoints(self) -> List[Dict]:
        """Get all registered endpoints"""
        return list(self.endpoints.values())


class APIRequest:
    """API request representation"""
    
    def __init__(self, method: HTTPMethod, endpoint: str, 
                 headers: Dict[str, str] = None, 
                 parameters: Dict[str, Any] = None,
                 body: Dict[str, Any] = None,
                 api_key: str = None):
        self.method = method
        self.endpoint = endpoint
        self.headers = headers or {}
        self.parameters = parameters or {}
        self.body = body or {}
        self.api_key = api_key
        self.timestamp = datetime.now()
        self.client_ip = headers.get('X-Forwarded-For', 'unknown')
        self.user_agent = headers.get('User-Agent', 'unknown')


class APIGateway:
    """Main API gateway handling requests, authentication, and routing"""
    
    def __init__(self):
        self.authentication = APIAuthentication()
        self.rate_limiter = APIRateLimiter()
        self.endpoint_registry = APIEndpointRegistry()
        self.request_handlers = {}
        self._register_request_handlers()
    
    def _register_request_handlers(self):
        """Register request handlers for endpoints"""
        
        # Property handlers
        self.request_handlers[('GET', '/properties')] = self._handle_search_properties
        self.request_handlers[('GET', '/properties/{id}')] = self._handle_get_property
        
        # Analytics handlers
        self.request_handlers[('GET', '/analytics/market-trends')] = self._handle_market_trends
        
        # Intelligence handlers
        self.request_handlers[('POST', '/intelligence/price-prediction')] = self._handle_price_prediction
        
        # Subscription handlers
        self.request_handlers[('GET', '/subscriptions')] = self._handle_get_subscription
    
    def handle_request(self, request: APIRequest) -> APIResponse:
        """
        Handle incoming API request
        """
        try:
            # Get endpoint metadata
            endpoint_metadata = self.endpoint_registry.get_endpoint(
                request.method, 
                request.endpoint
            )
            
            if not endpoint_metadata:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message="Endpoint not found",
                    errors=["404 - Endpoint not found"]
                )
            
            # Check authentication
            if endpoint_metadata['authentication_required']:
                auth_result = self.authentication.validate_api_key(request.api_key)
                if not auth_result['valid']:
                    return APIResponse(
                        status=ResponseStatus.ERROR,
                        message="Authentication failed",
                        errors=[auth_result['reason']]
                    )
                
                # Check permissions
                required_permission = endpoint_metadata.get('required_permission')
                if required_permission:
                    if not self.authentication.check_permission(request.api_key, required_permission):
                        return APIResponse(
                            status=ResponseStatus.ERROR,
                            message="Permission denied",
                            errors=[f"Missing required permission: {required_permission}"]
                        )
                
                user_tier = auth_result['tier']
            else:
                user_tier = 'free'
            
            # Check rate limits
            rate_limit_result = self.rate_limiter.check_rate_limit(
                request.api_key or 'anonymous', 
                user_tier
            )
            
            if not rate_limit_result['allowed']:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message="Rate limit exceeded",
                    errors=[f"Rate limit exceeded: {rate_limit_result['reason']}"],
                    metadata={
                        'retry_after': rate_limit_result['retry_after'],
                        'limits': rate_limit_result['limits']
                    }
                )
            
            # Route to handler
            handler_key = (request.method.value, request.endpoint)
            handler = self.request_handlers.get(handler_key)
            
            if handler:
                response_data = handler(request, endpoint_metadata)
                return APIResponse(
                    status=ResponseStatus.SUCCESS,
                    data=response_data,
                    metadata={
                        'rate_limit': rate_limit_result,
                        'processing_time_ms': 0  # Would be calculated in production
                    }
                )
            else:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message="Handler not implemented",
                    errors=["501 - Not Implemented"]
                )
        
        except Exception as e:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Internal server error",
                errors=[str(e)]
            )
    
    def _handle_search_properties(self, request: APIRequest, 
                                 endpoint_metadata: Dict) -> Dict[str, Any]:
        """Handle property search request"""
        # In production, this would query the database
        city = request.parameters.get('city', 'gurugram')
        min_price = request.parameters.get('min_price')
        max_price = request.parameters.get('max_price')
        bhk = request.parameters.get('bhk')
        page = int(request.parameters.get('page', 1))
        
        # Mock response data
        properties = [
            {
                'id': f'PROP-{i}',
                'title': f'{bhk or 3} BHK Apartment in {city.title()}',
                'price': f'{random.randint(50, 150)} Lakhs',
                'area_sqft': random.randint(1000, 2500),
                'locality': f'Sector {random.randint(1, 60)}',
                'bhk': bhk or 3,
                'city': city
            }
            for i in range(1, 11)
        ]
        
        return {
            'properties': properties,
            'total': 100,
            'page': page,
            'per_page': 10,
            'filters_applied': {
                'city': city,
                'min_price': min_price,
                'max_price': max_price,
                'bhk': bhk
            }
        }
    
    def _handle_get_property(self, request: APIRequest, 
                           endpoint_metadata: Dict) -> Dict[str, Any]:
        """Handle get property details request"""
        property_id = request.parameters.get('id', 'PROP-1')
        
        # Mock property data
        property_data = {
            'id': property_id,
            'title': 'Luxury 3 BHK Apartment',
            'price': '85 Lakhs',
            'area_sqft': 1800,
            'locality': 'Sector 56',
            'city': 'Gurugram',
            'bhk': 3,
            'bathrooms': 2,
            'furnishing': 'semi-furnished',
            'possession': 'ready_to_move',
            'amenities': ['parking', 'gym', 'pool', 'security'],
            'images': [f'image_{i}.jpg' for i in range(1, 6)]
        }
        
        return property_data
    
    def _handle_market_trends(self, request: APIRequest, 
                              endpoint_metadata: Dict) -> Dict[str, Any]:
        """Handle market trends request"""
        city = request.parameters.get('city', 'gurugram')
        period = request.parameters.get('period', '6m')
        
        # Mock trend data
        trend_data = {
            'city': city,
            'period': period,
            'trend': 'bullish',
            'price_change_percentage': 8.5,
            'volume_change_percentage': 12.3,
            'current_avg_price_per_sqft': 7500,
            'forecast': [
                {'month': 'Month +1', 'forecasted_price': 7650},
                {'month': 'Month +2', 'forecasted_price': 7800},
                {'month': 'Month +3', 'forecasted_price': 7950}
            ]
        }
        
        return trend_data
    
    def _handle_price_prediction(self, request: APIRequest, 
                                endpoint_metadata: Dict) -> Dict[str, Any]:
        """Handle price prediction request"""
        body = request.body
        
        # Mock prediction (in production, use actual ML model)
        area_sqft = body.get('area_sqft', 1500)
        bhk_count = body.get('bhk_count', 3)
        locality = body.get('locality', 'Sector 56')
        property_type = body.get('property_type', 'apartment')
        
        base_price = area_sqft * 7500
        predicted_price = base_price * (1 + (bhk_count * 0.1))
        
        prediction_data = {
            'property_features': {
                'area_sqft': area_sqft,
                'bhk_count': bhk_count,
                'locality': locality,
                'property_type': property_type
            },
            'predicted_price': round(predicted_price, -3),
            'price_per_sqft': round(predicted_price / area_sqft, 0),
            'confidence': 0.87,
            'model_used': 'ensemble',
            'prediction_range': {
                'min': round(predicted_price * 0.9, -3),
                'max': round(predicted_price * 1.1, -3)
            }
        }
        
        return prediction_data
    
    def _handle_get_subscription(self, request: APIRequest, 
                                endpoint_metadata: Dict) -> Dict[str, Any]:
        """Handle get subscription request"""
        # Mock subscription data
        subscription_data = {
            'plan': 'professional',
            'status': 'active',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'features': [
                'Unlimited property search',
                'Advanced analytics',
                '10,000 API calls/month'
            ],
            'usage': {
                'api_calls_this_month': 1234,
                'api_calls_limit': 10000
            }
        }
        
        return subscription_data


class APIDocumentationGenerator:
    """Generate API documentation in multiple formats"""
    
    def __init__(self, endpoint_registry: APIEndpointRegistry):
        self.endpoint_registry = endpoint_registry
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI/Swagger specification"""
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Akhi Real Estate Intelligence API',
                'version': '2.0.0',
                'description': 'Enterprise-grade real estate analytics and intelligence API',
                'contact': {
                    'name': 'API Support',
                    'email': 'api@akhiproperties.com'
                }
            },
            'servers': [
                {
                    'url': 'https://api.akhiproperties.com/v2',
                    'description': 'Production server'
                },
                {
                    'url': 'https://api-staging.akhiproperties.com/v2',
                    'description': 'Staging server'
                }
            ],
            'security': [
                {
                    'ApiKeyAuth': []
                }
            ],
            'components': {
                'securitySchemes': {
                    'ApiKeyAuth': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-API-Key',
                        'description': 'API key for authentication'
                    }
                },
                'schemas': {
                    'Error': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'message': {'type': 'string'},
                            'errors': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    },
                    'Property': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'title': {'type': 'string'},
                            'price': {'type': 'string'},
                            'area_sqft': {'type': 'integer'},
                            'locality': {'type': 'string'},
                            'city': {'type': 'string'}
                        }
                    }
                }
            },
            'paths': {}
        }
        
        # Add endpoints to paths
        for endpoint_data in self.endpoint_registry.get_all_endpoints():
            path = endpoint_data['endpoint']
            method = endpoint_data['method'].lower()
            
            if path not in spec['paths']:
                spec['paths'][path] = {}
            
            spec['paths'][path][method] = {
                'summary': endpoint_data['description'],
                'operationId': f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
                'parameters': [
                    {
                        'name': param_name,
                        'in': 'query',
                        'required': param_data['required'],
                        'description': param_data['description'],
                        'schema': {'type': param_data['type']}
                    }
                    for param_name, param_data in endpoint_data['parameters'].items()
                ],
                'responses': {
                    '200': {
                        'description': 'Success',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': endpoint_data['response']
                                }
                            }
                        }
                    },
                    '401': {
                        'description': 'Unauthorized',
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/Error'}
                            }
                        }
                    },
                    '429': {
                        'description': 'Rate Limit Exceeded',
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/Error'}
                            }
                        }
                    }
                }
            }
        
        return spec
    
    def generate_markdown_documentation(self) -> str:
        """Generate Markdown documentation"""
        openapi_spec = self.generate_openapi_spec()
        
        markdown = f"""# {openapi_spec['info']['title']}

{openapi_spec['info']['description']}

**Version:** {openapi_spec['info']['version']}

## Authentication

All API requests require authentication using an API key in the header:
```
X-API-Key: your_api_key_here
```

## Rate Limits

API rate limits are based on your subscription tier:
- **Free**: 100 requests/hour
- **Professional**: 1,000 requests/hour  
- **Enterprise**: 10,000 requests/hour
- **Institutional**: 100,000 requests/hour

## Endpoints

"""
        
        # Add endpoint documentation
        for endpoint_data in self.endpoint_registry.get_all_endpoints():
            method = endpoint_data['method'].upper()
            path = endpoint_data['endpoint']
            description = endpoint_data['description']
            
            markdown += f"### {method} {path}\n\n"
            markdown += f"{description}\n\n"
            
            if endpoint_data['parameters']:
                markdown += "**Parameters:**\n\n"
                markdown += "| Parameter | Type | Required | Description |\n"
                markdown += "|-----------|------|----------|-------------|\n"
                
                for param_name, param_data in endpoint_data['parameters'].items():
                    required = "Yes" if param_data['required'] else "No"
                    markdown += f"| {param_name} | {param_data['type']} | {required} | {param_data['description']} |\n"
                
                markdown += "\n"
            
            markdown += "**Response:**\n\n"
            markdown += f"```json\n{json.dumps(endpoint_data['response'], indent=2)}\n```\n\n"
            markdown += "---\n\n"
        
        # Add error codes
        markdown += """## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Support

For API support, contact: api@akhiproperties.com
"""
        
        return markdown


class EnterpriseAPIPlatform:
    """
    Main enterprise API platform
    """
    
    def __init__(self):
        self.gateway = APIGateway()
        self.documentation_generator = APIDocumentationGenerator(self.gateway.endpoint_registry)
    
    def register_client(self, user_id: str, tier: str = 'free',
                      permissions: List[str] = None) -> Dict[str, Any]:
        """Register new API client"""
        return self.gateway.authentication.register_api_key(user_id, tier, permissions)
    
    def process_request(self, method: str, endpoint: str, 
                       headers: Dict[str, str] = None,
                       parameters: Dict[str, Any] = None,
                       body: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process API request"""
        http_method = HTTPMethod(method.upper())
        api_key = headers.get('X-API-Key') if headers else None
        
        request = APIRequest(
            method=http_method,
            endpoint=endpoint,
            headers=headers or {},
            parameters=parameters or {},
            body=body or {},
            api_key=api_key
        )
        
        response = self.gateway.handle_request(request)
        return response.to_dict()
    
    def get_api_documentation(self, format: str = 'json') -> str:
        """Get API documentation in specified format"""
        if format == 'json':
            return json.dumps(self.documentation_generator.generate_openapi_spec(), indent=2)
        elif format == 'markdown':
            return self.documentation_generator.generate_markdown_documentation()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get API platform status"""
        return {
            'platform_status': 'operational',
            'version': '2.0.0',
            'endpoints_registered': len(self.gateway.endpoint_registry.get_all_endpoints()),
            'active_api_keys': len(self.gateway.authentication.api_keys),
            'rate_limit_status': 'active',
            'uptime_percentage': 99.9,
            'last_updated': datetime.now().isoformat()
        }


# Initialize global instances
api_gateway = APIGateway()
api_documentation_generator = APIDocumentationGenerator(api_gateway.endpoint_registry)
enterprise_api_platform = EnterpriseAPIPlatform()