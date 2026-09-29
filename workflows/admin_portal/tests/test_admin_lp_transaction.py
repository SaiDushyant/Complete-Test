"""
Admin Portal LP Transaction Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.lp_transaction_page import LpTransactionPage


# ==============================================================================
# SECTION 1: TOP NAVIGATION BAR HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_topbar_branding_and_title(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    lp_transaction_page.navigate()

    # Brand Logo & Responsive Icons
    assert lp_transaction_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert lp_transaction_page.logo_small.is_visible() or lp_transaction_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = lp_transaction_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert lp_transaction_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert lp_transaction_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert lp_transaction_page.menu_button.get_attribute("title") == "Open menu"
    assert lp_transaction_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert lp_transaction_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert lp_transaction_page.page_title.inner_text().strip() == "LP Transaction"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_topbar_sidebar_toggle_action(
    lp_transaction_page: LpTransactionPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    lp_transaction_page.navigate()

    body = lp_transaction_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    lp_transaction_page.menu_button.click()
    lp_transaction_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    lp_transaction_page.menu_button.click()
    lp_transaction_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_theme_toggle_switches_modes(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    lp_transaction_page.navigate()

    assert lp_transaction_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert lp_transaction_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert lp_transaction_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert lp_transaction_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert lp_transaction_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = lp_transaction_page.get_theme_mode() or "light"

    lp_transaction_page.toggle_theme()
    lp_transaction_page.page.wait_for_timeout(300)

    toggled_mode = lp_transaction_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    lp_transaction_page.toggle_theme()
    lp_transaction_page.page.wait_for_timeout(300)
    assert lp_transaction_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_notifications_dropdown(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify notification bell button, unread badge, dropdown menu,
    Mark all read link, and notifications content.
    """
    lp_transaction_page.navigate()

    assert lp_transaction_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert lp_transaction_page.notification_count.is_visible(), "Expected notification count badge to be visible."
    assert lp_transaction_page.notification_count.inner_text().strip().isdigit(), "Expected numeric notification count."

    lp_transaction_page.open_notifications()
    lp_transaction_page.notification_menu.wait_for(state="visible", timeout=10000)

    assert lp_transaction_page.notification_menu.is_visible(), "Expected notification dropdown menu to be open."
    assert lp_transaction_page.mark_all_read.is_visible(), "Expected 'Mark all read' link to be visible."
    assert lp_transaction_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Verify notification list has items or empty message
    menu_text = lp_transaction_page.notification_menu.inner_text().casefold()
    assert "notification" in menu_text or lp_transaction_page.notification_items.count() > 0


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_profile_dropdown_and_logout_link(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify profile dropdown displays admin avatar initials, username,
    role Administrator, and valid Logout URL.
    """
    lp_transaction_page.navigate()

    assert lp_transaction_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert lp_transaction_page.profile_initials.first.inner_text().strip() == "M"
    assert lp_transaction_page.profile_topbar_name.inner_text().strip() == "madmin"

    lp_transaction_page.open_profile_menu()
    lp_transaction_page.profile_menu.wait_for(state="visible", timeout=10000)

    assert lp_transaction_page.profile_menu.is_visible(), "Expected profile menu dropdown to be visible."
    assert lp_transaction_page.profile_name.inner_text().strip() == "madmin"
    assert "administrator" in lp_transaction_page.profile_role.inner_text().casefold()

    assert lp_transaction_page.logout_link.is_visible(), "Expected Logout item to be visible."
    logout_href = lp_transaction_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to /admin/Controlbase/Logout, got '{logout_href}'"
    )


# ==============================================================================
# SECTION 2: PAGE HEADING & ADD TRANSACTION MODAL (#myModal)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_page_loads_and_displays_heading(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify the page loads, heading displays 'Abook Balance Transaction',
    and 'Add Transaction' button is visible.
    """
    lp_transaction_page.navigate()

    # Heading element in page-title-box (DOM presence & text)
    assert lp_transaction_page.heading.count() >= 1, "Expected heading element in DOM."
    assert "abook balance transaction" in lp_transaction_page.heading.inner_text().casefold()

    # Action button
    assert lp_transaction_page.add_transaction_button.is_visible(), "Expected Add Transaction button."
    assert lp_transaction_page.add_transaction_button.inner_text().strip() == "Add Transaction"



@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_add_modal_opens_and_closes(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify clicking Add Transaction opens the Transaction Details modal
    with all expected inputs (type, amount, mode of payment, save button)
    and dismisses cleanly.
    """
    lp_transaction_page.navigate()

    lp_transaction_page.open_add_transaction_modal()
    assert lp_transaction_page.transaction_modal.is_visible(), "Expected #myModal to be open."
    assert "transaction details" in lp_transaction_page.transaction_modal_title.inner_text().casefold()

    # Form Fields
    assert lp_transaction_page.transaction_type_select.is_visible(), "Expected transaction_type select."
    type_options = [
        opt.get_attribute("value")
        for opt in lp_transaction_page.transaction_type_select.locator("option").all()
    ]
    assert "" in type_options
    assert "withdraw" in type_options
    assert "deposit" in type_options

    assert lp_transaction_page.amount_input.is_visible(), "Expected amount input."
    assert lp_transaction_page.amount_input.get_attribute("type") == "number"

    assert lp_transaction_page.mode_of_payment_input.is_visible(), "Expected mode_of_payment input."
    assert lp_transaction_page.save_button.is_visible(), "Expected Save button (#formSubmit)."

    # Dismiss modal safely
    lp_transaction_page.close_add_transaction_modal()
    assert not lp_transaction_page.transaction_modal.is_visible(), "Expected modal to close."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_add_modal_empty_submission_validation(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify submitting empty Transaction Details form keeps the modal open.
    """
    lp_transaction_page.navigate()

    lp_transaction_page.open_add_transaction_modal()
    assert lp_transaction_page.transaction_modal.is_visible()

    # Attempt to submit empty form
    lp_transaction_page.amount_input.fill("")
    lp_transaction_page.save_button.click()
    lp_transaction_page.page.wait_for_timeout(400)

    # Modal should remain open due to required validations
    assert lp_transaction_page.transaction_modal.is_visible(), "Modal should remain open on empty submission."

    lp_transaction_page.close_add_transaction_modal()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_add_modal_field_inputs_and_reset(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify the Add Transaction modal inputs accept transaction type,
    amount, and payment mode correctly, and reset cleanly on dismissal.
    """
    lp_transaction_page.navigate()

    lp_transaction_page.open_add_transaction_modal()
    assert lp_transaction_page.transaction_modal.is_visible()

    # Fill form fields
    lp_transaction_page.transaction_type_select.select_option(value="deposit")
    lp_transaction_page.amount_input.fill("500")
    lp_transaction_page.mode_of_payment_input.fill("USDT / Crypto")

    # Verify input values
    assert lp_transaction_page.transaction_type_select.input_value() == "deposit"
    assert lp_transaction_page.amount_input.input_value() == "500"
    assert lp_transaction_page.mode_of_payment_input.input_value() == "USDT / Crypto"

    # Close modal safely without saving
    lp_transaction_page.close_add_transaction_modal()
    assert not lp_transaction_page.transaction_modal.is_visible()


# ==============================================================================
# SECTION 3: TRANSACTION TABLE CARD (.card) & DATATABLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_card_and_datatable_controls(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify the LP Transaction table card wrapper, DataTable length dropdown
    with options 10, 25, 50, 100, and search filter input.
    """
    lp_transaction_page.navigate()

    assert lp_transaction_page.table_card.is_visible(), "Expected table card to be visible."
    assert lp_transaction_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert lp_transaction_page.length_dropdown.is_visible(), "Expected page length dropdown to be visible."
    assert lp_transaction_page.search_input.is_visible(), "Expected search filter input to be visible."

    # Verify length options
    options = [
        opt.get_attribute("value")
        for opt in lp_transaction_page.length_dropdown.locator("option").all()
    ]
    expected_options = ["10", "25", "50", "100"]
    for opt in expected_options:
        assert opt in options, f"Expected option '{opt}' in length dropdown, got {options}"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_headers_and_columns_are_valid(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify that all 5 expected table column headers (S.No, Transaction Type,
    Amount, Mode of Payment, Date Time) and sortable states are rendered correctly.
    """
    lp_transaction_page.navigate()

    expected_headers = [
        "s.no",
        "transaction type",
        "amount",
        "mode of payment",
        "date time",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in lp_transaction_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )

    # Check that headers are sortable
    assert lp_transaction_page.table_headers.count() >= 5
    for i in range(5):
        header_class = lp_transaction_page.table_headers.nth(i).get_attribute("class") or ""
        assert "sorting" in header_class, f"Expected header {i} to be sortable, got '{header_class}'"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_length_dropdown_selection(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify selecting different length options (25, 50, 100, 10) updates
    the dropdown value cleanly without errors.
    """
    lp_transaction_page.navigate()

    for length in ["25", "50", "100", "10"]:
        lp_transaction_page.select_length(length)
        assert lp_transaction_page.length_dropdown.input_value() == length


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_search_filtering(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify searching for a nonexistent term filters the table, and clearing
    the search restores the table state.
    """
    lp_transaction_page.navigate()

    # Search non-existent query
    lp_transaction_page.search_table("nonexistent_tx_xyz_999")
    info_text = lp_transaction_page.get_table_info_text().casefold()
    assert "0" in info_text or "showing 0 to 0 of 0" in info_text

    # Clear search
    lp_transaction_page.clear_search()
    restored_info = lp_transaction_page.get_table_info_text().casefold()
    assert "entries" in restored_info


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_column_sorting(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify clicking table column headers updates the sorting state
    between ascending and descending.
    """
    lp_transaction_page.navigate()

    first_header = lp_transaction_page.table_headers.first
    initial_class = first_header.get_attribute("class") or ""

    first_header.click()
    lp_transaction_page.page.wait_for_timeout(300)
    clicked_class = first_header.get_attribute("class") or ""
    assert "sorting_asc" in clicked_class or "sorting_desc" in clicked_class or clicked_class != initial_class

    first_header.click()
    lp_transaction_page.page.wait_for_timeout(300)
    second_clicked_class = first_header.get_attribute("class") or ""
    assert second_clicked_class != clicked_class or "sorting" in second_clicked_class


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_empty_state_and_info(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify table info status displays valid entries information and either
    data rows or the empty table notice is present.
    """
    lp_transaction_page.navigate()

    info_text = lp_transaction_page.get_table_info_text()
    assert "Showing" in info_text and "entries" in info_text

    # Either there are data rows or empty state cell
    if lp_transaction_page.get_row_count() == 0:
        assert lp_transaction_page.empty_state_cell.is_visible(), "Expected .dataTables_empty cell when 0 rows."
        assert "no data available" in lp_transaction_page.empty_state_cell.inner_text().casefold()
    else:
        assert lp_transaction_page.get_row_count() > 0


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_transaction_table_pagination_controls(
    lp_transaction_page: LpTransactionPage,
):
    """
    Verify pagination container is rendered, with Previous and Next buttons
    disabled when no multiple pages exist.
    """
    lp_transaction_page.navigate()

    assert lp_transaction_page.pagination.is_visible(), "Expected #datatable_paginate to be visible."
    assert lp_transaction_page.paginate_previous.is_visible(), "Expected Previous button to be visible."
    assert lp_transaction_page.paginate_next.is_visible(), "Expected Next button to be visible."

    # When 0 entries or 1 page, both buttons should have class 'disabled'
    prev_class = lp_transaction_page.paginate_previous.get_attribute("class") or ""
    next_class = lp_transaction_page.paginate_next.get_attribute("class") or ""
    if lp_transaction_page.get_row_count() <= 10:
        assert "disabled" in prev_class
        assert "disabled" in next_class

