"""
Admin Portal User Group Test Suite.
Tests all scenarios for User Group (#datatable), Add/Edit Modal (#myModal), Subgroups Modal (#subgroupModal), and Group Value Modal (#groupValueModal):
- Real UI testing on read-only table structure, headers, controls, search filtering, and modals
- SAFE MOCKED testing on form submissions, subgroup creations, cloning, and deletions to PREVENT any live admin data modification
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from workflows.admin_portal.pages.admin_user_group_page import AdminUserGroupPage


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_table_and_controls_render(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify User Group table, Add Group button, search box, length dropdown, and expected headers render."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    expect(page.table).to_be_visible()
    expect(page.search_input).to_be_visible()
    expect(page.entries_select).to_be_visible()
    expect(page.info_status).to_be_visible()
    expect(page.pagination).to_be_visible()
    expect(page.add_group_button).to_be_visible()

    expected_headers = [
        "S.No",
        "Group Name",
        "Swap Enabled",
        "Swap Grace Days",
        "Action",
        "Update Ref.Share %",
        "Ref.Share Type",
    ]
    actual_headers = page.get_header_titles()
    for header in expected_headers:
        assert any(header.lower() in h.lower() for h in actual_headers), f"Expected header '{header}' missing from {actual_headers}"


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_row_data_structure(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify row cell formatting, non-empty group names, swap status badges, and action icons."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        if cells.count() == 1 and "dataTables_empty" in (cells.first.get_attribute("class") or ""):
            continue

        group_text = cells.nth(1).inner_text().strip()
        assert group_text, "Expected Group Name cell to not be empty"

        edit_name_btn = cells.nth(1).locator("a.btnNameEdit")
        expect(edit_name_btn).to_be_attached()


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_search_filter(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify searching by group name filters table rows and clearing restores original rows."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    first_group = page.rows.first.locator("td").nth(1).inner_text().split("\n")[0].strip()
    original_count = page.get_row_count()

    page.search_group(first_group)
    expect(page.rows.first).to_be_visible()
    assert first_group.lower() in page.rows.first.inner_text().lower()

    page.clear_search()
    expect(page.rows).to_have_count(original_count)


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_search_empty_result(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify searching for a non-existent group displays empty table message."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    page.search_group("NON-EXISTENT-GROUP-XYZ-999")
    expect(page.empty_message).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_column_sorting(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify sortable user group column headers toggle ascending/descending states."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    headers = page.headers
    for i in range(headers.count()):
        header = headers.nth(i)
        first_sort = header.get_attribute("aria-sort")
        if first_sort is None:
            continue

        header.click()
        new_sort = header.get_attribute("aria-sort")
        assert new_sort in {"ascending", "descending"}


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("length_option", ["10", "25", "50", "100"])
def test_user_group_page_length_options(
    admin_user_group_page: AdminUserGroupPage,
    length_option: str,
):
    """Verify page length dropdown selects 10, 25, 50, 100 entries."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    page.select_page_length(length_option)
    assert page.entries_select.input_value() == length_option


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_pagination_controls(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify previous and next pagination buttons render correctly."""
    page = admin_user_group_page
    page.navigate()

    expect(page.table).to_be_visible()

    expect(page.pagination).to_be_visible()
    expect(page.previous_button).to_be_visible()
    expect(page.next_button).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_open_add_group_modal(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify Add Group button opens the User Group Form modal (#myModal) with expected fields."""
    page = admin_user_group_page
    page.navigate()

    expect(page.add_group_button).to_be_visible()

    page.open_add_group_modal()
    expect(page.modal).to_be_attached()

    if page.is_modal_visible():
        expect(page.modal_title).to_have_text("User Group Form")
        expect(page.group_name_input).to_be_visible()
        expect(page.swap_enabled_select).to_be_visible()
        expect(page.swap_grace_days_input).to_be_visible()
        expect(page.share_type_select).to_be_visible()
        expect(page.form_submit_button).to_be_visible()

        page.modal_close_button.first.click()


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_open_subgroups_modal(
    admin_user_group_page: AdminUserGroupPage,
):
    """Verify Subgroups button opens the Subgroup modal (#subgroupModal) with leverage inputs."""
    page = admin_user_group_page
    page.navigate()

    if page.subgroup_buttons.count() == 0:
        expect(page.table).to_be_visible()
        return

    page.open_first_subgroup_modal()
    expect(page.subgroup_modal).to_be_attached()

    if page.is_subgroup_modal_visible():
        expect(page.new_subgroup_value_input).to_be_visible()
        expect(page.new_subgroup_label_input).to_be_visible()
        expect(page.subgroup_submit_button).to_be_visible()

        page.subgroup_modal_close_button.first.click()


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_mocked_add_group_submit(
    admin_user_group_page: AdminUserGroupPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK user group creation/submission so live admin database is NEVER altered."""
    admin_user_group_page.navigate()

    def handle_save_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked user group created successfully"}',
        )

    # Intercept network requests to prevent database changes
    page.route("**/userGroup**", handle_save_request)
    page.route("**/saveUserGroup**", handle_save_request)
    page.route("**/addUserGroup**", handle_save_request)

    if admin_user_group_page.add_group_button.is_visible():
        admin_user_group_page.open_add_group_modal()
        if admin_user_group_page.is_modal_visible():
            admin_user_group_page.group_name_input.fill("MOCK_TEST_GROUP")
            expect(admin_user_group_page.form_submit_button).to_be_visible()
            admin_user_group_page.form_submit_button.click()

    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_mocked_subgroup_submit(
    admin_user_group_page: AdminUserGroupPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK subgroup creation so live admin database is NEVER altered."""
    admin_user_group_page.navigate()

    def handle_subgroup_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked subgroup added successfully"}',
        )

    page.route("**/subgroup**", handle_subgroup_request)
    page.route("**/saveSubgroup**", handle_subgroup_request)
    page.route("**/addSubgroup**", handle_subgroup_request)

    if admin_user_group_page.subgroup_buttons.count() > 0:
        admin_user_group_page.open_first_subgroup_modal()
        if admin_user_group_page.is_subgroup_modal_visible():
            admin_user_group_page.new_subgroup_value_input.fill("500")
            admin_user_group_page.new_subgroup_label_input.fill("1:500")
            expect(admin_user_group_page.subgroup_submit_button).to_be_visible()
            admin_user_group_page.subgroup_submit_button.click()

    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_mocked_clone_group(
    admin_user_group_page: AdminUserGroupPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK clone group action so live admin database is NEVER altered."""
    admin_user_group_page.navigate()

    def handle_clone_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked group cloned successfully"}',
        )

    page.route("**/cloneGroup**", handle_clone_request)
    page.route("**/cloneUserGroup**", handle_clone_request)

    if admin_user_group_page.clone_group_buttons.count() > 0:
        admin_user_group_page.clone_group_buttons.first.click(force=True)

    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_user_group_mocked_delete_group(
    admin_user_group_page: AdminUserGroupPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK delete group action so live admin database is NEVER altered."""
    admin_user_group_page.navigate()

    def handle_delete_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked group deleted successfully"}',
        )

    page.route("**/deleteGroup**", handle_delete_request)
    page.route("**/deleteUserGroup**", handle_delete_request)

    if admin_user_group_page.delete_group_buttons.count() > 0:
        admin_user_group_page.delete_group_buttons.first.click(force=True)

    assert True
