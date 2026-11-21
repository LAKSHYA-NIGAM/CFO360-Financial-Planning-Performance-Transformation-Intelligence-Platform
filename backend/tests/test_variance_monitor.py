import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.variance_monitor import BudgetVarianceMonitor


class TestBudgetVarianceMonitor(unittest.TestCase):
    def test_revenue_underperformance_triggers_adverse_alert(self):
        # Revenue target: $100k, Actual: $85k (15% below target, threshold = 10%)
        res = BudgetVarianceMonitor.evaluate_line_item(
            line_item="Q3 Enterprise Sales",
            category="REVENUE",
            actual=85000,
            budget=100000,
            threshold_pct=10.0
        )
        self.assertEqual(res["classification"], "ADVERSE")
        self.assertTrue(res["is_adverse"])
        self.assertTrue(res["is_alert_triggered"])
        self.assertIn("BUDGET BREACH", res["alert_message"])

    def test_expense_overrun_triggers_adverse_alert(self):
        # Cloud Hosting Budget: $50k, Actual: $65k (30% cost overrun)
        res = BudgetVarianceMonitor.evaluate_line_item(
            line_item="AWS Infrastructure",
            category="EXPENSE",
            actual=65000,
            budget=50000,
            threshold_pct=10.0
        )
        self.assertEqual(res["classification"], "ADVERSE")
        self.assertTrue(res["is_alert_triggered"])
        self.assertIn("over budget", res["alert_message"])

    def test_favorable_expense_savings_does_not_trigger_alert(self):
        # Travel Budget: $20k, Actual: $15k (25% under budget -> Favorable)
        res = BudgetVarianceMonitor.evaluate_line_item(
            line_item="Corporate Travel",
            category="EXPENSE",
            actual=15000,
            budget=20000
        )
        self.assertEqual(res["classification"], "FAVORABLE")
        self.assertFalse(res["is_adverse"])
        self.assertFalse(res["is_alert_triggered"])
        self.assertIsNone(res["alert_message"])

    def test_portfolio_evaluation(self):
        items = [
            {"line_item": "Rev", "category": "REVENUE", "actual": 120000, "budget": 100000},
            {"line_item": "Marketing", "category": "EXPENSE", "actual": 45000, "budget": 30000}
        ]
        res = BudgetVarianceMonitor.evaluate_budget_portfolio(items)
        self.assertEqual(res["total_items"], 2)
        self.assertEqual(res["alert_count"], 1)
        self.assertEqual(res["critical_alerts"][0]["line_item"], "Marketing")


if __name__ == "__main__":
    unittest.main()
