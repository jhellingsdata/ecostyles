"""Integration test for the bundled population dataset (uses the real packaged CSV).

Kept separate from test_population.py so the network/bundle mocks there don't apply here.
"""

import ecostyles.utils.population as pop


def test_bundled_csv_loads_with_recent_data():
    pop._BUNDLED = None  # reset the lazy cache so we read the real packaged file
    data, max_year = pop._load_bundled()

    assert len(data) > 10_000, "expected the full World Bank series"
    assert max_year >= 2023, "bundle should be reasonably current"
    # A stable, well-known value from the World Bank series.
    assert data[("GBR", 2023)] == 68_526_000
