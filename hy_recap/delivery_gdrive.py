"""
Google Drive delivery for the daily HY recap.

Uploads the rendered recap to a Drive folder using a **service account**, which
is what an unattended 07:15 ET job (cron / GitHub Actions) needs -- interactive
OAuth connectors don't work headless. Credentials come from the environment, so
nothing sensitive lands in the repo.

Setup (one-time):
  1. Create a Google Cloud service account and download its JSON key.
  2. Enable the Google Drive API for the project.
  3. Share the target Drive folder with the service account's email
     (…@….iam.gserviceaccount.com) as Editor. For Shared Drives, add the
     service account as a member.
  4. Export ``GOOGLE_APPLICATION_CREDENTIALS=/path/key.json`` and
     ``HY_DRIVE_FOLDER_ID=<folder id>``.

Install the extra deps: ``pip install -r requirements-drive.txt``.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
_MARKDOWN_MIME = "text/markdown"
_GDOC_MIME = "application/vnd.google-apps.document"


@dataclass
class DriveUploadResult:
    file_id: str
    name: str
    web_view_link: Optional[str] = None


def _build_service(credentials_path: Optional[str]):
    """Build an authenticated Drive v3 service from a service-account key."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as exc:  # pragma: no cover - exercised via message only
        raise RuntimeError(
            "Google Drive delivery needs extra packages. Install them with:\n"
            "  pip install -r requirements-drive.txt"
        ) from exc

    key_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key_path:
        raise RuntimeError(
            "Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON key "
            "(or pass credentials_path)."
        )
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=_SCOPES)
    # cache_discovery=False avoids a noisy warning in headless jobs.
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _default_media_factory(path: str):
    """Build a resumable-free MediaFileUpload for the Markdown file."""
    from googleapiclient.http import MediaFileUpload  # optional dep

    return MediaFileUpload(path, mimetype=_MARKDOWN_MIME, resumable=False)


def upload_markdown_to_drive(
    path: Path | str,
    folder_id: Optional[str] = None,
    *,
    credentials_path: Optional[str] = None,
    as_google_doc: bool = False,
    share_with: Optional[List[str]] = None,
    service: Any = None,
    media_factory: Optional[Callable[[str], Any]] = None,
) -> DriveUploadResult:
    """Upload ``path`` to Google Drive and return the created file's metadata.

    Args:
        path: Local Markdown file to upload.
        folder_id: Destination Drive folder id (defaults to HY_DRIVE_FOLDER_ID).
        credentials_path: Service-account JSON key (defaults to env var).
        as_google_doc: If True, convert the Markdown into a native Google Doc;
            otherwise store the raw ``.md`` file.
        share_with: Optional emails to grant reader access (handy when the file
            is owned by the service account).
        service: Pre-built Drive service (dependency injection for tests).
        media_factory: Builds the upload media from a path (injection for tests).
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Recap file not found: {path}")
    folder_id = folder_id or os.environ.get("HY_DRIVE_FOLDER_ID")

    if service is None:
        service = _build_service(credentials_path)

    metadata: dict[str, Any] = {"name": path.name}
    if as_google_doc:
        metadata["name"] = path.stem  # Docs don't carry a file extension
        metadata["mimeType"] = _GDOC_MIME
    if folder_id:
        metadata["parents"] = [folder_id]

    media = (media_factory or _default_media_factory)(str(path))
    created = (
        service.files()
        .create(
            body=metadata,
            media_body=media,
            fields="id,name,webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )

    file_id = created["id"]
    for email in share_with or []:
        service.permissions().create(
            fileId=file_id,
            body={"type": "user", "role": "reader", "emailAddress": email},
            sendNotificationEmail=False,
            supportsAllDrives=True,
        ).execute()

    result = DriveUploadResult(
        file_id=file_id,
        name=created.get("name", path.name),
        web_view_link=created.get("webViewLink"),
    )
    logger.info("Uploaded recap to Drive: %s (%s)", result.name, result.web_view_link or result.file_id)
    return result
