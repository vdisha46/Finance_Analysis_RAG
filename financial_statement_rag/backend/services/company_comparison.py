from __future__ import annotations

from typing import Any


class CompanyComparisonEngine:
    """Generate a comparable company analysis for two companies."""

    @staticmethod
    def compare_revenue(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Revenue",
            "company_a": company_a.get("revenue", 0),
            "company_b": company_b.get("revenue", 0),
            "winner": company_a.get("revenue", 0) >= company_b.get("revenue", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_profitability(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Profitability",
            "company_a": company_a.get("net_margin", 0),
            "company_b": company_b.get("net_margin", 0),
            "winner": company_a.get("net_margin", 0) >= company_b.get("net_margin", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_liquidity(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Liquidity",
            "company_a": company_a.get("current_ratio", 0),
            "company_b": company_b.get("current_ratio", 0),
            "winner": company_a.get("current_ratio", 0) >= company_b.get("current_ratio", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_solvency(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        debt_ratio_a = company_a.get("total_liabilities", 0) / max(company_a.get("total_assets", 1), 1)
        debt_ratio_b = company_b.get("total_liabilities", 0) / max(company_b.get("total_assets", 1), 1)
        return {
            "metric": "Solvency",
            "company_a": 1 - debt_ratio_a,
            "company_b": 1 - debt_ratio_b,
            "winner": (1 - debt_ratio_a) >= (1 - debt_ratio_b) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_efficiency(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Efficiency",
            "company_a": company_a.get("asset_turnover", 0),
            "company_b": company_b.get("asset_turnover", 0),
            "winner": company_a.get("asset_turnover", 0) >= company_b.get("asset_turnover", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_cash_flow(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Cash Flow",
            "company_a": company_a.get("operating_cash_flow", 0),
            "company_b": company_b.get("operating_cash_flow", 0),
            "winner": company_a.get("operating_cash_flow", 0) >= company_b.get("operating_cash_flow", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_growth(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Growth",
            "company_a": company_a.get("growth_rate", 0),
            "company_b": company_b.get("growth_rate", 0),
            "winner": company_a.get("growth_rate", 0) >= company_b.get("growth_rate", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def compare_valuation(company_a: dict[str, Any], company_b: dict[str, Any]) -> dict:
        return {
            "metric": "Valuation",
            "company_a": company_a.get("pe_ratio", 0),
            "company_b": company_b.get("pe_ratio", 0),
            "winner": company_a.get("pe_ratio", 0) <= company_b.get("pe_ratio", 0) and company_a.get("company_name", "A") or company_b.get("company_name", "B"),
        }

    @staticmethod
    def calculate_financial_score(company: dict[str, Any]) -> float:
        revenue = float(company.get("revenue", 0) or 0)
        profit = float(company.get("net_margin", 0) or 0)
        liquidity = float(company.get("current_ratio", 0) or 0)
        solvency = float(company.get("debt_to_equity", 0) or 0)
        growth = float(company.get("growth_rate", 0) or 0)
        return round((revenue / max(revenue, 1)) * 20 + (profit * 100) * 0.4 + (liquidity * 10) + (100 / max(solvency + 1, 1)) * 0.3 + growth * 0.5, 2)

    @staticmethod
    def generate_winner(company_a: dict[str, Any], company_b: dict[str, Any]) -> str:
        score_a = CompanyComparisonEngine.calculate_financial_score(company_a)
        score_b = CompanyComparisonEngine.calculate_financial_score(company_b)
        return company_a.get("company_name", "A") if score_a >= score_b else company_b.get("company_name", "B")

    @staticmethod
    def generate_investment_recommendation(company_a: dict[str, Any], company_b: dict[str, Any]) -> str:
        winner = CompanyComparisonEngine.generate_winner(company_a, company_b)
        return f"Preferred investment: {winner}. Based on profitability, liquidity, solvency, cash flow, and growth signals."
