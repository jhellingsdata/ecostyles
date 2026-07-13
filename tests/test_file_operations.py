"""Unit tests for ecostyles.utils.file_operations."""

import json

import altair as alt
import pandas as pd
import pytest

from ecostyles.utils.file_operations import (
    _strip_midnight_timestamps, add_source, modify_dimensions, save_chart,
)


@pytest.fixture
def line_chart():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    return alt.Chart(df).mark_line().encode(x="x:Q", y="y:Q")


def _find(obj, key):
    """Recursively find the first value stored under ``key`` in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            found = _find(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find(v, key)
            if found is not None:
                return found
    return None


# --------------------------------------------------------------------- add_source
def test_add_source_returns_layer_and_preserves_title(line_chart):
    base = line_chart.properties(title=alt.TitleParams("My title", subtitle="Sub"))
    before = base.to_dict()

    out = add_source(base, "ONS")
    spec = out.to_dict()

    assert "layer" in spec, "expected a layered chart"
    assert spec["layer"][0]["title"]["text"] == "My title", "original title must survive"
    assert base.to_dict() == before, "input chart must not be mutated"


def test_add_source_prefixes_bare_string(line_chart):
    text = _find(add_source(line_chart, "ONS").to_dict(), "_source")
    assert text == "Source: ONS"


def test_add_source_does_not_prefix_note(line_chart):
    text = _find(add_source(line_chart, "Note: seasonally adjusted").to_dict(), "_source")
    assert text == "Note: seasonally adjusted"


@pytest.mark.parametrize("source,expected", [
    (["Source: A", "Note: B"], "Source: A\nNote: B"),
    ("Source: A\nNote: B", "Source: A\nNote: B"),
])
def test_add_source_multiline(line_chart, source, expected):
    text = _find(add_source(line_chart, source).to_dict(), "_source")
    assert text == expected


def test_add_source_y_offset_applied(line_chart):
    spec = add_source(line_chart, "ONS", y_offset=45).to_dict()
    caption_mark = spec["layer"][-1]["mark"]
    assert caption_mark["type"] == "text"
    assert caption_mark["yOffset"] == 45


def test_add_source_keeps_dimensions(line_chart):
    sized = line_chart.properties(width=321, height=123)
    spec = add_source(sized, "ONS").to_dict()
    # A layer (unlike vconcat) keeps top-level width/height addressable.
    assert spec["width"] == 321 and spec["height"] == 123


# --------------------------------------------------------------------- save_chart
def test_save_chart_requires_name(line_chart):
    with pytest.raises(ValueError):
        save_chart(line_chart, "some/path")


def test_save_chart_to_cwd(line_chart, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    save_chart(line_chart, name="chart", width=200, height=150)
    assert (tmp_path / "chart.json").exists()
    assert (tmp_path / "chart.png").exists()


def test_save_chart_with_path_svg_and_minified_json(line_chart, tmp_path):
    out = tmp_path / "nested" / "dir"
    save_chart(line_chart, str(out), "chart", width=200, height=150, svg=True)
    assert (out / "chart.json").exists()
    assert (out / "chart.png").exists()
    assert (out / "chart.svg").exists()
    # JSON should be minified (single line, no indentation newlines)
    assert "\n" not in (out / "chart.json").read_text()


def test_save_chart_source_writes_extra_png(line_chart, tmp_path):
    save_chart(line_chart, str(tmp_path), "chart", width=200, height=150, source="ONS")
    assert (tmp_path / "chart_source.png").exists()


# ---------------------------------------------------------------- modify_dimensions
def test_modify_dimensions_sets_width_height(line_chart):
    spec = json.loads(modify_dimensions(line_chart, 111, 222))
    assert spec["width"] == 111
    assert spec["height"] == 222


def test_modify_dimensions_falsy_leaves_unset(line_chart):
    spec = json.loads(modify_dimensions(line_chart, 0, 0))
    assert "width" not in spec and "height" not in spec


# ---------------------------------------------------------------- timestamp stripping
@pytest.mark.parametrize("raw,expected", [
    ('"2020-01-01T00:00:00"', '"2020-01-01"'),
    ('"2020-01-01T00:00:00.000Z"', '"2020-01-01"'),
    ('"2020-01-01T12:30:00"', '"2020-01-01T12:30:00"'),   # non-midnight preserved
])
def test_strip_midnight_timestamps(raw, expected):
    assert _strip_midnight_timestamps(raw) == expected


def _dated_chart():
    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01", "2020-02-01"]), "v": [1, 2]})
    return alt.Chart(df).mark_line().encode(x="date:T", y="v:Q")


def test_save_chart_strips_midnight_timestamps(tmp_path):
    save_chart(_dated_chart(), str(tmp_path), "c", width=100, height=80)
    text = (tmp_path / "c.json").read_text()
    assert "T00:00:00" not in text
    assert "2020-01-01" in text


def test_save_chart_can_keep_timestamps(tmp_path):
    save_chart(_dated_chart(), str(tmp_path), "c", width=100, height=80, strip_timestamps=False)
    assert "T00:00:00" in (tmp_path / "c.json").read_text()
