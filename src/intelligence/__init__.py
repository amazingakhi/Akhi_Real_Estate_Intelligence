"""
Akhi Real Estate Intelligence (AREI) Engine
Proprietary Institutional Analytics, Valuation & Benchmarking Suite
"""

from .grepi_index import calculate_grepi_index, get_top_performing_micro_markets
from .valuation_avm import calculate_fairvalue_avm, get_valuation_gauge
from .financial_engine import calculate_capyield_model, run_irr_projection
from .corridor_quadrant import classify_corridor_quadrants, get_corridor_metrics

__all__ = [
    "calculate_grepi_index",
    "get_top_performing_micro_markets",
    "calculate_fairvalue_avm",
    "get_valuation_gauge",
    "calculate_capyield_model",
    "run_irr_projection",
    "classify_corridor_quadrants",
    "get_corridor_metrics",
]
