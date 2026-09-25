"""
Trade Terminal Workflow Example Test (Template).
Demonstrates fixture injection, Page Object usage, assertion conventions, and markers.
Maintained by Developer 1 (Trade Terminal Owner).

NOTE: This is an architectural template/example showing how new behavioral tests
should be structured. When implementing real workflows, replace the mock/TODO steps.
"""

import pytest

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


@pytest.mark.trade
@pytest.mark.smoke
def test_trade_login_page_renders_form_elements(trade_login_page: TradeLoginPage):
    """
    Verify that the unauthenticated Trade Terminal login page displays
    all required credentials inputs and the submission button.
    """
    trade_login_page.navigate()

    # Assert form presence
    assert trade_login_page.is_login_page_displayed(), (
        f"Expected Trade Terminal login page at '{settings.trade_terminal.login_url}' to show login form."
    )


@pytest.mark.trade
@pytest.mark.regression
def test_trader_can_view_dashboard_workspace(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that an authenticated trader can access the trading dashboard.
    Demonstrates authenticated fixture usage without repeating login steps.
    """
    trading_dashboard_page.navigate()

    # Assert dashboard container visibility
    assert_element_is_visible(
        trading_dashboard_page.dashboard_container,
        element_name="Trade Terminal Dashboard Workspace",
    )

    # TODO (Developer 1): Add specific workflow steps (e.g. order submission, watchlist symbol selection)
