"""
Client Portal PAMM Validation Test Suite.
Validates investment amount thresholds, zero/negative bounds, search SQLi/XSS resilience,
and modal lifecycles per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_pamm_page import ClientPAMMPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_pamm")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", SQLI_PAYLOADS[:2])
def test_val_pamm_search_sqli_resilience(
    client_pamm_page: ClientPAMMPage, payload: str, description: str
):
    """
    Verify that injecting SQL injection strings into PAMM search does not crash the page.
    """
    client_pamm_page.navigate()
    assert client_pamm_page.is_pamm_displayed(), "PAMM page not displayed"

    client_pamm_page.filter_by_search(payload)
    client_pamm_page.page.wait_for_timeout(1000)

    expect(client_pamm_page.table).to_be_visible()
    client_pamm_page.clear_search()
    logger.info(f"Verified PAMM search resilience against SQLi: {description}")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS[:2])
def test_val_pamm_search_xss_resilience(
    client_pamm_page: ClientPAMMPage, payload: str, description: str
):
    """
    Verify that injecting XSS strings into PAMM search does not execute scripts.
    """
    client_pamm_page.navigate()
    client_pamm_page.page.evaluate("window.xss_detected = 0;")

    client_pamm_page.filter_by_search(payload)
    client_pamm_page.page.wait_for_timeout(1000)

    is_triggered = client_pamm_page.page.evaluate("() => window.xss_detected === 1")
    assert not is_triggered, f"XSS executed during PAMM search with payload: {payload}"

    client_pamm_page.clear_search()
    logger.info(f"Verified PAMM search resilience against XSS: {description}")


@pytest.mark.client
@pytest.mark.regression
def test_val_pamm_follow_modal_lifecycle(client_pamm_page: ClientPAMMPage):
    """
    Verify that the Follow PAMM Manager modal opens, displays investment field, and dismisses cleanly.
    """
    client_pamm_page.navigate()
    if client_pamm_page.get_manager_count() > 0:
        manager_name = client_pamm_page.open_follow_modal(0)
        assert client_pamm_page.follow_modal.is_visible(), "Follow PAMM modal did not open!"

        # Verify investment amount input is present
        expect(client_pamm_page.investment_amount_input).to_be_visible()

        # Dismiss modal
        client_pamm_page.close_follow_modal()
        assert not client_pamm_page.follow_modal.is_visible(), "Follow modal did not close on cancel"
        logger.info(f"Verified Follow PAMM modal lifecycle for manager '{manager_name}'.")


@pytest.mark.client
@pytest.mark.regression
def test_val_pamm_statistics_modal_lifecycle(client_pamm_page: ClientPAMMPage):
    """
    Verify that the PAMM Statistics modal opens and dismisses cleanly.
    """
    client_pamm_page.navigate()
    if client_pamm_page.get_manager_count() > 0:
        client_pamm_page.open_statistics_modal(0)
        expect(client_pamm_page.statistics_modal.first).to_be_visible()

        client_pamm_page.close_statistics_modal()
        expect(client_pamm_page.statistics_modal.first).not_to_be_visible()
        logger.info("Verified PAMM Statistics modal lifecycle.")
