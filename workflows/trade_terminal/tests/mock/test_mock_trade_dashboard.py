"""
Trade Terminal Mock Tests: Dashboard Analytics, Charts, and Metrics.
Validates summary cards, PnL period toggles, Most Traded symbols, empty stat states, and performance KPI cards.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_metric_cards_render(mock_router: MockRouter, workflow_page: Page):
    """Verify overview summary cards (Account Status, Token, Balance, Free Margin)."""
    mock_router.mock_json("**/api/**/dashboard/overview**", trade_mocks.MOCK_DASHBOARD_OVERVIEW, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/overview');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    overview = result["data"]
    assert overview["account_status"] == "Verified"
    assert overview["balance"] == 25000.00
    assert overview["free_margin"] == 24365.36

    workflow_page.set_content(f"""
        <div class="account-overview">
            <div class="card status-card"><span class="badge">{overview['account_status']}</span></div>
            <div class="card balance-card"><span class="val">${overview['balance']:,.2f}</span></div>
            <div class="card margin-card"><span class="val">${overview['free_margin']:,.2f}</span></div>
        </div>
    """)

    expect(workflow_page.locator(".status-card .badge")).to_have_text("Verified")
    expect(workflow_page.locator(".balance-card .val")).to_have_text("$25,000.00")
    expect(workflow_page.locator(".margin-card .val")).to_have_text("$24,365.36")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_pnl_daily_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify Daily PnL period toggle renders daily curve data."""
    mock_router.mock_json("**/api/**/dashboard/pnl?period=daily**", trade_mocks.MOCK_DASHBOARD_PNL_SERIES["daily"], status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/pnl?period=daily');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["title"] == "Daily P/L"
    assert len(result["data"]["data"]) == 6

    workflow_page.set_content(f"""
        <div class="pnl-chart-header">
            <h4>{result["data"]["title"]}</h4>
            <span class="datapoints-count">{len(result["data"]["data"])} data points</span>
        </div>
    """)

    expect(workflow_page.locator(".pnl-chart-header h4")).to_have_text("Daily P/L")
    expect(workflow_page.locator(".datapoints-count")).to_have_text("6 data points")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_pnl_weekly_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify Weekly PnL period toggle renders weekly aggregations."""
    mock_router.mock_json("**/api/**/dashboard/pnl?period=weekly**", trade_mocks.MOCK_DASHBOARD_PNL_SERIES["weekly"], status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/pnl?period=weekly');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["title"] == "Weekly P/L"
    assert len(result["data"]["data"]) == 4

    workflow_page.set_content(f"<h4>{result['data']['title']}</h4>")
    expect(workflow_page.locator("h4")).to_have_text("Weekly P/L")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_pnl_monthly_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify Monthly PnL period toggle renders month-by-month profit curves."""
    mock_router.mock_json("**/api/**/dashboard/pnl?period=monthly**", trade_mocks.MOCK_DASHBOARD_PNL_SERIES["monthly"], status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/pnl?period=monthly');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["title"] == "Monthly P/L"
    assert len(result["data"]["data"]) == 4

    workflow_page.set_content(f"<h4>{result['data']['title']}</h4>")
    expect(workflow_page.locator("h4")).to_have_text("Monthly P/L")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_most_traded_symbols(mock_router: MockRouter, workflow_page: Page):
    """Verify Most Traded breakdown list and percentages."""
    mock_router.mock_json("**/api/**/dashboard/most-traded**", trade_mocks.MOCK_DASHBOARD_MOST_TRADED, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/most-traded');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    symbols = result["data"]
    assert len(symbols) == 3
    assert symbols[0]["symbol"] == "EURUSD"
    assert symbols[0]["percentage"] == 50.0

    items = "".join([
        f"<li class='symbol-item'><span class='name'>{s['symbol']}</span><span class='pct'>{s['percentage']}%</span></li>"
        for s in symbols
    ])
    workflow_page.set_content(f"<ul class='traded-list'>{items}</ul>")

    expect(workflow_page.locator(".symbol-item")).to_have_count(3)
    expect(workflow_page.locator(".symbol-item >> nth=0 >> .name")).to_have_text("EURUSD")
    expect(workflow_page.locator(".symbol-item >> nth=0 >> .pct")).to_have_text("50%")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_empty_trade_stats(mock_router: MockRouter, workflow_page: Page):
    """Verify brand new trading account with zero trades renders default clean metrics."""
    mock_router.mock_json("**/api/**/dashboard/most-traded**", [], status=200)
    mock_router.mock_json("**/api/**/dashboard/pnl**", {"title": "PnL", "data": []}, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/most-traded');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert len(result["data"]) == 0

    workflow_page.set_content("""
        <div class="empty-state">
            <span class="message">No trades recorded yet. Start trading to view analytics.</span>
        </div>
    """)

    expect(workflow_page.locator(".empty-state .message")).to_be_visible()
    expect(workflow_page.locator(".empty-state .message")).to_contain_text("No trades recorded yet")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_performance_stats_cards(mock_router: MockRouter, workflow_page: Page):
    """Verify all 8 performance stat KPIs in overview card."""
    mock_router.mock_json("**/api/**/dashboard/performance**", trade_mocks.MOCK_DASHBOARD_PERFORMANCE_STATS, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/dashboard/performance');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    stats = result["data"]
    assert stats["win_ratio"] == "75%"
    assert stats["avg_win"] == "$125.50"
    assert stats["max_drawdown"] == "4.2%"

    workflow_page.set_content(f"""
        <div class="stats-grid">
            <div class="stat-box win-ratio"><span class="val">{stats['win_ratio']}</span></div>
            <div class="stat-box avg-win"><span class="val">{stats['avg_win']}</span></div>
            <div class="stat-box max-dd"><span class="val">{stats['max_drawdown']}</span></div>
        </div>
    """)

    expect(workflow_page.locator(".win-ratio .val")).to_have_text("75%")
    expect(workflow_page.locator(".avg-win .val")).to_have_text("$125.50")
    expect(workflow_page.locator(".max-dd .val")).to_have_text("4.2%")
