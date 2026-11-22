"""
Multi-Scenario Financial Forecaster (Base, Bull, Bear)
Projects revenue, gross profit, and EBITDA margins across economic scenarios.
"""

from typing import Dict, Any


SCENARIO_MULTIPLIERS = {
  'bull': {'revenue_growth': 1.25, 'cogs_efficiency': 0.95, 'opex_multiplier': 1.05},
  'base': {'revenue_growth': 1.10, 'cogs_efficiency': 1.00, 'opex_multiplier': 1.02},
  'bear': {'revenue_growth': 0.90, 'cogs_efficiency': 1.08, 'opex_multiplier': 1.00},
}


def project_financial_scenarios(
  baseline_revenue: float,
  baseline_cogs: float,
  baseline_opex: float,
) -> Dict[str, Any]:
  if baseline_revenue <= 0:
    return {'error': 'Baseline revenue must be positive'}

  results = {}

  for scenario_name, mult in SCENARIO_MULTIPLIERS.items():
    proj_revenue = baseline_revenue * mult['revenue_growth']
    proj_cogs = baseline_cogs * mult['cogs_efficiency'] * mult['revenue_growth']
    proj_gross_profit = proj_revenue - proj_cogs
    proj_opex = baseline_opex * mult['opex_multiplier']
    proj_ebitda = proj_gross_profit - proj_opex

    ebitda_margin = (proj_ebitda / proj_revenue * 100) if proj_revenue > 0 else 0.0

    results[scenario_name] = {
      'projected_revenue': round(proj_revenue, 2),
      'projected_gross_profit': round(proj_gross_profit, 2),
      'projected_ebitda': round(proj_ebitda, 2),
      'ebitda_margin_pct': round(ebitda_margin, 2),
    }

  return results
