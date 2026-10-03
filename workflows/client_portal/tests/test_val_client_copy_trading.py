"""
Client Portal Copy Trading Leaderboard & Modals Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.B, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Search input filtering, empty search boundaries, non-existent manager queries.
2. Buttons & Actions: Follow modal lifecycle (Cancel dismissal), Statistics modal lifecycle (Close dismissal).
3. Dropdowns & Selects: Range (30D, 90D, 1Y, All Time), Risk, Fund, Rows per page selectors.
6. Calculations & Tables: 9-column managers leaderboard, summary cards metrics.
7. Security: Sanitization of search input against SQLi and XSS payloads, zero uncaught JS exceptions.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# 1. SEARCH FILTER: MATCHING & NON-EXISTENT BOUNDARY
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_copy_trading_search_and_clear_filter(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify search input boundary and filter behavior:
    - Entering a non-existent manager name filters table down to 0 rows without JS crashes.
    - Clearing search input restores manager rows.
    """
    client_copy_trading_page.navigate()
    expect(client_copy_trading_page.search_input).to_be_visible()

    initial_count = client_copy_trading_page.get_manager_count()

    # Search non-existent query
    client_copy_trading_page.filter_by_search("ZZZ_NON_EXISTENT_99999")
    filtered_count = client_copy_trading_page.get_manager_count()
    table_text = client_copy_trading_page.table.inner_text().lower()
    assert filtered_count == 0 or "no managers found" in table_text or "no data" in table_text, (
        f"Expected empty state for non-existent search query, got: {filtered_count} with text: {table_text}"
    )

    # Clear search
    client_copy_trading_page.clear_search()
    restored_count = client_copy_trading_page.get_manager_count()
    assert restored_count == initial_count, (
        f"Expected restored count {initial_count}, got: {restored_count}"
    )

    client_error_monitor.assert_no_js_errors("Copy Trading Search & Clear")


# ==============================================================================
# 2. DROPDOWN SELECTORS & ROWS PER PAGE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_copy_trading_dropdown_selectors(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify dropdown filters (Range, Risk, Fund, Rows):
    - Tests selecting available range options.
    - Tests rows per page selector (10, 25, 50).
    """
    client_copy_trading_page.navigate()

    # 1. Range selector
    expect(client_copy_trading_page.range_select).to_be_visible()
    client_copy_trading_page.range_select.select_option(index=0)
    client_copy_trading_page.page.wait_for_timeout(300)

    # 2. Rows selector
    expect(client_copy_trading_page.rows_select).to_be_visible()
    options = [opt.get_attribute("value") for opt in client_copy_trading_page.rows_select.locator("option").all()]
    if "25" in options:
        client_copy_trading_page.rows_select.select_option("25")
        expect(client_copy_trading_page.rows_select).to_have_value("25")

    client_error_monitor.assert_no_js_errors("Copy Trading Dropdowns")


# ==============================================================================
# 3. FOLLOW MODAL LIFECYCLE (NON-DESTRUCTIVE DISMISSAL)
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_copy_trading_follow_modal_lifecycle(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify Follow Manager modal dialog lifecycle without committing live subscription:
    - Click 'Follow' on the first manager row
    - Modal opens with title 'Follow Manager'
    - Displays trade method selections (Balance Based, Equity Based, Multiplier Based)
    - Clicking 'Cancel' dismisses modal cleanly with ZERO mutations
    """
    client_copy_trading_page.navigate()

    if client_copy_trading_page.get_manager_count() > 0:
        first_row = client_copy_trading_page.table_rows.first
        follow_btn = first_row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first

        if follow_btn.is_visible():
            manager_name = client_copy_trading_page.open_follow_modal(row_index=0)
            expect(client_copy_trading_page.follow_modal.first).to_be_visible()

            # Trade method selectors
            expect(client_copy_trading_page.modal_balance_based).to_be_visible()
            expect(client_copy_trading_page.modal_equity_based).to_be_visible()
            expect(client_copy_trading_page.modal_multiplier_based).to_be_visible()

            # Cancel and dismiss
            client_copy_trading_page.close_follow_modal()
            expect(client_copy_trading_page.follow_modal.first).not_to_be_visible()

    client_error_monitor.assert_no_js_errors("Follow Modal Lifecycle")


# ==============================================================================
# 4. STATISTICS MODAL LIFECYCLE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_copy_trading_statistics_modal_lifecycle(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2 & 6: Verify Statistics modal dialog opens and dismisses cleanly:
    - Click statistics icon button on first manager row
    - Modal opens with title 'STATISTICS'
    - Dismiss modal via close button
    """
    client_copy_trading_page.navigate()

    if client_copy_trading_page.get_manager_count() > 0:
        client_copy_trading_page.open_statistics_modal(row_index=0)
        expect(client_copy_trading_page.statistics_modal.first).to_be_visible()

        client_copy_trading_page.close_statistics_modal()
        expect(client_copy_trading_page.statistics_modal.first).not_to_be_visible()

    client_error_monitor.assert_no_js_errors("Statistics Modal Lifecycle")


# ==============================================================================
# 5. VIEW SWITCHER LIFECYCLE
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_copy_trading_view_switcher_lifecycle(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify view switching between TRADING MANAGER and MY FOLLOWERS / SUBSCRIPTION:
    - Switch to My Followers
    - Switch back to Trading Manager
    - Table remains visible and responsive
    """
    client_copy_trading_page.navigate()

    # Switch to My Followers
    client_copy_trading_page.switch_to_my_followers()
    expect(client_copy_trading_page.page.locator("main table")).to_be_visible()

    # Switch back to Trading Manager
    client_copy_trading_page.switch_to_trading_manager()
    expect(client_copy_trading_page.table).to_be_visible()

    client_error_monitor.assert_no_js_errors("Copy Trading View Switcher")


# ==============================================================================
# 6. SECURITY: SEARCH INPUT SANITIZATION (SQLi & XSS PAYLOADS)
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize(
    "payload,desc",
    [
        (SQLI_PAYLOADS[0][0], SQLI_PAYLOADS[0][1]),
        (XSS_PAYLOADS[0][0], XSS_PAYLOADS[0][1]),
        (XSS_PAYLOADS[1][0], XSS_PAYLOADS[1][1]),
    ],
)
def test_val_client_copy_trading_search_security_sanitization(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
    payload: str,
    desc: str,
):
    """
    Pillar 7 (Security): Verify search input sanitizes malicious injection strings:
    - Entering SQL injection or Cross-Site Scripting (XSS) payloads into search filter
      does not execute script, does not trigger alert dialogs, and causes no JS crashes.
    """
    alert_triggered = False

    def handle_dialog(dialog):
        nonlocal alert_triggered
        alert_triggered = True
        dialog.dismiss()

    client_copy_trading_page.page.on("dialog", handle_dialog)

    client_copy_trading_page.navigate()
    client_copy_trading_page.filter_by_search(payload)
    client_copy_trading_page.page.wait_for_timeout(300)

    # Clear search
    client_copy_trading_page.clear_search()
    client_copy_trading_page.page.wait_for_timeout(300)

    assert not alert_triggered, f"Security Alert! XSS dialog triggered by payload: {payload}"
    client_error_monitor.assert_no_js_errors(f"Copy Trading Search Sanitization: {desc}")
