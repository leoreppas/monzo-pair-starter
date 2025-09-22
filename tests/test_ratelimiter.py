from __future__ import annotations
from datetime import datetime, timedelta
from monzo_kata import RateLimiter


def test_ratelimiter_basic_sliding_window():
    rl = RateLimiter(limit=3, window=timedelta(seconds=60))
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    assert rl.allow("u", t0)
    assert rl.allow("u", t0)
    assert rl.allow("u", t0)
    assert rl.allow("u", t0) is False # 4th within same window denied




def test_ratelimiter_window_moves():
    rl = RateLimiter(limit=2, window=timedelta(seconds=10))
    t = datetime(2024, 1, 1, 0, 0, 0)
    assert rl.allow("k", t)
    assert rl.allow("k", t + timedelta(seconds=1))
    assert rl.allow("k", t + timedelta(seconds=2)) is False
    # After 10s from first event, one slot frees
    assert rl.allow("k", t + timedelta(seconds=11))




def test_ratelimiter_isolated_keys_and_zero_limit():
    rl = RateLimiter(limit=1, window=timedelta(seconds=5))
    t = datetime(2024, 1, 1, 0, 0, 0)
    assert rl.allow("a", t)
    assert rl.allow("b", t) # separate key gets its own window


    rl2 = RateLimiter(limit=0, window=timedelta(seconds=5))
    assert rl2.allow("x", t) is False