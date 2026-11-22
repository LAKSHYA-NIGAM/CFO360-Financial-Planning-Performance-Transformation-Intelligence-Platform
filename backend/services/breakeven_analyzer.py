"""
Break-Even Point (BEP) & Margin of Safety Analyzer
Calculates contribution margin ratio, break-even unit volume, break-even revenue,
and margin of safety percentage.
"""

from typing import Dict, Any


def calculate_breakeven(
  fixed_costs: float,
  sales_price_per_unit: float,
  variable_cost_per_unit: float,
  current_projected_units: float = 0,
) -> Dict[str, Any]:
  unit_contribution_margin = sales_price_per_unit - variable_cost_per_unit
  if sales_price_per_unit <= 0 or unit_contribution_margin <= 0:
    return {'error': 'Unit contribution margin must be strictly positive', 'breakeven_units': 0}

  cm_ratio = unit_contribution_margin / sales_price_per_unit
  breakeven_units = fixed_costs / unit_contribution_margin
  breakeven_revenue = breakeven_units * sales_price_per_unit

  margin_of_safety_units = max(0.0, current_projected_units - breakeven_units)
  margin_of_safety_pct = (margin_of_safety_units / current_projected_units * 100) if current_projected_units > 0 else 0.0

  return {
    'unit_contribution_margin': round(unit_contribution_margin, 2),
    'contribution_margin_ratio': round(cm_ratio, 4),
    'breakeven_units': round(breakeven_units, 2),
    'breakeven_revenue': round(breakeven_revenue, 2),
    'margin_of_safety_units': round(margin_of_safety_units, 2),
    'margin_of_safety_pct': round(margin_of_safety_pct, 2),
    'is_profitable_at_current_volume': current_projected_units >= breakeven_units,
  }
