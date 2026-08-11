"""Data-source adapters for the HY recap.

Each adapter is small and independent so a richer feed can replace it without
touching the generator. Adapters raise :class:`SourceUnavailable` (never a bare
network error) when they cannot produce data, so the generator can degrade
gracefully and record a warning.
"""

from .base import DataSource, SecurityMoversSource, SourceUnavailable
from .fred import FredSource
from .treasury import TreasuryParYieldSource
from .trace import TraceMoversSource

__all__ = [
    "DataSource",
    "SecurityMoversSource",
    "SourceUnavailable",
    "FredSource",
    "TreasuryParYieldSource",
    "TraceMoversSource",
]
