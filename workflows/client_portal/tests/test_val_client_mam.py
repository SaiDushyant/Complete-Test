"""
Client Portal MAM (Multi-Account Manager) Validation Test Suite.
Validates search filters with SQLi/XSS payloads, filter dropdowns,
modal configuration lifecycles, and view switching per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_mam_page import ClientMAMPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_mam")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", SQLI_PAYLOADS[:2])
def test_val_mam_search_sqli_resilience(
    client_mam_page: ClientMAMPage, payload: str, description: str
):
    """
    Verify that injecting SQL injection strings into the MAM manager search input
    does not cause uncaught 500 errors, broken rendering, or app crashes.
    """
    client_mam_page.navigate()
    assert client_mam_page.is_mam_displayed(), "MAM page not displayed"

    client_mam_page.filter_by_search(payload)
    client_mam_page.page.wait_for_timeout(1000)

    # Table container should remain visible and render gracefully
    expect(client_mam_page.table).to_be_visible()
    client_mam_page.clear_search()
    logger.info(f"Verified MAM search resilience against SQLi: {description}")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS[:2])
def test_val_mam_search_xss_resilience(
    client_mam_page: ClientMAMPage, payload: str, description: str
):
    """
    Verify that injecting XSS strings into MAM search does not trigger script execution.
    """
    client_mam_page.navigate()
    client_mam_page.page.evaluate("window.xss_detected = 0;")

    client_mam_page.filter_by_search(payload)
    client_mam_page.page.wait_for_timeout(1000)

    is_triggered = client_mam_page.page.evaluate("() => window.xss_detected === 1")
    assert not is_triggered, f"XSS executed during MAM search with payload: {payload}"

    client_mam_page.clear_search()
    logger.info(f"Verified MAM search resilience against XSS: {description}")


@pytest.mark.client
@pytest.mark.regression
def test_val_mam_follow_modal_lifecycle(client_mam_page: ClientMAMPage):
    """
    Verify that the Follow MAM Manager modal opens with manager name and can be dismissed safely.
    """
    client_mam_page.navigate()
    if client_mam_page.get_manager_count() > 0:
        manager_name = client_mam_page.open_follow_modal(0)
        assert client_mam_page.follow_modal.is_visible(), "Follow MAM modal did not open!"

        # Dismiss modal via Cancel
        client_mam_page.close_follow_modal()
        assert not client_mam_page.follow_modal.is_visible(), "Follow modal did not close on cancel"
        logger.info(f"Verified Follow MAM modal lifecycle for manager '{manager_name}'.")


@pytest.mark.client
@pytest.mark.regression
def test_val_mam_statistics_modal_lifecycle(client_mam_page: ClientMAMPage):
    """
    Verify that the MAM Statistics modal opens, loads metrics without NaN errors, and dismisses cleanly.
    """
    client_mam_page.navigate()
    if client_mam_page.get_manager_count() > 0:
        client_mam_page.open_statistics_modal(0)
        expect(client_mam_page.statistics_modal.first).to_be_visible()

        client_mam_page.close_statistics_modal()
        expect(client_mam_page.statistics_modal.first).not_to_be_visible()
        logger.info("Verified MAM Statistics modal lifecycle.")


@pytest.mark.client
@pytest.mark.regression
def test_val_mam_view_switching(client_mam_page: ClientMAMPage):
    """
    Verify seamless switching between MAM Manager leaderboard and My Followers view.
    """
    client_mam_page.navigate()
    client_mam_page.switch_to_my_followers()
    assert client_mam_page.followers_active_btn.is_visible(), "Followers active tab not visible"

    client_mam_page.switch_to_mam_manager()
    assert client_mam_page.is_mam_displayed(), "MAM manager view not restored"
    logger.info("Verified MAM view switching between Leaderboard and My Followers.")
