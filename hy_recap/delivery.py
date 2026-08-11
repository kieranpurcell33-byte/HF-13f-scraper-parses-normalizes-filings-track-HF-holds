"""Email delivery for the HY recap (self-contained SMTP, no external connector).

Sends the rendered Markdown as a multipart text/HTML email. Configuration is
env-driven so both the GitHub Action and a scheduled session can deliver by
setting secrets — nothing is hard-coded.

Environment variables
----------------------
SMTP_HOST                SMTP server host (e.g. smtp.gmail.com)
SMTP_PORT                Port (default 587 for STARTTLS; 465 for SSL)
SMTP_USER                Username / login
SMTP_PASSWORD            Password or app-specific token
SMTP_USE_SSL             "1" to use implicit SSL (port 465) instead of STARTTLS
EMAIL_FROM               From address (default: SMTP_USER)
EMAIL_TO                 Comma-separated recipient list (required to send)

If required settings are missing, :func:`send_recap_email` returns ``False`` and
records the reason — it never raises, so a delivery failure cannot break report
generation.
"""

from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass, field
from email.message import EmailMessage
from html import escape
from typing import List, Optional


@dataclass
class EmailConfig:
    host: Optional[str] = field(default_factory=lambda: os.getenv("SMTP_HOST") or None)
    port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT") or "587"))
    user: Optional[str] = field(default_factory=lambda: os.getenv("SMTP_USER") or None)
    password: Optional[str] = field(
        default_factory=lambda: os.getenv("SMTP_PASSWORD") or None
    )
    use_ssl: bool = field(
        default_factory=lambda: (os.getenv("SMTP_USE_SSL") or "") in ("1", "true", "True")
    )
    sender: Optional[str] = field(
        default_factory=lambda: os.getenv("EMAIL_FROM") or os.getenv("SMTP_USER") or None
    )
    recipients: List[str] = field(
        default_factory=lambda: [
            r.strip() for r in (os.getenv("EMAIL_TO") or "").split(",") if r.strip()
        ]
    )

    def missing(self) -> List[str]:
        need = {
            "SMTP_HOST": self.host,
            "SMTP_USER": self.user,
            "SMTP_PASSWORD": self.password,
            "EMAIL_TO": self.recipients,
        }
        return [k for k, v in need.items() if not v]


def _markdown_to_html(md: str) -> str:
    """Best-effort Markdown→HTML. Uses the ``markdown`` lib if present, else a
    monospace ``<pre>`` fallback so tables stay aligned in any client."""
    try:
        import markdown  # type: ignore

        body = markdown.markdown(md, extensions=["tables"])
    except Exception:
        body = f"<pre style='font-family:ui-monospace,monospace;font-size:13px'>{escape(md)}</pre>"
    return (
        "<html><body style='max-width:820px;margin:auto;"
        "font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#111'>"
        f"{body}</body></html>"
    )


def send_recap_email(
    markdown_body: str,
    subject: str,
    config: Optional[EmailConfig] = None,
) -> tuple[bool, str]:
    """Send the recap by email. Returns ``(sent, message)`` and never raises."""
    cfg = config or EmailConfig()
    missing = cfg.missing()
    if missing:
        return False, f"email not sent — missing config: {', '.join(missing)}"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg.sender
    msg["To"] = ", ".join(cfg.recipients)
    msg.set_content(markdown_body)  # text/plain fallback
    msg.add_alternative(_markdown_to_html(markdown_body), subtype="html")

    try:
        if cfg.use_ssl:
            with smtplib.SMTP_SSL(cfg.host, cfg.port, timeout=30) as s:
                s.login(cfg.user, cfg.password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(cfg.host, cfg.port, timeout=30) as s:
                s.starttls()
                s.login(cfg.user, cfg.password)
                s.send_message(msg)
    except Exception as exc:  # network / auth / TLS — report, don't crash
        return False, f"email send failed: {exc}"

    return True, f"emailed to {', '.join(cfg.recipients)}"
