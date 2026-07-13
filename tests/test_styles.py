"""Tests for the EcoStyles class."""

import pytest
import pandas as pd
import altair as alt
from ecostyles import EcoStyles

@pytest.fixture
def styles():
    """Create a fresh EcoStyles instance for each test."""
    return EcoStyles()

def test_initialization(styles):
    """Test that EcoStyles initializes with correct default values."""
    assert isinstance(styles.eco_colours, dict)
    assert isinstance(styles.palette, dict)
    assert isinstance(styles.country_groups, dict)
    
    # Check specific colors exist
    assert styles.eco_colours["pink"] == "#e6224b"
    assert styles.eco_colours["blue-light"] == "#179fdb"

def test_theme_registration(styles):
    """Test theme registration and enabling."""
    # Test valid theme names
    styles.register_and_enable_theme("cotd")
    styles.register_and_enable_theme("article")
    
    # Test invalid theme name
    with pytest.raises(ValueError):
        styles.register_and_enable_theme("invalid_theme")

def test_add_colour_explicit_map(styles):
    """Explicit colour_map pins countries (matched via name->ISO3); rest get default."""
    df = pd.DataFrame({'country': ['GBR', 'FRA', 'OECD'], 'value': [1, 2, 3]})
    # Key given as a name to prove normalisation to ISO3.
    result = styles.add_colour(df, 'country', {'United Kingdom': '#e6224b'}, default='#cccccc')

    assert 'colour' in result.columns
    assert result.loc[result.country == 'GBR', 'colour'].iloc[0] == '#e6224b'
    assert result.loc[result.country == 'FRA', 'colour'].iloc[0] == '#cccccc'
    assert 'colour' not in df.columns  # input not mutated


def test_add_colour_auto_palette(styles):
    """Without a map, distinct countries get consecutive palette colours, stable per country."""
    df = pd.DataFrame({'country': ['GBR', 'FRA', 'GBR', 'DEU']})
    result = styles.add_colour(df, 'country')

    assert result['colour'].iloc[0] == styles.category_palette[0]   # GBR (1st distinct)
    assert result['colour'].iloc[1] == styles.category_palette[1]   # FRA (2nd)
    assert result['colour'].iloc[2] == styles.category_palette[0]   # GBR again -> same
    assert result['colour'].iloc[3] == styles.category_palette[2]   # DEU (3rd)


def test_add_colour_country_group_matches_literal(styles):
    """Country groups that don't convert to ISO3 match on their literal label."""
    df = pd.DataFrame({'country': ['OECD', 'GBR']})
    result = styles.add_colour(df, 'country', {'OECD': '#123456'}, default='#000000')
    assert result.loc[result.country == 'OECD', 'colour'].iloc[0] == '#123456'
    assert result.loc[result.country == 'GBR', 'colour'].iloc[0] == '#000000'

def test_add_shaded_area(styles):
    """Test creating shaded area chart element."""
    start_date = '2020-01-01'
    end_date = '2020-12-31'

    result = styles.add_shaded_area(start_date, end_date)
    assert isinstance(result, alt.Chart)


def test_add_shaded_area_periods_and_validation(styles):
    """Shaded area accepts a periods dataframe and requires both endpoints otherwise."""
    rec = styles.get_recessions("uk")
    multi = styles.add_shaded_area(periods=rec)
    assert isinstance(multi, alt.Chart)
    with pytest.raises(ValueError):
        styles.add_shaded_area("2020-01-01")  # missing end_date


@pytest.mark.parametrize("region", ["uk", "us"])
def test_get_recessions(styles, region):
    rec = styles.get_recessions(region)
    assert list(rec.columns) == ["start", "end"]
    assert len(rec) > 0
    assert str(rec["start"].dtype).startswith("datetime")


def test_get_recessions_invalid_region(styles):
    with pytest.raises(ValueError):
        styles.get_recessions("fr")


def test_national_eco_colours(styles):
    assert styles.get_national_eco_colours("GB-SCT") == "#0063af"
    assert styles.get_national_eco_colours("GB-ENG") == "#5c267b"
    assert isinstance(styles.get_national_eco_colours(), dict)


def test_show_colours(styles):
    # swatches() returns a layered chart, so check against the common Altair base type.
    assert isinstance(styles.show_colours("eco"), alt.TopLevelMixin)
    assert isinstance(styles.show_colours("national_eco"), alt.TopLevelMixin)
    assert isinstance(styles.show_colours({"a": "#000000"}), alt.TopLevelMixin)  # custom mapping
    with pytest.raises(ValueError):
        styles.show_colours("does_not_exist")


def test_preview_theme_colours(styles):
    for name in ("article", "cotd", "newsletter"):
        assert styles.preview_theme_colours(name) is not None
    with pytest.raises(ValueError):
        styles.preview_theme_colours("bad_theme")

def test_update_y_axis_title(styles):
    """Test updating y-axis title.
    
    Notes
    ---
    - Currently fails due to error with 'to_dict' method.
    """
    # Create simple chart
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
    chart = alt.Chart(df).mark_point().encode(
        x='x:Q',
        y='y:Q'
    )
    
    new_title = "New Y Title"
    updated_chart = styles.update_y_axis_title(chart, new_title)
    
    # Convert to dict to check specifications
    chart_dict = updated_chart.to_dict()
    assert 'encoding' in chart_dict
    assert 'y' in chart_dict['encoding']
    assert 'axis' in chart_dict['encoding']['y']
    assert chart_dict['encoding']['y']['axis']['title'] == new_title