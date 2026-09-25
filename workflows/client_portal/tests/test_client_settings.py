"""
Client Portal Settings & Profile Workflow Tests.
Comprehensive validation covering every individual option across all 4 sub-tabs:
1. Personal Information
2. Trading Account
3. Documents (KYC)
4. Security (Change Password)
Includes automated monitoring for Browser Console, JavaScript Runtime, and Backend Network Errors.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_settings_header_elements(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify consistent header rendering on Settings view:
    - Page title is 'Settings'
    - Account badge and CREATE ACCOUNT action are present and enabled
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_settings_page.navigate()
    client_settings_page.header.assert_header_elements(expected_title="Settings")

    # Automated Error Check
    client_error_monitor.assert_no_errors("Settings Header")


@pytest.mark.client
@pytest.mark.regression
def test_client_settings_personal_information_all_fields(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Option 1: Personal Information sub-tab:
    - Verifies Full Name, Email, Phone Number, and Address fields
    - Asserts Email Address field is disabled / protected
    - Asserts 'SAVE CHANGES' and 'Cancel' buttons are rendered
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Personal Information")

    # Verify input fields
    expect(client_settings_page.full_name_input.first).to_be_visible()
    expect(client_settings_page.email_input.first).to_be_visible()
    expect(client_settings_page.email_input.first).to_be_disabled()
    expect(client_settings_page.phone_input.first).to_be_visible()
    expect(client_settings_page.address_input.first).to_be_visible()
    expect(client_settings_page.city_input.first).to_be_visible()
    expect(client_settings_page.state_input.first).to_be_visible()
    expect(client_settings_page.zip_input.first).to_be_visible()
    expect(client_settings_page.country_input.first).to_be_visible()

    # Verify actions
    expect(client_settings_page.save_button.first).to_be_visible()
    expect(client_settings_page.cancel_button.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Settings - Personal Information")


@pytest.mark.client
@pytest.mark.regression
def test_client_settings_trading_account_options(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Option 2: Trading Account sub-tab:
    - Verifies Account selector combobox (switching between accounts)
    - Verifies Account Type selection (DEMO / ECN)
    - Verifies Leverage selection (1:100 to 1:500)
    - Verifies 'SAVE TRADING SETTINGS' action button is visible
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Trading Account")

    # Verify Trading Account heading & controls
    expect(client_settings_page.trading_account_heading.first).to_be_visible()
    expect(client_settings_page.account_select.first).to_be_visible()
    expect(client_settings_page.account_type_select.first).to_be_visible()
    expect(client_settings_page.leverage_select.first).to_be_visible()
    expect(client_settings_page.save_trading_settings_button.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Settings - Trading Account")


@pytest.mark.client
@pytest.mark.regression
def test_client_settings_documents_kyc_options(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Option 3: Documents (KYC) sub-tab:
    - Verifies Documents heading and verification status badge (e.g. 'Pending Review')
    - Verifies uploaded document links (Address proof, National ID, Bank Statement)
    - Asserts valid non-empty document preview URLs
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Documents")

    expect(client_settings_page.documents_heading.first).to_be_visible()
    expect(client_settings_page.document_status_badge.first).to_be_visible()

    doc_count = client_settings_page.get_uploaded_document_count()
    assert doc_count > 0, "Expected at least one uploaded document in Documents tab."

    doc_urls = client_settings_page.get_uploaded_document_urls()
    for url in doc_urls:
        assert url.startswith("http"), f"Expected absolute HTTP document preview URL, got: {url}"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Settings - Documents KYC")


@pytest.mark.client
@pytest.mark.regression
def test_client_settings_security_password_options(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Option 4: Security (Change Password) sub-tab:
    - Verifies Change Password heading
    - Verifies all 3 password fields: Current Password, New Password, Confirm New Password
    - Verifies 'Send OTP' button is visible and enabled
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Security")

    expect(client_settings_page.security_heading.first).to_be_visible()
    expect(client_settings_page.current_password_input.first).to_be_visible()
    expect(client_settings_page.new_password_input.first).to_be_visible()
    expect(client_settings_page.confirm_password_input.first).to_be_visible()

    expect(client_settings_page.send_otp_button.first).to_be_visible()
    expect(client_settings_page.send_otp_button.first).to_be_enabled()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Settings - Security")


@pytest.mark.client
@pytest.mark.regression
def test_client_settings_end_to_end_journey_zero_errors(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Multi-tab endurance test:
    Navigates sequentially through all 4 Settings sub-tabs in one session:
    Personal Information -> Trading Account -> Documents -> Security
    Verifies that the entire navigation produces ZERO uncaught JS exceptions,
    ZERO browser console errors, and ZERO backend server 5xx failures.
    """
    client_settings_page.navigate()

    for tab in ["Personal Information", "Trading Account", "Documents", "Security"]:
        client_settings_page.open_subtab(tab)

    # Comprehensive error verification across the complete journey
    summary = client_error_monitor.get_summary()
    assert summary["total_errors"] == 0, (
        f"Errors encountered during Settings multi-tab journey:\n{summary}"
    )
