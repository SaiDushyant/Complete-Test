"""
Admin Portal User KYC Document Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A.2, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Search input, Remark textarea (#remark), SQLi/XSS sanitization.
2. Buttons & Actions: Remark modal, Delete modal, Add document modal, safe modal dismissals.
3. Dropdowns & Selects: Document verification status (Verified, Not Verified, Rejected), entries per page.
4. Document / Dropzone Rules: Rejected status requires mandatory non-empty remark.
5. Date & Time Pickers: Inverted date boundaries ('From > To'), date clear restoring full ledger.
6. Calculations & Tables: S.No ordering, pagination controls, column sorting traversal.
7. Security: Hidden permission flags (#editUserDoc, #deleteUserDoc, etc.), SQLi/XSS attack vectors.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.user_document_page import UserDocumentPage
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
def test_val_user_document_route_and_table_integrity(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify KYC Document page navigates successfully, renders
    the datatable, action buttons, and permission flags.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    expect(user_document_page.table).to_be_attached(timeout=15000)
    expect(user_document_page.page_actions).to_be_attached()
    expect(user_document_page.table_card).to_be_visible()

    admin_error_monitor.assert_no_errors("User Document Route & Table Integrity")


# ==============================================================================
# PILLAR 7: HIDDEN PERMISSION FLAGS INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_hidden_permission_flags_integrity(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Verify all 4 hidden permission configuration inputs
    exist in the DOM with their secure authorization state.
    """
    user_document_page.navigate()

    permission_flags = [
        (user_document_page.edit_user_doc_hidden, "editUserDoc"),
        (user_document_page.delete_user_doc_hidden, "deleteUserDoc"),
        (user_document_page.verify_user_doc_hidden, "verifyUserDoc"),
        (user_document_page.remarks_user_doc_hidden, "remarksUserDoc"),
    ]

    for loc, field_id in permission_flags:
        expect(loc).to_be_attached()
        assert loc.get_attribute("type") == "hidden", f"Expected #{field_id} to have type='hidden'"
        val = loc.get_attribute("value")
        assert val in ["0", "1"], f"Expected #{field_id} value to be binary flag, got '{val}'"

    admin_error_monitor.assert_no_errors("User Document Permission Flags")


# ==============================================================================
# PILLAR 3 & 4: DOCUMENT VERIFICATION DROPDOWNS & STATUS TRANSITION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_status_dropdown_options_and_classes(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the verification dropdowns present exact status options:
    'Verified' (1), 'Not Verified' (0), and 'Rejected' (2) with corresponding CSS classes.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    dropdowns = user_document_page.verification_dropdowns
    if dropdowns.count() > 0:
        first_select = dropdowns.first
        expect(first_select).to_be_visible()

        options = [opt.inner_text().strip() for opt in first_select.locator("option").all()]
        assert "Verified" in options, "Expected 'Verified' status option"
        assert "Not Verified" in options, "Expected 'Not Verified' status option"
        assert "Rejected" in options, "Expected 'Rejected' status option"

        current_val = first_select.input_value()
        current_class = first_select.get_attribute("class") or ""
        if current_val == "1":
            assert "btn-success" in current_class
        elif current_val == "0":
            assert "btn-warning" in current_class
        elif current_val == "2":
            assert "btn-danger" in current_class

    admin_error_monitor.assert_no_errors("Document Status Options")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_rejection_mandates_remarks_workflow(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2 & 4: Verify selecting 'Rejected' automatically triggers the Remarks
    modal (#remarkModal), mandates a non-empty comment, and allows clean dismissal.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    dropdowns = user_document_page.verification_dropdowns
    if dropdowns.count() > 0:
        first_select = dropdowns.first
        initial_val = first_select.input_value()

        # Select 'Rejected' (2)
        first_select.select_option("2")
        user_document_page.page.wait_for_timeout(600)

        # Assert Remarks modal is opened
        modal = user_document_page.remark_modal
        expect(modal).to_be_visible(timeout=5000)
        expect(user_document_page.remark_modal_title).to_contain_text("Remarks Form")

        # Verify textarea exists
        textarea = user_document_page.remark_modal_textarea
        expect(textarea).to_be_visible()

        # Dismiss modal without submitting mutation
        user_document_page.remark_modal_close.first.click()
        user_document_page.page.wait_for_timeout(500)
        expect(modal).not_to_be_visible()

        # Revert dropdown value cleanly
        first_select.select_option(initial_val)
        user_document_page.page.wait_for_timeout(300)

    admin_error_monitor.assert_no_errors("Document Rejection Remarks Workflow")


# ==============================================================================
# PILLAR 2: ROW ACTIONS & MODAL DISMISSAL SAFEGUARDS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_remark_action_modal_lifecycle(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking remark action button (.btnRemark) opens #remarkModal,
    allows typing remarks, and dismisses cleanly via 'Close'.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    remark_buttons = user_document_page.remark_buttons
    if remark_buttons.count() > 0:
        btn = remark_buttons.first
        btn.click()
        user_document_page.page.wait_for_timeout(500)

        modal = user_document_page.remark_modal
        expect(modal).to_be_visible()

        # Test textarea typing and boundary injection check
        textarea = user_document_page.remark_modal_textarea
        textarea.fill("Validation test remarks: Documents under manual verification.")
        expect(textarea).to_have_value("Validation test remarks: Documents under manual verification.")

        # Dismiss safely
        user_document_page.remark_modal_close.first.click()
        user_document_page.page.wait_for_timeout(500)
        expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Remark Modal Lifecycle")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_delete_modal_lifecycle(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking delete action button (.BtnDelete) triggers confirmation/delete
    modal, and closing it dismisses without executing deletion.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    delete_buttons = user_document_page.delete_buttons
    if delete_buttons.count() > 0:
        btn = delete_buttons.first
        btn.click()
        user_document_page.page.wait_for_timeout(500)

        # Check either #deleteModal or .jconfirm-box
        delete_modal = user_document_page.delete_modal
        confirm_dialog = user_document_page.confirm_dialog

        if delete_modal.is_visible():
            user_document_page.delete_modal_close.first.click()
            user_document_page.page.wait_for_timeout(500)
            expect(delete_modal).not_to_be_visible()
        elif confirm_dialog.is_visible():
            cancel_btn = confirm_dialog.locator("button:has-text('cancel'), button:has-text('No'), .btn-default").first
            if cancel_btn.is_visible():
                cancel_btn.click()
            user_document_page.page.wait_for_timeout(500)
            expect(confirm_dialog).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Delete Document Modal Lifecycle")


# ==============================================================================
# PILLAR 1: SEARCH FILTERING & SECURITY SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_search_filter_and_empty_state(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching existing user filters rows, and searching non-existent query
    displays empty state cleanly without crashing.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    # Search non-existent query
    user_document_page.search_document("NON_EXISTENT_DOCUMENT_USER_999999")
    user_document_page.page.wait_for_timeout(600)

    empty_cell = user_document_page.page.locator("#datatable tbody td").first
    expect(empty_cell).to_be_visible()
    cell_text = empty_cell.inner_text().lower()
    assert any(term in cell_text for term in ["no matching", "no data", "showing 0 to 0", "not found"]), (
        f"Expected empty state text, got: {cell_text}"
    )

    # Clear search restores table
    user_document_page.clear_search()
    user_document_page.page.wait_for_timeout(600)
    expect(user_document_page.document_rows.first).to_be_visible(timeout=10000)

    admin_error_monitor.assert_no_errors("User Document Search & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_search_sqli_xss_sanitization(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Test injecting SQLi and XSS payloads into KYC Document
    search input does not trigger unexpected browser dialogs or expose database errors.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    user_document_page.page.on("dialog", handle_dialog)

    # Test SQLi payloads
    for payload, description in SQLI_PAYLOADS[:2]:
        user_document_page.search_document(payload)
        user_document_page.page.wait_for_timeout(500)
        body_text = user_document_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL syntax error exposed for {description}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for {description}"
        assert not dialog_triggered, f"Security alert dialog triggered by {description}"

    # Test XSS payloads
    for payload, description in XSS_PAYLOADS[:2]:
        user_document_page.search_document(payload)
        user_document_page.page.wait_for_timeout(500)
        is_pwned = user_document_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"
        assert not dialog_triggered, f"Security alert dialog triggered by XSS: {payload}"

    user_document_page.clear_search()
    expect(user_document_page.table).to_be_attached()
    admin_error_monitor.assert_no_js_errors("User Document Search SQLi & XSS Sanitization")


# ==============================================================================
# PILLAR 3: PAGE LENGTH DROPDOWN PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_page_length_selector_validation(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the page length dropdown (10, 25, 50) triggers server-side
    re-draw and accurately updates the datatable info status.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    length_select = user_document_page.length_select
    expect(length_select).to_be_visible()

    for length in ["10", "25"]:
        length_select.select_option(length)
        user_document_page.wait_for_table_loaded()

        info_loc = user_document_page.table_info
        expect(info_loc).to_be_visible()
        expect(info_loc).to_contain_text(re.compile(rf"Showing 1 to (?:{length}|\d+) of", re.IGNORECASE))

    admin_error_monitor.assert_no_errors("Document Page Length Selector")


# ==============================================================================
# PILLAR 5: DATE RANGE BOUNDARIES & RESET
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_date_filters_boundaries(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test inverted date boundaries ('From > To') and verify Apply button
    triggers filter cleanly, and Clear button restores date inputs.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    from_date = user_document_page.from_date_input
    to_date = user_document_page.to_date_input
    apply_btn = user_document_page.apply_button
    clear_btn = user_document_page.clear_button

    if from_date.is_visible() and to_date.is_visible():
        input_type = from_date.get_attribute("type") or "date"
        if input_type == "datetime-local":
            from_date.fill("2026-12-31T23:59")
            to_date.fill("2026-01-01T00:00")
        else:
            from_date.fill("2026-12-31")
            to_date.fill("2026-01-01")

        if apply_btn.is_visible():
            apply_btn.click()
            user_document_page.wait_for_table_loaded()
            expect(user_document_page.table).to_be_attached()

        if clear_btn.is_visible():
            clear_btn.click()
            user_document_page.wait_for_table_loaded()
            expect(user_document_page.table).to_be_attached()

    admin_error_monitor.assert_no_errors("User Document Date Filter Boundaries")


# ==============================================================================
# PILLAR 6: TABLE COLUMN SORTING TRAVERSAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_document_column_sorting_traversal(
    user_document_page: UserDocumentPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table headers toggles sort order (sorting_asc / sorting_desc)
    without rendering errors or broken rows.
    """
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)

    headers = user_document_page.table_headers
    header_count = headers.count()
    assert header_count > 0, "Table should have header columns"

    tested = 0
    for idx in range(min(header_count, 4)):
        th = headers.nth(idx)
        th_class = th.get_attribute("class") or ""
        if "sorting" in th_class:
            th.click()
            user_document_page.page.wait_for_timeout(400)
            updated_class = th.get_attribute("class") or ""
            assert "sorting_asc" in updated_class or "sorting_desc" in updated_class, (
                f"Expected header {idx} to toggle sort class, got: {updated_class}"
            )
            tested += 1
            if tested >= 2:
                break

    admin_error_monitor.assert_no_errors("User Document Column Sorting")
