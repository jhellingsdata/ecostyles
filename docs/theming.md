# Previewing & refining themes

How to visualise a theme, compare iterations, and live-test changes. All commands assume
the dev environment is set up (`uv venv && uv pip install -e ".[dev,test]"`).

## The chart gallery

Previews render every chart in the **gallery** so you see a theme across chart types:

- `specs/gallery.py` — Python builders (line, bar, scatter, area, heatmap, geoshape).
- `specs/gallery/*.json` — curated Vega-Lite specs (real examples). Their embedded `config`
  is stripped at render time and replaced with the theme under test, so **add any chart you
  care about here** (e.g. `chart.to_json()` from Altair) and it joins every preview.

## 1. Side-by-side preview (the main tool)

`scripts/preview_themes.py` renders the gallery under one or more theme *variants* into a
single HTML page — rows are charts, columns are variants.

```bash
uv run python scripts/preview_themes.py                    # all themes, side by side
uv run python scripts/preview_themes.py cotd article       # just these themes
uv run python scripts/preview_themes.py cotd --dark        # add cotd dark mode
```

Writes `renders/preview.html` (git-ignored) and opens it. Add `--no-open` to skip the browser,
`--scale 3` for higher-res images.

## 2. Compare against a previous iteration

To check whether an edit is an improvement, render your **working** theme next to the version
committed at any git ref (branch, tag, or commit) — they appear as adjacent columns:

```bash
uv run python scripts/preview_themes.py cotd --compare-ref v0.2.0   # working vs the last release
uv run python scripts/preview_themes.py cotd --compare-ref main     # working vs main
uv run python scripts/preview_themes.py cotd --compare-ref HEAD     # working vs last commit
```

Typical loop: `--compare-ref HEAD`, edit `src/ecostyles/themes/cotd.py`, re-run, eyeball the
before/after columns, repeat; commit when happy.

## 3. Live testing (edit → refresh)

For fast iteration, serve a page that **re-renders on every refresh** — no re-running the command:

```bash
uv run python scripts/preview_themes.py cotd --serve        # http://localhost:8000
```

Edit the theme file, refresh the browser, see the change. Use a single theme to keep each
refresh quick (it re-renders every gallery chart on each request). `Ctrl+C` to stop.

## 4. Shareable contact sheet

For a single labelled PNG per theme (handy for sharing or a design review):

```bash
uv run python scripts/render_themes.py            # renders/<theme>.png for all themes
uv run python scripts/render_themes.py cotd       # just one
```

## Regression guard

`tests/test_theme_rendering.py` smoke-renders every theme across the `gallery.py` builders, so
CI fails if a theme change produces a spec Vega-Lite can't render. Run locally with `pytest`.
