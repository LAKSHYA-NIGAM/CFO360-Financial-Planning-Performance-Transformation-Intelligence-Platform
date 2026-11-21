import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.wacc_calculator import calculate_wacc


class TestWaccCalculator(unittest.TestCase):
    def test_standard_corporate_wacc(self):
        # Equity $7M, Debt $3M (70/30 split).
        # Rf = 4%, Beta = 1.2, Equity Premium = 5.5% -> Ke = 4% + 1.2*5.5% = 10.6%
        # Kd = 6%, Tax = 21% -> Kd_after_tax = 6% * 0.79 = 4.74%
        # WACC = (0.7 * 10.6%) + (0.3 * 4.74%) = 7.42% + 1.422% = 8.842%
        res = calculate_wacc(
            equity_value=7000000,
            debt_value=3000000,
            risk_free_rate=0.04,
            beta=1.2,
            market_risk_premium=0.055,
            cost_of_debt=0.06,
            corporate_tax_rate=0.21,
        )

        self.assertAlmostEqual(res['wacc'], 0.0884, places=3)
        self.assertEqual(res['wacc_percentage'], '8.84%')
        self.assertEqual(res['equity_weight'], 0.7)
        self.assertEqual(res['debt_weight'], 0.3)

    def test_zero_capital_boundary(self):
        res = calculate_wacc(0, 0, 0.04, 1.0, 0.05, 0.05)
        self.assertIn('error', res)


if __name__ == '__main__':
    unittest.main()
