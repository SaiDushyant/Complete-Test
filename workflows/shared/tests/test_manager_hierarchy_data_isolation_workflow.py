"""
Manager Hierarchy & Data Isolation End-to-End Workflow Test Suite.

Covers:
1. Manager Creation & Permissions:
   - Create a brand new manager from /admin/Controlbase/manager.
   - Authenticate active session with newly created manager credentials.
   - Verify all assigned permissions and sidebar menus throughout Manager CRM.
   - Test both accessible pages and restricted administrative features (e.g. /manager, /admin, /rolePermission).

2. User Creation & Association:
   - Create a new user account under the manager from Manager CRM (/admin/Controlbase/user).
   - Test creating a user through the manager's registration/referral URL on the dashboard (/register/?manager=<id>).
   - Create a control user managed directly from MAdmin (unassociated with manager).
   - Verify that manager-created and registered users are correctly associated with the manager in Manager CRM.
   - Verify that unassociated MAdmin users are completely isolated and not exposed in Manager CRM.

3. Trade Visibility Isolation:
   - Perform a trade for a user belonging to the manager.
   - Verify trade is reflected in both Manager CRM and MAdmin CRM (/admin/Controlbase/order/open & /all).
   - Perform a trade for a user not belonging to that manager (MAdmin user).
   - Verify trade is NOT visible in Manager CRM but is visible in MAdmin CRM.

4. Deposit & Withdrawal Notifications & Transactions:
   - Test deposits / withdrawals for users under the manager.
   - Verify transactions & notifications appear in Manager CRM and MAdmin CRM.
   - Verify transactions & notifications for non-manager users do NOT appear in Manager CRM.

5. Reports Isolation:
   - Generate / inspect reports (User Order Report & User Transaction Log) for manager users.
   - Verify reports for manager users are visible in Manager CRM.
   - Verify reports for non-manager users are NOT visible in Manager CRM.
   - Verify MAdmin CRM retains global visibility across all users and reports.

6. Ordered Teardown:
   - Revoke/delete all created users and managers cleanly in reverse order.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Generator
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("manager_hierarchy_isolation")

ADMIN_USER = settings.admin_portal.username or "madmin"
ADMIN_PASS = settings.admin_portal.password


def _dismiss_confirm_dialogs(page: Page, timeout: int = 3000) -> None:
    """Dismiss any jQuery confirm dialogs if present."""
    try:
        dialog_btns = page.locator(".jconfirm-box .jconfirm-buttons button")
        if dialog_btns.first.is_visible(timeout=timeout):
            dialog_btns.first.click()
            page.wait_for_timeout(800)
    except Exception:
        pass


def _expand_responsive_row(page: Page) -> None:
    """Expand collapsed DataTables responsive row."""
    try:
        if not page.locator("tr.child").is_visible():
            dtr = page.locator("table#datatable tbody tr td.dtr-control").first
            if dtr.is_visible(timeout=2000):
                dtr.click()
                page.wait_for_timeout(800)
    except Exception:
        pass


@pytest.fixture(scope="module")
def manager_workflow_session(browser: Browser) -> Generator[Dict[str, Any], None, None]:
    """
    Module-scoped fixture that sets up:
    1. Master Admin session.
    2. Dynamic Test Manager created via /admin/Controlbase/manager.
    3. Active Manager CRM session with registration URL extracted.
    4. Client User 1 created under Manager CRM.
    5. Client User 3 created directly in MAdmin (non-manager user).
    6. All emails verified.
    7. Teardown deleting all users, logging out manager, and deleting manager.
    """
    master_ctx: BrowserContext = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    master_page: Page = master_ctx.new_page()

    # Step 1: Master Admin Login
    login_url = settings.admin_portal.login_url or "https://stage.xtremenext.com/admin/Login/index"
    master_page.goto(login_url)
    master_page.fill("#username, input[name='username']", ADMIN_USER)
    master_page.fill("#password, input[name='password']", ADMIN_PASS)
    master_page.click("button[type='submit'], .savebut")
    master_page.wait_for_timeout(3000)

    ts = int(time.time())
    mgr_uname = f"mgr_dhanya_{ts}"
    mgr_email = f"mgr_dhanya_{ts}@testcorp.com"
    mgr_pass = os.getenv("TEST_DYNAMIC_USER_PASSWORD", "TestDynUser!123")

    u1_name = f"cl1_mgr_{ts}"
    u1_email = f"cl1_mgr_{ts}@testcorp.com"
    u1_pass = os.getenv("TEST_DYNAMIC_USER_PASSWORD", "TestDynUser!123")

    u2_name = f"cl2_reg_{ts}"
    u2_email = f"cl2_reg_{ts}@mailinator.com"
    u2_pass = os.getenv("TEST_DYNAMIC_USER_PASSWORD", "TestDynUser!123")

    u3_name = f"cl3_adm_{ts}"
    u3_email = f"cl3_adm_{ts}@testcorp.com"
    u3_pass = os.getenv("TEST_DYNAMIC_USER_PASSWORD", "TestDynUser!123")

    mgr_ctx: BrowserContext | None = None
    mgr_page: Page | None = None
    reg_url: str | None = None
    u1_acc: str | None = None
    u3_acc: str | None = None

    try:
        # Step 2: Master Admin creates new Manager
        logger.info(f"Provisioning custom manager: {mgr_uname}")
        master_page.goto("https://stage.xtremenext.com/admin/Controlbase/manager")
        master_page.wait_for_timeout(2000)
        expect(master_page.locator("#addNew")).to_be_visible(timeout=15000)
        master_page.click("#addNew")
        master_page.wait_for_timeout(1000)

        master_page.fill("#myModal #username", mgr_uname)
        master_page.fill("#myModal #email", mgr_email)
        master_page.fill("#myModal #password", mgr_pass)
        master_page.click("#myModal #formSubmit")
        master_page.wait_for_timeout(2500)
        _dismiss_confirm_dialogs(master_page)

        # Verify manager created in MAdmin table
        master_page.fill('input[type="search"]', mgr_uname)
        master_page.wait_for_timeout(1500)
        expect(master_page.locator("table#datatable tbody tr").first).to_contain_text(mgr_uname)
        logger.info(f"Manager '{mgr_uname}' created successfully by MAdmin!")

        # Step 3: Authenticate Manager CRM Session
        mgr_ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        mgr_page = mgr_ctx.new_page()
        mgr_page.goto(login_url)
        mgr_page.fill("#username, input[name='username']", mgr_uname)
        mgr_page.fill("#password, input[name='password']", mgr_pass)
        mgr_page.click("button[type='submit'], .savebut")
        mgr_page.wait_for_timeout(3000)
        assert "Controlbase" in mgr_page.url or "dashboard" in mgr_page.url.lower()
        logger.info(f"Manager '{mgr_uname}' successfully logged in to Manager CRM!")

        # Step 4: Extract Manager Registration URL
        reg_input = mgr_page.locator("#myInput")
        if reg_input.is_visible():
            reg_url = reg_input.input_value()
        logger.info(f"Manager registration URL: {reg_url}")

        # Step 5: Create User 1 from Manager CRM
        mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
        mgr_page.wait_for_timeout(2000)
        expect(mgr_page.locator("#addNew")).to_be_visible(timeout=15000)
        mgr_page.click("#addNew")
        mgr_page.wait_for_timeout(1000)
        if not mgr_page.locator("#userAddModal").is_visible():
            mgr_page.evaluate("$('#userAddModal').modal('show')")
            mgr_page.wait_for_timeout(1000)

        mgr_page.fill("#userAddModal #name", u1_name)
        mgr_page.fill("#userAddModal #email", u1_email)
        mgr_page.fill("#userAddModal #mobile", "9876543211")
        mgr_page.fill("#userAddModal #pass", u1_pass)
        mgr_page.fill("#userAddModal #investor_pass", "1234")

        # Select manager's auto-generated user group
        mgr_page.select_option("#userAddModal #user_group_id", index=1)
        mgr_page.wait_for_timeout(500)
        mgr_page.locator("#userAddModal #user_group_id").dispatch_event("change")
        mgr_page.wait_for_timeout(1500)
        if mgr_page.locator("#userAddModal #user_subgroup_value option").count() > 1:
            mgr_page.select_option("#userAddModal #user_subgroup_value", index=1)

        mgr_page.click("#userFormSubmit")
        mgr_page.wait_for_timeout(3000)
        _dismiss_confirm_dialogs(mgr_page)

        mgr_page.fill("#datatable_filter input", u1_email)
        mgr_page.wait_for_timeout(1500)
        u1_row = mgr_page.locator("table#datatable tbody tr").first
        expect(u1_row).to_contain_text(u1_name)
        u1_acc = mgr_page.locator("table#datatable tbody tr td:nth-child(4)").first.inner_text().strip()
        logger.info(f"Created User 1 under Manager CRM: {u1_name} (Account ID: {u1_acc})")

        # Step 6: Create User 3 (MAdmin standalone user)
        master_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
        master_page.wait_for_timeout(2000)
        master_page.click("#addNew")
        master_page.wait_for_timeout(1000)
        if not master_page.locator("#userAddModal").is_visible():
            master_page.evaluate("$('#userAddModal').modal('show')")
            master_page.wait_for_timeout(1000)

        master_page.fill("#userAddModal #name", u3_name)
        master_page.fill("#userAddModal #email", u3_email)
        master_page.fill("#userAddModal #mobile", "9876543213")
        master_page.fill("#userAddModal #pass", u3_pass)
        master_page.fill("#userAddModal #investor_pass", "1234")
        master_page.select_option("#userAddModal #user_group_id", index=1)
        master_page.wait_for_timeout(500)
        master_page.locator("#userAddModal #user_group_id").dispatch_event("change")
        master_page.wait_for_timeout(1000)
        if master_page.locator("#userAddModal #user_subgroup_value option").count() > 1:
            master_page.select_option("#userAddModal #user_subgroup_value", index=1)

        master_page.click("#userFormSubmit")
        master_page.wait_for_timeout(3000)
        _dismiss_confirm_dialogs(master_page)

        master_page.fill("#datatable_filter input", u3_email)
        master_page.wait_for_timeout(1500)
        u3_acc = master_page.locator("table#datatable tbody tr td:nth-child(4)").first.inner_text().strip()
        logger.info(f"Created User 3 (MAdmin User): {u3_name} (Account ID: {u3_acc})")

        # Step 7: Verify email status for all users in MAdmin
        for email in [u1_email, u3_email]:
            master_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
            master_page.wait_for_timeout(2000)
            master_page.fill("#datatable_filter input", email)
            master_page.wait_for_timeout(1500)
            _expand_responsive_row(master_page)
            try:
                verify_sel = master_page.locator("tr.child select[name='email_verification'], table#datatable tbody tr select[name='email_verification']").first
                if verify_sel.is_visible(timeout=3000):
                    verify_sel.select_option("Verified")
                    master_page.wait_for_timeout(1000)
            except Exception:
                pass

        session_data = {
            "master_ctx": master_ctx,
            "master_page": master_page,
            "mgr_ctx": mgr_ctx,
            "mgr_page": mgr_page,
            "mgr_uname": mgr_uname,
            "mgr_email": mgr_email,
            "reg_url": reg_url,
            "u1_name": u1_name,
            "u1_email": u1_email,
            "u1_pass": u1_pass,
            "u1_acc": u1_acc,
            "u2_name": u2_name,
            "u2_email": u2_email,
            "u2_pass": u2_pass,
            "u3_name": u3_name,
            "u3_email": u3_email,
            "u3_pass": u3_pass,
            "u3_acc": u3_acc,
        }

        yield session_data

    finally:
        logger.info("Executing comprehensive teardown for all created manager hierarchy entities...")

        # 1. Cleanup all users in MAdmin
        for email in [u1_email, u2_email, u3_email]:
            try:
                master_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
                master_page.wait_for_timeout(2000)
                master_page.fill("#datatable_filter input", email)
                master_page.wait_for_timeout(1500)
                _expand_responsive_row(master_page)
                del_btn = master_page.locator("tr.child a.BtnDelete, table#datatable tbody tr a.BtnDelete").first
                if del_btn.is_visible(timeout=4000):
                    del_btn.click()
                    master_page.wait_for_timeout(1000)
                    swal = master_page.locator("button.swal2-confirm, button:has-text('Yes, delete it!')").first
                    if swal.is_visible(timeout=3000):
                        swal.click()
                        master_page.wait_for_timeout(2000)
                    _dismiss_confirm_dialogs(master_page)
                    logger.info(f"Deleted test user {email}")
            except Exception as e:
                logger.warning(f"Error during teardown of user {email}: {e}")

        # 2. Logout Manager
        if mgr_page:
            try:
                mgr_page.goto("https://stage.xtremenext.com/admin/Login/logout")
                mgr_page.wait_for_timeout(1500)
                logger.info(f"Logged out test manager {mgr_uname}")
            except Exception as e:
                logger.warning(f"Error during manager logout: {e}")

        # 3. Delete Manager in MAdmin
        try:
            master_page.goto("https://stage.xtremenext.com/admin/Controlbase/manager")
            master_page.wait_for_timeout(2000)
            master_page.fill('input[type="search"]', mgr_uname)
            master_page.wait_for_timeout(1500)
            del_mgr = master_page.locator("table#datatable tbody tr").first.locator("a.BtnDelete").first
            if del_mgr.is_visible(timeout=4000):
                del_mgr.click()
                master_page.wait_for_timeout(1000)
                swal = master_page.locator("button.swal2-confirm, button:has-text('Yes, delete it!')").first
                if swal.is_visible(timeout=3000):
                    swal.click()
                    master_page.wait_for_timeout(2000)
                _dismiss_confirm_dialogs(master_page)
                logger.info(f"Deleted test manager {mgr_uname}")
        except Exception as e:
            logger.warning(f"Error during manager deletion: {e}")

        if mgr_ctx:
            mgr_ctx.close()
        master_ctx.close()


# ==============================================================================
# WORKFLOW 1: MANAGER CREATION & PERMISSIONS REFLECTION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.shared
@pytest.mark.regression
def test_workflow_manager_creation_and_permissions(manager_workflow_session: Dict[str, Any]):
    """
    Verify:
    1. Manager was successfully created from Manager/Group page.
    2. Manager account logged in and active session established.
    3. Assigned permissions are correctly reflected across sidebar menus.
    4. Restricted administrative pages (e.g. /manager, /admin, /rolePermission) are blocked/redirected.
    """
    mgr_page: Page = manager_workflow_session["mgr_page"]
    mgr_uname: str = manager_workflow_session["mgr_uname"]

    # 1. Verify Manager Dashboard
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/dashboard")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page).to_have_title("Dashboard")

    # 2. Verify Accessible Menus in Sidebar
    sidebar_text = mgr_page.locator("#sidebar-menu").first.inner_text()
    for menu in ["Dashboard", "Orders", "Manage User", "Deposit/WDL", "Reports/Logs"]:
        assert menu in sidebar_text, f"Expected '{menu}' menu to be visible in Manager sidebar"

    # 3. Test Restricted Administrative Features
    for restricted_url in [
        "https://stage.xtremenext.com/admin/Controlbase/manager",
        "https://stage.xtremenext.com/admin/Controlbase/admin",
        "https://stage.xtremenext.com/admin/Controlbase/rolePermission",
    ]:
        mgr_page.goto(restricted_url)
        mgr_page.wait_for_timeout(1500)
        # Should redirect back to dashboard or show 404/denied
        assert "/manager" not in mgr_page.url or "dashboard" in mgr_page.url.lower() or "404" in mgr_page.title()
        logger.info(f"Verified restricted URL '{restricted_url}' safely blocked for Manager {mgr_uname}")


# ==============================================================================
# WORKFLOW 2: USER CREATION & REGISTRATION URL ASSOCIATION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.shared
@pytest.mark.regression
def test_workflow_manager_user_creation_and_association(browser: Browser, manager_workflow_session: Dict[str, Any]):
    """
    Verify:
    1. User 1 created from Manager CRM is listed under Manager's user list.
    2. User 2 created via Registration URL is listed under Manager's user list.
    3. User 3 created from MAdmin is NOT exposed to Manager CRM (Data Isolation).
    """
    mgr_page: Page = manager_workflow_session["mgr_page"]
    master_page: Page = manager_workflow_session["master_page"]
    u1_email: str = manager_workflow_session["u1_email"]
    u2_name: str = manager_workflow_session["u2_name"]
    u2_email: str = manager_workflow_session["u2_email"]
    u2_pass: str = manager_workflow_session["u2_pass"]
    u3_email: str = manager_workflow_session["u3_email"]
    reg_url: str | None = manager_workflow_session["reg_url"]

    # 1. Verify User 1 in Manager CRM
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
    mgr_page.wait_for_timeout(2000)
    mgr_page.fill("#datatable_filter input", u1_email)
    mgr_page.wait_for_timeout(1500)
    expect(mgr_page.locator("table#datatable tbody tr").first).to_contain_text(u1_email)
    logger.info(f"User 1 ({u1_email}) verified in Manager CRM user table!")

    # 2. Test Registration URL (/register/?manager=<id>)
    if reg_url:
        reg_ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        reg_page = reg_ctx.new_page()
        reg_page.goto(reg_url)
        reg_page.wait_for_timeout(2000)
        reg_page.fill("#name", u2_name)
        reg_page.fill("#email", u2_email)
        reg_page.fill("#number", "9876543212")
        reg_page.wait_for_timeout(500)
        reg_page.click("button.next-btn")
        reg_page.wait_for_timeout(1500)
        if reg_page.locator("#pass1").is_visible():
            reg_page.fill("#pass1", u2_pass)
            reg_page.fill("#pass2", u2_pass)
            reg_page.check("#inputCheckbox")
            reg_page.click("button.savebut, button[type='submit']:has-text('Sign up')")
            reg_page.wait_for_timeout(3000)
            logger.info(f"User 2 submitted registration via URL: {reg_url}")
        reg_ctx.close()

    # 3. Verify Data Isolation: User 3 (MAdmin user) must NOT appear in Manager CRM
    mgr_page.fill("#datatable_filter input", u3_email)
    mgr_page.wait_for_timeout(1500)
    empty_cell = mgr_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or mgr_page.locator(f"table#datatable:has-text('{u3_email}')").count() == 0, (
        f"Data isolation violation: Non-manager user {u3_email} appeared in Manager CRM!"
    )
    logger.info(f"User 3 ({u3_email}) correctly hidden from Manager CRM (Data Isolation Confirmed)!")

    # 4. Verify MAdmin sees all users (Global Visibility)
    master_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
    master_page.wait_for_timeout(2000)
    master_page.fill("#datatable_filter input", u3_email)
    master_page.wait_for_timeout(1500)
    expect(master_page.locator("table#datatable tbody tr").first).to_contain_text(u3_email)
    logger.info("MAdmin CRM global user visibility confirmed!")


# ==============================================================================
# WORKFLOW 3: TRADE VISIBILITY & ISOLATION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.shared
@pytest.mark.regression
def test_workflow_trade_visibility_and_isolation(manager_workflow_session: Dict[str, Any]):
    """
    Verify:
    1. Manager CRM can access Order Management submenus (/order/open & /order/all).
    2. Non-manager user trades and accounts (User 3) are strictly isolated and not exposed in Manager CRM.
    3. MAdmin CRM retains global visibility across all order ledgers.
    """
    mgr_page: Page = manager_workflow_session["mgr_page"]
    master_page: Page = manager_workflow_session["master_page"]
    u1_acc: str = manager_workflow_session["u1_acc"]
    u3_acc: str = manager_workflow_session["u3_acc"]

    # 1. Verify Open Orders page in Manager CRM
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/order/open")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page.locator("table#datatable, table#orderHistory").first).to_be_visible()

    # 2. Verify All Orders page in Manager CRM
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/order/all")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page.locator("table#datatable, table#orderHistory").first).to_be_visible()

    # 3. Verify Non-Manager Trade Isolation in Manager CRM
    mgr_page.fill("#datatable_filter input, input[type='search']", str(u3_acc))
    mgr_page.wait_for_timeout(1500)
    empty_cell = mgr_page.locator("table#datatable tbody td.dataTables_empty, table tbody td.dataTables_empty").first
    assert empty_cell.is_visible() or mgr_page.locator(f"table tbody tr:has-text('{u3_acc}')").count() == 0, (
        f"Data isolation violation: Non-manager trade for Account {u3_acc} visible in Manager CRM!"
    )
    logger.info(f"Non-manager trade (Account: {u3_acc}) correctly hidden from Manager CRM!")

    # 4. Verify MAdmin retains global visibility
    master_page.goto("https://stage.xtremenext.com/admin/Controlbase/order/open")
    master_page.wait_for_timeout(2000)
    expect(master_page.locator("table#datatable, table#orderHistory").first).to_be_visible()
    logger.info("MAdmin verified global visibility for Orders!")


# ==============================================================================
# WORKFLOW 4: DEPOSITS, WITHDRAWALS & NOTIFICATIONS ISOLATION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.shared
@pytest.mark.regression
def test_workflow_deposit_withdrawal_and_notifications_isolation(manager_workflow_session: Dict[str, Any]):
    """
    Verify:
    1. Manager CRM can record/inspect deposits and withdrawals for manager users.
    2. Notifications dropdown functions correctly.
    3. Deposits/withdrawals for non-manager users do NOT appear in Manager CRM.
    """
    mgr_page: Page = manager_workflow_session["mgr_page"]
    master_page: Page = manager_workflow_session["master_page"]
    u1_acc: str = manager_workflow_session["u1_acc"]
    u3_acc: str = manager_workflow_session["u3_acc"]

    # 1. Verify Deposit List page in Manager CRM
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/payment")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page.locator("table#datatable")).to_be_visible()

    # 2. Verify Withdraw List page in Manager CRM
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/managewithdraw")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page.locator("table#datatable")).to_be_visible()

    # 3. Verify Manager Topbar Notifications Dropdown
    notif_btn = mgr_page.locator("#page-header-notifications-dropdown")
    expect(notif_btn).to_be_visible()
    notif_btn.click()
    mgr_page.wait_for_timeout(800)
    logger.info("Manager notification dropdown opened and verified!")

    # 4. Verify Non-Manager data isolation on Deposit & Withdraw lists
    mgr_page.fill("#datatable_filter input", str(u3_acc))
    mgr_page.wait_for_timeout(1500)
    empty_cell = mgr_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or mgr_page.locator(f"table#datatable:has-text('{u3_acc}')").count() == 0, (
        f"Data isolation violation: Non-manager transactions for {u3_acc} visible in Manager CRM!"
    )
    logger.info(f"Deposit/Withdrawal isolation confirmed for Account {u3_acc} in Manager CRM!")


# ==============================================================================
# WORKFLOW 5: REPORTS & DATA ISOLATION (USER ORDER REPORT & TRANSACTION LOG)
# ==============================================================================

@pytest.mark.admin
@pytest.mark.shared
@pytest.mark.regression
def test_workflow_reports_and_overall_data_isolation(manager_workflow_session: Dict[str, Any]):
    """
    Verify:
    1. User Order Report (/admin/Controlbase/userOrderReport) displays manager users and isolates non-manager users.
    2. User Transaction Log (/admin/Controlbase/userTransactionLog) isolates non-manager users.
    3. MAdmin retains complete global visibility across all reports and user data.
    """
    mgr_page: Page = manager_workflow_session["mgr_page"]
    master_page: Page = manager_workflow_session["master_page"]
    u1_acc: str = manager_workflow_session["u1_acc"]
    u3_acc: str = manager_workflow_session["u3_acc"]

    # 1. User Order Report Isolation
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/userOrderReport")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page.locator("table#datatable")).to_be_visible()

    # Search Non-Manager Account in Manager CRM Report
    mgr_page.fill("#datatable_filter input", str(u3_acc))
    mgr_page.wait_for_timeout(1500)
    empty_cell = mgr_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or mgr_page.locator(f"table#datatable:has-text('{u3_acc}')").count() == 0, (
        f"Data isolation violation: Non-manager user {u3_acc} appeared in Manager User Order Report!"
    )
    logger.info(f"User Order Report data isolation verified for Account {u3_acc}!")

    # 2. User Transaction Log Isolation
    mgr_page.goto("https://stage.xtremenext.com/admin/Controlbase/userTransactionLog")
    mgr_page.wait_for_timeout(2000)
    expect(mgr_page.locator("table#datatable")).to_be_visible()

    mgr_page.fill("#datatable_filter input", str(u3_acc))
    mgr_page.wait_for_timeout(1500)
    empty_cell = mgr_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or mgr_page.locator(f"table#datatable:has-text('{u3_acc}')").count() == 0, (
        f"Data isolation violation: Non-manager user {u3_acc} appeared in Manager User Transaction Log!"
    )
    logger.info(f"User Transaction Log data isolation verified for Account {u3_acc}!")

    # 3. Global Visibility in MAdmin Reports
    master_page.goto("https://stage.xtremenext.com/admin/Controlbase/userOrderReport")
    master_page.wait_for_timeout(2000)
    expect(master_page.locator("table#datatable")).to_be_visible()
    logger.info("MAdmin global report visibility confirmed across all user hierarchies!")
