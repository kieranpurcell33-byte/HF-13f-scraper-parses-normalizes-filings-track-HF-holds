"""
Live-feed adapters.

The primary adapter is :class:`RestGatewaySource` -- a generic HTTP client for a
JSON gateway *you* control that proxies your licensed data (Bloomberg via
``blpapi``, ICE, FINRA TRACE, etc.). Keeping the vendor integration behind your
own endpoint means no vendor SDK or entitlement leaks into this repo, and the
recap pipeline only ever speaks JSON.

Expected gateway contract (all dates are ISO ``YYYY-MM-DD``)::

    GET  {base}/macro?date=<d>            -> MacroSnapshot JSON
    GET  {base}/performers?date=<d>&n=<k> -> {"gainers": [...], "decliners": [...]}
    GET  {base}/news?date=<d>             -> {"items": [NewsItem, ...]}
    GET  {base}/outlook?date=<d>          -> NextSessionOutlook JSON

Each object matches the field names in ``hy_recap.models``. Auth is sent as
``Authorization: Bearer <HY_REST_API_KEY>`` when a key is configured.

Vendor-specific adapters (Bloomberg/ICE/TRACE direct) are intentionally left as
documented stubs -- wire them in ``registry.build_sources`` once your entitlement
and SDK are available on the runner.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Tuple

import requests

from hy_recap.config import RecapConfig
from hy_recap.models import (
    BondPerformer,
    MacroSnapshot,
    NewsItem,
    NextSessionOutlook,
)
from hy_recap.sources.base import (
    BondPerformanceSource,
    MacroSource,
    NewsSource,
    OutlookSource,
)

_TIMEOUT = 30


class RestGatewaySource(
    MacroSource, BondPerformanceSource, NewsSource, OutlookSource
):
    """One adapter that can serve every section from a JSON gateway."""

    def __init__(self, config: RecapConfig):
        if not config.rest_base_url:
            raise ValueError(
                "HY_REST_BASE_URL is required for the 'rest' source. "
                "Point it at your data gateway (see sources/feeds.py docstring)."
            )
        self.base = config.rest_base_url.rstrip("/")
        self.session = requests.Session()
        if config.rest_api_key:
            self.session.headers["Authorization"] = f"Bearer {config.rest_api_key}"

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.session.get(f"{self.base}/{path}", params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def get_macro(self, session_date: date) -> MacroSnapshot:
        data = self._get("macro", {"date": session_date.isoformat()})
        data.setdefault("session_date", session_date.isoformat())
        return MacroSnapshot.model_validate(data)

    def get_performers(
        self, session_date: date, top_n: int
    ) -> Tuple[List[BondPerformer], List[BondPerformer]]:
        data = self._get(
            "performers", {"date": session_date.isoformat(), "n": top_n}
        )
        gainers = [BondPerformer.model_validate(x) for x in data.get("gainers", [])]
        decliners = [BondPerformer.model_validate(x) for x in data.get("decliners", [])]
        return gainers[:top_n], decliners[:top_n]

    def get_news(self, session_date: date) -> List[NewsItem]:
        data = self._get("news", {"date": session_date.isoformat()})
        return [NewsItem.model_validate(x) for x in data.get("items", [])]

    def get_outlook(self, next_session_date: date) -> NextSessionOutlook:
        data = self._get("outlook", {"date": next_session_date.isoformat()})
        data.setdefault("next_session_date", next_session_date.isoformat())
        return NextSessionOutlook.model_validate(data)
