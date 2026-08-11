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
import os
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

    Destination is a scheme-prefixed string so one flag can target different
    backends. Credentials always come from the environment, never arguments:

      * ``drive`` or ``drive:<folder_id>`` -> upload to Google Drive
        (service account; see ``delivery_gdrive``). Without an explicit folder
        id, ``HY_DRIVE_FOLDER_ID`` is used.
      * anything else -> logged as an unrecognized destination (extend below
        for email / Slack / S3).
    """
    if not destination:
        logger.info("No delivery destination configured; file left at %s", path)
        return

    scheme, _, arg = destination.partition(":")
    if scheme == "drive":
        # Imported lazily so non-Drive runs don't require the Google deps.
        from hy_recap.delivery_gdrive import upload_markdown_to_drive

        as_doc = os.environ.get("HY_DRIVE_AS_DOC", "").lower() in ("1", "true", "yes")
        result = upload_markdown_to_drive(
            path, folder_id=arg or None, as_google_doc=as_doc
        )
        logger.info("Delivered to Google Drive: %s", result.web_view_link or result.file_id)
        return

    logger.warning("Unrecognized delivery destination '%s'; file left at %s", destination, path)
