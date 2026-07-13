"""Utility functions for file operations with Altair charts."""

import os
import json
import vl_convert as vlc
import altair as alt


def modify_dimensions(chart: alt.Chart, width: int, height: int) -> str:
    """Modify the width and height of a chart.

    Args:
        chart: Altair chart object
        width: Desired width in pixels
        height: Desired height in pixels

    Returns:
        str: Modified Vega-Lite specification as JSON
    """
    chart_dict = chart.to_dict()
    if width:
        chart_dict['width'] = width
    if height:
        chart_dict['height'] = height

    return json.dumps(chart_dict, indent=2)


def save_chart(chart, path="", name=None, width=350, height=280, svg=False, source=None):
    """Save an Altair chart as minified JSON and PNG (and optionally SVG).

    Args:
        chart: Altair chart object
        path: directory to save into. Defaults to "" (the current working directory).
            A non-empty path is created if it does not exist. Argument order is kept as
            ``(chart, path, name)`` for backward compatibility.
        name: base name for the files, e.g. 'chart1' (required)
        width: width of the chart in pixels (falsy value leaves width unset, e.g. for facets)
        height: height of the chart in pixels (falsy value leaves height unset)
        svg: True to also save an SVG file alongside the JSON and PNG
        source: optional source text to add to the bottom of the chart. When given, an
            additional PNG is written with '_source' appended to the name.

    Returns:
        None
    """
    if name is None:
        raise ValueError("save_chart requires a 'name' for the output files")

    # Only create a directory when an explicit, non-empty path is given.
    if path:
        os.makedirs(path, exist_ok=True)

    # Check for truthy width/height, add to chart if so. (Lets us avoid forcing
    # height/width onto charts that shouldn't have them, e.g. faceted charts.)
    vega_spec = modify_dimensions(chart, width, height)

    # Save as JSON (minified to save space)
    json_path = os.path.join(path, f'{name}.json')
    with open(json_path, 'w') as f:
        json.dump(json.loads(vega_spec), f, separators=(',', ':'))

    # Convert JSON to PNG using vl2png
    png_path = os.path.join(path, f'{name}.png')
    png_data = vlc.vegalite_to_png(vl_spec=vega_spec, scale=4)
    with open(png_path, "wb") as f:
        f.write(png_data)

    if svg:
        svg_path = os.path.join(path, f'{name}.svg')
        svg_data = vlc.vegalite_to_svg(vl_spec=vega_spec)
        with open(svg_path, "w") as f:
            f.write(svg_data)

    if source:
        sourced_chart = add_source(chart, source)
        vega_spec = modify_dimensions(sourced_chart, width, height)
        png_path = os.path.join(path, f'{name}_source.png')
        png_data = vlc.vegalite_to_png(vl_spec=vega_spec, scale=4)
        with open(png_path, "wb") as f:
            f.write(png_data)


def add_source(chart: alt.Chart, source, *, font_size: int = 10,
               color: str = '#676A8680', y_offset: int = 30) -> alt.Chart:
    """Layer a de-emphasised source/notes caption beneath a chart.

    The caption is a text mark layered onto the chart and pinned to the bottom of the
    plotting area (``y = 'height'``), then pushed below the axis with ``yOffset``. Because
    it's a layer (not a title or a concatenation) it works even when the chart already has
    a title, keeps the chart's normal width/height sizing, and supports multi-line sources.
    The input ``chart`` is not mutated.

    Args:
        chart: Altair chart object.
        source: The caption text. Either a string (use ``\\n`` to split lines) or a list
            of strings (one per line). A single-line string that does not already start
            with ``'Source:'`` or ``'Note:'`` is prefixed with ``'Source: '``.
        font_size: Caption font size in pixels.
        color: Caption colour (default is the brand domain colour at 50% opacity).
        y_offset: Pixels below the bottom of the plot area to place the caption. The
            default (30) clears a typical x-axis; increase it if the axis is taller.

    Returns:
        alt.Chart: A new layered chart with the caption below the original chart.
    """
    # Normalise the source into a list of lines.
    if isinstance(source, (list, tuple)):
        lines = [str(line) for line in source]
    else:
        lines = str(source).split('\n')

    # Auto-prefix a bare single-line source (leave 'Note:'/'Source:' and multi-line as-is).
    if len(lines) == 1 and not lines[0].startswith(('Source:', 'Note:')):
        lines = [f'Source: {lines[0]}']

    source_text = '\n'.join(lines)

    caption = (
        alt.Chart(alt.InlineData(values=[{'_source': source_text}]))
        .mark_text(
            align='left',
            baseline='top',
            fontStyle='italic',
            fontSize=font_size,
            color=color,
            lineBreak='\n',
            yOffset=y_offset,
        )
        .encode(
            text='_source:N',
            x=alt.value(0),
            y=alt.value('height'),
        )
    )

    return alt.layer(chart, caption)
