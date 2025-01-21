"""Tests for theme configurations."""

from ecostyles.themes import cotd, article

def test_cotd_theme():
    """Test Chart of the Day theme configuration."""
    # Test light mode
    light_theme = cotd.get_theme(dark_mode=False)
    assert isinstance(light_theme, dict)
    assert 'config' in light_theme
    
    # Check essential configuration elements
    config = light_theme['config']
    assert config['font'] == 'Circular Std'
    assert isinstance(config['range'], dict)
    assert isinstance(config['axis'], dict)
    
    # Test dark mode
    dark_theme = cotd.get_theme(dark_mode=True)
    assert isinstance(dark_theme, dict)

def test_article_theme():
    """Test article theme configuration."""
    theme = article.get_theme()
    assert isinstance(theme, dict)
    assert 'config' in theme
    
    config = theme['config']
    assert config['font'] == 'Circular Std'
    assert isinstance(config['range'], dict)
    assert isinstance(config['axis'], dict)
