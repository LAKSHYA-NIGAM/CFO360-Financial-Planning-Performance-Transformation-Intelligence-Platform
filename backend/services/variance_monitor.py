"""
Budget Variance Sensitivity & Adverse Threshold Alert Engine
Monitors actual financial performance against planned budgets, categorizes
favorable vs. adverse discrepancies, and flags critical variance breaches.
"""

from typing import Dict, List, Optional


class BudgetVarianceMonitor:
    @classmethod
    def evaluate_line_item(
        cls,
        line_item: str,
        category: str,  # 'REVENUE' or 'EXPENSE'
        actual: float,
        budget: float,
        threshold_pct: float = 10.0,
        threshold_abs: float = 25000.0
    ) -> Dict:
        """
        Evaluates variance for an individual budget line item.
        """
        diff = actual - budget
        variance_pct = round((diff / budget) * 100, 2) if budget != 0 else 0.0

        is_expense = category.upper() in ("EXPENSE", "OPEX", "COGS", "COST")
        # For expenses: higher than budget is Adverse (-). For revenue: lower than budget is Adverse (-).
        if is_expense:
            is_adverse = diff > 0
            favorable_str = "ADVERSE" if is_adverse else "FAVORABLE"
        else:
            is_adverse = diff < 0
            favorable_str = "ADVERSE" if is_adverse else "FAVORABLE"

        is_alert_triggered = is_adverse and (
            abs(variance_pct) >= threshold_pct or abs(diff) >= threshold_abs
        )

        alert_message = None
        if is_alert_triggered:
            direction = "over budget" if diff > 0 else "under budget"
            alert_message = (
                f"BUDGET BREACH: {line_item} is {abs(diff):,.2f} ({abs(variance_pct)}%) {direction}. "
                f"Exceeds sensitivity threshold of {threshold_pct}%."
            )

        return {
            "line_item": line_item,
            "category": category.upper(),
            "actual": actual,
            "budget": budget,
            "variance_amount": round(diff, 2),
            "variance_percentage": variance_pct,
            "classification": favorable_str,
            "is_adverse": is_adverse,
            "is_alert_triggered": is_alert_triggered,
            "alert_message": alert_message
        }

    @classmethod
    def evaluate_budget_portfolio(cls, items: List[Dict]) -> Dict:
        """
        Evaluates a complete budget vs actual schedule.
        """
        results = [
            cls.evaluate_line_item(
                item["line_item"],
                item.get("category", "EXPENSE"),
                item["actual"],
                item["budget"],
                item.get("threshold_pct", 10.0),
                item.get("threshold_abs", 25000.0)
            )
            for item in items
        ]

        alerts = [r for r in results if r["is_alert_triggered"]]

        return {
            "total_items": len(items),
            "alert_count": len(alerts),
            "items": results,
            "critical_alerts": alerts
        }
