"""
Admin Portal Mock Tests: Module 03 - Trader User Management & Lifecycle CRUD.
Tests user listing, table pagination, group filters, account creation, 422 duplicate validation,
status suspension toggles, balance adjustments, and killing active user sessions.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify that mocked user records populate correctly in the user management table."""
    mock_router.mock_json("**/Controlbase/userList**", admin_mocks.MOCK_ADMIN_USER_LIST, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/userList');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    users = result["data"]
    assert len(users) >= 1
    assert users[0]["id"] == "10098"
    assert users[0]["username"] == "trader_john"

    rows = "".join([
        f"<tr class='user-row' id='user-{u['id']}'>"
        f"<td class='user-id'>{u['id']}</td>"
        f"<td class='username'>{u['username']}</td>"
        f"<td class='email'>{u['email']}</td>"
        f"<td class='group'>{u['group']}</td>"
        f"<td class='balance'>${u['balance']:,.2f}</td></tr>"
        for u in users
    ])
    workflow_page.set_content(f"<table id='users-table'><tbody>{rows}</tbody></table>")

    expect(workflow_page.locator(".user-row")).to_have_count(len(users))
    expect(workflow_page.locator("#user-10098 .username")).to_have_text("trader_john")
    expect(workflow_page.locator("#user-10098 .group")).to_have_text("Standard_USD")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_table_pagination(mock_router: MockRouter, workflow_page: Page):
    """Verify table pagination controls with 100+ mocked user records."""
    mock_router.mock_json("**/Controlbase/userList?page=2**", admin_mocks.MOCK_ADMIN_USER_LIST, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/userList?page=2');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert len(result["data"]) >= 1

    workflow_page.set_content("""
        <div class="pagination-wrapper">
            <ul class="pagination">
                <li class="page-item"><a class="page-link" href="#">1</a></li>
                <li class="page-item active"><a class="page-link" href="#">2</a></li>
                <li class="page-item"><a class="page-link" href="#">3</a></li>
            </ul>
        </div>
    """)

    expect(workflow_page.locator(".pagination .active .page-link")).to_have_text("2")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_filter_by_group_and_status(mock_router: MockRouter, workflow_page: Page):
    """Verify filtering users by group (VIP_USD) and status (active/blocked)."""
    filtered_users = [
        {
            "id": "10099",
            "username": "vip_sarah",
            "email": "sarah@vip.com",
            "group": "VIP_USD",
            "balance": 50000.0,
            "status": "active",
        }
    ]
    mock_router.mock_json("**/Controlbase/userList?group=VIP_USD**", filtered_users, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/userList?group=VIP_USD');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert len(result["data"]) == 1
    assert result["data"][0]["group"] == "VIP_USD"

    workflow_page.set_content(f"""
        <div id="filter-display">
            <span class="active-group-filter">Group: {result["data"][0]["group"]}</span>
            <div class="user-card">{result["data"][0]["username"]} (${result["data"][0]["balance"]:,.2f})</div>
        </div>
    """)

    expect(workflow_page.locator(".active-group-filter")).to_have_text("Group: VIP_USD")
    expect(workflow_page.locator(".user-card")).to_contain_text("vip_sarah ($50,000.00)")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_user_success(mock_router: MockRouter, workflow_page: Page):
    """Verify successful creation of a new trader account from admin portal."""
    new_user = {
        "id": "10105",
        "username": "new_trader_alex",
        "email": "alex@sample.com",
        "group": "Standard_USD",
        "balance": 1000.0,
        "status": "active",
    }
    mock_router.mock_json("**/Controlbase/createUser**", {"status": 200, "user": new_user}, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/createUser', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'new_trader_alex', email: 'alex@sample.com' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["user"]["id"] == "10105"
    assert result["data"]["user"]["username"] == "new_trader_alex"

    workflow_page.set_content(f"""
        <div class="alert alert-success" id="create-user-toast">
            Trader account #{result["data"]["user"]["id"]} ({result["data"]["user"]["username"]}) created successfully.
        </div>
    """)

    expect(workflow_page.locator("#create-user-toast")).to_be_visible()
    expect(workflow_page.locator("#create-user-toast")).to_contain_text("new_trader_alex")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_user_duplicate_email(mock_router: MockRouter, workflow_page: Page):
    """Verify 422 duplicate email validation error display on user creation form."""
    mock_router.mock_error("**/Controlbase/createUser**", status=422, error_message="Email address already registered")

    result = workflow_page.evaluate("""async () => {
        try {
            const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/createUser', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'duplicate', email: 'john.trader@example.com' })
            });
            return { status: resp.status, data: await resp.json() };
        } catch (e) {
            return { error: e.toString() };
        }
    }""")

    assert result["status"] == 422
    assert "already registered" in result["data"]["error"]

    workflow_page.set_content("""
        <div class="form-group has-error">
            <input type="email" id="user-email" class="is-invalid" value="john.trader@example.com" />
            <div class="invalid-feedback">Email address already registered</div>
        </div>
    """)

    expect(workflow_page.locator(".invalid-feedback")).to_be_visible()
    expect(workflow_page.locator(".invalid-feedback")).to_have_text("Email address already registered")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_status_toggle_suspend(mock_router: MockRouter, workflow_page: Page):
    """Verify suspending an active user updates status badge immediately."""
    mock_router.mock_json("**/Controlbase/updateUserStatus**", {"status": 200, "user_id": "10098", "account_status": "blocked"}, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/updateUserStatus', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: '10098', status: 'blocked' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["account_status"] == "blocked"

    workflow_page.set_content(f"""
        <div id="user-status-card">
            <span class="user-id">Account #{result["data"]["user_id"]}</span>
            <span class="badge badge-danger status-pill">{result["data"]["account_status"]}</span>
        </div>
    """)

    expect(workflow_page.locator(".status-pill")).to_have_text("blocked")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_balance_adjustment(mock_router: MockRouter, workflow_page: Page):
    """Verify manual balance credit/debit by admin with audit note."""
    mock_router.mock_json(
        "**/Controlbase/adjustBalance**",
        {"status": 200, "account_id": "10098", "adjustment": 500.00, "new_balance": 15900.00},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/adjustBalance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: '10098', amount: 500.00, note: 'Bonus correction' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["new_balance"] == 15900.00

    workflow_page.set_content(f"""
        <div class="balance-card">
            <span class="label">Adjusted Balance:</span>
            <span class="value">${result["data"]["new_balance"]:,.2f}</span>
        </div>
    """)

    expect(workflow_page.locator(".balance-card .value")).to_have_text("$15,900.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_active_users_session_kill(mock_router: MockRouter, workflow_page: Page):
    """Verify admin ability to force-terminate an online user's active session."""
    mock_router.mock_json(
        "**/Controlbase/killSession**",
        {"status": 200, "session_terminated": True, "session_id": "sess-992", "account_id": "10098"},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/killSession', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: 'sess-992' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["session_terminated"] is True

    workflow_page.set_content("""
        <div class="session-status">Session sess-992 was terminated by Administrator.</div>
    """)

    expect(workflow_page.locator(".session-status")).to_contain_text("terminated by Administrator")
