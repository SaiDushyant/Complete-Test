"""
Admin Portal Mock Tests: Module 08 - Deposits Queue & Payment Gateways.
Tests deposit queue rendering, instant approvals, rejections with reason,
manual balance credits, payment list history, and OxaPay crypto blockchain tracker.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_deposit_queue_render(mock_router: MockRouter, workflow_page: Page):
    """Verify pending deposit transactions table with proof of payment links."""
    mock_router.mock_json("**/Controlbase/depositQueue**", admin_mocks.MOCK_PENDING_DEPOSITS, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/depositQueue');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    deposits = result["data"]
    assert len(deposits) >= 1
    assert deposits[0]["transaction_id"] == "DEP-7731"
    assert deposits[0]["gateway"] == "Crypto (USDT-TRC20)"

    workflow_page.set_content(f"""
        <table id="deposit-queue-table">
            <thead>
                <tr><th>Tx ID</th><th>Account</th><th>Amount</th><th>Gateway</th><th>Proof</th><th>Status</th></tr>
            </thead>
            <tbody>
                <tr id="row-{deposits[0]['transaction_id']}">
                    <td class="tx-id">{deposits[0]['transaction_id']}</td>
                    <td class="account-id">{deposits[0]['account_id']}</td>
                    <td class="amount">${deposits[0]['amount']:,.2f}</td>
                    <td class="gateway">{deposits[0]['gateway']}</td>
                    <td><a href="{deposits[0]['proof_img']}" class="proof-link">View Proof</a></td>
                    <td><span class="badge badge-warning status-badge">{deposits[0]['status']}</span></td>
                </tr>
            </tbody>
        </table>
    """)

    expect(workflow_page.locator(".tx-id")).to_have_text("DEP-7731")
    expect(workflow_page.locator(".amount")).to_have_text("$2,500.00")
    expect(workflow_page.locator(".status-badge")).to_have_text("PENDING_APPROVAL")
    expect(workflow_page.locator(".proof-link")).to_be_visible()


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_deposit_instant_approval(mock_router: MockRouter, workflow_page: Page):
    """Verify approving deposit immediately credits balance and sets status APPROVED."""
    mock_router.mock_json(
        "**/Controlbase/approveDeposit**",
        {"status": 200, "tx_status": "APPROVED", "transaction_id": "DEP-7731", "credited_amount": 2500.00},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/approveDeposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transaction_id: 'DEP-7731' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["tx_status"] == "APPROVED"

    workflow_page.set_content(f"""
        <div class="alert alert-success" id="approval-notice">
            Deposit {result["data"]["transaction_id"]} approved successfully. ${result["data"]["credited_amount"]:,.2f} credited to trader account.
        </div>
        <span class="badge badge-success current-status">{result["data"]["tx_status"]}</span>
    """)

    expect(workflow_page.locator("#approval-notice")).to_be_visible()
    expect(workflow_page.locator(".current-status")).to_have_text("APPROVED")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_deposit_rejection_with_reason(mock_router: MockRouter, workflow_page: Page):
    """Verify rejecting invalid deposit with reason note (e.g. 'Unverified TX Hash')."""
    mock_router.mock_json(
        "**/Controlbase/rejectDeposit**",
        {"status": 200, "tx_status": "REJECTED", "transaction_id": "DEP-7731", "reason": "Unverified TX Hash"},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/rejectDeposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transaction_id: 'DEP-7731', reason: 'Unverified TX Hash' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["tx_status"] == "REJECTED"
    assert result["data"]["reason"] == "Unverified TX Hash"

    workflow_page.set_content(f"""
        <div class="rejection-card">
            <span class="badge badge-danger rejection-status">{result["data"]["tx_status"]}</span>
            <span class="rejection-reason">Reason: {result["data"]["reason"]}</span>
        </div>
    """)

    expect(workflow_page.locator(".rejection-status")).to_have_text("REJECTED")
    expect(workflow_page.locator(".rejection-reason")).to_contain_text("Unverified TX Hash")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_manual_deposit_credit(mock_router: MockRouter, workflow_page: Page):
    """Verify admin manual balance deposit credit form for offline wire transfers."""
    mock_router.mock_json(
        "**/Controlbase/manualDeposit**",
        {"status": 200, "success": True, "account_id": "10098", "credited": 5000.00, "ref": "WIRE-OCT-001"},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/manualDeposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: '10098', amount: 5000.00, reference: 'WIRE-OCT-001' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["success"] is True
    assert result["data"]["credited"] == 5000.00

    workflow_page.set_content(f"""
        <div class="toast toast-success" id="credit-toast">
            Successfully credited ${result["data"]["credited"]:,.2f} to account {result["data"]["account_id"]}.
        </div>
    """)

    expect(workflow_page.locator("#credit-toast")).to_be_visible()
    expect(workflow_page.locator("#credit-toast")).to_contain_text("$5,000.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_payment_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify completed payments history table (/payment) rendering with method badges."""
    mock_router.mock_json("**/Controlbase/payment**", admin_mocks.MOCK_ADMIN_PAYMENT_LIST, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/payment');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    payments = result["data"]
    assert len(payments) == 2
    assert payments[0]["payment_id"] == "PAY-9921"
    assert payments[1]["payment_id"] == "PAY-9922"

    rows_html = "".join([
        f"<tr class='payment-row'><td class='id'>{p['payment_id']}</td><td class='gateway'>{p['gateway']}</td><td class='status'>{p['status']}</td></tr>"
        for p in payments
    ])
    workflow_page.set_content(f"<table id='payments-table'><tbody>{rows_html}</tbody></table>")

    expect(workflow_page.locator(".payment-row")).to_have_count(2)
    expect(workflow_page.locator(".payment-row >> nth=0 >> .id")).to_have_text("PAY-9921")
    expect(workflow_page.locator(".payment-row >> nth=1 >> .id")).to_have_text("PAY-9922")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_oxapay_payment_track_render(mock_router: MockRouter, workflow_page: Page):
    """Verify OxaPay crypto blockchain transaction tracker table (/oxapayPaymentTrack)."""
    mock_router.mock_json("**/Controlbase/oxapayPaymentTrack**", admin_mocks.MOCK_ADMIN_OXAPAY_LIST, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/oxapayPaymentTrack');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    oxa_records = result["data"]
    assert len(oxa_records) >= 1
    assert oxa_records[0]["crypto_currency"] == "USDT"
    assert oxa_records[0]["confirmations"] == 18

    workflow_page.set_content(f"""
        <div id="crypto-tracker">
            <span class="track-id">{oxa_records[0]['track_id']}</span>
            <span class="crypto-currency">{oxa_records[0]['crypto_currency']} ({oxa_records[0]['network']})</span>
            <span class="confirmations">{oxa_records[0]['confirmations']} Confirmations</span>
            <span class="tx-status">{oxa_records[0]['status']}</span>
        </div>
    """)

    expect(workflow_page.locator(".track-id")).to_have_text("OXA-5510")
    expect(workflow_page.locator(".crypto-currency")).to_contain_text("USDT (TRON (TRC20))")
    expect(workflow_page.locator(".confirmations")).to_have_text("18 Confirmations")
    expect(workflow_page.locator(".tx-status")).to_have_text("CONFIRMED")
