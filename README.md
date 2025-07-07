# ecostyles

A Python package for consistent Altair chart styling and themes.

## Installation

You can install the package directly from GitHub:

```bash
pip install git+https://github.com/jhellingsdata/ecostyles.git
```

## Usage

```python
from ecostyles import EcoStyles

# Create styles instance
styles = EcoStyles()

# Register and enable a theme
styles.register_and_enable_theme(theme_name="article")  # or "cotd", "newsletter"

# Create your Altair chart
import altair as alt
chart = alt.Chart(data).mark_line().encode(...)

# Use helper methods
styles.add_source(chart, "Source: ONS")
styles.save(chart, "path/to/save", "chart_name")
```

## Features

- Pre-defined color palettes and themes
- Helper methods for common chart modifications
- Consistent styling across projects
- Support for dark mode
- Easy export to various formats

## Requirements

- Python >= 3.8
- altair >= 5.0.0
- pandas >= 1.0.0
- vl-convert-python >= 1.0.0
- country-converter >= 1.0.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.