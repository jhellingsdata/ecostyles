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


def save_chart(chart, path, name, width=350, height=280, svg=False, titles:dict=None, source=None):
    """Save an Altair chart to a specified path in both JSON and PNG formats.
    
    Args:
        chart: Altair chart object
        path: directory path to save the files, e.g. 'charts'
        name: base name for the files, e.g. 'chart1'
        width: width of the chart in pixels
        height: height of the chart in pixels
        svg: True to save an SVG file as well as JSON and PNG
        source: source text to add to bottom of chart, e.g. 'ONS'. Saves a second PNG file with '_source' appended to the name.

    Returns:
        None
    """

    # Create directory if it doesn't exist
    os.makedirs(path, exist_ok=True)

    # Check if truthy value for width or height, add to chart if so. (This is so can avoid adding height/width to chart if not needed, e.g. for facetted charts)
    vega_spec = modify_dimensions(chart, width, height)
    
    # Save as JSON
    json_path = os.path.join(path, f'{name}.json')
    with open(json_path, 'w') as f:
        # Minimise JSON to save space
        json.dump(json.loads(vega_spec), f, separators=(',', ':'))
        # f.write(vega_spec)

    # Convert JSON to PNG using vl2png
    png_path = os.path.join(path, f'{name}.png')
    png_data = vlc.vegalite_to_png(vl_spec=vega_spec, scale=4)
    with open(png_path, "wb") as f:
        f.write(png_data)

    if svg:
        # Convert JSON to SVG using vl2svg
        svg_path = os.path.join(path, f'{name}.svg')
        svg_data = vlc.vegalite_to_svg(vl_spec=vega_spec)
        with open(svg_path, "w") as f:
            f.write(svg_data)

    if source:
        chart = add_source(chart, source)
        vega_spec = modify_dimensions(chart, width, height)
        png_path = os.path.join(path, f'{name}_source.png')
        png_data = vlc.vegalite_to_png(vl_spec=vega_spec, scale=4)
        with open(png_path, "wb") as f:
            f.write(png_data)

def add_source(chart: alt.Chart, source: str):
    """Add source text to the chart.
    Args:
        chart: Altair chart object
        source: source text to add to bottom of chart, e.g. 'ONS'.
    
    Returns:
        chart: Altair chart object with source text added

    Notes:
        - Only works for charts without a title.
    """

    chart.title = alt.TitleParams(
        source if source.startswith('Source:') else source if source.startswith('Note:') else f'Source: {source}',
        orient='bottom',
        fontStyle='italic',
        fontSize=10,
        color='#676A8680',  # domain colour with 50% opacity
        fontWeight='normal',
        frame='group',
        dx=0,
        offset=7
    )
    return chart