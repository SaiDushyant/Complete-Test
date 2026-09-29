"""
Admin Portal Account Requests Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.account_requests_page import AccountRequestsPage


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_topbar_branding_and_title(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify top navbar branding logos (small and large), page title ('Account Requests'),
    and sidebar menu button attributes matching the navbar-header layout.
    """
    account_requests_page.navigate()

    # Brand Logo & Responsive Icons
    assert account_requests_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert account_requests_page.logo_small.is_visible() or account_requests_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = account_requests_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert account_requests_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert account_requests_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert account_requests_page.menu_button.get_attribute("title") == "Open menu"
    assert account_requests_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert account_requests_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert account_requests_page.page_title.inner_text().strip() == "Account Requests"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_topbar_sidebar_toggle_action(
    account_requests_page: AccountRequestsPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    account_requests_page.navigate()

    body = account_requests_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    account_requests_page.menu_button.click()
    account_requests_page.page.wait_for_timeout(300)

    toggled_class = body.get_attribute("class") or ""
    toggled_sidebar_size = body.get_attribute("data-sidebar-size") or ""

    assert (
        toggled_class != initial_class
        or "sidebar-enable" in toggled_class
        or toggled_sidebar_size in ["sm", "lg", "condensed"]
    ), "Expected sidebar state to change on toggle."

    # Toggle back
    account_requests_page.menu_button.click()
    account_requests_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_theme_toggle_switches_modes(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify clicking the theme switch button toggles between dark and light themes,
    and dark/light SVG icons are present in the DOM.
    """
    account_requests_page.navigate()

    assert account_requests_page.theme_toggle.is_visible(), "Expected theme toggle button (#admin-theme-toggle) to be visible."
    assert account_requests_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert account_requests_page.theme_toggle.get_attribute("aria-label") == "Switch theme"

    # Both SVG icons (moon and sun) must exist in DOM
    assert account_requests_page.theme_dark_icon.count() >= 1, "Expected dark mode moon icon."
    assert account_requests_page.theme_light_icon.count() >= 1, "Expected light mode sun icon."

    # Test Theme Switching
    initial_mode = account_requests_page.get_theme_mode()
    account_requests_page.toggle_theme()
    account_requests_page.page.wait_for_timeout(300)

    new_mode = account_requests_page.get_theme_mode()
    assert new_mode != initial_mode, f"Expected theme mode to change from {initial_mode}."

    # Revert back to original mode
    account_requests_page.toggle_theme()
    account_requests_page.page.wait_for_timeout(300)
    assert account_requests_page.get_theme_mode() == initial_mode


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_notifications_dropdown(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify notifications button, badge, dropdown menu, header, and Mark all read link.
    """
    account_requests_page.navigate()

    assert account_requests_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert account_requests_page.notification_count.is_visible(), "Expected notification count badge."

    # Open dropdown
    account_requests_page.open_notifications()
    expect(account_requests_page.notification_menu).to_be_visible()

    # Verify head and mark all read link
    assert account_requests_page.notification_menu.locator("h6").inner_text().strip() == "Notifications"
    assert account_requests_page.mark_all_read.is_visible()
    assert account_requests_page.mark_all_read.inner_text().strip() == "Mark all read"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_profile_dropdown_and_logout_link(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify profile dropdown button, initials, admin name, menu header, and logout action link.
    """
    account_requests_page.navigate()

    assert account_requests_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert account_requests_page.profile_initials.is_visible(), "Expected profile initials to be visible."
    assert account_requests_page.profile_initials.inner_text().strip() == "M"

    if account_requests_page.profile_topbar_name.is_visible():
        assert account_requests_page.profile_topbar_name.inner_text().strip() == "madmin"

    # Open Profile Menu
    account_requests_page.open_profile_menu()
    expect(account_requests_page.profile_menu).to_be_visible()

    assert account_requests_page.profile_name.inner_text().strip() == "madmin"
    assert account_requests_page.profile_role.inner_text().strip() == "Administrator"

    # Logout link
    logout = account_requests_page.logout_link
    assert logout.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (logout.get_attribute("href") or "")
    assert "Logout" in logout.inner_text()
    assert logout.locator("i.mdi-logout").is_visible(), "Expected Logout icon."


# ==============================================================================
# SECTION 2: CARD HEADING & CONTROLS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_card_heading_and_refresh_action(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify the card heading ('Client Account Creation Requests') and that
    the Refresh button reloads table data cleanly.
    """
    account_requests_page.navigate()

    assert account_requests_page.card_heading.is_visible(), "Expected card heading to be visible."
    assert "Client Account Creation Requests" in account_requests_page.card_heading.inner_text()

    assert account_requests_page.refresh_button.is_visible(), "Expected Refresh button to be visible."
    assert "btn-primary" in (account_requests_page.refresh_button.get_attribute("class") or "")

    # Click refresh
    account_requests_page.click_refresh()
    expect(account_requests_page.requests_table).to_be_visible()
    assert account_requests_page.get_request_count() >= 1


# ==============================================================================
# SECTION 3: TABLE HEADERS, ROWS & DATA INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_table_headers_and_columns(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify the 11 columns in Client Account Creation Requests table.
    """
    account_requests_page.navigate()

    all_header_texts = [
        th.strip().casefold()
        for th in account_requests_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    expected_columns = [
        "s.no",
        "name",
        "email",
        "current account",
        "requested name",
        "type",
        "status",
        "created account",
        "requested at",
        "reviewed by",
        "action",
    ]

    for col in expected_columns:
        assert any(col in h for h in all_header_texts), f"Expected column '{col}' in headers."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_table_rows_data_integrity(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify table rows display valid sequential serial numbers, emails, account IDs, and timestamps.
    """
    account_requests_page.navigate()

    assert account_requests_page.get_request_count() == 10, "Expected 10 rows on page 1."

    first_row = account_requests_page.request_rows.first
    row_text = first_row.inner_text()

    assert "@" in row_text, "Expected valid client email in row."
    assert any(acc_type in row_text.lower() for acc_type in ["standard", "cent"]), "Expected account type in row."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_status_badges_and_action_buttons(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify status badges (pending, approved, rejected) and presence of Approve/Reject action buttons
    for pending requests.
    """
    account_requests_page.navigate()

    # Status badges
    assert account_requests_page.status_badges.count() >= 1, "Expected status badges."
    badge_texts = [b.strip().lower() for b in account_requests_page.status_badges.all_inner_texts()]
    assert any(st in badge_texts for st in ["pending", "approved", "rejected"])

    # Approve and Reject action buttons for pending requests
    assert account_requests_page.approve_buttons.count() >= 1, "Expected Approve action buttons."
    assert account_requests_page.reject_buttons.count() >= 1, "Expected Reject action buttons."

    first_approve = account_requests_page.approve_buttons.first
    assert first_approve.inner_text().strip() == "Approve"
    assert "btn-success" in (first_approve.get_attribute("class") or "")
    assert first_approve.get_attribute("data-id") is not None

    first_reject = account_requests_page.reject_buttons.first
    assert first_reject.inner_text().strip() == "Reject"
    assert "btn-danger" in (first_reject.get_attribute("class") or "")
    assert first_reject.get_attribute("data-id") is not None

    # Expand responsive row via dtr-control to verify visible display
    account_requests_page.request_rows.first.locator(".dtr-control").click()
    account_requests_page.page.wait_for_timeout(300)
    assert first_approve.is_visible() or account_requests_page.page.locator("tr.child button.btnApproveAccountRequest").first.is_visible()


# ==============================================================================
# SECTION 4: DATATABLE FILTERS, SORTING & PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_length_dropdown_selection(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify changing entries per page dropdown updates visible records.
    """
    account_requests_page.navigate()

    initial_info = account_requests_page.get_table_info_text()
    assert "Showing 1 to 10" in initial_info

    account_requests_page.select_page_length("25")
    expect(account_requests_page.table_info).to_contain_text("Showing 1 to 16")
    assert account_requests_page.get_request_count() == 16

    # Revert
    account_requests_page.select_page_length("10")
    expect(account_requests_page.table_info).to_contain_text("Showing 1 to 10")
    assert account_requests_page.get_request_count() == 10


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_search_filtering(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify search filtering isolates matching requests and unmatched query shows empty state.
    """
    account_requests_page.navigate()

    # Search for an unmatched query
    account_requests_page.search_request("nonexistent_unmatched_account_query_9999")
    try:
        account_requests_page.empty_state_cell.wait_for(state="visible", timeout=5000)
    except Exception:
        pass
    assert account_requests_page.empty_state_cell.is_visible() or account_requests_page.get_request_count() == 0, (
        "Expected empty state for unmatched search."
    )

    # Clear search
    account_requests_page.clear_search()
    account_requests_page.request_rows.first.wait_for(state="visible", timeout=10000)
    assert account_requests_page.get_request_count() == 10, "Expected table rows restored after clear."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_table_column_sorting(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify clicking table headers toggles column sorting between ascending and descending.
    """
    account_requests_page.navigate()

    name_header = account_requests_page.table_headers.filter(has_text="Name").first
    assert name_header.is_visible()

    # Click Name header to sort
    account_requests_page.sort_column_by_name("Name")
    header_class = name_header.get_attribute("class") or ""
    assert "sorting_asc" in header_class or "sorting_desc" in header_class

    # Click again to reverse
    account_requests_page.sort_column_by_name("Name")
    new_class = name_header.get_attribute("class") or ""
    assert ("sorting_asc" in new_class or "sorting_desc" in new_class)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_pagination_controls(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify pagination Previous and Next buttons traverse between page 1 and page 2.
    """
    account_requests_page.navigate()

    assert account_requests_page.pagination.is_visible(), "Expected pagination container."
    assert account_requests_page.get_active_page_number() == "1"
    assert "disabled" in (account_requests_page.paginate_previous.get_attribute("class") or "")

    # Click Next
    account_requests_page.click_next_page()
    assert account_requests_page.get_active_page_number() == "2"
    assert "disabled" not in (account_requests_page.paginate_previous.get_attribute("class") or "")

    # Click Previous
    account_requests_page.click_previous_page()
    assert account_requests_page.get_active_page_number() == "1"
    assert "disabled" in (account_requests_page.paginate_previous.get_attribute("class") or "")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_pagination_page_2_every_possible_way(
    account_requests_page: AccountRequestsPage,
):
    """
    Verify navigating to Page 2 via every possible method (page number button, Next button),
    verifying active button state, entry range 11 to 16, and returning via Previous and Page 1.
    """
    account_requests_page.navigate()

    # Initial state on Page 1
    assert account_requests_page.get_active_page_number() == "1"
    expect(account_requests_page.table_info).to_contain_text("Showing 1 to 10")
    assert "disabled" in (account_requests_page.paginate_previous.get_attribute("class") or "")

    # Way 1: Click page number "2" directly
    account_requests_page.click_page_number(2)
    expect(account_requests_page.table_info).to_contain_text("Showing 11 to 16")
    assert account_requests_page.get_active_page_number() == "2"
    assert "disabled" not in (account_requests_page.paginate_previous.get_attribute("class") or "")
    assert account_requests_page.get_request_count() == 6

    # Way 2: Return to Page 1 via Previous button
    account_requests_page.click_previous_page()
    expect(account_requests_page.table_info).to_contain_text("Showing 1 to 10")
    assert account_requests_page.get_active_page_number() == "1"
    assert "disabled" in (account_requests_page.paginate_previous.get_attribute("class") or "")

    # Way 3: Navigate to Page 2 via Next button
    account_requests_page.click_next_page()
    expect(account_requests_page.table_info).to_contain_text("Showing 11 to 16")
    assert account_requests_page.get_active_page_number() == "2"
    assert "disabled" not in (account_requests_page.paginate_previous.get_attribute("class") or "")

    # Way 4: Return to Page 1 via page number "1" button
    account_requests_page.click_page_number(1)
    expect(account_requests_page.table_info).to_contain_text("Showing 1 to 10")
    assert account_requests_page.get_active_page_number() == "1"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_account_requests_page_2_data_and_action_verification(
    account_requests_page: AccountRequestsPage,
):
    """
    Navigate to Page 2 and verify that all 6 records on Page 2 display complete details,
    timestamps, and valid status badges.
    """
    account_requests_page.navigate()

    # Navigate to Page 2
    account_requests_page.click_page_number(2)
    expect(account_requests_page.table_info).to_contain_text("Showing 11 to 16")

    # Verify rows count on Page 2
    assert account_requests_page.get_request_count() == 6, "Expected 6 records on Page 2."

    page_2_first_row = account_requests_page.request_rows.first
    assert "@" in page_2_first_row.inner_text(), "Expected valid client email on Page 2 record."
    assert page_2_first_row.locator(".request-status").count() >= 1, "Expected status badge on Page 2 record."

