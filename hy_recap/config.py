"""
Environment-driven configuration for the HY recap pipeline.

Secrets (API keys, service-account paths) are read from environment variables
only -- never committed. Copy ``.env.hy_recap.example`` to ``.env`` and fill in
your feed credentials, or export the variables in your scheduler.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

try:  # optional: load a local .env if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


def _get(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.environ.get(name)
    return val if val not in (None, "") else default


@dataclass
class RecapConfig:
    """Resolved configuration for a single recap run."""

    # Which adapter provides each section. "sample" renders deterministic
    # synthetic data (for format previews/tests). "rest" drives the generic
    # HTTP adapter against your own data gateway. Extend with "bloomberg",
    # "ice", "trace" by registering adapters in ``sources.registry``.
    bond_source: str = field(default_factory=lambda: _get("HY_BOND_SOURCE", "sample"))
    macro_source: str = field(default_factory=lambda: _get("HY_MACRO_SOURCE", "sample"))
    news_source: str = field(default_factory=lambda: _get("HY_NEWS_SOURCE", "sample"))
    outlook_source: str = field(default_factory=lambda: _get("HY_OUTLOOK_SOURCE", "sample"))

    # Generic REST gateway (the "I'll provide access/keys" path). Point this at
    # a service you control that proxies Bloomberg / ICE / FINRA TRACE and
    # returns JSON matching the shapes documented in ``sources/feeds.py``.
    rest_base_url: Optional[str] = field(default_factory=lambda: _get("HY_REST_BASE_URL"))
    rest_api_key: Optional[str] = field(default_factory=lambda: _get("HY_REST_API_KEY"))

    # Vendor credentials (used by vendor-specific adapters when enabled).
    bloomberg_host: Optional[str] = field(default_factory=lambda: _get("BLOOMBERG_HOST"))
    bloomberg_port: Optional[str] = field(default_factory=lambda: _get("BLOOMBERG_PORT"))
    ice_api_key: Optional[str] = field(default_factory=lambda: _get("ICE_API_KEY"))
    finra_trace_api_key: Optional[str] = field(
        default_factory=lambda: _get("FINRA_TRACE_API_KEY")
    )

    # Report shape
    index_name: str = field(
        default_factory=lambda: _get("HY_INDEX_NAME", "ICE BofA US High Yield")
    )
    top_n: int = field(default_factory=lambda: int(_get("HY_TOP_N", "5")))

    # Output & delivery
    output_dir: str = field(default_factory=lambda: _get("HY_OUTPUT_DIR", "./output/hy_recap"))
    delivery_timezone: str = field(
        default_factory=lambda: _get("HY_DELIVERY_TZ", "America/New_York")
    )
    delivery_deadline: str = field(default_factory=lambda: _get("HY_DELIVERY_DEADLINE", "07:15"))

    # Google Drive delivery (service account; see hy_recap/delivery_gdrive.py)
    drive_folder_id: Optional[str] = field(default_factory=lambda: _get("HY_DRIVE_FOLDER_ID"))
    drive_as_doc: bool = field(
        default_factory=lambda: (_get("HY_DRIVE_AS_DOC", "") or "").lower()
        in ("1", "true", "yes")
    )
    google_credentials_path: Optional[str] = field(
        default_factory=lambda: _get("GOOGLE_APPLICATION_CREDENTIALS")
    )

    def missing_credentials(self) -> list[str]:
        """Return the credentials a non-sample run still needs.

        Lets the CLI warn clearly instead of failing deep inside an adapter.
        """
        missing: list[str] = []
        selected = {self.bond_source, self.macro_source, self.news_source, self.outlook_source}
        if "rest" in selected and not self.rest_base_url:
            missing.append("HY_REST_BASE_URL")
        if "ice" in selected and not self.ice_api_key:
            missing.append("ICE_API_KEY")
        if "trace" in selected and not self.finra_trace_api_key:
            missing.append("FINRA_TRACE_API_KEY")
        if "bloomberg" in selected and not self.bloomberg_host:
            missing.append("BLOOMBERG_HOST")
        return missing
