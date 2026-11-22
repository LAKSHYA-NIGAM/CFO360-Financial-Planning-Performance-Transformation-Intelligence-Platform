"""
Discounted Cash Flow (DCF) & Net Present Value (NPV) Valuation Engine
Computes enterprise value, present value of projected free cash flows (FCF),
and Gordon Growth terminal value.
"""

from typing import List, Dict, Any


def calculate_dcf_valuation(
  initial_outflow: float,
  cash_flows: List[float],
  discount_rate: float,
  terminal_growth_rate: float = 0.025,
) -> Dict[str, Any]:
  if discount_rate <= 0 or discount_rate <= terminal_growth_rate:
    return {
      'npv': 0.0,
      'enterprise_value': 0.0,
      'pv_cash_flows': 0.0,
      'terminal_value': 0.0,
      'pv_terminal_value': 0.0,
      'error': 'Discount rate must be strictly greater than terminal growth rate',
    }

  pv_cash_flows = 0.0
  n = len(cash_flows)

  for t, cf in enumerate(cash_flows, 1):
    pv_cash_flows += cf / ((1 + discount_rate) ** t)

  # Terminal Value via Gordon Growth Model: FCF_n * (1 + g) / (WACC - g)
  last_fcf = cash_flows[-1] if n > 0 else 0.0
  terminal_value = (last_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
  pv_terminal_value = terminal_value / ((1 + discount_rate) ** n) if n > 0 else 0.0

  enterprise_value = pv_cash_flows + pv_terminal_value
  npv = enterprise_value - abs(initial_outflow)

  return {
    'npv': round(npv, 2),
    'enterprise_value': round(enterprise_value, 2),
    'pv_cash_flows': round(pv_cash_flows, 2),
    'terminal_value': round(terminal_value, 2),
    'pv_terminal_value': round(pv_terminal_value, 2),
    'is_positive_npv': npv > 0,
  }
