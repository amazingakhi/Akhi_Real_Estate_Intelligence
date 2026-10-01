"""
UI Components & Visual Design System
"""

from .ui_styles import inject_premium_fintech_theme
from .metrics_cards import (
    render_institutional_hero,
    render_grepi_badge,
    render_avm_three_tier_cards,
    render_valuation_gauge_card,
    render_corridor_quadrant_pill,
)

from .dossier_generator import generate_dossier_html

__all__ = [
    "inject_premium_fintech_theme",
    "render_institutional_hero",
    "render_grepi_badge",
    "render_avm_three_tier_cards",
    "render_valuation_gauge_card",
    "render_corridor_quadrant_pill",
    "generate_dossier_html",
]
