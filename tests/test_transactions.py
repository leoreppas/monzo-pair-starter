from __future__ import annotations
from decimal import Decimal
from datetime import timezone, date
import pytest

from monzo_kata import parse_transactions, daily_totals, Tx


def test_parse_transactions_happy_path():
    lines = [
        "tx1, 2024-10-19T22:30:00Z, -12.34, GBP",
        "tx2, 2024-10-19T23:59:59+01:00, 100.00, GBP",  # BST -> UTC 22:59:59
        "  ",
    ]
    txs = parse_transactions(lines)
    assert len(txs) == 2
    assert txs[0].id == "tx1"
    assert txs[0].when.tzinfo is not None
    assert txs[0].when.tzinfo == timezone.utc
    assert txs[0].amount == Decimal("-12.34")
    assert txs[0].currency == "GBP"

    # second line offset converts to UTC
    assert txs[1].when.tzinfo is not None
    assert txs[1].when.astimezone(timezone.utc).hour == 22
    assert txs[1].amount == Decimal("100.00")


def test_parse_transactions_validation():
    with pytest.raises(ValueError):
        parse_transactions(["badline"])
    with pytest.raises(ValueError):
        parse_transactions([", 2024-01-01T00:00:00Z, 1.0, GBP"])  # missing id
    with pytest.raises(ValueError):
        parse_transactions(["tx, not-a-time, 1.0, GBP"])  # bad time
    with pytest.raises(ValueError):
        parse_transactions(["tx, 2024-01-01T00:00:00Z, bananas, GBP"])  # bad amount
    with pytest.raises(ValueError):
        parse_transactions(["tx, 2024-01-01T00:00:00Z, 1.0, "])  # empty currency


def test_daily_totals_utc_and_currency_guard():
    lines = [
        "a, 2024-10-19T23:30:00+00:00, 10.00, GBP",
        "b, 2024-10-19T23:59:59+00:00, 5.00, GBP",
        "c, 2024-10-20T00:00:00+00:00, -2.50, GBP",
    ]
    txs = parse_transactions(lines)
    totals = daily_totals(txs)
    assert totals[date(2024, 10, 19)] == Decimal("15.00")
    assert totals[date(2024, 10, 20)] == Decimal("-2.50")

    # mixed currencies should error
    txs2 = parse_transactions([
        "x, 2024-10-19T10:00:00Z, 1.00, GBP",
        "y, 2024-10-19T11:00:00Z, 1.00, EUR",
    ])
    with pytest.raises(ValueError):
        daily_totals(txs2)
