"""Unit tests for ecostyles.utils.population.

Network is mocked out (``_fetch_one`` is patched), so these run offline and deterministically.
The live World Bank path is exercised manually during development.
"""

import pandas as pd
import pytest

import ecostyles.utils.population as pop

# Canned "World Bank" values keyed by (iso3, year).
FAKE = {
    ("GBR", 2023): 68_526_000,
    ("FRA", 2023): 68_372_286,
    ("GBR", 2000): 58_900_000,
    ("GBR", 2020): 67_100_000,
    ("USA", 2020): 331_500_000,
    ("DEU", 2022): 83_177_813,
}


def _fake_fetch(iso3, year, timeout):
    value = FAKE.get((iso3, year))
    return {(iso3, year): value} if value is not None else {}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(pop, "_fetch_one", _fake_fetch)


# ------------------------------------------------------------------- happy paths
def test_single_year_iso3():
    df = pd.DataFrame({"country": ["GBR", "FRA"], "m": [1, 2]})
    out = pop.add_population(df, "country", year=2023)
    assert out["population"].tolist() == [68_526_000, 68_372_286]
    assert "population" not in df.columns  # input not mutated


def test_name_is_converted_to_iso3():
    out = pop.add_population(pd.DataFrame({"c": ["Germany"]}), "c", year=2022)
    assert out["population"].iloc[0] == 83_177_813


def test_panel_year_column():
    df = pd.DataFrame({"country": ["GBR", "GBR", "USA"], "yr": [2000, 2020, 2020]})
    out = pop.add_population(df, "country", year_column="yr")
    assert out["population"].tolist() == [58_900_000, 67_100_000, 331_500_000]


def test_custom_population_column_name():
    out = pop.add_population(pd.DataFrame({"country": ["GBR"]}), "country",
                            year=2023, population_column="pop_total")
    assert "pop_total" in out.columns


# --------------------------------------------------------------- missing / errors
def test_unknown_country_gives_nan_and_warns():
    df = pd.DataFrame({"country": ["GBR", "Atlantis"]})
    with pytest.warns(UserWarning):
        out = pop.add_population(df, "country", year=2023)
    assert out["population"].iloc[0] == 68_526_000
    assert pd.isna(out["population"].iloc[1])


def test_year_not_available_gives_nan():
    # 1990 isn't in FAKE, so the fetch returns nothing.
    with pytest.warns(UserWarning):
        out = pop.add_population(pd.DataFrame({"country": ["GBR"]}), "country", year=1990)
    assert pd.isna(out["population"].iloc[0])


def test_requires_exactly_one_of_year_or_year_column():
    df = pd.DataFrame({"country": ["GBR"], "yr": [2023]})
    with pytest.raises(ValueError):
        pop.add_population(df, "country")  # neither
    with pytest.raises(ValueError):
        pop.add_population(df, "country", year=2023, year_column="yr")  # both


def test_missing_columns_raise_keyerror():
    df = pd.DataFrame({"country": ["GBR"]})
    with pytest.raises(KeyError):
        pop.add_population(df, "nope", year=2023)
    with pytest.raises(KeyError):
        pop.add_population(df, "country", year_column="missing")


# ----------------------------------------------------------------- payload parser
def test_parse_worldbank_payload_extracts_rows():
    payload = [
        {"page": 1, "pages": 1},
        [{"countryiso3code": "GBR", "date": "2023", "value": 68_526_000}],
    ]
    assert pop._parse_worldbank_payload(payload) == {("GBR", 2023): 68_526_000}


@pytest.mark.parametrize("payload", [
    [{"message": "no data"}, None],   # World Bank returns None rows when nothing matches
    [],                                # malformed
    {"unexpected": True},              # not even a list
])
def test_parse_worldbank_payload_handles_empty(payload):
    assert pop._parse_worldbank_payload(payload) == {}
