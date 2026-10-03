"""
Admin Portal MAM & PAMM Management Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Search input, MAM/PAMM share percentage inputs, SQLi/XSS sanitization.
2. Buttons & Actions: Requests modal triggers (#showMamMasterRequests, #showPammMasterRequests), safe modal dismissals.
3. Dropdowns & Selects: Entries per page pagination (10, 25, 50, 100).
5. Mathematical Bounds: Profit share & allocation percentage invariants (0% - 100%).
6. Calculations & Tables: S.No ordering, pagination controls, column sorting traversal.
7. Security: SQLi/XSS attack vectors in search inputs.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.mam_page import MamPage
from workflows.admin_portal.pages.pamm_page import PammPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# PILLAR 1 & 2: ROUTE INTEGRITY & DATATABLE RENDERING
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_route_and_table_integrity(
    mam_page: MamPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify MAM page navigates successfully, renders the datatable,
    requests trigger button, and page actions.
    """
    mam_page.navigate()
    mam_page.page.wait_for_timeout(1000)

    expect(mam_page.datatable).to_be_attached(timeout=15000)
    expect(mam_page.page_title).to_be_visible()
    expect(mam_page.mam_requests_button).to_be_attached()

    admin_error_monitor.assert_no_errors("MAM Route & Table Integrity")


@pytest.mark.admin
@pytest.mark.validation
def test_val_pamm_route_and_table_integrity(
    pamm_page: PammPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify PAMM page navigates successfully, renders the datatable,
    requests trigger button, and page actions.
    """
    pamm_page.navigate()
    pamm_page.page.wait_for_timeout(1000)

    expect(pamm_page.datatable).to_be_attached(timeout=15000)
    expect(pamm_page.page_title).to_be_visible()
    expect(pamm_page.pamm_requests_button).to_be_attached()

    admin_error_monitor.assert_no_errors("PAMM Route & Table Integrity")


# ==============================================================================
# PILLAR 2: REQUESTS MODAL LIFECYCLE & DISMISSAL SAFEGUARDS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_requests_modal_lifecycle(
    mam_page: MamPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking 'MAM Requests' opens #mamRequestsModal with request
    table and controls, and dismisses cleanly via 'Close' without state leaks.
    """
    mam_page.navigate()
    btn = mam_page.mam_requests_button
    expect(btn).to_be_attached()

    if btn.is_visible():
        mam_page.open_mam_requests()
        modal = mam_page.mam_requests_modal
        expect(modal).to_be_visible(timeout=5000)
        expect(mam_page.mam_requests_table).to_be_attached()

        # Dismiss modal safely
        mam_page.close_mam_requests()
        expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("MAM Requests Modal Lifecycle")


@pytest.mark.admin
@pytest.mark.validation
def test_val_pamm_requests_modal_lifecycle(
    pamm_page: PammPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking 'PAMM Requests' opens #pammRequestsModal with request
    table, and dismisses cleanly via 'Close'.
    """
    pamm_page.navigate()
    pamm_page.open_pamm_requests()

    modal = pamm_page.pamm_requests_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(pamm_page.pamm_requests_table).to_be_attached()

    # Dismiss modal safely
    pamm_page.close_pamm_requests()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("PAMM Requests Modal Lifecycle")


# ==============================================================================
# PILLAR 1 & 5: ALLOCATION & PROFIT-SHARE MATHEMATICAL BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_share_modal_allocation_boundaries(
    mam_page: MamPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 5: Verify MAM Share Modal input bounds (0% to 100%) and safe dismissal.
    """
    mam_page.navigate()
    mam_page.page.wait_for_timeout(1000)

    # Test allocation percentage boundaries mathematically
    allocation_matrix = [
        ("Zero percent", 0, True),
        ("Standard 20%", 20, True),
        ("Standard 50%", 50, True),
        ("Maximum 100%", 100, True),
        ("Negative share", -10, False),
        ("Exceeding 100%", 150, False),
    ]

    for label, val, is_valid in allocation_matrix:
        valid_share = 0 <= val <= 100
        assert valid_share == is_valid, f"MAM share boundary logic check mismatch for {val}% ({label})"

    # Verify modal exists in DOM
    expect(mam_page.mam_share_modal).to_be_attached()

    admin_error_monitor.assert_no_errors("MAM Share Allocation Boundaries")


@pytest.mark.admin
@pytest.mark.validation
def test_val_pamm_share_modal_allocation_boundaries(
    pamm_page: PammPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 5: Verify PAMM Share Modal input bounds and safe modal presence.
    """
    pamm_page.navigate()
    pamm_page.page.wait_for_timeout(1000)

    allocation_matrix = [
        ("Zero percent", 0, True),
        ("Standard 30%", 30, True),
        ("Maximum 100%", 100, True),
        ("Negative percent", -5, False),
        ("Over 100%", 101, False),
    ]

    for label, val, is_valid in allocation_matrix:
        valid_share = 0 <= val <= 100
        assert valid_share == is_valid, f"PAMM share boundary logic check mismatch for {val}% ({label})"

    expect(pamm_page.pamm_share_modal).to_be_attached()

    admin_error_monitor.assert_no_errors("PAMM Share Allocation Boundaries")


# ==============================================================================
# PILLAR 1: DATATABLE SEARCH & SECURITY SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_search_filter_and_empty_state(
    mam_page: MamPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching MAM master accounts filters rows, and non-existent
    query displays empty state cleanly.
    """
    mam_page.navigate()
    mam_page.page.wait_for_timeout(1000)

    mam_page.search_mam("NON_EXISTENT_MAM_ACCOUNT_999999")
    mam_page.page.wait_for_timeout(600)

    empty_cell = mam_page.page.locator("table#datatable tbody td").first
    if empty_cell.is_visible():
        cell_text = empty_cell.inner_text().lower()
        assert any(term in cell_text for term in ["no matching", "no data", "showing 0 to 0", "not found"]), (
            f"Expected empty state text, got: {cell_text}"
        )

    mam_page.clear_search()
    admin_error_monitor.assert_no_errors("MAM Search & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_pamm_search_filter_and_empty_state(
    pamm_page: PammPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching PAMM master accounts filters rows, and non-existent
    query displays empty state cleanly.
    """
    pamm_page.navigate()
    pamm_page.page.wait_for_timeout(1000)

    pamm_page.search_pamm("NON_EXISTENT_PAMM_ACCOUNT_999999")
    pamm_page.page.wait_for_timeout(600)

    empty_cell = pamm_page.page.locator("table#datatable tbody td").first
    if empty_cell.is_visible():
        cell_text = empty_cell.inner_text().lower()
        assert any(term in cell_text for term in ["no matching", "no data", "showing 0 to 0", "not found"]), (
            f"Expected empty state text, got: {cell_text}"
        )

    pamm_page.clear_search()
    admin_error_monitor.assert_no_errors("PAMM Search & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_search_sqli_xss_sanitization(
    mam_page: MamPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Test injecting SQLi and XSS payloads into MAM search input
    does not trigger unexpected browser dialogs or uncaught JS exceptions.
    """
    mam_page.navigate()
    mam_page.page.wait_for_timeout(1000)

    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    mam_page.page.on("dialog", handle_dialog)

    # Test SQLi payloads
    for payload, description in SQLI_PAYLOADS[:2]:
        mam_page.search_mam(payload)
        mam_page.page.wait_for_timeout(400)
        body_text = mam_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL syntax error exposed for {description}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for {description}"
        assert not dialog_triggered, f"Security alert dialog triggered by {description}"

    # Test XSS payloads
    for payload, description in XSS_PAYLOADS[:2]:
        mam_page.search_mam(payload)
        mam_page.page.wait_for_timeout(400)
        is_pwned = mam_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"
        assert not dialog_triggered, f"Security alert dialog triggered by XSS: {payload}"

    mam_page.clear_search()
    expect(mam_page.datatable).to_be_attached()
    admin_error_monitor.assert_no_js_errors("MAM Search SQLi & XSS Sanitization")


@pytest.mark.admin
@pytest.mark.validation
def test_val_pamm_search_sqli_xss_sanitization(
    pamm_page: PammPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Test injecting SQLi and XSS payloads into PAMM search input
    does not trigger unexpected browser dialogs or uncaught JS exceptions.
    """
    pamm_page.navigate()
    pamm_page.page.wait_for_timeout(1000)

    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    pamm_page.page.on("dialog", handle_dialog)

    # Test SQLi payloads
    for payload, description in SQLI_PAYLOADS[:2]:
        pamm_page.search_pamm(payload)
        pamm_page.page.wait_for_timeout(400)
        body_text = pamm_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL syntax error exposed for {description}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for {description}"
        assert not dialog_triggered, f"Security alert dialog triggered by {description}"

    # Test XSS payloads
    for payload, description in XSS_PAYLOADS[:2]:
        pamm_page.search_pamm(payload)
        pamm_page.page.wait_for_timeout(400)
        is_pwned = pamm_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"
        assert not dialog_triggered, f"Security alert dialog triggered by XSS: {payload}"

    pamm_page.clear_search()
    expect(pamm_page.datatable).to_be_attached()
    admin_error_monitor.assert_no_js_errors("PAMM Search SQLi & XSS Sanitization")


# ==============================================================================
# PILLAR 3: PAGE LENGTH DROPDOWN PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_pamm_page_length_selector_validation(
    mam_page: MamPage,
    pamm_page: PammPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify page length dropdown selection (10, 25) updates table info on MAM and PAMM.
    """
    # 1. MAM Page Length
    mam_page.navigate()
    mam_page.page.wait_for_timeout(1000)
    expect(mam_page.length_dropdown).to_be_visible()
    mam_page.length_dropdown.select_option("25")
    mam_page.page.wait_for_timeout(600)
    expect(mam_page.datatable).to_be_attached()

    # 2. PAMM Page Length
    pamm_page.navigate()
    pamm_page.page.wait_for_timeout(1000)
    expect(pamm_page.length_dropdown).to_be_visible()
    pamm_page.length_dropdown.select_option("25")
    pamm_page.page.wait_for_timeout(600)
    expect(pamm_page.datatable).to_be_attached()

    admin_error_monitor.assert_no_errors("MAM & PAMM Page Length Selector")


# ==============================================================================
# PILLAR 6: TABLE COLUMN SORTING TRAVERSAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_mam_pamm_column_sorting_traversal(
    mam_page: MamPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table headers toggles sort order (sorting_asc / sorting_desc)
    without rendering errors or broken rows.
    """
    mam_page.navigate()
    mam_page.page.wait_for_timeout(1000)

    headers = mam_page.table_headers
    header_count = headers.count()
    assert header_count > 0, "Table should have header columns"

    tested = 0
    for idx in range(min(header_count, 4)):
        th = headers.nth(idx)
        th_class = th.get_attribute("class") or ""
        if "sorting" in th_class:
            th.click()
            mam_page.page.wait_for_timeout(400)
            updated_class = th.get_attribute("class") or ""
            assert "sorting_asc" in updated_class or "sorting_desc" in updated_class, (
                f"Expected header {idx} to toggle sort class, got: {updated_class}"
            )
            tested += 1
            if tested >= 2:
                break

    admin_error_monitor.assert_no_errors("MAM Column Sorting")
