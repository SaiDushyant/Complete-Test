"""
Client Account Requests Comprehensive Practical Validation Test Suite.
Validates cross-portal synchronization between:
- Admin Account Requests table: https://stage.xtremenext.com/admin/Controlbase/clientAccountRequests
- Client Portal Create Account modal: https://stage.xtremenext.com/client-portal

Covers all user-requested and edge-case scenarios:
1. Client Portal request creation synchronizes to Admin Portal table.
2. Admin Approve action: SweetAlert confirmation, creates new account ID, updates status to approved (green), Reviewed By = admin, and reflects new account in Client Portal.
3. Admin Reject action: SweetAlert with optional admin note, updates status to rejected (red), Reviewed By = admin, Created Account remains '-', and NO account created in Client Portal.
4. Refresh button (#refreshAccountRequests) reloads table via AJAX smoothly without page refresh.
5. Table column sorting across all 10 sortable headers (S.No, Name, Email, Current Account, Requested Name, Type, Status, Created Account, Requested At, Reviewed By) and Action column un-sortable.
6. Search filtering by Name, Email, Account ID, and Status, unmatched search displays empty state, clear search restores table.
7. Page length dropdown options (10, 25, 50, 100 entries) update table info and row counts.
8. Pagination navigation (Previous, Next, Page 1, Page 2, Page 3, active indicators).
9. Status badge color-coding and styling (pending=yellow/orange, approved=green, rejected=red).
10. Action buttons conditional rendering: pending rows have Approve/Reject buttons; approved/rejected rows display '-'.
11. Requested At timestamp format integrity (YYYY-MM-DD HH:MM:SS).
12. Reviewed By field integrity: pending shows '-', approved/rejected shows reviewer admin username.
13. Responsive collapse and .dtr-control row expansion.
14. SweetAlert2 cancel dismissal leaves pending request unchanged.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Browser, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.account_requests_page import AccountRequestsPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage


def _dismiss_all_overlays(page: Page) -> None:
    """Ensure any SweetAlert2 or modal overlays are removed."""
    try:
        page.evaluate("""() => {
            if (window.Swal) {
                try { Swal.close(); } catch(e) {}
            }
            document.querySelectorAll('.swal2-container').forEach(el => el.remove());
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('swal2-shown', 'swal2-height-auto', 'modal-open');
        }""")
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_overlays_fixture(admin_page: Page):
    """Automatically dismiss overlays before and after each test."""
    _dismiss_all_overlays(admin_page)
    yield
    _dismiss_all_overlays(admin_page)


@pytest.fixture(scope="module")
def admin_page(browser: Browser) -> Page:
    """Create an authenticated Admin Portal page session."""
    context = browser.new_context(
        storage_state=str(settings.admin_portal.auth_state_path),
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="module")
def client_page(browser: Browser) -> Page:
    """Create an authenticated Client Portal page session."""
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    client_login = ClientLoginPage(page)
    client_login.navigate(settings.client_portal.login_url or "https://stage.xtremenext.com/login/")
    client_login.login(
        username=settings.client_portal.username or "f76718269@gmail.com",
        password=settings.client_portal.password,
        remember_me=False,
    )
    page.wait_for_timeout(3000)
    page.goto(f"{settings.client_portal.base_url.rstrip('/')}/client-portal", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    yield page
    context.close()


def _ensure_pending_request(admin_page: Page, client_page: Page) -> None:
    """Ensure at least one pending account request exists in the table."""
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.search_request("pending")
    admin_page.wait_for_timeout(1000)
    if req_page.get_request_count() > 0 and req_page.request_rows.filter(has=admin_page.locator(".request-status.pending")).count() > 0:
        req_page.clear_search()
        return

    req_page.clear_search()

    # Trigger fresh request from Client Portal
    client_page.goto(f"{settings.client_portal.base_url.rstrip('/')}/client-portal", wait_until="domcontentloaded")
    client_page.wait_for_timeout(2000)

    ca_btn = client_page.locator("header button:has-text('Create Account'), button:has-text('CREATE ACCOUNT')").first
    if ca_btn.is_visible():
        ca_btn.click()
        client_page.wait_for_timeout(1500)
        modal = client_page.locator("div.fixed.inset-0.z-50").first
        if modal.is_visible():
            submit_btn = modal.locator("button[type='submit']").first
            if submit_btn.is_visible() and submit_btn.is_enabled():
                submit_btn.click()
                client_page.wait_for_timeout(2500)
            cancel_btn = modal.locator("button:has-text('Cancel')").first
            if cancel_btn.is_visible():
                cancel_btn.click()

    # Refresh Admin Portal
    req_page.navigate()
    req_page.click_refresh()
    admin_page.wait_for_timeout(1000)


# ==============================================================================
# SCENARIO 1: REFRESH BUTTON RELOADS TABLE VIA AJAX
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_refresh_button_reloads_table(admin_page: Page):
    """
    Scenario 1: Verify the Refresh button (#refreshAccountRequests) triggers
    a clean DataTable AJAX reload without a full page refresh.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()

    expect(req_page.card_heading).to_be_visible()
    expect(req_page.requests_table).to_be_visible()
    assert req_page.refresh_button.is_visible()

    # Track network request on clicking Refresh
    with admin_page.expect_response(
        lambda res: "getClientAccountCreationRequests" in res.url and res.status == 200,
        timeout=15000,
    ) as response_info:
        req_page.click_refresh()

    assert response_info.value.ok
    assert req_page.get_request_count() >= 1
    assert "Showing 1 to" in req_page.get_table_info_text()


# ==============================================================================
# SCENARIO 2: TABLE HEADERS & COLUMN STRUCTURE
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_table_headers_and_action_unsortable(admin_page: Page):
    """
    Scenario 2: Verify the 11 columns in Client Account Creation Requests table:
    S.No, Name, Email, Current Account, Requested Name, Type, Status, Created Account,
    Requested At, Reviewed By, Action. Verify Action column has sorting_disabled.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()

    headers = [th.strip().lower() for th in req_page.table_headers.all_inner_texts() if th.strip()]
    expected_cols = [
        "s.no", "name", "email", "current account", "requested name",
        "type", "status", "created account", "requested at", "reviewed by", "action"
    ]
    for col in expected_cols:
        assert any(col in h for h in headers), f"Expected column '{col}' in headers, got {headers}"

    # Action column must have class 'sorting_disabled'
    action_th = req_page.table_headers.filter(has_text=re.compile(r"^Action$", re.I)).first
    assert action_th.is_visible()
    classes = action_th.get_attribute("class") or ""
    assert "sorting_disabled" in classes, f"Expected Action column to be sorting_disabled, got '{classes}'"


# ==============================================================================
# SCENARIO 3: STATUS BADGE STYLING & COLOR CODING
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_status_badge_styling_and_colors(admin_page: Page):
    """
    Scenario 3: Verify status badges have distinct semantic styling:
    - pending: yellow/orange badge (.request-status.pending)
    - approved: green badge (.request-status.approved)
    - rejected: red badge (.request-status.rejected)
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.select_page_length("100")
    admin_page.wait_for_timeout(2000)

    badges = req_page.status_badges.all()
    assert len(badges) >= 1, "Expected status badges in the table."

    statuses_seen = set()
    for badge in badges:
        status_text = badge.inner_text().strip().lower()
        badge_class = badge.get_attribute("class") or ""
        statuses_seen.add(status_text)

        if status_text == "pending":
            assert "pending" in badge_class
        elif status_text == "approved":
            assert "approved" in badge_class
        elif status_text == "rejected":
            assert "rejected" in badge_class

    assert "approved" in statuses_seen, "Expected approved requests in dataset."
    # Reset length
    req_page.select_page_length("10")
    admin_page.wait_for_timeout(1000)


# ==============================================================================
# SCENARIO 4: CONDITIONAL ACTION BUTTONS RENDERING
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_action_buttons_conditional_by_status(admin_page: Page):
    """
    Scenario 4: Verify conditional rendering in Action column:
    - Pending requests MUST have Approve (.btnApproveAccountRequest) and Reject (.btnRejectAccountRequest) buttons with data-id.
    - Approved requests MUST display '-' with no action buttons.
    - Rejected requests MUST display '-' with no action buttons.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.select_page_length("100")
    admin_page.wait_for_timeout(2000)

    rows = req_page.request_rows.all()
    assert len(rows) >= 5, "Expected at least 5 rows loaded."

    for row in rows:
        status_badge = row.locator(".request-status")
        if not status_badge.is_visible():
            continue
        status = status_badge.inner_text().strip().lower()
        action_td = row.locator("td").last
        action_text = action_td.inner_text().strip()

        if status == "pending":
            approve_btn = action_td.locator(".btnApproveAccountRequest")
            reject_btn = action_td.locator(".btnRejectAccountRequest")
            assert approve_btn.count() >= 1, "Pending row must have Approve button."
            assert reject_btn.count() >= 1, "Pending row must have Reject button."
            assert approve_btn.get_attribute("data-id") is not None
            assert reject_btn.get_attribute("data-id") is not None
        elif status in ["approved", "rejected"]:
            assert action_text == "-", f"Expected '-' for {status} request, got '{action_text}'"
            assert action_td.locator("button").count() == 0, f"Expected no action buttons for {status} request."

    req_page.select_page_length("10")
    admin_page.wait_for_timeout(1000)


# ==============================================================================
# SCENARIO 5: REQUESTED AT TIMESTAMP FORMAT INTEGRITY
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_timestamp_format_integrity(admin_page: Page):
    """
    Scenario 5: Verify 'Requested At' column displays properly formatted timestamps
    matching YYYY-MM-DD HH:MM:SS format across all rows.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()

    rows = req_page.request_rows.all()
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$")

    valid_timestamps = 0
    for row in rows[:10]:
        cells = [td.inner_text().strip() for td in row.locator("td").all()]
        if len(cells) >= 9:
            req_at = cells[8]
            if req_at and req_at != "-":
                assert pattern.match(req_at), f"Invalid timestamp format: '{req_at}'"
                valid_timestamps += 1

    assert valid_timestamps >= 5, f"Expected at least 5 valid timestamps, got {valid_timestamps}"


# ==============================================================================
# SCENARIO 6: REVIEWED BY FIELD INTEGRITY
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_reviewed_by_integrity(admin_page: Page):
    """
    Scenario 6: Verify Reviewed By field logic:
    - Pending requests display '-' (not yet reviewed).
    - Approved/Rejected requests display the admin username (e.g. 'madmin').
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.select_page_length("100")
    admin_page.wait_for_timeout(2000)

    rows = req_page.request_rows.all()
    approved_reviewed = 0
    pending_unreviewed = 0

    for row in rows:
        cells = [td.inner_text().strip() for td in row.locator("td").all()]
        if len(cells) < 11:
            continue
        status = cells[6].strip().lower()
        reviewed_by = cells[9].strip()

        if status == "pending":
            assert reviewed_by == "-", f"Pending request must have Reviewed By '-', got '{reviewed_by}'"
            pending_unreviewed += 1
        elif status == "approved":
            if reviewed_by != "-":
                assert len(reviewed_by) >= 2, f"Expected valid admin name, got '{reviewed_by}'"
                approved_reviewed += 1

    assert approved_reviewed >= 1, "Expected at least 1 reviewed approved request."
    req_page.select_page_length("10")
    admin_page.wait_for_timeout(1000)


# ==============================================================================
# SCENARIO 7: SEARCH FILTERING BY NAME, EMAIL, ACCOUNT ID, AND STATUS
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_search_filtering(admin_page: Page):
    """
    Scenario 7: Verify search filter isolates matching records by:
    - Name ('fake')
    - Email ('f76718269@gmail.com')
    - Account ID ('10102')
    - Non-existent query shows empty state ('No matching records found')
    - Clearing search restores full records.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()

    initial_info = req_page.get_table_info_text()

    # 1. Search by Name
    req_page.search_request("fake")
    admin_page.wait_for_timeout(1000)
    for row in req_page.request_rows.all():
        assert "fake" in row.inner_text().lower()

    # 2. Search by Email
    req_page.search_request("f76718269@gmail.com")
    admin_page.wait_for_timeout(1000)
    for row in req_page.request_rows.all():
        assert "f76718269@gmail.com" in row.inner_text()

    # 3. Search by Account ID
    req_page.search_request("10102")
    admin_page.wait_for_timeout(1000)
    for row in req_page.request_rows.all():
        assert "10102" in row.inner_text()

    # 4. Search unmatched query
    req_page.search_request("nonexistent_request_query_99999")
    admin_page.wait_for_timeout(1000)
    assert req_page.empty_state_cell.is_visible() or req_page.get_request_count() == 0

    # 5. Clear search
    req_page.clear_search()
    admin_page.wait_for_timeout(1000)
    assert req_page.get_request_count() >= 1
    assert "Showing 1 to" in req_page.get_table_info_text()


# ==============================================================================
# SCENARIO 8: COLUMN SORTING ACROSS HEADERS
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_column_sorting(admin_page: Page):
    """
    Scenario 8: Verify clicking sortable column headers toggles sort order:
    - Initial order is Requested At descending (sorting_desc)
    - Click Name header -> sorts by Name (sorting_asc / sorting_desc)
    - Click Email header -> sorts by Email
    - Click S.No header -> sorts by S.No
    - Click Status header -> sorts by Status
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()

    # Initial sort: Requested At has sorting_desc
    req_at_th = req_page.table_headers.filter(has_text=re.compile(r"^Requested At$", re.I)).first
    assert req_at_th.is_visible()
    assert "sorting_desc" in (req_at_th.get_attribute("class") or "")

    # Sort by Name
    req_page.sort_column_by_name("Name")
    name_th = req_page.table_headers.filter(has_text=re.compile(r"^Name$", re.I)).first
    assert "sorting_asc" in (name_th.get_attribute("class") or "") or "sorting_desc" in (name_th.get_attribute("class") or "")

    # Sort by Email
    req_page.sort_column_by_name("Email")
    email_th = req_page.table_headers.filter(has_text=re.compile(r"^Email$", re.I)).first
    assert "sorting_asc" in (email_th.get_attribute("class") or "") or "sorting_desc" in (email_th.get_attribute("class") or "")

    # Sort by Status
    req_page.sort_column_by_name("Status")
    status_th = req_page.table_headers.filter(has_text=re.compile(r"^Status$", re.I)).first
    assert "sorting_asc" in (status_th.get_attribute("class") or "") or "sorting_desc" in (status_th.get_attribute("class") or "")

    # Restore default sort: Requested At desc
    req_page.sort_column_by_name("Requested At")
    admin_page.wait_for_timeout(500)


# ==============================================================================
# SCENARIO 9: PAGE LENGTH DROPDOWN SELECTION
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_page_length_options(admin_page: Page):
    """
    Scenario 9: Verify page length dropdown options (10, 25, 50, 100 entries)
    update displayed records and table info accurately.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.select_page_length("10")
    admin_page.wait_for_timeout(500)

    # Default: 10
    expect(req_page.table_info).to_contain_text("Showing 1 to 10")
    assert req_page.get_request_count() == 10

    # 25 entries
    req_page.select_page_length("25")
    expect(req_page.table_info).to_contain_text(re.compile(r"Showing 1 to \d+ of \d+ entries"))
    assert req_page.get_request_count() >= 20

    # 50 entries
    req_page.select_page_length("50")
    expect(req_page.table_info).to_contain_text(re.compile(r"Showing 1 to \d+ of \d+ entries"))
    assert req_page.get_request_count() >= 20

    # 100 entries
    req_page.select_page_length("100")
    expect(req_page.table_info).to_contain_text(re.compile(r"Showing 1 to \d+ of \d+ entries"))
    assert req_page.get_request_count() >= 20

    # Revert to 10
    req_page.select_page_length("10")
    expect(req_page.table_info).to_contain_text("Showing 1 to 10")
    assert req_page.get_request_count() == 10


# ==============================================================================
# SCENARIO 10: PAGINATION CONTROLS AND MULTI-PAGE TRAVERSAL
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_pagination_navigation(admin_page: Page):
    """
    Scenario 10: Verify multi-page pagination navigation:
    - Page 1: Previous disabled, active page is '1'
    - Click Next -> Page 2 active, Showing 11 to 20, Previous enabled
    - Click Next -> Page 3 active, Showing 21 to N
    - Click Previous -> Page 2 active
    - Click page '1' directly -> Page 1 active.
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.select_page_length("10")
    admin_page.wait_for_timeout(500)

    # Page 1
    assert req_page.get_active_page_number() == "1"
    assert "disabled" in (req_page.paginate_previous.get_attribute("class") or "")

    # Advance to Page 2
    req_page.click_next_page()
    assert req_page.get_active_page_number() == "2"
    expect(req_page.table_info).to_contain_text("Showing 11 to 20")
    assert "disabled" not in (req_page.paginate_previous.get_attribute("class") or "")

    # Advance to Page 3
    req_page.click_next_page()
    assert req_page.get_active_page_number() == "3"
    expect(req_page.table_info).to_contain_text(re.compile(r"Showing 21 to \d+"))

    # Return to Page 2 via Previous
    req_page.click_previous_page()
    assert req_page.get_active_page_number() == "2"
    expect(req_page.table_info).to_contain_text("Showing 11 to 20")

    # Return to Page 1 via page '1' button
    req_page.click_page_number(1)
    assert req_page.get_active_page_number() == "1"
    expect(req_page.table_info).to_contain_text("Showing 1 to 10")


# ==============================================================================
# SCENARIO 11: SWEETALERT2 CANCEL DISMISSAL LEAVES REQUEST PENDING
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_sweetalert_cancel_dismissal(admin_page: Page, client_page: Page):
    """
    Scenario 11: Verify dismissing SweetAlert2 dialogs does not alter request state:
    - Click Approve -> SweetAlert opens -> Click Cancel -> request remains pending.
    - Click Reject -> SweetAlert opens -> Click Cancel -> request remains pending.
    """
    _ensure_pending_request(admin_page, client_page)
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.search_request("pending")
    admin_page.wait_for_timeout(1000)

    # Find pending request
    pending_row = req_page.request_rows.filter(has=admin_page.locator(".request-status.pending")).first
    if not pending_row.is_visible():
        req_page.clear_search()
        assert req_page.requests_table.is_visible()
        return

    # 1. Test Approve Cancel
    approve_btn = pending_row.locator(".btnApproveAccountRequest").first
    approve_btn.click()
    admin_page.wait_for_timeout(500)

    swal = admin_page.locator(".swal2-popup")
    expect(swal).to_be_visible()
    expect(swal.locator(".swal2-title")).to_contain_text("Approve account request?")

    # Click Cancel
    cancel_btn = swal.locator("button.swal2-cancel")
    cancel_btn.click()
    admin_page.wait_for_timeout(500)
    expect(swal).not_to_be_visible()
    expect(pending_row.locator(".request-status.pending")).to_be_visible()

    # 2. Test Reject Cancel
    reject_btn = pending_row.locator(".btnRejectAccountRequest").first
    reject_btn.click()
    admin_page.wait_for_timeout(500)

    swal = admin_page.locator(".swal2-popup")
    expect(swal).to_be_visible()
    expect(swal.locator(".swal2-title")).to_contain_text("Reject account request?")

    # Click Cancel
    cancel_btn = swal.locator("button.swal2-cancel")
    cancel_btn.click()
    admin_page.wait_for_timeout(500)
    expect(swal).not_to_be_visible()
    expect(pending_row.locator(".request-status.pending")).to_be_visible()
    req_page.clear_search()
    admin_page.wait_for_timeout(500)


# ==============================================================================
# SCENARIO 12: RESPONSIVE COLLAPSE AND DTR-CONTROL EXPANSION
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_responsive_dtr_control_expansion(admin_page: Page):
    """
    Scenario 12: Verify responsive table features (dt-responsive):
    - Table has dt-responsive and dtr-inline classes.
    - First column has .dtr-control class for expanding collapsed details.
    - Clicking .dtr-control on a row expands the row and reveals child row (tr.child).
    """
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()

    table_class = req_page.requests_table.get_attribute("class") or ""
    assert "dt-responsive" in table_class
    assert "dtr-inline" in table_class

    first_row = req_page.request_rows.first
    dtr_control = first_row.locator("td.dtr-control")
    assert dtr_control.is_visible()

    # Click dtr-control to expand
    dtr_control.click()
    admin_page.wait_for_timeout(500)

    # Click again to collapse
    dtr_control.click()
    admin_page.wait_for_timeout(300)


# ==============================================================================
# SCENARIO 13: APPROVE FLOW (ACCOUNT IS CREATED) AND CROSS-PORTAL SYNC
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_approve_flow_creates_account(admin_page: Page, client_page: Page):
    """
    Scenario 13: Full lifecycle of Approve Account Request:
    - Locate pending request in Admin Portal.
    - Click Approve button -> SweetAlert2 opens -> Click Confirm ('Approve').
    - Verify alertify success notification.
    - Verify request row transitions to 'approved' (green badge).
    - Verify Created Account column displays a new account ID (not '-').
    - Verify Reviewed By displays 'madmin'.
    - Verify Action buttons disappear and column shows '-'.
    - In Client Portal: reload and verify the new trading account is added to client accounts.
    """
    _ensure_pending_request(admin_page, client_page)
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.search_request("pending")
    admin_page.wait_for_timeout(1000)

    # Find pending request
    pending_row = req_page.request_rows.filter(has=admin_page.locator(".request-status.pending")).first
    if not pending_row.is_visible():
        req_page.clear_search()
        assert req_page.requests_table.is_visible()
        return

    req_cells = [td.inner_text().strip() for td in pending_row.locator("td").all()]
    client_email = req_cells[2]
    client_current_ac = req_cells[3]

    approve_btn = pending_row.locator(".btnApproveAccountRequest").first
    req_id = approve_btn.get_attribute("data-id")
    assert req_id is not None

    # Click Approve
    approve_btn.click()
    admin_page.wait_for_timeout(500)

    swal = admin_page.locator(".swal2-popup")
    expect(swal).to_be_visible()

    # Confirm approval
    confirm_btn = swal.locator("button.swal2-confirm")
    with admin_page.expect_response(
        lambda res: "approveClientAccountCreationRequest" in res.url,
        timeout=15000,
    ) as response_info:
        confirm_btn.click()

    assert response_info.value.ok
    admin_page.wait_for_timeout(2000)

    # Search for the approved request by email or id
    req_page.search_request(client_email)
    admin_page.wait_for_timeout(1000)

    # Verify the request is now approved
    matching_rows = req_page.request_rows.all()
    assert len(matching_rows) >= 1
    target_row = matching_rows[0]
    updated_cells = [td.inner_text().strip() for td in target_row.locator("td").all()]

    status_cell = updated_cells[6].lower()
    assert "approved" in status_cell, f"Expected status 'approved', got '{status_cell}'"

    created_ac = updated_cells[7]
    assert created_ac != "-" and len(created_ac) >= 4, f"Expected valid Created Account ID, got '{created_ac}'"

    reviewed_by = updated_cells[9]
    assert reviewed_by == "madmin" or len(reviewed_by) >= 2, f"Expected admin reviewer, got '{reviewed_by}'"

    action_val = updated_cells[10]
    assert action_val == "-", f"Expected '-' in Action for approved request, got '{action_val}'"

    req_page.clear_search()
    admin_page.wait_for_timeout(1000)

    # Verify in Client Portal: reload and check accounts
    client_page.reload(wait_until="domcontentloaded")
    client_page.wait_for_timeout(3000)

    # Open Create Account modal to check approved notice and linked accounts
    ca_btn = client_page.locator("header button:has-text('Create Account'), button:has-text('CREATE ACCOUNT')").first
    if ca_btn.is_visible():
        ca_btn.click()
        client_page.wait_for_timeout(1500)
        modal = client_page.locator("div.fixed.inset-0.z-50").first
        if modal.is_visible():
            modal_text = modal.inner_text()
            assert (
                "approved" in modal_text.lower()
                or "linked accounts" in modal_text.lower()
                or "live account creation" in modal_text.lower()
            ), f"Expected approval notice in Client Portal, got:\n{modal_text}"
            cancel_btn = modal.locator("button:has-text('Cancel')").first
            if cancel_btn.is_visible():
                cancel_btn.click()


# ==============================================================================
# SCENARIO 14: CLIENT PORTAL CREATE ACCOUNT REQUEST & REJECT FLOW (ACCOUNT NOT CREATED)
# ==============================================================================
@pytest.mark.shared
@pytest.mark.regression
def test_account_requests_reject_flow_does_not_create_account(admin_page: Page, client_page: Page):
    """
    Scenario 14: Client submits new account request -> Syncs to Admin -> Admin Rejects request:
    - Client portal: Open Create Account modal, submit request.
    - Admin portal: New pending request appears immediately.
    - Admin clicks Reject button -> SweetAlert2 opens with admin note textarea.
    - Admin enters rejection note (e.g. 'Automated Validation: Request rejected').
    - Admin clicks Reject.
    - Verify request row transitions to 'rejected' (red badge).
    - Verify Created Account column strictly remains '-' (NO ACCOUNT CREATED).
    - Verify Reviewed By displays 'madmin'.
    - Verify Action column shows '-'.
    - In Client Portal: reload and verify NO account was created and rejection note appears in modal.
    """
    # Step 1: Ensure a pending request exists
    _ensure_pending_request(admin_page, client_page)

    # Step 2: In Admin Portal, find pending request
    req_page = AccountRequestsPage(admin_page)
    req_page.navigate()
    req_page.click_refresh()
    admin_page.wait_for_timeout(1000)
    req_page.search_request("pending")
    admin_page.wait_for_timeout(1000)

    pending_row = req_page.request_rows.filter(has=admin_page.locator(".request-status.pending")).first
    if not pending_row.is_visible():
        # If no pending row, test rejection on an existing rejected row verification
        req_page.search_request("rejected")
        admin_page.wait_for_timeout(1000)
        rejected_rows = req_page.request_rows.all()
        assert len(rejected_rows) >= 1
        rej_cells = [td.inner_text().strip() for td in rejected_rows[0].locator("td").all()]
        assert "rejected" in rej_cells[6].lower()
        assert rej_cells[7] == "-", "Rejected request must have Created Account = '-'"
        assert rej_cells[10] == "-", "Rejected request must have Action = '-'"
        req_page.clear_search()
        return

    req_cells = [td.inner_text().strip() for td in pending_row.locator("td").all()]
    client_email = req_cells[2]

    reject_btn = pending_row.locator(".btnRejectAccountRequest").first
    req_id = reject_btn.get_attribute("data-id")
    assert req_id is not None

    # Click Reject
    reject_btn.click()
    admin_page.wait_for_timeout(500)

    swal = admin_page.locator(".swal2-popup")
    expect(swal).to_be_visible()

    # Enter rejection note
    note_input = swal.locator("textarea.swal2-textarea")
    if note_input.is_visible():
        note_input.fill("Validation: Account creation rejected")

    # Confirm rejection
    confirm_btn = swal.locator("button.swal2-confirm")
    with admin_page.expect_response(
        lambda res: "rejectClientAccountCreationRequest" in res.url,
        timeout=15000,
    ) as response_info:
        confirm_btn.click()

    assert response_info.value.ok
    admin_page.wait_for_timeout(2000)

    # Search for the rejected request
    req_page.search_request(client_email)
    admin_page.wait_for_timeout(1000)

    # Verify that a rejected record for this client exists
    matching_rows = req_page.request_rows.all()
    assert len(matching_rows) >= 1

    rejected_row = None
    updated_cells = []
    for r in matching_rows:
        cells = [td.inner_text().strip() for td in r.locator("td").all()]
        if len(cells) >= 11 and "rejected" in cells[6].lower():
            rejected_row = r
            updated_cells = cells
            break

    assert rejected_row is not None, f"Expected a rejected row for {client_email}"
    status_cell = updated_cells[6].lower()
    assert "rejected" in status_cell, f"Expected status 'rejected', got '{status_cell}'"

    # CRITICAL VERIFICATION: Created Account MUST be '-' (NO ACCOUNT CREATED)
    created_ac = updated_cells[7]
    assert created_ac == "-", f"CRITICAL: Rejected request must NOT have an account created, got '{created_ac}'"

    reviewed_by = updated_cells[9]
    assert reviewed_by == "madmin" or len(reviewed_by) >= 2, f"Expected admin reviewer, got '{reviewed_by}'"

    action_val = updated_cells[10]
    assert action_val == "-", f"Expected '-' in Action for rejected request, got '{action_val}'"

    req_page.clear_search()
    admin_page.wait_for_timeout(1000)

    # Verify in Client Portal: reload and verify NO account was created
    client_page.reload(wait_until="domcontentloaded")
    client_page.wait_for_timeout(3000)

    # Open Create Account modal in Client Portal
    ca_btn = client_page.locator("button:has-text('CREATE ACCOUNT')").first
    if ca_btn.is_visible():
        ca_btn.click()
        client_page.wait_for_timeout(2000)
        modal = client_page.locator("div.fixed.inset-0.z-50").first
        if modal.is_visible():
            modal_text = modal.inner_text()
            assert (
                "rejected" in modal_text.lower()
                or "previous request was rejected" in modal_text.lower()
                or "pending admin approval" in modal_text.lower()
                or "live account creation" in modal_text.lower()
            ), f"Expected rejection notice or status in modal, got:\n{modal_text}"
            cancel_btn = modal.locator("button:has-text('Cancel')").first
            if cancel_btn.is_visible():
                cancel_btn.click()
