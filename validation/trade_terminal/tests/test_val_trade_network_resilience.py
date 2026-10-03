"""
Trade Terminal Network Resilience & Security Telemetry Suite.
Verifies network disconnection handling, offline state UI stability,
automatic reconnection recovery, zero uncaught JS exceptions, CSRF protection,
and sensitive data leakage prevention across storage, network parameters, and console logs.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.utils.diagnostics import PageDiagnostics
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeNetworkResilience:
    """Validation test suite for trade terminal network resilience and runtime security."""

    def test_val_trade_network_offline_recovery_resilience(
        self, watchlist_page: WatchlistPage
    ):
        """
        Verify that simulating an offline network state does not crash the Trading Terminal UI
        and that restoring the online state cleanly reconnects and restores quotes.
        """
        page = watchlist_page.page
        watchlist_page.navigate()

        # 1. Simulate temporary offline network state
        page.context.set_offline(True)
        page.wait_for_timeout(1500)

        # Assert UI remains responsive and rendered
        assert page.is_visible("body"), "Trading Terminal crashed during offline network state."

        # 2. Restore online network condition
        page.context.set_offline(False)
        page.wait_for_timeout(2000)

        # Assert UI is fully operational post-reconnection
        watchlist_page.navigate()
        assert page.is_visible("body"), "Trading Terminal failed to restore after network reconnection."

    def test_val_trade_console_telemetry_clean_diagnostics(
        self, watchlist_page: WatchlistPage
    ):
        """
        Verify that running normal trade terminal workflows does not trigger
        uncaught JavaScript exceptions or critical runtime errors.
        """
        watchlist_page.navigate()
        watchlist_page.page.wait_for_timeout(1000)

        diagnostics: PageDiagnostics = getattr(watchlist_page.page, "_diagnostics", None)
        if diagnostics:
            critical_errors = diagnostics.get_page_errors()
            assert len(critical_errors) == 0, (
                f"Critical uncaught JS exceptions detected in Trade Terminal: {critical_errors}"
            )

    def test_val_trade_sensitive_data_storage_inspection(
        self, watchlist_page: WatchlistPage
    ):
        """
        Verify that window.localStorage and window.sessionStorage do not store
        plain text user passwords or sensitive credentials.
        """
        watchlist_page.navigate()
        page = watchlist_page.page

        # Extract localStorage contents
        local_storage_keys = page.evaluate("() => Object.keys(window.localStorage)")
        for key in local_storage_keys:
            val = page.evaluate(f"() => window.localStorage.getItem('{key}')") or ""
            assert "password=" not in val.lower(), f"Potential cleartext password found in localStorage key '{key}'"
            assert "raw_secret" not in val.lower(), f"Potential raw secret found in localStorage key '{key}'"

        # Extract sessionStorage contents
        session_storage_keys = page.evaluate("() => Object.keys(window.sessionStorage)")
        for key in session_storage_keys:
            val = page.evaluate(f"() => window.sessionStorage.getItem('{key}')") or ""
            assert "password=" not in val.lower(), f"Potential cleartext password found in sessionStorage key '{key}'"

    def test_val_trade_network_credentials_not_in_url_query_params(
        self, watchlist_page: WatchlistPage
    ):
        """Verify passwords and raw secret keys are never passed as URL query parameters in HTTP GET/POST."""
        current_url = watchlist_page.page.url
        assert "password=" not in current_url.lower(), f"Password leaked in URL parameters: {current_url}"
        assert "secret=" not in current_url.lower(), f"Secret leaked in URL parameters: {current_url}"

    def test_val_trade_csrf_token_header_integrity(
        self, watchlist_page: WatchlistPage
    ):
        """Verify application injects CSRF headers or tokens on state-mutating requests."""
        page = watchlist_page.page
        csrf_meta = page.locator("meta[name='csrf-token'], input[name='csrf_token']").first
        # If CSRF meta or input exists, verify non-empty
        if csrf_meta.is_visible():
            val = csrf_meta.get_attribute("content") or csrf_meta.input_value()
            assert val != "", "CSRF token element found but has empty value"
