"""
Corporate Financial Health Ratios & Cash Conversion Cycle Engine
Computes standard liquidity, profitability, and operational efficiency ratios
for executive FP&A reporting.
"""

from typing import Dict, Optional


class FinancialRatioEngine:
    @classmethod
    def compute_liquidity_ratios(
        cls, current_assets: float, current_liabilities: float, cash: float, receivables: float
    ) -> Dict:
        """
        Calculates Current Ratio and Quick (Acid-Test) Ratio.
        """
        if current_liabilities <= 0:
            return {
                "current_ratio": None,
                "quick_ratio": None,
                "assessment": "Invalid or zero current liabilities"
            }

        cr = round(current_assets / current_liabilities, 2)
        qr = round((cash + receivables) / current_liabilities, 2)

        if cr >= 1.5 and qr >= 1.0:
            assessment = "Strong Liquidity"
        elif cr >= 1.0:
            assessment = "Adequate Liquidity"
        else:
            assessment = "Liquidity Pressure / Working Capital Deficit"

        return {
            "current_ratio": cr,
            "quick_ratio": qr,
            "working_capital": round(current_assets - current_liabilities, 2),
            "assessment": assessment
        }

    @classmethod
    def compute_profitability_ratios(
        cls, revenue: float, cogs: float, opex: float, depreciation_amortization: float = 0.0
    ) -> Dict:
        """
        Calculates Gross Margin, EBITDA Margin, and Operating (EBIT) Margin.
        """
        if revenue <= 0:
            return {
                "gross_margin_pct": 0.0,
                "ebitda_margin_pct": 0.0,
                "operating_margin_pct": 0.0
            }

        gross_profit = revenue - cogs
        operating_income = gross_profit - opex
        ebitda = operating_income + depreciation_amortization

        return {
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round((gross_profit / revenue) * 100, 2),
            "operating_income_ebit": round(operating_income, 2),
            "operating_margin_pct": round((operating_income / revenue) * 100, 2),
            "ebitda": round(ebitda, 2),
            "ebitda_margin_pct": round((ebitda / revenue) * 100, 2)
        }

    @classmethod
    def compute_cash_conversion_cycle(cls, dso: float, dio: float, dpo: float) -> Dict:
        """
        Calculates Net Cash Conversion Cycle (CCC = DSO + DIO - DPO).
        """
        ccc = round(dso + dio - dpo, 1)
        return {
            "days_sales_outstanding_dso": dso,
            "days_inventory_outstanding_dio": dio,
            "days_payable_outstanding_dpo": dpo,
            "cash_conversion_cycle_days": ccc,
            "efficiency": "High Velocity" if ccc < 45 else ("Standard Velocity" if ccc < 90 else "Capital Trapped in Inventory/Receivables")
        }
