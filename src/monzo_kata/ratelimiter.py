from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Deque, Dict

@dataclass
class RateLimiter:
    """Per-key sliding-window limiter: allow up to `limit` events within the past `window`."""
    limit: int
    window: timedelta
    _events: Dict[str, Deque[datetime]] = field(default_factory=dict)

    def allow(self, key: str, now: datetime) -> bool:
        if self.limit <= 0:
            return False
        dq = self._events.setdefault(key, deque())
        cutoff = now - self.window
        # Evict anything strictly older than or equal to the cutoff
        while dq and dq[0] <= cutoff:
            dq.popleft()
        if len(dq) < self.limit:
            dq.append(now)
            return True
        return False
