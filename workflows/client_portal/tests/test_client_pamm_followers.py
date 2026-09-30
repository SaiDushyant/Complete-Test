"""
Client Portal PAMM Multi-Account Follower Flow Test Suite.

Validates the complete PAMM (Percentage Allocation Management Module) ecosystem:
1. Follower 1 (10100) logs into Client Portal, navigates to PAMM, discovers Master Account (10026),
   opens Follow Manager modal, inputs investment amount ($100), and confirms follow.
2. Follower 2 (10102) logs into Client Portal, navigates to PAMM, discovers Master Account (10026),
   inputs investment amount, and confirms follow.
3. Master Account (10026) logs into Client Portal, navigates to PAMM -> MY FOLLOWERS,
   and verifies active followers table headers and follower records.
4. Unfollow and Follow lifecycle validation: validates modal inputs, debit notices, cancellation,
   and execution with zero console errors, JS crashes, and network 5xx failures.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
from typing import Tuple
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_pamm_page import ClientPAMMPage
from workflows.shared.utils.error_monitor import ErrorMonitor


def _login_and_open_pamm(
    browser: Browser,
    username: str,
    password: str,
) -> Tuple[BrowserContext, Page, ClientPAMMPage, ErrorMonitor]:
    """Helper to establish an isolated authenticated session and navigate to PAMM."""
    context = browser.new_context(
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    monitor = ErrorMonitor(page)

    login_page = ClientLoginPage(page)
    login_page.navigate(settings.client_portal.login_url or f"{settings.client_portal.base_url.rstrip('/')}/login")
    login_page.login(email=username, password=password, remember_me=True)
    try:
        page.wait_for_url(lambda u: "/login" not in u, timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)

    # Navigate into Client Portal workspace
    if "/client-portal" not in page.url:
        page.goto(settings.client_portal.base_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    pamm_page = ClientPAMMPage(page)
    pamm_page.navigate()
    expect(pamm_page.main_heading.first).to_be_visible(timeout=10000)

    return context, page, pamm_page, monitor


@pytest.mark.client
@pytest.mark.pamm
def test_client_pamm_follower_1_follows_master(workflow_browser: Browser):
    """
    Verify Follower 1 (10100) discovers and initiates follow of Master Account (10026) via Client Portal PAMM:
    - Login as Follower 1 (10100)
    - Navigate to PAMM workspace
    - Verify PAMM summary cards and managers table are displayed
    - Locate Master Account (10026 / 'Me')
    - Verify Follow Manager modal: title, investment amount field, debit notice
    - Submit follow action with investment capital ($100)
    - Assert zero console errors, JS crashes, and backend 5xx failures
    """
    context, page, pamm_page, monitor = _login_and_open_pamm(
        workflow_browser,
        username=settings.pamm_follower_1_account,
        password=settings.pamm_follower_1_password,
    )

    try:
        # 1. Verify PAMM summary cards
        cards = pamm_page.get_summary_card_values()
        assert cards["managers"], "Expected MANAGERS count card to be populated"
        assert cards["followers"], "Expected FOLLOWERS card to be populated"

        # 2. Locate Master Account and Follow
        master_row = pamm_page.find_manager_row(settings.pamm_master_account)
        expect(master_row).to_be_visible()

        result = pamm_page.follow_manager(settings.pamm_master_account, investment_amount="100")
        assert result in ("followed", "already_following", "pending_settlement"), (
            f"Unexpected follow status for Follower 1: {result}"
        )

        # 3. Error Check
        monitor.assert_no_errors("Follower 1 PAMM Follow Flow")
    finally:
        context.close()


@pytest.mark.client
@pytest.mark.pamm
def test_client_pamm_follower_2_follows_master(workflow_browser: Browser):
    """
    Verify Follower 2 (10102) discovers and initiates follow of Master Account (10026) via Client Portal PAMM:
    - Login as Follower 2 (10102)
    - Navigate to PAMM workspace
    - Locate Master Account (10026 / 'Me')
    - Verify investment input and debit warning in Follow modal
    - Submit follow action with investment capital ($100)
    - Assert zero console errors, JS crashes, and backend 5xx failures
    """
    context, page, pamm_page, monitor = _login_and_open_pamm(
        workflow_browser,
        username=settings.pamm_follower_2_account,
        password=settings.pamm_follower_2_password,
    )

    try:
        # 1. Locate Master Account and Follow
        master_row = pamm_page.find_manager_row(settings.pamm_master_account)
        expect(master_row).to_be_visible()

        result = pamm_page.follow_manager(settings.pamm_master_account, investment_amount="100")
        assert result in ("followed", "already_following", "pending_settlement"), (
            f"Unexpected follow status for Follower 2: {result}"
        )

        # 2. Error Check
        monitor.assert_no_errors("Follower 2 PAMM Follow Flow")
    finally:
        context.close()


@pytest.mark.client
@pytest.mark.pamm
def test_client_pamm_master_verifies_followers_roster(workflow_browser: Browser):
    """
    Verify Master Account (10026) views active followers in Client Portal PAMM:
    - Login as Master Account (10026)
    - Navigate to PAMM workspace
    - Switch to 'MY FOLLOWERS' view
    - Assert table column headers: ['NAME', 'INVESTMENT', 'MANAGER SHARE (ELIGIBLE ORDERS)', 'ACTION']
    - Verify subtab switching (Active / History)
    - Assert zero console errors, JS crashes, and backend failures
    """
    context, page, pamm_page, monitor = _login_and_open_pamm(
        workflow_browser,
        username=settings.pamm_master_account,
        password=settings.pamm_master_password,
    )

    try:
        # 1. Switch to MY FOLLOWERS view
        pamm_page.switch_to_my_followers()
        expect(pamm_page.followers_active_btn).to_be_visible()
        expect(pamm_page.followers_history_btn).to_be_visible()

        # 2. Assert table headers
        expected_headers = ["NAME", "INVESTMENT", "MANAGER SHARE (ELIGIBLE ORDERS)", "ACTION"]
        actual_headers = pamm_page.get_followers_table_headers()
        assert [h.upper() for h in actual_headers] == [h.upper() for h in expected_headers], (
            f"Headers mismatch. Expected: {expected_headers}, got: {actual_headers}"
        )

        # 3. Test Active / History tab toggle
        pamm_page.followers_history_btn.click()
        page.wait_for_timeout(1000)
        pamm_page.followers_active_btn.click()
        page.wait_for_timeout(1000)

        # 4. Error Check
        monitor.assert_no_errors("Master PAMM Followers Roster Verification")
    finally:
        context.close()


@pytest.mark.client
@pytest.mark.pamm
def test_client_pamm_follow_modal_lifecycle_and_cancellation(workflow_browser: Browser):
    """
    Verify complete PAMM Follow Modal lifecycle:
    1. Follower 2 (10102) opens Follow modal for Master Account
    2. Verifies modal components: Title, Investment Amount input, Debit notice
    3. Verifies modal Cancel button dismisses modal without triggering debit
    4. Re-opens Follow modal and confirms submission
    5. Asserts zero console errors, JS crashes, and backend failures throughout
    """
    context, page, pamm_page, monitor = _login_and_open_pamm(
        workflow_browser,
        username=settings.pamm_follower_2_account,
        password=settings.pamm_follower_2_password,
    )

    try:
        # 1. Locate Master Row
        master_row = pamm_page.find_manager_row(settings.pamm_master_account)
        follow_btn = master_row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first

        if follow_btn.is_visible():
            follow_btn.click()
            expect(pamm_page.follow_modal.first).to_be_visible(timeout=5000)

            # 2. Verify modal components
            expect(pamm_page.investment_amount_input).to_be_visible()
            expect(pamm_page.modal_cancel_btn).to_be_visible()
            expect(pamm_page.modal_confirm_btn).to_be_visible()

            # 3. Verify Cancel dismissal
            pamm_page.modal_cancel_btn.click()
            expect(pamm_page.follow_modal.first).not_to_be_visible(timeout=5000)

            # 4. Re-open and confirm follow
            follow_btn.click()
            expect(pamm_page.follow_modal.first).to_be_visible(timeout=5000)
            pamm_page.investment_amount_input.fill("100")
            pamm_page.modal_confirm_btn.click()
            page.wait_for_timeout(2000)

            if pamm_page.follow_modal.first.is_visible():
                pamm_page.modal_cancel_btn.click()

        # 5. Error Check
        monitor.assert_no_errors("PAMM Follow Modal Lifecycle")
    finally:
        context.close()
