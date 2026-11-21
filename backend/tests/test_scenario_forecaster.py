import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.scenario_forecaster import project_financial_scenarios


class TestScenarioForecaster(unittest.TestCase):
    def test_projects_three_distinct_scenarios(self):
        res = project_financial_scenarios(
            baseline_revenue=1000000,
            baseline_cogs=400000,
            baseline_opex=300000,
        )

        self.assertIn('base', res)
        self.assertIn('bull', res)
        self.assertIn('bear', res)

        self.assertGreater(res['bull']['projected_revenue'], res['base']['projected_revenue'])
        self.assertGreater(res['base']['projected_revenue'], res['bear']['projected_revenue'])
        self.assertGreater(res['bull']['projected_ebitda'], res['bear']['projected_ebitda'])


if __name__ == '__main__':
    unittest.main()
