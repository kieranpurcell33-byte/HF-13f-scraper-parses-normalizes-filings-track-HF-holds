"""
Lightweight US bond-market trading calendar.

Used to resolve "the previous trading day" and "the next trading day" without a
heavy dependency. Covers weekends plus SIFMA/NYSE full-close holidays. For a
production feed you may prefer ``pandas_market_calendars``; this keeps the recap
self-contained. Half-days (e.g. day after Thanksgiving) are treated as normal
trading days, which is correct for "previous/next session" resolution.
"""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache
from typing import Set


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The nth (1-based) given weekday of a month. weekday: Mon=0..Sun=6."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return d + timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    """The last given weekday of a month."""
    if month == 12:
        d = date(year, 12, 31)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)
    offset = (d.weekday() - weekday) % 7
    return d - timedelta(days=offset)


def _observed(d: date) -> date:
    """Shift a fixed-date holiday to its observed day (Sat->Fri, Sun->Mon)."""
    if d.weekday() == 5:  # Saturday
        return d - timedelta(days=1)
    if d.weekday() == 6:  # Sunday
        return d + timedelta(days=1)
    return d


def _easter(year: int) -> date:
    """Anonymous Gregorian algorithm; Good Friday = Easter - 2 days."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month = (h + m - 7 * n + 114) // 31
    day = ((h + m - 7 * n + 114) % 31) + 1
    return date(year, month, day)


@lru_cache(maxsize=32)
def market_holidays(year: int) -> Set[date]:
    """Full-close US bond/equity market holidays for a calendar year."""
    holidays = {
        _observed(date(year, 1, 1)),  # New Year's Day
        _nth_weekday(year, 1, 0, 3),  # MLK Day (3rd Mon Jan)
        _nth_weekday(year, 2, 0, 3),  # Presidents' Day (3rd Mon Feb)
        _easter(year) - timedelta(days=2),  # Good Friday
        _last_weekday(year, 5, 0),  # Memorial Day (last Mon May)
        _observed(date(year, 6, 19)),  # Juneteenth
        _observed(date(year, 7, 4)),  # Independence Day
        _nth_weekday(year, 9, 0, 1),  # Labor Day (1st Mon Sep)
        _nth_weekday(year, 11, 3, 4),  # Thanksgiving (4th Thu Nov)
        _observed(date(year, 12, 25)),  # Christmas
    }
    return holidays


def is_trading_day(d: date) -> bool:
    """True if ``d`` is a weekday and not a full-close market holiday."""
    if d.weekday() >= 5:
        return False
    return d not in market_holidays(d.year)


def previous_trading_day(d: date) -> date:
    """The most recent trading day strictly before ``d``."""
    cur = d - timedelta(days=1)
    while not is_trading_day(cur):
        cur -= timedelta(days=1)
    return cur


def next_trading_day(d: date) -> date:
    """The next trading day strictly after ``d``."""
    cur = d + timedelta(days=1)
    while not is_trading_day(cur):
        cur += timedelta(days=1)
    return cur
