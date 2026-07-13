"""Render a labelled contact sheet of every gallery chart for each theme.

This is the visual design/review tool: run it after changing a theme to eyeball how it
looks across chart types, side by side, in one PNG per theme.

    uv run python scripts/render_themes.py            # all themes -> renders/
    uv run python scripts/render_themes.py cotd        # just one theme

Output goes to ``renders/<theme>.png`` (git-ignored).
"""

from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
from altair import theme
import vl_convert as vlc

# Make specs/ importable and ensure fonts are registered with vl-convert.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "specs"))
from gallery import build_all  # noqa: E402

from ecostyles import EcoStyles  # noqa: E402
from ecostyles.themes import article, cotd, newsletter  # noqa: E402

EcoStyles()  # side effect: registers the Circular Std fonts

# label -> theme config dict
THEMES = {
    "article": article.get_theme(),
    "cotd": cotd.get_theme(),
    "cotd_dark": cotd.get_theme(dark_mode=True),
    "newsletter": newsletter.get_theme(),
}

COLUMNS = 3


def _grid() -> alt.VConcatChart:
    """Arrange all gallery charts into a grid (COLUMNS per row)."""
    charts = list(build_all().values())
    rows = [alt.hconcat(*charts[i:i + COLUMNS]) for i in range(0, len(charts), COLUMNS)]
    return alt.vconcat(*rows).properties(spacing=24)


def render(label: str, config: dict, out_dir: Path) -> Path:
    # Register + enable this theme so Altair injects its config at serialisation time.
    theme.register(label, enable=True)(lambda cfg=config: cfg)
    spec = _grid().to_json()
    png = vlc.vegalite_to_png(vl_spec=spec, scale=2)
    out = out_dir / f"{label}.png"
    out.write_bytes(png)
    return out


def main(argv: list[str]) -> None:
    wanted = argv or list(THEMES)
    unknown = [t for t in wanted if t not in THEMES]
    if unknown:
        raise SystemExit(f"Unknown theme(s) {unknown}. Choose from {list(THEMES)}")

    out_dir = ROOT / "renders"
    out_dir.mkdir(exist_ok=True)
    for label in wanted:
        path = render(label, THEMES[label], out_dir)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
