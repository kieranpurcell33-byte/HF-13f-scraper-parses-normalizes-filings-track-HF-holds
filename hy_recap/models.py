"""Typed data models for the HY recap.

Pydantic models mirror the sections of the delivered report so the generator
can render deterministically and tests can assert on structured data rather than
free text.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class YieldPoint(BaseModel):
    """A single rate/spread observation with a day-over-day change."""

    label: str = Field(..., description="Human label, e.g. 'UST 10Y' or 'HY OAS'.")
    value: Optional[float] = Field(None, description="Latest level (pct or bps).")
    unit: str = Field("%", description="Unit for display, e.g. '%' or 'bps'.")
    change: Optional[float] = Field(
        None, description="Day-over-day change in the same unit."
    )
    as_of: Optional[date] = Field(None, description="Observation date.")

    def render(self) -> str:
        if self.value is None:
            return f"| {self.label} | n/a | — |"
        if self.unit == "%":
            val = f"{self.value:,.2f}%"
        elif self.unit == "bps":
            val = f"{self.value:,.0f} bps"
        elif self.unit.startswith("$"):
            val = f"${self.value:,.2f}"
        else:
            val = f"{self.value:,.2f} {self.unit}"
        if self.change is None:
            return f"| {self.label} | {val} | — |"
        arrow = "▲" if self.change > 0 else ("▼" if self.change < 0 else "▬")
        if self.unit == "%":
            chg = f"{arrow} {self.change:+.2f} pp"
        elif self.unit == "bps":
            chg = f"{arrow} {self.change:+.0f} bps"
        elif self.unit.startswith("$"):
            chg = f"{arrow} {self.change:+.2f}"
        else:
            chg = f"{arrow} {self.change:+.2f}"
        return f"| {self.label} | {val} | {chg} |"


class BondMove(BaseModel):
    """A single security-level mover (best/worst bond of the session)."""

    issuer: str
    cusip: Optional[str] = None
    coupon: Optional[float] = None
    maturity: Optional[str] = None
    price: Optional[float] = None
    price_change: Optional[float] = None
    spread_change_bps: Optional[float] = None
    driver: Optional[str] = Field(
        None, description="Short credit-specific reason for the move."
    )

    def render_row(self) -> str:
        def f(x, fmt):
            return format(x, fmt) if x is not None else "—"

        name = self.issuer
        if self.coupon is not None and self.maturity:
            name = f"{self.issuer} {self.coupon:.3f} {self.maturity}"
        return (
            f"| {name} | {self.cusip or '—'} | {f(self.price, '.3f')} | "
            f"{f(self.price_change, '+.3f')} | {f(self.spread_change_bps, '+.0f')} | "
            f"{self.driver or '—'} |"
        )


class MarketSnapshot(BaseModel):
    """Close-of-day levels for the covered session."""

    session_date: date
    points: List[YieldPoint] = Field(default_factory=list)
    fund_flow_note: Optional[str] = None

    def get(self, label: str) -> Optional[YieldPoint]:
        for p in self.points:
            if p.label == label:
                return p
        return None


class Recap(BaseModel):
    """The full recap payload for one delivery."""

    session_date: date
    delivery_date: date
    snapshot: MarketSnapshot
    top_gainers: List[BondMove] = Field(default_factory=list)
    top_losers: List[BondMove] = Field(default_factory=list)
    notable_events: List[str] = Field(default_factory=list)
    outlook: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(
        default_factory=list,
        description="Data gaps / degradations surfaced to the reader.",
    )
