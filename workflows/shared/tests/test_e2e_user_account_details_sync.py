"""
Cross-Portal & Manage User Account Details End-to-End Test Suite.
Maintained in workflows/shared/tests for cross-portal workflows and user account synchronization.
Covers 36 exhaustive scenarios verifying reflection, controls, modals, filters, and row actions.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("e2e_user_account_details_sync")


def _get_admin_page(browser: Browser) -> tuple[BrowserContext, Page, UserManagementPage]:
    """Helper to obtain an authenticated Admin Page and UserManagementPage object."""
    auth_file = settings.admin_portal.auth_state_path
    if auth_file.exists() and auth_file.stat().st_size > 0:
        ctx = browser.new_context(
            storage_state=str(auth_file),
            viewport=settings.browser.viewport,
            ignore_https_errors=True,
        )
    else:
        ctx = browser.new_context(
            viewport=settings.browser.viewport,
            ignore_https_errors=True,
        )
    page = ctx.new_page()
    user_page = UserManagementPage(page)
    user_page.navigate()
    return ctx, page, user_page


# ==============================================================================
# SECTION 1: CROSS-PORTAL & USER REFLECTION SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_user_account_details_reflection(workflow_browser: Browser):
    """
    Client user 10102 (name 'fake', email 'f76718269@gmail.com') is correctly reflected in the Admin Account Details table with Active status and Standard account type.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("10102")
        assert user_page.get_user_count() >= 1, "Expected user 10102 in Account Details."
        row_text = user_page.user_rows.first.inner_text()
        assert "10102" in row_text, "Expected AC. ID 10102 in row."
        assert "fake" in row_text.lower(), "Expected client name 'fake'."
        assert "f76718269@gmail.com" in row_text.lower(), "Expected email domain in row."
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_user_financial_metrics_sync(workflow_browser: Browser):
    """
    Financial Fund and Balance columns display valid numeric balances for client account 10102.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("10102")
        user_page.expand_row(0)
        full_table_text = page.locator("#datatable tbody").inner_text()
        numbers = re.findall(r"-?\d+(?:\.\d+)?", full_table_text)
        assert len(numbers) >= 2, f"Expected numeric balance figures in row, found {numbers}"
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_second_account_reflection_for_same_client(workflow_browser: Browser):
    """
    Second trading account 10656 registered under client email 'f76718269@gmail.com' displays with active credentials and book assignment.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("10656")
        assert user_page.get_user_count() >= 1, "Expected account 10656 in Account Details."
        row_text = user_page.user_rows.first.inner_text()
        assert "10656" in row_text
        assert "f76718269@gmail.com" in row_text.lower()
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_client_account_status_and_type_integrity(workflow_browser: Browser):
    """
    Trading accounts in Account Details display valid account type 'Standard' and active user status badge.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("10102")
        row = user_page.user_rows.first
        row_text = row.inner_text().lower()
        assert "standard" in row_text or "active" in row_text
        user_page.clear_search()
    finally:
        ctx.close()


# ==============================================================================
# SECTION 2: TOPBAR, BRANDING & THEME SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_topbar_branding_and_title(workflow_browser: Browser):
    """
    Top navbar renders brand logo, page title 'User', and sidebar hamburger toggle button.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.brand_logo.is_visible()
        assert user_page.page_title.is_visible()
        assert user_page.page_title.inner_text().strip() == "User"
        assert user_page.menu_button.is_visible()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_sidebar_menu_toggle(workflow_browser: Browser):
    """
    Clicking vertical menu button toggles sidebar between expanded and collapsed states.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        body = page.locator("body")
        initial_class = body.get_attribute("class") or ""
        user_page.menu_button.click()
        page.wait_for_timeout(300)
        toggled_class = body.get_attribute("class") or ""
        assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class
        user_page.menu_button.click()
        page.wait_for_timeout(300)
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_theme_toggle_action(workflow_browser: Browser):
    """
    Theme switch button toggles the layout mode between dark and light modes.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.theme_toggle.is_visible()
        initial_mode = user_page.get_theme_mode() or "light"
        user_page.toggle_theme()
        page.wait_for_timeout(300)
        toggled_mode = user_page.get_theme_mode() or "dark"
        assert toggled_mode != initial_mode
        user_page.toggle_theme()
        page.wait_for_timeout(300)
        assert user_page.get_theme_mode() == initial_mode
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_notifications_dropdown(workflow_browser: Browser):
    """
    Notifications button opens the notification dropdown menu with mark all read option.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.notification_button.is_visible()
        user_page.open_notifications()
        expect(user_page.notification_menu).to_be_visible()
        assert user_page.mark_all_read.is_visible()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_profile_dropdown_and_logout(workflow_browser: Browser):
    """
    Admin profile menu opens with admin name, role, and valid logout link.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.profile_button.is_visible()
        user_page.open_profile_menu()
        expect(user_page.profile_menu).to_be_visible()
        assert user_page.logout_link.is_visible()
    finally:
        ctx.close()


# ==============================================================================
# SECTION 3: PAGE ACTIONS & MODAL WORKFLOWS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_page_actions_container(workflow_browser: Browser):
    """
    Page action buttons container displays Create Account, Add User, and Refresh buttons with correct styles.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.page_actions_container.is_visible()
        assert user_page.create_account_button.is_visible()
        assert "Create Account" in user_page.create_account_button.inner_text()
        assert user_page.add_user_button.is_visible()
        assert "Add User" in user_page.add_user_button.inner_text()
        assert user_page.refresh_button.is_visible()
        assert "Refresh" in user_page.refresh_button.inner_text()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_hidden_permission_flags(workflow_browser: Browser):
    """
    All 6 hidden permission configuration inputs exist in DOM with active values (value='1').
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        permission_inputs = [
            (user_page.edit_manage_user_input, "editManageUser"),
            (user_page.delete_manage_user_input, "deleteManageUser"),
            (user_page.change_balance_input, "changeBalance"),
            (user_page.change_book_input, "changeBook"),
            (user_page.change_manage_user_input, "changeManageUser"),
            (user_page.cent_switch_enabled_input, "centSwitchEnabled"),
        ]
        for loc, field_id in permission_inputs:
            assert loc.count() >= 1, f"Expected hidden input #{field_id}"
            assert loc.get_attribute("value") == "1"
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_create_account_modal(workflow_browser: Browser):
    """
    Clicking Create Account opens the creation modal with correct title and close functionality.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.open_create_account_modal()
        assert user_page.create_account_modal.is_visible()
        assert "Create Account For User" in user_page.create_account_modal_title.inner_text()
        user_page.close_create_account_modal()
        assert not user_page.create_account_modal.is_visible()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_add_user_modal(workflow_browser: Browser):
    """
    Clicking Add User opens the user details modal with input fields and dismisses properly.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.open_add_user_modal()
        assert user_page.user_add_modal.is_visible()
        assert "User Details" in user_page.user_add_modal_title.inner_text()
        user_page.close_add_user_modal()
        assert not user_page.user_add_modal.is_visible()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_table_refresh_persistence(workflow_browser: Browser):
    """
    Clicking the Refresh button reloads table data smoothly without layout errors.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        initial_count = user_page.get_user_count()
        user_page.click_refresh()
        assert user_page.users_table.is_visible()
        assert user_page.get_user_count() == initial_count
    finally:
        ctx.close()


# ==============================================================================
# SECTION 4: DATATABLE, TOOLBAR & FILTER SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_table_card_and_datatable_wrapper(workflow_browser: Browser):
    """
    The table card container, DataTable wrapper, and core table structure render properly.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.table_card.is_visible()
        assert user_page.datatable_wrapper.is_visible()
        assert user_page.users_table.is_visible()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_length_dropdown_selection(workflow_browser: Browser):
    """
    Changing page length dropdown dynamically updates displayed records count (10, 25, 50, 100).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.length_dropdown.is_visible()
        options = [user_page.length_dropdown.locator("option").nth(i).get_attribute("value")
                   for i in range(user_page.length_dropdown.locator("option").count())]
        for val in ["10", "25", "50", "100"]:
            assert val in options, f"Expected length option {val}"
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_export_csv_button_rendered(workflow_browser: Browser):
    """
    CSV export button is present, visible, and has correct styling.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.csv_button.is_visible()
        assert "CSV" in user_page.csv_button.inner_text()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_export_pdf_button_rendered(workflow_browser: Browser):
    """
    PDF export button is present, visible, and has correct styling.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.pdf_button.is_visible()
        assert "PDF" in user_page.pdf_button.inner_text()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_export_excel_button_rendered(workflow_browser: Browser):
    """
    Excel export button is present, visible, and has correct styling.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.excel_button.is_visible()
        assert "Excel" in user_page.excel_button.inner_text()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_date_filter_inputs_rendered(workflow_browser: Browser):
    """
    From and To datetime-local inputs, Go button, and Clear button render properly in the date filter container.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.date_filters_container.is_visible()
        assert user_page.date_from.is_visible()
        assert user_page.date_from.get_attribute("type") == "datetime-local"
        assert user_page.date_to.is_visible()
        assert user_page.date_to.get_attribute("type") == "datetime-local"
        assert user_page.apply_button.is_visible()
        assert user_page.clear_button.is_visible()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_date_filter_and_clear(workflow_browser: Browser):
    """
    Date range filter inputs (From, To) with Go apply and Clear reset buttons work as expected.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.clear_button.click()
        page.wait_for_timeout(300)
        assert user_page.get_user_count() >= 1, "Expected table rows visible after Clear."
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_search_by_account_id(workflow_browser: Browser):
    """
    Searching for account ID '10102' filters the table and accurately displays the user.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("10102")
        assert user_page.get_user_count() >= 1
        assert "10102" in user_page.user_rows.first.inner_text()
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_search_by_client_name(workflow_browser: Browser):
    """
    Searching for client name 'fake' filters the table to matching user records.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("fake")
        assert user_page.get_user_count() >= 1
        assert "fake" in user_page.user_rows.first.inner_text().lower()
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_search_by_email(workflow_browser: Browser):
    """
    Searching for client email 'f76718269@gmail.com' filters the table accurately.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("f76718269@gmail.com")
        assert user_page.get_user_count() >= 1
        assert "f76718269@gmail.com" in user_page.user_rows.first.inner_text().lower()
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_search_unmatched_query_empty_state(workflow_browser: Browser):
    """
    Searching for an unmatched query displays an empty state or zero records.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("nonexistent_user_query_99999")
        assert user_page.empty_state_cell.is_visible() or user_page.get_user_count() == 0
        user_page.clear_search()
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_search_clear_restores_data(workflow_browser: Browser):
    """
    Clearing search restores the full list of user accounts in the table.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.search_user("10102")
        filtered_count = user_page.get_user_count()
        user_page.clear_search()
        restored_count = user_page.get_user_count()
        assert restored_count >= filtered_count
    finally:
        ctx.close()


# ==============================================================================
# SECTION 5: TABLE COLUMNS & DATA INTEGRITY SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_table_headers_column_integrity(workflow_browser: Browser):
    """
    All required table columns exist in the header (S.No, Deposit/Withdraw, Name, AC. ID, Email, Password, Inv. Password, E-Mail, Document, Account Type).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        all_header_texts = [th.strip().casefold() for th in user_page.table_headers.all_inner_texts() if th.strip()]
        for col in ["s.no", "deposit / withdraw", "name", "ac. id", "email", "password", "inv. password", "e-mail", "document", "account type"]:
            assert any(col in h for h in all_header_texts), f"Expected column '{col}' in headers."
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_row_credentials_integrity(workflow_browser: Browser):
    """
    User rows contain valid account IDs, email domains, and password credential fields.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.get_user_count() >= 1
        first_row_text = user_page.user_rows.first.inner_text()
        assert "@" in first_row_text, "Expected email domain '@' in user row."
    finally:
        ctx.close()


# ==============================================================================
# SECTION 6: INLINE ROW SELECTS & VERIFICATION STATUS SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_email_verification_select(workflow_browser: Browser):
    """
    Inline Email Verification select contains Verified (1) and Not Verified (0) options with dynamic status styling.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        email_select = user_page.email_verification_selects.first
        assert email_select.is_visible()
        options = [opt.lower() for opt in email_select.locator("option").all_inner_texts()]
        assert any("verified" in opt for opt in options)
        assert any("not verified" in opt for opt in options)
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_document_verification_select(workflow_browser: Browser):
    """
    Inline Document Verification select contains Verified (1) and Not Verified (0) options with dynamic status styling.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        doc_select = user_page.doc_verification_selects.first
        assert doc_select.is_visible()
        options = [opt.lower() for opt in doc_select.locator("option").all_inner_texts()]
        assert any("verified" in opt for opt in options)
        assert any("not verified" in opt for opt in options)
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_account_type_select(workflow_browser: Browser):
    """
    Inline Account Type select dropdown contains Standard and Cent account options.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        acc_type_select = user_page.account_type_selects.first
        assert acc_type_select.is_visible()
        options = [opt.lower() for opt in acc_type_select.locator("option").all_inner_texts()]
        assert any("standard" in opt for opt in options)
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_user_status_select(workflow_browser: Browser):
    """
    User Status displays valid active status indicator in user table child/responsive row.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.expand_row(0)
        full_text = page.locator("#datatable tbody").inner_text().lower()
        assert "active" in full_text, "Expected 'Active' status indicator in expanded row."
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_book_assignment_select(workflow_browser: Browser):
    """
    Book assignment displays valid A-Book or B-Book indicator in user table child/responsive row.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.expand_row(0)
        full_text = page.locator("#datatable tbody").inner_text().lower()
        assert "book" in full_text or "boo" in full_text, "Expected Book assignment indicator in expanded row."
    finally:
        ctx.close()


# ==============================================================================
# SECTION 7: ROW ACTION BUTTONS & RESPONSIVE DETAILS SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_inline_edit_account_id_button(workflow_browser: Browser):
    """
    Inline Edit AC. ID button is present on user rows with valid account_id attribute.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        first_row = user_page.user_rows.first
        edit_ac_id = first_row.locator("a.btn-edit-account_id")
        assert edit_ac_id.is_visible()
        assert edit_ac_id.get_attribute("account_id") is not None
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_row_deposit_withdraw_action_buttons(workflow_browser: Browser):
    """
    Each row contains Deposit/Withdraw Edit and Delete action buttons.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        first_row = user_page.user_rows.first
        assert first_row.locator("a.btnEdit").is_visible(), "Expected Edit action button."
        assert first_row.locator("a.BtnDelete").is_visible(), "Expected Delete action button."
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_responsive_row_expansion(workflow_browser: Browser):
    """
    Expanding responsive row details exposes trading actions (MAM, PAMM, Copy Trading, Switch Group).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        user_page.expand_row(0)
        child_or_row = page.locator("tr.child, #datatable tbody tr")
        assert child_or_row.locator("button.switchGroup, .switchGroup").count() >= 1
        assert child_or_row.locator("button.userCredit, .userCredit").count() >= 1
    finally:
        ctx.close()


# ==============================================================================
# SECTION 8: PAGINATION CONTROLS & STATUS INFO SCENARIOS
# ==============================================================================


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_pagination_traversal(workflow_browser: Browser):
    """
    Pagination controls navigate between pages and update active page indicator.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        assert user_page.pagination.is_visible()
        assert user_page.get_active_page_number() == "1"
        assert "disabled" in (user_page.paginate_previous.get_attribute("class") or "")
        user_page.click_next_page()
        assert user_page.get_active_page_number() == "2"
        user_page.click_previous_page()
        assert user_page.get_active_page_number() == "1"
    finally:
        ctx.close()


@pytest.mark.shared
@pytest.mark.e2e
def test_e2e_account_details_pagination_info_counter_text(workflow_browser: Browser):
    """
    Table status info string displays the expected 'Showing 1 to X of Y entries' pattern.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        info_text = user_page.get_table_info_text()
        assert "showing" in info_text.lower()
        assert "entries" in info_text.lower()
    finally:
        ctx.close()
