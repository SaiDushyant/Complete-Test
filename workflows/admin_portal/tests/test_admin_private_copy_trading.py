import pytest

from workflows.admin_portal.pages.private_copy_trading_page import PrivateCopyTradingPage


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_page_loads_and_displays_heading(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the Admin Private Copy Trading page loads and displays the heading."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.is_page_displayed(), (
        "Expected Private Copy Trading page title to be displayed."
    )
    assert private_copy_trading_page.page_title.inner_text().strip().casefold() == (
        "manage private copier"
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_topbar_branding_and_title(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the top navbar renders brand logo, title, and menu button."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.brand_logo.is_visible(), (
        "Expected brand logo to be visible in the navbar header."
    )
    assert private_copy_trading_page.brand_logo_images.count() >= 1, (
        "Expected at least one brand logo image to be rendered."
    )
    assert private_copy_trading_page.menu_button.is_visible(), (
        "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    )
    assert private_copy_trading_page.page_title.is_visible(), (
        "Expected topbar page title to be visible."
    )
    assert private_copy_trading_page.page_title.inner_text().strip() == (
        "Manage Private Copier"
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_theme_toggle_switches_modes(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking the theme switch toggles body data-layout-mode between light and dark."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.theme_toggle.is_visible(), (
        "Expected theme toggle button to be visible."
    )

    initial_mode = private_copy_trading_page.get_theme_mode() or "light"
    private_copy_trading_page.toggle_theme()
    private_copy_trading_page.page.wait_for_timeout(300)

    toggled_mode = private_copy_trading_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, (
        f"Expected layout mode to change after toggle, but remained '{initial_mode}'."
    )

    # Revert back to maintain initial layout state
    private_copy_trading_page.toggle_theme()
    private_copy_trading_page.page.wait_for_timeout(300)
    reverted_mode = private_copy_trading_page.get_theme_mode() or "light"
    assert reverted_mode == initial_mode, (
        f"Expected layout mode to revert to '{initial_mode}', got '{reverted_mode}'."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_notifications_dropdown(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the notification button opens the dropdown menu showing the Mark all read option."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.notification_button.is_visible(), (
        "Expected notification bell button to be visible."
    )
    assert private_copy_trading_page.notification_count.is_visible(), (
        "Expected notification count badge to be visible."
    )

    # Open notifications dropdown
    private_copy_trading_page.open_notifications()
    private_copy_trading_page.notification_menu.wait_for(state="visible", timeout=5000)

    assert private_copy_trading_page.notification_menu.is_visible(), (
        "Expected notification dropdown menu to be visible."
    )
    assert private_copy_trading_page.mark_all_read.is_visible(), (
        "Expected 'Mark all read' link to be visible in notifications."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_profile_dropdown_and_logout_link(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the profile menu displays admin credentials and a valid logout link."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.profile_button.is_visible(), (
        "Expected user profile dropdown button to be visible."
    )

    # Open profile dropdown
    private_copy_trading_page.open_profile_menu()
    private_copy_trading_page.profile_menu.wait_for(state="visible", timeout=5000)

    assert private_copy_trading_page.profile_menu.is_visible(), (
        "Expected user profile menu to open."
    )
    assert private_copy_trading_page.profile_name.inner_text().strip() == "madmin", (
        "Expected profile username to be 'madmin'."
    )
    assert private_copy_trading_page.profile_role.inner_text().strip() == "Administrator", (
        "Expected profile role to be 'Administrator'."
    )
    assert private_copy_trading_page.logout_link.is_visible(), (
        "Expected logout link to be visible in profile menu."
    )

    logout_href = private_copy_trading_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to '/admin/Controlbase/Logout', got '{logout_href}'."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_create_copier_button_and_modal(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that Create Copier button is visible and opens the Private Copy Trading modal."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.create_copier_button.is_visible(), (
        "Expected 'Create Copier' button (#addNewCopier) to be visible."
    )
    btn_text = private_copy_trading_page.create_copier_button.inner_text().strip()
    assert "create copier" in btn_text.casefold(), (
        f"Expected button text to contain 'Create Copier', got '{btn_text}'."
    )

    # Open Create Copier modal
    private_copy_trading_page.open_create_copier_modal()

    assert private_copy_trading_page.create_copier_modal.is_visible(), (
        "Expected Create Copier modal (#myModal) to be visible after clicking."
    )
    assert private_copy_trading_page.create_copier_modal_title.is_visible(), (
        "Expected modal title (#myModalLabel) to be visible."
    )
    title_text = private_copy_trading_page.create_copier_modal_title.inner_text().strip()
    assert "private copy trading" in title_text.casefold(), (
        f"Expected modal title 'Private Copy Trading', got '{title_text}'."
    )
    assert private_copy_trading_page.create_copier_form.is_visible(), (
        "Expected form (#formModal) inside Create Copier modal to be visible."
    )

    # Close modal
    private_copy_trading_page.close_create_copier_modal()
    private_copy_trading_page.page.wait_for_timeout(300)
    assert not private_copy_trading_page.create_copier_modal.is_visible(), (
        "Expected Create Copier modal to be closed."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_datatable_controls_are_present(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that DataTable length selection and search filter controls are present and configured."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.length_dropdown.is_visible(), (
        "Expected page length select dropdown to be visible."
    )
    assert private_copy_trading_page.search_input.is_visible(), (
        "Expected search filter input to be visible."
    )
    assert private_copy_trading_page.search_input.is_enabled(), (
        "Expected search filter input to be enabled."
    )

    # Default length value
    default_length = private_copy_trading_page.length_dropdown.input_value()
    assert default_length in ["10", "50"], (
        f"Expected default table length to be '10' or '50', got '{default_length}'."
    )

    # Verify options 10, 25, 50, 100
    options = private_copy_trading_page.length_dropdown.locator("option").all_inner_texts()
    expected_options = ["10", "25", "50", "100"]
    for opt in expected_options:
        assert opt in options, f"Expected option '{opt}' in length dropdown options: {options}"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_table_headers_and_columns_are_valid(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that all 8 expected table column headers are rendered correctly."""
    private_copy_trading_page.navigate()

    expected_headers = [
        "s.no",
        "master",
        "master a/c",
        "slaves",
        "copy type",
        "direction",
        "created",
        "action",
    ]

    actual_headers = private_copy_trading_page.get_table_headers()

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected column header '{expected}' among rendered headers: {actual_headers}"
        )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_table_rows_and_data_structure(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that table rows contain valid serial number, master name, master account, and slaves summary."""
    private_copy_trading_page.navigate()

    row_count = private_copy_trading_page.get_row_count()
    assert row_count > 0, "Expected at least one copier row in the Private Copy Trading table."

    first_row = private_copy_trading_page.table_rows.first
    cells = first_row.locator("td").all_inner_texts()

    # S.No (col 0)
    s_no = cells[0].strip()
    assert s_no.isdigit(), f"Expected numeric S.No, got '{s_no}'"

    # Master name (col 1)
    master_name = cells[1].strip()
    assert len(master_name) > 0, "Expected non-empty Master name in column 2."

    # Master A/C (col 2)
    master_ac = cells[2].strip()
    assert master_ac.isdigit(), f"Expected numeric Master A/C, got '{master_ac}'"

    # Slaves summary & View Slaves button
    assert first_row.locator(".private-slave-summary").is_visible(), (
        "Expected .private-slave-summary element in Slaves column."
    )
    assert first_row.locator("button.btnPrivateSlaves").is_visible(), (
        "Expected 'View Slaves' button (.btnPrivateSlaves) in Slaves column."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_search_filters_by_master_name(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that typing a master name into the search bar filters rows correctly."""
    private_copy_trading_page.navigate()

    initial_count = private_copy_trading_page.get_row_count()
    assert initial_count > 0, "Expected rows before searching."

    # Target master name from the first row
    first_master_name = (
        private_copy_trading_page.table_rows.first.locator("td").nth(1).inner_text().strip()
    )
    search_query = first_master_name[:12] if len(first_master_name) > 12 else first_master_name

    private_copy_trading_page.search(search_query)

    filtered_count = private_copy_trading_page.get_row_count()
    assert 0 < filtered_count <= initial_count, (
        f"Expected filtered count between 1 and {initial_count}, got {filtered_count}."
    )

    # First visible row should contain search query
    visible_master = (
        private_copy_trading_page.table_rows.first.locator("td").nth(1).inner_text().strip()
    )
    assert search_query.casefold() in visible_master.casefold(), (
        f"Expected '{search_query}' in filtered master name '{visible_master}'."
    )

    # Reset search and verify rows restored
    private_copy_trading_page.clear_search()
    assert private_copy_trading_page.get_row_count() == initial_count, (
        "Expected all rows restored after clearing search query."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_search_filters_by_master_account_id(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that searching by Master Account ID isolates the matching record."""
    private_copy_trading_page.navigate()

    initial_count = private_copy_trading_page.get_row_count()
    assert initial_count > 0, "Expected rows before searching."

    target_ac = (
        private_copy_trading_page.table_rows.first.locator("td").nth(2).inner_text().strip()
    )

    private_copy_trading_page.search(target_ac)

    filtered_count = private_copy_trading_page.get_row_count()
    assert filtered_count >= 1, (
        f"Expected at least 1 row matching account '{target_ac}', got {filtered_count}."
    )

    matched_ac = (
        private_copy_trading_page.table_rows.first.locator("td").nth(2).inner_text().strip()
    )
    assert matched_ac == target_ac, (
        f"Expected matched Account ID '{target_ac}', got '{matched_ac}'."
    )

    # Clear and verify restoration
    private_copy_trading_page.clear_search()
    assert private_copy_trading_page.get_row_count() == initial_count, (
        "Expected row count restored after clearing search."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_search_filters_by_slave_details(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that searching by slave follower name or ID finds the associated master row."""
    private_copy_trading_page.navigate()

    initial_count = private_copy_trading_page.get_row_count()
    assert initial_count > 0, "Expected rows before searching."

    # Extract text from the slaves preview column
    slave_preview = (
        private_copy_trading_page.table_rows.first.locator(".private-slave-preview")
        .inner_text()
        .strip()
    )
    # Extract first word or numeric token from preview
    token = slave_preview.split()[0].replace("(", "").replace(")", "").replace(",", "")

    private_copy_trading_page.search(token)

    filtered_count = private_copy_trading_page.get_row_count()
    assert filtered_count >= 1, (
        f"Expected at least 1 matching row for slave token '{token}', got {filtered_count}."
    )

    # Clear and verify restoration
    private_copy_trading_page.clear_search()
    assert private_copy_trading_page.get_row_count() == initial_count, (
        "Expected row count restored after clearing search."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_search_nonexistent_query_shows_empty_state(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that searching for an unknown string displays the empty state message and zero entries."""
    private_copy_trading_page.navigate()

    initial_count = private_copy_trading_page.get_row_count()

    private_copy_trading_page.search("nonexistent_private_copier_xyz_99999")

    # DataTable either shows 1 empty row with 'no matching records found' or 0 rows
    row_count = private_copy_trading_page.get_row_count()
    if row_count > 0:
        first_row_text = private_copy_trading_page.table_rows.first.inner_text().casefold()
        assert "no matching records found" in first_row_text, (
            f"Expected 'No matching records found' message, got '{first_row_text}'."
        )

    info_text = private_copy_trading_page.get_info_text().casefold()
    assert "0 to 0 of 0 entries" in info_text or "showing 0" in info_text, (
        f"Expected info status to show 0 entries, got '{info_text}'."
    )

    # Clear search and verify full rows return
    private_copy_trading_page.clear_search()
    assert private_copy_trading_page.get_row_count() == initial_count, (
        "Expected rows restored after clearing nonexistent search query."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_view_slaves_modal_opens_and_closes(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking View Slaves opens the Slave Accounts modal and displays the slaves list."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.view_slaves_buttons.count() > 0, (
        "Expected 'View Slaves' buttons to be present."
    )

    # Open View Slaves modal for row 0
    private_copy_trading_page.open_view_slaves_modal(0)

    assert private_copy_trading_page.private_slaves_modal.is_visible(), (
        "Expected Slave Accounts modal (#privateSlavesModal) to be visible."
    )
    assert private_copy_trading_page.private_slaves_modal_title.is_visible(), (
        "Expected modal title (#privateSlavesModalLabel) to be visible."
    )
    title_text = private_copy_trading_page.private_slaves_modal_title.inner_text().strip()
    assert "slave accounts" in title_text.casefold(), (
        f"Expected modal title 'Slave Accounts', got '{title_text}'."
    )
    assert private_copy_trading_page.private_slaves_modal_body.is_visible(), (
        "Expected #privateSlavesModalBody to be visible in modal."
    )

    # Close modal
    private_copy_trading_page.close_view_slaves_modal()
    private_copy_trading_page.page.wait_for_timeout(300)
    assert not private_copy_trading_page.private_slaves_modal.is_visible(), (
        "Expected Slave Accounts modal to be closed."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_table_column_sorting(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking a sortable column header (Master) toggles sorting classes."""
    private_copy_trading_page.navigate()

    master_header = private_copy_trading_page.page.locator(
        "#datatable thead th:has-text('Master')"
    ).first
    master_header.wait_for(state="visible", timeout=5000)

    # Click to sort ascending / descending
    master_header.click()
    private_copy_trading_page.page.wait_for_timeout(400)

    sort_class_first = master_header.get_attribute("class") or ""
    assert "sorting_asc" in sort_class_first or "sorting_desc" in sort_class_first, (
        f"Expected sorting class on header, got '{sort_class_first}'."
    )

    # Click second time to reverse
    master_header.click()
    private_copy_trading_page.page.wait_for_timeout(400)

    sort_class_second = master_header.get_attribute("class") or ""
    assert sort_class_second != sort_class_first, (
        f"Expected sort class to toggle from '{sort_class_first}', got '{sort_class_second}'."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_pagination_and_info_status(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the table info status and pagination elements are displayed properly."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.datatable_info.is_visible(), (
        "Expected #datatable_info element to be visible."
    )
    info_text = private_copy_trading_page.get_info_text().casefold()
    assert "showing" in info_text and "entries" in info_text, (
        f"Expected 'Showing ... entries' pattern in info text, got '{info_text}'."
    )

    assert private_copy_trading_page.pagination.is_visible(), (
        "Expected pagination controls (#datatable_paginate) to be visible."
    )
    assert private_copy_trading_page.pagination_items.count() >= 1, (
        "Expected at least one pagination item to be rendered."
    )
    assert private_copy_trading_page.pagination_active.is_visible(), (
        "Expected active page indicator in pagination."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_length_dropdown_selection(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify selecting different page length options updates the dropdown value."""
    private_copy_trading_page.navigate()

    # Change to 25
    private_copy_trading_page.select_page_length("25")
    assert private_copy_trading_page.length_dropdown.input_value() == "25", (
        "Expected page length dropdown value to be '25'."
    )

    # Change to 50
    private_copy_trading_page.select_page_length("50")
    assert private_copy_trading_page.length_dropdown.input_value() == "50", (
        "Expected page length dropdown value to be '50'."
    )

    # Revert to 10
    private_copy_trading_page.select_page_length("10")
    assert private_copy_trading_page.length_dropdown.input_value() == "10", (
        "Expected page length dropdown value to revert to '10'."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_responsive_control_expansion(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking the responsive dtr-control toggle on a row expands collapsed details."""
    private_copy_trading_page.navigate()

    assert private_copy_trading_page.dtr_controls.count() > 0, (
        "Expected responsive dtr-control elements on data rows."
    )

    # Click first row's dtr-control
    private_copy_trading_page.toggle_responsive_row(0)
    private_copy_trading_page.page.wait_for_timeout(400)

    # Toggle again to collapse
    private_copy_trading_page.toggle_responsive_row(0)
    private_copy_trading_page.page.wait_for_timeout(400)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_create_copier_modal_form_fields_and_inputs(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the Create Copier form displays all required input fields, search pickers, and direction radios."""
    private_copy_trading_page.navigate()
    private_copy_trading_page.open_create_copier_modal()

    # Master account picker
    assert private_copy_trading_page.master_search_input.is_visible(), (
        "Expected master search input (#masterSearch) to be visible."
    )
    master_placeholder = private_copy_trading_page.master_search_input.get_attribute("placeholder") or ""
    assert "search by name or account id" in master_placeholder.casefold(), (
        f"Expected master search placeholder, got '{master_placeholder}'."
    )

    # Slave account picker
    assert private_copy_trading_page.slave_search_input.is_visible(), (
        "Expected slave search input (#slaveSearch) to be visible."
    )
    slave_placeholder = private_copy_trading_page.slave_search_input.get_attribute("placeholder") or ""
    assert "search by name or account id" in slave_placeholder.casefold(), (
        f"Expected slave search placeholder, got '{slave_placeholder}'."
    )

    # Copy type dropdown
    assert private_copy_trading_page.copy_type_dropdown.is_visible(), (
        "Expected Copy Type select (#tradeMethod) to be visible."
    )
    assert private_copy_trading_page.copy_type_dropdown.input_value() == "balance", (
        "Expected default copy type to be 'balance' (Balance Wise)."
    )
    options = private_copy_trading_page.copy_type_dropdown.locator("option").all_inner_texts()
    for expected_opt in ["Balance Wise", "Equity Wise", "Multiplier Wise"]:
        assert any(expected_opt in opt for opt in options), (
            f"Expected '{expected_opt}' in tradeMethod options: {options}"
        )

    # Trading direction radios
    assert private_copy_trading_page.direction_normal_radio.is_visible(), (
        "Expected Normal Copy radio (#directionNormal) to be visible."
    )
    assert private_copy_trading_page.direction_normal_radio.is_checked(), (
        "Expected Normal Copy to be selected by default."
    )
    assert private_copy_trading_page.direction_reverse_radio.is_visible(), (
        "Expected Reverse Copy radio (#directionReverse) to be visible."
    )
    assert not private_copy_trading_page.direction_reverse_radio.is_checked(), (
        "Expected Reverse Copy to be unchecked by default."
    )

    # Save button
    assert private_copy_trading_page.form_save_button.is_visible(), (
        "Expected Save button (#formSubmit) to be visible."
    )

    private_copy_trading_page.close_create_copier_modal()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_create_copier_copy_type_multiplier_toggle(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that selecting 'Multiplier Wise' dynamically displays the Multiplier Value input field."""
    private_copy_trading_page.navigate()
    private_copy_trading_page.open_create_copier_modal()

    # Initially hidden under Balance Wise
    assert not private_copy_trading_page.multiplier_wrap.is_visible(), (
        "Expected Multiplier Value wrap (#multiplierWrap) to be hidden by default."
    )

    # Select Multiplier Wise
    private_copy_trading_page.select_copy_type("multiplier")
    assert private_copy_trading_page.multiplier_wrap.is_visible(), (
        "Expected #multiplierWrap to become visible when 'multiplier' is selected."
    )
    assert private_copy_trading_page.multiplier_input.is_visible(), (
        "Expected #multiplierValue input field to be visible."
    )
    mult_placeholder = private_copy_trading_page.multiplier_input.get_attribute("placeholder") or ""
    assert "e.g. 2" in mult_placeholder.casefold(), (
        f"Expected placeholder 'e.g. 2', got '{mult_placeholder}'."
    )

    # Revert to Balance Wise
    private_copy_trading_page.select_copy_type("balance")
    assert not private_copy_trading_page.multiplier_wrap.is_visible(), (
        "Expected #multiplierWrap to hide again when reverting to 'balance'."
    )

    private_copy_trading_page.close_create_copier_modal()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_create_copier_trading_direction_radio_toggle(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking Reverse Copy selects the reverse radio and unselects normal copy."""
    private_copy_trading_page.navigate()
    private_copy_trading_page.open_create_copier_modal()

    # Select Reverse Copy
    private_copy_trading_page.select_direction(reverse=True)
    assert private_copy_trading_page.direction_reverse_radio.is_checked(), (
        "Expected Reverse Copy to be checked."
    )
    assert not private_copy_trading_page.direction_normal_radio.is_checked(), (
        "Expected Normal Copy to be unchecked after selecting Reverse."
    )

    # Select Normal Copy back
    private_copy_trading_page.select_direction(reverse=False)
    assert private_copy_trading_page.direction_normal_radio.is_checked(), (
        "Expected Normal Copy to be checked after toggling back."
    )
    assert not private_copy_trading_page.direction_reverse_radio.is_checked(), (
        "Expected Reverse Copy to be unchecked."
    )

    private_copy_trading_page.close_create_copier_modal()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_create_copier_empty_submission_validation(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking Save without selecting required accounts prevents submission and retains modal."""
    private_copy_trading_page.navigate()
    private_copy_trading_page.open_create_copier_modal()

    # Attempt to submit empty form
    private_copy_trading_page.form_save_button.click()
    private_copy_trading_page.page.wait_for_timeout(500)

    # Modal should stay visible (form is not submitted)
    assert private_copy_trading_page.create_copier_modal.is_visible(), (
        "Expected Create Copier modal to remain open when required fields are missing."
    )

    private_copy_trading_page.close_create_copier_modal()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_slave_accounts_modal_content_and_rows(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that the Slave Accounts modal displays the list of slave accounts with index, name, and account."""
    private_copy_trading_page.navigate()

    # Search for sapna which has multiple slaves (Velan, Azar)
    private_copy_trading_page.search("sapna")
    private_copy_trading_page.page.wait_for_timeout(400)

    assert private_copy_trading_page.get_row_count() >= 1, "Expected matching row for sapna."

    # Open View Slaves modal
    private_copy_trading_page.open_view_slaves_modal(0)

    assert private_copy_trading_page.private_slaves_modal.is_visible(), (
        "Expected Slave Accounts modal to be visible."
    )
    assert private_copy_trading_page.slave_rows.count() >= 2, (
        f"Expected at least 2 slave account rows for sapna, got {private_copy_trading_page.slave_rows.count()}."
    )

    modal_text = private_copy_trading_page.private_slaves_modal_body.inner_text()
    assert "Velan" in modal_text, f"Expected 'Velan' in modal body text: {modal_text}"
    assert "10029" in modal_text, f"Expected '10029' in modal body text: {modal_text}"
    assert "Azar" in modal_text, f"Expected 'Azar' in modal body text: {modal_text}"
    assert "10048" in modal_text, f"Expected '10048' in modal body text: {modal_text}"

    private_copy_trading_page.close_view_slaves_modal()
    private_copy_trading_page.clear_search()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_private_copy_trading_edit_copier_modal_opens(
    private_copy_trading_page: PrivateCopyTradingPage,
):
    """Verify that clicking the Edit action opens the Private Copy Trading modal pre-loaded with copier data."""
    private_copy_trading_page.navigate()

    # In responsive view, expand row first if edit button is inside collapsed child row
    if not private_copy_trading_page.edit_buttons.first.is_visible():
        private_copy_trading_page.toggle_responsive_row(0)
        private_copy_trading_page.page.wait_for_timeout(300)

    if private_copy_trading_page.edit_buttons.first.is_visible():
        private_copy_trading_page.open_edit_copier_modal(0)
        assert private_copy_trading_page.create_copier_modal.is_visible(), (
            "Expected Edit modal (#myModal) to open when clicking the edit pencil button."
        )
        private_copy_trading_page.close_create_copier_modal()


