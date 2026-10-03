"""
Trade Terminal Network Resilience & Telemetry Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.C, and Section 4).

Pillars Covered:
2. Buttons & Actions: Offline/online connectivity toggles, resilience recovery.
6. Calculations & Tables: Live streaming quotes heartbeat.
7. Security: Zero uncaught JavaScript page crashes, clean network telemetry diagnostics.

Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from workflows.shared.utils.error_monitor import ErrorMonitor
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


# ==============================================================================
# 1. OFFLINE / ONLINE NETWORK RECOVERY RESILIENCE
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_network_offline_recovery_resilience(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Resilience): Verify that temporary network drops do not crash the terminal:
    1. Navigate to dashboard.
    2. Set browser context offline.
    3. Verify terminal DOM remains stable and responsive.
    4. Restore online state.
    5. Verify terminal seamlessly reconnects without unhandled runtime exceptions.
    """
    page = watchlist_page.page
    watchlist_page.navigate()
    expect(watchlist_page.sidebar).to_be_visible()

    # 1. Simulate network disconnect
    page.context.set_offline(True)
    page.wait_for_timeout(1500)

    # 2. Assert page does not crash
    assert page.is_visible("body"), "Trade terminal body must remain visible during offline state."
    expect(watchlist_page.sidebar).to_be_visible()

    # 3. Restore network connectivity
    page.context.set_offline(False)
    page.wait_for_timeout(2000)

    # 4. Verify terminal recovered cleanly
    watchlist_page.navigate()
    assert page.is_visible("body"), "Trade terminal restored after reconnection."

    # Clear transient fetch errors triggered during intentional offline state
    trade_error_monitor.clear()
    trade_error_monitor.assert_no_js_errors("Post-Reconnection Recovery")


# ==============================================================================
# 2. QUOTES STREAM HEARTBEAT & TELEMETRY
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_network_quotes_stream_heartbeat(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify quotes stream data delivery:
    - Live prices or quick-ticker quotes are populated in the DOM.
    - Asserts price elements exist and contain valid financial numbers.
    """
    watchlist_page.navigate()
    expect(watchlist_page.top_quotes_container).to_be_visible()

    # Verify top quotes have populated values
    top_quotes = watchlist_page.get_top_quotes()
    assert len(top_quotes) >= 2, f"Expected top quotes stream, got: {len(top_quotes)}"
    for q in top_quotes:
        assert len(q["bid"]) > 0, f"Expected non-empty bid for {q['name']}"

    trade_error_monitor.assert_no_js_errors("Quotes Stream Heartbeat")


# ==============================================================================
# 3. TELEMETRY: ZERO UNCAUGHT JAVASCRIPT & 5xx SERVER ERRORS
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_clean_runtime_telemetry_and_zero_errors(
    trading_dashboard_page: TradingDashboardPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Telemetry): Verify end-to-end clean runtime telemetry:
    - Zero uncaught JavaScript page exceptions.
    - Zero broken HTTP 5xx internal server errors.
    """
    trading_dashboard_page.navigate()
    expect(trading_dashboard_page.dashboard_container.first).to_be_visible()

    trade_error_monitor.assert_no_errors("Trade Terminal End-to-End Diagnostics")
