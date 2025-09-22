from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Dict


@dataclass(frozen=True)
class Tx:
    id: str
    when: datetime  # stored in UTC
    amount: Decimal  # positive for credit, negative for debit
    currency: str


def parse_iso8601_utc(s: str) -> datetime:
    """Parse ISO-8601 timestamps into timezone-aware UTC datetimes."""
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"invalid timestamp: {s}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_transactions(lines: Iterable[str]) -> List[Tx]:
    """Parse CSV lines: id, timestamp_iso8601, amount_decimal, currency."""
    txs: List[Tx] = []
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            raise ValueError(f"line {idx}: expected 4 fields, got {len(parts)}")
        id_, ts_s, amt_s, ccy = parts
        if not id_:
            raise ValueError(f"line {idx}: id is required")
        if not ccy:
            raise ValueError(f"line {idx}: currency is required")
        try:
            when = parse_iso8601_utc(ts_s)
        except ValueError as e:
            raise ValueError(f"line {idx}: {e}") from e
        try:
            amount = Decimal(amt_s)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"line {idx}: invalid amount: {amt_s}") from e
        txs.append(Tx(id=id_, when=when, amount=amount, currency=ccy))
    return txs


def daily_totals(txs: Iterable[Tx]) -> Dict[date, Decimal]:
    """Per-day totals in UTC; error if mixed currencies present."""
    totals: Dict[date, Decimal] = {}
    ccy_seen: set[str] = set()
    for tx in txs:
        ccy_seen.add(tx.currency)
        d = tx.when.astimezone(timezone.utc).date()
        totals[d] = totals.get(d, Decimal("0")) + tx.amount
    if len(ccy_seen) > 1:
        raise ValueError("mixed currencies encountered; provide a single currency")
    return totals
