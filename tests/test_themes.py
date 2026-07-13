"""Structural tests for theme configurations."""

import pytest

from ecostyles.themes import article, cotd, newsletter

# Each theme exposes get_theme(); cotd additionally accepts dark_mode.
THEME_CONFIGS = {
    "article": article.get_theme(),
    "cotd": cotd.get_theme(dark_mode=False),
    "cotd_dark": cotd.get_theme(dark_mode=True),
    "newsletter": newsletter.get_theme(),
}


@pytest.mark.parametrize("name,theme", THEME_CONFIGS.items())
def test_theme_has_expected_structure(name, theme):
    assert isinstance(theme, dict)
    assert "config" in theme

    config = theme["config"]
    assert config["font"] == "Circular Std"
    assert isinstance(config["range"], dict)
    assert isinstance(config["axis"], dict)
    # Every theme should carry the brand categorical palette.
    assert config["range"]["category"][0] == "#36B7B4"


def test_cotd_dark_mode_differs_from_light():
    light = cotd.get_theme(dark_mode=False)["config"]
    dark = cotd.get_theme(dark_mode=True)["config"]
    assert light["background"] != dark["background"], "dark mode must change the background"


def test_cotd_is_more_impactful_than_article():
    """cotd should be visibly punchier than article: bigger title, thicker lines."""
    cotd_config = cotd.get_theme()["config"]
    article_config = article.get_theme()["config"]
    assert cotd_config["title"]["fontSize"] > article_config["title"]["fontSize"]
    assert cotd_config["line"].get("strokeWidth", 1) > article_config["line"].get("strokeWidth", 1)
    assert "background" in cotd_config  # cotd has a distinguishing background
