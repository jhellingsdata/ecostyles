"""Preview and compare ecostyles themes across the chart gallery.

Renders every gallery chart under one or more theme *variants* and lays them out side by
side as PNGs in a single HTML page, so you can eyeball a theme and — crucially — compare
iterations (e.g. your working edits vs the version committed on a branch/tag).

Charts come from two places (both theme-agnostic once their own config is stripped):
  - specs/gallery.py       -> the Python builders (build_all)
  - specs/gallery/*.json   -> curated Vega-Lite specs

Examples
--------
    uv run python scripts/preview_themes.py                     # all themes, side by side
    uv run python scripts/preview_themes.py cotd article        # just these themes
    uv run python scripts/preview_themes.py cotd --dark         # add cotd dark mode
    uv run python scripts/preview_themes.py cotd --compare-ref HEAD   # working cotd vs cotd @HEAD
    uv run python scripts/preview_themes.py cotd --serve        # live: edit theme, refresh browser

Output: renders/preview.html (git-ignored). --serve starts a local server instead.
"""

from __future__ import annotations

import argparse
import base64
import inspect
import json
import subprocess
import sys
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import vl_convert as vlc

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
THEMES = ["article", "cotd", "newsletter"]

sys.path.insert(0, str(SPECS))
from ecostyles import EcoStyles  # noqa: E402  (registers the bundled fonts)

EcoStyles()


# --------------------------------------------------------------------------- charts
def load_charts() -> list[tuple[str, dict]]:
    """Return [(name, spec_without_config)] from the Python builders and JSON specs."""
    charts: list[tuple[str, dict]] = []

    import importlib
    gallery = importlib.import_module("gallery")
    importlib.reload(gallery)  # pick up edits when serving
    for name, chart in gallery.build_all().items():
        spec = chart.to_dict()
        spec.pop("config", None)
        charts.append((f"gallery.{name}", spec))

    for path in sorted((SPECS / "gallery").glob("*.json")):
        spec = json.loads(path.read_text())
        spec.pop("config", None)          # strip embedded config; the theme supplies it
        charts.append((path.stem, spec))

    return charts


# --------------------------------------------------------------------------- themes
def _get_theme_fn(name: str, ref: str | None):
    """Return a theme's get_theme() callable, from the working tree or a git ref."""
    rel = f"src/ecostyles/themes/{name}.py"
    if ref:
        source = subprocess.check_output(["git", "show", f"{ref}:{rel}"], text=True, cwd=ROOT)
    else:
        source = (ROOT / rel).read_text()  # read fresh each call so edits show when serving
    namespace: dict = {}
    exec(compile(source, f"{name}@{ref or 'working'}", "exec"), namespace)
    return namespace["get_theme"]


def theme_config(name: str, dark: bool = False, ref: str | None = None) -> dict:
    """Return the ``config`` block for a theme (optionally dark, optionally from a git ref)."""
    fn = _get_theme_fn(name, ref)
    accepts_dark = bool(inspect.signature(fn).parameters)
    return (fn(dark) if accepts_dark else fn())["config"]


def build_variants(names: list[str], dark: bool, compare_ref: str | None) -> list[tuple[str, dict]]:
    """Build the ordered list of (label, config) columns to render."""
    variants: list[tuple[str, dict]] = []
    for name in names:
        if compare_ref:
            variants.append((f"{name} @{compare_ref}", theme_config(name, ref=compare_ref)))
            variants.append((f"{name} (working)", theme_config(name)))
        else:
            variants.append((name, theme_config(name)))
        if dark and name == "cotd":
            variants.append((f"{name} (dark)", theme_config(name, dark=True)))
    return variants


# --------------------------------------------------------------------------- render
def render_png(spec: dict, config: dict, scale: float) -> bytes:
    return vlc.vegalite_to_png(vl_spec=json.dumps({**spec, "config": config}), scale=scale)


def _img(png: bytes) -> str:
    return f'<img loading="lazy" src="data:image/png;base64,{base64.b64encode(png).decode()}">'


def build_html(variants: list[tuple[str, dict]], charts: list[tuple[str, dict]], scale: float) -> str:
    head = "".join(f"<th>{label}</th>" for label, _ in variants)
    rows = []
    for chart_name, spec in charts:
        cells = [f"<th class='name'>{chart_name}</th>"]
        for _, config in variants:
            try:
                cells.append(f"<td>{_img(render_png(spec, config, scale))}</td>")
            except Exception as exc:  # noqa: BLE001 - show render errors inline, keep going
                cells.append(f"<td class='err'>{type(exc).__name__}: {exc}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>ecostyles theme preview</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; margin: 24px; background: #fff; color: #122b39; }}
  h1 {{ font-size: 18px; }}
  .meta {{ color: #676a86; font-size: 13px; margin-bottom: 16px; }}
  table {{ border-collapse: collapse; }}
  th, td {{ padding: 10px; vertical-align: top; text-align: left; }}
  thead th {{ position: sticky; top: 0; background: #fff; border-bottom: 2px solid #eee; font-size: 13px; }}
  th.name {{ font-family: ui-monospace, monospace; font-size: 12px; color: #676a86; white-space: nowrap; }}
  tbody tr {{ border-bottom: 1px solid #f0f0f0; }}
  img {{ max-width: 460px; height: auto; display: block; }}
  .err {{ color: #e6224b; font-family: monospace; font-size: 12px; max-width: 320px; }}
</style></head><body>
<h1>ecostyles theme preview</h1>
<div class="meta">{len(charts)} charts &times; {len(variants)} variants &middot; refresh to re-render</div>
<table><thead><tr><th class="name">chart</th>{head}</tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</body></html>"""


# --------------------------------------------------------------------------- modes
def write_file(html: str, open_browser: bool) -> Path:
    out = ROOT / "renders" / "preview.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    if open_browser:
        webbrowser.open(out.as_uri())
    return out


def serve(args, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Rebuild everything each request so theme/spec edits show on refresh.
            variants = build_variants(args.themes, args.dark, args.compare_ref)
            html = build_html(variants, load_charts(), args.scale).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *_):  # quiet
            pass

    url = f"http://localhost:{port}/"
    print(f"Serving theme preview at {url} (edit a theme, refresh to re-render; Ctrl+C to stop)")
    webbrowser.open(url)
    HTTPServer(("localhost", port), Handler).serve_forever()


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("themes", nargs="*", default=THEMES, help=f"themes to preview (default: {THEMES})")
    parser.add_argument("--dark", action="store_true", help="also render cotd dark mode")
    parser.add_argument("--compare-ref", metavar="REF",
                        help="add a column per theme showing it as of this git ref (e.g. HEAD, main, v0.2.0)")
    parser.add_argument("--scale", type=float, default=2.0, help="render scale (default 2)")
    parser.add_argument("--serve", action="store_true", help="serve a live-reloading page instead of writing a file")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-open", action="store_true", help="don't open a browser")
    args = parser.parse_args(argv)

    unknown = [t for t in args.themes if t not in THEMES]
    if unknown:
        parser.error(f"unknown theme(s) {unknown}; choose from {THEMES}")

    if args.serve:
        serve(args, args.port)
        return

    variants = build_variants(args.themes, args.dark, args.compare_ref)
    out = write_file(build_html(variants, load_charts(), args.scale), not args.no_open)
    print(f"wrote {out.relative_to(ROOT)} ({len(variants)} variants)")


if __name__ == "__main__":
    main(sys.argv[1:])
