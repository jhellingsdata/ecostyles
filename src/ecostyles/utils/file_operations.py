"""Utility functions for file operations with Altair charts."""

import os
import re
import json
import vl_convert as vlc
import altair as alt

# Matches an exact-midnight time component of an ISO datetime, e.g. the "T00:00:00"
# (optionally with fractional seconds and/or a trailing Z) in "2020-01-01T00:00:00".
_MIDNIGHT_RE = re.compile(r"T00:00:00(?:\.0+)?Z?")


def _strip_midnight_timestamps(spec_json: str) -> str:
    """Drop exact-midnight time components from ISO dates in a serialised spec.

    Pandas datetime columns serialise as e.g. ``"2020-01-01T00:00:00"``, which bloats the
    JSON with text that carries no information for date-level charts. Where the time is
    exactly midnight we drop it, leaving ``"2020-01-01"``. Non-midnight times (which do
    carry information) are left untouched.
    """
    return _MIDNIGHT_RE.sub("", spec_json)


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


def _spec_for_save(chart, width, height, strip_timestamps) -> str:
    """Serialise a chart to a minified spec string, optionally stripping midnight times."""
    spec = json.dumps(json.loads(modify_dimensions(chart, width, height)),
                      separators=(",", ":"))
    return _strip_midnight_timestamps(spec) if strip_timestamps else spec


def save_chart(chart, path="", name=None, width=350, height=280, svg=False, source=None,
               strip_timestamps=True):
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
        strip_timestamps: True (default) to drop exact-midnight ``T00:00:00`` time
            components from inline date data, keeping the JSON compact.

    Returns:
        None
    """
    if name is None:
        raise ValueError("save_chart requires a 'name' for the output files")

    # Only create a directory when an explicit, non-empty path is given.
    if path:
        os.makedirs(path, exist_ok=True)

    # One minified (and optionally timestamp-stripped) spec, reused for every output.
    spec = _spec_for_save(chart, width, height, strip_timestamps)

    json_path = os.path.join(path, f'{name}.json')
    with open(json_path, 'w') as f:
        f.write(spec)

    png_path = os.path.join(path, f'{name}.png')
    with open(png_path, "wb") as f:
        f.write(vlc.vegalite_to_png(vl_spec=spec, scale=4))

    if svg:
        svg_path = os.path.join(path, f'{name}.svg')
        with open(svg_path, "w") as f:
            f.write(vlc.vegalite_to_svg(vl_spec=spec))

    if source:
        sourced_spec = _spec_for_save(add_source(chart, source), width, height, strip_timestamps)
        png_path = os.path.join(path, f'{name}_source.png')
        with open(png_path, "wb") as f:
            f.write(vlc.vegalite_to_png(vl_spec=sourced_spec, scale=4))


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
