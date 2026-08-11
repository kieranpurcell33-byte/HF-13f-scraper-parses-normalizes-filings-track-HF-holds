"""
Deterministic sample data sources.

These generate a fully-formed, *illustrative* recap so you can preview the
output format and run tests without a live feed. The numbers are synthetic and
clearly flagged as such via ``data_caveats`` on the report -- never present a
sample-sourced recap as real market data.
"""

from __future__ import annotations

from datetime import date
from typing import List, Tuple

from hy_recap.models import (
    BondPerformer,
    Direction,
    MacroSnapshot,
    NewsItem,
    NextSessionOutlook,
    OutlookItem,
)
from hy_recap.sources.base import (
    BondPerformanceSource,
    MacroSource,
    NewsSource,
    OutlookSource,
)

SAMPLE_CAVEAT = (
    "ILLUSTRATIVE SAMPLE DATA -- figures below are synthetic and for format "
    "preview only. Connect a licensed feed (set HY_*_SOURCE) for real numbers."
)


class SampleMacroSource(MacroSource):
    def get_macro(self, session_date: date) -> MacroSnapshot:
        return MacroSnapshot(
            session_date=session_date,
            ust_2y=3.92,
            ust_10y=4.65,
            ust_30y=5.25,
            hy_index_name="ICE BofA US High Yield",
            hy_oas_bps=281.0,
            hy_oas_chg_bps=-4.0,
            hy_yield_pct=7.38,
            hy_total_return_pct=0.18,
            cdx_hy_price=107.35,
            cdx_hy_chg=0.22,
            ig_oas_bps=84.0,
            fund_flow_usd=1_250_000_000.0,
            new_issue_volume_usd=3_400_000_000.0,
            sp500_chg_pct=0.41,
            wti_chg_pct=-1.10,
            tone="Risk-on; dovish rate repricing pulled spreads tighter into a firm bid.",
        )


class SampleNewsSource(NewsSource):
    def get_news(self, session_date: date) -> List[NewsItem]:
        return [
            NewsItem(
                headline="Soft payrolls report pares rate-hike bets, lifts credit",
                summary=(
                    "A weaker-than-expected employment print drove yields lower and "
                    "opened a hospitable window for issuers; HY caught a firm bid."
                ),
                category="macro",
                source="(sample)",
            ),
            NewsItem(
                headline="Record primary calendar as issuers rush the tighter window",
                summary="Multiple HY borrowers launched deals to lock in lower coupons.",
                category="primary",
                source="(sample)",
            ),
            NewsItem(
                headline="Ratings agency upgrades a large B-rated telecom to BB-",
                summary="Deleveraging and FCF inflection cited; bonds rallied on the news.",
                category="ratings",
                source="(sample)",
            ),
        ]


class SampleBondSource(BondPerformanceSource):
    def get_performers(
        self, session_date: date, top_n: int
    ) -> Tuple[List[BondPerformer], List[BondPerformer]]:
        gainers = [
            BondPerformer(
                issuer="Sample Telecom Holdings",
                ticker="SAMTL",
                description="7.25% 2031",
                sector="Telecom",
                rating="B2/B",
                direction=Direction.GAINER,
                price=98.4,
                price_chg=3.1,
                spread_bps=412.0,
                spread_chg_bps=-58.0,
                total_return_pct=3.2,
                reason="Upgraded to BB- on deleveraging; short squeeze in the 2031s.",
            ),
            BondPerformer(
                issuer="Sample Energy Partners",
                ticker="SAMEP",
                description="6.50% 2029",
                sector="Energy",
                rating="B1/B+",
                direction=Direction.GAINER,
                price=101.2,
                price_chg=1.8,
                spread_bps=345.0,
                spread_chg_bps=-31.0,
                total_return_pct=1.9,
                reason="Beat-and-raise earnings plus a bond tender at a premium.",
            ),
        ][:top_n]
        decliners = [
            BondPerformer(
                issuer="Sample Retail Corp",
                ticker="SAMRT",
                description="9.00% 2028",
                sector="Retail",
                rating="Caa1/CCC+",
                direction=Direction.DECLINER,
                price=71.5,
                price_chg=-6.4,
                spread_bps=980.0,
                spread_chg_bps=+145.0,
                total_return_pct=-8.1,
                reason="Guidance cut and covenant-amendment chatter; liquidity worries.",
            ),
            BondPerformer(
                issuer="Sample Healthcare Group",
                ticker="SAMHC",
                description="5.75% 2030",
                sector="Healthcare",
                rating="B3/B-",
                direction=Direction.DECLINER,
                price=88.9,
                price_chg=-2.7,
                spread_bps=560.0,
                spread_chg_bps=+64.0,
                total_return_pct=-2.9,
                reason="Reimbursement-rule headline and a sponsor dividend recap rumor.",
            ),
        ][:top_n]
        return gainers, decliners


class SampleOutlookSource(OutlookSource):
    def get_outlook(self, next_session_date: date) -> NextSessionOutlook:
        return NextSessionOutlook(
            next_session_date=next_session_date,
            economic_calendar=[
                OutlookItem(label="CPI, 8:30am ET", detail="Core print steers the rate path and HY beta."),
                OutlookItem(label="10Y Treasury auction, 1:00pm ET", detail="Duration demand read-through."),
            ],
            primary_pipeline=[
                OutlookItem(label="2-3 HY deals expected", detail="Refi-driven; watch reception as a risk gauge."),
            ],
            themes=[
                OutlookItem(label="Spread compression vs. tights", detail="OAS near multi-year lows; asymmetry to widening."),
                OutlookItem(label="Earnings dispersion", detail="Retail/healthcare idiosyncratic risk in focus."),
            ],
            summary=(
                "Expect a constructive-but-cautious open: tight spreads and firm technicals "
                "argue for carry, while CPI is the swing factor for rate-sensitive names."
            ),
        )
