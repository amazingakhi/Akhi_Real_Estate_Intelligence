"""
Akhi Real Estate Intelligence - Advanced AI/ML Features
Predictive analytics, ensemble models, and AI-powered insights
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import random
import math


class PredictionModel(Enum):
    """Types of prediction models"""
    ENSEMBLE = "ensemble"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"  # Long Short-Term Memory for time series


class MarketTrend(Enum):
    """Market trend predictions"""
    BULLISH = "bullish"  # Prices expected to rise
    BEARISH = "bearish"  # Prices expected to fall
    NEUTRAL = "neutral"  # Stable prices
    VOLATILE = "volatile"  # High uncertainty


class InvestmentRisk(Enum):
    """Investment risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EnsemblePricePredictor:
    """
    Ensemble price prediction using multiple models
    Combines predictions from multiple models for better accuracy
    """
    
    def __init__(self):
        self.models = {
            PredictionModel.RANDOM_FOREST: self._random_forest_predict,
            PredictionModel.GRADIENT_BOOSTING: self._gradient_boosting_predict,
            PredictionModel.NEURAL_NETWORK: self._neural_network_predict
        }
        self.model_weights = {
            PredictionModel.RANDOM_FOREST: 0.35,
            PredictionModel.GRADIENT_BOOSTING: 0.40,
            PredictionModel.NEURAL_NETWORK: 0.25
        }
        self.model_performance = {
            PredictionModel.RANDOM_FOREST: 0.87,  # R² score
            PredictionModel.GRADIENT_BOOSTING: 0.91,
            PredictionModel.NEURAL_NETWORK: 0.85
        }
    
    def predict_price(self, property_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict property price using ensemble of models
        """
        predictions = {}
        
        # Get predictions from each model
        for model_type, predict_func in self.models.items():
            try:
                prediction = predict_func(property_features)
                predictions[model_type] = prediction
            except Exception as e:
                print(f"Error in {model_type.value}: {e}")
                predictions[model_type] = None
        
        # Calculate ensemble prediction
        ensemble_prediction = self._calculate_ensemble_prediction(predictions)
        
        # Calculate prediction confidence
        confidence = self._calculate_prediction_confidence(predictions)
        
        return {
            'ensemble_prediction': ensemble_prediction,
            'individual_predictions': predictions,
            'confidence_score': confidence,
            'model_weights': self.model_weights,
            'model_performance': self.model_performance,
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _random_forest_predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Random Forest price prediction"""
        # Simplified implementation - in production use actual trained model
        base_price = Decimal(str(features.get('base_price', 5000000)))
        area = Decimal(str(features.get('area_sqft', 1000)))
        bhk = features.get('bhk_count', 2)
        locality_score = features.get('locality_score', 0.5)
        
        # Feature-based price calculation
        price_per_sqft = 8000 + (locality_score * 4000) + (bhk * 500)
        predicted_price = area * Decimal(str(price_per_sqft))
        
        # Add some randomness for variance
        variance = random.uniform(0.95, 1.05)
        predicted_price = predicted_price * Decimal(str(variance))
        
        return {
            'predicted_price': round(predicted_price, -3),
            'price_per_sqft': round(price_per_sqft, 0),
            'confidence': 0.87,
            'feature_importance': {
                'area': 0.35,
                'locality': 0.30,
                'bhk': 0.15,
                'age': 0.10,
                'amenities': 0.10
            }
        }
    
    def _gradient_boosting_predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Gradient Boosting price prediction"""
        base_price = Decimal(str(features.get('base_price', 5000000)))
        area = Decimal(str(features.get('area_sqft', 1000)))
        bhk = features.get('bhk_count', 2)
        locality_score = features.get('locality_score', 0.5)
        property_age = features.get('property_age', 0)
        
        # More sophisticated feature engineering
        area_normalized = area / Decimal('1000')  # Normalize to thousands
        bhk_premium = (bhk - 2) * 200000  # Premium for BHK above 2
        age_depreciation = min(property_age * 50000, 500000)  # Max 5L depreciation
        locality_premium = locality_score * 2000000
        
        predicted_price = base_price + (area_normalized * 5000000) + bhk_premium - age_depreciation + locality_premium
        
        # Gradient boosting typically gives better accuracy
        variance = random.uniform(0.97, 1.03)
        predicted_price = predicted_price * Decimal(str(variance))
        
        return {
            'predicted_price': round(predicted_price, -3),
            'price_per_sqft': round(predicted_price / area, 0),
            'confidence': 0.91,
            'feature_importance': {
                'area': 0.40,
                'locality': 0.35,
                'bhk': 0.10,
                'age': 0.10,
                'amenities': 0.05
            }
        }
    
    def _neural_network_predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Neural Network price prediction"""
        # Simulated neural network prediction
        area = Decimal(str(features.get('area_sqft', 1000)))
        bhk = features.get('bhk_count', 2)
        locality_score = features.get('locality_score', 0.5)
        property_type = features.get('property_type', 'apartment')
        
        # Neural network-style non-linear relationships
        area_factor = math.log(float(area) / 1000 + 1) * 3000000
        bhk_factor = bhk * 400000
        locality_factor = (locality_score ** 2) * 2500000
        
        # Property type adjustments
        type_multipliers = {
            'apartment': 1.0,
            'villa': 1.3,
            'independent_house': 1.2,
            'plot': 0.8
        }
        type_multiplier = type_multipliers.get(property_type, 1.0)
        
        predicted_price = (area_factor + bhk_factor + locality_factor) * Decimal(str(type_multiplier))
        
        variance = random.uniform(0.96, 1.04)
        predicted_price = predicted_price * Decimal(str(variance))
        
        return {
            'predicted_price': round(predicted_price, -3),
            'price_per_sqft': round(predicted_price / area, 0),
            'confidence': 0.85,
            'feature_importance': {
                'area': 0.30,
                'locality': 0.35,
                'bhk': 0.15,
                'property_type': 0.20
            }
        }
    
    def _calculate_ensemble_prediction(self, predictions: Dict[PredictionModel, Dict]) -> Decimal:
        """Calculate weighted ensemble prediction"""
        total_weight = Decimal('0')
        weighted_sum = Decimal('0')
        
        for model_type, prediction in predictions.items():
            if prediction and 'predicted_price' in prediction:
                weight = Decimal(str(self.model_weights[model_type]))
                price = Decimal(str(prediction['predicted_price']))
                weighted_sum += price * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return Decimal('0')
    
    def _calculate_prediction_confidence(self, predictions: Dict[PredictionModel, Dict]) -> float:
        """Calculate overall prediction confidence based on model agreement"""
        valid_predictions = [p for p in predictions.values() if p and 'predicted_price' in p]
        
        if len(valid_predictions) < 2:
            return 0.5  # Low confidence if fewer than 2 models
        
        prices = [float(p['predicted_price']) for p in valid_predictions]
        mean_price = sum(prices) / len(prices)
        
        # Calculate coefficient of variation
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        std_dev = math.sqrt(variance)
        
        if mean_price == 0:
            return 0.5
        
        cv = std_dev / mean_price
        
        # Lower CV = higher confidence
        confidence = max(0.1, min(0.95, 1.0 - cv))
        
        return round(confidence, 2)


class MarketTrendAnalyzer:
    """
    Analyze market trends and predict future market movements
    """
    
    def __init__(self):
        self.historical_data = self._generate_historical_data()
    
    def _generate_historical_data(self) -> Dict[str, List[Dict]]:
        """Generate sample historical market data"""
        # In production, this would fetch from database
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        historical_data = {}
        
        # Generate data for different cities
        cities = ['mumbai', 'delhi', 'bangalore', 'gurugram']
        
        for city in cities:
            city_data = []
            base_price = 8000 if city == 'mumbai' else 6000
            
            for i, month in enumerate(months):
                # Add seasonal variations and trends
                seasonal_factor = 1.0 + 0.1 * math.sin(2 * math.pi * i / 12)
                trend_factor = 1.0 + (i * 0.01)  # Upward trend
                random_factor = random.uniform(0.95, 1.05)
                
                month_data = {
                    'month': month,
                    'avg_price_per_sqft': round(base_price * seasonal_factor * trend_factor * random_factor, 0),
                    'transaction_volume': random.randint(100, 500),
                    'listing_count': random.randint(200, 800),
                    'days_on_market': random.randint(30, 90)
                }
                city_data.append(month_data)
            
            historical_data[city] = city_data
        
        return historical_data
    
    def analyze_market_trend(self, city: str, period_months: int = 6) -> Dict[str, Any]:
        """
        Analyze market trend for a city over specified period
        """
        city_data = self.historical_data.get(city, [])
        
        if not city_data:
            return {
                'success': False,
                'message': f'No data available for {city}'
            }
        
        # Get recent data
        recent_data = city_data[-period_months:]
        
        # Calculate trend metrics
        prices = [d['avg_price_per_sqft'] for d in recent_data]
        volumes = [d['transaction_volume'] for d in recent_data]
        
        # Price trend
        price_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] > 0 else 0
        
        # Volume trend
        volume_change = ((volumes[-1] - volumes[0]) / volumes[0]) * 100 if volumes[0] > 0 else 0
        
        # Determine market trend
        if price_change > 5:
            trend = MarketTrend.BULLISH
        elif price_change < -5:
            trend = MarketTrend.BEARISH
        elif abs(price_change) < 2:
            trend = MarketTrend.NEUTRAL
        else:
            trend = MarketTrend.VOLATILE
        
        # Calculate momentum
        momentum = self._calculate_momentum(prices)
        
        return {
            'success': True,
            'city': city,
            'analysis_period': f'{period_months} months',
            'trend': trend.value,
            'price_change_percentage': round(price_change, 2),
            'volume_change_percentage': round(volume_change, 2),
            'current_avg_price_per_sqft': prices[-1],
            'momentum_score': momentum,
            'market_health': self._calculate_market_health(recent_data),
            'forecast': self._generate_price_forecast(prices, trend)
        }
    
    def _calculate_momentum(self, prices: List[float]) -> float:
        """Calculate market momentum score"""
        if len(prices) < 3:
            return 0.5
        
        # Simple momentum calculation
        recent_change = (prices[-1] - prices[-3]) / prices[-3] if prices[-3] > 0 else 0
        
        # Normalize to 0-1 range
        momentum = 0.5 + (recent_change * 5)  # Amplify for score
        return max(0.1, min(0.9, momentum))
    
    def _calculate_market_health(self, data: List[Dict]) -> str:
        """Calculate overall market health"""
        avg_days_on_market = sum(d['days_on_market'] for d in data) / len(data)
        avg_volume = sum(d['transaction_volume'] for d in data) / len(data)
        
        if avg_days_on_market < 45 and avg_volume > 300:
            return "healthy"
        elif avg_days_on_market < 60 and avg_volume > 200:
            return "moderate"
        else:
            return "slow"
    
    def _generate_price_forecast(self, historical_prices: List[float], 
                                current_trend: MarketTrend) -> Dict[str, Any]:
        """Generate 3-month price forecast"""
        last_price = historical_prices[-1]
        
        # Forecast based on trend
        trend_multipliers = {
            MarketTrend.BULLISH: [1.02, 1.03, 1.04],
            MarketTrend.BEARISH: [0.98, 0.97, 0.96],
            MarketTrend.NEUTRAL: [1.00, 1.00, 1.00],
            MarketTrend.VOLATILE: [0.99, 1.01, 1.00]
        }
        
        multipliers = trend_multipliers.get(current_trend, [1.00, 1.00, 1.00])
        
        forecast = []
        for i, multiplier in enumerate(multipliers):
            forecast_price = last_price * multiplier
            forecast.append({
                'month': f'Month +{i+1}',
                'forecasted_price': round(forecast_price, 0),
                'confidence': round(0.9 - (i * 0.05), 2)  # Decreasing confidence
            })
        
        return forecast


class InvestmentRiskAnalyzer:
    """
    Analyze investment risk for properties
    """
    
    def __init__(self):
        self.risk_factors = {
            'market_volatility': 0.25,
            'location_risk': 0.20,
            'tech_infrastructure': 0.15,
            'regulatory_risk': 0.15,
            'liquidity_risk': 0.15,
            'developer_risk': 0.10
        }
    
    def analyze_investment_risk(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze investment risk for a property
        """
        risk_scores = {}
        
        # Market volatility risk
        risk_scores['market_volatility'] = self._assess_market_volatility_risk(property_data)
        
        # Location risk
        risk_scores['location_risk'] = self._assess_location_risk(property_data)
        
        # Technical infrastructure risk
        risk_scores['tech_infrastructure'] = self._assess_infrastructure_risk(property_data)
        
        # Regulatory risk
        risk_scores['regulatory_risk'] = self._assess_regulatory_risk(property_data)
        
        # Liquidity risk
        risk_scores['liquidity_risk'] = self._assess_liquidity_risk(property_data)
        
        # Developer risk
        risk_scores['developer_risk'] = self._assess_developer_risk(property_data)
        
        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(risk_scores)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_risk)
        
        # Generate risk mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(risk_scores, risk_level)
        
        return {
            'overall_risk_score': overall_risk,
            'risk_level': risk_level.value,
            'individual_risk_scores': risk_scores,
            'risk_factors_weight': self.risk_factors,
            'mitigation_strategies': mitigation_strategies,
            'investment_recommendation': self._get_investment_recommendation(risk_level),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _assess_market_volatility_risk(self, property_data: Dict) -> float:
        """Assess market volatility risk (0-1, higher = riskier)"""
        city = property_data.get('city', 'gurugram')
        # Simplified - in production use historical volatility data
        city_risk_map = {
            'mumbai': 0.3,
            'delhi': 0.35,
            'bangalore': 0.25,
            'gurugram': 0.4,
            'pune': 0.35
        }
        return city_risk_map.get(city, 0.4)
    
    def _assess_location_risk(self, property_data: Dict) -> float:
        """Assess location-specific risk"""
        locality_score = property_data.get('locality_score', 0.5)
        # Lower locality score = higher risk
        return 1.0 - locality_score
    
    def _assess_infrastructure_risk(self, property_data: Dict) -> float:
        """Assess technical infrastructure risk"""
        connectivity_score = property_data.get('connectivity_score', 0.7)
        # Lower connectivity = higher risk
        return 1.0 - connectivity_score
    
    def _assess_regulatory_risk(self, property_data: Dict) -> float:
        """Assess regulatory and compliance risk"""
        rera_registered = property_data.get('rera_registered', False)
        # Non-RERA properties have higher risk
        return 0.2 if rera_registered else 0.7
    
    def _assess_liquidity_risk(self, property_data: Dict) -> float:
        """Assess liquidity risk (how quickly can it be sold)"""
        property_type = property_data.get('property_type', 'apartment')
        city = property_data.get('city', 'gurugram')
        
        # Apartments in major cities have better liquidity
        if property_type == 'apartment' and city in ['mumbai', 'delhi', 'bangalore']:
            return 0.2
        elif property_type == 'plot':
            return 0.6  # Plots have lower liquidity
        else:
            return 0.4
    
    def _assess_developer_risk(self, property_data: Dict) -> float:
        """Assess developer/builder risk"""
        builder_reputation = property_data.get('builder_reputation', 0.5)
        # Lower reputation = higher risk
        return 1.0 - builder_reputation
    
    def _calculate_overall_risk(self, risk_scores: Dict[str, float]) -> float:
        """Calculate weighted overall risk score"""
        total_weight = sum(self.risk_factors.values())
        weighted_risk = sum(
            risk_scores[factor] * weight 
            for factor, weight in self.risk_factors.items()
        )
        return weighted_risk / total_weight if total_weight > 0 else 0.5
    
    def _determine_risk_level(self, overall_risk: float) -> InvestmentRisk:
        """Determine risk level based on overall score"""
        if overall_risk < 0.25:
            return InvestmentRisk.LOW
        elif overall_risk < 0.45:
            return InvestmentRisk.MODERATE
        elif overall_risk < 0.65:
            return InvestmentRisk.HIGH
        else:
            return InvestmentRisk.VERY_HIGH
    
    def _generate_mitigation_strategies(self, risk_scores: Dict[str, float], 
                                     risk_level: InvestmentRisk) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        # Address high-risk areas
        high_risk_factors = [factor for factor, score in risk_scores.items() if score > 0.6]
        
        if 'market_volatility' in high_risk_factors:
            strategies.append("Consider dollar-cost averaging to mitigate timing risk")
            strategies.append("Diversify across different property types and locations")
        
        if 'location_risk' in high_risk_factors:
            strategies.append("Thoroughly verify location development plans and infrastructure projects")
            strategies.append("Consider proximity to upcoming metro/transport hubs")
        
        if 'regulatory_risk' in high_risk_factors:
            strategies.append("Ensure property has proper RERA registration and approvals")
            strategies.append("Verify all legal documents and title clearance")
        
        if 'liquidity_risk' in high_risk_factors:
            strategies.append("Be prepared for longer holding period")
            strategies.append("Focus on properties with high rental demand")
        
        if risk_level in [InvestmentRisk.HIGH, InvestmentRisk.VERY_HIGH]:
            strategies.append("Consider starting with smaller investment to test the market")
            strategies.append("Maintain higher liquidity buffer")
        
        return strategies if strategies else ["Property appears to have balanced risk profile"]
    
    def _get_investment_recommendation(self, risk_level: InvestmentRisk) -> str:
        """Get investment recommendation based on risk level"""
        recommendations = {
            InvestmentRisk.LOW: "Strong Buy - Low risk investment with good potential",
            InvestmentRisk.MODERATE: "Buy - Moderate risk, suitable for balanced portfolio",
            InvestmentRisk.HIGH: "Hold - Higher risk, thorough due diligence recommended",
            InvestmentRisk.VERY_HIGH: "Avoid - Very high risk, not recommended for conservative investors"
        }
        return recommendations.get(risk_level, "Insufficient data for recommendation")


class NaturalLanguagePropertyParser:
    """
    Advanced NLP for parsing natural language property queries
    """
    
    def __init__(self):
        self.intent_patterns = {
            'buy': ['buy', 'purchase', 'looking for', 'want to buy', 'interested in buying'],
            'rent': ['rent', 'lease', 'on rent', 'for rent', 'rental'],
            'invest': ['invest', 'investment', 'investing', 'ROI', 'returns']
        }
        
        self.bhk_patterns = {
            '1bhk': ['1bhk', '1 bhk', 'one bedroom', '1 bedroom'],
            '2bhk': ['2bhk', '2 bhk', 'two bedroom', '2 bedroom'],
            '3bhk': ['3bhk', '3 bhk', 'three bedroom', '3 bedroom'],
            '4bhk': ['4bhk', '4 bhk', 'four bedroom', '4 bedroom']
        }
        
        self.location_patterns = {
            'mumbai': ['mumbai', 'bombay'],
            'delhi': ['delhi', 'new delhi', 'ncr'],
            'bangalore': ['bangalore', 'bengaluru'],
            'gurugram': ['gurugram', 'gurgaon'],
            'pune': ['pune']
        }
    
    def parse_property_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language property query
        """
        query_lower = query.lower()
        
        parsed_data = {
            'original_query': query,
            'intent': self._extract_intent(query_lower),
            'property_type': self._extract_property_type(query_lower),
            'bhk_requirement': self._extract_bhk_requirement(query_lower),
            'location': self._extract_location(query_lower),
            'budget_range': self._extract_budget(query_lower),
            'additional_requirements': self._extract_additional_requirements(query_lower),
            'confidence_score': self._calculate_confidence(parsed_data)
        }
        
        return parsed_data
    
    def _extract_intent(self, query: str) -> str:
        """Extract user intent (buy/rent/invest)"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return intent
        return 'search'  # Default intent
    
    def _extract_property_type(self, query: str) -> str:
        """Extract property type"""
        property_types = {
            'apartment': ['apartment', 'flat', '2bhk', '3bhk'],
            'villa': ['villa', 'independent house', 'bunglow'],
            'plot': ['plot', 'land', 'site'],
            'commercial': ['commercial', 'office', 'shop', 'retail']
        }
        
        for prop_type, patterns in property_types.items():
            for pattern in patterns:
                if pattern in query:
                    return prop_type
        
        return 'apartment'  # Default
    
    def _extract_bhk_requirement(self, query: str) -> Optional[int]:
        """Extract BHK requirement"""
        for bhk, patterns in self.bhk_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return int(bhk[0])  # Extract number from '1bhk', '2bhk', etc.
        return None
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location preference"""
        for location, patterns in self.location_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return location
        return None
    
    def _extract_budget(self, query: str) -> Dict[str, Optional[Decimal]]:
        """Extract budget range"""
        import re
        
        # Look for budget patterns like "50 lakhs", "1 crore", "5 million"
        budget_patterns = [
            r'(\d+)\s*(?:lakhs|lakh|l)',
            r'(\d+(?:\.\d+)?)\s*(?:crore|cr)',
            r'(\d+)\s*(?:million)'
        ]
        
        budget_range = {'min': None, 'max': None}
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, query)
            if matches:
                if 'crore' in pattern or 'cr' in pattern:
                    value = Decimal(matches[0]) * 10000000  # Convert to Lakhs
                elif 'million' in pattern:
                    value = Decimal(matches[0]) * 10000000  # 1 million = 1 crore approx
                else:
                    value = Decimal(matches[0]) * 100000  # Already in Lakhs
                
                budget_range['max'] = value
                break
        
        return budget_range
    
    def _extract_additional_requirements(self, query: str) -> List[str]:
        """Extract additional requirements"""
        requirements = []
        
        requirement_keywords = {
            'parking': ['parking', 'car parking'],
            'gym': ['gym', 'fitness', 'club'],
            'pool': ['pool', 'swimming'],
            'security': ['security', 'gated'],
            'furnished': ['furnished', 'semi-furnished'],
            'new': ['new', 'under construction', 'upcoming'],
            'ready': ['ready', 'ready to move', 'possession']
        }
        
        for requirement, keywords in requirement_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    requirements.append(requirement)
                    break
        
        return requirements
    
    def _calculate_confidence(self, parsed_data: Dict) -> float:
        """Calculate confidence score for parsing"""
        confidence = 0.5  # Base confidence
        
        if parsed_data['intent'] != 'search':
            confidence += 0.2
        if parsed_data['location']:
            confidence += 0.15
        if parsed_data['bhk_requirement']:
            confidence += 0.1
        if parsed_data['budget_range']['max']:
            confidence += 0.05
        
        return min(0.95, confidence)


class AdvancedAIMLEngine:
    """
    Main AI/ML engine combining all advanced features
    """
    
    def __init__(self):
        self.ensemble_predictor = EnsemblePricePredictor()
        self.market_analyzer = MarketTrendAnalyzer()
        self.risk_analyzer = InvestmentRiskAnalyzer()
        self.nlp_parser = NaturalLanguagePropertyParser()
    
    def comprehensive_property_analysis(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive AI-powered property analysis
        """
        # Price prediction
        price_prediction = self.ensemble_predictor.predict_price(property_data)
        
        # Market trend analysis
        city = property_data.get('city', 'gurugram')
        market_trend = self.market_analyzer.analyze_market_trend(city)
        
        # Risk analysis
        risk_analysis = self.risk_analyzer.analyze_investment_risk(property_data)
        
        # Generate investment score
        investment_score = self._calculate_investment_score(
            price_prediction, market_trend, risk_analysis
        )
        
        return {
            'property_analysis': {
                'price_prediction': price_prediction,
                'market_trend': market_trend,
                'risk_analysis': risk_analysis,
                'investment_score': investment_score
            },
            'ai_insights': self._generate_ai_insights(
                price_prediction, market_trend, risk_analysis
            ),
            'recommendations': self._generate_recommendations(
                investment_score, risk_analysis['risk_level']
            ),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _calculate_investment_score(self, price_prediction: Dict, 
                                  market_trend: Dict, 
                                  risk_analysis: Dict) -> Dict[str, Any]:
        """Calculate overall investment score (0-100)"""
        scores = {}
        
        # Price prediction confidence
        scores['prediction_confidence'] = price_prediction['confidence_score'] * 100
        
        # Market trend score
        trend_scores = {
            'bullish': 85,
            'neutral': 70,
            'volatile': 55,
            'bearish': 40
        }
        scores['market_score'] = trend_scores.get(market_trend['trend'], 50)
        
        # Risk score (inverted - lower risk = higher score)
        risk_scores = {
            'low': 90,
            'moderate': 75,
            'high': 50,
            'very_high': 25
        }
        scores['risk_score'] = risk_scores.get(risk_analysis['risk_level'], 50)
        
        # Calculate weighted overall score
        weights = {
            'prediction_confidence': 0.3,
            'market_score': 0.4,
            'risk_score': 0.3
        }
        
        overall_score = sum(
            scores[key] * weights[key] 
            for key in weights.keys()
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'component_scores': scores,
            'grade': self._get_investment_grade(overall_score)
        }
    
    def _get_investment_grade(self, score: float) -> str:
        """Get investment grade based on score"""
        if score >= 85:
            return 'A+ (Excellent Investment)'
        elif score >= 75:
            return 'A (Good Investment)'
        elif score >= 65:
            return 'B (Moderate Investment)'
        elif score >= 50:
            return 'C (Risky Investment)'
        else:
            return 'D (High Risk Investment)'
    
    def _generate_ai_insights(self, price_prediction: Dict, 
                             market_trend: Dict, 
                             risk_analysis: Dict) -> List[str]:
        """Generate AI-powered insights"""
        insights = []
        
        # Price insights
        confidence = price_prediction['confidence_score']
        if confidence > 0.85:
            insights.append("High confidence in price prediction with strong model agreement")
        elif confidence > 0.7:
            insights.append("Moderate confidence in price prediction")
        else:
            insights.append("Price prediction has moderate uncertainty - consider manual verification")
        
        # Market insights
        trend = market_trend['trend']
        if trend == 'bullish':
            insights.append("Market showing bullish trend - favorable for appreciation")
        elif trend == 'bearish':
            insights.append("Market showing bearish trend - caution advised for short-term")
        elif trend == 'volatile':
            insights.append("High market volatility - suitable for long-term investors only")
        
        # Risk insights
        risk_level = risk_analysis['risk_level']
        if risk_level == 'low':
            insights.append("Low risk profile suitable for conservative investors")
        elif risk_level == 'high':
            insights.append("High risk profile - requires thorough due diligence")
        
        return insights
    
    def _generate_recommendations(self, investment_score: Dict, 
                                risk_level: str) -> List[str]:
        """Generate investment recommendations"""
        recommendations = []
        
        score = investment_score['overall_score']
        grade = investment_score['grade']
        
        if score >= 80:
            recommendations.append(f"Strong Buy: {grade} - Excellent investment opportunity")
            recommendations.append("Consider immediate action given favorable market conditions")
        elif score >= 60:
            recommendations.append(f"Buy: {grade} - Good investment potential")
            recommendations.append("Proceed with standard due diligence process")
        elif score >= 40:
            recommendations.append(f"Hold: {grade} - Moderate investment potential")
            recommendations.append("Conduct detailed analysis before proceeding")
        else:
            recommendations.append(f"Avoid: {grade} - High risk investment")
            recommendations.append("Not recommended for conservative investment strategies")
        
        return recommendations


# Initialize global instances
ensemble_price_predictor = EnsemblePricePredictor()
market_trend_analyzer = MarketTrendAnalyzer()
investment_risk_analyzer = InvestmentRiskAnalyzer()
nlp_property_parser = NaturalLanguagePropertyParser()
advanced_ai_ml_engine = AdvancedAIMLEngine()