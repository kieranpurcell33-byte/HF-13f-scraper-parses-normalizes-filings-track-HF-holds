"""FINRA TRACE adapter — security-level daily movers (best/worst bonds).

TRACE (Trade Reporting and Compliance Engine) is the tape for US corporate-bond
transactions. This adapter authenticates to the FINRA API with OAuth2
client-credentials and queries a corporate-bond dataset to build the daily
gainers/losers list that populates the credit-specific section of the recap.

Honesty note
------------
The *free* FINRA API surfaces market breadth, volume and summary datasets.
True per-CUSIP end-of-day price returns (needed to rank the single best/worst
bond with real prices) generally require an entitled TRACE data product or a
commercial vendor (ICE, S&P/Markit, Bloomberg). This adapter:

* authenticates and queries the configured dataset, and
* maps rows to :class:`BondMove` **only when** the response actually carries
  price / return fields;
* otherwise raises :class:`SourceUnavailable` so the generator degrades and the
  report says the section needs a richer feed — it never invents prices.

Swapping in a vendor feed means implementing one method (``fetch_movers``)
against this same interface.
"""

from __future__ import annotations

import base64
from datetime import date
from typing import List, Optional

import requests

from ..models import BondMove
from .base import SecurityMoversSource, SourceUnavailable

TOKEN_URL = (
    "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token"
    "?grant_type=client_credentials"
)
# FINRA data platform. Dataset/group are configurable so an entitled TRACE
# corporate-bond dataset can be pointed at without code changes.
DATA_BASE = "https://api.finra.org/data/group/{group}/name/{dataset}"

# Candidate field names across FINRA/vendor schemas; we accept whichever exists.
_PRICE_FIELDS = ("lastSalePrice", "closePrice", "price", "endOfDayPrice")
_PRICE_CHG_FIELDS = ("priceChange", "netChange", "changeInPrice")
_SPREAD_CHG_FIELDS = ("spreadChange", "oasChange", "changeInSpread")
_ISSUER_FIELDS = ("issuerName", "issuer", "companyName", "issueSymbolIdentifier")
_CUSIP_FIELDS = ("cusip", "cusipId", "cusipIdentifier")
_COUPON_FIELDS = ("couponRate", "coupon", "interestRate")
_MATURITY_FIELDS = ("maturityDate", "maturity")


def _first(row: dict, keys) -> Optional[object]:
    for k in keys:
        if k in row and row[k] not in (None, "", "null"):
            return row[k]
    return None


class TraceMoversSource(SecurityMoversSource):
    name = "FINRA TRACE"

    def __init__(
        self,
        client_id: Optional[str],
        client_secret: Optional[str],
        group: str = "fixedIncomeMarket",
        dataset: str = "corporateBondDailyMetrics",
        timeout: float = 20.0,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.group = group
        self.dataset = dataset
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def _token(self) -> str:
        creds = f"{self.client_id}:{self.client_secret}".encode()
        headers = {"Authorization": f"Basic {base64.b64encode(creds).decode()}"}
        try:
            resp = requests.post(TOKEN_URL, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            token = resp.json().get("access_token")
        except requests.RequestException as exc:
            raise SourceUnavailable(f"FINRA auth failed: {exc}") from exc
        if not token:
            raise SourceUnavailable("FINRA auth returned no access_token")
        return token

    def _query(self, token: str, session: date) -> List[dict]:
        url = DATA_BASE.format(group=self.group, dataset=self.dataset)
        body = {
            "limit": 5000,
            "compareFilters": [
                {
                    "fieldName": "tradeReportDate",
                    "fieldValue": session.isoformat(),
                    "compareType": "equal",
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as exc:
            raise SourceUnavailable(f"FINRA query failed: {exc}") from exc
        # FINRA returns a list, or {"data": [...]} depending on endpoint.
        if isinstance(payload, list):
            return payload
        return payload.get("data", []) if isinstance(payload, dict) else []

    def _to_move(self, row: dict) -> Optional[BondMove]:
        price_chg = _first(row, _PRICE_CHG_FIELDS)
        spread_chg = _first(row, _SPREAD_CHG_FIELDS)
        if price_chg is None and spread_chg is None:
            return None  # no ranking signal in this row
        issuer = _first(row, _ISSUER_FIELDS)
        if issuer is None:
            return None
        try:
            return BondMove(
                issuer=str(issuer),
                cusip=(str(_first(row, _CUSIP_FIELDS)) if _first(row, _CUSIP_FIELDS) else None),
                coupon=(float(_first(row, _COUPON_FIELDS)) if _first(row, _COUPON_FIELDS) else None),
                maturity=(str(_first(row, _MATURITY_FIELDS)) if _first(row, _MATURITY_FIELDS) else None),
                price=(float(_first(row, _PRICE_FIELDS)) if _first(row, _PRICE_FIELDS) else None),
                price_change=(float(price_chg) if price_chg is not None else None),
                spread_change_bps=(float(spread_chg) if spread_chg is not None else None),
            )
        except (ValueError, TypeError):
            return None

    def fetch_movers(
        self, session: date, top_n: int = 5
    ) -> tuple[List[BondMove], List[BondMove]]:
        if not self.is_available():
            raise SourceUnavailable(
                "FINRA_API_CLIENT_ID / FINRA_API_CLIENT_SECRET not configured"
            )
        token = self._token()
        rows = self._query(token, session)
        moves = [m for m in (self._to_move(r) for r in rows) if m is not None]
        if not moves:
            raise SourceUnavailable(
                "TRACE dataset carried no per-security price/spread change fields "
                f"({self.group}/{self.dataset}); a per-CUSIP daily-return feed "
                "(entitled TRACE product or ICE/Markit/Bloomberg) is required to "
                "rank named bond movers."
            )

        def sort_key(m: BondMove) -> float:
            if m.price_change is not None:
                return m.price_change
            # fall back to inverse spread change (tighter = better)
            return -(m.spread_change_bps or 0.0)

        moves.sort(key=sort_key, reverse=True)
        gainers = moves[:top_n]
        losers = list(reversed(moves[-top_n:]))
        return gainers, losers
