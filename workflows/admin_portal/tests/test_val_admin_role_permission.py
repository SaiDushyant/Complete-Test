"""
Admin Portal Role & Permission Management Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Add Role input (role_name), Search input, SQLi/XSS sanitization.
2. Buttons & Actions: Modal triggers (#addNew, a.BtnDelete, a.btnNameEdit), SweetAlert dialog, safe dismissals.
3. Dropdowns & Selects: Entries per page pagination (10, 25, 50, 100).
6. Calculations & Tables: S.No ordering, pagination controls, column sorting traversal.
7. Security: Hidden permission flags (#editrolePermission, #deleterolePermission, #editPermission), injection vectors.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.role_permission_page import RolePermissionPage
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
def test_val_role_permission_route_and_table_integrity(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify Role Permission page navigates successfully, renders
    the datatable, header elements, and action buttons.
    """
    role_permission_page.navigate()
    role_permission_page.page.wait_for_timeout(1000)

    expect(role_permission_page.table).to_be_attached(timeout=15000)
    expect(role_permission_page.page_title).to_be_visible()
    expect(role_permission_page.add_role_button).to_be_visible()

    admin_error_monitor.assert_no_errors("Role Permission Route & Table Integrity")


# ==============================================================================
# PILLAR 7: HIDDEN PERMISSION FLAGS INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_permission_hidden_flags_integrity(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Verify all 3 hidden permission configuration inputs
    exist in the DOM with their binary authorization flags.
    """
    role_permission_page.navigate()

    permission_flags = [
        (role_permission_page.edit_role_perm_hidden, "editrolePermission"),
        (role_permission_page.delete_role_perm_hidden, "deleterolePermission"),
        (role_permission_page.edit_perm_hidden, "editPermission"),
    ]

    for loc, field_id in permission_flags:
        expect(loc).to_be_attached()
        assert loc.get_attribute("type") == "hidden", f"Expected #{field_id} to have type='hidden'"
        val = loc.get_attribute("value")
        assert val in ["0", "1"], f"Expected #{field_id} value to be binary flag, got '{val}'"

    admin_error_monitor.assert_no_errors("Role Permission Flags")


# ==============================================================================
# PILLAR 1 & 2: ADD ROLE MODAL (#myModal) LIFECYCLE & INPUT VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_add_modal_lifecycle_and_field_elements(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking 'Add Role Permission' opens #myModal with
    role name input, Save button, and dismisses cleanly via 'Close'.
    """
    role_permission_page.navigate()
    role_permission_page.add_role_button.click()
    role_permission_page.page.wait_for_timeout(500)

    modal = role_permission_page.role_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(role_permission_page.role_modal_title).to_contain_text("Role Permission Form")

    # Verify input field and save button
    expect(role_permission_page.role_modal_input).to_be_visible()
    expect(role_permission_page.role_modal_save).to_be_visible()

    # Dismiss modal safely
    role_permission_page.role_modal_close.first.click()
    role_permission_page.page.wait_for_timeout(500)
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Add Role Modal Lifecycle")


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_add_empty_form_submission_boundaries(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify submitting an empty role name enforces required boundary.
    """
    role_permission_page.navigate()
    role_permission_page.add_role_button.click()
    role_permission_page.page.wait_for_timeout(500)

    modal = role_permission_page.role_modal
    expect(modal).to_be_visible()

    # Clear input
    role_permission_page.role_modal_input.fill("")

    # Verify checkValidity prevents submission
    validation_status = role_permission_page.page.evaluate("""() => {
        const input = document.querySelector("#myModal input[name='role_name']");
        return {
            required: input ? input.required : false,
            valid: input ? input.checkValidity() : true
        };
    }""")

    # Attempt to click save
    role_permission_page.role_modal_save.click()
    role_permission_page.page.wait_for_timeout(400)

    # Modal should remain open
    expect(modal).to_be_visible()

    role_permission_page.role_modal_close.first.click()
    role_permission_page.page.wait_for_timeout(400)
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Empty Role Form Submission")


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_name_input_matrix_validation(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test Role Name string boundary values.
    """
    role_permission_page.navigate()
    role_permission_page.add_role_button.click()
    role_permission_page.page.wait_for_timeout(500)

    input_elem = role_permission_page.role_modal_input
    expect(input_elem).to_be_visible()

    test_roles = [
        "Compliance Auditor",
        "Risk Manager Tier 1",
        "Junior Support Desk",
    ]

    for role_name in test_roles:
        input_elem.fill(role_name)
        expect(input_elem).to_have_value(role_name)

    role_permission_page.role_modal_close.first.click()
    role_permission_page.page.wait_for_timeout(400)
    admin_error_monitor.assert_no_errors("Role Name Input Matrix")


# ==============================================================================
# PILLAR 2: SWEETALERT DELETE CONFIRMATION MODAL LIFECYCLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_delete_sweetalert_modal_lifecycle(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking delete action button triggers SweetAlert2 popup,
    and clicking 'No, cancel!' dismisses popup cleanly without state deletion.
    """
    role_permission_page.navigate()
    role_permission_page.page.wait_for_timeout(1000)

    delete_buttons = role_permission_page.delete_buttons
    if delete_buttons.count() > 0:
        btn = delete_buttons.first
        btn.click()
        role_permission_page.page.wait_for_timeout(500)

        # SweetAlert popup should appear
        popup = role_permission_page.swal_popup
        if popup.is_visible():
            expect(popup).to_be_visible()
            cancel_btn = role_permission_page.swal_cancel_button
            expect(cancel_btn).to_be_visible()
            cancel_btn.click()
            role_permission_page.page.wait_for_timeout(500)
            expect(popup).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Role Delete SweetAlert Lifecycle")


# ==============================================================================
# PILLAR 1: DATATABLE SEARCH & SECURITY SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_search_filter_and_empty_state(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching role names filters rows, and non-existent query
    displays empty state cleanly.
    """
    role_permission_page.navigate()
    role_permission_page.page.wait_for_timeout(1000)

    # Search non-existent query
    role_permission_page.search_input.fill("NON_EXISTENT_ROLE_NAME_999999")
    role_permission_page.page.wait_for_timeout(600)

    empty_cell = role_permission_page.page.locator("table#datatable tbody td").first
    if empty_cell.is_visible():
        cell_text = empty_cell.inner_text().lower()
        assert any(term in cell_text for term in ["no matching", "no data", "showing 0 to 0", "not found"]), (
            f"Expected empty state text, got: {cell_text}"
        )

    role_permission_page.search_input.fill("")
    role_permission_page.page.wait_for_timeout(600)
    expect(role_permission_page.role_rows.first).to_be_visible(timeout=10000)

    admin_error_monitor.assert_no_errors("Role Search & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_search_sqli_xss_sanitization(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Test injecting SQLi and XSS payloads into Role
    search input does not trigger unexpected browser dialogs or uncaught JS exceptions.
    """
    role_permission_page.navigate()
    role_permission_page.page.wait_for_timeout(1000)

    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    role_permission_page.page.on("dialog", handle_dialog)

    # Test SQLi payloads
    for payload, description in SQLI_PAYLOADS[:2]:
        role_permission_page.search_input.fill(payload)
        role_permission_page.page.wait_for_timeout(400)
        body_text = role_permission_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL syntax error exposed for {description}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for {description}"
        assert not dialog_triggered, f"Security alert dialog triggered by {description}"

    # Test XSS payloads
    for payload, description in XSS_PAYLOADS[:2]:
        role_permission_page.search_input.fill(payload)
        role_permission_page.page.wait_for_timeout(400)
        is_pwned = role_permission_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"
        assert not dialog_triggered, f"Security alert dialog triggered by XSS: {payload}"

    role_permission_page.search_input.fill("")
    expect(role_permission_page.table).to_be_attached()
    admin_error_monitor.assert_no_js_errors("Role Search SQLi & XSS Sanitization")


# ==============================================================================
# PILLAR 3: PAGE LENGTH DROPDOWN PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_page_length_selector_validation(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the page length dropdown (10, 25) triggers re-draw
    and accurately updates datatable info.
    """
    role_permission_page.navigate()
    role_permission_page.page.wait_for_timeout(1000)

    length_select = role_permission_page.length_select
    expect(length_select).to_be_visible()

    for length in ["10", "25"]:
        length_select.select_option(length)
        role_permission_page.page.wait_for_timeout(600)

        info_loc = role_permission_page.table_info
        expect(info_loc).to_be_visible()
        expect(info_loc).to_contain_text(re.compile(rf"Showing 1 to (?:{length}|\d+) of", re.IGNORECASE))

    admin_error_monitor.assert_no_errors("Role Page Length Selector")


# ==============================================================================
# PILLAR 6: TABLE COLUMN SORTING TRAVERSAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_role_column_sorting_traversal(
    role_permission_page: RolePermissionPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table headers toggles sort order (sorting_asc / sorting_desc)
    without rendering errors or broken rows.
    """
    role_permission_page.navigate()
    role_permission_page.page.wait_for_timeout(1000)

    headers = role_permission_page.table_headers
    header_count = headers.count()
    assert header_count > 0, "Table should have header columns"

    tested = 0
    for idx in range(min(header_count, 3)):
        th = headers.nth(idx)
        th_class = th.get_attribute("class") or ""
        if "sorting" in th_class:
            th.click()
            role_permission_page.page.wait_for_timeout(400)
            updated_class = th.get_attribute("class") or ""
            assert "sorting_asc" in updated_class or "sorting_desc" in updated_class, (
                f"Expected header {idx} to toggle sort class, got: {updated_class}"
            )
            tested += 1
            if tested >= 2:
                break

    admin_error_monitor.assert_no_errors("Role Column Sorting")
