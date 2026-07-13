"""Smoke-render every theme across every gallery chart type.

This is the regression guard for themes: if a theme produces a spec that Vega-Lite can't
render (bad config key, invalid value), the corresponding render raises and the test fails.
For *visual* review, use ``scripts/render_themes.py`` which builds labelled contact sheets.
"""

import altair as alt
import pytest
import vl_convert as vlc

from ecostyles import EcoStyles
from ecostyles.themes import cotd

from gallery import GALLERY  # from specs/ (see pytest.ini pythonpath)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
NAMED_THEMES = ["article", "cotd", "newsletter"]


@pytest.fixture(scope="module")
def styles():
    # Instantiating registers the Circular Std fonts with vl-convert.
    return EcoStyles()


def _render(chart: alt.Chart) -> bytes:
    return vlc.vegalite_to_png(vl_spec=chart.to_json(), scale=1)


@pytest.mark.parametrize("theme_name", NAMED_THEMES)
@pytest.mark.parametrize("chart_name", list(GALLERY))
def test_theme_renders_every_chart(styles, theme_name, chart_name):
    styles.register_and_enable_theme(theme_name)
    chart = GALLERY[chart_name]().properties(width=200, height=150)
    png = _render(chart)
    assert png[:8] == PNG_MAGIC
    assert len(png) > 1000


@pytest.mark.parametrize("chart_name", list(GALLERY))
def test_cotd_dark_mode_renders(chart_name):
    EcoStyles()  # register fonts
    from altair import theme

    theme.register("cotd_dark", enable=True)(lambda: cotd.get_theme(dark_mode=True))
    chart = GALLERY[chart_name]().properties(width=200, height=150)
    png = _render(chart)
    assert png[:8] == PNG_MAGIC
