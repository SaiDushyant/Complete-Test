"""
Client Portal Copy Trading Validation Test Suite.
Validates search filters with malicious/boundary inputs, trade method modal configuration,
and summary metric boundaries per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_copy_trading")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.fixture(scope="function")
def client_copy_trading_page(authenticated_client_page: Page) -> ClientCopyTradingPage:
    """Provide an authenticated ClientCopyTradingPage object."""
    return ClientCopyTradingPage(authenticated_client_page)


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", SQLI_PAYLOADS[:2])
def test_val_copy_trading_search_sqli_resilience(
    client_copy_trading_page: ClientCopyTradingPage, payload: str, description: str
):
    """
    Verify that injecting SQL injection strings into the manager search input
    does not cause uncaught 500 errors or app crashes.
    """
    client_copy_trading_page.navigate()
    assert client_copy_trading_page.is_copy_trading_displayed(), "Copy trading page not displayed"

    # Filter with SQLi payload
    client_copy_trading_page.filter_by_search(payload)
    client_copy_trading_page.page.wait_for_timeout(1000)

    # Table should still exist without crashing
    expect(client_copy_trading_page.table).to_be_visible()
    client_copy_trading_page.clear_search()
    logger.info(f"Verified Copy Trading search resilience against SQLi: {description}")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS[:2])
def test_val_copy_trading_search_xss_resilience(
    client_copy_trading_page: ClientCopyTradingPage, payload: str, description: str
):
    """
    Verify that injecting XSS strings into manager search does not trigger client script execution.
    """
    client_copy_trading_page.navigate()
    client_copy_trading_page.page.evaluate("window.xss_detected = 0;")

    client_copy_trading_page.filter_by_search(payload)
    client_copy_trading_page.page.wait_for_timeout(1000)

    is_triggered = client_copy_trading_page.page.evaluate("() => window.xss_detected === 1")
    assert not is_triggered, f"XSS executed during Copy Trading search with payload: {payload}"

    client_copy_trading_page.clear_search()
    logger.info(f"Verified Copy Trading search resilience against XSS: {description}")


@pytest.mark.client
@pytest.mark.regression
def test_val_copy_trading_follow_modal_lifecycle(client_copy_trading_page: ClientCopyTradingPage):
    """
    Verify that the Follow Manager modal opens, provides method choices, and can be cancelled safely.
    """
    client_copy_trading_page.navigate()
    if client_copy_trading_page.get_manager_count() > 0:
        manager_name = client_copy_trading_page.open_follow_modal(0)
        assert client_copy_trading_page.follow_modal.is_visible(), "Follow modal did not open!"

        # Verify trade method options are visible
        assert client_copy_trading_page.modal_balance_based.is_visible(), "Balance Based method missing"
        assert client_copy_trading_page.modal_equity_based.is_visible(), "Equity Based method missing"

        # Dismiss modal via Cancel
        client_copy_trading_page.close_follow_modal()
        assert not client_copy_trading_page.follow_modal.is_visible(), "Follow modal did not close on cancel"
        logger.info(f"Verified Follow Modal lifecycle for manager '{manager_name}'.")
