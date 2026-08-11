"""
Assemble a :class:`RecapReport` from the configured data sources.

The builder is deliberately thin: it resolves which session to recap, pulls each
section, records data-provenance caveats, and hands back a validated report. All
market logic lives behind the source interfaces.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import List, Optional

from hy_recap.calendar_util import next_trading_day, previous_trading_day
from hy_recap.config import RecapConfig
from hy_recap.models import RecapReport
from hy_recap.sources.registry import Sources, build_sources
from hy_recap.sources.sample import SAMPLE_CAVEAT

logger = logging.getLogger(__name__)


class RecapBuilder:
    """Builds the daily recap for a target session."""

    def __init__(self, config: Optional[RecapConfig] = None, sources: Optional[Sources] = None):
        self.config = config or RecapConfig()
        self.sources = sources or build_sources(self.config)

    def _caveats(self) -> List[str]:
        cfg = self.config
        caveats: List[str] = []
        if "sample" in {
            cfg.bond_source,
            cfg.macro_source,
            cfg.news_source,
            cfg.outlook_source,
        }:
            caveats.append(SAMPLE_CAVEAT)
        caveats.append(
            "Issuer-level moves reflect the configured bond feed "
            f"(HY_BOND_SOURCE={cfg.bond_source}); index/spread levels are as reported by the feed."
        )
        return caveats

    def build(self, session_date: Optional[date] = None, as_of: Optional[date] = None) -> RecapReport:
        """Build the recap.

        Args:
            session_date: The session to recap. If omitted, uses the trading day
                before ``as_of`` (which defaults to today) -- i.e. "the previous
                trading day".
            as_of: Reference date for resolving the previous session.
        """
        if session_date is None:
            reference = as_of or date.today()
            session_date = previous_trading_day(reference)

        next_session = next_trading_day(session_date)
        logger.info("Building HY recap for %s (next session %s)", session_date, next_session)

        macro = self.sources.macro.get_macro(session_date)
        gainers, decliners = self.sources.bonds.get_performers(session_date, self.config.top_n)
        news = self.sources.news.get_news(session_date)
        outlook = self.sources.outlook.get_outlook(next_session)

        summary = self._executive_summary(macro, gainers, decliners)

        return RecapReport(
            session_date=session_date,
            executive_summary=summary,
            macro=macro,
            notable_news=news,
            top_performers=gainers,
            bottom_performers=decliners,
            outlook=outlook,
            data_caveats=self._caveats(),
        )

    @staticmethod
    def _executive_summary(macro, gainers, decliners) -> str:
        """Compose a one-paragraph lead from the numbers, defensively."""
        parts: List[str] = []
        if macro.hy_total_return_pct is not None:
            parts.append(
                f"The {macro.hy_index_name} index returned "
                f"{macro.hy_total_return_pct:+.2f}% on the day"
            )
        if macro.hy_oas_bps is not None and macro.hy_oas_chg_bps is not None:
            parts.append(
                f"OAS {'tightened' if macro.hy_oas_chg_bps < 0 else 'widened'} "
                f"{abs(macro.hy_oas_chg_bps):.0f}bp to {macro.hy_oas_bps:.0f}bp"
            )
        lead = ("; ".join(parts) + ".") if parts else "HY session recap."
        if macro.tone:
            lead += f" {macro.tone}"
        if gainers:
            lead += f" Best bid: {gainers[0].issuer}."
        if decliners:
            lead += f" Weakest: {decliners[0].issuer}."
        return lead
