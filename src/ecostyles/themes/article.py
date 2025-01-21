"""Article chart theme configuration."""

from altair import theme

def get_theme() -> theme.ThemeConfig:
    """Returns a theme suitable for Economics Observatory article charts.
    
    Returns:
        dict: Theme configuration
    """

    text = '#122b39'

    domain = '#676A86'
    title_colour = domain
    subtitle_colour = domain + 'E6'

    
    return {
        'config': {
            'font': 'Circular Std',
            'text': {
                'color': domain,
                'align': 'left',
                'baseline': 'middle',
                'dx': 7,
                'dy': 0,
                'fontSize': 11
            },
            'view': {
                'stroke': None,
                'continuousWidth': 400,
                'continuousHeight': 300,
                'discreteWidth': 400,
                'discreteHeight': 300,
            },
            "range": {
                "category": ["#36B7B4", "#E6224B", "#F4C245", "#0063AF", "#00A767", "#179FDB", "#EB5C2E"],
                "diverging": ["#E6224B", "#E54753", "#C9C9C9", "#179FDB", "#122B39"],
                "heatmap": ["#C9C9C9", "#179FDB", "#0063AF", "#122B39"],
                "ordinal": ["#00A767", "#36B7B4", "#179FDB", "#0063AF", "#243B5A"]
            },
            'bar': {
                'color': "#179fdb"  # blue-light
            },
            'line': {
                'color': "#e6224b"  # red
            },
            'rule': {
                'color': domain,
            },
            'area': {
                'opacity': 0.3
            },
            'point': {
                'filled': True,
                'size': 80,
                'color': "#e6224b",  # red
                'opacity': 0.95
            },
            'geoshape': {
                'stroke': 'white',
                'strokeWidth': 0.3
            },
            'rect': {
                'fill': '#d6d4d4',
                'opacity': 0.3
            },
            # Set shared axis options
            'axis': {
                'labelColor': domain,
                'labelFontSize': 11,
                'labelFont': 'Circular Std',
                'labelOpacity': 0.7,
                'tickColor': domain,
                'tickOpacity': 0.5,
                'domainColor': '#676A86',
                'domainOpacity': 0.5,
                'gridColor': domain,
                'gridDash': [2, 2],
                'gridOpacity': 0.5,
                'title': None,
                'titleColor': domain,
                'titleOpacity': 0.8,
                'tickSize': 4

            },
            'axisXDiscrete': {
                'grid': False,
                'labelAngle': 0,
                'tickCount': 10,
                'tickOpacity': 0.5,
                'title': None 
            },
            'axisYDiscrete': {
                'ticks': False,
                'labelPadding': 5
            },
            'axisXTemporal': {
                'grid': False,
                'ticks': True,

            },
            'axisXQuantitative': {
                'grid': True
                
            },
            'axisYQuantitative': {
                'gridColor': domain,
                'gridDash': [1, 5],
                'gridOpacity': 0.5,
                'ticks': False,
                'labelPadding': 5,
                'tickCount': 8,
                'titleAngle': 0,
                'titleAlign': 'left',
                'titleBaseline': 'bottom',
                'titleX': 0,
                'titleY': -5
            },
            'title': {
                'color': subtitle_colour,
                'subtitleColor': domain,
                'font': 'Circular Std',
                'subtitleFont': 'Circular Std',
                'anchor': 'start',
                'fontSize': 14,
                'subtitleFontSize': 12,
                'subtitlePadding': 4,
                "offset": 0,
                "frame": "group"
            },
            'legend': {
                'titleColor': text,
                'title': None,
                'labelColor': text,
                'labelFontSize': 11
            }
        }
    }