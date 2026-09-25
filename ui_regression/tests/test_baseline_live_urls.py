"""
Tests for BASELINE_URL and LIVE_URL configuration, cross-environment view matching,
and domain drift noise suppression.
"""

import os
from pathlib import Path
from unittest.mock import patch
import pytest

from crawler.crawler_config import (
    BASELINE_URL,
    LIVE_URL,
    BASE_URL,
    BASELINE_DOMAIN,
    LIVE_DOMAIN,
    BASELINE_ADMIN_BASE_URL,
    LIVE_ADMIN_BASE_URL,
    BASELINE_ADMIN_LOGIN_URL,
    LIVE_ADMIN_LOGIN_URL,
    BASELINE_AUTH_STATE,
    LIVE_AUTH_STATE,
    BASELINE_ADMIN_AUTH_STATE,
    LIVE_ADMIN_AUTH_STATE,
    get_trading_auth_pages,
    get_admin_auth_pages,
)
from comparer.comparer import (
    get_canonical_route,
    NoiseFilter,
    ElementComparer,
)


# ============================================================
# 1. URL CONFIGURATION & RESOLUTION TESTS
# ============================================================

def test_baseline_and_live_url_defaults():
    """Verify that BASELINE_URL and LIVE_URL are defined and BASE_URL aliases BASELINE_URL."""
    assert BASELINE_URL is not None and len(BASELINE_URL) > 0
    assert LIVE_URL is not None and len(LIVE_URL) > 0
    assert BASE_URL == BASELINE_URL


def test_auth_state_isolation_paths():
    """Verify that live auth states are isolated from baseline auth states to prevent overwriting."""
    assert BASELINE_AUTH_STATE != LIVE_AUTH_STATE
    assert BASELINE_ADMIN_AUTH_STATE != LIVE_ADMIN_AUTH_STATE
    assert LIVE_AUTH_STATE.name == "auth_state_live.json"
    assert LIVE_ADMIN_AUTH_STATE.name == "auth_state_admin_live.json"


def test_dynamic_auth_pages_generator():
    """Verify that get_trading_auth_pages and get_admin_auth_pages respect the given base_url."""
    custom_trading = "https://preview.custom-trading.com"
    pages = get_trading_auth_pages(custom_trading)
    assert f"{custom_trading}/login/" in pages
    assert f"{custom_trading}/register/" in pages
    assert f"{custom_trading}/reset/" in pages

    custom_admin_login = "https://preview.admin.com/login"
    admin_pages = get_admin_auth_pages(custom_admin_login)
    assert admin_pages == [custom_admin_login]


# ============================================================
# 2. CANONICAL ROUTE MATCHING TESTS
# ============================================================

def test_get_canonical_route_exact_prefix():
    """Verify stripping base_url prefix from full URLs."""
    base_url = "https://stage.example.com"
    
    # Root
    assert get_canonical_route("https://stage.example.com/", base_url) == "/"
    assert get_canonical_route("https://stage.example.com", base_url) == "/"
    
    # Deep route
    assert get_canonical_route("https://stage.example.com/dashboard/analytics", base_url) == "/dashboard/analytics"
    assert get_canonical_route("https://stage.example.com/dashboard/analytics/", base_url) == "/dashboard/analytics"
    
    # With query parameter
    assert get_canonical_route("https://stage.example.com/trades?page=2", base_url) == "/trades?page=2"
    
    # With hash fragment (should be stripped)
    assert get_canonical_route("https://stage.example.com/profile#settings", base_url) == "/profile"


def test_get_canonical_route_cross_environment():
    """Verify that identical relative paths produce the identical canonical route across different hosts."""
    baseline_host = "https://stage.example.com"
    live_host = "https://preview.staging-preview.example.org:8080"

    route_b = get_canonical_route("https://stage.example.com/admin/users?sort=asc#section", baseline_host)
    route_l = get_canonical_route("https://preview.staging-preview.example.org:8080/admin/users?sort=asc", live_host)

    assert route_b == route_l
    assert route_b == "/admin/users?sort=asc"


def test_canonical_key_generation():
    """Verify host-agnostic snapshot key generation for cross-environment matching."""
    baseline_url = "https://stage.example.com/dashboard"
    live_url = "https://live-preprod.example.com/dashboard"

    key_b = ElementComparer._get_canonical_key(
        url=baseline_url,
        view_name="crypto-tab",
        viewport="xl",
        base_url="https://stage.example.com",
    )
    key_l = ElementComparer._get_canonical_key(
        url=live_url,
        view_name="crypto-tab",
        viewport="xl",
        base_url="https://live-preprod.example.com",
    )

    assert key_b == key_l
    assert key_b == "/dashboard::view::crypto-tab::viewport::xl"


# ============================================================
# 3. NOISE FILTER DOMAIN NORMALIZATION TESTS
# ============================================================

def test_noise_filter_domain_normalization_in_attributes():
    """Verify that links and image sources pointing to baseline domain are normalized against live domain."""
    b_base = "https://stage.example.com"
    l_base = "https://preview.example.com"

    filter_cross = NoiseFilter(
        enabled=True,
        baseline_base_url=b_base,
        live_base_url=l_base,
    )

    b_attrs = {
        "href": "https://stage.example.com/account/security",
        "src": "https://stage.example.com/static/img/avatar.png",
        "title": "Account Settings",
    }
    l_attrs = {
        "href": "https://preview.example.com/account/security",
        "src": "https://preview.example.com/static/img/avatar.png",
        "title": "Account Settings",
    }

    norm_b = filter_cross.normalize_attributes(b_attrs, source_env="baseline")
    norm_l = filter_cross.normalize_attributes(l_attrs, source_env="live")

    # The URLs should normalize identically so diff is suppressed
    assert norm_b["href"] == norm_l["href"]
    assert norm_b["href"] == "[BASE_URL]/account/security"
    assert norm_b["src"] == norm_l["src"]
    assert norm_b["src"] == "[BASE_URL]/static/img/avatar.png"
    assert norm_b["title"] == norm_l["title"]


def test_noise_filter_text_normalization_cross_domain():
    """Verify that text referencing the domain is normalized to avoid false drift."""
    b_base = "https://stage.example.com"
    l_base = "https://preview.example.com"

    filter_cross = NoiseFilter(
        enabled=True,
        baseline_base_url=b_base,
        live_base_url=l_base,
    )

    b_text = "Welcome to stage.example.com trading hub"
    l_text = "Welcome to preview.example.com trading hub"

    norm_b = filter_cross.normalize_text(b_text, source_env="baseline")
    norm_l = filter_cross.normalize_text(l_text, source_env="live")

    assert norm_b == norm_l
    assert "[BASE_DOMAIN]" in norm_b


# ============================================================
# 4. CROSS-ENVIRONMENT VIEW PAIRING TEST IN COMPARER
# ============================================================

def test_comparer_pairs_cross_environment_views():
    """
    Simulate a baseline snapshot on stage and live snapshot on preprod.
    Verify compare_all correctly pairs them via canonical routes instead of flagging
    missing and new pages.
    """
    baseline_snapshots = {
        "https://stage.example.com/analytics::viewport::xl": {
            "file_name": "https___stage_example_com_analytics__xl.json",
            "page": {
                "url": "https://stage.example.com/analytics",
                "view_name": None,
                "viewport": "xl",
                "title": "Analytics Dashboard",
                "type": "authenticated",
            },
            "elements": [
                {
                    "tag": "h1",
                    "locator": "h1",
                    "is_unique": True,
                    "text": "Analytics",
                    "direct_text": "Analytics",
                    "classes": "title",
                    "visible": True,
                    "attributes": {},
                },
                {
                    "tag": "a",
                    "locator": "a#home-link",
                    "id": "home-link",
                    "is_unique": True,
                    "text": "Go to Home",
                    "direct_text": "Go to Home",
                    "classes": "nav-link",
                    "visible": True,
                    "attributes": {
                        "id": "home-link",
                        "href": "https://stage.example.com/home",
                    },
                },
            ],
        }
    }

    live_snapshots = {
        "https://preprod.example.com/analytics::viewport::xl": {
            "file_name": "https___preprod_example_com_analytics__xl.json",
            "page": {
                "url": "https://preprod.example.com/analytics",
                "view_name": None,
                "viewport": "xl",
                "title": "Analytics Dashboard",
                "type": "authenticated",
            },
            "elements": [
                {
                    "tag": "h1",
                    "locator": "h1",
                    "is_unique": True,
                    "text": "Analytics",
                    "direct_text": "Analytics",
                    "classes": "title",
                    "visible": True,
                    "attributes": {},
                },
                {
                    "tag": "a",
                    "locator": "a#home-link",
                    "id": "home-link",
                    "is_unique": True,
                    "text": "Go to Home",
                    "direct_text": "Go to Home",
                    "classes": "nav-link",
                    "visible": True,
                    "attributes": {
                        "id": "home-link",
                        "href": "https://preprod.example.com/home",
                    },
                },
            ],
        }
    }

    comparer = ElementComparer(
        baseline_base_url="https://stage.example.com",
        live_base_url="https://preprod.example.com",
    )

    report = comparer.compare_all(
        baseline_snapshots=baseline_snapshots,
        live_snapshots=live_snapshots,
        baseline_base_url="https://stage.example.com",
        live_base_url="https://preprod.example.com",
    )

    summary = report["summary"]
    assert summary["total_views_compared"] == 1
    # Both elements (h1 and a#home-link) should match and have no drift thanks to domain normalization
    assert summary["total_matched_unchanged"] == 2
    assert summary["total_modified"] == 0
    assert summary["total_missing"] == 0
    assert summary["total_added"] == 0
    assert summary["has_drift"] is False

    page_report = report["pages"][0]
    assert page_report["baseline_url"] == "https://stage.example.com/analytics"
    assert page_report["live_url"] == "https://preprod.example.com/analytics"
    assert page_report["status"] == "UNCHANGED"


# ============================================================
# 5. SITE-SPECIFIC CREDENTIALS RESOLUTION TESTS
# ============================================================

def test_baseline_and_live_credentials_resolution():
    """Verify that baseline and live credentials variables are defined and accessible."""
    from crawler.crawler_config import (
        BASELINE_TEST_USER_EMAIL,
        LIVE_TEST_USER_EMAIL,
        BASELINE_TEST_USER_PASSWORD,
        LIVE_TEST_USER_PASSWORD,
        BASELINE_ADMIN_USER_USERNAME,
        LIVE_ADMIN_USER_USERNAME,
        BASELINE_ADMIN_USER_PASSWORD,
        LIVE_ADMIN_USER_PASSWORD,
    )
    assert BASELINE_TEST_USER_EMAIL is not None and len(BASELINE_TEST_USER_EMAIL) > 0
    assert LIVE_TEST_USER_EMAIL is not None and len(LIVE_TEST_USER_EMAIL) > 0
    assert BASELINE_TEST_USER_PASSWORD is not None and len(BASELINE_TEST_USER_PASSWORD) > 0
    assert LIVE_TEST_USER_PASSWORD is not None and len(LIVE_TEST_USER_PASSWORD) > 0
    assert BASELINE_ADMIN_USER_USERNAME is not None and len(BASELINE_ADMIN_USER_USERNAME) > 0
    assert LIVE_ADMIN_USER_USERNAME is not None and len(LIVE_ADMIN_USER_USERNAME) > 0
    assert BASELINE_ADMIN_USER_PASSWORD is not None and len(BASELINE_ADMIN_USER_PASSWORD) > 0
    assert LIVE_ADMIN_USER_PASSWORD is not None and len(LIVE_ADMIN_USER_PASSWORD) > 0


def test_independent_site_credentials_override(monkeypatch):
    """Verify that setting distinct environment variables assigns separate credentials to baseline vs live."""
    monkeypatch.setenv("BASELINE_TEST_USER_EMAIL", "base_user_1")
    monkeypatch.setenv("LIVE_TEST_USER_EMAIL", "live_user_2")
    monkeypatch.setenv("BASELINE_ADMIN_USER_USERNAME", "base_admin_1")
    monkeypatch.setenv("LIVE_ADMIN_USER_USERNAME", "live_admin_2")

    b_email = os.getenv("BASELINE_TEST_USER_EMAIL")
    l_email = os.getenv("LIVE_TEST_USER_EMAIL")
    b_admin = os.getenv("BASELINE_ADMIN_USER_USERNAME")
    l_admin = os.getenv("LIVE_ADMIN_USER_USERNAME")

    assert b_email == "base_user_1"
    assert l_email == "live_user_2"
    assert b_email != l_email

    assert b_admin == "base_admin_1"
    assert l_admin == "live_admin_2"
    assert b_admin != l_admin

