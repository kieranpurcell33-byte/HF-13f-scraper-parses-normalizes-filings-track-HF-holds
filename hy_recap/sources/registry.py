"""
Wire a :class:`RecapConfig` to concrete source implementations.

Each section (macro / bonds / news / outlook) is resolved independently, so you
can mix a live bond feed with, say, a sample outlook while you build things out.
Add a new backend by extending ``_FACTORIES``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from hy_recap.config import RecapConfig
from hy_recap.sources.base import (
    BondPerformanceSource,
    MacroSource,
    NewsSource,
    OutlookSource,
)
from hy_recap.sources import sample as _sample


@dataclass
class Sources:
    """The four resolved sources the builder needs."""

    macro: MacroSource
    bonds: BondPerformanceSource
    news: NewsSource
    outlook: OutlookSource


def _rest(config: RecapConfig):
    # Imported lazily so `requests`-free sample runs don't pay for it.
    from hy_recap.sources.feeds import RestGatewaySource

    return RestGatewaySource(config)


# name -> factory returning an object implementing the needed protocol(s).
_FACTORIES: Dict[str, Callable[[RecapConfig], object]] = {
    "sample": lambda cfg: None,  # handled specially below (one instance per section)
    "rest": _rest,
}


def _resolve(name: str, config: RecapConfig, sample_factory):
    if name == "sample":
        return sample_factory()
    factory = _FACTORIES.get(name)
    if factory is None:
        raise ValueError(
            f"Unknown source '{name}'. Known: {sorted(_FACTORIES)}. "
            "Register vendor adapters in sources/registry.py."
        )
    return factory(config)


def build_sources(config: RecapConfig) -> Sources:
    """Instantiate the sources selected by ``config``.

    The generic REST gateway implements all four protocols, so when several
    sections point at ``rest`` they share one HTTP client.
    """
    rest_singleton = None

    def rest_shared(cfg: RecapConfig):
        nonlocal rest_singleton
        if rest_singleton is None:
            rest_singleton = _rest(cfg)
        return rest_singleton

    def resolve(name: str, sample_factory):
        if name == "rest":
            return rest_shared(config)
        return _resolve(name, config, sample_factory)

    return Sources(
        macro=resolve(config.macro_source, _sample.SampleMacroSource),
        bonds=resolve(config.bond_source, _sample.SampleBondSource),
        news=resolve(config.news_source, _sample.SampleNewsSource),
        outlook=resolve(config.outlook_source, _sample.SampleOutlookSource),
    )
