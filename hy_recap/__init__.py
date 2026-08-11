"""
hy_recap -- a pluggable pipeline that produces a daily US high-yield bond
market recap: notable news, best/worst issuer-level movers, index context, and
the outlook for the next session.

Public API::

    from hy_recap import RecapBuilder, RecapConfig, render_markdown

    report = RecapBuilder().build()          # previous trading day
    print(render_markdown(report))
"""

from hy_recap.builder import RecapBuilder
from hy_recap.config import RecapConfig
from hy_recap.models import RecapReport
from hy_recap.renderer import render_markdown

__all__ = ["RecapBuilder", "RecapConfig", "RecapReport", "render_markdown"]

__version__ = "0.1.0"
