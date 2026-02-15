from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class LotMatch(BaseModel):
    ticker: str
    sell_date: date
    quantity: int
    cost_base: Decimal
    proceeds: Decimal
    raw_gain: Decimal
    held_over_12_months: bool
    discount: Decimal
    net_gain: Decimal


class FinancialYearSummary(BaseModel):
    financial_year: str
    total_gains: Decimal
    total_losses: Decimal
    discount_gains: Decimal
    non_discount_gains: Decimal
    discount_amount: Decimal
    net_capital_gain: Decimal
    lot_matches: list[LotMatch] = []


class CGTOverview(BaseModel):
    financial_years: list[FinancialYearSummary]
