"""Abstract adapter interfaces and shared HTTP helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..models import BondMove, YieldPoint


class SourceUnavailable(Exception):
    """Raised when an adapter cannot produce data (missing key, HTTP error, …).

    The generator catches this and records a warning instead of crashing. This
    is deliberately distinct from a programming error so real bugs still surface.
    """


class DataSource(ABC):
    """A source of rate/spread observations (:class:`YieldPoint`)."""

    name: str = "data-source"

    @abstractmethod
    def is_available(self) -> bool:
        """Cheap check (e.g. is the API key configured)."""

    @abstractmethod
    def fetch_points(self, session: date) -> List[YieldPoint]:
        """Return level observations for (up to and including) ``session``.

        Must raise :class:`SourceUnavailable` on any failure.
        """


class SecurityMoversSource(ABC):
    """A source of security-level daily movers (best/worst bonds)."""

    name: str = "movers-source"

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def fetch_movers(
        self, session: date, top_n: int = 5
    ) -> tuple[List[BondMove], List[BondMove]]:
        """Return ``(gainers, losers)`` for ``session``.

        Must raise :class:`SourceUnavailable` on any failure.
        """
