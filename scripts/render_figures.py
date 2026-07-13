#!/usr/bin/env python3
"""
Render the project figures to static assets in docs/.

Produces both .svg (crisp, version-controllable) and .png (for the README
and for viewers that don't render inline SVG) for:
  - the agent pipeline diagram (diagram.py)
  - the framework landscape figure (landscape.py)

Usage:
    pip install cairosvg
    python scripts/render_figures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tumorboard_agent.diagram import AGENT_DIAGRAM_SVG
from tumorboard_agent.landscape import LANDSCAPE_SVG

DOCS = Path(__file__).resolve().parent.parent / "docs"

FIGURES = {
    "agent_pipeline": (AGENT_DIAGRAM_SVG, 900),
    "landscape": (LANDSCAPE_SVG, 1180),
}


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    try:
        import cairosvg
    except ImportError:
        raise SystemExit("Please 'pip install cairosvg' to render PNGs.")

    for name, (svg, width) in FIGURES.items():
        svg_path = DOCS / f"{name}.svg"
        png_path = DOCS / f"{name}.png"
        svg_path.write_text(svg.strip(), encoding="utf-8")
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png_path), output_width=width * 2)
        print(f"wrote {svg_path}  and  {png_path}")


if __name__ == "__main__":
    main()
