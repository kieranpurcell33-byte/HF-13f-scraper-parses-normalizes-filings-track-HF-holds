"""
Command-line entrypoint for generating the daily HY recap.

Examples::

    # Recap the previous trading day (default), sample data, print to stdout
    python -m hy_recap

    # Recap a specific session and write to the output dir
    python -m hy_recap --date 2026-08-10 --write

    # Use your live gateway for every section
    HY_MACRO_SOURCE=rest HY_BOND_SOURCE=rest HY_NEWS_SOURCE=rest \
    HY_OUTLOOK_SOURCE=rest HY_REST_BASE_URL=https://feed.internal/hy \
    python -m hy_recap --write
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime

from hy_recap.builder import RecapBuilder
from hy_recap.config import RecapConfig
from hy_recap.delivery import deliver, write_recap
from hy_recap.renderer import render_markdown


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:  # pragma: no cover - argparse surfaces the message
        raise argparse.ArgumentTypeError(f"Invalid date '{value}', expected YYYY-MM-DD") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hy_recap", description="Generate the US HY bond daily recap."
    )
    parser.add_argument(
        "--date",
        type=_parse_date,
        default=None,
        help="Session to recap (YYYY-MM-DD). Default: previous trading day.",
    )
    parser.add_argument(
        "--write", action="store_true", help="Write the recap to the output directory."
    )
    parser.add_argument(
        "--deliver", metavar="DEST", default=None, help="Invoke the delivery hook with DEST."
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = RecapConfig()
    missing = config.missing_credentials()
    if missing:
        print(
            "WARNING: missing credentials for selected non-sample sources: "
            + ", ".join(missing),
            file=sys.stderr,
        )

    builder = RecapBuilder(config=config)
    report = builder.build(session_date=args.date)
    markdown = render_markdown(report)

    if args.write:
        path = write_recap(markdown, report.session_date, config.output_dir)
        print(f"Wrote {path}", file=sys.stderr)
        if args.deliver:
            deliver(path, args.deliver)
    else:
        print(markdown)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
