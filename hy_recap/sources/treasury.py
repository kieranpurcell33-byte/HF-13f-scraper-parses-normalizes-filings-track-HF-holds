"""US Treasury par-yield-curve adapter (public, no API key).

Fallback source for the 10Y/30Y when FRED is unavailable. Uses the Treasury
FiscalData API, which is free and unauthenticated:
https://fiscaldata.treasury.gov/datasets/daily-treasury-par-yield-curve-rates/
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

import requests

from ..models import YieldPoint
from .base import DataSource, SourceUnavailable

FISCAL_BASE = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    "/v2/accounting/od/daily_treasury_yield_curve"
)

# FiscalData field -> our label
_FIELDS = {
    "bc_10year": "UST 10Y",
    "bc_30year": "UST 30Y",
}


class TreasuryParYieldSource(DataSource):
    name = "Treasury FiscalData"

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def is_available(self) -> bool:
        return True  # public endpoint, no key required

    def fetch_points(self, session: date) -> List[YieldPoint]:
        start = session - timedelta(days=10)
        params = {
            "filter": (
                f"record_date:gte:{start.isoformat()},"
                f"record_date:lte:{session.isoformat()}"
            ),
            "sort": "record_date",
            "page[size]": "500",
        }
        try:
            resp = requests.get(FISCAL_BASE, params=params, timeout=self.timeout)
            resp.raise_for_status()
            rows = resp.json().get("data", [])
        except requests.RequestException as exc:
            raise SourceUnavailable(f"Treasury request failed: {exc}") from exc

        if not rows:
            raise SourceUnavailable("Treasury returned no rows")

        points: List[YieldPoint] = []
        for field, label in _FIELDS.items():
            series = []
            for r in rows:
                v = r.get(field)
                if v in (None, "", "null"):
                    continue
                try:
                    series.append((date.fromisoformat(r["record_date"]), float(v)))
                except (ValueError, KeyError):
                    continue
            if not series:
                continue
            as_of, latest = series[-1]
            prev = series[-2][1] if len(series) >= 2 else None
            points.append(
                YieldPoint(
                    label=label,
                    value=latest,
                    unit="%",
                    change=None if prev is None else latest - prev,
                    as_of=as_of,
                )
            )
        if not points:
            raise SourceUnavailable("Treasury rows missing 10Y/30Y fields")
        return points
