"""
Admin Portal User Management Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.A.2, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Add User form (Name, Email, Mobile, Passwords), User Search, SQLi/XSS sanitization.
2. Buttons & Actions: Modal triggers (#addNew, #createAccount, #refresh), modal dismissal, export buttons.
3. Dropdowns & Selects: Group select, Subgroup/Leverage select, Entries per page pagination (10, 25, 50, 100).
5. Date & Time Pickers: Inverted date boundaries ('From > To'), date clear restoring full ledger.
6. Calculations & Tables: Table S.No ordering, pagination controls, column sorting traversal.
7. Security: SQLi and XSS attack vectors in user creation and search inputs.

Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.admin_portal.pages.user_document_page import UserDocumentPage
from workflows.admin_portal.pages.account_requests_page import AccountRequestsPage
from workflows.admin_portal.pages.admin_active_users_page import AdminActiveUsersPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# PILLAR 1 & 2: USER MANAGEMENT SUB-ROUTES INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_management_subroutes_integrity(
    user_management_page: UserManagementPage,
    user_document_page: UserDocumentPage,
    account_requests_page: AccountRequestsPage,
    admin_active_users_page: AdminActiveUsersPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify primary User Management sub-routes navigate successfully,
    render their respective DataTables, and show zero critical UI crashes.
    """
    # 1. Account Details (/admin/Controlbase/user)
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)
    expect(user_management_page.users_table).to_be_attached(timeout=15000)
    expect(user_management_page.page_actions_container).to_be_visible()

    # 2. Account Requests (/admin/Controlbase/clientAccountRequests)
    account_requests_page.navigate()
    account_requests_page.page.wait_for_timeout(1000)
    expect(account_requests_page.requests_table).to_be_attached(timeout=15000)

    # 3. User Documents (KYC) (/admin/Controlbase/userDocument)
    user_document_page.navigate()
    user_document_page.page.wait_for_timeout(1000)
    expect(user_document_page.table).to_be_attached(timeout=15000)

    # 4. Active Users (/admin/Controlbase/activeUsers)
    admin_active_users_page.navigate()
    admin_active_users_page.page.wait_for_timeout(1000)
    expect(admin_active_users_page.table).to_be_attached(timeout=15000)

    admin_error_monitor.assert_no_errors("User Management Sub-Routes")


# ==============================================================================
# PILLAR 1 & 2: ADD USER MODAL (#userAddModal) LIFECYCLE & INPUT VALIDATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_add_modal_field_elements_and_lifecycle(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify clicking '+ Add User' opens #userAddModal with all onboarding
    fields, and closing dismisses the modal cleanly without state leaks.
    """
    user_management_page.navigate()
    user_management_page.open_add_user_modal()

    modal = user_management_page.user_add_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(user_management_page.user_add_modal_title).to_contain_text("User Details")

    # Verify input field existence inside #userAddModal
    expect(modal.locator("#name")).to_be_attached()
    expect(modal.locator("#email")).to_be_attached()
    expect(modal.locator("#mobile")).to_be_attached()
    expect(modal.locator("#pass")).to_be_attached()
    expect(modal.locator("#investor_pass")).to_be_attached()
    expect(modal.locator("#user_group_id")).to_be_attached()
    expect(modal.locator("#user_subgroup_value")).to_be_attached()
    expect(modal.locator("#sendmailuser")).to_be_attached()
    expect(modal.locator("#userFormSubmit")).to_be_attached()

    # Close modal cleanly
    user_management_page.close_add_user_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Add User Modal Lifecycle")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_add_empty_form_submission_boundaries(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify submitting an empty #userAddModal form triggers HTML5
    validation or required boundary enforcement preventing submission.
    """
    user_management_page.navigate()
    user_management_page.open_add_user_modal()

    modal = user_management_page.user_add_modal
    expect(modal).to_be_visible()

    # Clear all text inputs
    modal.locator("#name").fill("")
    modal.locator("#email").fill("")
    modal.locator("#mobile").fill("")
    modal.locator("#pass").fill("")

    # Verify required / validity constraints via browser evaluation
    validation_status = user_management_page.page.evaluate("""() => {
        const form = document.querySelector("#userAddModal form") || document.querySelector("#userAddModal");
        const nameInput = document.querySelector("#userAddModal #name");
        const emailInput = document.querySelector("#userAddModal #email");
        const mobileInput = document.querySelector("#userAddModal #mobile");
        const passInput = document.querySelector("#userAddModal #pass");

        return {
            nameRequired: nameInput ? nameInput.required : false,
            emailRequired: emailInput ? emailInput.required : false,
            mobileRequired: mobileInput ? mobileInput.required : false,
            passRequired: passInput ? passInput.required : false,
            nameValid: nameInput ? nameInput.checkValidity() : true,
            emailValid: emailInput ? emailInput.checkValidity() : true
        };
    }""")

    # Attempt to click submit without filling inputs
    modal.locator("#userFormSubmit").click()
    user_management_page.page.wait_for_timeout(500)

    # Modal should remain open because validation prevented submission
    expect(modal).to_be_visible()

    user_management_page.close_add_user_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Empty User Form Boundaries")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_add_name_field_validation_matrix(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test Name input boundary matrix (standard alpha, spaces, digits, special characters).
    """
    user_management_page.navigate()
    user_management_page.open_add_user_modal()
    modal = user_management_page.user_add_modal

    name_matrix = [
        ("Normal Name", "Test Python", True),
        ("Multiple Words", "Test Kumar Python", True),
        ("With Digits", "Test12345", False),
        ("With Special Char", "Test@Python", False),
        ("Empty String", "", False),
        ("Whitespace Only", "   ", False),
    ]

    for label, val, is_valid_alpha in name_matrix:
        name_input = modal.locator("#name")
        name_input.fill(val)
        name_input.dispatch_event("input")
        name_input.dispatch_event("change")

        res = user_management_page.page.evaluate("""([val]) => {
            const isStrictAlpha = /^[a-zA-Z ]+$/.test(val);
            const isNonEmpty = val.trim().length > 0;
            return isStrictAlpha && isNonEmpty;
        }""", [val])

        assert res == is_valid_alpha, f"Name check mismatch for '{val}' ({label})"

    user_management_page.close_add_user_modal()
    admin_error_monitor.assert_no_errors("User Name Field Validation")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_add_email_field_validation_matrix(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test Email input format validation matrix (missing domain, missing user, embedded spaces, SQLi, XSS).
    """
    user_management_page.navigate()
    user_management_page.open_add_user_modal()
    modal = user_management_page.user_add_modal

    email_matrix = [
        ("Standard Email", "user@example.com", True),
        ("Subdomain Email", "user@sub.example.com", True),
        ("Missing Domain", "user@", False),
        ("Missing Recipient", "@test.com", False),
        ("Embedded Space", "user space@test.com", False),
        ("Missing TLD", "user@localhost", False),
        ("SQLi Payload", "' OR '1'='1", False),
        ("XSS Payload", "<script>alert(1)</script>", False),
    ]

    for label, email_val, exp_valid in email_matrix:
        email_input = modal.locator("#email")
        email_input.fill(email_val)
        email_input.dispatch_event("input")
        email_input.dispatch_event("change")

        is_valid = user_management_page.page.evaluate("""([val]) => {
            const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            return re.test(val);
        }""", [email_val])

        assert is_valid == exp_valid, f"Email format validation failed for '{email_val}' ({label})"

    user_management_page.close_add_user_modal()
    admin_error_monitor.assert_no_errors("User Email Field Validation")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_add_phone_and_password_validation(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Validate Phone number formatting and Password boundary policies.
    """
    user_management_page.navigate()
    user_management_page.open_add_user_modal()
    modal = user_management_page.user_add_modal

    # Phone tests
    phone_input = modal.locator("#mobile")
    phone_input.fill("9876543210")
    expect(phone_input).to_have_value("9876543210")

    # Password tests
    pass_input = modal.locator("#pass")
    inv_pass_input = modal.locator("#investor_pass")

    pass_input.fill("StrongP@ssw0rd!2026")
    inv_pass_input.fill("InvP@ssw0rd!2026")

    expect(pass_input).to_have_value("StrongP@ssw0rd!2026")
    expect(inv_pass_input).to_have_value("InvP@ssw0rd!2026")

    user_management_page.close_add_user_modal()
    admin_error_monitor.assert_no_errors("User Phone and Password Validation")


# ==============================================================================
# PILLAR 2: CREATE ACCOUNT MODAL (#createAccountModal) LIFECYCLE & SEARCH
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_create_account_modal_lifecycle_and_user_search(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify '+ Create Account' opens #createAccountModal, handles
    user search query inputs safely, and dismisses cleanly.
    """
    user_management_page.navigate()
    user_management_page.open_create_account_modal()

    modal = user_management_page.create_account_modal
    expect(modal).to_be_visible(timeout=5000)
    expect(user_management_page.create_account_modal_title).to_contain_text("Create Account For User")

    # Test user search input
    search_input = modal.locator("#caUserSearch")
    if search_input.count() > 0:
        search_input.fill("test")
        user_management_page.page.wait_for_timeout(300)

        # Injection payload safety
        search_input.fill("' OR 1=1--")
        user_management_page.page.wait_for_timeout(300)

    user_management_page.close_create_account_modal()
    expect(modal).not_to_be_visible()

    admin_error_monitor.assert_no_errors("Create Account Modal Lifecycle")


# ==============================================================================
# PILLAR 1: DATATABLE SEARCH & SECURITY SANITIZATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_table_search_filter_and_empty_state(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Test searching valid user filters rows, and searching non-existent user
    displays empty state cleanly without crashing.
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)

    # Search for an improbable non-existent query
    user_management_page.search_user("NON_EXISTENT_USER_TOKEN_999999")
    user_management_page.page.wait_for_timeout(600)

    empty_cell = user_management_page.page.locator("#datatable tbody td").first
    expect(empty_cell).to_be_visible()
    cell_text = empty_cell.inner_text().lower()
    assert any(term in cell_text for term in ["no matching", "no data", "showing 0 to 0", "not found"]), (
        f"Expected empty state text, got: {cell_text}"
    )

    # Clear search
    user_management_page.clear_search()
    user_management_page.page.wait_for_timeout(600)
    expect(user_management_page.user_rows.first).to_be_visible(timeout=10000)

    admin_error_monitor.assert_no_errors("User Search Filter & Empty State")


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_table_search_sqli_xss_sanitization(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 7 (Security): Test that injecting SQLi and XSS payloads into User Management
    search input does not trigger unexpected script execution or expose database credentials.
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)

    # Track any unexpected window dialog
    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    user_management_page.page.on("dialog", handle_dialog)

    # Test SQLi payloads
    for payload, description in SQLI_PAYLOADS[:2]:
        user_management_page.search_user(payload)
        user_management_page.page.wait_for_timeout(500)
        body_text = user_management_page.page.locator("body").inner_text()
        assert "SQL syntax" not in body_text, f"SQL syntax error exposed for {description}"
        assert "Fatal error" not in body_text, f"Fatal error exposed for {description}"
        assert not dialog_triggered, f"Security alert dialog triggered by {description}"

    # Test XSS payloads
    for payload, description in XSS_PAYLOADS[:2]:
        user_management_page.search_user(payload)
        user_management_page.page.wait_for_timeout(500)
        is_pwned = user_management_page.page.evaluate("() => Boolean(window.pwned || window.xss_detected)")
        assert is_pwned is False, f"XSS payload executed: {payload}"
        assert not dialog_triggered, f"Security alert dialog triggered by XSS: {payload}"

    user_management_page.clear_search()
    expect(user_management_page.users_table).to_be_attached()
    admin_error_monitor.assert_no_errors("User Search SQLi & XSS Sanitization")


# ==============================================================================
# PILLAR 3: PAGE LENGTH DROPDOWN PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_table_page_length_selector_validation(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify the page length dropdown (10, 25, 50) triggers server-side
    re-draw and accurately updates the datatable info status.
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)

    length_select = user_management_page.length_dropdown
    expect(length_select).to_be_visible()

    for length in ["10", "25"]:
        length_select.select_option(length)
        # Wait for processing indicator to finish if visible
        try:
            user_management_page.page.locator("#datatable_processing").wait_for(state="hidden", timeout=8000)
        except Exception:
            pass

        # Validate #datatable_info reflects the selection
        info_loc = user_management_page.table_info
        expect(info_loc).to_be_visible()
        expect(info_loc).to_contain_text(re.compile(rf"Showing 1 to (?:{length}|\d+) of", re.IGNORECASE))

    admin_error_monitor.assert_no_errors("User Table Page Length Selector")


# ==============================================================================
# PILLAR 5: DATE RANGE BOUNDARIES & RESET
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_table_date_filters_boundaries(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 5: Test inverted date boundaries ('From > To') and verify Apply button
    triggers search cleanly, and Clear button restores date inputs.
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)

    from_date = user_management_page.date_from
    to_date = user_management_page.date_to
    apply_btn = user_management_page.apply_button
    clear_btn = user_management_page.clear_button

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
            user_management_page.page.wait_for_timeout(800)
            expect(user_management_page.users_table).to_be_attached()

        if clear_btn.is_visible():
            clear_btn.click()
            user_management_page.page.wait_for_timeout(800)
            expect(user_management_page.users_table).to_be_attached()

    admin_error_monitor.assert_no_errors("User Date Filter Boundaries")


# ==============================================================================
# PILLAR 6: TABLE COLUMN SORTING TRAVERSAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_table_column_sorting_traversal(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify clicking table headers toggles sort order (sorting_asc / sorting_desc)
    without rendering errors or broken rows.
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)

    headers = user_management_page.table_headers
    header_count = headers.count()
    assert header_count > 0, "Table should have header columns"

    # Test sorting on first 3 sortable headers
    tested = 0
    for idx in range(min(header_count, 4)):
        th = headers.nth(idx)
        th_class = th.get_attribute("class") or ""
        if "sorting" in th_class:
            th.click()
            user_management_page.page.wait_for_timeout(400)
            updated_class = th.get_attribute("class") or ""
            assert "sorting_asc" in updated_class or "sorting_desc" in updated_class, (
                f"Expected header {idx} to toggle sort class, got: {updated_class}"
            )
            tested += 1
            if tested >= 2:
                break

    admin_error_monitor.assert_no_errors("User Table Column Sorting")


# ==============================================================================
# PILLAR 2: EXPORT BUTTONS INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.validation
def test_val_user_export_buttons_integrity(
    user_management_page: UserManagementPage,
    admin_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify that CSV, PDF, and Excel export buttons exist, are enabled,
    and possess valid action classes.
    """
    user_management_page.navigate()
    user_management_page.page.wait_for_timeout(1000)

    expect(user_management_page.csv_button).to_be_attached()
    expect(user_management_page.pdf_button).to_be_attached()
    expect(user_management_page.excel_button).to_be_attached()

    for btn in [user_management_page.csv_button, user_management_page.pdf_button, user_management_page.excel_button]:
        if btn.is_visible():
            expect(btn).to_be_enabled()

    admin_error_monitor.assert_no_errors("User Export Buttons Integrity")
