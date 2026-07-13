"""Chart of the Day (cotd) theme configuration.

'Chart of the day' is our social-media style: charts are viewed in web and mobile feeds,
often small and without surrounding context. Compared with `article`, this theme is tuned
for impact at a glance — a soft grey background to stand out in a feed, thicker lines,
larger and higher-contrast axis labels, a bigger narrative title, and a more feed-friendly
default size. Distilled from `specs/cotd_example.json`.
"""

from altair import theme


def get_theme(dark_mode: bool = False) -> theme.ThemeConfig:
    """Get the Chart of the Day theme configuration.

    Args:
        dark_mode: Whether to use dark-mode colours (dark background, light text).

    Returns:
        dict: Theme configuration
    """

    if dark_mode:
        background = '#122b39'      # brand dark blue
        domain = '#a9bcd0'          # lighter blue-grey so axis labels stay legible on dark
        text = '#e8eef4'            # near-white body/legend text
        title_colour = '#f4f7fa'
        label_opacity = 1.0         # full opacity on dark — labels were hard to read faded
    else:
        background = '#f4f4f4'      # soft grey — stands out against white feeds
        domain = '#676A86'          # muted grey for axes/labels
        text = '#122b39'            # brand dark blue
        title_colour = '#122b39'
        label_opacity = 0.9

    subtitle_colour = domain + 'E6'

    return {
        'config': {
            'font': 'Circular Std',
            'background': background,
            'text': {
                'color': domain,
                'align': 'left',
                'baseline': 'middle',
                'dx': 7,
                'dy': 0,
                'fontSize': 12
            },
            'view': {
                'stroke': None,
                # Feed-friendly defaults — larger than `article`.
                'continuousWidth': 420,
                'continuousHeight': 340,
                'discreteWidth': 420,
                'discreteHeight': 340,
            },
            "range": {
                "category": ["#36B7B4", "#E6224B", "#F4C245", "#0063AF", "#00A767", "#179FDB", "#EB5C2E", "#5C267B", "#122B39"],
                "diverging": ["#E6224B", "#E54753", "#C9C9C9", "#179FDB", "#122B39"],
                "heatmap": ["#C9C9C9", "#179FDB", "#0063AF", "#122B39"],
                "ordinal": ["#00A767", "#36B7B4", "#179FDB", "#0063AF", "#243B5A"]
            },
            'bar': {
                'color': "#179fdb"
            },
            'line': {
                'color': "#e6224b",
                'strokeWidth': 3          # thicker than default for feed legibility
            },
            'rule': {
                'color': domain,
            },
            'area': {
                'opacity': 0.3
            },
            'point': {
                'filled': True,
                'size': 90,
                'color': "#e6224b",
                'opacity': 0.95
            },
            'geoshape': {
                'stroke': background,
                'strokeWidth': 0.3
            },
            'rect': {
                'fill': '#d6d4d4',
                'opacity': 0.3
            },
            'axis': {
                'labelColor': domain,
                'labelFontSize': 13,      # larger labels for mobile
                'labelFont': 'Circular Std',
                'labelOpacity': label_opacity,   # higher contrast than `article`; full on dark
                'tickColor': domain,
                'tickOpacity': 0.5,
                'domainColor': domain,
                'domainOpacity': 0.5,
                'gridColor': domain,
                'gridDash': [2, 2],
                'gridOpacity': 0.5,
                'title': None,
                'titleColor': domain,
                'titleFontSize': 13,
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
                'grid': False             # ? no vertical gridlines by default (cleaner in feeds)
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
                'color': title_colour,
                'subtitleColor': subtitle_colour,
                'font': 'Circular Std',
                'subtitleFont': 'Circular Std',
                'anchor': 'start',        # left-aligned narrative titles
                'fontSize': 18,           # large, punchy headline
                'fontWeight': 'bold',
                'lineHeight': 22,         # sensible wrapping for multi-line narrative titles
                'subtitleFontSize': 14,
                'subtitlePadding': 5,
                'offset': 12,
                'frame': 'group'
            },
            'legend': {
                'titleColor': text,
                'title': None,
                'labelColor': text,
                'labelFontSize': 13
            }
        }
    }
