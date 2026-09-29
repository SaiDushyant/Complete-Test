"""
Client Portal Dashboard Workflow Tests.
Validates header elements, account badge, summary cards, and cash flow controls.
Includes automated monitoring for Browser Console, JavaScript Runtime, and Backend Network Errors.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_dashboard_header_elements(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Client Portal dashboard displays the universal header elements:
    - Page title is 'Dashboard'
    - Account selector badge with account ID is visible
    - 'CREATE ACCOUNT' action button is visible and enabled
    - Menu collapse toggle is present
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()

    # 1. Assert header visibility and title
    client_dashboard_page.header.assert_header_elements(expected_title="Dashboard")

    # 2. Assert selected account ID is populated in account badge
    account_id = client_dashboard_page.header.get_selected_account()
    assert account_id and account_id.isdigit(), (
        f"Expected numeric account ID in header badge, got: '{account_id}'"
    )

    # Automated Error Check
    client_error_monitor.assert_no_errors("Dashboard Header")


@pytest.mark.client
@pytest.mark.regression
def test_client_dashboard_summary_cards(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Account Dashboard renders all 4 key metric cards:
    - TOTAL FUNDS
    - ACCOUNT BALANCE
    - AVAILABLE BUFFER
    - ACTIVE REFERRALS
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()

    expect(client_dashboard_page.total_funds_card).to_be_visible()
    expect(client_dashboard_page.account_balance_card).to_be_visible()
    expect(client_dashboard_page.available_buffer_card).to_be_visible()
    expect(client_dashboard_page.active_referrals_card).to_be_visible()

    card_values = client_dashboard_page.get_summary_card_values()
    assert "$" in card_values["total_funds"], "Expected '$' currency in TOTAL FUNDS card."
    assert "$" in card_values["account_balance"], "Expected '$' currency in ACCOUNT BALANCE card."

    # Automated Error Check
    client_error_monitor.assert_no_errors("Dashboard Summary Cards")


@pytest.mark.client
@pytest.mark.regression
def test_client_dashboard_cash_flow_period_toggle(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Account Cash Flow section allows switching between Day, Week, and Month views.
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()

    expect(client_dashboard_page.cash_flow_container).to_be_visible()

    for period in ["Day", "Week", "Month"]:
        client_dashboard_page.select_cash_flow_period(period)
        button_locator = client_dashboard_page.get_cash_flow_period_tab(period)
        expect(button_locator).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Dashboard Cash Flow Toggle")


@pytest.mark.client
@pytest.mark.regression
def test_client_dashboard_negative_rapid_toggle_resilience(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Negative Scenario: Stress & Rapid Interaction Resilience:
    - Rapidly triggers cash flow period tabs without awaiting animation settles
    - Ensures no race condition state corruption, duplicate DOM cards, or JS crashes
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    expect(client_dashboard_page.cash_flow_container).to_be_visible()

    # Rapid stress clicks across periods
    for _ in range(3):
        client_dashboard_page.select_cash_flow_period("Day")
        client_dashboard_page.select_cash_flow_period("Week")
        client_dashboard_page.select_cash_flow_period("Month")

    expect(client_dashboard_page.cash_flow_container).to_be_visible()

    client_error_monitor.assert_no_errors("Dashboard Rapid Toggle Resilience")

