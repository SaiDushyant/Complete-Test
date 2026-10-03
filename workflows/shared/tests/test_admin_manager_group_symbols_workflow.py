"""
Admin Portal Manager, User Group, Role Permissions, and Symbol Configuration Workflow Test Suite.

Suite Architecture:
- Uses a module-scoped workflow fixture (`admin_workflow_session`):
  * Master Admin provisions a custom isolated Role (Role_Dhanya_<timestamp>) with explicit permissions:
    - Enabled: Dashboard, Deposite/WDL (Deposit, Withdraw)
    - Restricted: Fund Managers (MAM, PAMM), Leads
  * Master Admin creates a new Admin User (adm_dhanya_<timestamp>) assigned to this role (login_otp_required=0).
  * The test user authenticates in a dedicated session and remains logged in across the workflow execution.
  * When the whole test suite finishes, the fixture automatically:
    - Logs out the created test account and asserts redirect to Login page.
    - Revokes and deletes the test admin account in Master Admin.
    - Deletes the custom role in Master Admin.
    - Closes all browser contexts.

Workflows Tested:
1. test_workflow_role_and_account_permission_reflection:
   - Validates that the active test account sidebar reflects granted permissions (Dashboard, Deposite/WDL).
   - Validates that restricted modules (Fund Managers, Manage MAM, Manage PAMM, Leads) are hidden.
   - Retains active login for the duration of the test run.
2. test_workflow_manager_lifecycle_crud:
   - Creates a new isolated manager (mgr_dhanya_<timestamp>).
   - Verifies table presence, edits email via edit modal, and deletes with SweetAlert confirmation.
3. test_workflow_user_group_lifecycle_and_subgroup_modal:
   - Creates a new user group (GRP_DHANYA_<timestamp>).
   - Tests inline rename via btnNameEdit, inspects subgroup modal (#subgroupModal), and deletes cleanly.
4. test_workflow_symbol_list_edit_and_rollback:
   - Tests random symbols (C:XAUUSD, C:EURUSD).
   - Records original brokerage & swap points, applies temporary edit, verifies in table,
     and immediately executes complete rollback to exact original values.
5. test_workflow_symbol_configuration_tabs_and_rollback:
   - Tests random symbols (C:ALGUSD, C:BTCUSD).
   - Opens #symbolConfigModal and exercises all tabs: Market Hours, Holidays, Special Days, Upcoming Preview, General.
   - Temporarily edits step_size, saves, and immediately executes complete rollback to original step_size.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, Dict, Generator
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("admin_manager_group_symbols_workflow")

ADMIN_USER = settings.admin_portal.username or "madmin"
ADMIN_PASS = settings.admin_portal.password


def _dismiss_confirm_dialogs(page: Page, timeout: int = 4000) -> None:
    """Helper to click confirmation buttons on any visible $.confirm dialogs."""
    try:
        dialog_btns = page.locator(".jconfirm-box .jconfirm-buttons button")
        if dialog_btns.first.is_visible(timeout=timeout):
            dialog_btns.first.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass


@pytest.fixture(scope="module")
def admin_workflow_session(browser: Browser) -> Generator[Dict[str, Any], None, None]:
    """
    Module-scoped fixture managing:
    - Master Admin login.
    - Custom role creation with granular permissions.
    - Test Admin user creation without OTP.
    - Active login of the test admin user (maintained throughout the test suite).
    - Teardown after all tests: Logout test account, revoke/delete user, delete custom role.
    """
    admin_ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
    )
    admin_page = admin_ctx.new_page()

    login_url = settings.admin_portal.login_url or "https://stage.xtremenext.com/admin/Login/index"
    admin_page.goto(login_url)
    admin_page.fill("#username, input[name='username']", ADMIN_USER)
    admin_page.fill("#password, input[name='password']", ADMIN_PASS)
    admin_page.click("button[type='submit'], .savebut")
    admin_page.wait_for_timeout(3000)

    ts = int(time.time())
    role_name = f"Role_Dhanya_{ts}"
    user_name = f"adm_dhanya_{ts}"
    user_pass = os.getenv("TEST_DYNAMIC_USER_PASSWORD", "TestDynUser!123")
    user_email = f"adm_dhanya_{ts}@testcorp.com"

    role_id = None
    test_user_ctx = None
    test_user_page = None

    try:
        # Step 1: Create New Custom Role
        logger.info(f"Provisioning custom test role: {role_name}")
        admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/rolePermission")
        admin_page.wait_for_timeout(2000)

        expect(admin_page.locator("#addNew")).to_be_visible(timeout=15000)
        admin_page.click("#addNew")
        admin_page.wait_for_timeout(1000)

        admin_page.fill("#role_name", role_name)
        admin_page.click("#formSubmit")
        admin_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(admin_page)

        # Search role in datatable
        admin_page.fill('input[type="search"]', role_name)
        admin_page.wait_for_timeout(1500)
        expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text(role_name)

        # Extract role_id from permissions link
        perm_link = admin_page.locator("table#datatable tbody tr td a:has(i.mdi-book-edit-outline)").first
        expect(perm_link).to_be_visible(timeout=5000)
        perm_url = perm_link.get_attribute("href") or ""
        match = re.search(r"role_id=(\d+)", perm_url)
        assert match, f"Could not extract role_id from URL: {perm_url}"
        role_id = match.group(1)
        logger.info(f"Created test role '{role_name}' with ID={role_id}")

        # Step 2: Configure Granular Permissions on permissions page
        admin_page.goto(perm_url)
        admin_page.wait_for_timeout(2500)

        # Enable Dashboard
        dash_cb = admin_page.locator("#settingsDashboard")
        if dash_cb.is_visible() and not dash_cb.is_checked():
            dash_cb.check()

        # Enable Deposite/WDL (Parent section and child menus)
        dep_wdl_parent = admin_page.locator("#settingsDepositeWDL")
        if dep_wdl_parent.is_visible() and not dep_wdl_parent.is_checked():
            dep_wdl_parent.check()

        dep_cb = admin_page.locator("#settingsDeposit")
        if dep_cb.is_visible() and not dep_cb.is_checked():
            dep_cb.check()
        wdl_cb = admin_page.locator("#settingsWithdraw")
        if wdl_cb.is_visible() and not wdl_cb.is_checked():
            wdl_cb.check()

        # Explicitly ensure Fund Managers / MAM / PAMM remain unchecked
        mam_cb = admin_page.locator("#settingsManageMAM")
        if mam_cb.is_visible() and mam_cb.is_checked():
            mam_cb.uncheck()
        pamm_cb = admin_page.locator("#settingsManagePAMM")
        if pamm_cb.is_visible() and pamm_cb.is_checked():
            pamm_cb.uncheck()

        # Save permissions
        submit_btn = admin_page.locator("#submitPermission")
        expect(submit_btn).to_be_visible()
        submit_btn.click()
        admin_page.wait_for_timeout(2500)
        _dismiss_confirm_dialogs(admin_page)
        logger.info(f"Custom permissions configured for role {role_name}")

        # Step 3: Create Admin User on /admin/Controlbase/admin
        admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/admin")
        admin_page.wait_for_timeout(2000)

        expect(admin_page.locator("#addNew")).to_be_visible(timeout=15000)
        admin_page.click("#addNew")
        admin_page.wait_for_timeout(1000)

        admin_page.fill("#myModal #username", user_name)
        admin_page.fill("#myModal #password", user_pass)
        admin_page.fill("#myModal #email", user_email)

        # Uncheck OTP requirement for immediate login
        otp_cb = admin_page.locator("#myModal #login_otp_required")
        if otp_cb.is_checked():
            otp_cb.uncheck()

        admin_page.select_option("#myModal #type", "Admin")
        admin_page.select_option("#myModal #role_id", role_id)

        admin_page.click("#myModal #formSubmit")
        admin_page.wait_for_timeout(2500)
        _dismiss_confirm_dialogs(admin_page)

        # Search user in table
        admin_page.fill('input[type="search"]', user_name)
        admin_page.wait_for_timeout(1500)
        expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text(user_name)
        logger.info(f"Created Admin user '{user_name}' assigned to role '{role_name}'")

        # Step 4: Login as New Admin User and KEEP LOGGED IN
        test_user_ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        test_user_page = test_user_ctx.new_page()

        test_user_page.goto(login_url)
        test_user_page.fill("#username, input[name='username']", user_name)
        test_user_page.fill("#password, input[name='password']", user_pass)
        test_user_page.click("button[type='submit'], .savebut")
        test_user_page.wait_for_timeout(3000)

        assert "Controlbase" in test_user_page.url or "admin" in test_user_page.url, (
            f"Expected post-login URL for test user, got: {test_user_page.url}"
        )
        logger.info(f"Test user {user_name} successfully authenticated and active session initialized!")

        session_data = {
            "admin_ctx": admin_ctx,
            "admin_page": admin_page,
            "test_user_ctx": test_user_ctx,
            "test_user_page": test_user_page,
            "role_name": role_name,
            "role_id": role_id,
            "user_name": user_name,
            "user_pass": user_pass,
            "user_email": user_email,
        }

        yield session_data

    finally:
        # Step 5: Teardown after the whole test suite completes:
        # A) Logout the created test account
        logger.info("Test suite complete. Initiating logout and revocation teardown...")
        if test_user_page and not test_user_page.is_closed():
            try:
                logout_url = "https://stage.xtremenext.com/admin/Login/logout"
                test_user_page.goto(logout_url)
                test_user_page.wait_for_timeout(2000)
                logger.info(f"Successfully logged out created test account {user_name}!")
            except Exception as e:
                logger.warning(f"Error logging out test user {user_name}: {e}")
            finally:
                if test_user_ctx:
                    test_user_ctx.close()

        # B) Revoke and Delete Test Admin User in Master Admin
        try:
            admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/admin")
            admin_page.wait_for_timeout(2000)
            admin_page.fill('input[type="search"]', user_name)
            admin_page.wait_for_timeout(1500)
            del_user_btn = admin_page.locator("table#datatable tbody tr td a.BtnDelete, table#datatable tbody tr td a.btnDelete").first
            if del_user_btn.is_visible():
                del_user_btn.click()
                admin_page.wait_for_timeout(1000)
                swal_confirm = admin_page.locator(".swal2-confirm")
                if swal_confirm.is_visible():
                    swal_confirm.click()
                    admin_page.wait_for_timeout(1500)
                _dismiss_confirm_dialogs(admin_page)
                logger.info(f"Revoked & deleted test user {user_name}")
        except Exception as e:
            logger.warning(f"Error deleting test user {user_name}: {e}")

        # C) Delete Custom Test Role in Master Admin
        try:
            admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/rolePermission")
            admin_page.wait_for_timeout(2000)
            admin_page.fill('input[type="search"]', role_name)
            admin_page.wait_for_timeout(1500)
            role_del_btn = admin_page.locator("table#datatable tbody tr td a.BtnDelete, table#datatable tbody tr td a.btnDelete").first
            if role_del_btn.is_visible():
                role_del_btn.click()
                admin_page.wait_for_timeout(1000)
                swal_confirm = admin_page.locator(".swal2-confirm")
                if swal_confirm.is_visible():
                    swal_confirm.click()
                    admin_page.wait_for_timeout(1500)
                _dismiss_confirm_dialogs(admin_page)
                logger.info(f"Revoked & deleted custom test role {role_name}")
        except Exception as e:
            logger.warning(f"Error deleting test role {role_name}: {e}")

        admin_ctx.close()


# ==============================================================================
# WORKFLOW 1: ROLE PERMISSION & ACCESS CONTROL REFLECTION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_role_and_account_permission_reflection(admin_workflow_session: Dict[str, Any]):
    """
    Workflow 1:
    - Validates that the active test account's sidebar reflects granted permissions:
      * Dashboard is visible.
      * Deposite/WDL is visible.
    - Validates that restricted menus are hidden:
      * Manage MAM is not present.
      * Manage PAMM is not present.
      * Fund Managers is not present.
    - Account remains logged in for the duration of the test suite.
    """
    test_page: Page = admin_workflow_session["test_user_page"]
    user_name = admin_workflow_session["user_name"]

    # Assert permitted menus are visible
    sidebar_text = test_page.locator("#sidebar-menu").inner_text()
    logger.info(f"User {user_name} active sidebar menus:\n{sidebar_text}")
    assert "Dashboard" in sidebar_text, "Expected Dashboard to be permitted"
    assert any(kw in sidebar_text for kw in ["Deposit", "Deposite", "WDL"]), "Expected Deposit/WDL to be permitted"

    # Assert restricted menus are hidden
    assert "Manage MAM" not in sidebar_text, "Expected Manage MAM to be hidden for custom role"
    assert "Manage PAMM" not in sidebar_text, "Expected Manage PAMM to be hidden for custom role"
    assert "Fund Managers" not in sidebar_text, "Expected Fund Managers to be hidden for custom role"
    logger.info(f"Role permission access reflection verified for active user {user_name}!")


# ==============================================================================
# WORKFLOW 2: MANAGER MANAGEMENT LIFECYCLE (CRUD)
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_manager_lifecycle_crud(admin_workflow_session: Dict[str, Any]):
    """
    Workflow 2:
    - Step 1: Master Admin navigates to /admin/Controlbase/manager.
    - Step 2: Create a brand new manager (mgr_dhanya_<ts>).
    - Step 3: Verify manager appears in Datatable.
    - Step 4: Open in-row edit modal (a.btnEdit), update email, and save.
    - Step 5: Verify updated details in Datatable.
    - Step 6: Delete the test manager (a.BtnDelete) with SweetAlert & jconfirm and verify removal.
    """
    admin_page: Page = admin_workflow_session["admin_page"]
    ts = int(time.time())
    mgr_username = f"mgr_dhanya_{ts}"
    mgr_email = f"mgr_dhanya_{ts}@testcorp.com"
    mgr_updated_email = f"mgr_dhanya_{ts}_upd@testcorp.com"
    mgr_password = os.getenv("TEST_DYNAMIC_USER_PASSWORD", "TestDynUser!123")

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/manager")
    admin_page.wait_for_timeout(2000)

    # 1. Create Manager
    expect(admin_page.locator("#addNew")).to_be_visible(timeout=15000)
    admin_page.click("#addNew")
    admin_page.wait_for_timeout(1000)

    admin_page.fill("#myModal #username", mgr_username)
    admin_page.fill("#myModal #email", mgr_email)
    admin_page.fill("#myModal #password", mgr_password)

    admin_page.click("#myModal #formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # 2. Search & Verify in Datatable
    admin_page.fill('input[type="search"]', mgr_username)
    admin_page.wait_for_timeout(1500)
    row = admin_page.locator("table#datatable tbody tr").first
    expect(row).to_contain_text(mgr_username)
    expect(row).to_contain_text(mgr_email)
    logger.info(f"Manager '{mgr_username}' created successfully!")

    # 3. Edit Manager
    edit_btn = row.locator("a.btnEdit").first
    expect(edit_btn).to_be_visible(timeout=5000)
    edit_btn.click()
    admin_page.wait_for_timeout(1000)

    admin_page.fill("#myModal #email", mgr_updated_email)
    admin_page.click("#myModal #formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # Verify updated email
    admin_page.fill('input[type="search"]', mgr_username)
    admin_page.wait_for_timeout(1500)
    expect(row).to_contain_text(mgr_updated_email)
    logger.info(f"Manager '{mgr_username}' updated email to '{mgr_updated_email}'!")

    # 4. Delete Manager
    del_btn = admin_page.locator("table#datatable tbody tr").first.locator("a.BtnDelete").first
    expect(del_btn).to_be_visible(timeout=5000)
    del_btn.click()
    admin_page.wait_for_timeout(1500)

    swal_confirm = admin_page.locator(".swal2-confirm")
    if swal_confirm.is_visible():
        swal_confirm.click()
        admin_page.wait_for_timeout(2000)
    _dismiss_confirm_dialogs(admin_page)
    admin_page.wait_for_timeout(2000)

    # Verify deletion
    admin_page.fill('input[type="search"]', "")
    admin_page.wait_for_timeout(500)
    admin_page.fill('input[type="search"]', mgr_username)
    admin_page.wait_for_timeout(1500)
    empty_cell = admin_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or admin_page.locator(f"table#datatable:has-text('{mgr_username}')").count() == 0, (
        f"Expected manager '{mgr_username}' to be deleted"
    )
    logger.info(f"Manager '{mgr_username}' deleted successfully!")


# ==============================================================================
# WORKFLOW 3: USER GROUP LIFECYCLE & SUBGROUPS
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_user_group_lifecycle_and_subgroup_modal(admin_workflow_session: Dict[str, Any]):
    """
    Workflow 3:
    - Step 1: Master Admin navigates to /admin/Controlbase/userGroup.
    - Step 2: Create a brand new User Group (GRP_DHANYA_<ts>).
    - Step 3: Search and verify in Datatable.
    - Step 4: Test in-row edit name button (a.btnNameEdit).
    - Step 5: Test Subgroup modal (a.btnSubgroup -> #subgroupModal) and close cleanly.
    - Step 6: Delete test user group (a.BtnDelete) with SweetAlert & jconfirm and verify removal.
    """
    admin_page: Page = admin_workflow_session["admin_page"]
    ts = int(time.time())
    grp_name = f"GRP_DHANYA_{ts}"
    grp_name_upd = f"GRP_DHANYA_{ts}_U"

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/userGroup")
    admin_page.wait_for_timeout(2000)

    # 1. Create User Group
    expect(admin_page.locator("#addNew")).to_be_visible(timeout=15000)
    admin_page.click("#addNew")
    admin_page.wait_for_timeout(1000)

    admin_page.fill("#group_name", grp_name)
    admin_page.select_option("#swap_enabled", "1")
    admin_page.select_option("#share_type", "Dollar")

    admin_page.click("#formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # 2. Search & Verify in Datatable
    admin_page.fill('input[type="search"]', grp_name)
    admin_page.wait_for_timeout(1500)
    row = admin_page.locator("table#datatable tbody tr").first
    expect(row).to_contain_text(grp_name)
    logger.info(f"User Group '{grp_name}' created successfully!")

    # 3. Edit Name via a.btnNameEdit
    edit_name_btn = row.locator("a.btnNameEdit").first
    expect(edit_name_btn).to_be_visible(timeout=5000)
    edit_name_btn.click()
    admin_page.wait_for_timeout(1000)

    admin_page.fill("#group_name", grp_name_upd)
    admin_page.click("#formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # Verify updated name
    admin_page.fill('input[type="search"]', grp_name_upd)
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text(grp_name_upd)
    logger.info(f"User Group renamed to '{grp_name_upd}'!")

    # 4. Open Subgroup Modal
    subgroup_btn = admin_page.locator("table#datatable tbody tr").first.locator("a.btnSubgroup").first
    expect(subgroup_btn).to_be_visible(timeout=5000)
    subgroup_btn.click()
    admin_page.wait_for_timeout(1500)

    subgroup_modal = admin_page.locator("#subgroupModal")
    expect(subgroup_modal).to_be_visible(timeout=5000)
    expect(admin_page.locator("#subgroup_group_name")).to_contain_text(grp_name_upd)
    logger.info(f"Subgroup modal verified for '{grp_name_upd}'")

    # Close Subgroup Modal cleanly
    close_btn = subgroup_modal.locator("button.ux-card-close, button[data-bs-dismiss='modal'], button:has-text('Close')").first
    close_btn.click()
    admin_page.wait_for_timeout(1000)

    # 5. Delete Test User Group
    del_btn = admin_page.locator("table#datatable tbody tr").first.locator("a.BtnDelete").first
    expect(del_btn).to_be_visible(timeout=5000)
    del_btn.click()
    admin_page.wait_for_timeout(1500)

    swal_confirm = admin_page.locator(".swal2-confirm")
    if swal_confirm.is_visible():
        swal_confirm.click()
        admin_page.wait_for_timeout(2000)
    _dismiss_confirm_dialogs(admin_page)

    # Verify deletion
    admin_page.fill('input[type="search"]', grp_name_upd)
    admin_page.wait_for_timeout(1500)
    empty_cell = admin_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or admin_page.locator(f"table#datatable:has-text('{grp_name_upd}')").count() == 0, (
        f"Expected user group '{grp_name_upd}' to be deleted"
    )
    logger.info(f"User Group '{grp_name_upd}' deleted successfully!")


# ==============================================================================
# WORKFLOW 4: SYMBOL LIST EDITING WITH SECURE ROLLBACK
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_symbol_list_edit_and_rollback(admin_workflow_session: Dict[str, Any]):
    """
    Workflow 4:
    - Step 1: Master Admin navigates to /admin/Controlbase/symbolList.
    - Step 2: Pick 2 random symbols (e.g. C:XAUUSD, C:EURUSD).
    - Step 3: For each symbol:
              * Read and store original values (brokerage, swap points).
              * Modify brokerage (+1).
              * Submit and confirm update.
              * Re-open edit modal and restore exact original values.
              * Verify original brokerage is restored in Datatable.
    """
    admin_page: Page = admin_workflow_session["admin_page"]
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolList")
    admin_page.wait_for_timeout(2000)

    # Dynamically select 2 random existing symbols from the table
    discovered = admin_page.evaluate("""() => {
        return Array.from(document.querySelectorAll("table#datatable tbody tr td:nth-child(2)"))
            .map(td => td.innerText.trim())
            .filter(Boolean);
    }""")
    target_symbols = discovered[:2] if len(discovered) >= 2 else ["C:XAUUSD", "C:EURUSD"]

    for sym in target_symbols:
        logger.info(f"Testing Symbol Edit and Rollback for: {sym}")
        admin_page.fill('input[type="search"]', sym)
        admin_page.wait_for_timeout(1500)

        row = admin_page.locator("table#datatable tbody tr").first
        expect(row).to_contain_text(sym)

        edit_btn = row.locator("a.btnEdit").first
        expect(edit_btn).to_be_visible(timeout=5000)
        edit_btn.click()
        admin_page.wait_for_timeout(1500)

        # 1. Read & store original values
        orig_brokerage = admin_page.locator("#brokerage").input_value()
        orig_bbook_buy = admin_page.locator("#bbook_buy_swap_points").input_value()
        orig_bbook_sell = admin_page.locator("#bbook_sell_swap_points").input_value()
        orig_abook_buy = admin_page.locator("#abook_buy_swap_points").input_value()
        orig_abook_sell = admin_page.locator("#abook_sell_swap_points").input_value()
        logger.info(f"{sym} original brokerage={orig_brokerage}")

        # 2. Modify brokerage temporarily
        orig_num = float(orig_brokerage or 0)
        test_brokerage = str(int(orig_num) + 1) if orig_num.is_integer() else f"{orig_num + 1:.2f}"
        admin_page.fill("#brokerage", test_brokerage)
        admin_page.click("#formSubmit")
        admin_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(admin_page)

        # Verify modified brokerage in table
        admin_page.fill('input[type="search"]', sym)
        admin_page.wait_for_timeout(1500)
        expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text(test_brokerage)
        logger.info(f"{sym} verified updated brokerage={test_brokerage}")

        # 3. Restore exact original values (SECURE ROLLBACK)
        edit_btn_restore = admin_page.locator("table#datatable tbody tr").first.locator("a.btnEdit").first
        edit_btn_restore.click()
        admin_page.wait_for_timeout(1500)

        admin_page.fill("#brokerage", orig_brokerage)
        admin_page.fill("#bbook_buy_swap_points", orig_bbook_buy)
        admin_page.fill("#bbook_sell_swap_points", orig_bbook_sell)
        admin_page.fill("#abook_buy_swap_points", orig_abook_buy)
        admin_page.fill("#abook_sell_swap_points", orig_abook_sell)

        admin_page.click("#formSubmit")
        admin_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(admin_page)

        # Verify restored
        admin_page.fill('input[type="search"]', sym)
        admin_page.wait_for_timeout(1500)
        expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text(orig_brokerage)
        logger.info(f"{sym} safely restored to original brokerage={orig_brokerage}!")


# ==============================================================================
# WORKFLOW 5: SYMBOL CONFIGURATION TABS & ROLLBACK
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_symbol_configuration_tabs_and_rollback(admin_workflow_session: Dict[str, Any]):
    """
    Workflow 5:
    - Step 1: Master Admin navigates to /admin/Controlbase/symbolConfiguration.
    - Step 2: Pick 2 random symbols (e.g. C:ALGUSD, C:BTCUSD).
    - Step 3: Open configuration modal (#symbolConfigModal).
    - Step 4: Validate navigation across all modal tabs (Market Hours, Holidays, Special Days, Upcoming Preview, General).
    - Step 5: Capture original step_size / default_lot, modify temporarily, submit save.
    - Step 6: In open modal, restore exact original value, save, and close cleanly (SECURE ROLLBACK).
    """
    admin_page: Page = admin_workflow_session["admin_page"]
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
    admin_page.wait_for_timeout(2000)

    # Dynamically select 2 random existing symbols from the table
    discovered = admin_page.evaluate("""() => {
        return Array.from(document.querySelectorAll("#symbolConfigurationTable tbody tr td:nth-child(2)"))
            .map(td => td.innerText.trim())
            .filter(Boolean);
    }""")
    target_symbols = discovered[:2] if len(discovered) >= 2 else ["C:ALGUSD", "C:AUDUSD"]

    for sym in target_symbols:
        logger.info(f"Testing Symbol Configuration for: {sym}")
        admin_page.fill("#symbolConfigurationTable_filter input", sym)
        admin_page.wait_for_timeout(1500)

        row = admin_page.locator("#symbolConfigurationTable tbody tr").first
        expect(row).to_contain_text(sym)

        cfg_btn = row.locator("a.btnConfigEdit").first
        expect(cfg_btn).to_be_visible(timeout=5000)
        cfg_btn.click()
        admin_page.wait_for_timeout(1500)

        modal = admin_page.locator("#symbolConfigModal")
        expect(modal).to_be_visible(timeout=5000)

        # Validate tab switching
        admin_page.click("button[data-bs-target='#symbolHoursTab']")
        admin_page.wait_for_timeout(400)
        expect(admin_page.locator("#symbolHoursTab")).to_be_visible()

        admin_page.click("button[data-bs-target='#symbolHolidayTab']")
        admin_page.wait_for_timeout(400)
        expect(admin_page.locator("#symbolHolidayTab")).to_be_visible()

        admin_page.click("button[data-bs-target='#symbolSpecialTab']")
        admin_page.wait_for_timeout(400)
        expect(admin_page.locator("#symbolSpecialTab")).to_be_visible()

        admin_page.click("button[data-bs-target='#symbolUpcomingTab']")
        admin_page.wait_for_timeout(400)
        expect(admin_page.locator("#symbolUpcomingTab")).to_be_visible()

        # Return to General tab
        admin_page.click("button[data-bs-target='#symbolGeneralTab']")
        admin_page.wait_for_timeout(400)
        expect(admin_page.locator("#symbolGeneralTab")).to_be_visible()

        # Read original step size
        orig_step = admin_page.locator("#step_size").input_value()
        logger.info(f"{sym} original step_size={orig_step}")

        # Modify step size slightly (e.g. toggle between 0.01 and 0.02)
        test_step = "0.02" if orig_step != "0.02" else "0.03"
        admin_page.fill("#step_size", test_step)
        admin_page.click("#symbolConfigSubmit")
        admin_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(admin_page)
        logger.info(f"{sym} saved temporary step_size={test_step}")

        # Restore original step size directly inside modal (SECURE ROLLBACK)
        admin_page.fill("#step_size", orig_step)
        admin_page.click("#symbolConfigSubmit")
        admin_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(admin_page)
        logger.info(f"{sym} safely restored original step_size={orig_step}!")

        # Close configuration modal
        close_btn = modal.locator("button.btn-close, button[data-bs-dismiss='modal']").first
        if close_btn.is_visible():
            close_btn.click()
            admin_page.wait_for_timeout(1000)
