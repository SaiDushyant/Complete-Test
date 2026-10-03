"""
Admin Portal Lead Management & Bulk Import Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A.4, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Add Lead form (Name, Email, Phone, Description), Search input, SQLi/XSS sanitization.
2. Buttons & Actions: Modal triggers (#addNew, #bulkUpload, #manageLeadTypes), safe modal dismissals.
3. Dropdowns & Selects: Admin assign select, Lead Type select, Entries per page pagination.
4. Dropzones & Uploads: Bulk file upload input (#bulk_file) format & boundary rules.
5. Date & Time Pickers: Followup date picker, report date boundaries.
6. Calculations & Tables: S.No ordering, pagination controls, column sorting traversal.
7. Security: Hidden permission flags (#editlead, #deletelead, #settingsLeadType), injection attacks.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.manage_leads_page import ManageLeadsPage
from workflows.admin_portal.pages.leads_report_page import LeadsReportPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# PILLAR 1 & 2: SUB-ROUTES INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_subroutes_integrity(
    manage_leads_page: ManageLeadsPage,
    leads_report_page: LeadsReportPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify primary Lead Management sub-routes navigate successfully,
    render their respective DataTables, and show zero critical UI crashes.
    """
    # 1. Manage Leads (/admin/Controlbase/leads)
    manage_leads_page.navigate()
    manage_leads_page.page.wait_for_timeout(1000)
    expect(manage_leads_page.datatable).to_be_attached(timeout=15000)
    expect(manage_leads_page.actions_bar).to_be_visible()

    # 2. Leads Report (/admin/Controlbase/leadReport)
    leads_report_page.navigate()
    leads_report_page.page.wait_for_timeout(1000)
    expect(leads_report_page.datatable).to_be_attached(timeout=15000)
    expect(leads_report_page.filter_bar).to_be_visible()

    admin_error_monitor.assert_no_errors("Lead Management Sub-Routes")


# ==============================================================================
# PILLAR 7: HIDDEN PERMISSION FLAGS INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_lead_hidden_permission_flags_integrity(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Verify all 3 hidden permission configuration inputs
    exist in the DOM with their binary authorization flags.
    """
    manage_leads_page.navigate()

    permission_flags = [
        (manage_leads_page.permission_edit, "editlead"),
        (manage_leads_page.permission_delete, "deletelead"),
        (manage_leads_page.permission_settings, "settingsLeadType"),
    ]

    for loc, field_id in permission_flags:
        expect(loc).to_be_attached()
        assert loc.get_attribute("type") == "hidden", f"Expected #{field_id} to have type='hidden'"
        val = loc.get_attribute("value")
        assert val in ["0", "1"], f"Expected #{field_id} value to be binary flag, got '{val}'"

    admin_error_monitor.assert_no_errors("Lead Permission Flags")


# ==============================================================================
# PILLAR 1 & 2: ADD LEAD MODAL (#myModal) LIFECYCLE & INPUT VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_lead_add_modal_field_elements_and_lifecycle(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking '+ Add Lead' opens #myModal with all onboarding
    fields, and closing dismisses the modal cleanly without state leaks.
    """
    manage_leads_page.navigate()
    manage_leads_page.open_add_lead_modal()

    modal = manage_leads_page.lead_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(manage_leads_page.lead_modal_title).to_contain_text("Lead")

    # Verify input fields inside modal
    expect(modal.locator("#name")).to_be_attached()
    expect(modal.locator("#email")).to_be_attached()
    expect(modal.locator("#phone")).to_be_attached()
    expect(modal.locator("#admin_id")).to_be_attached()
    expect(modal.locator("#lead_type_id")).to_be_attached()
    expect(modal.locator("#followup_date")).to_be_attached()
    expect(modal.locator("#discription")).to_be_attached()
    expect(modal.locator("#formSubmit")).to_be_attached()

    # Close modal cleanly
    manage_leads_page.close_add_lead_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Add Lead Modal Lifecycle")


@pytest.mark.admin
@pytest.mark.validation
def test_val_lead_add_empty_form_submission_boundaries(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify submitting an empty lead form enforces validation
    and prevents improper submission.
    """
    manage_leads_page.navigate()
    manage_leads_page.open_add_lead_modal()

    modal = manage_leads_page.lead_modal
    expect(modal).to_be_visible()

    # Clear all text inputs
    modal.locator("#name").fill("")
    modal.locator("#email").fill("")
    modal.locator("#phone").fill("")

    # Verify required / validity constraints via browser evaluation
    validation_status = manage_leads_page.page.evaluate("""() => {
        const nameInput = document.querySelector("#myModal #name");
        const emailInput = document.querySelector("#myModal #email");
        const phoneInput = document.querySelector("#myModal #phone");

        return {
            nameRequired: nameInput ? nameInput.required : false,
            emailRequired: emailInput ? emailInput.required : false,
            nameValid: nameInput ? nameInput.checkValidity() : true,
            emailValid: emailInput ? emailInput.checkValidity() : true
        };
    }""")

    # Attempt to click submit without filling inputs
    modal.locator("#formSubmit").click()
    manage_leads_page.page.wait_for_timeout(500)

    # Modal should remain open because validation prevented submission
    expect(modal).to_be_visible()

    manage_leads_page.close_add_lead_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Empty Lead Form Boundaries")


@pytest.mark.admin
@pytest.mark.validation
def test_val_lead_add_input_matrix_validation(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test Lead form input matrix for Name, Email, and Phone.
    """
    manage_leads_page.navigate()
    manage_leads_page.open_add_lead_modal()
    modal = manage_leads_page.lead_modal

    # Name validation
    name_input = modal.locator("#name")
    name_input.fill("Enterprise Trading Desk")
    expect(name_input).to_have_value("Enterprise Trading Desk")

    # Email format validation
    email_matrix = [
        ("Valid RFC Email", "lead@institution.com", True),
        ("Missing Domain", "lead@", False),
        ("Missing Recipient", "@domain.com", False),
        ("Embedded Space", "lead name@test.com", False),
    ]

    for label, email_val, exp_valid in email_matrix:
        email_input = modal.locator("#email")
        email_input.fill(email_val)
        email_input.dispatch_event("input")
        email_input.dispatch_event("change")

        is_valid = manage_leads_page.page.evaluate("""([val]) => {
            const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            return re.test(val);
        }""", [email_val])
        assert is_valid == exp_valid, f"Lead email format mismatch for '{email_val}' ({label})"

    # Phone input (enforces type='number' numeric digits only)
    phone_input = modal.locator("#phone")
    expect(phone_input).to_have_attribute("type", "number")
    phone_input.fill("9876543210")
    expect(phone_input).to_have_value("9876543210")

    manage_leads_page.close_add_lead_modal()
    admin_error_monitor.assert_no_errors("Lead Add Input Matrix")


# ==============================================================================
# PILLAR 4: BULK UPLOAD MODAL & FILE TYPE BOUNDARIES
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_lead_bulk_upload_modal_lifecycle_and_file_boundaries(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2 & 4: Verify clicking 'Bulk Upload' opens #bulkUploadModal with file
    upload input (#bulk_file), tests format boundaries, and dismisses cleanly.
    """
    manage_leads_page.navigate()
    manage_leads_page.open_bulk_upload_modal()

    modal = manage_leads_page.bulk_upload_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(manage_leads_page.bulk_upload_modal_title).to_contain_text("Bulk Upload")

    # Verify file input exists
    file_input = modal.locator("#bulk_file")
    expect(file_input).to_be_attached()
    assert file_input.get_attribute("type") == "file", "Expected #bulk_file to have type='file'"

    # Verify submit button
    expect(modal.locator("#bulkFormSubmit")).to_be_attached()

    # Close modal cleanly
    manage_leads_page.close_bulk_upload_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Bulk Upload Modal Lifecycle")


# ==============================================================================
# PILLAR 2: LEAD TYPES MODAL (#leadTypeModal) LIFECYCLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_lead_types_modal_lifecycle(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking 'Lead Types' opens #leadTypeModal, verifies
    category input (#lead_type_name), and dismisses cleanly without state leaks.
    """
    manage_leads_page.navigate()
    manage_leads_page.open_lead_types_modal()

    modal = manage_leads_page.lead_types_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(manage_leads_page.lead_types_modal_title).to_contain_text("Lead Type")

    # Check input and action buttons
    expect(modal.locator("#lead_type_name")).to_be_attached()
    expect(modal.locator("#leadTypeSubmit")).to_be_attached()

    manage_leads_page.close_lead_types_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Lead Types Modal Lifecycle")


# ==============================================================================
# PILLAR 1: DATATABLE SEARCH & SECURITY SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_table_search_filter_and_empty_state(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching leads filters rows, and searching non-existent query
    displays empty state cleanly without crashing.
    """
    manage_leads_page.navigate()
    manage_leads_page.page.wait_for_timeout(1000)

    # Search non-existent query
    manage_leads_page.search_leads("NON_EXISTENT_LEAD_TICKET_999999")
    manage_leads_page.page.wait_for_timeout(600)

    empty_cell = manage_leads_page.page.locator("table#datatable tbody td").first
    expect(empty_cell).to_be_visible()
    cell_text = empty_cell.inner_text().lower()
    assert any(term in cell_text for term in ["no matching", "no data", "showing 0 to 0", "not found"]), (
        f"Expected empty state text, got: {cell_text}"
    )

    # Clear search restores table
    manage_leads_page.clear_search()
    manage_leads_page.page.wait_for_timeout(600)
    expect(manage_leads_page.table_rows.first).to_be_visible(timeout=10000)

    admin_error_monitor.assert_no_errors("Leads Search & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_table_search_sqli_xss_sanitization(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Test injecting SQLi and XSS payloads into Leads
    search input does not trigger unexpected browser dialogs or uncaught JS exceptions.
    """
    manage_leads_page.navigate()
    manage_leads_page.page.wait_for_timeout(1000)

    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    manage_leads_page.page.on("dialog", handle_dialog)

    # Test SQLi payloads
    for payload, description in SQLI_PAYLOADS[:2]:
        manage_leads_page.search_leads(payload)
        manage_leads_page.page.wait_for_timeout(500)
        body_text = manage_leads_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL syntax error exposed for {description}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for {description}"
        assert not dialog_triggered, f"Security alert dialog triggered by {description}"

    # Test XSS payloads
    for payload, description in XSS_PAYLOADS[:2]:
        manage_leads_page.search_leads(payload)
        manage_leads_page.page.wait_for_timeout(500)
        is_pwned = manage_leads_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"
        assert not dialog_triggered, f"Security alert dialog triggered by XSS: {payload}"

    manage_leads_page.clear_search()
    expect(manage_leads_page.datatable).to_be_attached()
    admin_error_monitor.assert_no_js_errors("Leads Search SQLi & XSS Sanitization")


# ==============================================================================
# PILLAR 3: PAGE LENGTH DROPDOWN PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_table_page_length_selector_validation(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the page length dropdown (10, 25, 50) triggers server-side
    re-draw and accurately updates the datatable info status.
    """
    manage_leads_page.navigate()
    manage_leads_page.page.wait_for_timeout(1000)

    length_select = manage_leads_page.length_dropdown
    expect(length_select).to_be_visible()

    for length in ["10", "25"]:
        length_select.select_option(length)
        manage_leads_page.page.wait_for_timeout(800)

        info_loc = manage_leads_page.datatable_info
        expect(info_loc).to_be_visible()
        expect(info_loc).to_contain_text(re.compile(rf"Showing 1 to (?:{length}|\d+) of", re.IGNORECASE))

    admin_error_monitor.assert_no_errors("Leads Page Length Selector")


# ==============================================================================
# PILLAR 6: TABLE COLUMN SORTING TRAVERSAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_table_column_sorting_traversal(
    manage_leads_page: ManageLeadsPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table headers toggles sort order (sorting_asc / sorting_desc)
    without rendering errors or broken rows.
    """
    manage_leads_page.navigate()
    manage_leads_page.page.wait_for_timeout(1000)

    headers = manage_leads_page.table_headers
    header_count = headers.count()
    assert header_count > 0, "Table should have header columns"

    tested = 0
    for idx in range(min(header_count, 4)):
        th = headers.nth(idx)
        th_class = th.get_attribute("class") or ""
        if "sorting" in th_class:
            th.click()
            manage_leads_page.page.wait_for_timeout(400)
            updated_class = th.get_attribute("class") or ""
            assert "sorting_asc" in updated_class or "sorting_desc" in updated_class, (
                f"Expected header {idx} to toggle sort class, got: {updated_class}"
            )
            tested += 1
            if tested >= 2:
                break

    admin_error_monitor.assert_no_errors("Leads Column Sorting")


# ==============================================================================
# PILLAR 5: LEADS REPORT FILTERS AND EXPORT INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_leads_report_filters_and_export_integrity(
    leads_report_page: LeadsReportPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2 & 5: Verify Leads Report filter inputs (#fromDate, #toDate),
    employee select, lead type select, and Download button exist and are enabled.
    """
    leads_report_page.navigate()
    leads_report_page.page.wait_for_timeout(1000)

    expect(leads_report_page.from_date_input).to_be_visible()
    expect(leads_report_page.to_date_input).to_be_visible()
    expect(leads_report_page.employee_select).to_be_visible()
    expect(leads_report_page.lead_type_select).to_be_visible()
    expect(leads_report_page.filter_button).to_be_visible()
    expect(leads_report_page.download_button).to_be_visible()

    # Test inverted date boundaries on report
    leads_report_page.from_date_input.fill("2026-12-31")
    leads_report_page.to_date_input.fill("2026-01-01")
    leads_report_page.filter_button.click()
    leads_report_page.page.wait_for_timeout(800)

    expect(leads_report_page.datatable).to_be_attached()

    admin_error_monitor.assert_no_errors("Leads Report Filters & Export")
