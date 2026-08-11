"""Assemble and render the HY daily recap from configured data sources."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .config import Settings
from .models import BondMove, MarketSnapshot, Recap, YieldPoint
from .sources import (
    DataSource,
    FredSource,
    SecurityMoversSource,
    SourceUnavailable,
    TraceMoversSource,
    TreasuryParYieldSource,
)

# Preferred display order for snapshot rows.
_POINT_ORDER = ["HY OAS", "HY yield-to-worst", "UST 10Y", "UST 30Y", "WTI crude"]


def previous_business_day(ref: date) -> date:
    """Previous weekday before ``ref`` (Mon→Fri). Does not adjust for holidays."""
    d = ref - timedelta(days=1)
    while d.weekday() >= 5:  # 5=Sat, 6=Sun
        d -= timedelta(days=1)
    return d


class RecapGenerator:
    """Builds a :class:`Recap` and renders it to Markdown.

    Narrative sections (notable events, outlook, fund-flow note, sources) are not
    inferable from price feeds; pass them in via ``narrative`` (e.g. from a
    morning LLM/editorial step). When absent, the section renders a clearly
    marked placeholder and a warning — never invented copy.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        data_sources: Optional[Sequence[DataSource]] = None,
        movers_source: Optional[SecurityMoversSource] = None,
    ):
        self.settings = settings or Settings()
        if data_sources is None:
            data_sources = [
                FredSource(self.settings.fred_api_key, self.settings.http_timeout),
                TreasuryParYieldSource(self.settings.http_timeout),
            ]
        self.data_sources = list(data_sources)

        if movers_source is None and self.settings.movers_provider == "finra":
            movers_source = TraceMoversSource(
                self.settings.finra_client_id,
                self.settings.finra_client_secret,
                timeout=self.settings.http_timeout,
            )
        self.movers_source = movers_source

    # ---- build -----------------------------------------------------------
    def _collect_points(self, session: date, warnings: List[str]) -> List[YieldPoint]:
        merged: Dict[str, YieldPoint] = {}
        for src in self.data_sources:
            if not src.is_available():
                warnings.append(f"{src.name}: unavailable (not configured); skipped.")
                continue
            try:
                for p in src.fetch_points(session):
                    # First source to provide a label wins; later sources only
                    # fill genuine gaps.
                    if p.label not in merged:
                        merged[p.label] = p
            except SourceUnavailable as exc:
                warnings.append(f"{src.name}: {exc}")
            except Exception as exc:  # defensive: never let one source crash the run
                warnings.append(f"{src.name}: unexpected error: {exc}")

        ordered = [merged[l] for l in _POINT_ORDER if l in merged]
        ordered += [p for l, p in merged.items() if l not in _POINT_ORDER]
        if not ordered:
            warnings.append(
                "No rate/spread source produced data; snapshot left blank."
            )
        return ordered

    def _apply_editorial_levels(
        self,
        points: List[YieldPoint],
        narrative: dict,
        warnings: List[str],
    ) -> List[YieldPoint]:
        """Fill gaps with editor-supplied levels (``narrative['levels']``).

        Used when the live feed is unreachable or an editor wants to pin a
        triangulated level. These fill only labels the live sources did not
        provide, and their use is recorded as a warning so provenance is never
        silent.
        """
        raw = narrative.get("levels") or []
        if not raw:
            return points
        have = {p.label for p in points}
        added: List[str] = []
        for item in raw:
            try:
                yp = YieldPoint(**item)
            except Exception as exc:  # skip malformed entries, keep going
                warnings.append(f"Editorial level skipped ({item!r}): {exc}")
                continue
            if yp.label in have:
                continue
            points.append(yp)
            have.add(yp.label)
            added.append(yp.label)
        if added:
            ordered = [p for l in _POINT_ORDER for p in points if p.label == l]
            ordered += [p for p in points if p.label not in _POINT_ORDER]
            warnings.append(
                "Editor-supplied levels used (live feed did not cover): "
                + ", ".join(added)
                + ". These are triangulated, not live terminal marks."
            )
            return ordered
        return points

    def _collect_movers(
        self, session: date, warnings: List[str]
    ) -> tuple[List[BondMove], List[BondMove]]:
        if self.movers_source is None or not self.movers_source.is_available():
            warnings.append(
                "Security-level movers: no entitled feed configured. Best/worst "
                "named bonds require FINRA TRACE (FINRA_API_CLIENT_ID/SECRET) or a "
                "vendor feed (ICE/Markit/Bloomberg). Section left as template."
            )
            return [], []
        try:
            return self.movers_source.fetch_movers(session)
        except SourceUnavailable as exc:
            warnings.append(f"{self.movers_source.name}: {exc}")
            return [], []
        except Exception as exc:  # defensive
            warnings.append(f"{self.movers_source.name}: unexpected error: {exc}")
            return [], []

    def build(
        self,
        session_date: Optional[date] = None,
        delivery_date: Optional[date] = None,
        narrative: Optional[dict] = None,
    ) -> Recap:
        delivery = delivery_date or date.today()
        session = session_date or previous_business_day(delivery)
        narrative = narrative or {}
        warnings: List[str] = []

        points = self._collect_points(session, warnings)
        points = self._apply_editorial_levels(points, narrative, warnings)
        gainers, losers = self._collect_movers(session, warnings)

        snapshot = MarketSnapshot(
            session_date=session,
            points=points,
            fund_flow_note=narrative.get("fund_flow_note"),
        )

        notable = list(narrative.get("notable_events", []))
        outlook = list(narrative.get("outlook", []))
        if not notable:
            warnings.append(
                "Notable events not supplied; provide narrative['notable_events'] "
                "from the morning editorial/LLM step."
            )
        if not outlook:
            warnings.append(
                "Outlook not supplied; provide narrative['outlook'] from the "
                "morning editorial/LLM step."
            )

        return Recap(
            session_date=session,
            delivery_date=delivery,
            snapshot=snapshot,
            top_gainers=gainers,
            top_losers=losers,
            notable_events=notable,
            outlook=outlook,
            sources=list(narrative.get("sources", [])),
            warnings=warnings,
        )

    # ---- render ----------------------------------------------------------
    def render_markdown(self, recap: Recap) -> str:
        s = recap.snapshot
        lines: List[str] = []
        A = lines.append

        A("# US High Yield Bond Market — Daily Recap")
        A("")
        A(f"**Delivery:** {recap.delivery_date:%A, %B %d, %Y} (before 07:15 AM EST)")
        A(f"**Session covered:** {recap.session_date:%A, %B %d, %Y}")
        A("**Prepared:** Pre-market — auto-generated by `hy_recap`")
        A("")
        A("---")
        A("")

        # 1. Snapshot
        A("## 1. Snapshot")
        A("")
        if s.points:
            A("| Metric | Level | Day-over-day |")
            A("|---|---|---|")
            for p in s.points:
                A(p.render())
            if s.fund_flow_note:
                A(f"| HY fund flows | {s.fund_flow_note} | — |")
        else:
            A("_No market levels available — all rate/spread sources were "
              "unavailable. See Data Provenance below._")
        A("")
        A("---")
        A("")

        # 2. Notable events
        A("## 2. Most Notable Events / News")
        A("")
        if recap.notable_events:
            for e in recap.notable_events:
                A(f"- {e}")
        else:
            A("_Narrative not supplied for this run. Populate "
              "`narrative['notable_events']` from the morning editorial/LLM step._")
        A("")
        A("---")
        A("")

        # 3. Best/worst bonds
        A("## 3. Best & Worst Performing HY Bonds (company/credit-specific)")
        A("")
        if recap.top_gainers or recap.top_losers:
            A("**Top gainers**")
            A("")
            A("| Bond | CUSIP | Price | Δ Price | Δ Spread (bps) | Driver |")
            A("|---|---|---|---|---|---|")
            for m in recap.top_gainers:
                A(m.render_row())
            A("")
            A("**Top decliners**")
            A("")
            A("| Bond | CUSIP | Price | Δ Price | Δ Spread (bps) | Driver |")
            A("|---|---|---|---|---|---|")
            for m in recap.top_losers:
                A(m.render_row())
        else:
            A("> **Security-level movers unavailable for this run.** Best/worst "
              "named bonds require an entitled TRACE feed or a vendor "
              "(ICE/Markit/Bloomberg). No prices are asserted. Template:")
            A("")
            A("| Rank | Bond | CUSIP | Δ Price | Δ Spread | Driver |")
            A("|---|---|---|---|---|---|")
            A("| Top gainer | _[feed]_ | | | | _upgrade / beat / M&A / tender_ |")
            A("| Top decliner | _[feed]_ | | | | _downgrade / guidance cut / distress_ |")
        A("")
        A("---")
        A("")

        # 4. Outlook
        A("## 4. What's Expected — Next Trading Day & Week Ahead")
        A("")
        if recap.outlook:
            for o in recap.outlook:
                A(f"- {o}")
        else:
            A("_Narrative not supplied for this run. Populate "
              "`narrative['outlook']` from the morning editorial/LLM step._")
        A("")
        A("---")
        A("")

        # 5. Provenance / warnings
        A("## 5. Data Provenance & Caveats")
        A("")
        if s.points:
            asof = ", ".join(sorted({p.as_of.isoformat() for p in s.points if p.as_of}))
            A(f"- Market levels as-of {asof or 'n/a'}. Per-source provenance "
              "(live feed vs. editor-supplied) is listed in the warnings below.")
        if recap.warnings:
            A("- **Warnings / data gaps this run:**")
            for w in recap.warnings:
                A(f"  - {w}")
        else:
            A("- No data gaps this run.")
        A("")

        if recap.sources:
            A("## Sources")
            A("")
            for src in recap.sources:
                A(f"- {src}")
            A("")

        A("*Auto-generated by the `hy_recap` pipeline. Not investment advice. "
          "Verify all levels against a terminal before trading.*")
        A("")
        return "\n".join(lines)

    def write(self, recap: Recap, output_dir: Optional[str] = None) -> Path:
        out_dir = Path(output_dir or self.settings.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{recap.delivery_date.isoformat()}_US_HY_Daily_Recap.md"
        path = out_dir / fname
        path.write_text(self.render_markdown(recap), encoding="utf-8")
        return path
