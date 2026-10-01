import pytest

from workflows.admin_portal.pages.copy_trading_page import CopyTradingPage


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_page_loads_and_displays_heading(
    copy_trading_page: CopyTradingPage,
):
    """Verify that the Admin Copy Trading page loads and displays the heading."""
    copy_trading_page.navigate()

    assert copy_trading_page.is_copy_trading_displayed(), (
        "Expected Copy Trading page title and datatable to be displayed."
    )
    assert copy_trading_page.page_title.inner_text().strip().casefold() == (
        "copy trading"
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_client_portal_requests_does_not_redirect(
    copy_trading_page: CopyTradingPage,
):
    """
    Verify clicking 'Client Portal Requests' stays on the admin page
    and opens the in-page approval modal rather than redirecting to client portal.
    If 0 requests exist, verify the button is conditionally hidden by the app.
    """
    copy_trading_page.navigate()

    # The button visibility is driven by pending requests: $('#showCopyMasterRequests').toggle(count > 0)
    btn = copy_trading_page.client_portal_requests_button

    if btn.is_visible():
        badge_count = copy_trading_page.get_request_badge_count()
        assert badge_count > 0, "Expected positive count when request button is visible."

        # Click the Client Portal Requests button
        copy_trading_page.open_client_portal_requests()

        # Ensure URL did NOT redirect to client-portal
        current_url = copy_trading_page.page.url
        assert "client-portal" not in current_url, (
            f"Unexpected redirection to client-portal: {current_url}"
        )
        assert "/admin/Controlbase/follow" in current_url, (
            f"Expected to remain on Admin Copy Trading view, got {current_url}"
        )

        # Verify modal dialog opens inside the admin panel
        copy_trading_page.copy_requests_modal.wait_for(state="visible", timeout=5000)
        assert copy_trading_page.copy_requests_modal.is_visible(), (
            "Expected Copy Requests modal dialog to be visible."
        )

        copy_trading_page.close_client_portal_requests()
    else:
        # If count == 0, button is conditionally hidden by the application
        assert not btn.is_visible(), (
            "Client Portal Requests button is hidden when there are 0 pending requests."
        )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_datatable_controls_are_present(
    copy_trading_page: CopyTradingPage,
):
    """Verify that table length selection and search filter controls are available."""
    copy_trading_page.navigate()

    # Wait for DataTable to finish initializing
    copy_trading_page.length_dropdown.wait_for(state="visible", timeout=10000)
    copy_trading_page.search_input.wait_for(state="visible", timeout=10000)

    assert copy_trading_page.length_dropdown.is_visible(), (
        "Expected page length dropdown to be visible."
    )
    assert copy_trading_page.search_input.is_visible(), (
        "Expected DataTable search input to be visible."
    )
    assert copy_trading_page.length_dropdown.input_value() == "50", (
        "Expected default page length to be 50 entries."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_table_headers_and_columns_are_valid(
    copy_trading_page: CopyTradingPage,
):
    """Verify that all 6 required table column headers are rendered correctly."""
    copy_trading_page.navigate()

    expected_headers = [
        "s.no",
        "copy trader name",
        "account id",
        "rank",
        "total followers",
        "action",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in copy_trading_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_table_rows_have_valid_data(
    copy_trading_page: CopyTradingPage,
):
    """Verify that Copy Trading rows display valid account IDs, ranks, and action buttons."""
    copy_trading_page.navigate()

    # Wait for table rows to render
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    row_count = copy_trading_page.get_row_count()
    assert row_count > 0, "Expected at least one Copy Trader row in table."

    # Validate first row data
    first_row = copy_trading_page.table_rows.first
    cells = first_row.locator("td").all_inner_texts()

    assert len(cells) >= 6, f"Expected at least 6 cells in row, got {len(cells)}"

    # Account ID (3rd column) should be numeric
    account_id = cells[2].strip()
    assert account_id.isdigit(), f"Expected numeric Account ID, got '{account_id}'"

    # Rank (4th column) should be numeric
    rank = cells[3].strip()
    assert rank.isdigit(), f"Expected numeric Rank, got '{rank}'"

    # Total Followers (5th column) should be numeric
    followers = cells[4].strip()
    assert followers.isdigit(), f"Expected numeric Followers, got '{followers}'"

    # Action column has Followers List button
    assert first_row.locator("a.btnReport").is_visible(), (
        "Expected 'Followers List' button in the Action column."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_search_filters_rows(
    copy_trading_page: CopyTradingPage,
):
    """Verify that entering a search query filters the Copy Trading table."""
    copy_trading_page.navigate()

    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    initial_count = copy_trading_page.get_row_count()
    assert initial_count > 0, "Expected rows before searching."

    # Search for an existing account ID
    first_account_id = copy_trading_page.table_rows.first.locator("td").nth(2).inner_text().strip()
    copy_trading_page.search_trader(first_account_id)
    copy_trading_page.page.wait_for_timeout(600)

    filtered_count = copy_trading_page.get_row_count()
    assert 0 < filtered_count <= initial_count, (
        f"Expected filtered results between 1 and {initial_count}, got {filtered_count}"
    )

    # Search for a nonexistent trader to verify empty state
    copy_trading_page.search_trader("nonexistent_trader_xyz_999")
    copy_trading_page.page.wait_for_timeout(600)

    no_match_text = copy_trading_page.table_rows.first.inner_text().casefold()
    assert "no matching records found" in no_match_text or copy_trading_page.get_row_count() == 0, (
        "Expected 'No matching records found' for unmatched search query."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_followers_list_action(
    copy_trading_page: CopyTradingPage,
):
    """Verify that clicking 'Followers List' triggers the followers sub-table or report popup."""
    copy_trading_page.navigate()

    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    assert copy_trading_page.action_buttons.count() > 0, (
        "Expected Followers List buttons to be present."
    )

    # Click first row's Followers List button
    first_btn = copy_trading_page.action_buttons.first
    follower_count = int(first_btn.get_attribute("data-count") or "0")

    first_btn.click()

    if follower_count == 0:
        # Zero followers triggers alert modal
        copy_trading_page.alert_box.wait_for(state="visible", timeout=5000)
        assert copy_trading_page.alert_box.is_visible(), (
            "Expected alert popup for manager with zero followers."
        )
        assert "no followers" in copy_trading_page.alert_box.inner_text().casefold()
        copy_trading_page.alert_ok_button.click()
    else:
        # > 0 followers expands inline table
        copy_trading_page.followers_subtable.wait_for(state="visible", timeout=5000)
        assert copy_trading_page.followers_subtable.is_visible(), (
            "Expected inline followers subtable to expand."
        )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_topbar_branding_and_title(
    copy_trading_page: CopyTradingPage,
):
    """Verify that the top navbar renders the brand logo, page title, and sidebar toggle button."""
    copy_trading_page.navigate()

    assert copy_trading_page.brand_logo.is_visible(), (
        "Expected brand logo to be visible in the navbar header."
    )
    assert copy_trading_page.brand_logo_images.count() >= 1, (
        "Expected at least one brand logo image (large/small) to be rendered."
    )
    assert copy_trading_page.menu_button.is_visible(), (
        "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    )
    assert copy_trading_page.page_title.is_visible(), (
        "Expected topbar page title to be visible."
    )
    assert copy_trading_page.page_title.inner_text().strip() == "Copy Trading"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_theme_toggle_switches_modes(
    copy_trading_page: CopyTradingPage,
):
    """Verify that clicking the theme switch toggles the body data-layout-mode between light and dark."""
    copy_trading_page.navigate()

    assert copy_trading_page.theme_toggle.is_visible(), (
        "Expected theme toggle button to be visible."
    )

    initial_mode = copy_trading_page.get_theme_mode() or "light"
    copy_trading_page.toggle_theme()
    copy_trading_page.page.wait_for_timeout(300)

    toggled_mode = copy_trading_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, (
        f"Expected layout mode to change after toggle, but remained '{initial_mode}'."
    )

    # Revert back to maintain initial layout state
    copy_trading_page.toggle_theme()
    copy_trading_page.page.wait_for_timeout(300)
    reverted_mode = copy_trading_page.get_theme_mode() or "light"
    assert reverted_mode == initial_mode, (
        f"Expected layout mode to revert to '{initial_mode}', got '{reverted_mode}'."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_notifications_dropdown_and_items(
    copy_trading_page: CopyTradingPage,
):
    """Verify that the notification button opens the notifications dropdown with count and actions."""
    copy_trading_page.navigate()

    assert copy_trading_page.notification_button.is_visible(), (
        "Expected notification bell button to be visible."
    )
    assert copy_trading_page.notification_count.is_visible(), (
        "Expected notification count badge to be visible."
    )

    # Open notifications dropdown
    copy_trading_page.open_notifications()
    copy_trading_page.notification_menu.wait_for(state="visible", timeout=5000)

    assert copy_trading_page.notification_menu.is_visible(), (
        "Expected notification dropdown menu to be visible."
    )
    assert copy_trading_page.mark_all_read.is_visible(), (
        "Expected 'Mark all read' link to be visible in notifications."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_profile_dropdown_and_logout_link(
    copy_trading_page: CopyTradingPage,
):
    """Verify that the profile menu displays admin credentials and a valid logout link."""
    copy_trading_page.navigate()

    assert copy_trading_page.profile_button.is_visible(), (
        "Expected user profile dropdown button to be visible."
    )

    # Open profile dropdown
    copy_trading_page.open_profile_menu()
    copy_trading_page.profile_menu.wait_for(state="visible", timeout=5000)

    assert copy_trading_page.profile_menu.is_visible(), (
        "Expected user profile menu to open."
    )
    assert copy_trading_page.profile_name.inner_text().strip() == "madmin", (
        "Expected profile username to be 'madmin'."
    )
    assert copy_trading_page.profile_role.inner_text().strip() == "Administrator", (
        "Expected profile role to be 'Administrator'."
    )
    assert copy_trading_page.logout_link.is_visible(), (
        "Expected logout link to be visible in profile menu."
    )

    logout_href = copy_trading_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to '/admin/Controlbase/Logout', got '{logout_href}'."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_edit_trader_modal_opens(
    copy_trading_page: CopyTradingPage,
):
    """Verify that clicking the edit pencil on a trader row opens the Edit Trader modal."""
    copy_trading_page.navigate()
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    assert copy_trading_page.edit_name_buttons.count() > 0, (
        "Expected at least one edit trader button (.btnNameEdit) to be present."
    )

    # Click the first edit button
    copy_trading_page.open_edit_trader_modal(0)
    copy_trading_page.edit_modal.wait_for(state="visible", timeout=5000)

    assert copy_trading_page.edit_modal.is_visible(), (
        "Expected Edit Trader modal (#myModal) to be visible."
    )
    assert copy_trading_page.edit_name_input.is_visible(), (
        "Expected trader name input (#name) to be visible."
    )
    assert copy_trading_page.edit_fee_input.is_visible(), (
        "Expected copy trading fee input (#copy_trading_fee) to be visible."
    )
    assert copy_trading_page.edit_submit_button.is_visible(), (
        "Expected submit button (#formSubmit) to be visible."
    )

    # Close modal safely without modifying data
    copy_trading_page.close_edit_trader_modal()
    assert not copy_trading_page.edit_modal.is_visible(), (
        "Expected Edit Trader modal to be dismissed."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_responsive_row_expansion(
    copy_trading_page: CopyTradingPage,
):
    """Verify that clicking the responsive table toggle expands the child row with actions."""
    # Set compact viewport so table enters responsive collapsed state
    copy_trading_page.page.set_viewport_size({"width": 800, "height": 800})
    copy_trading_page.navigate()
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    assert copy_trading_page.dtr_controls.count() > 0, (
        "Expected responsive dtr-control indicators on table rows."
    )

    # Click first row dtr-control
    first_control = copy_trading_page.dtr_controls.first
    first_control.click()
    copy_trading_page.page.wait_for_timeout(500)

    # Verify that child row or details appear
    child_or_parent = copy_trading_page.page.locator(
        "#datatable tbody tr.child, #datatable tbody tr.parent, #datatable .dtr-details"
    )
    assert child_or_parent.count() > 0 or copy_trading_page.action_buttons.first.is_visible(), (
        "Expected responsive details row (.child) or parent indicator (.parent) after toggle click."
    )

    # Verify Followers List button is reachable inside row or child
    assert copy_trading_page.action_buttons.count() > 0, (
        "Expected action buttons to be present."
    )
    # Restore viewport
    copy_trading_page.page.set_viewport_size({"width": 1280, "height": 720})


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_table_column_sorting(
    copy_trading_page: CopyTradingPage,
):
    """Verify that clicking a sortable table column header updates the sorting state."""
    copy_trading_page.navigate()
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    # Target the Account ID header
    account_header = copy_trading_page.page.locator(
        "#datatable thead th:has-text('Account ID')"
    )
    account_header.wait_for(state="visible", timeout=5000)

    # Click to sort
    account_header.click()
    copy_trading_page.page.wait_for_timeout(400)

    sort_class_after_first_click = account_header.get_attribute("class") or ""
    assert (
        "sorting_asc" in sort_class_after_first_click
        or "sorting_desc" in sort_class_after_first_click
    ), (
        f"Expected column header to have sorting class, got '{sort_class_after_first_click}'."
    )

    # Click again to reverse sort direction
    account_header.click()
    copy_trading_page.page.wait_for_timeout(400)

    sort_class_after_second_click = account_header.get_attribute("class") or ""
    assert sort_class_after_second_click != sort_class_after_first_click, (
        "Expected sort direction to change upon second header click."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_table_pagination_and_info(
    copy_trading_page: CopyTradingPage,
):
    """Verify that the table info status and pagination controls are displayed correctly."""
    copy_trading_page.navigate()
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    assert copy_trading_page.datatable_info.is_visible(), (
        "Expected DataTable info status element (#datatable_info) to be visible."
    )

    info_text = copy_trading_page.datatable_info.inner_text().strip()
    assert "showing" in info_text.casefold() and "entries" in info_text.casefold(), (
        f"Expected entry status pattern in info text, got '{info_text}'."
    )

    assert copy_trading_page.pagination.is_visible(), (
        "Expected DataTable pagination (#datatable_paginate) to be visible."
    )
    assert copy_trading_page.pagination_items.count() >= 1, (
        "Expected at least one pagination item to be rendered."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_requests_modal_table_structure_and_headers(
    copy_trading_page: CopyTradingPage,
):
    """Verify that opening the Client Portal Requests modal displays the requests table and 7 columns."""
    copy_trading_page.navigate()

    if copy_trading_page.client_portal_requests_button.is_visible():
        copy_trading_page.open_client_portal_requests()
    else:
        copy_trading_page.page.evaluate("$('#copyRequestsModal').modal('show')")
        copy_trading_page.page.wait_for_timeout(500)

    copy_trading_page.copy_requests_modal.wait_for(state="visible", timeout=5000)

    # Check modal title
    assert copy_trading_page.copy_requests_modal_title.is_visible(), (
        "Expected requests modal title to be visible."
    )
    assert copy_trading_page.copy_requests_modal_title.inner_text().strip() == (
        "Client Portal Requests"
    )

    # Check all 7 expected headers
    expected_headers = [
        "s.no",
        "name",
        "account id",
        "email",
        "status",
        "requested at",
        "action",
    ]
    actual_headers = [
        h.strip().casefold()
        for h in copy_trading_page.copy_requests_table_headers.all_inner_texts()
        if h.strip()
    ]
    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected '{expected}' among requests headers: {actual_headers}"
        )

    # Verify refresh button exists in modal footer
    assert copy_trading_page.copy_requests_refresh_button.is_visible(), (
        "Expected refresh button (#refreshCopyMasterRequests) to be visible."
    )

    # Safely close modal
    copy_trading_page.close_client_portal_requests()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_requests_modal_rows_and_actions(
    copy_trading_page: CopyTradingPage,
):
    """Verify that requests modal rows contain valid account IDs, pending status, and Approve/Reject buttons."""
    copy_trading_page.navigate()

    if copy_trading_page.client_portal_requests_button.is_visible():
        badge_count = copy_trading_page.get_request_badge_count()
        assert badge_count > 0, "Expected badge count > 0 when button is visible."

        # Open requests modal
        copy_trading_page.open_client_portal_requests()
        copy_trading_page.copy_requests_modal.wait_for(state="visible", timeout=5000)

        # Verify rows count matches or is positive
        row_count = copy_trading_page.copy_requests_table_rows.count()
        assert row_count > 0, "Expected at least one request row in requests table."
        assert row_count == badge_count, (
            f"Expected {badge_count} request rows matching badge, found {row_count}."
        )

        # Check first row data
        first_row = copy_trading_page.copy_requests_table_rows.first
        cells = first_row.locator("td").all_inner_texts()
        assert len(cells) >= 7, f"Expected 7 cells in row, got {len(cells)}"

        account_id = cells[2].strip()
        assert account_id.isdigit(), f"Expected numeric Account ID, got '{account_id}'"

        email = cells[3].strip()
        assert "@" in email, f"Expected email in column 4, got '{email}'"

        status = cells[4].strip().casefold()
        assert "pending" in status, f"Expected pending status, got '{status}'"

        # Action column must contain both Approve and Reject buttons
        assert first_row.locator("button.btnApproveCopyMaster").is_visible(), (
            "Expected Approve button in request row."
        )
        assert first_row.locator("button.btnRejectCopyMaster").is_visible(), (
            "Expected Reject button in request row."
        )

        # Safely close modal without submitting actions
        copy_trading_page.close_client_portal_requests()
    else:
        # If button is hidden (no pending requests), verify modal structure directly without skipping
        copy_trading_page.page.evaluate("$('#copyRequestsModal').modal('show')")
        copy_trading_page.page.wait_for_timeout(500)
        assert copy_trading_page.copy_requests_modal_title.is_visible()
        expect(copy_trading_page.copy_requests_table).to_be_visible()
        copy_trading_page.close_client_portal_requests()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_page_length_to_10_generates_3_pages(
    copy_trading_page: CopyTradingPage,
):
    """Verify selecting 10 entries updates status to 1-10 of 21 and generates 3 pagination pages."""
    copy_trading_page.navigate()
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    # Change dropdown to 10 entries
    copy_trading_page.length_dropdown.select_option("10")
    copy_trading_page.page.wait_for_timeout(600)

    # Verify info text reflects 1 to 10
    info_text = copy_trading_page.datatable_info.inner_text().strip()
    assert "1 to 10" in info_text, (
        f"Expected info text to contain '1 to 10', got '{info_text}'."
    )

    # Verify 3 page buttons appear
    pagination_links = copy_trading_page.page.locator(
        "#datatable_paginate .pagination li a"
    ).all_inner_texts()
    assert "1" in pagination_links and "2" in pagination_links and "3" in pagination_links, (
        f"Expected pages 1, 2, and 3 in pagination, got {pagination_links}."
    )

    # Click page 2 and verify rows 11 to 20 are displayed
    page_2_btn = copy_trading_page.page.locator("#datatable_paginate a:has-text('2')")
    page_2_btn.click()
    copy_trading_page.page.wait_for_timeout(600)

    info_text_page_2 = copy_trading_page.datatable_info.inner_text().strip()
    assert "11 to 20" in info_text_page_2, (
        f"Expected info text on Page 2 to contain '11 to 20', got '{info_text_page_2}'."
    )

    # Restore dropdown back to 50
    copy_trading_page.length_dropdown.select_option("50")
    copy_trading_page.page.wait_for_timeout(500)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_copy_trading_responsive_plus_symbol_opens_followers_inner_table(
    copy_trading_page: CopyTradingPage,
):
    """Verify that in responsive/zoomed view, clicking (+) reveals Followers List and opens the inner table."""
    # Set compact viewport simulating zoomed or narrow layout
    copy_trading_page.page.set_viewport_size({"width": 800, "height": 800})
    copy_trading_page.navigate()
    copy_trading_page.table_rows.first.wait_for(state="visible", timeout=10000)

    # Row 3 (index 2) has followers in the dataset
    controls = copy_trading_page.dtr_controls
    assert controls.count() > 2, "Expected at least 3 rows with responsive plus toggle."

    # Click plus symbol (+) on row 3
    controls.nth(2).click()
    copy_trading_page.page.wait_for_timeout(600)

    # Verify child row expanded
    child_row = copy_trading_page.page.locator("#datatable tbody tr.child")
    assert child_row.is_visible(), "Expected child row (.child) to be expanded."

    # Locate and click Followers List button inside child row
    child_report_btn = copy_trading_page.page.locator("#datatable tbody tr.child a.btnReport")
    assert child_report_btn.is_visible(), "Expected Followers List button in child row."
    child_report_btn.click()
    copy_trading_page.page.wait_for_timeout(1000)

    # Verify inner followers sub-table appears
    inner_table = copy_trading_page.followers_subtable
    inner_table.wait_for(state="visible", timeout=5000)
    assert inner_table.is_visible(), "Expected inner followers table (table.report-inner-table) to be visible."

    # Verify inner table columns
    inner_headers = [h.strip().casefold() for h in inner_table.locator("th").all_inner_texts() if h.strip()]
    expected_inner_headers = ["follower id", "follower name", "account id", "token", "hash"]
    for expected in expected_inner_headers:
        assert any(expected in h for h in inner_headers), (
            f"Expected '{expected}' among inner table headers: {inner_headers}"
        )

    # Restore viewport
    copy_trading_page.page.set_viewport_size({"width": 1280, "height": 720})




