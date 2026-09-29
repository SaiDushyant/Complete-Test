"""
Admin Portal Manage MAM Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.mam_page import MamPage


# ==============================================================================
# SECTION 1: TOP NAVIGATION BAR HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_topbar_branding_and_title(
    mam_page: MamPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    mam_page.navigate()

    # Brand Logo & Responsive Icons
    assert mam_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert mam_page.logo_small.is_visible() or mam_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = mam_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert mam_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert mam_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert mam_page.menu_button.get_attribute("title") == "Open menu"
    assert mam_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert mam_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert mam_page.page_title.inner_text().strip() == "Manage MAM"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_topbar_sidebar_toggle_action(
    mam_page: MamPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    mam_page.navigate()

    body = mam_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    mam_page.menu_button.click()
    mam_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    mam_page.menu_button.click()
    mam_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_theme_toggle_switches_modes(
    mam_page: MamPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    mam_page.navigate()

    assert mam_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert mam_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert mam_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert mam_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert mam_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = mam_page.get_theme_mode() or "light"

    mam_page.toggle_theme()
    mam_page.page.wait_for_timeout(300)

    toggled_mode = mam_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    mam_page.toggle_theme()
    mam_page.page.wait_for_timeout(300)
    assert mam_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_notifications_dropdown(
    mam_page: MamPage,
):
    """
    Verify notification bell button, unread badge, dropdown menu,
    Mark all read link, and empty state notice.
    """
    mam_page.navigate()

    assert mam_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert mam_page.notification_count.is_visible(), "Expected notification count badge to be visible."
    assert mam_page.notification_count.inner_text().strip().isdigit(), "Expected numeric notification count."

    mam_page.open_notifications()
    mam_page.notification_menu.wait_for(state="visible", timeout=5000)

    assert mam_page.notification_menu.is_visible(), "Expected notification dropdown menu to be open."
    assert mam_page.mark_all_read.is_visible(), "Expected 'Mark all read' link to be visible."
    assert mam_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Verify notification list empty message
    assert "notification not found" in mam_page.notification_menu.inner_text().casefold(), (
        "Expected 'Notification not found.' in notification list."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_profile_dropdown_and_logout_link(
    mam_page: MamPage,
):
    """
    Verify profile dropdown displays admin avatar initials, username,
    role Administrator, and valid Logout URL.
    """
    mam_page.navigate()

    assert mam_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert mam_page.profile_initials.first.inner_text().strip() == "M"
    assert mam_page.profile_topbar_name.inner_text().strip() == "madmin"

    mam_page.open_profile_menu()
    mam_page.profile_menu.wait_for(state="visible", timeout=5000)

    assert mam_page.profile_menu.is_visible(), "Expected profile menu dropdown to be visible."
    assert mam_page.profile_name.inner_text().strip() == "madmin"
    assert "administrator" in mam_page.profile_role.inner_text().casefold()

    assert mam_page.logout_link.is_visible(), "Expected Logout item to be visible."
    logout_href = mam_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to /admin/Controlbase/Logout, got '{logout_href}'"
    )


# ==============================================================================
# SECTION 2: PAGE TITLE & MAM REQUESTS MODAL
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_page_loads_and_displays_heading(
    mam_page: MamPage,
):
    """Verify that the Admin Manage MAM page loads and displays the heading."""
    mam_page.navigate()

    assert mam_page.is_mam_displayed(), (
        "Expected Manage MAM page title and DataTable to be displayed."
    )
    assert mam_page.page_title.inner_text().strip().casefold() == "manage mam"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_requests_button_and_modal_structure(
    mam_page: MamPage,
):
    """Verify that the MAM Requests button displays the badge and opens the requests modal."""
    mam_page.navigate()

    btn = mam_page.mam_requests_button
    if btn.is_visible():
        badge_count = mam_page.get_request_badge_count()
        assert badge_count >= 0, "Expected non-negative request badge count."

        # Open modal
        mam_page.open_mam_requests()
        assert mam_page.mam_requests_modal.is_visible(), (
            "Expected MAM Requests modal (#mamRequestsModal) to be visible."
        )
        assert mam_page.mam_requests_modal_title.is_visible(), (
            "Expected modal title to be visible."
        )
        assert "mam requests" in mam_page.mam_requests_modal_title.inner_text().casefold()

        # Check table
        assert mam_page.mam_requests_table.is_visible(), (
            "Expected requests table inside modal to be visible."
        )

        expected_headers = ["s.no", "name", "account id", "email", "status", "requested at", "action"]
        actual_headers = [
            th.strip().casefold()
            for th in mam_page.mam_requests_table_headers.all_inner_texts()
            if th.strip()
        ]
        for exp in expected_headers:
            assert any(exp in h for h in actual_headers), (
                f"Expected header '{exp}' in requests table: {actual_headers}"
            )

        # Close modal
        mam_page.close_mam_requests()
        assert not mam_page.mam_requests_modal.is_visible(), (
            "Expected MAM Requests modal to be closed."
        )


@pytest.mark.admin
@pytest.mark.regression
# ==============================================================================
# SECTION 3: MAM TABLE CARD & DATATABLE CONTROLS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_table_card_and_datatable_controls(
    mam_page: MamPage,
):
    """
    Verify the MAM table card wrapper, DataTable length dropdown with
    options 10, 25, 50, 100, and search filter input.
    """
    mam_page.navigate()

    assert mam_page.table_card.is_visible(), "Expected .card.mam-table-card to be visible."
    assert mam_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert mam_page.length_dropdown.is_visible(), "Expected page length dropdown to be visible."
    assert mam_page.search_input.is_visible(), "Expected search input to be visible."

    # Verify length options
    options = [
        opt.get_attribute("value")
        for opt in mam_page.length_dropdown.locator("option").all()
    ]
    expected_options = ["10", "25", "50", "100"]
    for opt in expected_options:
        assert opt in options, f"Expected option '{opt}' in length dropdown, got {options}"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_table_headers_and_columns_are_valid(
    mam_page: MamPage,
):
    """
    Verify that all 6 required table column headers (S.No, MAM Name, Account ID,
    Rank, Total Followers, Action) and sortable states are rendered correctly.
    """
    mam_page.navigate()

    expected_headers = [
        "s.no",
        "mam name",
        "account id",
        "rank",
        "total followers",
        "action",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in mam_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )

    # First 5 headers are sortable; the 6th (Action) has sorting_disabled
    for i in range(5):
        assert "sorting" in (mam_page.table_headers.nth(i).get_attribute("class") or "")
    assert "sorting_disabled" in (mam_page.table_headers.nth(5).get_attribute("class") or "")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_table_rows_data_integrity(
    mam_page: MamPage,
):
    """
    Verify that MAM table rows display sequential S.No, MAM Name with edit pencil,
    numeric Account ID, Rank, Total Followers, and Followers List button with token.
    """
    mam_page.navigate()

    row_count = mam_page.get_row_count()
    assert row_count > 0, "Expected at least one MAM row in table."

    first_row = mam_page.table_rows.first
    cells = first_row.locator("td").all_inner_texts()
    assert len(cells) >= 6, f"Expected at least 6 cells in row, got {len(cells)}"

    # S.No (1st column) has responsive dtr-control and is numeric
    s_no = cells[0].strip()
    assert s_no.isdigit(), f"Expected numeric S.No, got '{s_no}'"
    assert "dtr-control" in (first_row.locator("td").first.get_attribute("class") or "")

    # MAM Name has edit pencil button
    assert first_row.locator(".btnNameEdit, a.btnNameEdit").is_visible(), (
        "Expected edit pencil button next to MAM name."
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
def test_admin_mam_edit_mam_name_modal_opens_and_closes(
    mam_page: MamPage,
):
    """
    Verify clicking the edit pencil next to a MAM Name opens the MAM Details modal (#myModal)
    with the manager's name prefilled, and can be dismissed safely.
    """
    mam_page.navigate()

    assert mam_page.edit_name_buttons.count() > 0, "Expected MAM name edit pencil buttons."

    # Open edit modal
    mam_page.open_edit_mam_modal(0)
    assert mam_page.edit_modal.is_visible(), "Expected MAM Details modal (#myModal) to be visible."
    assert "mam details" in mam_page.edit_modal_title.inner_text().casefold()

    name_value = mam_page.edit_name_input.input_value()
    assert len(name_value.strip()) > 0, f"Expected prefilled manager name, got '{name_value}'"
    assert mam_page.edit_submit_button.is_visible(), "Expected Save button (#formSubmit) to be visible."

    # Close modal safely
    mam_page.close_edit_mam_modal()
    assert not mam_page.edit_modal.is_visible(), "Expected MAM Details modal to be closed."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_edit_mam_name_empty_submission_validation(
    mam_page: MamPage,
):
    """
    Verify that clearing the MAM name and attempting to save keeps the modal open
    and does not submit empty data.
    """
    mam_page.navigate()

    assert mam_page.edit_name_buttons.count() > 0
    mam_page.open_edit_mam_modal(0)
    assert mam_page.edit_modal.is_visible()

    original_name = mam_page.edit_name_input.input_value()

    # Clear name and click Save
    mam_page.edit_name_input.fill("")
    mam_page.edit_submit_button.click()
    mam_page.page.wait_for_timeout(400)

    # Modal should remain open
    assert mam_page.edit_modal.is_visible(), (
        "Expected MAM Details modal to remain open on empty submission."
    )

    # Restore original name and close
    mam_page.edit_name_input.fill(original_name)
    mam_page.close_edit_mam_modal()
    assert not mam_page.edit_modal.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_followers_list_zero_count_shows_alert(
    mam_page: MamPage,
):
    """
    Verify clicking Followers List on a row with 0 followers displays
    the alert dialog ('No followers are assigned to this MAM.').
    """
    mam_page.navigate()

    btn_zero = mam_page.page.locator("a.btnReport[data-count='0']").first
    if btn_zero.is_visible():
        btn_zero.scroll_into_view_if_needed()
        btn_zero.click()
        mam_page.alert_box.wait_for(state="visible", timeout=15000)

        assert mam_page.alert_box.is_visible(), "Expected alert popup for zero followers."
        assert "no followers" in mam_page.alert_content.inner_text().casefold(), (
            "Expected 'No followers are assigned to this MAM.' in alert content."
        )

        mam_page.dismiss_alert()
        mam_page.page.wait_for_timeout(300)
        assert not mam_page.alert_box.is_visible(), "Expected alert popup to be dismissed."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_followers_list_nonzero_count_expands_subtable(
    mam_page: MamPage,
):
    """
    Verify clicking Followers List on a row with assigned followers reveals
    the inline subtable with follower details, MAM share, and action buttons.
    """
    mam_page.navigate()

    btn_with_followers = mam_page.page.locator("a.btnReport:not([data-count='0'])").first
    if btn_with_followers.is_visible():
        btn_with_followers.scroll_into_view_if_needed()
        btn_with_followers.click()
        mam_page.followers_subtable.wait_for(state="visible", timeout=15000)

        assert mam_page.followers_subtable.is_visible(), "Expected inline followers subtable."

        expected_subtable_headers = [
            "s.no",
            "follower name",
            "account id",
            "mam share",
            "follower share",
            "date / action",
        ]
        subtable_headers = [
            th.strip().casefold()
            for th in mam_page.followers_subtable_headers.all_inner_texts()
            if th.strip()
        ]
        for exp in expected_subtable_headers:
            assert any(exp in h for h in subtable_headers), (
                f"Expected header '{exp}' in followers subtable, got {subtable_headers}"
            )

        # Verify follower row cells
        first_follower = mam_page.followers_subtable_rows.first
        cells = first_follower.locator("td").all_inner_texts()
        assert len(cells) >= 6
        assert cells[2].strip().isdigit(), f"Expected numeric Follower Account ID, got '{cells[2]}'"

        # Verify Unfollow button
        unfollow_btn = first_follower.locator("button.btnMamUnfollow")
        assert unfollow_btn.is_visible(), "Expected Unfollow button in follower row."
        assert unfollow_btn.get_attribute("data-manager"), "Expected data-manager attribute."
        assert unfollow_btn.get_attribute("data-follower"), "Expected data-follower attribute."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_edit_mam_share_modal_opens_and_closes(
    mam_page: MamPage,
):
    """
    Verify clicking the edit pencil inside the followers subtable opens the
    User Management / MAM Share modal (#myModal_mam) and can be dismissed safely.
    """
    mam_page.navigate()

    btn_with_followers = mam_page.page.locator("a.btnReport:not([data-count='0'])").first
    if btn_with_followers.is_visible():
        btn_with_followers.scroll_into_view_if_needed()
        btn_with_followers.click()
        mam_page.followers_subtable.wait_for(state="visible", timeout=15000)

        btn_edit_share = mam_page.edit_mam_share_buttons.first
        if btn_edit_share.is_visible():
            mam_page.open_edit_mam_share_modal(0)
            assert mam_page.mam_share_modal.is_visible(), (
                "Expected MAM Share modal (#myModal_mam) to be visible."
            )
            assert mam_page.mam_share_input.is_visible(), (
                "Expected #mam_share input to be visible."
            )
            share_val = mam_page.mam_share_input.input_value()
            assert float(share_val) >= 0, f"Expected non-negative share value, got '{share_val}'"

            # Close modal safely
            mam_page.close_edit_mam_share_modal()
            assert not mam_page.mam_share_modal.is_visible(), (
                "Expected MAM Share modal to be closed."
            )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_page_length_selection(
    mam_page: MamPage,
):
    """
    Verify changing page length dropdown updates visible row count
    and DataTable info status.
    """
    mam_page.navigate()

    total_rows_initial = mam_page.get_row_count()
    if total_rows_initial > 10:
        mam_page.select_page_length("10")
        assert mam_page.get_row_count() == 10, "Expected 10 rows visible when length set to 10."
        assert "1 to 10" in mam_page.datatable_info.inner_text().casefold()

        # Revert to 25
        mam_page.select_page_length("25")
        assert mam_page.get_row_count() == total_rows_initial


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_search_filters_by_mam_name(
    mam_page: MamPage,
):
    """Verify that entering a MAM manager name filters the table rows."""
    mam_page.navigate()

    initial_count = mam_page.get_row_count()
    assert initial_count > 0, "Expected rows before searching."

    # Extract MAM name from first row
    first_name = mam_page.table_rows.first.locator("td").nth(1).inner_text().strip()
    query = first_name[:8] if len(first_name) > 8 else first_name

    mam_page.search_mam(query)
    filtered_count = mam_page.get_row_count()

    assert 0 < filtered_count <= initial_count, (
        f"Expected filtered results between 1 and {initial_count}, got {filtered_count}."
    )

    mam_page.clear_search()
    assert mam_page.get_row_count() == initial_count, (
        "Expected row count restored after clearing search."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_search_filters_by_account_id(
    mam_page: MamPage,
):
    """Verify that searching by Account ID isolates the matching MAM manager."""
    mam_page.navigate()

    initial_count = mam_page.get_row_count()
    target_ac = mam_page.table_rows.first.locator("td").nth(2).inner_text().strip()

    mam_page.search_mam(target_ac)
    filtered_count = mam_page.get_row_count()

    assert filtered_count >= 1, f"Expected at least 1 matching row for account '{target_ac}'."
    matched_ac = mam_page.table_rows.first.locator("td").nth(2).inner_text().strip()
    assert matched_ac == target_ac

    mam_page.clear_search()
    assert mam_page.get_row_count() == initial_count


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_search_nonexistent_query_shows_empty_state(
    mam_page: MamPage,
):
    """Verify that searching for an unknown string displays empty state message."""
    mam_page.navigate()

    initial_count = mam_page.get_row_count()
    mam_page.search_mam("nonexistent_mam_manager_xyz_99999")

    row_count = mam_page.get_row_count()
    if row_count > 0:
        first_row_text = mam_page.table_rows.first.inner_text().casefold()
        assert "no matching records found" in first_row_text

    mam_page.clear_search()
    assert mam_page.get_row_count() == initial_count


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_table_column_sorting(
    mam_page: MamPage,
):
    """Verify that clicking sortable column headers (Account ID and Total Followers) toggles sorting state."""
    mam_page.navigate()

    for col_name in ["Account ID", "Total Followers"]:
        header = mam_page.page.locator(
            f"#datatable thead th:has-text('{col_name}')"
        ).first
        header.wait_for(state="visible", timeout=5000)

        header.click()
        mam_page.page.wait_for_timeout(400)
        sort_first = header.get_attribute("class") or ""
        assert "sorting_asc" in sort_first or "sorting_desc" in sort_first

        header.click()
        mam_page.page.wait_for_timeout(400)
        sort_second = header.get_attribute("class") or ""
        assert sort_second != sort_first


@pytest.mark.admin
@pytest.mark.regression
def test_admin_mam_table_pagination_and_info(
    mam_page: MamPage,
):
    """Verify that table info status and pagination elements are displayed correctly."""
    mam_page.navigate()

    assert mam_page.datatable_info.is_visible()
    info_text = mam_page.datatable_info.inner_text().strip().casefold()
    assert "showing" in info_text and "entries" in info_text

    assert mam_page.pagination.is_visible()
    assert mam_page.pagination_items.count() >= 1
    assert mam_page.pagination_previous.is_visible()
    assert mam_page.pagination_next.is_visible()
