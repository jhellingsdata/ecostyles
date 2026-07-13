"""Core styling functionality for Economics Observatory visualisations."""

import json
from importlib import resources

import altair as alt
from altair import theme
import pandas as pd
import country_converter as coco
from . import themes
from .utils.file_operations import save_chart, add_source
from .utils.population import add_population
from .utils.palette import swatches
from .utils.fonts import setup_fonts

class EcoStyles:
    """Main class for Economics Observatory visualisation styling."""
    
    def __init__(self) -> None:
        # Set up fonts first
        self._font_dir = setup_fonts()

        self.eco_colours = {
            "red": "#e6224b",                      # ECO pink/red (categorical #2)
            "blue-light": "#179fdb",               # ECO light-blue
            "blue-dark": "#122b39",                # ECO dark-blue / background
            "yellow": "#f4c245",                   # ECO yellow
            "orange": "#eb5c2e",                   # ECO orange
            "turquoise": "#36b7b4",                # ECO turquoise (categorical #1)
            "green": "#00a767",                    # ECO green
            "mid-blue": "#0063af",                 # ECO mid-blue
            "purple": "#5c267b",                   # ECO purple
            "dot": "#f4134d",                      # ECO dot (primary brand mark)
            "grey": "#676a86",                     # ECO grey (axes, labels, de-emphasis)
        }

        self.organisation_colours = {
            'OBR': 'rgb(69,101,133)',             # OBR blue
            'NIESR': 'rgb(104,27,20)'             # NIESR red
        }

        # Official flag / brand colours for the UK nations.
        self.national_colours = {
            'GB-SCT': '#005EB8',  # Scotland
            'GB-WLS': '#C8102E',  # Wales, red (green is 00B140)
            'GB-NIR': '#FEDD00',  # Northern Ireland, yellow
            'UK-red': '#C8102E',  # UK, red
            'UK-blue': '#012169'  # UK, blue
        }

        # ECO default colours for representing the UK nations (from the ECO palette),
        # for a consistent on-brand look rather than the official flag colours above.
        self.national_eco_colours = {
            'GB-ENG': '#5c267b',  # England — ECO purple
            'GB-WLS': '#e6224b',  # Wales — ECO pink
            'GB-SCT': '#0063af',  # Scotland — ECO mid-blue
            'GB-NIR': '#00a767',  # Northern Ireland — ECO green
        }

        self.palette = {
            "light": {
                "Other_3": "#d6d4d4",             # light gray
                "deemphasise_color": "#B4B4B4",   # gray
                "dark_grey": "#596870",           # dark gray
                "Deemphasise_Discrete": "#182a38",# dark bluish-gray
                "Deemphasise_Continuous": "#182a3833",
                "accent": "#179fdb",              # bright blue
                "text": "#122b39",                # dark blue
                "domain": "#122b39",              # dark blue
                "non-uk": "#a8c0de",             # light blue / grey
                "country-group": "#eb5c2e",       
                "background": "#fff",
            },
            "dark": {
                "Other_3": "#d6d4d4",
                "deemphasise_color": "#B4B4B4",
                "dark_grey": "#596870",
                "Deemphasise_Discrete": "#182a38",
                "Deemphasise_Continuous": "#182a3833",
                "accent": "#179fdb",
                "text": '#b4c8d8',
                "domain": "#b4c8d8",
                "non-uk": "#a8c0de",
                "country-group": "#eb5c2e",
                "background": "#122b39",
            },
            "light-transparent": {
                "background": None,
            },
            "dark-transparent": {
                "text": "#fff",
                "background": None,
            },
        }

        self.country_groups = {
            'OECD': 'OECD',
            'OECDE': 'OECD-Europe',
            'EU27': 'EU27',
            'EU27_2020': 'EU27 (2020)',
            'EA19': 'EA19',
            'G-7': 'G7',
            'G7': 'G7'
        }

    def get_country_groups_list(self) -> list:
        """Return a list of country group identifiers."""
        return list(self.country_groups.keys())

    def get_country_groups_dict(self) -> dict:
        """Return a dictionary of country group identifiers and their corresponding codes."""
        return self.country_groups

    def eco_palette(self, theme='light'):
        """Return the colour palette for the specified theme."""
        return self.palette.get(theme)
    
    def get_eco_colours(self):
        """Return the custom colours dictionary."""
        return self.eco_colours
    
    def get_national_colours(self, country_code=None):
        """Return the national (flag) colours dictionary or a specific country colour."""
        if country_code:
            return self.national_colours.get(country_code)
        return self.national_colours

    def get_national_eco_colours(self, country_code=None):
        """Return the ECO-palette nation colours dictionary or a specific country colour."""
        if country_code:
            return self.national_eco_colours.get(country_code)
        return self.national_eco_colours

    def show_colours(self, which="eco", **kwargs):
        """Return an Altair swatch chart for an organisation palette (a visual reference).

        Args:
            which: 'eco', 'national', 'national_eco', or a custom dict/list of colours.
            **kwargs: forwarded to the swatch renderer (e.g. columns, size, title).
        """
        groups = {
            "eco": (self.eco_colours, "ECO colours"),
            "national": (self.national_colours, "UK nation flag colours"),
            "national_eco": (self.national_eco_colours, "UK nation ECO colours"),
        }
        if isinstance(which, (dict, list, tuple)):
            return swatches(which, **kwargs)
        if which not in groups:
            raise ValueError(f"which must be one of {list(groups)} or a dict/list of colours")
        colours, default_title = groups[which]
        kwargs.setdefault("title", default_title)
        return swatches(colours, **kwargs)

    def preview_theme_colours(self, theme_name="article"):
        """Return stacked swatch charts of a theme's colour ranges.

        Shows the category / diverging / heatmap / ordinal palettes the theme defines.
        """
        theme_getters = {
            "article": themes.article.get_theme,
            "cotd": themes.cotd.get_theme,
            "newsletter": themes.newsletter.get_theme,
        }
        if theme_name not in theme_getters:
            raise ValueError(f"theme_name must be one of {list(theme_getters)}")
        ranges = theme_getters[theme_name]()["config"].get("range", {})
        charts = [swatches(palette, title=f"{theme_name}: {name}", columns=len(palette))
                  for name, palette in ranges.items()]
        return alt.vconcat(*charts)

    def register_and_enable_theme(self, theme_name: str="article", dark_mode: bool=False):
        """Register and enable a custom theme.
        
        Args:
            theme_name: One of 'cotd', 'article', or 'newsletter'
            dark_mode: Whether to use dark mode theme (currently only 'cotd' honours this)
        """
        if theme_name not in ['cotd', 'article', 'newsletter']:
            raise ValueError("theme_name must be 'cotd', 'article', or 'newsletter'")
        
        # def theme_function():
        #     if theme_name == "cotd":
        #         return themes.cotd.get_theme(dark_mode)
        #     elif theme_name == "article":
        #         return themes.article.get_theme()
        # alt.themes.register(theme_name, theme_function)
        # theme.enable(theme_name)
        
        # Register the theme
        if theme_name == "cotd":
            @theme.register("cotd", enable=True)
            def custom_theme() -> theme.ThemeConfig:
                return themes.cotd.get_theme(dark_mode)
        elif theme_name == "article":
            @theme.register("article", enable=True)
            def custom_theme() -> theme.ThemeConfig:
                return themes.article.get_theme()
        elif theme_name == "newsletter":
            @theme.register("newsletter", enable=True)
            def custom_theme() -> theme.ThemeConfig:
                return themes.newsletter.get_theme()


    def add_colour(self, df: pd.DataFrame, country_column: str, 
                  colour_override: dict=None) -> pd.DataFrame:
        """Add colour columns to a dataframe based on country codes.
        
        Args:
            df: Input dataframe
            country_column: Name of column containing country codes/names
            colour_override: Optional dictionary to override default colors
        
        Returns:
            DataFrame with added color columns

        Note: INCOMPLETE
        """
        palette = self.palette.copy()

        if colour_override:
            palette.update(colour_override)

        first_country = df[country_column].iloc[0]
        if len(first_country) != 3:
            df['ISO3'] = coco.convert(df[country_column].tolist(), to='ISO3')
            country_col_to_use = 'ISO3'
        else:
            country_col_to_use = country_column

        df['color-bar'] = df[country_col_to_use].apply(
            lambda x: palette.get('GBR-bar') if x == 'GBR' else
            palette.get('light').get('country-group') if x in self.country_groups else
            palette.get('light').get('non-uk')
        )

        df['color-line'] = df[country_col_to_use].apply(
            lambda x: palette.get(x, palette.get('domain'))
        )

        return df

    def get_recessions(self, region: str = "uk") -> pd.DataFrame:
        """Return recession periods for a region as a dataframe.

        Args:
            region: 'uk' or 'us'.

        Returns:
            DataFrame with datetime 'start' and 'end' columns, one row per recession.
            Pass it straight to ``add_shaded_area(periods=...)``.
        """
        key = region.lower()
        if key not in ("uk", "us"):
            raise ValueError("region must be 'uk' or 'us'")

        data_file = resources.files("ecostyles.data").joinpath("recessions", f"recessions_{key}.json")
        with resources.as_file(data_file) as path, open(path) as f:
            records = json.load(f)

        df = pd.DataFrame(records).rename(columns={"Start": "start", "End": "end"})
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        return df

    def add_shaded_area(self, start_date=None, end_date=None, *, periods=None,
                        start_field="start", end_field="end", color=None, opacity=None):
        """Return a shaded rectangle layer spanning one or more date ranges.

        Provide **either** a single ``start_date`` and ``end_date`` (a custom range) **or**
        a ``periods`` dataframe with ``start_field``/``end_field`` columns — e.g. from
        :meth:`get_recessions` to shade every recession. Layer the result over your chart
        (``chart + styles.add_shaded_area(...)``).

        With no ``color``/``opacity``, the active theme's ``rect`` config is used.

        Args:
            start_date, end_date: Endpoints of a single shaded band.
            periods: Dataframe of multiple bands (overrides start_date/end_date).
            start_field, end_field: Column names for the band endpoints in ``periods``.
            color: Optional fill colour override.
            opacity: Optional opacity override.
        """
        if periods is not None:
            data = periods
        else:
            if start_date is None or end_date is None:
                raise ValueError("Provide `periods`, or both `start_date` and `end_date`.")
            data = pd.DataFrame({start_field: [pd.to_datetime(start_date)],
                                 end_field: [pd.to_datetime(end_date)]})

        mark_kwargs = {}
        if color is not None:
            mark_kwargs["fill"] = color
        if opacity is not None:
            mark_kwargs["opacity"] = opacity

        return (
            alt.Chart(data)
            .mark_rect(**mark_kwargs)
            .encode(x=alt.X(f"{start_field}:T"), x2=f"{end_field}:T")
        )
    
    def update_y_axis_title(self, chart: alt.Chart, title: str):
        """Update y-axis title of an Altair chart."""

        spec = chart.to_dict()
        if 'encoding' in spec and 'y' in spec['encoding']:
            if 'axis' not in spec['encoding']['y']:
                spec['encoding']['y']['axis'] = {}
            spec['encoding']['y']['axis']['title'] = title
        elif 'layer' in spec:
            for layer in spec['layer']:
                if 'encoding' in layer and 'y' in layer['encoding']:
                    if 'axis' not in layer['encoding']['y']:
                        layer['encoding']['y']['axis'] = {}
                    layer['encoding']['y']['axis']['title'] = title
                    break
        else:
            print('Warning: y-axis not found in chart')
        
        return alt.Chart.from_dict(spec)
    
    def display(self, chart, title, subtitle, y_title):
        """Display two versions of a chart with different titles."""
        title_params = alt.TitleParams(
            text=title,
            subtitle=subtitle,
        )
        chart_title = chart.properties(title=title_params)
        chart_y_title = self.update_y_axis_title(chart, y_title)

        chart_title.display()
        chart_y_title.display()

        return chart_title, chart_y_title

    # Delegate file operations to utils module
    def save(self, *args, **kwargs):
        """Save chart to file(s). See utils.file_operations.save_chart for details."""
        return save_chart(*args, **kwargs)
    
    def add_source(self, *args, **kwargs):
        """Add source attribution to chart. See utils.file_operations.add_source for details."""
        return add_source(*args, **kwargs)

    def add_population(self, *args, **kwargs):
        """Add a population column via the World Bank API. See utils.population.add_population."""
        return add_population(*args, **kwargs)