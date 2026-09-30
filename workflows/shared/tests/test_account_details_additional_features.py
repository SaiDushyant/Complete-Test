"""
Additional Features & Scenarios Practical Validation Test Suite.
Validates all supplementary operational features on Admin Account Details (/admin/Controlbase/user):
1. Account Type Toggle (Standard vs Cent)
2. User Status Toggle (Active vs Not Active)
3. Book Assignment (A-Book vs B-Book)
4. Edit User Modal (Name, Mobile, Fund, Equity, Balance)
5. Add Credit Bonus Modal (Credit bonus, expiry date)
6. Stopout Percentage Modal (Stopout %)
7. Edit Referby ID Modal (Referral sponsor ID)
8. Send Password Reset Link Action
9. Make MAM Modal (MAM Master rank and username)
10. Make PAMM Modal (PAMM Master rank and username)
11. Make Copy Trading Modal (Copy Trading Master rank, username, fee %)
12. Private Copy Trading Modal (Master, Slave picker, copy type, trading direction)
13. Switch Group & Leverage Modal (Group list and leverage selection)
14. Create Account For User Modal (User picker, account email toggle)
15. Add User Registration Modal (Full trader registration form)
16. Export Utilities & Refresh (CSV, PDF, Excel, and DataTable Refresh)
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage


def _get_admin_page(workflow_browser: Browser) -> tuple[BrowserContext, Page, UserManagementPage]:
    """Helper to authenticate admin quickly using auth_state or login and navigate to Account Details."""
    auth_file = settings.admin_portal.auth_state_path
    if auth_file.exists() and auth_file.stat().st_size > 0:
        ctx = workflow_browser.new_context(
            storage_state=str(auth_file),
            viewport={"width": 1600, "height": 900},
            ignore_https_errors=True,
        )
    else:
        ctx = workflow_browser.new_context(
            viewport={"width": 1600, "height": 900},
            ignore_https_errors=True,
        )
    page = ctx.new_page()
    user_page = UserManagementPage(page)
    user_page.navigate()
    if "Login" in page.url:
        login_page = AdminLoginPage(page)
        login_page.login()
        user_page.navigate()
    return ctx, page, user_page


def _safe_close_modal(page: Page, modal_selector: str) -> None:
    """Helper to safely close any Bootstrap modal via close button or jQuery."""
    modal = page.locator(modal_selector)
    close_btn = modal.locator(".ux-card-close, button[data-bs-dismiss='modal'], .modal-footer button:has-text('Close')").first
    if close_btn.is_visible():
        try:
            close_btn.click(timeout=2000)
        except Exception:
            pass
    page.wait_for_timeout(300)
    page.evaluate(f"() => {{ if (window.jQuery) {{ window.jQuery('{modal_selector}').modal('hide'); }} }}")
    page.wait_for_timeout(300)


@pytest.mark.shared
def test_additional_account_type_toggle(workflow_browser: Browser):
    """
    Verify inline Account Type select dropdown allows switching between Standard and Cent trading account types.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        acc_type_sel = page.locator("select.updateAccountType").first
        expect(acc_type_sel).to_be_attached()
        options = [acc_type_sel.locator("option").nth(i).get_attribute("value") 
                   for i in range(acc_type_sel.locator("option").count())]
        assert "standard" in options, "Expected 'standard' in Account Type options"
        assert "cent" in options, "Expected 'cent' in Account Type options"
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_user_status_active_inactive_toggle(workflow_browser: Browser):
    """
    Verify inline User Status select contains Active (1) and Not Active (0) states for account access control.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        status_sel = page.locator("select.updateUserStatus").first
        expect(status_sel).to_be_attached()
        options = [status_sel.locator("option").nth(i).get_attribute("value") 
                   for i in range(status_sel.locator("option").count())]
        assert "1" in options, "Expected '1' (Active) in User Status options"
        assert "0" in options, "Expected '0' (Not Active) in User Status options"
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_book_assignment_a_and_b_book(workflow_browser: Browser):
    """
    Verify Book assignment dropdown allows toggling between A-Book (STP LP routing) and B-Book (Broker Risk book).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        book_sel = page.locator("select.userBook").first
        expect(book_sel).to_be_attached()
        options = [book_sel.locator("option").nth(i).get_attribute("value") 
                   for i in range(book_sel.locator("option").count())]
        assert "a" in options, "Expected 'a' (A Book) in Book options"
        assert "b" in options, "Expected 'b' (B Book) in Book options"
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_edit_user_modal_form(workflow_browser: Browser):
    """
    Verify clicking Edit User pencil (a.btnEditUser) opens #editUserModal with Name, Mobile, Fund, Equity, and Balance fields.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_edit_user = page.locator("a.btnEditUser:visible").first
        expect(btn_edit_user).to_be_visible()
        btn_edit_user.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#editUserModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Edit User")
        expect(modal.locator("#user_name")).to_be_visible()
        expect(modal.locator("#phone")).to_be_visible()
        expect(modal.locator("#fund")).to_be_visible()
        expect(modal.locator("#equity")).to_be_visible()
        expect(modal.locator("#balance")).to_be_visible()
        expect(modal.locator("#editUserButton")).to_be_visible()

        _safe_close_modal(page, "#editUserModal")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_add_credit_bonus_modal_form(workflow_browser: Browser):
    """
    Verify clicking Bonus button (button.userCredit) opens #userCreditBonus modal with Bonus Amount and Expire Date inputs.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_bonus = page.locator("button.userCredit:visible").first
        expect(btn_bonus).to_be_visible()
        btn_bonus.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#userCreditBonus")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("User Bonus")
        expect(modal.locator("#user_credit")).to_be_visible()
        expect(modal.locator("#expire_date")).to_be_visible()
        expect(modal.locator("#userCreditBonusBtn")).to_be_visible()

        _safe_close_modal(page, "#userCreditBonus")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_stopout_percentage_modal_form(workflow_browser: Browser):
    """
    Verify clicking Stopout pencil (a.btnEditStopout) opens #stopoutModal for setting custom stop-out percentage.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_stopout = page.locator("a.btnEditStopout:visible").first
        expect(btn_stopout).to_be_visible()
        btn_stopout.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#stopoutModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Stop-out")
        expect(modal.locator("#stopout")).to_be_visible()
        expect(modal.locator("#stopoutSavebtn")).to_be_visible()

        _safe_close_modal(page, "#stopoutModal")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_edit_referby_id_modal_form(workflow_browser: Browser):
    """
    Verify clicking Refer By pencil (a.btnEditReferBy) opens #refreByModal for updating referral sponsor ID.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_refer = page.locator("a.btnEditReferBy:visible").first
        expect(btn_refer).to_be_visible()
        btn_refer.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#refreByModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Referby")
        expect(modal.locator("#referby")).to_be_visible()
        expect(modal.locator("#refreByButton")).to_be_visible()

        _safe_close_modal(page, "#refreByModal")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_password_reset_link_button(workflow_browser: Browser):
    """
    Verify Password Reset button (button.userPasswordResetLink) is present in row actions.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_reset = page.locator("button.userPasswordResetLink:visible").first
        expect(btn_reset).to_be_visible()
        assert "Password Reset" in btn_reset.inner_text()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_make_mam_workflow(workflow_browser: Browser):
    """
    Verify clicking MAM action (button.userMam) triggers either #mampopup (Make MAM) or confirmation dialog (Disable MAM).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_mam = page.locator("button.userMam:visible, button:has-text('MAM'):visible").first
        expect(btn_mam).to_be_visible()
        btn_mam.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#mampopup")
        if modal.is_visible():
            expect(modal.locator(".modal-title")).to_contain_text("Make MAM")
            expect(modal.locator("#rank")).to_be_visible()
            expect(modal.locator("#mam_name")).to_be_visible()
            _safe_close_modal(page, "#mampopup")
        else:
            confirm_box = page.locator(".jconfirm-box:visible, .jconfirm:visible").first
            expect(confirm_box).to_be_visible()
            dismiss_btn = page.locator(".jconfirm button:has-text('close'), .jconfirm button:has-text('Cancel'), .jconfirm button.btn-default").first
            if dismiss_btn.is_visible():
                dismiss_btn.click()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_make_pamm_workflow(workflow_browser: Browser):
    """
    Verify clicking PAMM action (button.userPamm) triggers either #pammpopup (Make PAMM) or confirmation dialog (Disable PAMM).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_pamm = page.locator("button.userPamm:visible, button:has-text('PAMM'):visible").first
        expect(btn_pamm).to_be_visible()
        btn_pamm.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#pammpopup")
        if modal.is_visible():
            expect(modal.locator(".modal-title")).to_contain_text("Make PAMM")
            expect(modal.locator("#pamm_rank")).to_be_visible()
            expect(modal.locator("#pamm_name")).to_be_visible()
            _safe_close_modal(page, "#pammpopup")
        else:
            confirm_box = page.locator(".jconfirm-box:visible, .jconfirm:visible").first
            expect(confirm_box).to_be_visible()
            dismiss_btn = page.locator(".jconfirm button:has-text('close'), .jconfirm button:has-text('Cancel'), .jconfirm button.btn-default").first
            if dismiss_btn.is_visible():
                dismiss_btn.click()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_make_copy_trading_modal_form(workflow_browser: Browser):
    """
    Verify clicking Copy Trading button (button.userCopyTrading) opens #copyTradingPopup with Rank, User name, and Fee inputs.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_ct = page.locator("button.userCopyTrading:visible").first
        expect(btn_ct).to_be_visible()
        btn_ct.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#copyTradingPopup")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Make Copy Trading")
        expect(modal.locator("#copy_trading_name")).to_be_visible()
        expect(modal.locator("#copy_trading_fee_manager")).to_be_visible()
        expect(modal.locator("#formCTSubmit")).to_be_visible()

        _safe_close_modal(page, "#copyTradingPopup")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_private_copy_trading_modal_and_slaves(workflow_browser: Browser):
    """
    Verify clicking Private Copy button opens #privateCopierUserModal with Master display, Slave search, Copy Type, and Direction.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_pc = page.locator("button.userPrivateCopyTrading:visible").first
        expect(btn_pc).to_be_visible()
        btn_pc.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#privateCopierUserModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Private Copy Trading")
        expect(modal.locator("#pcMasterDisplay")).to_be_visible()
        expect(modal.locator("#pcSlaveSearch")).to_be_visible()
        expect(modal.locator("#pcTradeMethod")).to_be_visible()
        expect(modal.locator("#pcDirectionNormal")).to_be_attached()
        expect(modal.locator("#pcDirectionReverse")).to_be_attached()
        expect(modal.locator("#pcFormSubmit")).to_be_visible()

        _safe_close_modal(page, "#privateCopierUserModal")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_switch_group_and_leverage_modal(workflow_browser: Browser):
    """
    Verify clicking Switch Group button opens #switchGroupModal with Group List options (ECN, Default, etc.) and Leverage selection.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.user_rows.first).to_be_visible(timeout=10000)
        user_page.expand_row(0)
        page.wait_for_timeout(800)

        btn_sg = page.locator("button.switchGroup:visible").first
        expect(btn_sg).to_be_visible()
        btn_sg.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#switchGroupModal")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Switch Group")
        expect(modal.locator("#group_id")).to_be_visible()
        expect(modal.locator("#subgroup_value")).to_be_visible()
        expect(modal.locator("#switchGroupBtn")).to_be_visible()

        _safe_close_modal(page, "#switchGroupModal")
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_create_account_for_user_modal(workflow_browser: Browser):
    """
    Verify clicking Create Account topbar button opens #createAccountModal with user search (#caUserSearch) and send mail checkbox.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.create_account_button).to_be_visible()
        user_page.open_create_account_modal()
        modal = user_page.create_account_modal
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("Create Account For User")
        expect(modal.locator("#caUserSearch")).to_be_visible()
        expect(modal.locator("#sendmail")).to_be_attached()
        expect(modal.locator("#createAcBtn")).to_be_visible()

        user_page.close_create_account_modal()
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_add_user_registration_modal(workflow_browser: Browser):
    """
    Verify clicking Add User topbar button opens #userAddModal with all registration fields (Name, Email, Mobile, Pass, Group, Leverage).
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.add_user_button).to_be_visible()
        user_page.open_add_user_modal()
        modal = user_page.user_add_modal
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-title")).to_contain_text("User Details")
        expect(modal.locator("#name")).to_be_visible()
        expect(modal.locator("#email")).to_be_visible()
        expect(modal.locator("#mobile")).to_be_visible()
        expect(modal.locator("#pass")).to_be_visible()
        expect(modal.locator("#investor_pass")).to_be_visible()
        expect(modal.locator("#user_group_id")).to_be_visible()
        expect(modal.locator("#user_subgroup_value")).to_be_visible()
        expect(modal.locator("#sendmailuser")).to_be_attached()
        expect(modal.locator("#userFormSubmit")).to_be_visible()

        user_page.close_add_user_modal()
        expect(modal).not_to_be_visible()
    finally:
        ctx.close()


@pytest.mark.shared
def test_additional_export_buttons_and_refresh(workflow_browser: Browser):
    """
    Verify CSV, PDF, Excel data export buttons are rendered, and the Refresh button reloads table data via AJAX without errors.
    """
    ctx, page, user_page = _get_admin_page(workflow_browser)
    try:
        expect(user_page.csv_button).to_be_visible()
        expect(user_page.pdf_button).to_be_visible()
        expect(user_page.excel_button).to_be_visible()

        # Click Refresh
        initial_count = user_page.get_user_count()
        user_page.click_refresh()
        page.wait_for_timeout(1000)
        assert user_page.get_user_count() == initial_count, "Expected table count to persist after refresh"
    finally:
        ctx.close()
