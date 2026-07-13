"""Build the bundled population dataset from the World Bank bulk CSV download.

Downloads the full ``SP.POP.TOTL`` ("Population, total") series for every economy as a
single zip, reshapes the wide World Bank CSV into a compact long CSV, and writes it to the
package data directory.

Run this to refresh the bundle (e.g. once a year when the World Bank updates):

    uv run python scripts/fetch_population.py

Output: src/ecostyles/data/population/population.csv  (columns: iso3,year,population)
"""

from __future__ import annotations

import csv
import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"
OUT = Path(__file__).resolve().parent.parent / "src/ecostyles/data/population/population.csv"


def _download_rows() -> list[list[str]]:
    """Download the zip and return the parsed rows of the main data CSV."""
    request = urllib.request.Request(URL, headers={"User-Agent": "ecostyles"})
    with urllib.request.urlopen(request, timeout=60) as response:
        blob = response.read()

    archive = zipfile.ZipFile(io.BytesIO(blob))
    # The data file is the one named API_*.csv (others are metadata).
    data_name = next(n for n in archive.namelist()
                     if n.startswith("API_") and n.endswith(".csv"))
    with archive.open(data_name) as f:
        text = io.TextIOWrapper(f, encoding="utf-8-sig")
        return list(csv.reader(text))


def reshape(rows: list[list[str]]) -> list[tuple[str, int, int]]:
    """Turn the wide World Bank CSV (a year per column) into (iso3, year, population)."""
    header_idx = next(i for i, r in enumerate(rows) if r and r[0] == "Country Name")
    header = rows[header_idx]
    year_cols = {i: int(c) for i, c in enumerate(header) if c.strip().isdigit()}

    records: list[tuple[str, int, int]] = []
    for row in rows[header_idx + 1:]:
        if len(row) < 4 or not row[1].strip():
            continue
        iso3 = row[1].strip()
        for i, year in year_cols.items():
            value = row[i].strip() if i < len(row) else ""
            if value:
                records.append((iso3, year, int(float(value))))
    records.sort(key=lambda r: (r[0], r[1]))
    return records


def main() -> None:
    records = reshape(_download_rows())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["iso3", "year", "population"])
        writer.writerows(records)

    years = {r[1] for r in records}
    economies = {r[0] for r in records}
    print(f"wrote {OUT.relative_to(OUT.parents[3])}: {len(records)} rows, "
          f"{len(economies)} economies, years {min(years)}-{max(years)}")


if __name__ == "__main__":
    main()
