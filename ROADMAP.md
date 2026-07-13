# ecostyles — Roadmap & Backlog

Living plan for refining and extending the package. Sequenced into phases;
each item notes **why** and an **acceptance** criterion so we know when it's done.

## Decisions locked

- **Package manager:** `uv` (dev workflow below). Commit `uv.lock` for reproducibility.
- **Altair:** target **6.x** (`altair>=6.2`). Current code + tests already pass on 6.2.2.
- **Versioning:** keep an explicit, visible version in `pyproject.toml` as the single source;
  expose `__version__` at runtime via stdlib `importlib.metadata`. Bump with **`bump-my-version`**
  (maintained successor to `bump2version`): one command edits + commits + tags. Chosen over
  `setuptools-scm` for a visible version and a simpler mental model.
- **CI/CD:** deliberately minimal — GitHub Actions test matrix on push, tag-triggered PyPI publish
  via Trusted Publishing. No release-please/semantic-release/changelog automation for now
  (overkill for a solo maintainer + <10 users).

### Dev workflow (new machine / colleagues)

```bash
uv venv --python 3.13
uv pip install -e ".[test]"    # or: uv sync  (once uv.lock is committed)
uv run pytest
```

---

## Phase 1 — Foundations & quick fixes (low risk, high value)

Goal: correct packaging, single-source the version, land the small API fixes. **✅ DONE.**

- [x] **Fix data packaging.** `recessions/*.json` now shipped via broadened `package-data`
  (`ecostyles = ["data/**/*"]`) + explicit `packages.find where=["src"]`. Verified in built wheel.
- [x] **Single-source the version.** `_version.py` reads `importlib.metadata.version("ecostyles")`
  with a dev fallback; the only literal lives in `pyproject.toml`.
- [x] **`save_chart`: `path` optional → saves to cwd.** Default `path=""`; directory only created
  when non-empty. Argument order kept as `(chart, path, name)` for backward compat; `name` required.
- [x] **Rewrite `add_source`** — now a **text-mark layer** pinned to `y='height'` with `yOffset`
  (default 30, configurable) to sit below the axis. Non-mutating, multi-line (string `\n` or list),
  coexists with an existing title. Bonus: because it's a layer (not vconcat), the chart keeps
  normal `width`/`height` sizing.
- [x] **`.gitignore`** `.venv/`; **docstrings/README** version + name fixes.

## Phase 2 — Theme differentiation

Decision: **keep one file per theme** (leave `article` as-is for now — revisit after the Phase 3
testing overhaul for deeper per-chart-type customisation). Build a distinct, impactful `cotd`.
A small shared base of good-viz defaults is deferred until it clearly earns its place.

- [x] **Design an improved `cotd`** (social/mobile). Distilled from `specs/cotd_example.json`:
  soft grey background (`#f4f4f4`), `line.strokeWidth 3`, larger/higher-contrast axis labels (13px,
  opacity 0.9), bold 18px narrative title, feed-friendly default view (500×340), no vertical
  gridlines. Also implemented real **dark mode** (was a silent no-op). Verified across line/bar,
  light + dark. *Acceptance met.*
- [ ] **`article` refinements** — deferred to post-Phase-3 (needs the rendering harness to review
  against varied chart types). Capture specific tweaks then.
- [ ] Consider extracting `add_source`/logo layers seen in `cotd_example.json` into helper methods
  (an `add_logo` companion to `add_source`) — see Phase 5.

## Phase 3 — Testing overhaul  **✅ DONE (utilities + harness); add_colour deferred to Phase 5**

Goal: real coverage of utilities + a visual theme-design harness.

- [x] **Unit tests** for `add_source`, `save_chart`, `modify_dimensions` — `tests/test_file_operations.py`.
  Coverage of `file_operations` went 16% → 100%; overall 60% → 85%. `add_colour`/`update_y_axis_title`
  proper tests are deferred until they're rewritten (Phase 5) rather than pinning broken behaviour.
- [x] **Theme rendering harness** — `specs/gallery.py` (theme-agnostic builders: line, bar, scatter,
  area, heatmap, geoshape), `tests/test_theme_rendering.py` (smoke-renders every theme × chart to
  PNG as a regression guard, incl. cotd dark), and `scripts/render_themes.py` (one command →
  labelled contact sheet per theme in `renders/`, git-ignored) for visual review.
- [x] **`noxfile.py`** now uses the **uv** backend across Python 3.10–3.14 (nox added to the `dev` extra).
- [ ] *(follow-up)* Consider committing reference contact sheets for visual diffing once themes settle.

## Phase 4 — CI/CD & release automation  **✅ DONE (needs one-time PyPI/GitHub setup — see RELEASING.md)**

- [x] **CI workflow** (`.github/workflows/ci.yml`): PR + push-to-main → `uv` install + pytest
  matrix on Python 3.10–3.14, with run-cancellation concurrency.
- [x] **Release workflow** (`.github/workflows/release.yml`): on tag `v*` → `uv build` → publish
  to PyPI via **Trusted Publishing** (OIDC, no tokens), gated behind a `pypi` environment.
- [x] **`bump-my-version`** configured in `pyproject.toml` (single-source version bump → commit →
  `v{version}` tag). Dry-run verified.
- [x] **`RELEASING.md`** — full guide incl. the one-time PyPI pending-publisher + GitHub
  environment setup you must do before the first release.
- **Correction landed here:** dropped Python 3.9 (Altair 6.2 requires ≥3.10; 3.9 is EOL) and
  added 3.14 (verified: full suite passes on 3.14.5). `requires-python = ">=3.10"`.

## Phase 5 — New functionality

- [x] **`add_population`** helper (`utils/population.py`) — **offline-first**. Reads a population
  snapshot **bundled in the package** (`data/population/population.csv`, World Bank `SP.POP.TOTL`,
  1960–latest, all economies), so normal use needs no network. Years newer than the bundle are
  fetched live from the World Bank API (`allow_fetch=False` to stay fully offline). World Bank
  chosen over the UN Data Portal (no auth token; UN-WPP-sourced). Accepts `year` or `year_column`;
  names/ISO2→ISO3 via `country_converter`; unresolved → NaN + warning. Refresh the bundle with
  `scripts/fetch_population.py` (single bulk-CSV download). Verified end-to-end; 15 tests.
- [ ] **`add_shaded_area` upgrade:** accept the packaged recessions datasets by name (uk/us) and
  respect theme `rect` config rather than hardcoded opacity.
- [ ] **Rewrite `add_colour`** into a correct, documented country→colour lookup (feeds Phase 3 tests).

## Phase 6 — Documentation

- [ ] **Method reference** for all public `EcoStyles` methods + utilities (docstrings → docs).
- [ ] Usage guide with worked examples per theme; contributing/release guide.

---

## Backlog (unscheduled / ideas)

- **Zero-line emphasis in themes.** Bake a conditional axis expression into
  `axisXQuantitative`/`axisYQuantitative` so the `value === 0` gridline is emphasised
  (solid, darker) while others stay dashed/faint. Note: use conditional axis *styling*
  props (`gridColor`/`gridDash`/`gridOpacity` via `alt.expr("datum.value === 0 ? ...")`),
  **not** `grid` (a whole-axis boolean that ignores expressions). Good for +/- bar charts.

- Dark-mode parity across all themes (only `cotd` takes `dark_mode` today).
- `display()` helper is oddly specific — review whether it earns its place.
- Type hints + `py.typed` marker for downstream type-checking.

## Open questions (resolve at each phase kickoff)

1. What specific tweaks does `article` need?
2. World Bank vs UN as the primary population source, and how much caching.
