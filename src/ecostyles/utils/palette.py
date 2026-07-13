"""Render colour palettes as Altair swatch charts — a visual aid for exploring styles."""

from __future__ import annotations

import altair as alt
import pandas as pd


def swatches(colours, title: str | None = None, columns: int = 8, size: int = 60) -> alt.Chart:
    """Return an Altair chart of labelled colour swatches laid out in a grid.

    Each swatch is a coloured tile with its name and hex printed *beneath* it (so the label
    is legible whatever the swatch colour). Fills use the literal hex values (no colour scale).

    Args:
        colours: a ``{name: hex}`` mapping, or an ordered list of hex strings.
        title: optional chart title.
        columns: number of swatches per row (use 1 for a vertical list).
        size: swatch tile size in pixels.

    Returns:
        An Altair chart.
    """
    items = list(colours.items()) if isinstance(colours, dict) else [(c, c) for c in colours]

    gap, label_h = 12, 34
    records = []
    for idx, (name, hex_) in enumerate(items):
        col, row = idx % columns, idx // columns
        x0, y0 = col * (size + gap), row * (size + label_h + gap)
        # Name and hex on separate lines so labels stay narrower than the tile.
        label = str(name) if str(name).lower() == str(hex_).lower() else f"{name}\n{hex_}"
        records.append({"x0": x0, "x1": x0 + size, "xmid": x0 + size / 2,
                        "y0": y0, "y1": y0 + size, "ylabel": y0 + size + 4,
                        "hex": hex_, "label": label})
    df = pd.DataFrame(records)
    n_rows = (len(items) + columns - 1) // columns
    total_w = columns * (size + gap)
    total_h = n_rows * (size + label_h + gap)

    xscale = alt.Scale(domain=[0, total_w])
    yscale = alt.Scale(domain=[total_h, 0])  # reversed so row 0 is at the top

    # opacity=1 so the tiles show true colour even if a theme sets a faded `rect` opacity.
    tiles = alt.Chart(df).mark_rect(stroke="white", strokeWidth=2, opacity=1).encode(
        x=alt.X("x0:Q", scale=xscale, axis=None), x2="x1:Q",
        y=alt.Y("y0:Q", scale=yscale, axis=None), y2="y1:Q",
        color=alt.Color("hex:N", scale=None),
    )
    labels = alt.Chart(df).mark_text(
        baseline="top", align="center", fontSize=9, lineBreak="\n",
    ).encode(
        x=alt.X("xmid:Q", scale=xscale, axis=None),
        y=alt.Y("ylabel:Q", scale=yscale, axis=None),
        text="label:N",
    )
    chart = (tiles + labels).properties(width=total_w, height=total_h)
    return chart.properties(title=title) if title else chart
