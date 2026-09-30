"""
Admin Portal User Document Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.user_document_page import UserDocumentPage


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_topbar_branding_and_title(
    user_document_page: UserDocumentPage,
):
    """
    Verify top navbar branding logos (small and large), page title ('User Document'),
    and sidebar menu button attributes matching the navbar-header layout.
    """
    user_document_page.navigate()

    # Brand Logo & Responsive Icons
    assert user_document_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert user_document_page.logo_small.is_visible() or user_document_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = user_document_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert user_document_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert user_document_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert user_document_page.menu_button.get_attribute("title") == "Open menu"
    assert user_document_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert user_document_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert user_document_page.page_title.inner_text().strip() == "User Document"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_topbar_sidebar_toggle_action(
    user_document_page: UserDocumentPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    user_document_page.navigate()

    body = user_document_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    user_document_page.menu_button.click()
    user_document_page.page.wait_for_timeout(300)

    toggled_class = body.get_attribute("class") or ""
    toggled_sidebar_size = body.get_attribute("data-sidebar-size") or ""

    assert (
        toggled_class != initial_class
        or "sidebar-enable" in toggled_class
        or toggled_sidebar_size in ["sm", "lg", "condensed"]
    ), "Expected sidebar state to change on toggle."

    # Toggle back
    user_document_page.menu_button.click()
    user_document_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_theme_toggle_switches_modes(
    user_document_page: UserDocumentPage,
):
    """
    Verify clicking the theme switch button toggles between dark and light themes,
    and dark/light SVG icons are present in the DOM.
    """
    user_document_page.navigate()

    assert user_document_page.theme_toggle.is_visible(), "Expected theme toggle button (#admin-theme-toggle) to be visible."
    assert user_document_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert user_document_page.theme_toggle.get_attribute("aria-label") == "Switch theme"

    # Both SVG icons (moon and sun) must exist in DOM
    assert user_document_page.theme_dark_icon.count() >= 1, "Expected dark mode moon icon."
    assert user_document_page.theme_light_icon.count() >= 1, "Expected light mode sun icon."

    # Test Theme Switching
    initial_mode = user_document_page.get_theme_mode()
    user_document_page.toggle_theme()
    user_document_page.page.wait_for_timeout(300)

    new_mode = user_document_page.get_theme_mode()
    assert new_mode != initial_mode, f"Expected theme mode to change from {initial_mode}."

    # Revert back to original mode
    user_document_page.toggle_theme()
    user_document_page.page.wait_for_timeout(300)
    assert user_document_page.get_theme_mode() == initial_mode


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_notifications_dropdown(
    user_document_page: UserDocumentPage,
):
    """
    Verify notifications button, badge, dropdown menu, header, and Mark all read link.
    """
    user_document_page.navigate()

    assert user_document_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert user_document_page.notification_count.is_visible(), "Expected notification count badge."

    # Open dropdown
    user_document_page.open_notifications()
    expect(user_document_page.notification_menu).to_be_visible()

    # Verify head and mark all read link
    assert user_document_page.notification_menu.locator("h6").inner_text().strip() == "Notifications"
    assert user_document_page.mark_all_read.is_visible()
    assert user_document_page.mark_all_read.inner_text().strip() == "Mark all read"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_profile_dropdown_and_logout_link(
    user_document_page: UserDocumentPage,
):
    """
    Verify profile dropdown button, initials, admin name, menu header, and logout action link.
    """
    user_document_page.navigate()

    assert user_document_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert user_document_page.profile_initials.is_visible(), "Expected profile initials to be visible."
    assert user_document_page.profile_initials.inner_text().strip() == "M"

    if user_document_page.profile_topbar_name.is_visible():
        assert user_document_page.profile_topbar_name.inner_text().strip() == "madmin"

    # Open Profile Menu
    user_document_page.open_profile_menu()
    expect(user_document_page.profile_menu).to_be_visible()

    assert user_document_page.profile_name.inner_text().strip() == "madmin"
    assert user_document_page.profile_role.inner_text().strip() == "Administrator"

    # Logout link
    logout = user_document_page.logout_link
    assert logout.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (logout.get_attribute("href") or "")
    assert "Logout" in logout.inner_text()
    assert logout.locator("i.mdi-logout").is_visible(), "Expected Logout icon."


# ==============================================================================
# SECTION 2: PAGE ACTIONS & HIDDEN PERMISSIONS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_page_actions_and_hidden_permissions(
    user_document_page: UserDocumentPage,
):
    """
    Verify the page actions container, Add Document button (#addNew), 4 hidden
    permission inputs (#editUserDoc, #deleteUserDoc, #verifyUserDoc, #remarksUserDoc),
    and opening/closing the Add Document modal (#myModal).
    """
    user_document_page.navigate()

    # Container and Add Document button
    assert user_document_page.page_actions.is_visible(), "Expected .user-document-page-actions to be visible."
    assert user_document_page.add_document_button.is_visible(), "Expected #addNew button to be visible."
    assert user_document_page.add_document_button.inner_text().strip() == "Add Document"

    # Hidden permission values
    assert user_document_page.edit_user_doc_hidden.get_attribute("value") == "1"
    assert user_document_page.delete_user_doc_hidden.get_attribute("value") == "1"
    assert user_document_page.verify_user_doc_hidden.get_attribute("value") == "1"
    assert user_document_page.remarks_user_doc_hidden.get_attribute("value") == "1"

    # Click Add Document to open modal
    user_document_page.add_document_button.click()
    user_document_page.page.wait_for_timeout(500)

    expect(user_document_page.document_modal).to_be_visible()
    assert "User Document Form" in user_document_page.document_modal_title.inner_text()

    # Close modal
    user_document_page.document_modal_close.first.click()
    user_document_page.page.wait_for_timeout(500)
    expect(user_document_page.document_modal).not_to_be_visible()


# ==============================================================================
# SECTION 3: TABLE CARD & 13 COLUMN HEADERS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_table_card_and_13_column_headers(
    user_document_page: UserDocumentPage,
):
    """
    Verify the table card container, DataTable wrapper, 13 exact column headers,
    initial 10 rows rendered, and pagination info.
    """
    user_document_page.navigate()

    assert user_document_page.table_card.is_visible(), "Expected .user-document-table-card to be visible."
    assert user_document_page.table_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."

    # Validate exact 13 headers
    headers = [th.inner_text().strip() for th in user_document_page.table_headers.all()]
    expected_headers = [
        "S.No",
        "User Name",
        "Account Id",
        "Address (front)",
        "Address (back)",
        "National ID (front)",
        "National ID (back)",
        "Updated Time",
        "Bank",
        "Other",
        "Document",
        "Remarks",
        "Action",
    ]
    assert headers == expected_headers, f"Expected headers {expected_headers}, got {headers}."

    # Validate row count and info
    assert user_document_page.document_rows.count() == 10
    info_text = user_document_page.table_info.inner_text()
    assert "Showing 1 to 10 of" in info_text
    assert "entries" in info_text


# ==============================================================================
# SECTION 4: TABLE ROWS DATA & DOCUMENT LINKS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_table_rows_data_and_file_links(
    user_document_page: UserDocumentPage,
):
    """
    Verify row data integrity: S.No, user names, account IDs, and valid document
    links or '-' placeholders across all columns.
    """
    user_document_page.navigate()

    rows = user_document_page.document_rows
    assert rows.count() >= 1, "Expected table rows to be present."

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")

        # Serial number
        sno = cells.nth(0).inner_text().strip()
        assert sno.isdigit(), f"Expected row {i} S.No to be numeric, got '{sno}'."

        # User Name and Account ID
        user_name = cells.nth(1).inner_text().strip()
        account_id = cells.nth(2).inner_text().strip()
        assert len(user_name) > 0, f"Expected non-empty user name in row {i}."
        assert len(account_id) > 0, f"Expected non-empty account id in row {i}."

        # Document links (columns 3, 4, 5, 6, 8, 9)
        for col_idx in [3, 4, 5, 6, 8, 9]:
            cell_text = cells.nth(col_idx).inner_text().strip()
            link = cells.nth(col_idx).locator("a")
            if link.count() > 0:
                href = link.first.get_attribute("href") or ""
                assert href.startswith("http") or href.startswith("/"), (
                    f"Expected valid document link in row {i} col {col_idx}, got '{href}'."
                )
                assert link.first.get_attribute("target") == "_blank"
            else:
                assert cell_text == "-", f"Expected '-' for missing document, got '{cell_text}'."


# ==============================================================================
# SECTION 5: VERIFICATION DROPDOWNS & DYNAMIC STYLING
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_verification_dropdown_status_and_classes(
    user_document_page: UserDocumentPage,
):
    """
    Verify verification dropdowns (select.userDocumentVerification):
    - Option 1 (Verified, btn-success)
    - Option 0 (Not Verified, btn-warning)
    - Option 2 (Rejected, btn-danger)
    And verify selecting 'Rejected' automatically triggers the Remark Modal.
    """
    user_document_page.navigate()

    dropdowns = user_document_page.verification_dropdowns
    assert dropdowns.count() >= 1, "Expected verification dropdowns in table."

    first_select = dropdowns.first
    options = [opt.inner_text().strip() for opt in first_select.locator("option").all()]
    assert "Verified" in options
    assert "Not Verified" in options
    assert "Rejected" in options

    # Check initial status class corresponds to selected option
    initial_val = first_select.input_value()
    initial_classes = first_select.get_attribute("class") or ""

    if initial_val == "1":
        assert "btn-success" in initial_classes
    elif initial_val == "0":
        assert "btn-warning" in initial_classes
    elif initial_val == "2":
        assert "btn-danger" in initial_classes

    # Changing to Rejected (2) triggers #remarkModal
    first_select.select_option("2")
    user_document_page.page.wait_for_timeout(600)

    expect(user_document_page.remark_modal).to_be_visible()
    assert "Remarks Form" in user_document_page.remark_modal_title.inner_text()

    # Close modal and revert status
    user_document_page.remark_modal_close.first.click()
    user_document_page.page.wait_for_timeout(500)
    first_select.select_option(initial_val)
    user_document_page.page.wait_for_timeout(500)


# ==============================================================================
# SECTION 6: ROW ACTION BUTTONS & MODALS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_remarks_action_opens_modal(
    user_document_page: UserDocumentPage,
):
    """
    Verify clicking the remark pencil button (a.btnRemark) opens the Remarks Form
    modal (#remarkModal) with textarea #remark and Update Remark button.
    """
    user_document_page.navigate()

    remark_buttons = user_document_page.remark_buttons
    assert remark_buttons.count() >= 1, "Expected remark action buttons."

    first_remark_btn = remark_buttons.first
    assert first_remark_btn.locator("i.mdi-pencil").is_visible(), "Expected pencil icon."

    first_remark_btn.click()
    user_document_page.page.wait_for_timeout(500)

    expect(user_document_page.remark_modal).to_be_visible()
    assert "Remarks Form" in user_document_page.remark_modal_title.inner_text()
    assert user_document_page.remark_modal_textarea.is_visible()
    assert user_document_page.remark_modal.locator("button:has-text('Update Remark')").is_visible()

    # Close modal
    user_document_page.remark_modal_close.first.click()
    user_document_page.page.wait_for_timeout(500)
    expect(user_document_page.remark_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_edit_action_opens_form_modal(
    user_document_page: UserDocumentPage,
):
    """
    Verify clicking the edit document button (a.btnEdit) opens the User Document Form
    modal (#myModal) with existing record details.
    """
    user_document_page.navigate()

    edit_buttons = user_document_page.edit_buttons
    assert edit_buttons.count() >= 1, "Expected edit action buttons."

    first_edit_btn = edit_buttons.first
    assert first_edit_btn.locator("i.mdi-book-edit-outline").is_visible(), "Expected book-edit icon."

    first_edit_btn.click()
    user_document_page.page.wait_for_timeout(500)

    expect(user_document_page.document_modal).to_be_visible()
    assert "User Document Form" in user_document_page.document_modal_title.inner_text()

    # Close modal
    user_document_page.document_modal_close.first.click()
    user_document_page.page.wait_for_timeout(500)
    expect(user_document_page.document_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_delete_action_with_and_without_documents(
    user_document_page: UserDocumentPage,
):
    """
    Verify clicking delete button (a.BtnDelete):
    - On a user with no uploaded documents: triggers error confirm dialog ('No document found to delete')
    - On a user with uploaded documents: triggers #deleteModal ('User Delete Document Form')
    """
    user_document_page.navigate()

    delete_buttons = user_document_page.delete_buttons
    assert delete_buttons.count() >= 1, "Expected delete action buttons."

    # Row 0 (master) has no documents -> triggers alert
    delete_buttons.first.click()
    user_document_page.page.wait_for_timeout(500)

    expect(user_document_page.confirm_dialog).to_be_visible()
    assert "No document found to delete" in user_document_page.confirm_dialog.inner_text()
    user_document_page.confirm_dialog_close.first.click()
    user_document_page.page.wait_for_timeout(500)
    expect(user_document_page.confirm_dialog).not_to_be_visible()

    # Row 3 (mallinath mulage) has address.jpg -> triggers #deleteModal
    delete_buttons.nth(3).click()
    user_document_page.page.wait_for_timeout(500)

    expect(user_document_page.delete_modal).to_be_visible()
    assert "User Delete Document Form" in user_document_page.delete_modal_title.inner_text()
    user_document_page.delete_modal_close.first.click()
    user_document_page.page.wait_for_timeout(500)
    expect(user_document_page.delete_modal).not_to_be_visible()


# ==============================================================================
# SECTION 7: CONTROLS, FILTERS & SEARCH
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_length_dropdown_selection(
    user_document_page: UserDocumentPage,
):
    """
    Verify changing visible entries per page via datatable_length dropdown
    dynamically updates visible row count and datatable info.
    """
    user_document_page.navigate()

    # Select 25
    user_document_page.select_page_length("25")
    assert user_document_page.document_rows.count() == 25
    assert "Showing 1 to 25 of" in user_document_page.table_info.inner_text()

    # Select 50
    user_document_page.select_page_length("50")
    assert user_document_page.document_rows.count() == 50
    assert "Showing 1 to 50 of" in user_document_page.table_info.inner_text()

    # Revert to 10
    user_document_page.select_page_length("10")
    assert user_document_page.document_rows.count() == 10
    assert "Showing 1 to 10 of" in user_document_page.table_info.inner_text()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_date_filter_controls(
    user_document_page: UserDocumentPage,
):
    """
    Verify date filter controls:
    - #from and #to datetime-local inputs
    - Go button (#apply) triggers table draw and sets clear flag
    - Clear button (#clear) resets from/to inputs and clears filter.
    """
    user_document_page.navigate()

    assert user_document_page.from_date_input.is_visible()
    assert user_document_page.to_date_input.is_visible()
    assert user_document_page.apply_button.is_visible()
    assert user_document_page.clear_button.is_visible()

    # Fill date range and click Go
    user_document_page.filter_by_date("2026-08-01T00:00", "2026-09-01T00:00")
    assert user_document_page.clear_button.get_attribute("value") == "1"

    # Reset filter
    user_document_page.clear_date_filter()
    assert user_document_page.from_date_input.input_value() == ""
    assert user_document_page.to_date_input.input_value() == ""
    assert user_document_page.clear_button.get_attribute("value") == "2"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_search_filtering(
    user_document_page: UserDocumentPage,
):
    """
    Verify search input filters rows by user name or account ID,
    displays empty state when unmatched, and restores on clear.
    """
    user_document_page.navigate()

    # Search for specific user "Keerthi"
    user_document_page.search_document("Keerthi")
    expect(user_document_page.table_info).to_contain_text("Showing 1 to 1 of 1 entries")
    assert user_document_page.document_rows.count() == 1
    assert "Keerthi" in user_document_page.document_rows.first.inner_text()

    # Search for non-existent record
    user_document_page.search_document("ZZZZNONEXISTENTUSERXYZ")
    expect(user_document_page.table_info).to_contain_text("Showing 0 to 0 of 0 entries")
    assert user_document_page.empty_row.is_visible()
    assert "No data available in table" in user_document_page.empty_row.inner_text()

    # Clear search
    user_document_page.clear_search()
    expect(user_document_page.table_info).to_contain_text("Showing 1 to 10 of")
    assert user_document_page.document_rows.count() == 10


# ==============================================================================
# SECTION 8: PAGINATION & PAGE 2 NAVIGATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_document_pagination_page_2_every_possible_way(
    user_document_page: UserDocumentPage,
):
    """
    Verify full pagination controls and Page 2 traversal:
    1. Page 1 initial state: active page 1, Previous button disabled.
    2. Navigate to Page 2 via page number button '2':
       - Active page becomes 2
       - Status info displays 'Showing 11 to 20 of 64 entries'
       - Previous button becomes enabled
       - Page 2 first row S.No is 11
    3. Return to Page 1 via Previous button:
       - Active page becomes 1
       - Status info displays 'Showing 1 to 10 of 64 entries'
       - Previous button is disabled again
    4. Navigate to Page 2 via Next button:
       - Active page becomes 2
       - Status info displays 'Showing 11 to 20 of 64 entries'
    """
    user_document_page.navigate()

    # 1. Page 1 Initial State
    expect(user_document_page.active_page_button).to_have_text("1")
    assert "disabled" in (user_document_page.previous_page_button.get_attribute("class") or "")
    expect(user_document_page.table_info).to_contain_text("Showing 1 to 10 of")

    # 2. Navigate to Page 2 via page number button '2'
    user_document_page.click_page_number(2)
    expect(user_document_page.active_page_button).to_have_text("2")
    expect(user_document_page.table_info).to_contain_text("Showing 11 to 20 of")
    assert "disabled" not in (user_document_page.previous_page_button.get_attribute("class") or "")

    # Check S.No on Page 2 starts at 11
    first_sno_p2 = user_document_page.document_rows.first.locator("td").first.inner_text().strip()
    assert first_sno_p2 == "11", f"Expected Page 2 first S.No to be 11, got {first_sno_p2}."

    # 3. Return to Page 1 via Previous button
    user_document_page.click_previous_page()
    expect(user_document_page.active_page_button).to_have_text("1")
    expect(user_document_page.table_info).to_contain_text("Showing 1 to 10 of")
    assert "disabled" in (user_document_page.previous_page_button.get_attribute("class") or "")

    # 4. Navigate to Page 2 via Next button
    user_document_page.click_next_page()
    expect(user_document_page.active_page_button).to_have_text("2")
    expect(user_document_page.table_info).to_contain_text("Showing 11 to 20 of")
    assert "disabled" not in (user_document_page.previous_page_button.get_attribute("class") or "")
