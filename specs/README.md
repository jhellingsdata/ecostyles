# specs/

Reusable chart specifications for developing and testing themes. Drop charts here that
represent real, varied cases (line, bar, scatter, heatmap, maps, small multiples,
annotated/narrative charts) so we can render them across every theme and compare.

Two formats are welcome:

- **Vega-Lite JSON** (`*.json`) — a full spec, e.g. exported from Altair via
  `chart.to_json()` or copied from the Vega editor. Note these usually embed their own
  `config`, so they render with *their own* styling, not the active `ecostyles` theme;
  strip the `config` block if you want to test a theme against the spec.
- **Altair builders** (`*.py`) — a function returning an `alt.Chart` (no theme applied),
  which the theme test harness (Phase 3) can render under each theme.

## Contents

- `cotd_example.json` — a "chart of the day" reference (UK taxpayer income bunching)
  showing the more impactful design direction: soft grey background, thick lines, large
  narrative title, annotation callout, source line, and logo. Its embedded `config` was
  the basis for the `cotd` theme. Note: it builds on the older `article` config, so some
  properties are redundant or overridden per-encoding.
