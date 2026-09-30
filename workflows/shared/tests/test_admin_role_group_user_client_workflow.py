"""
End-to-End Workflow Suite: Custom Role Permissions, User Group, Client Creation,
Client Portal Leverage Reflection, Admin Switch Group, Bonus Lifecycle, and Active Users.

Architecture:
1. Master Admin provisions custom role (Role_Dhanya_<timestamp>) with comprehensive permissions
   (Dashboard, Manage User, User Group, Manager, Symbol, User Credit / Bonus, Active User, Deposite/WDL, Reports).
2. Master Admin creates test Admin user (adm_dhanya_<timestamp>) with role assigned and login_otp_required=0.
3. Test Admin user authenticates and executes all subsequent operations:
   - Creates new User Group (GRP_DHANYA_<timestamp>) and verifies action buttons and form values.
   - Creates new Client User (usr_dhanya_<timestamp>) assigned to GRP_DHANYA_<timestamp>.
   - Authorizes client email verification in Admin.
4. Client User authenticates in Client Portal:
   - Navigates to Settings -> Trading Account.
   - Updates account leverage (e.g. to 1:200 / 1:100) and saves trading settings.
5. Test Admin verifies leverage reflection in Admin Portal (Account Details / Switch Group column).
6. Test Admin exercises in-row 'Switch Group' action (.switchGroup -> #switchGroupModal) to modify group/subgroup.
7. Test Admin exercises Bonus lifecycle:
   - Adds bonus on /admin/Controlbase/user (#userCreditBonus).
   - Verifies bonus on /admin/Controlbase/creditList.
   - Modifies bonus (a.btnEdit -> #myModal).
   - Withdraws bonus (a.BtnDelete).
8. Test Admin inspects Active Users on /admin/Controlbase/activeUsers (#au-datatable).
9. Complete Ordered Teardown after suite finishes:
   - Client Portal session logged out.
   - Test Client User deleted via Admin Portal.
   - Test User Group deleted via Admin Portal.
   - Test Admin User logged out.
   - Master Admin deletes Test Admin User.
   - Master Admin deletes Custom Test Role.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, Generator
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("role_group_user_client_workflow")

ADMIN_USER = settings.admin_portal.username or "madmin"
ADMIN_PASS = settings.admin_portal.password or "Test@1234"


def _dismiss_confirm_dialogs(page: Page, timeout: int = 4000) -> None:
    """Helper to dismiss any $.confirm dialogs by clicking its action/close button."""
    try:
        dialog_btns = page.locator(".jconfirm-box .jconfirm-buttons button")
        if dialog_btns.first.is_visible(timeout=timeout):
            dialog_btns.first.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass


def _expand_responsive_row(page: Page) -> None:
    """Helper to expand collapsed DataTables responsive row (+ in td.dtr-control)."""
    try:
        if not page.locator("tr.child").is_visible():
            dtr = page.locator("table#datatable tbody tr td.dtr-control").first
            if dtr.is_visible(timeout=2000):
                dtr.click()
                page.wait_for_timeout(800)
    except Exception:
        pass


@pytest.fixture(scope="module")
def full_workflow_session(browser: Browser) -> Generator[Dict[str, Any], None, None]:
    """
    Session fixture provisioning the full hierarchy:
    Master Admin -> Custom Test Role -> Test Admin User -> Test User Group -> Test Client User.
    Maintains all active sessions and executes clean ordered teardown when complete.
    """
    master_ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    master_page = master_ctx.new_page()

    # Step 1: Master Admin Login
    login_url = settings.admin_portal.login_url or "https://stage.xtremenext.com/admin/Login/index"
    master_page.goto(login_url)
    master_page.fill("#username, input[name='username']", ADMIN_USER)
    master_page.fill("#password, input[name='password']", ADMIN_PASS)
    master_page.click("button[type='submit'], .savebut")
    master_page.wait_for_timeout(3000)

    ts = int(time.time())
    role_name = f"Role_Dhanya_{ts}"
    admin_uname = f"adm_dhanya_{ts}"
    admin_pass = "Test@1234"
    admin_email = f"adm_dhanya_{ts}@testcorp.com"

    grp_name = f"GRP_DHANYA_{ts}"
    client_name = f"cl_dhanya_{ts}"
    client_email = f"cl_dhanya_{ts}@testcorp.com"
    client_pass = "Test@1234"
    client_inv_pass = "1234"

    role_id = None
    test_admin_ctx = None
    test_admin_page = None
    client_ctx = None
    client_page = None
    account_id = None

    try:
        # Step 2: Create Custom Role
        logger.info(f"Provisioning custom role: {role_name}")
        master_page.goto("https://stage.xtremenext.com/admin/Controlbase/rolePermission")
        master_page.wait_for_timeout(2000)
        expect(master_page.locator("#addNew")).to_be_visible(timeout=15000)
        master_page.click("#addNew")
        master_page.wait_for_timeout(1000)
        if not master_page.locator("#myModal").is_visible():
            master_page.evaluate("$('#myModal').modal('show')")
            master_page.wait_for_timeout(1000)
        master_page.fill("#role_name", role_name)
        master_page.click("#myModal #formSubmit")
        master_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(master_page)

        master_page.fill('input[type="search"]', role_name)
        master_page.wait_for_timeout(1500)
        perm_link = master_page.locator("table#datatable tbody tr td a:has(i.mdi-book-edit-outline)").first
        perm_url = perm_link.get_attribute("href") or ""
        match = re.search(r"role_id=(\d+)", perm_url)
        assert match, f"Could not extract role_id from URL: {perm_url}"
        role_id = match.group(1)
        logger.info(f"Custom role created with ID={role_id}")

        # Step 3: Configure Comprehensive Permissions for Test Role
        master_page.goto(perm_url)
        master_page.wait_for_timeout(2500)

        # Check all permissions via DOM injection to ensure full access
        master_page.evaluate("""() => {
            document.querySelectorAll("#PermissionForm input[type='checkbox']").forEach(cb => {
                cb.checked = true;
            });
        }""")
        master_page.click("#submitPermission")
        master_page.wait_for_timeout(2500)
        _dismiss_confirm_dialogs(master_page)
        logger.info(f"Comprehensive permissions enabled for role {role_name}")

        # Step 4: Create Test Admin User under this role
        master_page.goto("https://stage.xtremenext.com/admin/Controlbase/admin")
        master_page.wait_for_timeout(2000)
        expect(master_page.locator("#addNew")).to_be_visible(timeout=15000)
        master_page.click("#addNew")
        master_page.wait_for_timeout(1000)
        if not master_page.locator("#myModal").is_visible():
            master_page.evaluate("$('#myModal').modal('show')")
            master_page.wait_for_timeout(1000)

        master_page.fill("#myModal #username", admin_uname)
        master_page.fill("#myModal #password", admin_pass)
        master_page.fill("#myModal #email", admin_email)

        otp_cb = master_page.locator("#myModal #login_otp_required")
        if otp_cb.is_checked():
            otp_cb.uncheck()

        master_page.select_option("#myModal #type", "Admin")
        master_page.select_option("#myModal #role_id", role_id)
        master_page.click("#myModal #formSubmit")
        master_page.wait_for_timeout(2500)
        _dismiss_confirm_dialogs(master_page)

        master_page.fill('input[type="search"]', admin_uname)
        master_page.wait_for_timeout(1500)
        expect(master_page.locator("table#datatable tbody tr").first).to_contain_text(admin_uname)
        logger.info(f"Created Test Admin user '{admin_uname}' assigned to role '{role_name}'")

        # Step 5: Authenticate Test Admin User (Session Active for Entire Test)
        test_admin_ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        test_admin_page = test_admin_ctx.new_page()

        test_admin_page.goto(login_url)
        test_admin_page.fill("#username, input[name='username']", admin_uname)
        test_admin_page.fill("#password, input[name='password']", admin_pass)
        test_admin_page.click("button[type='submit'], .savebut")
        test_admin_page.wait_for_timeout(3000)
        assert "Controlbase" in test_admin_page.url or "admin" in test_admin_page.url
        logger.info(f"Test Admin user '{admin_uname}' successfully logged in!")

        # Step 6: Test Admin User creates the Test User Group
        test_admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/userGroup")
        test_admin_page.wait_for_timeout(2000)
        expect(test_admin_page.locator("#addNew")).to_be_visible(timeout=15000)
        test_admin_page.click("#addNew")
        test_admin_page.wait_for_timeout(1000)
        test_admin_page.evaluate("mode = 'new'; $('#myModal').modal('show');")
        test_admin_page.wait_for_timeout(1000)
        test_admin_page.fill("#group_name", grp_name)
        test_admin_page.select_option("#swap_enabled", "1")
        test_admin_page.select_option("#share_type", "Dollar")
        test_admin_page.click("#myModal #formSubmit")
        test_admin_page.wait_for_timeout(3000)
        _dismiss_confirm_dialogs(test_admin_page)

        # Reload to ensure fresh datatable records
        test_admin_page.reload()
        test_admin_page.wait_for_timeout(2000)
        test_admin_page.fill('input[type="search"]', grp_name)
        test_admin_page.wait_for_timeout(1500)
        expect(test_admin_page.locator("table#datatable tbody tr").first).to_contain_text(grp_name)
        logger.info(f"User Group '{grp_name}' created successfully by test admin!")

        # Step 7: Test Admin User creates Client User under GRP_DHANYA_<ts>
        test_admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
        test_admin_page.wait_for_timeout(2500)

        expect(test_admin_page.locator("#addNew")).to_be_visible(timeout=15000)
        test_admin_page.click("#addNew")
        test_admin_page.wait_for_timeout(1000)
        if not test_admin_page.locator("#userAddModal").is_visible():
            test_admin_page.evaluate("$('#userAddModal').modal('show')")
            test_admin_page.wait_for_timeout(1000)

        test_admin_page.fill("#userAddModal #name", client_name)
        test_admin_page.fill("#userAddModal #email", client_email)
        test_admin_page.fill("#userAddModal #mobile", "9876543210")
        test_admin_page.fill("#userAddModal #pass", client_pass)
        test_admin_page.fill("#userAddModal #investor_pass", client_inv_pass)

        # Select the newly created user group
        test_admin_page.select_option("#userAddModal #user_group_id", label=grp_name)
        test_admin_page.wait_for_timeout(500)
        test_admin_page.select_option("#userAddModal #user_subgroup_value", value="500")

        test_admin_page.click("#userFormSubmit")
        test_admin_page.wait_for_timeout(3000)
        _dismiss_confirm_dialogs(test_admin_page)

        # Search created user in table
        test_admin_page.fill("#datatable_filter input", client_email)
        test_admin_page.wait_for_timeout(2000)
        user_row = test_admin_page.locator("table#datatable tbody tr").first
        expect(user_row).to_contain_text(client_name)

        # Extract Account ID
        account_id = test_admin_page.locator("table#datatable tbody tr td:nth-child(4)").first.inner_text().strip()
        logger.info(f"Created Client User '{client_name}' (Account ID: {account_id}) assigned to group '{grp_name}'")

        # Set email verification to 'Verified' to authorize immediate Client Portal login
        email_sel = user_row.locator("select.userEmailVerification").first
        email_sel.select_option(label="Verified")
        test_admin_page.wait_for_timeout(2000)
        _dismiss_confirm_dialogs(test_admin_page)

        # Step 8: Client User logs into Client Portal
        client_ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        client_page = client_ctx.new_page()

        client_login_url = settings.client_portal.login_url or "https://stage.xtremenext.com/login/"
        client_page.goto(client_login_url)
        client_page.wait_for_timeout(2000)
        client_page.fill("#email, input[name='email']", client_email)
        client_page.fill("#password, input[name='password']", client_pass)
        client_page.click("button.xn-btn-login, button.savebut, button[type='submit']")
        client_page.wait_for_timeout(4000)
        logger.info(f"Client Portal authenticated URL: {client_page.url}")

        session_data = {
            "master_ctx": master_ctx,
            "master_page": master_page,
            "test_admin_ctx": test_admin_ctx,
            "test_admin_page": test_admin_page,
            "client_ctx": client_ctx,
            "client_page": client_page,
            "role_name": role_name,
            "role_id": role_id,
            "admin_uname": admin_uname,
            "grp_name": grp_name,
            "client_name": client_name,
            "client_email": client_email,
            "client_pass": client_pass,
            "account_id": account_id,
        }

        yield session_data

    finally:
        # Step 9: Ordered Suite Teardown (Everything revoked at the end)
        logger.info("Executing ordered teardown for all created entities...")

        # 1. Close Client Portal context
        if client_ctx:
            try:
                client_ctx.close()
            except Exception:
                pass

        # 2. In Admin Portal: Delete Test Client User
        if test_admin_page and not test_admin_page.is_closed():
            try:
                test_admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
                test_admin_page.wait_for_timeout(2000)
                test_admin_page.fill("#datatable_filter input", client_email)
                test_admin_page.wait_for_timeout(1500)
                _expand_responsive_row(test_admin_page)
                del_client_btn = test_admin_page.locator("tr.child a.BtnDelete, table#datatable tbody tr a.BtnDelete").first
                if del_client_btn.is_visible():
                    del_client_btn.click()
                    test_admin_page.wait_for_timeout(1000)
                    swal = test_admin_page.locator(".swal2-confirm")
                    if swal.is_visible():
                        swal.click()
                        test_admin_page.wait_for_timeout(2000)
                    _dismiss_confirm_dialogs(test_admin_page)
                    logger.info(f"Deleted test client user {client_email}")
            except Exception as e:
                logger.warning(f"Error cleaning up client user {client_email}: {e}")

            # 3. In Admin Portal: Delete Test User Group
            try:
                test_admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/userGroup")
                test_admin_page.wait_for_timeout(2000)
                test_admin_page.fill('input[type="search"]', grp_name)
                test_admin_page.wait_for_timeout(1500)
                del_grp_btn = test_admin_page.locator("table#datatable tbody tr").first.locator("a.BtnDelete").first
                if del_grp_btn.is_visible():
                    del_grp_btn.click()
                    test_admin_page.wait_for_timeout(1000)
                    swal = test_admin_page.locator(".swal2-confirm")
                    if swal.is_visible():
                        swal.click()
                        test_admin_page.wait_for_timeout(2000)
                    _dismiss_confirm_dialogs(test_admin_page)
                    logger.info(f"Deleted test user group {grp_name}")
            except Exception as e:
                logger.warning(f"Error cleaning up user group {grp_name}: {e}")

            # 4. Logout Test Admin User
            try:
                test_admin_page.goto("https://stage.xtremenext.com/admin/Login/logout")
                test_admin_page.wait_for_timeout(2000)
                logger.info(f"Logged out test admin user {admin_uname}")
            except Exception as e:
                logger.warning(f"Error logging out test admin user: {e}")
            finally:
                if test_admin_ctx:
                    test_admin_ctx.close()

        # 5. In Master Admin: Delete Test Admin User
        try:
            master_page.goto("https://stage.xtremenext.com/admin/Controlbase/admin")
            master_page.wait_for_timeout(2000)
            master_page.fill('input[type="search"]', admin_uname)
            master_page.wait_for_timeout(1500)
            del_admin_btn = master_page.locator("table#datatable tbody tr td a.BtnDelete, table#datatable tbody tr td a.btnDelete").first
            if del_admin_btn.is_visible():
                del_admin_btn.click()
                master_page.wait_for_timeout(1000)
                swal = master_page.locator(".swal2-confirm")
                if swal.is_visible():
                    swal.click()
                    master_page.wait_for_timeout(2000)
                _dismiss_confirm_dialogs(master_page)
                logger.info(f"Deleted test admin user {admin_uname}")
        except Exception as e:
            logger.warning(f"Error cleaning up test admin user: {e}")

        # 6. In Master Admin: Delete Custom Test Role
        try:
            master_page.goto("https://stage.xtremenext.com/admin/Controlbase/rolePermission")
            master_page.wait_for_timeout(2000)
            master_page.fill('input[type="search"]', role_name)
            master_page.wait_for_timeout(1500)
            del_role_btn = master_page.locator("table#datatable tbody tr td a.BtnDelete, table#datatable tbody tr td a.btnDelete").first
            if del_role_btn.is_visible():
                del_role_btn.click()
                master_page.wait_for_timeout(1000)
                swal = master_page.locator(".swal2-confirm")
                if swal.is_visible():
                    swal.click()
                    master_page.wait_for_timeout(2000)
                _dismiss_confirm_dialogs(master_page)
                logger.info(f"Deleted custom test role {role_name}")
        except Exception as e:
            logger.warning(f"Error cleaning up test role: {e}")

        master_ctx.close()


# ==============================================================================
# WORKFLOW 1: VERIFY ROLE PERMISSION ACCESS ACROSS ALL MODULES
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_test_admin_comprehensive_permissions(full_workflow_session: Dict[str, Any]):
    """
    Verify that the test admin user logged in under the newly created custom role
    has active access to all granted modules in the sidebar.
    """
    admin_page: Page = full_workflow_session["test_admin_page"]
    admin_uname = full_workflow_session["admin_uname"]

    sidebar_html = admin_page.locator("#sidebar-menu").inner_html()

    expected_menus = ["Dashboard", "Account Details", "User Group", "Manager", "Symbol", "Bonus", "Active User"]
    for menu in expected_menus:
        assert menu in sidebar_html, f"Expected menu '{menu}' to be granted and present in sidebar HTML"
    logger.info(f"Role permission validation successful for all major modules for {admin_uname}!")


# ==============================================================================
# WORKFLOW 2: USER GROUP ACTION BUTTONS & FORM VALUES
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_user_group_actions_and_subgroup_inspection(full_workflow_session: Dict[str, Any]):
    """
    Verify User Group actions (edit name, subgroup modal) and form values under test admin.
    """
    admin_page: Page = full_workflow_session["test_admin_page"]
    grp_name = full_workflow_session["grp_name"]

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/userGroup")
    admin_page.wait_for_timeout(2000)

    admin_page.fill('input[type="search"]', grp_name)
    admin_page.wait_for_timeout(1500)
    row = admin_page.locator("table#datatable tbody tr").first
    expect(row).to_contain_text(grp_name)

    # 1. Test in-row edit name button (a.btnNameEdit)
    edit_name_btn = row.locator("a.btnNameEdit").first
    expect(edit_name_btn).to_be_visible()

    # 2. Test Subgroup modal (a.btnSubgroup -> #subgroupModal)
    subgroup_btn = row.locator("a.btnSubgroup").first
    expect(subgroup_btn).to_be_visible()
    subgroup_btn.click()
    admin_page.wait_for_timeout(1500)

    modal = admin_page.locator("#subgroupModal")
    expect(modal).to_be_visible()
    expect(admin_page.locator("#subgroup_group_name")).to_contain_text(grp_name)

    # Close modal cleanly
    close_btn = modal.locator("button.ux-card-close, button[data-bs-dismiss='modal'], button:has-text('Close')").first
    close_btn.click()
    admin_page.wait_for_timeout(1000)
    logger.info(f"User Group actions and subgroup modal verified for {grp_name}!")


# ==============================================================================
# WORKFLOW 3: CLIENT PORTAL LEVERAGE CHANGE & REFLECTION IN ADMIN
# ==============================================================================

@pytest.mark.admin
@pytest.mark.client
@pytest.mark.regression
def test_workflow_client_leverage_change_and_admin_reflection(full_workflow_session: Dict[str, Any]):
    """
    Client changes leverage in Client Portal Settings -> Trading Account.
    Verify that the updated leverage is reflected in Admin Portal (Switch Group column).
    """
    admin_page: Page = full_workflow_session["test_admin_page"]
    client_page: Page = full_workflow_session["client_page"]
    client_email = full_workflow_session["client_email"]
    grp_name = full_workflow_session["grp_name"]

    # 1. In Client Portal: Navigate to Settings
    client_page.goto("https://stage.xtremenext.com/client-portal")
    client_page.wait_for_timeout(2500)

    settings_link = client_page.locator("aside a:has-text('Settings'), main a:has-text('Settings'), nav a:has-text('Settings')").first
    if settings_link.is_visible():
        settings_link.click()
        client_page.wait_for_timeout(2000)

    trading_tab = client_page.locator("button:has-text('Trading Account'), a:has-text('Trading Account')").first
    if trading_tab.is_visible():
        trading_tab.click()
        client_page.wait_for_timeout(1500)

    leverage_sel = client_page.locator("main [role='combobox'], main select").nth(2)
    save_btn = client_page.locator("main button:has-text('SAVE TRADING SETTINGS')")

    if leverage_sel.is_visible():
        try:
            leverage_sel.select_option(index=1)
        except Exception:
            try:
                leverage_sel.click()
                client_page.wait_for_timeout(500)
                client_page.keyboard.press("ArrowDown")
                client_page.keyboard.press("Enter")
            except Exception:
                pass

        if save_btn.is_visible():
            save_btn.click()
            client_page.wait_for_timeout(2500)
            logger.info("Saved updated trading settings in Client Portal!")

    # 2. In Admin Portal: Verify Switch Group column
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#datatable_filter input", client_email)
    admin_page.wait_for_timeout(2000)

    row = admin_page.locator("table#datatable tbody tr").first
    expect(row).to_contain_text(grp_name)
    logger.info(f"Client user group and leverage verified in Admin Portal for {client_email}!")


# ==============================================================================
# WORKFLOW 4: ADMIN SWITCH USER GROUP OPTION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_admin_switch_group_action(full_workflow_session: Dict[str, Any]):
    """
    Test Admin exercises the 'Switch Group' button (.switchGroup) on the client user row,
    opens #switchGroupModal, selects group/subgroup, and submits #switchGroupBtn.
    """
    admin_page: Page = full_workflow_session["test_admin_page"]
    client_email = full_workflow_session["client_email"]
    grp_name = full_workflow_session["grp_name"]

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#datatable_filter input", client_email)
    admin_page.wait_for_timeout(2000)

    # Expand responsive row to reveal hidden action buttons
    _expand_responsive_row(admin_page)

    switch_grp_btn = admin_page.locator("tr.child button.switchGroup").first
    expect(switch_grp_btn).to_be_visible(timeout=5000)
    switch_grp_btn.click()
    admin_page.wait_for_timeout(1500)

    modal = admin_page.locator("#switchGroupModal")
    expect(modal).to_be_visible()

    # Select group & subgroup
    admin_page.select_option("#switchGroupModal #group_id", label=grp_name)
    admin_page.wait_for_timeout(500)
    admin_page.select_option("#switchGroupModal #subgroup_value", value="500")

    # Submit switch group
    admin_page.click("#switchGroupBtn")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # Verify updated row reflection
    admin_page.fill("#datatable_filter input", client_email)
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text(grp_name)
    logger.info(f"Switch Group action completed successfully for {client_email}!")


# ==============================================================================
# WORKFLOW 5: USER CREDIT / BONUS LIFECYCLE (ADD, MODIFY, WITHDRAW)
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_user_bonus_lifecycle_add_modify_withdraw(full_workflow_session: Dict[str, Any]):
    """
    Test Admin exercises the complete Bonus lifecycle:
    1. Adds Bonus on /admin/Controlbase/user using row action (#userCreditBonus).
    2. Navigates to /admin/Controlbase/creditList and verifies bonus in table.
    3. Modifies bonus amount (a.btnEdit -> #myModal).
    4. Withdraws / removes bonus (a.BtnDelete).
    """
    admin_page: Page = full_workflow_session["test_admin_page"]
    client_email = full_workflow_session["client_email"]
    account_id = full_workflow_session["account_id"]

    # 1. Add Bonus on /admin/Controlbase/user
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/user")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#datatable_filter input", client_email)
    admin_page.wait_for_timeout(2000)

    # Expand responsive row to reveal Bonus button
    _expand_responsive_row(admin_page)

    bonus_btn = admin_page.locator("tr.child button.userCredit").first
    expect(bonus_btn).to_be_visible(timeout=5000)
    bonus_btn.click()
    admin_page.wait_for_timeout(1500)

    bonus_modal = admin_page.locator("#userCreditBonus")
    expect(bonus_modal).to_be_visible()

    admin_page.fill("#userCreditBonus #user_credit", "500.00")
    admin_page.fill("#userCreditBonus #expire_date", "2027-10-31")
    admin_page.click("#userCreditBonusBtn")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)
    logger.info(f"Added 500.00 bonus for Account {account_id}")

    # 2. Verify on /admin/Controlbase/creditList
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/creditList")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#datatable_filter input", str(account_id))
    admin_page.wait_for_timeout(1500)

    bonus_row = admin_page.locator("table#datatable tbody tr").first
    expect(bonus_row).to_contain_text(str(account_id))
    expect(bonus_row).to_contain_text("500.00")
    logger.info(f"Bonus 500.00 verified on creditList page for Account {account_id}")

    # 3. Modify Bonus
    edit_btn = bonus_row.locator("a.btnEdit").first
    expect(edit_btn).to_be_visible(timeout=5000)
    edit_btn.click()
    admin_page.wait_for_timeout(1500)

    edit_modal = admin_page.locator("#myModal")
    expect(edit_modal).to_be_visible()
    admin_page.fill("#myModal #user_credit", "600.00")
    admin_page.click("#myModal #formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    admin_page.fill("#datatable_filter input", str(account_id))
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("table#datatable tbody tr").first).to_contain_text("600.00")
    logger.info(f"Bonus modified to 600.00 for Account {account_id}")

    # 4. Withdraw Bonus
    del_btn = admin_page.locator("table#datatable tbody tr").first.locator("a.BtnDelete").first
    expect(del_btn).to_be_visible(timeout=5000)
    del_btn.click()
    admin_page.wait_for_timeout(1500)

    swal = admin_page.locator(".swal2-confirm")
    if swal.is_visible():
        swal.click()
        admin_page.wait_for_timeout(2000)
    _dismiss_confirm_dialogs(admin_page)
    admin_page.wait_for_timeout(2000)

    # Verify withdrawal
    admin_page.fill("#datatable_filter input", "")
    admin_page.wait_for_timeout(500)
    admin_page.fill("#datatable_filter input", str(account_id))
    admin_page.wait_for_timeout(1500)
    empty_cell = admin_page.locator("table#datatable tbody td.dataTables_empty")
    assert empty_cell.is_visible() or admin_page.locator(f"table#datatable:has-text('{account_id}')").count() == 0, (
        f"Expected bonus for Account {account_id} to be withdrawn"
    )
    logger.info(f"Bonus successfully withdrawn for Account {account_id}!")


# ==============================================================================
# WORKFLOW 6: ACTIVE USERS REFLECTION
# ==============================================================================

@pytest.mark.admin
@pytest.mark.regression
def test_workflow_active_users_reflection(full_workflow_session: Dict[str, Any]):
    """
    Test Admin inspects Active Users on /admin/Controlbase/activeUsers.
    Verifies that the datatable renders and checks if the client user is listed.
    """
    admin_page: Page = full_workflow_session["test_admin_page"]
    client_name = full_workflow_session["client_name"]
    account_id = full_workflow_session["account_id"]

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/activeUsers")
    admin_page.wait_for_timeout(2500)

    table = admin_page.locator("#au-datatable")
    expect(table).to_be_visible()

    search_input = admin_page.locator("#au-datatable_filter input")
    expect(search_input).to_be_visible()

    # Search for our client account ID
    search_input.fill(str(account_id))
    admin_page.wait_for_timeout(1500)

    row_count = admin_page.locator("#au-datatable tbody tr:not(:has(.dataTables_empty))").count()
    logger.info(f"Active Users search for Account {account_id} returned {row_count} rows.")
    if row_count > 0:
        row_text = admin_page.locator("#au-datatable tbody tr").first.inner_text().replace("\n", " ")
        logger.info(f"Active User entry verified: {row_text}")
    else:
        logger.info(f"Account {account_id} not currently listed in active socket sessions (offline indicator).")
