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
    assert styles.eco_colours["red"] == "#e6224b"
    assert styles.eco_colours["blue-light"] == "#179fdb"

def test_theme_registration(styles):
    """Test theme registration and enabling."""
    # Test valid theme names
    styles.register_and_enable_theme("cotd")
    styles.register_and_enable_theme("article")
    
    # Test invalid theme name
    with pytest.raises(ValueError):
        styles.register_and_enable_theme("invalid_theme")

def test_add_colour(styles):
    """Test adding colors to a dataframe."""
    # Create sample dataframe
    df = pd.DataFrame({
        'country': ['GBR', 'FRA', 'OECD'],
        'value': [1, 2, 3]
    })
    colour_override = {
        'GBR': 'red',
        'GBR-bar': 'red',
        'FRA': 'blue',
        'OECD': 'grey'
    }
    
    # Add colors
    result = styles.add_colour(df, 'country', colour_override)
    
    # Check new columns exist
    assert 'color-bar' in result.columns
    assert 'color-line' in result.columns
    
    # Check specific color assignments
    gbr_row = result[result['country'] == 'GBR']
    assert not gbr_row['color-bar'].isna().any()
    assert not gbr_row['color-line'].isna().any()

def test_add_shaded_area(styles):
    """Test creating shaded area chart element."""
    start_date = '2020-01-01'
    end_date = '2020-12-31'
    
    result = styles.add_shaded_area(start_date, end_date)
    assert isinstance(result, alt.Chart)

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