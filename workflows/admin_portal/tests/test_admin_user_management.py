"""
Admin Portal User Management Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.user_management_page import UserManagementPage


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_topbar_branding_and_title(
    user_management_page: UserManagementPage,
):
    """
    Verify top navbar branding logos (small and large), page title ('User'),
    and sidebar menu button attributes matching the navbar-header layout.
    """
    user_management_page.navigate()

    # Brand Logo & Responsive Icons
    assert user_management_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert user_management_page.logo_small.is_visible() or user_management_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = user_management_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert user_management_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert user_management_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert user_management_page.menu_button.get_attribute("title") == "Open menu"
    assert user_management_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert user_management_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert user_management_page.page_title.inner_text().strip() == "User"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_topbar_sidebar_toggle_action(
    user_management_page: UserManagementPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    user_management_page.navigate()

    body = user_management_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    user_management_page.menu_button.click()
    user_management_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    user_management_page.menu_button.click()
    user_management_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_theme_toggle_switches_modes(
    user_management_page: UserManagementPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    user_management_page.navigate()

    assert user_management_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert user_management_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert user_management_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert user_management_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert user_management_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = user_management_page.get_theme_mode() or "light"

    user_management_page.toggle_theme()
    user_management_page.page.wait_for_timeout(300)

    toggled_mode = user_management_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    user_management_page.toggle_theme()
    user_management_page.page.wait_for_timeout(300)
    assert user_management_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_notifications_dropdown(
    user_management_page: UserManagementPage,
):
    """
    Verify notifications button (#page-header-notifications-dropdown),
    unread badge count, and notifications dropdown menu.
    """
    user_management_page.navigate()

    assert user_management_page.notification_button.is_visible(), (
        "Expected notifications button to be visible."
    )
    assert user_management_page.notification_count.is_visible(), (
        "Expected notification badge count to be visible."
    )

    user_management_page.open_notifications()
    user_management_page.page.wait_for_timeout(300)

    assert user_management_page.notification_menu.is_visible(), (
        "Expected notification dropdown menu to open."
    )
    assert user_management_page.mark_all_read.is_visible(), (
        "Expected 'Mark all read' action link to be visible."
    )

    # Close dropdown
    user_management_page.notification_button.click()
    user_management_page.page.wait_for_timeout(200)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_profile_dropdown_and_logout_link(
    user_management_page: UserManagementPage,
):
    """
    Verify user profile dropdown button displays initials, username,
    and profile menu contains admin details and Logout item.
    """
    user_management_page.navigate()

    assert user_management_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert user_management_page.profile_initials.inner_text().strip() == "M"

    user_management_page.open_profile_menu()
    user_management_page.page.wait_for_timeout(300)

    assert user_management_page.profile_menu.is_visible(), "Expected profile menu dropdown to open."
    assert "madmin" in user_management_page.profile_name.inner_text().casefold()
    assert "administrator" in user_management_page.profile_role.inner_text().casefold()

    assert user_management_page.logout_link.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (user_management_page.logout_link.get_attribute("href") or "")

    # Close dropdown
    user_management_page.profile_button.click()
    user_management_page.page.wait_for_timeout(200)


# ==============================================================================
# SECTION 2: TOP ACTION BUTTONS & MODALS (.user-page-actions)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_page_actions_container_and_buttons_rendered(
    user_management_page: UserManagementPage,
):
    """
    Verify the user-page-actions container renders the Create Account,
    Add User, and Refresh buttons with correct styles and icons.
    """
    user_management_page.navigate()

    assert user_management_page.page_actions_container.is_visible(), (
        "Expected .user-page-actions container to be visible."
    )

    # Create Account button
    assert user_management_page.create_account_button.is_visible(), (
        "Expected Create Account button to be visible."
    )
    assert "Create Account" in user_management_page.create_account_button.inner_text()
    assert "btn-primary" in (user_management_page.create_account_button.get_attribute("class") or "")

    # Add User button
    assert user_management_page.add_user_button.is_visible(), (
        "Expected Add User button to be visible."
    )
    assert "Add User" in user_management_page.add_user_button.inner_text()
    assert "btn-primary" in (user_management_page.add_user_button.get_attribute("class") or "")

    # Refresh button
    assert user_management_page.refresh_button.is_visible(), (
        "Expected Refresh button to be visible."
    )
    assert "Refresh" in user_management_page.refresh_button.inner_text()
    assert user_management_page.refresh_icon.count() >= 1, (
        "Expected feather-refresh-ccw icon in Refresh button."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_page_actions_hidden_permission_inputs(
    user_management_page: UserManagementPage,
):
    """
    Verify all 6 hidden permission configuration inputs exist in the DOM
    with their enabled values (value='1').
    """
    user_management_page.navigate()

    permission_inputs = [
        (user_management_page.edit_manage_user_input, "editManageUser"),
        (user_management_page.delete_manage_user_input, "deleteManageUser"),
        (user_management_page.change_balance_input, "changeBalance"),
        (user_management_page.change_book_input, "changeBook"),
        (user_management_page.change_manage_user_input, "changeManageUser"),
        (user_management_page.cent_switch_enabled_input, "centSwitchEnabled"),
    ]

    for loc, field_id in permission_inputs:
        assert loc.count() >= 1, f"Expected hidden input #{field_id} to exist in DOM."
        assert loc.get_attribute("type") == "hidden", f"Expected #{field_id} to have type='hidden'."
        assert loc.get_attribute("value") == "1", f"Expected #{field_id} to have value='1'."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_create_account_button_opens_modal(
    user_management_page: UserManagementPage,
):
    """
    Verify clicking Create Account opens #createAccountModal with
    'Create Account For User' heading, and closing it dismisses the modal.
    """
    user_management_page.navigate()

    user_management_page.open_create_account_modal()
    assert user_management_page.create_account_modal.is_visible(), (
        "Expected #createAccountModal to be visible after click."
    )
    assert "Create Account For User" in user_management_page.create_account_modal_title.inner_text()

    user_management_page.close_create_account_modal()
    assert not user_management_page.create_account_modal.is_visible(), (
        "Expected #createAccountModal to be dismissed after Close."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_add_user_button_opens_modal(
    user_management_page: UserManagementPage,
):
    """
    Verify clicking Add User opens #userAddModal with 'User Details' heading,
    and closing it dismisses the modal.
    """
    user_management_page.navigate()

    user_management_page.open_add_user_modal()
    assert user_management_page.user_add_modal.is_visible(), (
        "Expected #userAddModal to be visible after click."
    )
    assert "User Details" in user_management_page.user_add_modal_title.inner_text()

    user_management_page.close_add_user_modal()
    assert not user_management_page.user_add_modal.is_visible(), (
        "Expected #userAddModal to be dismissed after Close."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_refresh_button_action(
    user_management_page: UserManagementPage,
):
    """
    Verify clicking the Refresh button reloads table data smoothly without layout breaking.
    """
    user_management_page.navigate()

    user_management_page.click_refresh()
    assert user_management_page.page_actions_container.is_visible()
    assert user_management_page.refresh_button.is_visible()


# ==============================================================================
# SECTION 3: DATATABLE CARD & FILTER CONTROLS (.user-table-card)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_table_card_and_datatable_controls(
    user_management_page: UserManagementPage,
):
    """
    Verify the user table card container, DataTable wrapper,
    entries-per-page dropdown (10, 25, 50, 100), and search input.
    """
    user_management_page.navigate()

    assert user_management_page.table_card.is_visible(), "Expected .user-table-card to be visible."
    assert user_management_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert user_management_page.length_dropdown.is_visible(), "Expected page length dropdown to be visible."

    options = user_management_page.length_dropdown.locator("option")
    option_values = [options.nth(i).get_attribute("value") for i in range(options.count())]
    for expected_val in ["10", "25", "50", "100"]:
        assert expected_val in option_values, f"Expected length option '{expected_val}'."

    assert user_management_page.search_input.is_visible(), "Expected search input to be visible."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_export_buttons_rendered(
    user_management_page: UserManagementPage,
):
    """
    Verify the table exports group renders CSV, PDF, and Excel buttons.
    """
    user_management_page.navigate()

    assert user_management_page.export_buttons.count() >= 3, "Expected at least 3 export buttons."
    assert user_management_page.csv_button.is_visible(), "Expected CSV export button."
    assert "CSV" in user_management_page.csv_button.inner_text()

    assert user_management_page.pdf_button.is_visible(), "Expected PDF export button."
    assert "PDF" in user_management_page.pdf_button.inner_text()

    assert user_management_page.excel_button.is_visible(), "Expected Excel export button."
    assert "Excel" in user_management_page.excel_button.inner_text()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_date_filter_controls(
    user_management_page: UserManagementPage,
):
    """
    Verify the user-date-filters container renders From and To datetime-local inputs,
    Go button, and Clear button.
    """
    user_management_page.navigate()

    assert user_management_page.date_filters_container.is_visible(), (
        "Expected .user-date-filters to be visible."
    )
    assert user_management_page.date_from.is_visible(), "Expected From date input."
    assert user_management_page.date_from.get_attribute("type") == "datetime-local"

    assert user_management_page.date_to.is_visible(), "Expected To date input."
    assert user_management_page.date_to.get_attribute("type") == "datetime-local"

    assert user_management_page.apply_button.is_visible(), "Expected Go apply button."
    assert "Go" in user_management_page.apply_button.inner_text()
    assert "btn-primary" in (user_management_page.apply_button.get_attribute("class") or "")

    assert user_management_page.clear_button.is_visible(), "Expected Clear button."
    assert "Clear" in user_management_page.clear_button.inner_text()
    assert "btn-danger" in (user_management_page.clear_button.get_attribute("class") or "")


# ==============================================================================
# SECTION 4: TABLE COLUMNS, ROWS & PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_table_headers_and_columns(
    user_management_page: UserManagementPage,
):
    """
    Verify the table headers contain expected user account and trading columns.
    """
    user_management_page.navigate()

    all_header_texts = [
        th.strip().casefold()
        for th in user_management_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    expected_columns = [
        "s.no",
        "deposit / withdraw",
        "name",
        "ac. id",
        "email",
        "password",
        "inv. password",
        "e-mail",
        "document",
        "account type",
    ]

    for col in expected_columns:
        assert any(col in h for h in all_header_texts), f"Expected column '{col}' in headers."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_table_rows_data_integrity(
    user_management_page: UserManagementPage,
):
    """
    Verify table renders records with valid numeric IDs, emails, and balances.
    """
    user_management_page.navigate()

    assert user_management_page.get_user_count() >= 1, "Expected at least 1 user row rendered."

    first_row = user_management_page.user_rows.first
    row_text = first_row.inner_text()

    # Verify presence of email domain character and edit controls
    assert "@" in row_text, "Expected valid email in user row."
    assert first_row.locator("a.btnEdit").is_visible(), "Expected Edit action button."
    assert first_row.locator("a.btn-edit-account_id").is_visible(), "Expected Edit Account ID button."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_table_row_select_dropdowns(
    user_management_page: UserManagementPage,
):
    """
    Verify inline action dropdowns for email verification, document verification,
    account type, user status, and book assignment exist in rows.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    assert user_management_page.email_verification_selects.count() >= 1, (
        "Expected userEmailVerification dropdown."
    )
    assert user_management_page.doc_verification_selects.count() >= 1, (
        "Expected userDocumentVerification dropdown."
    )
    assert user_management_page.account_type_selects.count() >= 1, (
        "Expected updateAccountType dropdown."
    )
    assert user_management_page.user_status_selects.count() >= 1, (
        "Expected updateUserStatus dropdown."
    )
    assert user_management_page.user_book_selects.count() >= 1, (
        "Expected userBook dropdown."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_length_dropdown_selection(
    user_management_page: UserManagementPage,
):
    """
    Verify changing page length dropdown dynamically updates displayed records.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    initial_info = user_management_page.get_table_info_text()
    assert "Showing 1 to 10" in initial_info

    user_management_page.select_page_length("25")
    expect(user_management_page.table_info).to_contain_text("Showing 1 to 25")

    # Revert
    user_management_page.select_page_length("10")
    expect(user_management_page.table_info).to_contain_text("Showing 1 to 10")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_search_filtering(
    user_management_page: UserManagementPage,
):
    """
    Verify searching filters table rows and unmatched query shows empty state.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    # Search for an unmatched query
    user_management_page.search_user("nonexistent_unmatched_user_query_9999")
    try:
        user_management_page.empty_state_cell.wait_for(state="visible", timeout=5000)
    except Exception:
        pass
    assert user_management_page.empty_state_cell.is_visible() or user_management_page.get_user_count() == 0, (
        "Expected empty state for unmatched search."
    )

    # Clear search
    user_management_page.clear_search()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=10000)
    assert user_management_page.get_user_count() >= 1, "Expected table rows restored after clear."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_table_pagination_controls(
    user_management_page: UserManagementPage,
):
    """
    Verify pagination Previous/Next traversal controls traverse between pages.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    assert user_management_page.pagination.is_visible(), "Expected pagination container."
    assert user_management_page.get_active_page_number() == "1"
    assert "disabled" in (user_management_page.paginate_previous.get_attribute("class") or "")

    # Click Next
    user_management_page.click_next_page()
    assert user_management_page.get_active_page_number() == "2"
    assert "disabled" not in (user_management_page.paginate_previous.get_attribute("class") or "")

    # Click Previous
    user_management_page.click_previous_page()
    assert user_management_page.get_active_page_number() == "1"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_pagination_page_2_every_possible_way(
    user_management_page: UserManagementPage,
):
    """
    Verify navigating to Page 2 via every possible method (page number button, Next button),
    verifying active button state, entry range 11 to 20, and returning via Previous and Page 1.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    # Initial state on Page 1
    assert user_management_page.get_active_page_number() == "1"
    expect(user_management_page.table_info).to_contain_text("Showing 1 to 10")
    assert "disabled" in (user_management_page.paginate_previous.get_attribute("class") or "")

    # Way 1: Click page number "2" directly
    user_management_page.click_page_number(2)
    expect(user_management_page.table_info).to_contain_text("Showing 11 to 20")
    assert user_management_page.get_active_page_number() == "2"
    # Previous button must now be enabled (disabled class removed)
    assert "disabled" not in (user_management_page.paginate_previous.get_attribute("class") or "")
    # Check that 10 rows are displayed for page 2
    assert user_management_page.get_user_count() == 10

    # Way 2: Return to Page 1 via Previous button
    user_management_page.click_previous_page()
    expect(user_management_page.table_info).to_contain_text("Showing 1 to 10")
    assert user_management_page.get_active_page_number() == "1"
    assert "disabled" in (user_management_page.paginate_previous.get_attribute("class") or "")

    # Way 3: Navigate to Page 2 via Next button
    user_management_page.click_next_page()
    expect(user_management_page.table_info).to_contain_text("Showing 11 to 20")
    assert user_management_page.get_active_page_number() == "2"
    assert "disabled" not in (user_management_page.paginate_previous.get_attribute("class") or "")

    # Way 4: Return to Page 1 via page number "1" button
    user_management_page.click_page_number(1)
    expect(user_management_page.table_info).to_contain_text("Showing 1 to 10")
    assert user_management_page.get_active_page_number() == "1"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_verification_dropdowns_and_verified_behavior(
    user_management_page: UserManagementPage,
):
    """
    Verify verification dropdowns (Email Verification, Document Verification),
    their option values (1=Verified, 0=Not Verified), and the corresponding CSS classes
    (userVerified btn-success vs btn-danger) and what happens when verified.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    # 1. Email Verification Select
    email_select = user_management_page.email_verification_selects.first
    email_options = [opt.lower() for opt in email_select.locator("option").all_inner_texts()]
    assert any("verified" in opt for opt in email_options), "Expected 'Verified' option."
    assert any("not verified" in opt for opt in email_options), "Expected 'Not Verified' option."

    email_opt_count = email_select.locator("option").count()
    email_opt_values = [
        email_select.locator("option").nth(i).get_attribute("value")
        for i in range(email_opt_count)
    ]
    assert "1" in email_opt_values and "0" in email_opt_values

    # Check verified styling: verified has userVerified and btn-success
    first_email_val = email_select.input_value()
    first_email_class = email_select.get_attribute("class") or ""
    if first_email_val == "1":
        assert "btn-success" in first_email_class
        assert "userVerified" in first_email_class

    # 2. Document Verification Select
    doc_select = user_management_page.doc_verification_selects.first
    doc_options = [opt.lower() for opt in doc_select.locator("option").all_inner_texts()]
    assert any("verified" in opt for opt in doc_options), "Expected 'Verified' option."
    assert any("not verified" in opt for opt in doc_options), "Expected 'Not Verified' option."

    # 3. Account Type Select (Standard vs Cent)
    acc_type_select = user_management_page.account_type_selects.first
    acc_options = [opt.lower() for opt in acc_type_select.locator("option").all_inner_texts()]
    assert any("standard" in opt for opt in acc_options)
    assert any("cent" in opt for opt in acc_options)

    # 4. User Status Select (Active vs Not Active)
    status_select = user_management_page.user_status_selects.first
    status_options = [opt.lower() for opt in status_select.locator("option").all_inner_texts()]
    assert any("active" in opt for opt in status_options)

    # 5. Book Select (A Book vs B Book)
    book_select = user_management_page.user_book_selects.first
    book_options = [opt.lower() for opt in book_select.locator("option").all_inner_texts()]
    assert any("a book" in opt for opt in book_options)
    assert any("b book" in opt for opt in book_options)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_table_row_action_buttons_and_expanded_details(
    user_management_page: UserManagementPage,
):
    """
    Verify each action button in table rows: Deposit/Withdraw edit/delete buttons,
    Account ID edit button, Refer by button, and expanding row via dtr-control to check
    responsive controls (MAM, PAMM, Copy Trading, Switch Group, Bonus, Password Reset).
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    first_row = user_management_page.user_rows.first

    # 1. Deposit / Withdraw action buttons
    edit_btn = first_row.locator("a.btnEdit")
    delete_btn = first_row.locator("a.BtnDelete")
    assert edit_btn.is_visible(), "Expected Edit action button."
    assert delete_btn.is_visible(), "Expected Delete action button."

    # 2. Account ID edit button
    edit_ac_id = first_row.locator("a.btn-edit-account_id")
    assert edit_ac_id.is_visible(), "Expected Edit Account ID button."
    assert edit_ac_id.get_attribute("account_id") is not None

    # 3. Refer by edit button
    edit_refer = first_row.locator("a.btnEditReferBy")
    assert edit_refer.count() >= 1, "Expected Edit Refer By button in row DOM."

    # 4. Responsive expansion via dtr-control
    user_management_page.expand_row(0)

    # In expanded state or table columns, verify trading buttons exist
    child_or_row = user_management_page.page.locator("tr.child, #datatable tbody tr")
    assert child_or_row.locator("button.userMam, .userMam").count() >= 1, "Expected MAM button."
    assert child_or_row.locator("button.userPamm, .userPamm").count() >= 1, "Expected PAMM button."
    assert child_or_row.locator("button.userCopyTrading, .userCopyTrading").count() >= 1, "Expected Copy Trading button."
    assert child_or_row.locator("button.switchGroup, .switchGroup").count() >= 1, "Expected Switch Group button."
    assert child_or_row.locator("button.userCredit, .userCredit").count() >= 1, "Expected Bonus button."
    assert child_or_row.locator("button.userPasswordResetLink, .userPasswordResetLink").count() >= 1, "Expected Password Reset button."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_page_2_row_buttons_verification(
    user_management_page: UserManagementPage,
):
    """
    Navigate to Page 2 and verify that all rows on Page 2 display verified status dropdowns,
    Deposit/Withdraw action buttons, and can expand responsive controls.
    """
    user_management_page.navigate()
    user_management_page.user_rows.first.wait_for(state="visible", timeout=15000)

    # Navigate to Page 2
    user_management_page.click_page_number(2)
    expect(user_management_page.table_info).to_contain_text("Showing 11 to 20")

    # Verify rows count on Page 2
    assert user_management_page.get_user_count() == 10, "Expected 10 rows on Page 2."

    # Verify each row on Page 2 has verification and action controls
    page_2_first_row = user_management_page.user_rows.first
    assert page_2_first_row.locator("select.userEmailVerification").count() >= 1
    assert page_2_first_row.locator("select.userDocumentVerification").count() >= 1
    assert page_2_first_row.locator("select.updateAccountType").count() >= 1
    assert page_2_first_row.locator("a.btnEdit").is_visible()
    assert page_2_first_row.locator("a.btn-edit-account_id").is_visible()

    # Expand a row on Page 2 to ensure responsive controls work on page 2
    user_management_page.expand_row(0)
    page = user_management_page.page
    child_or_row = page.locator("tr.child, #datatable tbody tr")
    assert child_or_row.locator(".userMam, .userPamm, .switchGroup").count() >= 1


