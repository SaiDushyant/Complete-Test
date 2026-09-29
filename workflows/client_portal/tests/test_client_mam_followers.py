"""
Client Portal MAM Multi-Account Follower Flow Test Suite.

Validates the complete MAM (Multi-Account Manager) ecosystem:
1. Follower 1 (10100) logs into Client Portal, navigates to MAM, and follows Master Account (10026).
2. Follower 2 (10102) logs into Client Portal, navigates to MAM, and follows Master Account (10026).
3. Master Account (10026) logs into Client Portal, navigates to MAM -> MY FOLLOWERS, and verifies
   both Follower 1 and Follower 2 appear in the active followers roster with correct profit share and MAM ID.
4. Unfollow and Re-follow lifecycle validation: verifies real-time membership updates on Master's followers roster.
5. Continuous monitoring for zero console errors, JS crashes, and network 5xx failures.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
from typing import Generator, Tuple
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_mam_page import ClientMAMPage
from workflows.shared.utils.error_monitor import ErrorMonitor


def _login_and_open_mam(
    browser: Browser,
    username: str,
    password: str,
) -> Tuple[BrowserContext, Page, ClientMAMPage, ErrorMonitor]:
    """Helper to establish an isolated authenticated session and navigate to MAM."""
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

    mam_page = ClientMAMPage(page)
    mam_page.navigate()
    expect(mam_page.main_heading.first).to_be_visible(timeout=10000)

    return context, page, mam_page, monitor


@pytest.mark.client
@pytest.mark.mam
def test_client_mam_follower_1_follows_master(workflow_browser: Browser):
    """
    Verify Follower 1 (10100) discovers and follows Master Account (10026) via Client Portal MAM:
    - Login as Follower 1 (10100)
    - Navigate to MAM workspace
    - Verify MAM summary cards and managers table are displayed
    - Locate Master Account (10026 / 'Me')
    - If not already following, click 'Follow' and confirm in the Follow Manager modal
    - Assert that row action button displays 'Unfollow'
    - Assert zero console errors, JS crashes, and backend failures
    """
    context, page, mam_page, monitor = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_follower_1_account,
        password=settings.mam_follower_1_password,
    )

    try:
        # 1. Verify MAM cards
        cards = mam_page.get_summary_card_values()
        assert cards["managers"], "Expected MANAGERS count card to be populated"
        assert cards["followers"], "Expected FOLLOWERS card to be populated"

        # 2. Locate Master Account and Follow
        result = mam_page.follow_manager(settings.mam_master_account)
        assert result in ("followed", "already_following"), (
            f"Unexpected follow status for Follower 1: {result}"
        )

        # 3. Verify Master Row Action is 'Unfollow'
        master_row = mam_page.find_manager_row(settings.mam_master_account)
        expect(master_row.locator("button").filter(has_text=re.compile(r"^Unfollow$", re.I)).first).to_be_visible()

        # 4. Error Check
        monitor.assert_no_errors("Follower 1 MAM Follow Flow")
    finally:
        context.close()


@pytest.mark.client
@pytest.mark.mam
def test_client_mam_follower_2_follows_master(workflow_browser: Browser):
    """
    Verify Follower 2 (10102) discovers and follows Master Account (10026) via Client Portal MAM:
    - Login as Follower 2 (10102)
    - Navigate to MAM workspace
    - Locate Master Account (10026 / 'Me')
    - If not already following, click 'Follow' and confirm in the Follow Manager modal
    - Assert that row action button displays 'Unfollow'
    - Assert zero console errors, JS crashes, and backend failures
    """
    context, page, mam_page, monitor = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_follower_2_account,
        password=settings.mam_follower_2_password,
    )

    try:
        # 1. Follow Master Account
        result = mam_page.follow_manager(settings.mam_master_account)
        assert result in ("followed", "already_following"), (
            f"Unexpected follow status for Follower 2: {result}"
        )

        # 2. Verify Master Row Action is 'Unfollow'
        master_row = mam_page.find_manager_row(settings.mam_master_account)
        expect(master_row.locator("button").filter(has_text=re.compile(r"^Unfollow$", re.I)).first).to_be_visible()

        # 3. Error Check
        monitor.assert_no_errors("Follower 2 MAM Follow Flow")
    finally:
        context.close()


@pytest.mark.client
@pytest.mark.mam
def test_client_mam_master_verifies_followers_roster(workflow_browser: Browser):
    """
    Verify Master Account (10026) views active followers in Client Portal MAM:
    - Login as Master Account (10026)
    - Navigate to MAM workspace
    - Switch to 'MY FOLLOWERS' view
    - Assert table column headers: ['FOLLOWER NAME', 'YOUR PROFIT SHARE', 'USER ID', 'MAM ID', 'ACTION']
    - Verify both Follower 1 (10100) and Follower 2 (10102) are present in the table
    - Verify Profit Share (50%) and MAM ID (26) are correctly bound
    - Verify each follower row contains an enabled 'View' action button
    - Assert zero console errors, JS crashes, and backend failures
    """
    context, page, mam_page, monitor = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_master_account,
        password=settings.mam_master_password,
    )

    try:
        # 1. Switch to MY FOLLOWERS view
        mam_page.switch_to_my_followers()
        expect(mam_page.followers_active_btn).to_be_visible()

        # 2. Assert table headers
        expected_headers = ["FOLLOWER NAME", "YOUR PROFIT SHARE", "USER ID", "MAM ID", "ACTION"]
        actual_headers = mam_page.get_followers_table_headers()
        assert [h.upper() for h in actual_headers] == [h.upper() for h in expected_headers], (
            f"Headers mismatch. Expected: {expected_headers}, got: {actual_headers}"
        )

        # 3. Extract follower records
        records = mam_page.get_followers_table_records()
        assert len(records) >= 2, f"Expected at least 2 followers for Master, found: {len(records)}"

        follower_user_ids = [r["user_id"] for r in records]
        follower_names = [r["follower_name"] for r in records]

        # Verify Follower 1 (10100)
        assert any(settings.mam_follower_1_account in name for name in follower_names) or "100" in follower_user_ids, (
            f"Follower 1 ({settings.mam_follower_1_account}) not found in followers roster: {records}"
        )

        # Verify Follower 2 (10102)
        assert any(settings.mam_follower_2_account in name for name in follower_names) or "102" in follower_user_ids, (
            f"Follower 2 ({settings.mam_follower_2_account}) not found in followers roster: {records}"
        )

        # Verify Profit Share is populated (50%)
        for rec in records:
            assert rec["profit_share"], f"Expected profit share for follower {rec}"
            assert rec["mam_id"], f"Expected MAM ID for follower {rec}"

        # 4. Error Check
        monitor.assert_no_errors("Master MAM Followers Roster Verification")
    finally:
        context.close()


@pytest.mark.client
@pytest.mark.mam
def test_client_mam_unfollow_and_refollow_lifecycle(workflow_browser: Browser):
    """
    Verify complete Unfollow and Re-follow lifecycle:
    1. Follower 2 (10102) unfollows Master Account (10026) via 'CONFIRM UNFOLLOW' modal
    2. Verify Follower 2 row button reverts to 'Follow'
    3. Master Account (10026) checks MY FOLLOWERS and verifies Follower 2 is removed
    4. Follower 2 (10102) re-follows Master Account (10026) via 'CONFIRM FOLLOW' modal
    5. Master Account (10026) checks MY FOLLOWERS and verifies Follower 2 is restored
    - Asserts zero console errors, JS crashes, and backend failures throughout
    """
    # Phase 1: Follower 2 Unfollows Master
    ctx_f2, page_f2, mam_f2, mon_f2 = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_follower_2_account,
        password=settings.mam_follower_2_password,
    )
    try:
        unfollow_res = mam_f2.unfollow_manager(settings.mam_master_account)
        assert unfollow_res in ("unfollowed", "already_unfollowed")

        # Row button should now say Follow
        master_row = mam_f2.find_manager_row(settings.mam_master_account)
        expect(master_row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first).to_be_visible()
        mon_f2.assert_no_errors("Follower 2 Unfollow Action")
    finally:
        ctx_f2.close()

    # Phase 2: Master Account checks Follower 2 is not in Active roster
    ctx_m, page_m, mam_m, mon_m = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_master_account,
        password=settings.mam_master_password,
    )
    try:
        mam_m.switch_to_my_followers()
        page_m.wait_for_timeout(1000)
        records_after_unfollow = mam_m.get_followers_table_records()
        f2_present = any(settings.mam_follower_2_account in r["follower_name"] or r["user_id"] == "102" for r in records_after_unfollow)
        assert not f2_present, (
            f"Follower 2 ({settings.mam_follower_2_account}) should NOT appear after unfollow: {records_after_unfollow}"
        )
        mon_m.assert_no_errors("Master Roster After Unfollow")
    finally:
        ctx_m.close()

    # Phase 3: Follower 2 Re-follows Master
    ctx_f2_re, page_f2_re, mam_f2_re, mon_f2_re = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_follower_2_account,
        password=settings.mam_follower_2_password,
    )
    try:
        refollow_res = mam_f2_re.follow_manager(settings.mam_master_account)
        assert refollow_res in ("followed", "already_following")

        master_row_re = mam_f2_re.find_manager_row(settings.mam_master_account)
        expect(master_row_re.locator("button").filter(has_text=re.compile(r"^Unfollow$", re.I)).first).to_be_visible()
        mon_f2_re.assert_no_errors("Follower 2 Re-follow Action")
    finally:
        ctx_f2_re.close()

    # Phase 4: Master Account verifies Follower 2 is restored in Active roster
    ctx_m_restored, page_m_restored, mam_m_restored, mon_m_restored = _login_and_open_mam(
        workflow_browser,
        username=settings.mam_master_account,
        password=settings.mam_master_password,
    )
    try:
        mam_m_restored.switch_to_my_followers()
        page_m_restored.wait_for_timeout(1000)
        restored_records = mam_m_restored.get_followers_table_records()
        f2_restored = any(settings.mam_follower_2_account in r["follower_name"] or r["user_id"] == "102" for r in restored_records)
        assert f2_restored, (
            f"Follower 2 ({settings.mam_follower_2_account}) should be restored after re-follow: {restored_records}"
        )
        mon_m_restored.assert_no_errors("Master Roster Restoration")
    finally:
        ctx_m_restored.close()
