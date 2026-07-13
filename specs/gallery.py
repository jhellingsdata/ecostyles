"""A gallery of theme-agnostic chart specifications for exercising themes.

Each builder returns a plain ``alt.Chart`` with **no theme/config applied**, so the
active ``ecostyles`` theme decides the styling. The set covers the mark types our themes
configure (line, bar, point/scatter, area, rect/heatmap, geoshape) plus common cases
(multi-series colour, temporal axes, faceting).

Used by:
- ``tests/test_theme_rendering.py`` — smoke-renders every theme x chart (regression guard).
- ``scripts/render_themes.py`` — builds a labelled contact sheet per theme (visual review).

Data is generated deterministically (fixed seed) so renders are stable across runs.
"""

from __future__ import annotations

import math

import altair as alt
import pandas as pd


# --------------------------------------------------------------------------- data
def _timeseries() -> pd.DataFrame:
    """Two smooth-ish series over 24 months."""
    dates = pd.date_range("2022-01-01", periods=24, freq="MS")
    rows = []
    for i, d in enumerate(dates):
        rows.append({"date": d, "series": "UK", "value": 100 + 12 * math.sin(i / 3)})
        rows.append({"date": d, "series": "US", "value": 100 + 8 * math.cos(i / 4) + i})
    return pd.DataFrame(rows)


def _categories() -> pd.DataFrame:
    return pd.DataFrame(
        {"group": ["G7", "EU27", "OECD", "UK", "US", "EA19"],
         "value": [3.0, 2.4, 3.1, 1.8, 2.9, 2.2]}
    )


def _scatter() -> pd.DataFrame:
    xs = [5, 12, 18, 22, 27, 33, 39, 44, 51, 58, 63, 70]
    return pd.DataFrame(
        {"gdp_per_capita": xs,
         "life_expectancy": [66 + 0.28 * x - 0.0016 * x * x for x in xs],
         "region": (["Europe", "Asia", "Americas"] * 4)}
    )


def _stacked() -> pd.DataFrame:
    rows = []
    for year in range(2015, 2024):
        for sector in ["Services", "Manufacturing", "Agriculture"]:
            base = {"Services": 60, "Manufacturing": 30, "Agriculture": 10}[sector]
            rows.append({"year": year, "sector": sector,
                         "share": base + (year - 2015) * (1 if sector == "Services" else -0.3)})
    return pd.DataFrame(rows)


def _heatmap() -> pd.DataFrame:
    rows = []
    for m in range(1, 13):
        for h in range(0, 24, 3):
            rows.append({"month": m, "hour": h,
                         "intensity": abs(math.sin(m / 2) * math.cos(h / 6)) * 100})
    return pd.DataFrame(rows)


def _geo() -> dict:
    """A tiny hand-made GeoJSON FeatureCollection (offline, no vega_datasets)."""
    def square(x, y, s):
        return [[[x, y], [x + s, y], [x + s, y + s], [x, y + s], [x, y]]]
    feats = []
    for i, (x, y) in enumerate([(0, 0), (2.2, 0), (0, 2.2), (2.2, 2.2), (1.1, 4.4)]):
        feats.append({
            "type": "Feature",
            "properties": {"id": f"R{i}", "value": (i + 1) * 15},
            "geometry": {"type": "Polygon", "coordinates": square(x, y, 2)},
        })
    return {"type": "FeatureCollection", "features": feats}


# ----------------------------------------------------------------------- builders
def line_multi() -> alt.Chart:
    """Multi-series line chart on a temporal axis."""
    return (
        alt.Chart(_timeseries())
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Month"),
            y=alt.Y("value:Q", title="Index (2022=100)"),
            color=alt.Color("series:N", title="Country"),
        )
    )


def bar() -> alt.Chart:
    """Simple categorical bar chart."""
    return (
        alt.Chart(_categories())
        .mark_bar()
        .encode(x=alt.X("group:N", title=None, sort="-y"), y=alt.Y("value:Q", title="Growth, %"))
    )


def scatter() -> alt.Chart:
    """Coloured scatter plot (points)."""
    return (
        alt.Chart(_scatter())
        .mark_point()
        .encode(
            x=alt.X("gdp_per_capita:Q", title="GDP per capita (000s)"),
            y=alt.Y("life_expectancy:Q", title="Life expectancy", scale=alt.Scale(zero=False)),
            color=alt.Color("region:N", title="Region"),
        )
    )


def area_stacked() -> alt.Chart:
    """Normalised stacked area chart."""
    return (
        alt.Chart(_stacked())
        .mark_area()
        .encode(
            x=alt.X("year:O", title=None),
            y=alt.Y("share:Q", stack="normalize", title="Share of GVA"),
            color=alt.Color("sector:N", title="Sector"),
        )
    )


def heatmap() -> alt.Chart:
    """Rect/heatmap with a sequential colour scale."""
    return (
        alt.Chart(_heatmap())
        .mark_rect()
        .encode(
            x=alt.X("hour:O", title="Hour"),
            y=alt.Y("month:O", title="Month"),
            color=alt.Color("intensity:Q", title="Intensity"),
        )
    )


def geoshape() -> alt.Chart:
    """Choropleth using an inline (offline) GeoJSON."""
    data = alt.Data(values=_geo(), format=alt.DataFormat(property="features", type="json"))
    return (
        alt.Chart(data)
        .mark_geoshape()
        .encode(color=alt.Color("properties.value:Q", title="Value"))
        .project(type="identity", reflectY=True)
    )


#: Registry of chart name -> builder. Order is the display order in contact sheets.
GALLERY = {
    "line_multi": line_multi,
    "bar": bar,
    "scatter": scatter,
    "area_stacked": area_stacked,
    "heatmap": heatmap,
    "geoshape": geoshape,
}


def build_all(width: int = 240, height: int = 180) -> dict[str, alt.Chart]:
    """Build every gallery chart at a compact size, titled with its name."""
    return {
        name: builder().properties(width=width, height=height, title=name)
        for name, builder in GALLERY.items()
    }
