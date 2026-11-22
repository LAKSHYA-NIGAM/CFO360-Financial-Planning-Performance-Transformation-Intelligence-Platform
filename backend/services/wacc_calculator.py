"""
Weighted Average Cost of Capital (WACC) Engine
Computes cost of equity via CAPM: Ke = Rf + Beta * (Rm - Rf)
and after-tax cost of debt: Kd_after_tax = Kd * (1 - TaxRate)
blended across capital structure weights.
"""

from typing import Dict, Any


def calculate_wacc(
  equity_value: float,
  debt_value: float,
  risk_free_rate: float,
  beta: float,
  market_risk_premium: float,
  cost_of_debt: float,
  corporate_tax_rate: float = 0.21,
) -> Dict[str, Any]:
  total_capital = equity_value + debt_value
  if total_capital <= 0:
    return {'wacc': 0.0, 'error': 'Total capital must be positive'}

  weight_equity = equity_value / total_capital
  weight_debt = debt_value / total_capital

  # CAPM Cost of Equity
  cost_of_equity = risk_free_rate + (beta * market_risk_premium)

  # After-tax Cost of Debt
  after_tax_cost_of_debt = cost_of_debt * (1 - corporate_tax_rate)

  # WACC = (E/V * Ke) + (D/V * Kd * (1 - T))
  wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)

  return {
    'wacc': round(wacc, 4),
    'wacc_percentage': f"{round(wacc * 100, 2)}%",
    'cost_of_equity': round(cost_of_equity, 4),
    'after_tax_cost_of_debt': round(after_tax_cost_of_debt, 4),
    'equity_weight': round(weight_equity, 4),
    'debt_weight': round(weight_debt, 4),
  }
