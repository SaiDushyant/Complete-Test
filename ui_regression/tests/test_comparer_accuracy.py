"""
Tests for Comparer Matching Accuracy, Drift Prevention, and Noise Filtering.
Validates >= 95% matching accuracy, domino cascade prevention, duplicate ID ordering,
table cell text normalization, and transient loader suppression.
"""

import json
from pathlib import Path
import pytest

from comparer.comparer import ElementComparer, NoiseFilter


def test_domino_cascade_prevention():
    """
    Verify that modifying or shifting a single element does NOT cause a cascading
    domino effect of false diffs on subsequent elements with bare tag locators.
    """
    comparer = ElementComparer()

    # Create a baseline of 100 span and div elements
    baseline_elements = []
    for i in range(100):
        baseline_elements.append({
            "index": i,
            "tag": "span",
            "locator": "span",
            "is_unique": False,
            "classes": "item-text",
            "text": f"Item {i}",
            "visible": True,
            "attributes": {"class": "item-text"},
        })

    # In live, insert 1 new element at index 10 and modify index 50
    live_elements = [dict(e) for e in baseline_elements]
    live_elements.insert(10, {
        "index": 10,
        "tag": "span",
        "locator": "span",
        "is_unique": False,
        "classes": "item-text new-item",
        "text": "Newly Inserted Item",
        "visible": True,
        "attributes": {"class": "item-text new-item"},
    })
    live_elements[51]["text"] = "Item 50 Modified"

    result = comparer.match_and_diff_elements(baseline_elements, live_elements)

    # In the old comparer, bare tag matching would pair index 10 live with index 10 baseline,
    # causing 90 cascading modifications (90% false drift).
    # With the new multi-tier comparer (Pass 5a/5b text+classes matching),
    # all other 98 items match their exact corresponding element!
    accuracy = (result["matched_unchanged_count"] / len(baseline_elements)) * 100
    assert accuracy >= 95.0, f"Expected accuracy >= 95%, got {accuracy:.2f}%"
    assert result["matched_unchanged_count"] >= 98
    assert result["modified_count"] <= 2


def test_duplicate_id_fifo_ordering():
    """
    Verify duplicate IDs (e.g. id="email" across multiple order tabs)
    are matched in document order (FIFO) instead of overwriting a dictionary.
    """
    comparer = ElementComparer()

    baseline = [
        {"tag": "input", "id": "email", "locator": "#email", "is_unique": False, "attributes": {"name": "market_email", "id": "email"}},
        {"tag": "input", "id": "email", "locator": "#email", "is_unique": False, "attributes": {"name": "limit_email", "id": "email"}},
        {"tag": "input", "id": "email", "locator": "#email", "is_unique": False, "attributes": {"name": "stop_email", "id": "email"}},
    ]

    live = [
        {"tag": "input", "id": "email", "locator": "#email", "is_unique": False, "attributes": {"name": "market_email", "id": "email"}},
        {"tag": "input", "id": "email", "locator": "#email", "is_unique": False, "attributes": {"name": "limit_email", "id": "email"}},
        {"tag": "input", "id": "email", "locator": "#email", "is_unique": False, "attributes": {"name": "stop_email", "id": "email"}},
    ]

    result = comparer.match_and_diff_elements(baseline, live)
    assert result["matched_unchanged_count"] == 3
    assert result["modified_count"] == 0
    assert result["missing_count"] == 0
    assert result["added_count"] == 0


def test_table_cell_dynamic_data_normalization():
    """
    Verify non-action record data inside table cells (e.g. MAM account names,
    closed trade IDs) normalizes to [TABLE_DATA_CELL] without false drift.
    """
    comparer = ElementComparer()

    baseline = [
        {"tag": "table", "locator": "table", "is_unique": True, "classes": "datatable"},
        {"tag": "tr", "locator": "tr", "is_unique": False, "classes": "row-1"},
        {"tag": "td", "locator": "td", "is_unique": False, "text": "Master_Account_001", "classes": "user-cell"},
        {"tag": "td", "locator": "td", "is_unique": False, "text": "Edit", "classes": "btn-action"},
    ]

    live = [
        {"tag": "table", "locator": "table", "is_unique": True, "classes": "datatable"},
        {"tag": "tr", "locator": "tr", "is_unique": False, "classes": "row-1"},
        {"tag": "td", "locator": "td", "is_unique": False, "text": "Master_Account_999", "classes": "user-cell"},
        {"tag": "td", "locator": "td", "is_unique": False, "text": "Edit", "classes": "btn-action"},
    ]

    result = comparer.match_and_diff_elements(baseline, live)
    assert result["matched_unchanged_count"] == 4
    assert result["modified_count"] == 0
    assert result["missing_count"] == 0
    assert result["added_count"] == 0


def test_position_counter_normalization():
    """
    Verify position count strings ('Positions (5)' vs 'Positions (12)')
    and curPostionLength containers normalize without triggering drift.
    """
    comparer = ElementComparer()

    baseline = [
        {"tag": "span", "locator": "span.curPostionLength", "is_unique": True, "classes": "curPostionLength", "text": "Positions (5)"},
        {"tag": "div", "locator": "div.position-text", "is_unique": True, "classes": "position-text", "text": "Open Positions (2)"},
    ]

    live = [
        {"tag": "span", "locator": "span.curPostionLength", "is_unique": True, "classes": "curPostionLength", "text": "Positions (18)"},
        {"tag": "div", "locator": "div.position-text", "is_unique": True, "classes": "position-text", "text": "Open Positions (0)"},
    ]

    result = comparer.match_and_diff_elements(baseline, live)
    assert result["matched_unchanged_count"] == 2
    assert result["modified_count"] == 0


def test_transient_loader_and_skeleton_suppression():
    """
    Verify transient loading overlays, animsition spinners, and skeletons
    present in baseline but gone in live (or vice versa) do not report missing/added elements.
    """
    comparer = ElementComparer()

    baseline = [
        {"tag": "div", "locator": ".loader-overlay", "is_unique": True, "classes": "loader-overlay animsition-loading", "visible": True},
        {"tag": "div", "locator": ".dashboard-skeleton", "is_unique": True, "classes": "dashboard-skeleton", "visible": True},
        {"tag": "main", "locator": "main#app", "is_unique": True, "text": "Content", "visible": True},
    ]

    live = [
        {"tag": "main", "locator": "main#app", "is_unique": True, "text": "Content", "visible": True},
    ]

    result = comparer.match_and_diff_elements(baseline, live)
    assert result["matched_unchanged_count"] == 1
    assert result["missing_count"] == 0
    assert result["added_count"] == 0


def test_svg_and_chart_noise_suppression():
    """
    Verify SVG path coordinates, ApexCharts dynamic IDs, and chart points
    do not trigger false attribute diffs.
    """
    comparer = ElementComparer()

    baseline = [
        {
            "tag": "path",
            "locator": "path.apexcharts-line",
            "is_unique": True,
            "classes": "apexcharts-line",
            "attributes": {"d": "M 0 100 L 50 80 L 100 20", "points": "0,100 50,80 100,20", "stroke": "#1E90FF"}
        },
        {
            "tag": "text",
            "id": "SvgjsText1045",
            "locator": "#SvgjsText1045",
            "is_unique": True,
            "classes": "apexcharts-text",
            "text": "1.32559",
            "attributes": {"x": "100.5", "y": "20.2", "id": "SvgjsText1045"}
        }
    ]

    live = [
        {
            "tag": "path",
            "locator": "path.apexcharts-line",
            "is_unique": True,
            "classes": "apexcharts-line",
            "attributes": {"d": "M 0 102 L 50 79 L 100 18", "points": "0,102 50,79 100,18", "stroke": "#2E90FF"}
        },
        {
            "tag": "text",
            "id": "SvgjsText2090",
            "locator": "#SvgjsText2090",
            "is_unique": True,
            "classes": "apexcharts-text",
            "text": "1.32565",
            "attributes": {"x": "101.2", "y": "20.8", "id": "SvgjsText2090"}
        }
    ]

    result = comparer.match_and_diff_elements(baseline, live)
    assert result["matched_unchanged_count"] == 2
    assert result["modified_count"] == 0
    assert result["missing_count"] == 0


def test_comparer_baseline_snapshot_accuracy():
    """
    Test comparer on actual recorded baseline snapshot files to verify
    element match accuracy >= 95%.
    """
    comparer = ElementComparer()
    baseline_file = Path(__file__).resolve().parent.parent / "element_output" / "home_view_dashboard_sm_43cd3bc8.json"
    if not baseline_file.exists():
        baseline_file = Path("ui_regression/element_output/home_view_dashboard_sm_43cd3bc8.json")
    if not baseline_file.exists():
        pytest.skip(f"Baseline file {baseline_file} not found")

    with open(baseline_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    elements = data.get("elements", [])
    assert len(elements) > 100

    # Self-comparison should be 100% accurate
    res_self = comparer.match_and_diff_elements(elements, elements)
    self_acc = (res_self["matched_unchanged_count"] / len(elements)) * 100
    assert self_acc == 100.0

    # Simulation with 3% random live market fluctuations (prices, ticks, timestamps)
    live_sim = [dict(e) for e in elements]
    for idx in range(0, min(len(live_sim), 20)):
        if "text" in live_sim[idx] and live_sim[idx]["text"]:
            live_sim[idx]["text"] = live_sim[idx]["text"] + " 1.2543"

    res_sim = comparer.match_and_diff_elements(elements, live_sim)
    sim_acc = (res_sim["matched_unchanged_count"] / len(elements)) * 100
    assert sim_acc >= 95.0, f"Expected matching accuracy >= 95%, got {sim_acc:.2f}%"
