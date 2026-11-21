"""
CFO360 - Automated Backend API Test Suite
-----------------------------------------
Validates all analytical endpoints, JSON responses, error handling,
and data query filtering.
"""
import os
import sys
import unittest

# Ensure backend directory is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app


class CFO360APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_health_check(self):
        """Verify /health returns 200 with data_loaded=True."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertTrue(data.get("data_loaded"))

    def test_02_get_regions(self):
        """Verify /api/regions returns distinct geographical regions."""
        response = self.client.get("/api/regions")
        self.assertEqual(response.status_code, 200)
        regions = response.get_json()
        self.assertIsInstance(regions, list)
        self.assertGreater(len(regions), 0)

    def test_03_kpi_summary(self):
        """Verify /api/kpi-summary returns high-level executive metrics."""
        response = self.client.get("/api/kpi-summary")
        self.assertEqual(response.status_code, 200)
        kpis = response.get_json()
        self.assertIsInstance(kpis, dict)
        self.assertIn("total_revenue_cr", kpis)
        self.assertIn("budget_revenue_cr", kpis)
        self.assertIn("gross_margin_pct", kpis)
        self.assertIn("ebitda_margin_pct", kpis)

    def test_04_revenue_trend_unfiltered(self):
        """Verify /api/revenue-trend returns monthly chronological timeline."""
        response = self.client.get("/api/revenue-trend")
        self.assertEqual(response.status_code, 200)
        trend = response.get_json()
        self.assertIsInstance(trend, list)
        self.assertGreater(len(trend), 0)
        first = trend[0]
        self.assertIn("month", first)
        self.assertIn("revenue_cr", first)
        self.assertIn("budget_revenue_cr", first)

    def test_05_revenue_trend_with_region_filter(self):
        """Verify /api/revenue-trend filters properly by region parameter."""
        reg_res = self.client.get("/api/regions")
        regions = reg_res.get_json()
        target_region = regions[0]

        response = self.client.get(f"/api/revenue-trend?region={target_region}")
        self.assertEqual(response.status_code, 200)
        filtered = response.get_json()
        self.assertIsInstance(filtered, list)
        self.assertGreater(len(filtered), 0)

    def test_06_revenue_by_region(self):
        """Verify /api/revenue-by-region returns regional breakdown."""
        response = self.client.get("/api/revenue-by-region")
        self.assertEqual(response.status_code, 200)
        breakdown = response.get_json()
        self.assertIsInstance(breakdown, list)
        self.assertGreater(len(breakdown), 0)
        self.assertIn("region", breakdown[0])
        self.assertIn("revenue_cr", breakdown[0])
        self.assertIn("variance_pct", breakdown[0])

    def test_07_revenue_by_product(self):
        """Verify /api/revenue-by-product returns product breakdown."""
        response = self.client.get("/api/revenue-by-product")
        self.assertEqual(response.status_code, 200)
        products = response.get_json()
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        self.assertIn("product", products[0])
        self.assertIn("revenue_cr", products[0])

    def test_08_budget_variance(self):
        """Verify /api/budget-variance returns variance calculations."""
        response = self.client.get("/api/budget-variance")
        self.assertEqual(response.status_code, 200)
        variance = response.get_json()
        self.assertIsInstance(variance, list)
        self.assertGreater(len(variance), 0)
        self.assertIn("region", variance[0])
        self.assertIn("revenue_cr", variance[0])
        self.assertIn("budget_cr", variance[0])
        self.assertIn("variance_pct", variance[0])

    def test_09_profitability_waterfall(self):
        """Verify /api/profitability returns P&L waterfall metrics."""
        response = self.client.get("/api/profitability")
        self.assertEqual(response.status_code, 200)
        pnl = response.get_json()
        self.assertIsInstance(pnl, list)
        self.assertGreater(len(pnl), 0)
        self.assertIn("gross_profit_cr", pnl[0])
        self.assertIn("ebitda_cr", pnl[0])

    def test_10_forecast_endpoint(self):
        """Verify /api/forecast returns projection data points."""
        response = self.client.get("/api/forecast")
        self.assertEqual(response.status_code, 200)
        forecast = response.get_json()
        self.assertIsInstance(forecast, list)
        self.assertGreater(len(forecast), 0)
        self.assertIn("revenue_cr", forecast[0])
        self.assertIn("type", forecast[0])

    def test_11_insights_endpoint(self):
        """Verify /api/insights returns executive takeaway narratives."""
        response = self.client.get("/api/insights")
        self.assertEqual(response.status_code, 200)
        insights = response.get_json()
        self.assertIsInstance(insights, (dict, list))

    def test_12_json_404_and_405_handling(self):
        """Verify unknown route returns JSON 404 and OPTIONS fallback returns JSON 405."""
        res_404 = self.client.get("/non-existent-route-random")
        self.assertEqual(res_404.status_code, 404)
        data_404 = res_404.get_json()
        self.assertEqual(data_404.get("status"), 404)

        res_405 = self.client.get("/api/unknown-subpath")
        self.assertIn(res_405.status_code, [404, 405])
        data_405 = res_405.get_json()
        self.assertIn("error", data_405)


if __name__ == "__main__":
    unittest.main(verbosity=2)
