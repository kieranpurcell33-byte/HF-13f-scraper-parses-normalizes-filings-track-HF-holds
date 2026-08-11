"""Unit tests for the hy_recap package (no network access required)."""

from __future__ import annotations

from datetime import date
from typing import List

import pytest

from hy_recap.config import Settings
from hy_recap.generator import RecapGenerator, previous_business_day
from hy_recap.models import BondMove, MarketSnapshot, Recap, YieldPoint
from hy_recap.sources.base import (
    DataSource,
    SecurityMoversSource,
    SourceUnavailable,
)


# --- fakes ----------------------------------------------------------------
class FakeRates(DataSource):
    name = "FakeRates"

    def __init__(self, points):
        self._points = points

    def is_available(self):
        return True

    def fetch_points(self, session):
        return self._points


class BrokenRates(DataSource):
    name = "BrokenRates"

    def is_available(self):
        return True

    def fetch_points(self, session):
        raise SourceUnavailable("boom")


class FakeMovers(SecurityMoversSource):
    name = "FakeMovers"

    def is_available(self):
        return True

    def fetch_movers(self, session, top_n=5):
        g = [BondMove(issuer="ACME", price=101.0, price_change=1.25, driver="beat")]
        l = [BondMove(issuer="ZORP", price=72.0, price_change=-4.5, driver="downgrade")]
        return g, l


class UnavailMovers(SecurityMoversSource):
    name = "UnavailMovers"

    def is_available(self):
        return False

    def fetch_movers(self, session, top_n=5):  # pragma: no cover
        raise AssertionError("should not be called when unavailable")


# --- tests ----------------------------------------------------------------
@pytest.mark.unit
def test_previous_business_day_skips_weekend():
    # 2026-08-11 is a Tuesday -> Monday 08-10
    assert previous_business_day(date(2026, 8, 11)) == date(2026, 8, 10)
    # 2026-08-10 is a Monday -> Friday 08-07
    assert previous_business_day(date(2026, 8, 10)) == date(2026, 8, 7)
    # Sunday 08-09 -> Friday 08-07
    assert previous_business_day(date(2026, 8, 9)) == date(2026, 8, 7)


@pytest.mark.unit
def test_yieldpoint_render_units():
    assert "264 bps" in YieldPoint(label="HY OAS", value=264, unit="bps", change=-3).render()
    assert "▼ -3 bps" in YieldPoint(label="HY OAS", value=264, unit="bps", change=-3).render()
    assert "4.65%" in YieldPoint(label="UST 10Y", value=4.65, unit="%", change=0.02).render()
    assert "$77.00" in YieldPoint(label="WTI crude", value=77.0, unit="$/bbl", change=-1.1).render()
    assert "n/a" in YieldPoint(label="X", value=None, unit="%").render()


@pytest.mark.unit
def test_build_full_recap_with_movers_and_narrative():
    pts = [
        YieldPoint(label="HY OAS", value=264, unit="bps", change=-3, as_of=date(2026, 8, 10)),
        YieldPoint(label="UST 10Y", value=4.65, unit="%", change=0.0, as_of=date(2026, 8, 10)),
    ]
    gen = RecapGenerator(
        settings=Settings(),
        data_sources=[FakeRates(pts)],
        movers_source=FakeMovers(),
    )
    recap = gen.build(
        session_date=date(2026, 8, 10),
        delivery_date=date(2026, 8, 11),
        narrative={
            "notable_events": ["Dovish repricing after weak jobs report."],
            "outlook": ["CPI Wed Aug 12 is the swing factor."],
            "sources": ["https://example.com/a"],
            "fund_flow_note": "Largest inflow in a month",
        },
    )
    assert recap.session_date == date(2026, 8, 10)
    assert recap.top_gainers and recap.top_gainers[0].issuer == "ACME"
    assert recap.top_losers and recap.top_losers[0].issuer == "ZORP"
    assert recap.notable_events and recap.outlook
    assert recap.warnings == []  # nothing degraded

    md = gen.render_markdown(recap)
    assert "US High Yield Bond Market" in md
    assert "ACME" in md and "ZORP" in md
    assert "264 bps" in md
    assert "CPI Wed Aug 12" in md
    assert "Largest inflow in a month" in md


@pytest.mark.unit
def test_degrades_without_movers_feed_no_fabrication():
    pts = [YieldPoint(label="HY OAS", value=270, unit="bps", change=2, as_of=date(2026, 8, 10))]
    gen = RecapGenerator(
        settings=Settings(),
        data_sources=[FakeRates(pts)],
        movers_source=UnavailMovers(),
    )
    recap = gen.build(session_date=date(2026, 8, 10), delivery_date=date(2026, 8, 11))
    assert recap.top_gainers == [] and recap.top_losers == []
    # A warning must explain the gap, and no invented bond appears.
    assert any("movers" in w.lower() for w in recap.warnings)
    md = gen.render_markdown(recap)
    assert "Security-level movers unavailable" in md
    assert "_[feed]_" in md  # template, not fabricated prices


@pytest.mark.unit
def test_source_failure_is_captured_not_raised():
    gen = RecapGenerator(
        settings=Settings(),
        data_sources=[BrokenRates(), FakeRates([YieldPoint(label="UST 30Y", value=5.25, unit="%")])],
        movers_source=UnavailMovers(),
    )
    recap = gen.build(session_date=date(2026, 8, 10), delivery_date=date(2026, 8, 11))
    # Broken source recorded as a warning; the working one still contributes.
    assert any("BrokenRates" in w for w in recap.warnings)
    assert recap.snapshot.get("UST 30Y") is not None


@pytest.mark.unit
def test_first_source_wins_second_fills_gaps():
    a = FakeRates([YieldPoint(label="HY OAS", value=264, unit="bps")])
    b = FakeRates([
        YieldPoint(label="HY OAS", value=999, unit="bps"),  # should be ignored
        YieldPoint(label="UST 10Y", value=4.65, unit="%"),  # should fill
    ])
    gen = RecapGenerator(settings=Settings(), data_sources=[a, b], movers_source=UnavailMovers())
    recap = gen.build(session_date=date(2026, 8, 10), delivery_date=date(2026, 8, 11))
    assert recap.snapshot.get("HY OAS").value == 264
    assert recap.snapshot.get("UST 10Y").value == 4.65


@pytest.mark.unit
def test_editorial_levels_fill_gaps_and_warn():
    live = FakeRates([YieldPoint(label="HY OAS", value=264, unit="bps", change=-3)])
    gen = RecapGenerator(settings=Settings(), data_sources=[live], movers_source=UnavailMovers())
    recap = gen.build(
        session_date=date(2026, 8, 10),
        delivery_date=date(2026, 8, 11),
        narrative={
            "levels": [
                {"label": "HY OAS", "value": 999, "unit": "bps"},   # live wins, ignored
                {"label": "UST 10Y", "value": 4.65, "unit": "%"},   # fills gap
            ]
        },
    )
    assert recap.snapshot.get("HY OAS").value == 264  # live source preserved
    assert recap.snapshot.get("UST 10Y").value == 4.65  # editor filled
    assert any("Editor-supplied levels used" in w for w in recap.warnings)


@pytest.mark.unit
def test_bondmove_render_row_handles_missing_fields():
    row = BondMove(issuer="ACME", coupon=6.5, maturity="2031-05-15",
                   price=101.25, price_change=1.1, spread_change_bps=-15, driver="beat").render_row()
    assert "ACME 6.500 2031-05-15" in row
    assert "-15" in row
    # all-missing still renders em-dashes, no crash
    assert "—" in BondMove(issuer="X").render_row()
