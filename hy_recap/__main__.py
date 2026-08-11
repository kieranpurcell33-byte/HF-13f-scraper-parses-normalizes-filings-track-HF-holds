"""CLI: ``python -m hy_recap`` — generate the HY daily recap.

Examples
--------
    # Auto: previous business day, live feeds, write to ./reports
    python -m hy_recap

    # Supply the editorial narrative (events/outlook/sources) as JSON
    python -m hy_recap --narrative narrative.json

    # Backfill a specific session
    python -m hy_recap --session-date 2026-08-10 --delivery-date 2026-08-11
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from .config import Settings
from .generator import RecapGenerator


def _parse_date(s: str | None):
    return date.fromisoformat(s) if s else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hy_recap", description=__doc__)
    ap.add_argument("--session-date", help="Session to recap (YYYY-MM-DD).")
    ap.add_argument("--delivery-date", help="Delivery date (YYYY-MM-DD).")
    ap.add_argument("--narrative", help="Path to JSON with events/outlook/sources.")
    ap.add_argument("--out", help="Output directory (default: reports/).")
    ap.add_argument(
        "--print", action="store_true", help="Print the Markdown to stdout."
    )
    args = ap.parse_args(argv)

    narrative = None
    if args.narrative:
        with open(args.narrative, encoding="utf-8") as fh:
            narrative = json.load(fh)

    gen = RecapGenerator(Settings())
    recap = gen.build(
        session_date=_parse_date(args.session_date),
        delivery_date=_parse_date(args.delivery_date),
        narrative=narrative,
    )
    path = gen.write(recap, output_dir=args.out)

    if args.print:
        print(gen.render_markdown(recap))
    else:
        print(f"Wrote {path}")

    if recap.warnings:
        print(f"\n{len(recap.warnings)} data warning(s):", file=sys.stderr)
        for w in recap.warnings:
            print(f"  - {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
