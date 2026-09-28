from __future__ import annotations

from typing import Any


def safe_divide(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return float(numerator) / float(denominator)


class FinancialRatioEngine:
    """Compute key financial ratios from row-based statements."""

    @staticmethod
    def compute_from_statement(data: dict[str, Any]) -> dict[str, float | None]:
        current_assets = float(data.get("current_assets", 0) or 0)
        current_liabilities = float(data.get("current_liabilities", 0) or 0)
        inventory = float(data.get("inventory", 0) or 0)
        cash = float(data.get("cash_and_equivalents", 0) or 0)
        total_liabilities = float(data.get("total_liabilities", 0) or 0)
        total_equity = float(data.get("total_equity", 0) or 0)
        revenue = float(data.get("revenue", 0) or 0)
        gross_profit = float(data.get("gross_profit", 0) or 0)
        operating_income = float(data.get("operating_income", 0) or 0)
        ebitda = float(data.get("ebitda", 0) or 0)
        net_income = float(data.get("net_income", 0) or 0)
        total_assets = float(data.get("total_assets", 0) or 0)
        interest_expense = float(data.get("interest_expense", 0) or 0)
        ebit = float(data.get("ebit", 0) or 0)

        ratios = {
            "current_ratio": safe_divide(current_assets, current_liabilities),
            "quick_ratio": safe_divide(current_assets - inventory, current_liabilities),
            "cash_ratio": safe_divide(cash, current_liabilities),
            "gross_margin": safe_divide(gross_profit, revenue),
            "operating_margin": safe_divide(operating_income, revenue),
            "ebitda_margin": safe_divide(ebitda, revenue),
            "net_margin": safe_divide(net_income, revenue),
            "roe": safe_divide(net_income, total_equity),
            "roa": safe_divide(net_income, total_assets),
            "debt_to_equity": safe_divide(total_liabilities, total_equity),
            "interest_coverage": safe_divide(ebit, interest_expense) if interest_expense else None,
        }
        return ratios
