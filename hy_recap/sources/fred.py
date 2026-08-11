"""FRED (St. Louis Fed) adapter — HY spreads/yields, Treasuries, crude.

Fully working with a free FRED API key (``FRED_API_KEY``). Series used:

* ``BAMLH0A0HYM2``    ICE BofA US HY Option-Adjusted Spread  (percent → bps ×100)
* ``BAMLH0A0HYM2EY``  ICE BofA US HY Effective Yield         (percent)
* ``DGS10`` / ``DGS30`` Treasury constant-maturity yields    (percent)
* ``DCOILWTICO``      WTI spot                               ($/bbl)

FRED lags a day or two on some series; we ask for the latest observation on or
before the session date and pair it with the immediately prior one to compute a
day-over-day change.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

import requests

try:
    from tenacity import retry, stop_after_attempt, wait_exponential

    _retry = retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
except Exception:  # pragma: no cover - tenacity optional
    def _retry(fn):
        return fn

from ..models import YieldPoint
from .base import DataSource, SourceUnavailable

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# (series_id, label, unit, bps_scale)
_SERIES = [
    ("BAMLH0A0HYM2", "HY OAS", "bps", 100.0),
    ("BAMLH0A0HYM2EY", "HY yield-to-worst", "%", 1.0),
    ("DGS10", "UST 10Y", "%", 1.0),
    ("DGS30", "UST 30Y", "%", 1.0),
    ("DCOILWTICO", "WTI crude", "$/bbl", 1.0),  # dollar level; change in $
]


class FredSource(DataSource):
    name = "FRED"

    def __init__(self, api_key: Optional[str], timeout: float = 20.0):
        self.api_key = api_key
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.api_key)

    @_retry
    def _observations(self, series_id: str, session: date) -> List[tuple[date, float]]:
        # Look back ~14 calendar days to guarantee we capture two valid prints
        start = session - timedelta(days=14)
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start.isoformat(),
            "observation_end": session.isoformat(),
            "sort_order": "asc",
        }
        resp = requests.get(FRED_BASE, params=params, timeout=self.timeout)
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        out: List[tuple[date, float]] = []
        for o in obs:
            v = o.get("value")
            if v in (None, ".", ""):
                continue
            try:
                out.append((date.fromisoformat(o["date"]), float(v)))
            except (ValueError, KeyError):
                continue
        return out

    def fetch_points(self, session: date) -> List[YieldPoint]:
        if not self.is_available():
            raise SourceUnavailable("FRED_API_KEY not configured")

        points: List[YieldPoint] = []
        try:
            for series_id, label, unit, scale in _SERIES:
                series = self._observations(series_id, session)
                if not series:
                    continue
                as_of, latest = series[-1]
                prev = series[-2][1] if len(series) >= 2 else None
                value = latest * scale
                change = None if prev is None else (latest - prev) * scale
                points.append(
                    YieldPoint(
                        label=label,
                        value=value,
                        unit=unit,
                        change=change,
                        as_of=as_of,
                    )
                )
        except requests.RequestException as exc:
            raise SourceUnavailable(f"FRED request failed: {exc}") from exc

        if not points:
            raise SourceUnavailable("FRED returned no usable observations")
        return points
