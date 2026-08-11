"""
Pydantic models describing a daily US high-yield (HY) bond market recap.

The recap has four sections, mirroring the deliverable spec:
  1. Notable events / news for the session.
  2. Best and worst performing HY bonds of the day (issuer / credit specific).
  3. Macro & index context (rates, spreads, flows, tone).
  4. What is expected for the next trading day.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Direction(str, Enum):
    """Which end of the day's performance a bond sits on."""

    GAINER = "gainer"
    DECLINER = "decliner"


class MacroSnapshot(BaseModel):
    """Index-level and rates context for the session.

    All spread figures are in basis points; returns and yields in percent.
    Fields are optional so a partial feed still produces a usable recap.
    """

    session_date: date = Field(..., description="Trading session the snapshot describes")

    # Rates
    ust_2y: Optional[float] = Field(None, description="2Y US Treasury yield (%)")
    ust_10y: Optional[float] = Field(None, description="10Y US Treasury yield (%)")
    ust_30y: Optional[float] = Field(None, description="30Y US Treasury yield (%)")

    # HY index (ICE BofA US High Yield / Bloomberg HY 2% Capped, per config)
    hy_index_name: str = Field("ICE BofA US High Yield", description="HY index used")
    hy_oas_bps: Optional[float] = Field(None, description="HY option-adjusted spread (bps)")
    hy_oas_chg_bps: Optional[float] = Field(None, description="Day-over-day OAS change (bps)")
    hy_yield_pct: Optional[float] = Field(None, description="HY index effective yield (%)")
    hy_total_return_pct: Optional[float] = Field(None, description="HY index daily total return (%)")

    # Derivatives / IG context
    cdx_hy_price: Optional[float] = Field(None, description="CDX.NA.HY on-the-run price")
    cdx_hy_chg: Optional[float] = Field(None, description="CDX.NA.HY day change (price points)")
    ig_oas_bps: Optional[float] = Field(None, description="IG index OAS (bps)")

    # Technicals
    fund_flow_usd: Optional[float] = Field(
        None, description="HY mutual fund + ETF net flow for the day (USD)"
    )
    new_issue_volume_usd: Optional[float] = Field(
        None, description="HY primary market pricing volume for the day (USD)"
    )

    # Cross-asset
    sp500_chg_pct: Optional[float] = Field(None, description="S&P 500 daily change (%)")
    wti_chg_pct: Optional[float] = Field(None, description="WTI crude daily change (%)")

    tone: Optional[str] = Field(
        None, description="One-line qualitative read of the session (risk-on/off)"
    )


class BondPerformer(BaseModel):
    """A single issuer-level bond among the day's best/worst movers."""

    issuer: str = Field(..., description="Issuer / borrower name")
    ticker: Optional[str] = Field(None, description="Issuer ticker, if listed")
    cusip: Optional[str] = Field(None, description="Bond CUSIP/ISIN")
    description: Optional[str] = Field(
        None, description="Coupon and maturity, e.g. '7.25% 2031'"
    )
    sector: Optional[str] = Field(None, description="Industry sector")
    rating: Optional[str] = Field(None, description="Composite rating, e.g. 'B2/B'")

    direction: Direction = Field(..., description="Gainer or decliner")
    price: Optional[float] = Field(None, description="Closing dollar price")
    price_chg: Optional[float] = Field(None, description="Day price change (points)")
    spread_bps: Optional[float] = Field(None, description="Closing spread (bps)")
    spread_chg_bps: Optional[float] = Field(None, description="Day spread change (bps)")
    total_return_pct: Optional[float] = Field(None, description="Day total return (%)")

    reason: str = Field(
        ..., description="Company/credit-specific driver of the move (the 'why')"
    )


class NewsItem(BaseModel):
    """A notable event or headline relevant to HY credit."""

    headline: str = Field(..., description="Headline")
    summary: Optional[str] = Field(None, description="One or two sentence summary")
    category: Optional[str] = Field(
        None, description="e.g. 'ratings', 'M&A', 'earnings', 'macro', 'default'"
    )
    source: Optional[str] = Field(None, description="Publisher / source name")
    url: Optional[str] = Field(None, description="Link to the source")


class OutlookItem(BaseModel):
    """A single forward-looking item for the next session."""

    label: str = Field(..., description="What to watch, e.g. 'CPI 8:30am ET'")
    detail: Optional[str] = Field(None, description="Why it matters for HY")


class NextSessionOutlook(BaseModel):
    """What is expected for the next trading day."""

    next_session_date: date = Field(..., description="Next trading session")
    economic_calendar: List[OutlookItem] = Field(
        default_factory=list, description="Scheduled data / events"
    )
    primary_pipeline: List[OutlookItem] = Field(
        default_factory=list, description="Expected new-issue supply"
    )
    themes: List[OutlookItem] = Field(
        default_factory=list, description="Key credit themes / watch items"
    )
    summary: Optional[str] = Field(None, description="One-paragraph forward view")


class RecapReport(BaseModel):
    """The full daily recap document, ready to render and deliver."""

    session_date: date = Field(..., description="Trading day being recapped")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="UTC generation timestamp"
    )

    executive_summary: Optional[str] = Field(
        None, description="Top-of-note paragraph summarizing the session"
    )
    macro: MacroSnapshot = Field(..., description="Index & rates context")
    notable_news: List[NewsItem] = Field(
        default_factory=list, description="Notable events / news"
    )
    top_performers: List[BondPerformer] = Field(
        default_factory=list, description="Best performing HY bonds"
    )
    bottom_performers: List[BondPerformer] = Field(
        default_factory=list, description="Worst performing HY bonds"
    )
    outlook: NextSessionOutlook = Field(..., description="Next-session expectations")

    data_caveats: List[str] = Field(
        default_factory=list,
        description="Data provenance / coverage notes surfaced to the reader",
    )
