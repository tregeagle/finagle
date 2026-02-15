from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Action, StockTransaction
from app.schemas.report import CGTOverview, FinancialYearSummary, LotMatch

ZERO = Decimal("0")


@dataclass
class BuyLot:
    date: date
    remaining: int
    cost_per_unit: Decimal
    fee_per_unit: Decimal


def _financial_year(d: date) -> str:
    if d.month >= 7:
        return f"{d.year}-{str(d.year + 1)[2:]}"
    return f"{d.year - 1}-{str(d.year)[2:]}"


def _held_over_12_months(buy_date: date, sell_date: date) -> bool:
    return (sell_date - buy_date) > timedelta(days=365)


def compute_cgt(db: Session, user_id: int, fy: str | None = None) -> CGTOverview:
    stmt = (
        select(StockTransaction)
        .where(StockTransaction.user_id == user_id)
        .order_by(StockTransaction.date, StockTransaction.time)
    )
    transactions = list(db.scalars(stmt).all())

    buy_queues: dict[str, list[BuyLot]] = defaultdict(list)
    fy_matches: dict[str, list[LotMatch]] = defaultdict(list)

    for txn in transactions:
        ticker = txn.ticker.upper()
        if txn.action == Action.BUY:
            fee_per_unit = Decimal(str(txn.fee)) / txn.quantity
            cost_per_unit = Decimal(str(txn.price))
            buy_queues[ticker].append(
                BuyLot(
                    date=txn.date,
                    remaining=txn.quantity,
                    cost_per_unit=cost_per_unit,
                    fee_per_unit=fee_per_unit,
                )
            )
        else:
            sell_qty = txn.quantity
            sell_fee_per_unit = Decimal(str(txn.fee)) / txn.quantity
            sell_price = Decimal(str(txn.price))
            sell_fy = _financial_year(txn.date)

            queue = buy_queues[ticker]
            while sell_qty > 0 and queue:
                lot = queue[0]
                matched = min(lot.remaining, sell_qty)

                cost_base = matched * (lot.cost_per_unit + lot.fee_per_unit)
                proceeds = matched * (sell_price - sell_fee_per_unit)
                raw_gain = proceeds - cost_base
                held_long = _held_over_12_months(lot.date, txn.date)
                discount = (raw_gain * Decimal("0.5")) if (held_long and raw_gain > ZERO) else ZERO
                net_gain = raw_gain - discount

                fy_matches[sell_fy].append(
                    LotMatch(
                        ticker=ticker,
                        sell_date=txn.date,
                        quantity=matched,
                        cost_base=cost_base.quantize(Decimal("0.01")),
                        proceeds=proceeds.quantize(Decimal("0.01")),
                        raw_gain=raw_gain.quantize(Decimal("0.01")),
                        held_over_12_months=held_long,
                        discount=discount.quantize(Decimal("0.01")),
                        net_gain=net_gain.quantize(Decimal("0.01")),
                    )
                )

                lot.remaining -= matched
                sell_qty -= matched
                if lot.remaining == 0:
                    queue.pop(0)

    summaries = []
    for fy_key in sorted(fy_matches.keys()):
        if fy and fy_key != fy:
            continue
        matches = fy_matches[fy_key]
        summaries.append(_build_summary(fy_key, matches))

    return CGTOverview(financial_years=summaries)


def _build_summary(fy_key: str, matches: list[LotMatch]) -> FinancialYearSummary:
    total_gains = sum((m.raw_gain for m in matches if m.raw_gain > ZERO), ZERO)
    total_losses = sum((m.raw_gain for m in matches if m.raw_gain < ZERO), ZERO)

    discount_raw = sum(
        (m.raw_gain for m in matches if m.held_over_12_months and m.raw_gain > ZERO), ZERO
    )
    non_discount_raw = sum(
        (m.raw_gain for m in matches if not m.held_over_12_months and m.raw_gain > ZERO), ZERO
    )

    # ATO 18A: apply losses against non-discount first, then discount
    remaining_losses = abs(total_losses)

    non_discount_net = non_discount_raw - min(remaining_losses, non_discount_raw)
    remaining_losses -= min(remaining_losses, non_discount_raw)

    discount_eligible = discount_raw - min(remaining_losses, discount_raw)
    discount_amount = discount_eligible * Decimal("0.5")

    net_capital_gain = max(ZERO, non_discount_net + discount_eligible - discount_amount)

    return FinancialYearSummary(
        financial_year=fy_key,
        total_gains=total_gains.quantize(Decimal("0.01")),
        total_losses=total_losses.quantize(Decimal("0.01")),
        discount_gains=discount_raw.quantize(Decimal("0.01")),
        non_discount_gains=non_discount_raw.quantize(Decimal("0.01")),
        discount_amount=discount_amount.quantize(Decimal("0.01")),
        net_capital_gain=net_capital_gain.quantize(Decimal("0.01")),
        lot_matches=matches,
    )
