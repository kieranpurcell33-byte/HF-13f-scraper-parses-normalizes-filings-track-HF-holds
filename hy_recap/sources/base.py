"""
Abstract data-source interfaces for the recap pipeline.

The builder depends only on these four protocols, so any feed -- Bloomberg,
ICE, FINRA TRACE, a REST gateway, or the bundled sample generator -- can supply
the data as long as it returns the ``hy_recap.models`` shapes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Tuple

from hy_recap.models import (
    BondPerformer,
    MacroSnapshot,
    NewsItem,
    NextSessionOutlook,
)


class MacroSource(ABC):
    """Provides index-level and rates context for a session."""

    @abstractmethod
    def get_macro(self, session_date: date) -> MacroSnapshot:
        """Return the macro/index snapshot for ``session_date``."""


class BondPerformanceSource(ABC):
    """Provides issuer-level best/worst movers for a session.

    This is the section that requires a licensed security-level price/spread
    feed (TRACE / Bloomberg / ICE).
    """

    @abstractmethod
    def get_performers(
        self, session_date: date, top_n: int
    ) -> Tuple[List[BondPerformer], List[BondPerformer]]:
        """Return ``(top_gainers, top_decliners)`` for ``session_date``."""


class NewsSource(ABC):
    """Provides notable HY-relevant events/news for a session."""

    @abstractmethod
    def get_news(self, session_date: date) -> List[NewsItem]:
        """Return notable news items for ``session_date``."""


class OutlookSource(ABC):
    """Provides forward-looking expectations for the next session."""

    @abstractmethod
    def get_outlook(self, next_session_date: date) -> NextSessionOutlook:
        """Return the outlook for ``next_session_date``."""
