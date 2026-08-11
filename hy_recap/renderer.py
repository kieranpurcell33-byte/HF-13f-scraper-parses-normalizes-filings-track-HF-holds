"""
Render a :class:`RecapReport` to a deliverable string (Markdown).

Uses Jinja2 with the templates in ``hy_recap/templates``. HTML can be produced
by rendering the Markdown output through any Markdown converter downstream; the
Markdown itself is the canonical deliverable.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from hy_recap.models import RecapReport

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html",), default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_markdown(report: RecapReport, template_name: str = "recap.md.j2") -> str:
    """Render the recap to a Markdown document."""
    env = _environment()
    template = env.get_template(template_name)
    text = template.render(report=report)
    # Collapse the runs of blank lines Jinja block tags can leave behind.
    lines = text.split("\n")
    cleaned: list[str] = []
    blank = 0
    for line in lines:
        if line.strip() == "":
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        cleaned.append(line.rstrip())
    return "\n".join(cleaned).strip() + "\n"
