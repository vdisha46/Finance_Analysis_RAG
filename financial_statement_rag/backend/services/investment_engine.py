from __future__ import annotations


class InvestmentDecisionEngine:
    """Compute a 0-100 financial health score and investment recommendation."""

    @staticmethod
    def compute_financial_health_score(metrics: dict) -> float:
        profitability = float(metrics.get("profitability", 0) or 0)
        liquidity = float(metrics.get("liquidity", 0) or 0)
        solvency = float(metrics.get("solvency", 0) or 0)
        cash_flow = float(metrics.get("cash_flow", 0) or 0)
        growth = float(metrics.get("growth", 0) or 0)
        valuation = float(metrics.get("valuation", 0) or 0)

        score = (
            profitability * 0.25
            + liquidity * 0.15
            + solvency * 0.15
            + cash_flow * 0.20
            + growth * 0.15
            + valuation * 0.10
        )
        return round(min(max(score, 0), 100), 2)

    @staticmethod
    def generate_recommendation(company_a_score: float, company_b_score: float, company_a_name: str, company_b_name: str) -> dict:
        winner = company_a_name if company_a_score >= company_b_score else company_b_name
        if company_a_score == company_b_score:
            winner = "Tie"

        reason = (
            f"Higher profitability, stronger cash flow, better debt management, and superior growth "
            f"support {winner} as the preferred investment choice."
            if winner != "Tie"
            else "Both companies show similar financial strength and require a deeper qualitative review."
        )

        return {
            "winner": winner,
            "company_a_score": round(company_a_score, 2),
            "company_b_score": round(company_b_score, 2),
            "reason": reason,
        }
