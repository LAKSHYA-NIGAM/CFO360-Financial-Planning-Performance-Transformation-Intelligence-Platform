import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.dcf_valuation import calculate_dcf_valuation


class TestDcfValuation(unittest.TestCase):
    def test_standard_5_year_dcf_model(self):
        # Initial investment $1M, cash flows $200k, $250k, $300k, $350k, $400k. WACC = 10%, g = 2.5%
        cash_flows = [200000, 250000, 300000, 350000, 400000]
        res = calculate_dcf_valuation(
            initial_outflow=1000000,
            cash_flows=cash_flows,
            discount_rate=0.10,
            terminal_growth_rate=0.025,
        )

        self.assertTrue(res['is_positive_npv'])
        self.assertGreater(res['enterprise_value'], 3000000)
        self.assertGreater(res['terminal_value'], 5000000)
        self.assertNotIn('error', res)

    def test_invalid_discount_rate_error_handling(self):
        # Discount rate equal to or less than growth rate
        res = calculate_dcf_valuation(
            initial_outflow=500000,
            cash_flows=[100000],
            discount_rate=0.02,
            terminal_growth_rate=0.025,
        )
        self.assertIn('error', res)
        self.assertEqual(res['npv'], 0.0)


if __name__ == '__main__':
    unittest.main()
