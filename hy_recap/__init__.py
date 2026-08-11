"""US High Yield bond market daily-recap generator.

Assembles a pre-market recap of the prior US high-yield session from live
market-data sources and renders it as Markdown in the delivered format.

Design principles
-----------------
* **Never fabricate.** Any figure that cannot be sourced is left blank and the
  gap is recorded as an explicit warning in the output. A missing number is
  reported as missing, not invented.
* **Pluggable sources.** Data providers implement small adapter interfaces so a
  richer feed (Bloomberg/ICE/paid TRACE) can be dropped in without touching the
  generator.
* **Graceful degradation.** If a source is unavailable the recap still renders,
  with the affected section clearly marked and a note on what feed would fill it.
"""

from .models import (
    BondMove,
    MarketSnapshot,
    Recap,
    YieldPoint,
)
from .generator import RecapGenerator
from .config import Settings

__all__ = [
    "BondMove",
    "MarketSnapshot",
    "Recap",
    "YieldPoint",
    "RecapGenerator",
    "Settings",
]

__version__ = "0.1.0"
