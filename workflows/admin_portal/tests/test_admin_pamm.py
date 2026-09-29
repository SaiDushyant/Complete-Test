"""
Admin Portal Manage PAMM Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.pamm_page import PammPage


# ==============================================================================
# SECTION 1: TOP NAVIGATION BAR HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_topbar_branding_and_title(
    pamm_page: PammPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    pamm_page.navigate()

    # Brand Logo & Responsive Icons
    assert pamm_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert pamm_page.logo_small.is_visible() or pamm_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = pamm_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert pamm_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert pamm_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert pamm_page.menu_button.get_attribute("title") == "Open menu"
    assert pamm_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert pamm_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert pamm_page.page_title.inner_text().strip() == "Manage PAMM"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_topbar_sidebar_toggle_action(
    pamm_page: PammPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    pamm_page.navigate()

    body = pamm_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    pamm_page.menu_button.click()
    pamm_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    pamm_page.menu_button.click()
    pamm_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_theme_toggle_switches_modes(
    pamm_page: PammPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    pamm_page.navigate()

    assert pamm_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert pamm_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert pamm_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert pamm_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert pamm_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = pamm_page.get_theme_mode() or "light"

    pamm_page.toggle_theme()
    pamm_page.page.wait_for_timeout(300)

    toggled_mode = pamm_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    pamm_page.toggle_theme()
    pamm_page.page.wait_for_timeout(300)
    assert pamm_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_notifications_dropdown(
    pamm_page: PammPage,
):
    """
    Verify notification bell button, unread badge, dropdown menu,
    Mark all read link, and notifications content.
    """
    pamm_page.navigate()

    assert pamm_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert pamm_page.notification_count.is_visible(), "Expected notification count badge to be visible."
    assert pamm_page.notification_count.inner_text().strip().isdigit(), "Expected numeric notification count."

    pamm_page.open_notifications()
    pamm_page.notification_menu.wait_for(state="visible", timeout=10000)

    assert pamm_page.notification_menu.is_visible(), "Expected notification dropdown menu to be open."
    assert pamm_page.mark_all_read.is_visible(), "Expected 'Mark all read' link to be visible."
    assert pamm_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Verify notification list has items or empty message
    menu_text = pamm_page.notification_menu.inner_text().casefold()
    assert "notification" in menu_text or pamm_page.notification_items.count() > 0


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_profile_dropdown_and_logout_link(
    pamm_page: PammPage,
):
    """
    Verify profile dropdown displays admin avatar initials, username,
    role Administrator, and valid Logout URL.
    """
    pamm_page.navigate()

    assert pamm_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert pamm_page.profile_initials.first.inner_text().strip() == "M"
    assert pamm_page.profile_topbar_name.inner_text().strip() == "madmin"

    pamm_page.open_profile_menu()
    pamm_page.profile_menu.wait_for(state="visible", timeout=10000)

    assert pamm_page.profile_menu.is_visible(), "Expected profile menu dropdown to be visible."
    assert pamm_page.profile_name.inner_text().strip() == "madmin"
    assert "administrator" in pamm_page.profile_role.inner_text().casefold()

    assert pamm_page.logout_link.is_visible(), "Expected Logout item to be visible."
    logout_href = pamm_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to /admin/Controlbase/Logout, got '{logout_href}'"
    )


# ==============================================================================
# SECTION 2: PAGE HEADING & PAMM REQUESTS MODAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_page_loads_and_displays_heading(
    pamm_page: PammPage,
):
    """Verify that the Admin Manage PAMM page loads and displays the heading."""
    pamm_page.navigate()

    assert pamm_page.is_pamm_displayed(), (
        "Expected Manage PAMM page title and DataTable to be displayed."
    )
    assert pamm_page.page_title.inner_text().strip().casefold() == "manage pamm"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_requests_button_and_modal_structure(
    pamm_page: PammPage,
):
    """
    Verify that the PAMM Requests button displays pending count badge (e.g. 3)
    and opens the requests approval modal.
    """
    pamm_page.navigate()

    btn = pamm_page.pamm_requests_button
    assert btn.is_visible(), "Expected PAMM Requests button to be visible."
    badge_count = pamm_page.get_request_badge_count()
    assert badge_count >= 0, f"Expected non-negative request badge count, got {badge_count}"

    # Open modal
    pamm_page.open_pamm_requests()
    assert pamm_page.pamm_requests_modal.is_visible(), (
        "Expected PAMM Requests modal (#pammRequestsModal) to be visible."
    )
    assert pamm_page.pamm_requests_modal_title.is_visible(), "Expected modal title to be visible."
    assert "pamm requests" in pamm_page.pamm_requests_modal_title.inner_text().casefold()

    # Check requests table and columns
    assert pamm_page.pamm_requests_table.is_visible(), "Expected requests table to be visible."
    expected_headers = ["s.no", "name", "account id", "email", "status", "requested at", "action"]
    actual_headers = [
        th.strip().casefold()
        for th in pamm_page.pamm_requests_table_headers.all_inner_texts()
        if th.strip()
    ]
    for exp in expected_headers:
        assert any(exp in h for h in actual_headers), (
            f"Expected header '{exp}' in requests table, got {actual_headers}"
        )

    # Check Approve & Reject action buttons
    if badge_count > 0:
        assert pamm_page.pamm_requests_approve_buttons.count() >= 1, "Expected Approve button."
        assert pamm_page.pamm_requests_reject_buttons.count() >= 1, "Expected Reject button."

    # Verify Refresh button
    assert pamm_page.pamm_requests_refresh_button.is_visible(), "Expected Refresh button."
    pamm_page.pamm_requests_refresh_button.click()
    pamm_page.page.wait_for_timeout(400)

    # Close modal
    pamm_page.close_pamm_requests()
    assert not pamm_page.pamm_requests_modal.is_visible(), "Expected PAMM Requests modal to be closed."


# ==============================================================================
# SECTION 3: PAMM TABLE CARD & DATATABLE CONTROLS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_table_card_and_datatable_controls(
    pamm_page: PammPage,
):
    """
    Verify the PAMM table card wrapper, DataTable length dropdown with
    options 10, 25, 50, 100, and search filter input.
    """
    pamm_page.navigate()

    assert pamm_page.table_card.is_visible(), "Expected .card.pamm-table-card to be visible."
    assert pamm_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert pamm_page.length_dropdown.is_visible(), "Expected page length dropdown to be visible."
    assert pamm_page.search_input.is_visible(), "Expected search input to be visible."

    # Verify length options
    options = [
        opt.get_attribute("value")
        for opt in pamm_page.length_dropdown.locator("option").all()
    ]
    expected_options = ["10", "25", "50", "100"]
    for opt in expected_options:
        assert opt in options, f"Expected option '{opt}' in length dropdown, got {options}"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_table_headers_and_columns_are_valid(
    pamm_page: PammPage,
):
    """
    Verify that all 6 required table column headers (S.No, PAMM Name, Account ID,
    Rank, Total Followers, Action) and sortable states are rendered correctly.
    """
    pamm_page.navigate()

    expected_headers = [
        "s.no",
        "pamm name",
        "account id",
        "rank",
        "total followers",
        "action",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in pamm_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )

    # First 5 headers are sortable; the 6th (Action) has sorting_disabled
    for i in range(5):
        assert "sorting" in (pamm_page.table_headers.nth(i).get_attribute("class") or "")
    assert "sorting_disabled" in (pamm_page.table_headers.nth(5).get_attribute("class") or "")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_table_rows_data_integrity(
    pamm_page: PammPage,
):
    """
    Verify that PAMM table rows display sequential S.No, PAMM Name with edit pencil,
    numeric Account ID, Rank, Total Followers, and Followers List button with token.
    """
    pamm_page.navigate()

    row_count = pamm_page.get_row_count()
    assert row_count > 0, "Expected at least one PAMM row in table."

    first_row = pamm_page.table_rows.first
    cells = first_row.locator("td").all_inner_texts()
    assert len(cells) >= 6, f"Expected at least 6 cells in row, got {len(cells)}"

    # S.No (1st column) has responsive dtr-control and is numeric
    s_no = cells[0].strip()
    assert s_no.isdigit(), f"Expected numeric S.No, got '{s_no}'"
    assert "dtr-control" in (first_row.locator("td").first.get_attribute("class") or "")

    # PAMM Name has edit pencil button
    assert first_row.locator(".btnNameEdit, a.btnNameEdit").is_visible(), (
        "Expected edit pencil button next to PAMM name."
    )

    # Account ID (3rd column) is numeric
    account_id = cells[2].strip()
    assert account_id.isdigit(), f"Expected numeric Account ID, got '{account_id}'"

    # Rank (4th column) is numeric
    rank = cells[3].strip()
    assert rank.isdigit(), f"Expected numeric Rank, got '{rank}'"

    # Total Followers (5th column) is numeric
    total_followers = cells[4].strip()
    assert total_followers.isdigit(), f"Expected numeric Total Followers, got '{total_followers}'"

    # Action column has Followers List button with data-token
    btn_report = first_row.locator("a.btnReport")
    assert btn_report.is_visible(), "Expected Followers List button in Action column."
    assert btn_report.get_attribute("data-token"), "Expected data-token attribute on Followers List button."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_edit_pamm_name_modal_opens_and_closes(
    pamm_page: PammPage,
):
    """
    Verify clicking the edit pencil next to a PAMM Name opens the PAMM Details modal (#myModalName)
    with the manager's name prefilled, and can be dismissed safely.
    """
    pamm_page.navigate()

    pamm_page.edit_name_buttons.first.wait_for(state="visible", timeout=10000)
    assert pamm_page.edit_name_buttons.count() > 0, "Expected PAMM name edit pencil buttons."

    # Open edit modal
    pamm_page.open_edit_pamm_name_modal(0)
    assert pamm_page.edit_name_modal.is_visible(), "Expected PAMM Details modal (#myModalName) to be visible."
    assert "pamm details" in pamm_page.edit_name_modal_title.inner_text().casefold()

    name_value = pamm_page.edit_name_input.input_value()
    assert len(name_value.strip()) > 0, f"Expected prefilled manager name, got '{name_value}'"
    assert pamm_page.edit_name_submit_button.is_visible(), "Expected Save button (#formSubmitName) to be visible."

    # Close modal safely
    pamm_page.close_edit_pamm_name_modal()
    assert not pamm_page.edit_name_modal.is_visible(), "Expected PAMM Details modal to be closed."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_edit_pamm_name_empty_submission_validation(
    pamm_page: PammPage,
):
    """
    Verify that clearing the PAMM name and attempting to save keeps the modal open
    and does not submit empty data.
    """
    pamm_page.navigate()

    pamm_page.edit_name_buttons.first.wait_for(state="visible", timeout=10000)
    assert pamm_page.edit_name_buttons.count() > 0
    pamm_page.open_edit_pamm_name_modal(0)
    assert pamm_page.edit_name_modal.is_visible()

    original_name = pamm_page.edit_name_input.input_value()

    # Clear name and click Save
    pamm_page.edit_name_input.fill("")
    pamm_page.edit_name_submit_button.click()
    pamm_page.page.wait_for_timeout(400)

    # Modal should remain open
    assert pamm_page.edit_name_modal.is_visible(), (
        "Expected PAMM Details modal to remain open on empty submission."
    )

    # Restore original name and close
    pamm_page.edit_name_input.fill(original_name)
    pamm_page.close_edit_pamm_name_modal()
    assert not pamm_page.edit_name_modal.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_followers_list_zero_count_shows_alert(
    pamm_page: PammPage,
):
    """
    Verify clicking Followers List on a row with 0 followers displays
    the alert dialog ('No followers are assigned to this PAMM.').
    """
    pamm_page.navigate()

    btn_zero = pamm_page.page.locator("a.btnReport[data-count='0']").first
    if btn_zero.is_visible():
        btn_zero.scroll_into_view_if_needed()
        btn_zero.click()
        pamm_page.alert_box.wait_for(state="visible", timeout=15000)

        assert pamm_page.alert_box.is_visible(), "Expected alert popup for zero followers."
        assert "no followers" in pamm_page.alert_content.inner_text().casefold(), (
            "Expected 'No followers are assigned to this PAMM.' in alert content."
        )

        pamm_page.dismiss_alert()
        pamm_page.page.wait_for_timeout(300)
        assert not pamm_page.alert_box.is_visible(), "Expected alert popup to be dismissed."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_followers_list_nonzero_count_expands_subtable(
    pamm_page: PammPage,
):
    """
    Verify clicking Followers List on a row with assigned followers reveals
    the inline subtable with follower details, PAMM share, and action buttons.
    """
    pamm_page.navigate()

    btn_with_followers = pamm_page.page.locator("a.btnReport:not([data-count='0'])").first
    if btn_with_followers.is_visible():
        btn_with_followers.scroll_into_view_if_needed()
        btn_with_followers.click()
        pamm_page.followers_subtable.wait_for(state="visible", timeout=15000)

        assert pamm_page.followers_subtable.is_visible(), "Expected inline followers subtable."

        expected_subtable_headers = [
            "s.no",
            "follower name",
            "account id",
            "pamm share",
            "follower share",
            "date / action",
        ]
        subtable_headers = [
            th.strip().casefold()
            for th in pamm_page.followers_subtable_headers.all_inner_texts()
            if th.strip()
        ]
        for exp in expected_subtable_headers:
            assert any(exp in h for h in subtable_headers), (
                f"Expected header '{exp}' in followers subtable, got {subtable_headers}"
            )

        # Verify follower row cells
        first_follower = pamm_page.followers_subtable_rows.first
        cells = first_follower.locator("td").all_inner_texts()
        assert len(cells) >= 6
        assert cells[2].strip().isdigit(), f"Expected numeric Follower Account ID, got '{cells[2]}'"

        # Verify Unfollow button
        unfollow_btn = first_follower.locator("button.btnPammUnfollow, button:has-text('Unfollow')")
        assert unfollow_btn.is_visible(), "Expected Unfollow button in follower row."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_page_length_selection(
    pamm_page: PammPage,
):
    """
    Verify changing page length dropdown updates visible row count
    and DataTable info status.
    """
    pamm_page.navigate()

    total_rows_initial = pamm_page.get_row_count()
    if total_rows_initial > 10:
        pamm_page.select_page_length("10")
        assert pamm_page.get_row_count() == 10, "Expected 10 rows visible when length set to 10."
        assert "1 to 10" in pamm_page.datatable_info.inner_text().casefold()

        # Revert to 25
        pamm_page.select_page_length("25")
        assert pamm_page.get_row_count() == 25 or pamm_page.get_row_count() == total_rows_initial


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_search_filters_by_pamm_name(
    pamm_page: PammPage,
):
    """Verify that entering a PAMM manager name filters the table rows."""
    pamm_page.navigate()

    initial_count = pamm_page.get_row_count()
    assert initial_count > 0, "Expected rows before searching."

    # Extract PAMM name from first row
    first_name = pamm_page.table_rows.first.locator("td").nth(1).inner_text().strip()
    query = first_name[:8] if len(first_name) > 8 else first_name

    pamm_page.search_pamm(query)
    filtered_count = pamm_page.get_row_count()

    assert 0 < filtered_count <= initial_count, (
        f"Expected filtered results between 1 and {initial_count}, got {filtered_count}."
    )

    pamm_page.clear_search()
    assert pamm_page.get_row_count() == initial_count, (
        "Expected row count restored after clearing search."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_search_filters_by_account_id(
    pamm_page: PammPage,
):
    """Verify that searching by Account ID isolates the matching PAMM manager."""
    pamm_page.navigate()

    initial_count = pamm_page.get_row_count()
    target_ac = pamm_page.table_rows.first.locator("td").nth(2).inner_text().strip()

    pamm_page.search_pamm(target_ac)
    filtered_count = pamm_page.get_row_count()

    assert filtered_count >= 1, f"Expected at least 1 matching row for account '{target_ac}'."
    matched_ac = pamm_page.table_rows.first.locator("td").nth(2).inner_text().strip()
    assert matched_ac == target_ac

    pamm_page.clear_search()
    assert pamm_page.get_row_count() == initial_count


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_search_nonexistent_query_shows_empty_state(
    pamm_page: PammPage,
):
    """Verify that searching for an unknown string displays empty state message."""
    pamm_page.navigate()

    initial_count = pamm_page.get_row_count()
    pamm_page.search_pamm("nonexistent_pamm_manager_xyz_99999")

    row_count = pamm_page.get_row_count()
    if row_count > 0:
        first_row_text = pamm_page.table_rows.first.inner_text().casefold()
        assert "no matching records found" in first_row_text

    pamm_page.clear_search()
    assert pamm_page.get_row_count() == initial_count


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_table_column_sorting(
    pamm_page: PammPage,
):
    """Verify that clicking sortable column headers (Account ID and Total Followers) toggles sorting state."""
    pamm_page.navigate()

    for col_name in ["Account ID", "Total Followers"]:
        header = pamm_page.page.locator(
            f"#datatable thead th:has-text('{col_name}')"
        ).first
        header.wait_for(state="visible", timeout=10000)

        header.click()
        pamm_page.page.wait_for_timeout(400)
        sort_first = header.get_attribute("class") or ""
        assert "sorting_asc" in sort_first or "sorting_desc" in sort_first

        header.click()
        pamm_page.page.wait_for_timeout(400)
        sort_second = header.get_attribute("class") or ""
        assert sort_second != sort_first


@pytest.mark.admin
@pytest.mark.regression
def test_admin_pamm_table_pagination_and_info(
    pamm_page: PammPage,
):
    """Verify that table info status and pagination elements are displayed correctly."""
    pamm_page.navigate()

    assert pamm_page.datatable_info.is_visible()
    info_text = pamm_page.datatable_info.inner_text().strip().casefold()
    assert "showing" in info_text and "entries" in info_text

    assert pamm_page.pagination.is_visible()
    assert pamm_page.pagination_items.count() >= 1
    assert pamm_page.pagination_previous.is_visible()
    assert pamm_page.pagination_next.is_visible()
