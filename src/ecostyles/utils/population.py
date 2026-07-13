"""Fetch population data and join it onto a dataframe.

Uses the World Bank Indicators API (indicator ``SP.POP.TOTL``, "Population, total"),
which needs no authentication, accepts ISO3 country codes directly, and sources its
figures from the UN World Population Prospects plus national statistical offices.

Public entry point: :func:`add_population`.
"""

from __future__ import annotations

import json
import urllib.request
import warnings
from functools import lru_cache

import country_converter as coco
import pandas as pd

_WB_BASE = "https://api.worldbank.org/v2"
_WB_INDICATOR = "SP.POP.TOTL"


def _build_url(iso3: str, year: int) -> str:
    # One country, one year: the simplest, most portable World Bank request. (Multi-country
    # `;` batching and `date=start:end` ranges are documented but blocked by some corporate
    # networks/proxies, so we keep requests to this robust primitive and cache each result.)
    return f"{_WB_BASE}/country/{iso3}/indicator/{_WB_INDICATOR}?date={year}&format=json"


def _parse_worldbank_payload(payload) -> dict[tuple[str, int], float | None]:
    """Turn a World Bank JSON payload into a ``{(iso3, year): value}`` mapping.

    The payload is ``[metadata, rows]``; ``rows`` is ``None`` when nothing matched.
    """
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return {}

    result: dict[tuple[str, int], float | None] = {}
    for row in payload[1]:
        iso3 = row.get("countryiso3code")
        date = row.get("date")
        if iso3 and date is not None:
            result[(iso3, int(date))] = row.get("value")
    return result


@lru_cache(maxsize=4096)
def _fetch_one(iso3: str, year: int, timeout: int) -> dict[tuple[str, int], float | None]:
    """Fetch population for a single ISO3 code and year. Cached per unique request."""
    request = urllib.request.Request(
        _build_url(iso3, year),
        headers={"User-Agent": "ecostyles"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return _parse_worldbank_payload(payload)


def add_population(df: pd.DataFrame, country_column: str, year: int | None = None, *,
                   year_column: str | None = None, population_column: str = "population",
                   timeout: int = 30) -> pd.DataFrame:
    """Add a population column to ``df`` by matching country codes to World Bank data.

    Args:
        df: Input dataframe (not mutated; a copy is returned).
        country_column: Column of country identifiers. ISO3 codes, names, or ISO2 all work
            (converted to ISO3 via ``country_converter``).
        year: A single year to fetch for every row. Provide this **or** ``year_column``.
        year_column: Column holding a per-row year (for panel/time-series data). Provide
            this **or** ``year``.
        population_column: Name of the column to add (default ``"population"``).
        timeout: HTTP timeout in seconds.

    Returns:
        A copy of ``df`` with ``population_column`` added. Rows whose country/year can't be
        resolved get ``NaN`` and a warning is emitted.
    """
    if (year is None) == (year_column is None):
        raise ValueError("Provide exactly one of `year` or `year_column`.")
    if year_column is not None and year_column not in df.columns:
        raise KeyError(f"year_column {year_column!r} not found in dataframe")
    if country_column not in df.columns:
        raise KeyError(f"country_column {country_column!r} not found in dataframe")

    df = df.copy()

    # Resolve everything to ISO3 (coco accepts ISO3/name/ISO2 and returns ISO3).
    converted = coco.convert(df[country_column].astype(str).tolist(), to="ISO3", not_found=None)
    if isinstance(converted, str):  # coco returns a bare string for a single input
        converted = [converted]
    iso3 = pd.Series(converted, index=df.index)

    # Which years do we need, and what year does each row want?
    if year is not None:
        row_years = pd.Series(int(year), index=df.index)
    else:
        row_years = df[year_column].astype(int)
    years = row_years.tolist()

    # Unique (country, year) pairs to fetch — avoids repeat calls; lru_cache does the rest.
    pairs = {(code, int(yr)) for code, yr in zip(iso3.tolist(), years) if code}
    if not pairs:
        warnings.warn("add_population: no valid country codes resolved; population set to NaN.")
        df[population_column] = pd.NA
        return df

    lookup: dict[tuple[str, int], float | None] = {}
    for code, yr in pairs:
        lookup.update(_fetch_one(code, yr, timeout))

    df[population_column] = [
        lookup.get((code, int(yr))) if code else None
        for code, yr in zip(iso3, row_years)
    ]

    missing = int(df[population_column].isna().sum())
    if missing:
        warnings.warn(
            f"add_population: {missing} row(s) had no population value "
            "(unresolved country or year not available)."
        )
    return df
