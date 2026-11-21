import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.financial_ratios import FinancialRatioEngine


class TestFinancialRatioEngine(unittest.TestCase):
    def test_liquidity_ratios_calculation(self):
        # Assets: $500k, Liabilities: $250k, Cash: $100k, AR: $100k
        res = FinancialRatioEngine.compute_liquidity_ratios(500000, 250000, 100000, 100000)
        self.assertEqual(res["current_ratio"], 2.0)
        self.assertEqual(res["quick_ratio"], 0.8)
        self.assertEqual(res["working_capital"], 250000.0)
        self.assertEqual(res["assessment"], "Adequate Liquidity")

    def test_profitability_margins(self):
        # Rev: $1M, COGS: $400k, OpEx: $300k, D&A: $50k
        # Gross profit: $600k (60%), EBIT: $300k (30%), EBITDA: $350k (35%)
        res = FinancialRatioEngine.compute_profitability_ratios(1000000, 400000, 300000, 50000)
        self.assertEqual(res["gross_profit"], 600000.0)
        self.assertEqual(res["gross_margin_pct"], 60.0)
        self.assertEqual(res["operating_income_ebit"], 300000.0)
        self.assertEqual(res["operating_margin_pct"], 30.0)
        self.assertEqual(res["ebitda"], 350000.0)
        self.assertEqual(res["ebitda_margin_pct"], 35.0)

    def test_cash_conversion_cycle(self):
        # DSO: 42 days, DIO: 35 days, DPO: 30 days -> CCC = 47 days
        res = FinancialRatioEngine.compute_cash_conversion_cycle(42.0, 35.0, 30.0)
        self.assertEqual(res["cash_conversion_cycle_days"], 47.0)
        self.assertEqual(res["efficiency"], "Standard Velocity")


if __name__ == "__main__":
    unittest.main()
