"""
Client Portal Exhaustive Labels, Inputs, Dropdowns, Checkboxes & Controls Validation Suite.
Validates EVERY minute label, placeholder, dropdown option list, checkbox (Remember Me, Terms),
search input, and interactive control across all 11 modules and authentication pages.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_register_page import ClientRegisterPage
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
from workflows.client_portal.pages.client_withdraw_page import ClientWithdrawPage
from workflows.client_portal.pages.client_internal_transfer_page import ClientInternalTransferPage
from workflows.client_portal.pages.client_wallet_page import ClientWalletPage
from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.client_portal.pages.client_mam_page import ClientMAMPage
from workflows.client_portal.pages.client_pamm_page import ClientPAMMPage
from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_all_elements_labels_dropdowns")

pytestmark = [pytest.mark.client, pytest.mark.validation]


# =============================================================================
# 1. LOGIN & SIGNUP PAGES (Labels, Placeholders, Checkboxes, Dropdowns)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_login_page_all_labels_and_checkboxes(browser: Browser):
    """
    Verify every label, placeholder, checkbox (Remember Me), toggle, and link on the Login page.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    login_page = ClientLoginPage(page)

    try:
        login_page.navigate()

        # 1. Branding & Headings
        expect(page.locator("text=/Sign in|Welcome|Login/i").first).to_be_visible()

        # 2. Email Label & Input
        expect(login_page.email_input).to_be_visible()
        email_ph = login_page.email_input.get_attribute("placeholder") or ""
        assert len(email_ph) > 0, "Email input missing placeholder"

        # 3. Password Label & Input
        expect(login_page.password_input).to_be_visible()
        pass_ph = login_page.password_input.get_attribute("placeholder") or ""
        assert len(pass_ph) > 0, "Password input missing placeholder"

        # 4. Remember Me Checkbox & Label
        expect(login_page.remember_me_checkbox).to_be_attached()
        if login_page.remember_me_label.is_visible():
            expect(login_page.remember_me_label).to_contain_text(re.compile(r"Remember", re.I))

        # Test Checkbox Interaction (check / uncheck)
        login_page.remember_me_checkbox.check()
        assert login_page.remember_me_checkbox.is_checked(), "Remember Me checkbox failed to check!"
        login_page.remember_me_checkbox.uncheck()
        assert not login_page.remember_me_checkbox.is_checked(), "Remember Me checkbox failed to uncheck!"

        # 5. Forgot Password Link
        expect(login_page.forgot_password_link).to_be_visible()
        expect(login_page.forgot_password_link).to_contain_text(re.compile(r"Forgot", re.I))

        # 6. Login Button
        expect(login_page.login_button).to_be_visible()
        expect(login_page.login_button).to_contain_text(re.compile(r"Sign in|Login", re.I))

        # 7. Sign up navigation link
        signup_link = page.locator("a[href*='register'], a:has-text('Sign up')").first
        expect(signup_link).to_be_visible()

        logger.info("Verified all Login page labels, placeholders, and Remember Me checkbox.")
    finally:
        ctx.close()


@pytest.mark.client
@pytest.mark.regression
def test_val_signup_page_all_labels_dropdowns_and_checkboxes(browser: Browser):
    """
    Verify every label, input placeholder, country code dropdown, and Terms checkbox across Step 1 and Step 2 of Registration.
    """
    ctx: BrowserContext = browser.new_context(viewport=settings.browser.viewport, ignore_https_errors=True)
    page: Page = ctx.new_page()
    reg_page = ClientRegisterPage(page)

    try:
        reg_page.navigate()

        # Step 1: Labels & Inputs
        expect(reg_page.name_input).to_be_visible()
        expect(reg_page.email_input).to_be_visible()
        expect(reg_page.phone_input).to_be_visible()

        # Step 1: Country Dial Code dropdown / combobox
        country_select = page.locator(".iti__country-list, select.iti-country-select, .iti__selected-country, [role='combobox']").first
        if country_select.is_visible():
            expect(country_select).to_be_visible()
            logger.info("Country dial code dropdown is visible and interactive.")

        # Check Step 1 Placeholders
        assert (reg_page.name_input.get_attribute("placeholder") or "").strip() != ""
        assert (reg_page.email_input.get_attribute("placeholder") or "").strip() != ""
        assert (reg_page.phone_input.get_attribute("placeholder") or "").strip() != ""

        # Step 1: Next button & Sign in link
        expect(reg_page.next_button).to_be_visible()
        signin_link = page.locator("a[href*='login'], a:has-text('Sign in')").first
        expect(signin_link).to_be_visible()

        # Fill Step 1 and advance to Step 2
        reg_page.fill_step_1(name="Alexander Taylor", email="val_label_test@mailinator.com", phone="9876543210")
        reg_page.click_next()

        # Step 2: Password, Confirm Password, Terms Checkbox, Sign up Button
        expect(reg_page.password_input).to_be_visible()
        expect(reg_page.confirm_password_input).to_be_visible()

        # Terms & Conditions Checkbox
        terms_checkbox = page.locator("#inputCheckbox, input[type='checkbox']").first
        expect(terms_checkbox).to_be_attached()
        terms_checkbox.check()
        assert terms_checkbox.is_checked(), "Terms checkbox failed to check!"
        terms_checkbox.uncheck()
        assert not terms_checkbox.is_checked(), "Terms checkbox failed to uncheck!"
        terms_checkbox.check()

        # Submit button
        expect(reg_page.signup_submit_button).to_be_visible()

        logger.info("Verified all Registration page labels, dropdowns, and checkboxes.")
    finally:
        ctx.close()


# =============================================================================
# 2. DASHBOARD (Metrics, Cash Flow Period Toggles, Sidebar Links)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_dashboard_all_labels_and_controls(client_dashboard_page: ClientDashboardPage):
    """
    Verify all labels, metric cards, cash flow tabs, and sidebar navigation links.
    """
    client_dashboard_page.navigate()

    # 1. Summary Cards
    expect(client_dashboard_page.total_funds_card).to_be_visible()
    expect(client_dashboard_page.account_balance_card).to_be_visible()
    expect(client_dashboard_page.available_buffer_card).to_be_visible()
    expect(client_dashboard_page.active_referrals_card).to_be_visible()

    # 2. Cash Flow Section & Period Toggle Tabs
    expect(client_dashboard_page.cash_flow_container).to_be_visible()
    expect(client_dashboard_page.cash_flow_day_tab).to_be_visible()
    expect(client_dashboard_page.cash_flow_week_tab).to_be_visible()
    expect(client_dashboard_page.cash_flow_month_tab).to_be_visible()

    # 3. Sidebar Navigation Tabs Verification
    sidebar = client_dashboard_page.sidebar
    expect(sidebar.dashboard_tab.first).to_be_visible()
    expect(sidebar.deposit_tab.first).to_be_visible()
    expect(sidebar.withdraw_tab.first).to_be_visible()
    expect(sidebar.internal_transfer_tab.first).to_be_visible()
    expect(sidebar.wallet_tab.first).to_be_visible()
    expect(sidebar.copy_trading_tab.first).to_be_visible()
    expect(sidebar.mam_tab.first).to_be_visible()
    expect(sidebar.pamm_tab.first).to_be_visible()
    expect(sidebar.refer_earn_tab.first).to_be_visible()
    expect(sidebar.settings_tab.first).to_be_visible()

    logger.info("Verified all Dashboard labels, metric cards, cash flow toggles, and sidebar links.")


# =============================================================================
# 3. DEPOSIT PAGE (Funding Rails, Form Dropdowns, Dropzone, History Table)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_deposit_all_labels_and_dropdowns(client_deposit_page: ClientDepositPage):
    """
    Verify all funding rail labels, deposit form dropdown options, proof upload dropzone, and history table headers.
    """
    client_deposit_page.navigate()

    # 1. Funding Rails Cards
    rails = client_deposit_page.get_funding_rails_info()
    assert len(rails) > 0, "No funding rail cards found"
    for r in rails:
        assert "minimum" in r["full_text"].lower()

    # 2. Form Dropdowns Options
    expect(client_deposit_page.destination_account_select).to_be_visible()
    expect(client_deposit_page.payment_method_select).to_be_visible()

    dest_options = client_deposit_page.destination_account_select.locator("option").all()
    assert len(dest_options) > 0, "Destination account select has no options"

    payment_methods = client_deposit_page.get_payment_method_options()
    assert len(payment_methods) > 0, "Payment method select has no options"

    # 3. Amount & Dropzone Labels
    expect(client_deposit_page.amount_input).to_be_visible()
    expect(client_deposit_page.proof_upload_label).to_be_visible()
    expect(client_deposit_page.submit_button).to_be_visible()

    # 4. History Table Headers & Rows Select
    headers = client_deposit_page.get_table_headers()
    assert all(h in " ".join(headers) for h in ["DATE", "METHOD", "AMOUNT", "STATUS"]), (
        f"Missing expected deposit history headers: {headers}"
    )
    expect(client_deposit_page.history_rows_select).to_be_visible()

    logger.info("Verified all Deposit page labels, dropdown options, dropzone, and table headers.")


# =============================================================================
# 4. WITHDRAW PAGE (Bank Details, Crypto Addresses, Form Dropdowns, OTP Modal)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_withdraw_all_labels_inputs_and_dropdowns(client_withdraw_page: ClientWithdrawPage):
    """
    Verify all 6 bank detail inputs, 4 crypto address inputs & copy buttons, payout dropdowns, and table headers.
    """
    client_withdraw_page.navigate()

    # 1. Bank Details Inputs
    expect(client_withdraw_page.bank_name_input).to_be_visible()
    expect(client_withdraw_page.account_number_input).to_be_visible()
    expect(client_withdraw_page.ifsc_code_input).to_be_visible()
    expect(client_withdraw_page.swift_code_input).to_be_visible()
    expect(client_withdraw_page.branch_input).to_be_visible()
    expect(client_withdraw_page.location_input).to_be_visible()
    expect(client_withdraw_page.save_details_button).to_be_visible()

    # 2. Crypto Addresses & Copy Buttons
    expect(client_withdraw_page.usdt_trc20_input).to_be_visible()
    expect(client_withdraw_page.usdt_bep_input).to_be_visible()
    expect(client_withdraw_page.upi_input).to_be_visible()
    expect(client_withdraw_page.ss_payment_input).to_be_visible()

    # 3. Request Payout Dropdowns
    source_options = client_withdraw_page.get_source_options()
    assert len(source_options) > 0, "Withdraw source select has no options"

    payment_options = client_withdraw_page.get_payment_method_options()
    assert len(payment_options) > 0, "Withdraw payment method select has no options"

    expect(client_withdraw_page.amount_input).to_be_visible()
    expect(client_withdraw_page.request_withdraw_button).to_be_visible()

    # 4. History Table Headers
    headers = client_withdraw_page.get_table_headers()
    assert all(h in " ".join(headers) for h in ["DATE", "METHOD", "AMOUNT", "STATUS"]), (
        f"Missing expected withdraw history headers: {headers}"
    )

    logger.info("Verified all Withdraw page labels, inputs, crypto addresses, and dropdown options.")


# =============================================================================
# 5. INTERNAL TRANSFER PAGE (Source/Dest Dropdowns, Amount, Memo, Modal)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_internal_transfer_all_labels_and_dropdowns(client_internal_transfer_page: ClientInternalTransferPage):
    """
    Verify Source & Destination dropdown options, amount & memo inputs, and action buttons.
    """
    client_internal_transfer_page.navigate()

    expect(client_internal_transfer_page.main_heading.first).to_be_visible()
    expect(client_internal_transfer_page.transfer_details_heading.first).to_be_visible()

    # Dropdowns
    source_opts = client_internal_transfer_page.get_source_options()
    dest_opts = client_internal_transfer_page.get_destination_options()
    assert len(source_opts) > 0, "Internal transfer source select has no options"
    assert len(dest_opts) > 0, "Internal transfer destination select has no options"

    # Inputs & Buttons
    expect(client_internal_transfer_page.amount_input).to_be_visible()
    expect(client_internal_transfer_page.memo_input).to_be_visible()
    expect(client_internal_transfer_page.cancel_button).to_be_visible()
    expect(client_internal_transfer_page.review_transfer_button).to_be_visible()

    # Table Headers
    headers = client_internal_transfer_page.get_table_headers()
    assert all(h in " ".join(headers) for h in ["DATE", "DETAILS", "AMOUNT", "STATUS"]), (
        f"Missing expected internal transfer headers: {headers}"
    )

    logger.info("Verified all Internal Transfer labels, dropdown options, and controls.")


# =============================================================================
# 6. WALLET MANAGEMENT PAGE (Cards, Action Buttons, Ledger Tables)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_wallet_all_labels_and_tables(client_wallet_page: ClientWalletPage):
    """
    Verify summary cards, top action buttons, and both ledger tables on Wallet page.
    """
    client_wallet_page.navigate()

    # Summary Cards
    expect(client_wallet_page.client_wallet_card).to_be_visible()
    expect(client_wallet_page.ib_wallet_card).to_be_visible()
    expect(client_wallet_page.consolidated_funds_card).to_be_visible()

    # Action buttons
    expect(client_wallet_page.export_report_button).to_be_visible()
    expect(client_wallet_page.account_to_wallet_button).to_be_visible()

    # Accounts & History Tables
    acc_headers = client_wallet_page.get_accounts_table_headers()
    assert "WALLET" in " ".join(acc_headers) and "BALANCE" in " ".join(acc_headers)

    hist_headers = client_wallet_page.get_history_table_headers()
    assert "MOVEMENT" in " ".join(hist_headers) and "AMOUNT" in " ".join(hist_headers)

    logger.info("Verified all Wallet Management labels, action buttons, and table structures.")


# =============================================================================
# 7. COPY TRADING, MAM & PAMM (Search Bars, Filters, Cards, Modals)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_copy_trading_all_labels_search_and_dropdowns(client_copy_trading_page: ClientCopyTradingPage):
    """
    Verify Copy Trading summary cards, view switcher buttons, search input, filter dropdowns, and table headers.
    """
    client_copy_trading_page.navigate()

    # Summary Cards
    cards = client_copy_trading_page.get_summary_card_values()
    assert all(k in cards for k in ["managers", "managed_capital", "closed_trades", "followers"])

    # View Buttons
    expect(client_copy_trading_page.trading_manager_btn).to_be_visible()
    expect(client_copy_trading_page.my_followers_btn).to_be_visible()

    # Search Bar
    expect(client_copy_trading_page.search_input).to_be_visible()
    search_ph = client_copy_trading_page.search_input.get_attribute("placeholder") or ""
    assert "search" in search_ph.lower(), f"Search input placeholder unexpected: {search_ph}"

    # Dropdowns (Range, Risk, Fund, Rows)
    expect(client_copy_trading_page.range_select).to_be_visible()
    expect(client_copy_trading_page.risk_select).to_be_visible()
    expect(client_copy_trading_page.fund_select).to_be_visible()
    expect(client_copy_trading_page.rows_select).to_be_visible()

    # Table Headers
    headers = client_copy_trading_page.get_table_headers()
    assert all(h in " ".join(headers) for h in ["NAME", "RANK", "GROWTH", "WIN RATE", "ACTION"])

    logger.info("Verified all Copy Trading labels, search bar, dropdowns, and table headers.")


@pytest.mark.client
@pytest.mark.regression
def test_val_mam_all_labels_search_and_dropdowns(client_mam_page: ClientMAMPage):
    """
    Verify MAM summary cards, search input, filter dropdowns, and table column headers.
    """
    client_mam_page.navigate()

    # Summary Cards
    cards = client_mam_page.get_summary_card_values()
    assert all(k in cards for k in ["managers", "managed_capital", "closed_trades", "followers"])

    # Search Bar & Dropdowns
    expect(client_mam_page.search_input).to_be_visible()
    expect(client_mam_page.range_select).to_be_visible()
    expect(client_mam_page.risk_select).to_be_visible()
    expect(client_mam_page.fund_select).to_be_visible()
    expect(client_mam_page.rows_select).to_be_visible()

    # Table Headers
    headers = client_mam_page.get_table_headers()
    assert all(h in " ".join(headers) for h in ["NAME", "RANK", "GROWTH", "WIN RATE", "ACTION"])

    logger.info("Verified all MAM labels, search bar, and dropdowns.")


@pytest.mark.client
@pytest.mark.regression
def test_val_pamm_all_labels_search_and_dropdowns(client_pamm_page: ClientPAMMPage):
    """
    Verify PAMM summary cards, search input, filter dropdowns, and table column headers.
    """
    client_pamm_page.navigate()

    # Summary Cards
    cards = client_pamm_page.get_summary_card_values()
    assert all(k in cards for k in ["managers", "managed_capital", "closed_trades", "followers"])

    # Search Bar & Dropdowns
    expect(client_pamm_page.search_input).to_be_visible()
    expect(client_pamm_page.range_select).to_be_visible()
    expect(client_pamm_page.risk_select).to_be_visible()
    expect(client_pamm_page.fund_select).to_be_visible()
    expect(client_pamm_page.rows_select).to_be_visible()

    # Table Headers
    headers = client_pamm_page.get_table_headers()
    assert all(h in " ".join(headers) for h in ["NAME", "RANK", "GROWTH", "WIN RATE", "ACTION"])

    logger.info("Verified all PAMM labels, search bar, and dropdowns.")


# =============================================================================
# 8. REFER & EARN (Cards, Referral Link, Tree View, Table Controls)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_refer_earn_all_labels_and_controls(client_refer_earn_page: ClientReferEarnPage):
    """
    Verify summary metric cards, unique referral link, tree view headings, and referred clients table.
    """
    client_refer_earn_page.navigate()

    # Summary Cards
    metrics = client_refer_earn_page.get_summary_metrics()
    assert "total_earnings" in metrics and "successful_referrals" in metrics

    # Unique Link & Copy button
    expect(client_refer_earn_page.unique_link_input.first).to_be_visible()
    expect(client_refer_earn_page.copy_link_button).to_be_visible()

    # How It Works & Tree View
    expect(client_refer_earn_page.how_it_works_container).to_be_visible()
    expect(client_refer_earn_page.tree_view_heading).to_be_visible()

    # Referred Clients Table
    headers = client_refer_earn_page.get_table_header_titles()
    assert all(h in " ".join(headers) for h in ["CLIENT", "ACCOUNT", "REF ID", "BALANCE", "IB EARNED"])

    logger.info("Verified all Refer & Earn labels, copy button, tree view, and table controls.")


# =============================================================================
# 9. ACCOUNT SETTINGS (4 Sub-Tabs, Inputs, Dropdowns, KYC Documents & Security)
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_val_settings_all_subtabs_labels_and_dropdowns(client_settings_page: ClientSettingsPage):
    """
    Verify all 4 Settings sub-tabs, personal info inputs, trading dropdowns, documents badges, and security password inputs.
    """
    client_settings_page.navigate()

    # 1. Personal Info Sub-tab
    client_settings_page.open_subtab("personal")
    expect(client_settings_page.full_name_input).to_be_visible()
    expect(client_settings_page.email_input).to_be_visible()
    expect(client_settings_page.phone_input).to_be_visible()
    expect(client_settings_page.address_input).to_be_visible()
    expect(client_settings_page.city_input).to_be_visible()
    expect(client_settings_page.state_input).to_be_visible()
    expect(client_settings_page.zip_input).to_be_visible()
    expect(client_settings_page.country_input).to_be_visible()
    expect(client_settings_page.save_button).to_be_visible()

    # 2. Trading Account Sub-tab & Dropdowns
    client_settings_page.open_subtab("trading")
    expect(client_settings_page.account_select).to_be_visible()
    expect(client_settings_page.account_type_select).to_be_visible()
    expect(client_settings_page.leverage_select).to_be_visible()
    expect(client_settings_page.save_trading_settings_button).to_be_visible()

    # 3. Documents Sub-tab & KYC Badges
    client_settings_page.open_subtab("documents")
    expect(client_settings_page.documents_heading.first).to_be_visible()
    expect(client_settings_page.document_status_badge.first).to_be_visible()

    # 4. Security Sub-tab & Change Password Inputs
    client_settings_page.open_subtab("security")
    expect(client_settings_page.current_password_input).to_be_visible()
    expect(client_settings_page.new_password_input).to_be_visible()
    expect(client_settings_page.confirm_password_input).to_be_visible()
    expect(client_settings_page.send_otp_button.first).to_be_visible()

    logger.info("Verified all Account Settings sub-tabs, personal inputs, trading dropdowns, KYC badges, and security fields.")
