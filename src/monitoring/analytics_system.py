"""
Akhi Real Estate Intelligence - Monitoring and Analytics System
Comprehensive system monitoring, error tracking, and business analytics
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import time
import threading
from collections import defaultdict, deque


class MetricType(Enum):
    """Types of metrics to track"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricsCollector:
    """Collect and manage application metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(dict)
        self.histograms = defaultdict(list)
        self.summaries = defaultdict(list)
        self.lock = threading.Lock()
    
    def increment_counter(self, name: str, value: float = 1.0, 
                         labels: Dict[str, str] = None) -> None:
        """Increment a counter metric"""
        with self.lock:
            key = self._make_key(name, labels)
            if key not in self.metrics:
                self.metrics[key] = {
                    'type': MetricType.COUNTER.value,
                    'value': 0.0,
                    'labels': labels or {},
                    'created_at': datetime.now().isoformat()
                }
            self.metrics[key]['value'] += value
            self.metrics[key]['updated_at'] = datetime.now().isoformat()
    
    def set_gauge(self, name: str, value: float, 
                 labels: Dict[str, str] = None) -> None:
        """Set a gauge metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.metrics[key] = {
                'type': MetricType.GAUGE.value,
                'value': value,
                'labels': labels or {},
                'updated_at': datetime.now().isoformat()
            }
    
    def observe_histogram(self, name: str, value: float, 
                        labels: Dict[str, str] = None) -> None:
        """Observe a histogram metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.histograms[key].append({
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'labels': labels or {}
            })
    
    def observe_summary(self, name: str, value: float, 
                      labels: Dict[str, str] = None) -> None:
        """Observe a summary metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.summaries[key].append({
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'labels': labels or {}
            })
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a unique key for metric with labels"""
        if labels:
            label_str = ",".join([f"{k}={v}" for k, v in sorted(labels.items())])
            return f"{name}{{{label_str}}}"
        return name
    
    def get_metric(self, name: str, labels: Dict[str, str] = None) -> Optional[Dict]:
        """Get a specific metric"""
        key = self._make_key(name, labels)
        return self.metrics.get(key)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self.lock:
            return {
                'counters': {k: v for k, v in self.metrics.items() if v['type'] == MetricType.COUNTER.value},
                'gauges': {k: v for k, v in self.metrics.items() if v['type'] == MetricType.GAUGE.value},
                'histograms': dict(self.histograms),
                'summaries': dict(self.summaries),
                'collected_at': datetime.now().isoformat()
            }
    
    def calculate_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Calculate statistics for histogram"""
        key = self._make_key(name, labels)
        values = [h['value'] for h in self.histograms.get(key, [])]
        
        if not values:
            return {}
        
        import statistics
        return {
            'count': len(values),
            'sum': sum(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
        }


class ErrorTracker:
    """Track and analyze application errors"""
    
    def __init__(self):
        self.errors = deque(maxlen=1000)  # Keep last 1000 errors
        self.error_counts = defaultdict(int)
        self.lock = threading.Lock()
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None,
                  severity: AlertSeverity = AlertSeverity.ERROR) -> str:
        """Track an error with context"""
        error_id = self._generate_error_id()
        
        error_data = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': self._get_stack_trace(error),
            'severity': severity.value,
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
            'user_id': context.get('user_id') if context else None,
            'request_id': context.get('request_id') if context else None
        }
        
        with self.lock:
            self.errors.append(error_data)
            self.error_counts[error_data['error_type']] += 1
        
        return error_id
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"ERR-{timestamp}-{random_str}"
    
    def _get_stack_trace(self, error: Exception) -> str:
        """Get stack trace from error"""
        import traceback
        return traceback.format_exc()
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors"""
        with self.lock:
            return list(self.errors)[-limit:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self.lock:
            total_errors = len(self.errors)
            error_type_counts = dict(self.error_counts)
            
            if total_errors > 0:
                recent_24h = datetime.now() - timedelta(hours=24)
                recent_errors = [e for e in self.errors 
                              if datetime.fromisoformat(e['timestamp']) > recent_24h]
            else:
                recent_errors = []
            
            return {
                'total_errors': total_errors,
                'recent_24h_errors': len(recent_errors),
                'error_types': error_type_counts,
                'most_common_error': max(error_type_counts.items(), 
                                          key=lambda x: x[1])[0] if error_type_counts else None,
                'last_24h_error_rate': len(recent_errors) / 24 if recent_errors else 0
            }


class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.request_times = deque(maxlen=10000)
        self.db_query_times = deque(maxlen=5000)
        self.api_response_times = defaultdict(deque)
        self.lock = threading.Lock()
    
    def record_request_time(self, duration_ms: float, endpoint: str = None) -> None:
        """Record HTTP request duration"""
        with self.lock:
            self.request_times.append({
                'duration_ms': duration_ms,
                'endpoint': endpoint,
                'timestamp': datetime.now().isoformat()
            })
            
            if endpoint:
                self.api_response_times[endpoint].append(duration_ms)
    
    def record_db_query_time(self, duration_ms: float, query_type: str = None) -> None:
        """Record database query duration"""
        with self.lock:
            self.db_query_times.append({
                'duration_ms': duration_ms,
                'query_type': query_type,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            if not self.request_times:
                return {'status': 'no_data'}
            
            request_durations = [r['duration_ms'] for r in self.request_times]
            db_durations = [d['duration_ms'] for d in self.db_query_times] if self.db_query_times else [0]
            
            import statistics
            
            return {
                'http_requests': {
                    'total': len(request_durations),
                    'avg_response_time_ms': statistics.mean(request_durations),
                    'median_response_time_ms': statistics.median(request_durations),
                    'p95_response_time_ms': self._calculate_percentile(request_durations, 95),
                    'p99_response_time_ms': self._calculate_percentile(request_durations, 99),
                    'max_response_time_ms': max(request_durations),
                    'min_response_time_ms': min(request_durations)
                },
                'database_queries': {
                    'total': len(db_durations),
                    'avg_query_time_ms': statistics.mean(db_durations) if db_durations else 0,
                    'median_query_time_ms': statistics.median(db_durations) if db_durations else 0,
                    'slow_queries_count': len([d for d in db_durations if d > 100])
                },
                'endpoint_performance': {
                    endpoint: {
                        'avg_time_ms': statistics.mean(times),
                        'request_count': len(times)
                    }
                    for endpoint, times in self.api_response_times.items()
                }
            }
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        import statistics
        if not data:
            return 0.0
        return statistics.quantiles(data, n=100)[percentile - 1]


class HealthChecker:
    """Check system health and dependencies"""
    
    def __init__(self):
        self.health_checks = {}
        self.last_check_results = {}
    
    def register_health_check(self, name: str, check_func: Callable, 
                           critical: bool = False) -> None:
        """Register a health check function"""
        self.health_checks[name] = {
            'function': check_func,
            'critical': critical
        }
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for name, check_config in self.health_checks.items():
            try:
                start_time = time.time()
                check_result = check_config['function']()
                duration = time.time() - start_time
                
                check_status = check_result.get('status', 'healthy')
                is_healthy = check_status == 'healthy'
                
                if not is_healthy and check_config['critical']:
                    overall_status = HealthStatus.UNHEALTHY
                elif not is_healthy and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                
                results[name] = {
                    'status': check_status,
                    'message': check_result.get('message', 'OK'),
                    'duration_ms': round(duration * 1000, 2),
                    'critical': check_config['critical'],
                    'checked_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'message': str(e),
                    'duration_ms': 0,
                    'critical': check_config['critical'],
                    'checked_at': datetime.now().isoformat(),
                    'error': True
                }
                
                if check_config['critical']:
                    overall_status = HealthStatus.UNHEALTHY
        
        self.last_check_results = {
            'overall_status': overall_status.value,
            'checks': results,
            'checked_at': datetime.now().isoformat()
        }
        
        return self.last_check_results
    
    def get_last_health_status(self) -> Dict[str, Any]:
        """Get last health check results"""
        return self.last_check_results


class BusinessAnalytics:
    """Track business metrics and KPIs"""
    
    def __init__(self):
        self.metrics = {
            'user_registrations': [],
            'property_views': [],
            'lead_generations': [],
            'conversions': [],
            'revenue': []
        }
        self.lock = threading.Lock()
    
    def track_user_registration(self, user_id: str, user_type: str = 'free') -> None:
        """Track user registration"""
        with self.lock:
            self.metrics['user_registrations'].append({
                'user_id': user_id,
                'user_type': user_type,
                'timestamp': datetime.now().isoformat()
            })
    
    def track_property_view(self, property_id: str, user_id: str = None) -> None:
        """Track property view"""
        with self.lock:
            self.metrics['property_views'].append({
                'property_id': property_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
    
    def track_lead_generation(self, lead_id: str, source: str, value: float = 0) -> None:
        """Track lead generation"""
        with self.lock:
            self.metrics['lead_generations'].append({
                'lead_id': lead_id,
                'source': source,
                'value': value,
                'timestamp': datetime.now().isoformat()
            })
    
    def track_conversion(self, conversion_id: str, conversion_type: str, 
                       value: float) -> None:
        """Track conversion"""
        with self.lock:
            self.metrics['conversions'].append({
                'conversion_id': conversion_id,
                'conversion_type': conversion_type,
                'value': value,
                'timestamp': datetime.now().isoformat()
            })
    
    def track_revenue(self, transaction_id: str, amount: float, 
                     source: str = 'subscription') -> None:
        """Track revenue"""
        with self.lock:
            self.metrics['revenue'].append({
                'transaction_id': transaction_id,
                'amount': amount,
                'source': source,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_business_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get business metrics for specified period"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        with self.lock:
            # Filter metrics by period
            recent_registrations = [
                m for m in self.metrics['user_registrations']
                if datetime.fromisoformat(m['timestamp']) > cutoff_date
            ]
            
            recent_views = [
                m for m in self.metrics['property_views']
                if datetime.fromisoformat(m['timestamp']) > cutoff_date
            ]
            
            recent_leads = [
                m for m in self.metrics['lead_generations']
                if datetime.fromisoformat(m['timestamp']) > cutoff_date
            ]
            
            recent_conversions = [
                m for m in self.metrics['conversions']
                if datetime.fromisoformat(m['timestamp']) > cutoff_date
            ]
            
            recent_revenue = [
                m for m in self.metrics['revenue']
                if datetime.fromisoformat(m['timestamp']) > cutoff_date
            ]
            
            # Calculate KPIs
            total_revenue = sum(m['amount'] for m in recent_revenue)
            total_leads = len(recent_leads)
            total_conversions = len(recent_conversions)
            conversion_rate = (total_conversions / total_leads * 100) if total_leads > 0 else 0
            
            return {
                'period_days': period_days,
                'user_registrations': {
                    'total': len(recent_registrations),
                    'by_type': self._count_by_field(recent_registrations, 'user_type')
                },
                'property_views': {
                    'total': len(recent_views),
                    'unique_properties': len(set(m['property_id'] for m in recent_views))
                },
                'lead_generation': {
                    'total': total_leads,
                    'by_source': self._count_by_field(recent_leads, 'source')
                },
                'conversions': {
                    'total': total_conversions,
                    'rate_percentage': round(conversion_rate, 2),
                    'by_type': self._count_by_field(recent_conversions, 'conversion_type')
                },
                'revenue': {
                    'total': total_revenue,
                    'by_source': self._sum_by_field(recent_revenue, 'source'),
                    'average_transaction_value': total_revenue / len(recent_revenue) if recent_revenue else 0
                },
                'calculated_at': datetime.now().isoformat()
            }
    
    def _count_by_field(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Count items by field value"""
        counts = defaultdict(int)
        for item in items:
            counts[item.get(field, 'unknown')] += 1
        return dict(counts)
    
    def _sum_by_field(self, items: List[Dict], field: str) -> Dict[str, float]:
        """Sum values by field"""
        sums = defaultdict(float)
        for item in items:
            sums[item.get(field, 'unknown')] += item.get('value', item.get('amount', 0))
        return dict(sums)


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alerts = deque(maxlen=500)
        self.alert_rules = []
        self.lock = threading.Lock()
    
    def add_alert_rule(self, name: str, condition: Callable, 
                     severity: AlertSeverity = AlertSeverity.WARNING) -> None:
        """Add an alert rule"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'severity': severity,
            'enabled': True
        })
    
    def check_alert_rules(self) -> List[Dict[str, Any]]:
        """Check all alert rules and generate alerts"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if not rule['enabled']:
                continue
            
            try:
                if rule['condition']():
                    alert = {
                        'alert_id': self._generate_alert_id(),
                        'rule_name': rule['name'],
                        'severity': rule['severity'].value,
                        'triggered_at': datetime.now().isoformat(),
                        'status': 'active'
                    }
                    
                    with self.lock:
                        self.alerts.append(alert)
                    
                    triggered_alerts.append(alert)
            except Exception as e:
                print(f"Error checking alert rule {rule['name']}: {e}")
        
        return triggered_alerts
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        random_str = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"ALERT-{timestamp}-{random_str}"
    
    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        with self.lock:
            alerts = list(self.alerts)
            
            if severity:
                alerts = [a for a in alerts if a['severity'] == severity.value]
            
            return alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        with self.lock:
            for alert in self.alerts:
                if alert['alert_id'] == alert_id:
                    alert['status'] = 'acknowledged'
                    alert['acknowledged_at'] = datetime.now().isoformat()
                    return True
            return False


class MonitoringSystem:
    """
    Main monitoring and analytics system
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.error_tracker = ErrorTracker()
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.business_analytics = BusinessAnalytics()
        self.alert_manager = AlertManager()
        
        # Register default health checks
        self._register_default_health_checks()
        
        # Register default alert rules
        self._register_default_alert_rules()
    
    def _register_default_health_checks(self):
        """Register default health checks"""
        self.health_checker.register_health_check(
            'database',
            lambda: {'status': 'healthy', 'message': 'Database connection OK'},
            critical=True
        )
        
        self.health_checker.register_health_check(
            'cache',
            lambda: {'status': 'healthy', 'message': 'Cache connection OK'},
            critical=False
        )
        
        self.health_checker.register_health_check(
            'api',
            lambda: {'status': 'healthy', 'message': 'API endpoints responding'},
            critical=True
        )
    
    def _register_default_alert_rules(self):
        """Register default alert rules"""
        self.alert_manager.add_alert_rule(
            'high_error_rate',
            lambda: self.error_tracker.get_error_statistics()['last_24h_error_rate'] > 10,
            AlertSeverity.CRITICAL
        )
        
        self.alert_manager.add_alert_rule(
            'slow_response_time',
            lambda: self.performance_monitor.get_performance_stats().get('http_requests', {}).get('p95_response_time_ms', 0) > 2000,
            AlertSeverity.WARNING
        )
        
        self.alert_manager.add_alert_rule(
            'low_disk_space',
            lambda: False,  # Would check actual disk space
            AlertSeverity.WARNING
        )
    
    def record_api_request(self, endpoint: str, duration_ms: float, 
                        status_code: int = 200) -> None:
        """Record API request metrics"""
        self.metrics_collector.increment_counter('api_requests_total', labels={'endpoint': endpoint})
        self.metrics_collector.increment_counter(f'api_requests_status_{status_code}', 
                                             labels={'endpoint': endpoint})
        self.performance_monitor.record_request_time(duration_ms, endpoint)
        
        if status_code >= 500:
            self.metrics_collector.increment_counter('api_errors_total', labels={'endpoint': endpoint})
    
    def record_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """Record an error"""
        return self.error_tracker.track_error(error, context)
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        return {
            'health': self.health_checker.run_health_checks(),
            'performance': self.performance_monitor.get_performance_stats(),
            'errors': self.error_tracker.get_error_statistics(),
            'metrics': self.metrics_collector.get_all_metrics(),
            'alerts': {
                'active': len(self.alert_manager.get_active_alerts()),
                'recent': self.alert_manager.check_alert_rules()
            },
            'business': self.business_analytics.get_business_metrics(period_days=7),
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_monitoring_dashboard(self) -> str:
        """Generate monitoring dashboard HTML"""
        overview = self.get_system_overview()
        
        checks_html = "".join([
            f'<div class="health-check {check["status"]}">'
            f'<span class="check-name">{name}</span>'
            f'<span class="check-status">{check["status"]}</span>'
            f'<span class="check-time">{check["duration_ms"]}ms</span>'
            f'</div>'
            for name, check in overview['health']['checks'].items()
        ])

        return f"""
        <div class="monitoring-dashboard">
            <h1>System Monitoring Dashboard</h1>
            
            <div class="health-status">
                <h2>System Health: {overview['health']['overall_status'].upper()}</h2>
                <div class="health-checks">
                    {checks_html}
                </div>
            </div>
            
            <div class="performance-metrics">
                <h2>Performance Metrics</h2>
                <div class="metric-cards">
                    <div class="metric-card">
                        <span class="metric-label">Avg Response Time</span>
                        <span class="metric-value">{overview['performance']['http_requests']['avg_response_time_ms']:.2f}ms</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">P95 Response Time</span>
                        <span class="metric-value">{overview['performance']['http_requests']['p95_response_time_ms']:.2f}ms</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Error Rate</span>
                        <span class="metric-value">{overview['errors']['last_24h_error_rate']:.2f}/hour</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Active Alerts</span>
                        <span class="metric-value">{overview['alerts']['active']}</span>
                    </div>
                </div>
            </div>
            
            <div class="business-metrics">
                <h2>Business Metrics (7 Days)</h2>
                <div class="business-cards">
                    <div class="business-card">
                        <span class="business-label">New Users</span>
                        <span class="business-value">{overview['business']['user_registrations']['total']}</span>
                    </div>
                    <div class="business-card">
                        <span class="business-label">Property Views</span>
                        <span class="business-value">{overview['business']['property_views']['total']}</span>
                    </div>
                    <div class="business-card">
                        <span class="business-label">Leads Generated</span>
                        <span class="business-value">{overview['business']['lead_generation']['total']}</span>
                    </div>
                    <div class="business-card">
                        <span class="business-label">Revenue</span>
                        <span class="business-value">₹{overview['business']['revenue']['total']:,.2f}</span>
                    </div>
                </div>
            </div>
        </div>
        """


# Initialize global instances
metrics_collector = MetricsCollector()
error_tracker = ErrorTracker()
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()
business_analytics = BusinessAnalytics()
alert_manager = AlertManager()
monitoring_system = MonitoringSystem()