from __future__ import annotations


class ValuationEngine:
    """Compute simple valuation metrics for a company."""

    @staticmethod
    def calculate_pe_ratio(market_price: float, earnings_per_share: float) -> float | None:
        if earnings_per_share in (None, 0):
            return None
        return market_price / earnings_per_share

    @staticmethod
    def calculate_pb_ratio(market_price: float, book_value_per_share: float) -> float | None:
        if book_value_per_share in (None, 0):
            return None
        return market_price / book_value_per_share

    @staticmethod
    def calculate_ev_ebitda(enterprise_value: float, ebitda: float) -> float | None:
        if ebitda in (None, 0):
            return None
        return enterprise_value / ebitda

    @staticmethod
    def calculate_ev_sales(enterprise_value: float, revenue: float) -> float | None:
        if revenue in (None, 0):
            return None
        return enterprise_value / revenue

    @staticmethod
    def calculate_peg_ratio(pe_ratio: float | None, growth_rate: float | None) -> float | None:
        if pe_ratio is None or growth_rate in (None, 0):
            return None
        return pe_ratio / growth_rate

    @staticmethod
    def dcf_valuation(fcff: float, wacc: float, growth_rate: float, terminal_years: int = 5) -> dict:
        if wacc in (None, 0):
            return {"intrinsic_value": None, "fair_value": None}
        terminal_value = (fcff * (1 + growth_rate)) / (wacc - growth_rate)
        intrinsic_value = terminal_value / (1 + wacc) ** terminal_years
        return {
            "intrinsic_value": round(intrinsic_value, 2),
            "fair_value": round(intrinsic_value, 2),
            "terminal_value": round(terminal_value, 2),
            "wacc": wacc,
        }
