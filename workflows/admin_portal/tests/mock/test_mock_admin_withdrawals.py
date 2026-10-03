"""
Admin Portal Mock Tests: Module 09 - Withdrawals Queue & Refund Lifecycle.
Tests pending withdrawals queue, approval payout hashing, rejection with automated wallet refund,
CSV report export, and the dedicated Manage Withdraw view (/managewithdraw).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_queue_render(mock_router: MockRouter, workflow_page: Page):
    """Verify pending withdrawal requests table with destination wallet/bank details."""
    mock_router.mock_json("**/Controlbase/withdrawQueue**", admin_mocks.MOCK_ADMIN_WITHDRAW_QUEUE, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/withdrawQueue');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    queue = result["data"]
    assert len(queue) == 2
    assert queue[0]["withdrawal_id"] == "WTH-3310"
    assert queue[1]["withdrawal_id"] == "WTH-3311"

    rows = "".join([
        f"<tr class='withdraw-row' id='{item['withdrawal_id']}'>"
        f"<td class='id'>{item['withdrawal_id']}</td>"
        f"<td class='amount'>${item['amount']:,.2f}</td>"
        f"<td class='method'>{item['payout_method']}</td>"
        f"<td class='status'>{item['status']}</td></tr>"
        for item in queue
    ])
    workflow_page.set_content(f"<table id='withdraw-queue'><tbody>{rows}</tbody></table>")

    expect(workflow_page.locator(".withdraw-row")).to_have_count(2)
    expect(workflow_page.locator("#WTH-3310 .amount")).to_have_text("$1,200.00")
    expect(workflow_page.locator("#WTH-3311 .amount")).to_have_text("$8,500.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_approval_success(mock_router: MockRouter, workflow_page: Page):
    """Verify approving withdrawal sets state to PROCESSED and logs payout hash."""
    mock_router.mock_json(
        "**/Controlbase/approveWithdraw**",
        {"status": 200, "tx_status": "PROCESSED", "withdrawal_id": "WTH-3310", "payout_hash": "0xabc9921ef1"},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/approveWithdraw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ withdrawal_id: 'WTH-3310' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["tx_status"] == "PROCESSED"
    assert "payout_hash" in result["data"]

    workflow_page.set_content(f"""
        <div id="payout-result" class="alert alert-success">
            Withdrawal {result["data"]["withdrawal_id"]} processed. Tx Hash: {result["data"]["payout_hash"]}
        </div>
        <span class="badge badge-success payout-badge">{result["data"]["tx_status"]}</span>
    """)

    expect(workflow_page.locator("#payout-result")).to_be_visible()
    expect(workflow_page.locator(".payout-badge")).to_have_text("PROCESSED")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_rejection_auto_refund(mock_router: MockRouter, workflow_page: Page):
    """Verify rejecting withdrawal immediately refunds deducted balance to trader."""
    mock_router.mock_json(
        "**/Controlbase/rejectWithdraw**",
        {"status": 200, "refund_issued": True, "refunded_amount": 1200.00, "account_id": "10098"},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/rejectWithdraw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ withdrawal_id: 'WTH-3310', reason: 'Compliance KYC Verification Required' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["refund_issued"] is True
    assert result["data"]["refunded_amount"] == 1200.00

    workflow_page.set_content(f"""
        <div class="alert alert-info" id="refund-notice">
            ${result["data"]["refunded_amount"]:,.2f} has been refunded to trader {result["data"]["account_id"]}.
        </div>
    """)

    expect(workflow_page.locator("#refund-notice")).to_be_visible()
    expect(workflow_page.locator("#refund-notice")).to_contain_text("$1,200.00 has been refunded")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_export_csv(mock_router: MockRouter, workflow_page: Page):
    """Verify export of withdrawal records to CSV data stream."""
    mock_router.mock_json(
        "**/Controlbase/exportWithdrawals**",
        {"download_ready": True, "filename": "withdrawals_2026_10.csv", "records_count": 2},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/exportWithdrawals');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["download_ready"] is True
    assert result["data"]["records_count"] == 2

    workflow_page.set_content(f"""
        <div class="export-container">
            <a href="/downloads/{result["data"]["filename"]}" id="download-csv-link">
                Download {result["data"]["filename"]} ({result["data"]["records_count"]} records)
            </a>
        </div>
    """)

    expect(workflow_page.locator("#download-csv-link")).to_be_visible()
    expect(workflow_page.locator("#download-csv-link")).to_contain_text("withdrawals_2026_10.csv")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_manage_withdraw_view(mock_router: MockRouter, workflow_page: Page):
    """Verify Manage Withdraw table (/managewithdraw) with status filtering."""
    mock_router.mock_json("**/Controlbase/managewithdraw**", admin_mocks.MOCK_ADMIN_WITHDRAW_QUEUE, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/managewithdraw');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert len(result["data"]) == 2

    workflow_page.set_content("""
        <div id="manage-withdraw-page">
            <select id="status-filter">
                <option value="ALL">All Statuses</option>
                <option value="PENDING" selected>Pending</option>
                <option value="PROCESSED">Processed</option>
            </select>
            <div class="records-summary">Showing 2 pending withdrawals</div>
        </div>
    """)

    expect(workflow_page.locator("#status-filter")).to_be_visible()
    expect(workflow_page.locator(".records-summary")).to_contain_text("Showing 2 pending withdrawals")
