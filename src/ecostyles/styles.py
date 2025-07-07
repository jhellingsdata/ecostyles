"""Core styling functionality for Economics Observatory visualisations."""

import altair as alt
from altair import theme
import pandas as pd
import country_converter as coco
from . import themes
from .utils.file_operations import save_chart, add_source
from .utils.fonts import setup_fonts

class EcoStyles:
    """Main class for Economics Observatory visualisation styling."""
    
    def __init__(self) -> None:
        # Set up fonts first
        self._font_dir = setup_fonts()

        self.eco_colours = {
            "red": "#e6224b",                      # light red
            "blue-light": "#179fdb",               # bright blue
            "blue-dark": "#122b39",                # dark blue
            "yellow": "#f4c245",                   # light yellow
            "orange": "#eb5c2e",                   # orange
            "turquoise": "#36b7b4"                 # turquoise
        }

        self.organisation_colours = {
            'OBR': 'rgb(69,101,133)',             # OBR blue
            'NIESR': 'rgb(104,27,20)'             # NIESR red
        }

        self.national_colours = {
            'GB-SCT': '#005EB8',  # Scotland
            'GB-WLS': '#C8102E',  # Wales, red (green is 00B140)
            'GB-NIR': '#FEDD00',  # Northern Ireland, yellow
            'UK-red': '#C8102E',  # UK, red
            'UK-blue': '#012169'  # UK, blue
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
        """Return the national colours dictionary or specific country color."""
        if country_code:
            return self.national_colours.get(country_code)
        return self.national_colours

    def register_and_enable_theme(self, theme_name: str="article", dark_mode: bool=False):
        """Register and enable a custom theme.
        
        Args:
            theme_name: One of 'cotd', 'article', or 'growth_diagnostics'
            dark_mode: Whether to use dark mode theme
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

    def add_shaded_area(self, start_date, end_date):
        """Add a shaded area between two dates on a chart."""
        df = pd.DataFrame({'start': [start_date], 'end': [end_date]})
        
        rect = alt.Chart(df).mark_rect(
            opacity=0.5,
        ).encode(
            x=alt.X('start:T'),
            x2='end:T'
        )

        return rect
    
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