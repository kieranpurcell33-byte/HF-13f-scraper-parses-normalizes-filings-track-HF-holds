"""Tests for the hy_recap daily high-yield recap pipeline."""

from datetime import date

import pytest

from hy_recap import RecapBuilder, RecapConfig, render_markdown
from hy_recap.calendar_util import (
    is_trading_day,
    next_trading_day,
    previous_trading_day,
)
from hy_recap.delivery import output_filename, write_recap
from hy_recap.models import Direction


# --- Trading calendar ------------------------------------------------------

def test_weekend_is_not_a_trading_day():
    assert not is_trading_day(date(2026, 8, 8))   # Saturday
    assert not is_trading_day(date(2026, 8, 9))   # Sunday
    assert is_trading_day(date(2026, 8, 10))      # Monday


def test_previous_trading_day_skips_weekend():
    # Monday 2026-08-10 -> previous session is Friday 2026-08-07
    assert previous_trading_day(date(2026, 8, 10)) == date(2026, 8, 7)


def test_next_trading_day_skips_weekend():
    # Friday 2026-08-07 -> next session is Monday 2026-08-10
    assert next_trading_day(date(2026, 8, 7)) == date(2026, 8, 10)


def test_holiday_is_skipped():
    # 2026-01-01 New Year's Day is a full-close holiday.
    assert not is_trading_day(date(2026, 1, 1))
    # Independence Day 2026 falls on Saturday -> observed Friday 7/3.
    assert not is_trading_day(date(2026, 7, 3))


def test_good_friday_is_a_holiday():
    # Good Friday 2026 = 2026-04-03.
    assert not is_trading_day(date(2026, 4, 3))


# --- Builder ---------------------------------------------------------------

def test_build_previous_trading_day_from_reference():
    report = RecapBuilder().build(as_of=date(2026, 8, 11))  # Tuesday
    assert report.session_date == date(2026, 8, 10)         # Monday
    assert report.outlook.next_session_date == date(2026, 8, 11)


def test_build_explicit_date():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    assert report.session_date == date(2026, 8, 10)
    assert report.top_performers and report.bottom_performers
    assert report.top_performers[0].direction == Direction.GAINER
    assert report.bottom_performers[0].direction == Direction.DECLINER


def test_sample_report_flags_synthetic_data():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    assert any("SAMPLE" in c.upper() for c in report.data_caveats)


def test_executive_summary_mentions_index_move():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    assert "%" in report.executive_summary


# --- Rendering -------------------------------------------------------------

def test_render_markdown_has_all_four_sections():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    md = render_markdown(report)
    assert "Notable events & news" in md
    assert "Best & worst performing HY bonds" in md
    assert "Market context" in md
    assert "Expected for the next trading day" in md


def test_render_markdown_is_nonempty_and_dated():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    md = render_markdown(report)
    assert md.startswith("# US High Yield Daily Recap")
    assert "August 10, 2026" in md
    # List items should be on separate lines (whitespace-control regression guard).
    assert "[(sample)]\n" in md


# --- Config & delivery -----------------------------------------------------

def test_config_defaults_to_sample():
    cfg = RecapConfig()
    assert cfg.bond_source == "sample"
    assert cfg.missing_credentials() == []


def test_config_reports_missing_rest_credentials(monkeypatch):
    monkeypatch.setenv("HY_BOND_SOURCE", "rest")
    monkeypatch.delenv("HY_REST_BASE_URL", raising=False)
    cfg = RecapConfig()
    assert "HY_REST_BASE_URL" in cfg.missing_credentials()


def test_output_filename_format():
    assert output_filename(date(2026, 8, 10)) == "hy_recap_2026-08-10.md"


def test_write_recap_roundtrip(tmp_path):
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    md = render_markdown(report)
    path = write_recap(md, report.session_date, output_dir=str(tmp_path))
    assert path.exists()
    assert path.read_text(encoding="utf-8") == md


def test_unknown_source_raises(monkeypatch):
    monkeypatch.setenv("HY_MACRO_SOURCE", "does-not-exist")
    with pytest.raises(ValueError):
        RecapBuilder(config=RecapConfig())
