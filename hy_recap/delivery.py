"""
Write the rendered recap to disk (and, optionally, hand it to a delivery hook).

Filenames follow ``hy_recap_YYYY-MM-DD.md`` for the recapped session, which makes
them naturally sortable and idempotent for a scheduled job.

Delivery to an external destination (Google Drive, email, S3, Slack) is left as
a pluggable hook so credentials stay in your environment/scheduler rather than
in this module. See ``docs/HY_RECAP.md`` for wiring the 07:15 ET job.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def output_filename(session_date: date, ext: str = "md") -> str:
    return f"hy_recap_{session_date.isoformat()}.{ext}"


def write_recap(
    content: str,
    session_date: date,
    output_dir: str = "./output/hy_recap",
    ext: str = "md",
) -> Path:
    """Write ``content`` to ``output_dir`` and return the path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / output_filename(session_date, ext)
    path.write_text(content, encoding="utf-8")
    logger.info("Wrote recap to %s (%d bytes)", path, len(content))
    return path


def deliver(path: Path, destination: Optional[str] = None) -> None:
    """Hand the written file to an external destination.

    This is a hook, not an implementation: it logs by default. Wire your
    Google Drive / email / Slack push here (the Drive MCP connector, an SMTP
    call, etc.). Kept credential-free so nothing sensitive lands in the repo.
    """
    if not destination:
        logger.info("No delivery destination configured; file left at %s", path)
        return
    logger.info("Delivery hook invoked for destination=%s, file=%s", destination, path)
    # e.g. upload_to_drive(path, folder_id=destination) — implement per your stack.
