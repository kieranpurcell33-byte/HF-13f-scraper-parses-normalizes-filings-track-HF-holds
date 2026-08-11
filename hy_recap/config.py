"""Environment-driven configuration for the HY recap generator.

All secrets/keys are read from the environment (optionally via a local ``.env``
file). Nothing is hard-coded, and the module never raises on missing keys — the
absence of a key simply disables the corresponding data source, which the
generator surfaces as a warning rather than a crash.
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


@dataclass
class Settings:
    """Runtime configuration, populated from environment variables.

    Environment variables
    ----------------------
    FRED_API_KEY
        Key for the St. Louis Fed FRED API (https://fred.stlouisfed.org/docs/api/).
        Enables HY OAS / yield and Treasury series. Free to obtain.
    FINRA_API_CLIENT_ID / FINRA_API_CLIENT_SECRET
        OAuth2 client-credentials for the FINRA API (https://developer.finra.org).
        Enables the TRACE security-level movers source.
    HY_MOVERS_PROVIDER
        Which security-movers adapter to use: ``finra`` (default) or ``none``.
    HY_RECAP_OUTPUT_DIR
        Directory reports are written to (default ``reports``).
    HY_RECAP_TIMEZONE
        Market timezone for date logic (default ``America/New_York``).
    """

    fred_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("FRED_API_KEY") or None
    )
    finra_client_id: Optional[str] = field(
        default_factory=lambda: os.getenv("FINRA_API_CLIENT_ID") or None
    )
    finra_client_secret: Optional[str] = field(
        default_factory=lambda: os.getenv("FINRA_API_CLIENT_SECRET") or None
    )
    movers_provider: str = field(
        default_factory=lambda: (os.getenv("HY_MOVERS_PROVIDER") or "finra").lower()
    )
    output_dir: str = field(
        default_factory=lambda: os.getenv("HY_RECAP_OUTPUT_DIR") or "reports"
    )
    timezone: str = field(
        default_factory=lambda: os.getenv("HY_RECAP_TIMEZONE") or "America/New_York"
    )
    http_timeout: float = field(
        default_factory=lambda: float(os.getenv("HY_RECAP_HTTP_TIMEOUT") or "20")
    )

    @property
    def has_fred(self) -> bool:
        return bool(self.fred_api_key)

    @property
    def has_finra(self) -> bool:
        return bool(self.finra_client_id and self.finra_client_secret)
