"""
Unit and Integration Tests for 5-Viewport Regression Testing.
Verifies centralized viewport configuration, filename generation, snapshot keys,
comparer viewport segregation (baseline(vp) <-> live(vp)), and report generation.
"""

import json
from pathlib import Path
import pytest

from crawler.crawler_config import (
    DEFAULT_VIEWPORT,
    DEFAULT_VIEWPORT_HEIGHT,
    VIEWPORT_NAMES,
    VIEWPORT_ORDER,
    VIEWPORTS,
    get_viewport_config,
    parse_viewports,
)
from crawler.crawler import (
    Crawler,
    extract_viewport_from_filename,
    filename_from_url,
)
from comparer.comparer import ElementComparer, NoiseFilter


# ============================================================
# 1. CENTRALIZED VIEWPORT CONFIGURATION TESTS
# ============================================================

def test_viewport_definitions():
    """Verify all 5 required viewports exist with exact required widths."""
    expected_widths = {
        "sm": 640,
        "md": 768,
        "lg": 1024,
        "xl": 1280,
        "2xl": 1536,
    }

    for vp_name, expected_width in expected_widths.items():
        assert vp_name in VIEWPORTS, f"Viewport '{vp_name}' must be defined in VIEWPORTS"
        assert VIEWPORTS[vp_name]["width"] == expected_width, (
            f"Viewport '{vp_name}' width should be {expected_width}px, got {VIEWPORTS[vp_name]['width']}px"
        )
        assert VIEWPORTS[vp_name]["height"] == DEFAULT_VIEWPORT_HEIGHT

    assert set(VIEWPORT_NAMES) == set(expected_widths.keys())
    assert VIEWPORT_ORDER == ["sm", "md", "lg", "xl", "2xl"]


def test_get_viewport_config():
    """Verify get_viewport_config retrieves valid configs and handles case/whitespace."""
    assert get_viewport_config("SM") == {"width": 640, "height": DEFAULT_VIEWPORT_HEIGHT}
    assert get_viewport_config("  md ") == {"width": 768, "height": DEFAULT_VIEWPORT_HEIGHT}
    assert get_viewport_config("lg") == {"width": 1024, "height": DEFAULT_VIEWPORT_HEIGHT}
    assert get_viewport_config("xl") == {"width": 1280, "height": DEFAULT_VIEWPORT_HEIGHT}
    assert get_viewport_config("2XL") == {"width": 1536, "height": DEFAULT_VIEWPORT_HEIGHT}

    with pytest.raises(ValueError, match="Unknown viewport"):
        get_viewport_config("4k_ultra_wide")


def test_parse_viewports():
    """Verify parse_viewports parses strings, lists, defaults, and validates."""
    # Default gives all 5 in order
    assert parse_viewports(None) == ["sm", "md", "lg", "xl", "2xl"]
    assert parse_viewports("") == ["sm", "md", "lg", "xl", "2xl"]

    # Comma-separated string
    assert parse_viewports("sm,lg,2xl") == ["sm", "lg", "2xl"]
    assert parse_viewports(" MD , XL ") == ["md", "xl"]

    # List of strings
    assert parse_viewports(["sm", "md"]) == ["sm", "md"]

    # Invalid viewport raises error
    with pytest.raises(ValueError, match="Invalid viewport"):
        parse_viewports("sm,invalid_vp")


# ============================================================
# 2. VIEWPORT-AWARE FILENAME GENERATION & EXTRACTION
# ============================================================

def test_filename_from_url_with_viewports():
    """Verify filenames include viewport identifiers and never collide across viewports."""
    url = "https://stage.xtremenext.com/login"
    
    filenames = {}
    for vp in VIEWPORT_NAMES:
        fname = filename_from_url(url, viewport=vp)
        assert vp in fname, f"Filename '{fname}' must contain viewport identifier '{vp}'"
        assert fname.endswith(".json")
        filenames[vp] = fname

    # All 5 filenames for the same URL must be unique (cannot overwrite each other)
    assert len(set(filenames.values())) == 5


def test_filename_from_url_with_in_dom_views():
    """Verify filenames for in-DOM views include view name and viewport."""
    url = "https://stage.xtremenext.com/client-portal"
    fname_sm = filename_from_url(url, view_suffix="deposit", viewport="sm")
    fname_2xl = filename_from_url(url, view_suffix="deposit", viewport="2xl")

    assert "deposit" in fname_sm
    assert "sm" in fname_sm
    assert "2xl" in fname_2xl
    assert fname_sm != fname_2xl


def test_extract_viewport_from_filename():
    """Verify extract_viewport_from_filename parses the viewport name."""
    assert extract_viewport_from_filename("login_sm_947a741f.json") == "sm"
    assert extract_viewport_from_filename("client-portal_view_deposit_md_4b6c391b.json") == "md"
    assert extract_viewport_from_filename("admin_Controlbase_Dashboard_2xl_d8e21760.json") == "2xl"
    assert extract_viewport_from_filename("legacy_unversioned_file_d8e21760.json") is None


# ============================================================
# 3. STRICT VIEWPORT-SPECIFIC COMPARISON KEYS
# ============================================================

def test_snapshot_key_generation():
    """Verify snapshot keys isolate viewports so viewports are never cross-compared."""
    url = "https://stage.xtremenext.com/dashboard"

    key_sm = ElementComparer._get_snapshot_key(url, view_name=None, viewport="sm")
    key_md = ElementComparer._get_snapshot_key(url, view_name=None, viewport="md")
    key_lg = ElementComparer._get_snapshot_key(url, view_name=None, viewport="lg")
    key_xl = ElementComparer._get_snapshot_key(url, view_name=None, viewport="xl")
    key_2xl = ElementComparer._get_snapshot_key(url, view_name=None, viewport="2xl")

    # All keys must be unique and contain their viewport
    keys = [key_sm, key_md, key_lg, key_xl, key_2xl]
    assert len(set(keys)) == 5
    for vp, key in zip(VIEWPORT_NAMES, keys):
        assert f"viewport::{vp}" in key


def test_comparer_segregates_viewports(tmp_path):
    """
    Verify ElementComparer compares baseline(vp) <-> live(vp) strictly
    and never compares baseline(sm) with live(md) or live(xl).
    """
    comparer = ElementComparer(baseline_dir=tmp_path)

    # Mock baseline snapshots for sm and xl
    baseline_snapshots = {
        "https://stage.xtremenext.com/dashboard::viewport::sm": {
            "file_name": "dashboard_sm_11111111.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "sm"},
            "elements": [
                {"locator": "#mobile-header", "tag": "div", "is_unique": True, "text": "Mobile Header", "visible": True}
            ],
            "statistics": {"element_count": 1},
        },
        "https://stage.xtremenext.com/dashboard::viewport::xl": {
            "file_name": "dashboard_xl_22222222.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "xl"},
            "elements": [
                {"locator": "#desktop-sidebar", "tag": "nav", "is_unique": True, "text": "Desktop Sidebar", "visible": True}
            ],
            "statistics": {"element_count": 1},
        },
    }

    # Mock live snapshots matching same viewports
    live_snapshots = {
        "https://stage.xtremenext.com/dashboard::viewport::sm": {
            "file_name": "dashboard_sm_11111111.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "sm"},
            "elements": [
                {"locator": "#mobile-header", "tag": "div", "is_unique": True, "text": "Mobile Header", "visible": True}
            ],
            "statistics": {"element_count": 1},
        },
        "https://stage.xtremenext.com/dashboard::viewport::xl": {
            "file_name": "dashboard_xl_22222222.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "xl"},
            "elements": [
                {"locator": "#desktop-sidebar", "tag": "nav", "is_unique": True, "text": "Desktop Sidebar", "visible": True}
            ],
            "statistics": {"element_count": 1},
        },
    }

    report = comparer.compare_all(baseline_snapshots, live_snapshots)

    # 2 views compared (one sm, one xl)
    assert report["summary"]["total_views_compared"] == 2
    assert report["summary"]["has_drift"] is False
    assert report["summary"]["total_matched_unchanged"] == 2
    assert report["summary"]["total_modified"] == 0
    assert report["summary"]["total_missing"] == 0

    # Per-viewport summary breakdown
    by_vp = report["summary"]["by_viewport"]
    assert by_vp["sm"]["views_compared"] == 1
    assert by_vp["sm"]["matched_unchanged"] == 1
    assert by_vp["sm"]["has_drift"] is False

    assert by_vp["xl"]["views_compared"] == 1
    assert by_vp["xl"]["matched_unchanged"] == 1
    assert by_vp["xl"]["has_drift"] is False


def test_comparer_detects_viewport_specific_drift(tmp_path):
    """Verify drift in one viewport (e.g. sm) is detected without corrupting other viewports."""
    comparer = ElementComparer(baseline_dir=tmp_path)

    baseline_snapshots = {
        "https://stage.xtremenext.com/dashboard::viewport::sm": {
            "file_name": "dashboard_sm_111.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "sm"},
            "elements": [
                {"locator": "#btn-menu", "tag": "button", "is_unique": True, "text": "Menu", "visible": True}
            ],
        },
        "https://stage.xtremenext.com/dashboard::viewport::2xl": {
            "file_name": "dashboard_2xl_222.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "2xl"},
            "elements": [
                {"locator": "#nav-bar", "tag": "nav", "is_unique": True, "text": "Full Navigation", "visible": True}
            ],
        },
    }

    # Live snapshot has modified text in sm, but 2xl is unchanged
    live_snapshots = {
        "https://stage.xtremenext.com/dashboard::viewport::sm": {
            "file_name": "dashboard_sm_111.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "sm"},
            "elements": [
                {"locator": "#btn-menu", "tag": "button", "is_unique": True, "text": "Open Menu", "visible": True}
            ],
        },
        "https://stage.xtremenext.com/dashboard::viewport::2xl": {
            "file_name": "dashboard_2xl_222.json",
            "page": {"url": "https://stage.xtremenext.com/dashboard", "viewport": "2xl"},
            "elements": [
                {"locator": "#nav-bar", "tag": "nav", "is_unique": True, "text": "Full Navigation", "visible": True}
            ],
        },
    }

    report = comparer.compare_all(baseline_snapshots, live_snapshots)

    assert report["summary"]["has_drift"] is True
    assert report["summary"]["total_modified"] == 1
    assert report["summary"]["total_matched_unchanged"] == 1

    by_vp = report["summary"]["by_viewport"]
    assert by_vp["sm"]["has_drift"] is True
    assert by_vp["sm"]["modified"] == 1

    assert by_vp["2xl"]["has_drift"] is False
    assert by_vp["2xl"]["matched_unchanged"] == 1


def test_load_baseline_snapshots_with_viewports(tmp_path):
    """Verify load_baseline_snapshots correctly loads files from disk with viewport keys."""
    # Write sample snapshot JSON files to tmp_path
    for vp in ["sm", "md", "lg"]:
        sample_record = {
            "page": {
                "url": "https://stage.xtremenext.com/sample",
                "viewport": vp,
                "title": f"Sample Page {vp}",
                "type": "root_page"
            },
            "statistics": {"element_count": 2},
            "elements": [
                {"locator": f"#el-{vp}", "tag": "div", "is_unique": True, "text": f"Element {vp}", "visible": True}
            ]
        }
        fname = filename_from_url("https://stage.xtremenext.com/sample", viewport=vp)
        with open(tmp_path / fname, "w", encoding="utf-8") as f:
            json.dump(sample_record, f)

    comparer = ElementComparer(baseline_dir=tmp_path)
    loaded = comparer.load_baseline_snapshots()

    assert len(loaded) == 3
    for vp in ["sm", "md", "lg"]:
        expected_key = f"https://stage.xtremenext.com/sample::viewport::{vp}"
        assert expected_key in loaded
        assert loaded[expected_key]["page"]["viewport"] == vp


# ============================================================
# 4. ENHANCED NUMBER & TRADE NORMALIZATION TESTS
# ============================================================

def test_noise_filter_number_and_trade_normalization():
    """Verify numbers, formatted commas, percentages, floats, and trade IDs normalize properly."""
    nf = NoiseFilter(enabled=True)

    # Formatted thousands numbers (e.g. 2,904 vs 2,910)
    assert nf.normalize_text("2,904") == "[NUMBER]"
    assert nf.normalize_text("2,910") == "[NUMBER]"
    assert nf.normalize_text("1,234,567.89") == "[NUMBER]"

    # Percentages (1-digit decimal, 2-digit decimal, integer, negative)
    assert nf.normalize_text("18.7%") == "[PERCENT]"
    assert nf.normalize_text("19.69%") == "[PERCENT]"
    assert nf.normalize_text("+4.96%") == "[PERCENT]"
    assert nf.normalize_text("-0.5%") == "[PERCENT]"
    assert nf.normalize_text("100%") == "[PERCENT]"

    # Floats and decimals
    assert nf.normalize_text("0.08") == "[FLOAT]"
    assert nf.normalize_text("3097.10") == "[FLOAT]"
    assert nf.normalize_text("-100.84") == "[FLOAT]"

    # Standalone integers (e.g. 123 vs 127)
    assert nf.normalize_text("123") == "[INT]"
    assert nf.normalize_text("127") == "[INT]"

    # Prices & Currencies
    assert nf.normalize_text("$ 1.13823") == "[PRICE]"
    assert nf.normalize_text("€12.50") == "[PRICE]"
    assert nf.normalize_text("50.5 USDT") == "[PRICE]"

    # Dynamic metrics & margin levels
    assert nf.normalize_text("Balance: 13,500.00") == "[METRIC]"
    assert nf.normalize_text("Margin Level: 11253.94%") == "[METRIC]"
    assert nf.normalize_text("Total PNL: -100.84") == "[METRIC]"

    # Dynamic user hash classes
    classes_baseline = nf.normalize_classes("user_margin_level_BVT8QQ2W7C green font-bold")
    classes_live = nf.normalize_classes("user_margin_level_W7M0B23CVE green font-bold")
    assert classes_baseline == classes_live
    assert "user-dynamic-hash-class" in classes_baseline
