import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.breakeven_analyzer import calculate_breakeven


class TestBreakevenAnalyzer(unittest.TestCase):
    def test_standard_breakeven_analysis(self):
        # Fixed costs: $100k. Price: $50/unit. Variable cost: $30/unit (CM = $20/unit, 40% CM ratio).
        # BEP units = 100,000 / 20 = 5,000 units. BEP Revenue = $250,000.
        # Current volume: 8,000 units -> Margin of safety = 3,000 units (37.5%).
        res = calculate_breakeven(
            fixed_costs=100000,
            sales_price_per_unit=50,
            variable_cost_per_unit=30,
            current_projected_units=8000,
        )

        self.assertEqual(res['unit_contribution_margin'], 20.0)
        self.assertEqual(res['contribution_margin_ratio'], 0.40)
        self.assertEqual(res['breakeven_units'], 5000.0)
        self.assertEqual(res['breakeven_revenue'], 250000.0)
        self.assertEqual(res['margin_of_safety_units'], 3000.0)
        self.assertEqual(res['margin_of_safety_pct'], 37.5)
        self.assertTrue(res['is_profitable_at_current_volume'])

    def test_negative_margin_handling(self):
        # Variable cost exceeds sales price
        res = calculate_breakeven(10000, 20, 25)
        self.assertIn('error', res)


if __name__ == '__main__':
    unittest.main()
