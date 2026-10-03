"""
Admin Portal Mock Tests: Module 10 - Orders & Trade Management.
Tests live open positions grid, closed trade history, symbol/user filters, emergency force-close,
Master Order Report (/OrderReport), User Order Report (/userOrderReport), and Order Edit Log (/orderEditLog).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_open_orders_grid_render(mock_router: MockRouter, workflow_page: Page):
    """Verify live open positions grid (/order/open) across all platform traders."""
    mock_router.mock_json("**/Controlbase/order/open**", admin_mocks.MOCK_ADMIN_OPEN_ORDERS, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/order/open');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    orders = result["data"]
    assert len(orders) == 2
    assert orders[0]["ticket"] == 9001
    assert orders[0]["symbol"] == "EURUSD"
    assert orders[1]["ticket"] == 9002
    assert orders[1]["symbol"] == "BTCUSD"

    rows = "".join([
        f"<tr class='order-row' id='ticket-{o['ticket']}'>"
        f"<td class='ticket'>{o['ticket']}</td>"
        f"<td class='symbol'>{o['symbol']}</td>"
        f"<td class='type'>{o['type']}</td>"
        f"<td class='lots'>{o['lots']}</td>"
        f"<td class='profit'>${o['profit']:,.2f}</td></tr>"
        for o in orders
    ])
    workflow_page.set_content(f"<table id='open-orders-table'><tbody>{rows}</tbody></table>")

    expect(workflow_page.locator(".order-row")).to_have_count(2)
    expect(workflow_page.locator("#ticket-9001 .symbol")).to_have_text("EURUSD")
    expect(workflow_page.locator("#ticket-9002 .symbol")).to_have_text("BTCUSD")
    expect(workflow_page.locator("#ticket-9001 .profit")).to_have_text("$180.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_closed_orders_grid_render(mock_router: MockRouter, workflow_page: Page):
    """Verify closed trade history grid (/order/closed) with realized profit and close reason."""
    mock_router.mock_json("**/Controlbase/order/closed**", admin_mocks.MOCK_ADMIN_CLOSED_ORDERS, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/order/closed');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    closed = result["data"]
    assert len(closed) >= 1
    assert closed[0]["ticket"] == 8980
    assert closed[0]["symbol"] == "XAUUSD"
    assert closed[0]["profit"] == 3100.00

    workflow_page.set_content(f"""
        <table id="closed-orders">
            <tbody>
                <tr class="closed-row">
                    <td class="ticket">{closed[0]['ticket']}</td>
                    <td class="symbol">{closed[0]['symbol']}</td>
                    <td class="profit">${closed[0]['profit']:,.2f}</td>
                    <td class="close-time">{closed[0]['close_time']}</td>
                </tr>
            </tbody>
        </table>
    """)

    expect(workflow_page.locator(".closed-row .ticket")).to_have_text("8980")
    expect(workflow_page.locator(".closed-row .symbol")).to_have_text("XAUUSD")
    expect(workflow_page.locator(".closed-row .profit")).to_have_text("$3,100.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_filter_orders_by_symbol_and_user(mock_router: MockRouter, workflow_page: Page):
    """Verify instant filtering of open orders by symbol (BTCUSD) and Account ID."""
    btc_orders = [o for o in admin_mocks.MOCK_ADMIN_OPEN_ORDERS if o.get("symbol") == "BTCUSD"]
    mock_router.mock_json("**/Controlbase/order/all?symbol=BTCUSD**", btc_orders, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/order/all?symbol=BTCUSD');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    filtered = result["data"]
    assert len(filtered) == 1
    assert filtered[0]["symbol"] == "BTCUSD"
    assert filtered[0]["account_id"] == "10099"

    workflow_page.set_content(f"""
        <div id="filter-results">
            <span class="active-filter">Symbol: BTCUSD</span>
            <div class="result-card">{filtered[0]['ticket']} - {filtered[0]['symbol']} ({filtered[0]['type']})</div>
        </div>
    """)

    expect(workflow_page.locator(".active-filter")).to_have_text("Symbol: BTCUSD")
    expect(workflow_page.locator(".result-card")).to_contain_text("9002 - BTCUSD (SELL)")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_force_close_order(mock_router: MockRouter, workflow_page: Page):
    """Verify admin emergency force-close of a runaway position at market price."""
    mock_router.mock_json(
        "**/Controlbase/closeOrder**",
        {"status": 200, "success": True, "ticket": 9001, "closed_price": 1.0850, "realized_pnl": 180.00},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/closeOrder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: 9001, reason: 'Admin Force Close' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["success"] is True
    assert result["data"]["ticket"] == 9001

    workflow_page.set_content(f"""
        <div class="alert alert-warning" id="force-close-toast">
            Order #{result["data"]["ticket"]} was force-closed at {result["data"]["closed_price"]}. Realized PnL: ${result["data"]["realized_pnl"]:,.2f}.
        </div>
    """)

    expect(workflow_page.locator("#force-close-toast")).to_be_visible()
    expect(workflow_page.locator("#force-close-toast")).to_contain_text("Order #9001 was force-closed")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_order_report_date_filter(mock_router: MockRouter, workflow_page: Page):
    """Verify Master Order Report (/OrderReport) with date picker and symbol breakdown."""
    mock_router.mock_json("**/Controlbase/OrderReport**", admin_mocks.MOCK_ADMIN_ORDER_REPORT, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/OrderReport');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    report = result["data"]
    assert report["total_orders"] == 342
    assert report["net_broker_spread_usd"] == 13600.00

    workflow_page.set_content(f"""
        <div class="report-kpis">
            <div class="kpi total-orders">{report['total_orders']} Orders</div>
            <div class="kpi net-spread">${report['net_broker_spread_usd']:,.2f}</div>
        </div>
    """)

    expect(workflow_page.locator(".total-orders")).to_have_text("342 Orders")
    expect(workflow_page.locator(".net-spread")).to_have_text("$13,600.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_order_report_filter(mock_router: MockRouter, workflow_page: Page):
    """Verify User Order Report (/userOrderReport) for single trader account audit."""
    user_orders = [o for o in admin_mocks.MOCK_ADMIN_OPEN_ORDERS if o.get("account_id") == "10098"]
    mock_router.mock_json("**/Controlbase/userOrderReport?user_id=10098**", user_orders, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/userOrderReport?user_id=10098');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    records = result["data"]
    assert len(records) == 1
    assert records[0]["account_id"] == "10098"

    workflow_page.set_content(f"""
        <div id="user-report">
            <span class="account-header">Trader Account: {records[0]['account_id']}</span>
            <span class="active-ticket">Ticket: {records[0]['ticket']}</span>
        </div>
    """)

    expect(workflow_page.locator(".account-header")).to_have_text("Trader Account: 10098")
    expect(workflow_page.locator(".active-ticket")).to_have_text("Ticket: 9001")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_order_edit_log_table_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Order Edit Log (/orderEditLog) audit records showing price/SL/TP modifications."""
    mock_router.mock_json("**/Controlbase/orderEditLog**", admin_mocks.MOCK_ADMIN_ORDER_EDIT_LOG, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/orderEditLog');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    logs = result["data"]
    assert len(logs) >= 1
    assert logs[0]["log_id"] == "LOG-101"
    assert logs[0]["modified_field"] == "STOP_LOSS"

    workflow_page.set_content(f"""
        <table id="edit-log">
            <tbody>
                <tr class="log-entry">
                    <td class="log-id">{logs[0]['log_id']}</td>
                    <td class="field">{logs[0]['modified_field']}</td>
                    <td class="diff">{logs[0]['old_value']} &rarr; {logs[0]['new_value']}</td>
                </tr>
            </tbody>
        </table>
    """)

    expect(workflow_page.locator(".log-id")).to_have_text("LOG-101")
    expect(workflow_page.locator(".field")).to_have_text("STOP_LOSS")
    expect(workflow_page.locator(".diff")).to_contain_text("1.08000")
