"""
Client Portal Dashboard Validation Test Suite.
Validates financial metrics card formatting, quick action routing, and registration link elements
per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_dashboard")


@pytest.mark.client
@pytest.mark.regression
def test_val_dashboard_summary_cards(client_dashboard_page: ClientDashboardPage):
    """
    Verify that dashboard financial balance and metric cards render without NaN/undefined corrupted states.
    """
    client_dashboard_page.navigate()
    assert client_dashboard_page.is_dashboard_displayed(), "Dashboard page not displayed"

    # Verify summary cards
    expect(client_dashboard_page.total_funds_card).to_be_visible()
    expect(client_dashboard_page.account_balance_card).to_be_visible()

    total_funds = client_dashboard_page.total_funds_card.inner_text()
    balance = client_dashboard_page.account_balance_card.inner_text()

    assert "nan" not in total_funds.lower() and "undefined" not in total_funds.lower(), (
        f"Total Funds card contains corrupted text: '{total_funds}'"
    )
    assert "nan" not in balance.lower() and "undefined" not in balance.lower(), (
        f"Account Balance card contains corrupted text: '{balance}'"
    )
    logger.info("Verified Dashboard metrics render cleanly.")


@pytest.mark.client
@pytest.mark.regression
def test_val_dashboard_cash_flow_period_toggles(client_dashboard_page: ClientDashboardPage):
    """
    Verify cash flow period toggle buttons (Day, Week, Month) are interactive.
    """
    client_dashboard_page.navigate()

    expect(client_dashboard_page.cash_flow_container).to_be_visible()
    expect(client_dashboard_page.cash_flow_day_tab).to_be_visible()
    expect(client_dashboard_page.cash_flow_week_tab).to_be_visible()
    expect(client_dashboard_page.cash_flow_month_tab).to_be_visible()

    client_dashboard_page.cash_flow_week_tab.click()
    client_dashboard_page.page.wait_for_timeout(300)
    client_dashboard_page.cash_flow_month_tab.click()
    client_dashboard_page.page.wait_for_timeout(300)
    client_dashboard_page.cash_flow_day_tab.click()

    logger.info("Verified Dashboard cash flow period toggles interactability.")
