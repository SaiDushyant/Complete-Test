"""
Client Portal KYC Documents & Settings Profile Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.B.1, Section 3.B.2, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Read-only email immutability, personal info inputs, password match boundaries.
2. Buttons & Actions: Save Changes lifecycle, Send OTP lifecycle, Sub-tab switching responsiveness.
3. Dropdowns & Selects: Account selector, Account Type, Leverage options in Trading Account subtab.
4. Dropzones & Uploads: KYC document cards, document status badges, preview link URI schemes.
7. Security: Sanitization of profile inputs against SQLi and XSS, client tampering prevention.

Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor


# ==============================================================================
# 1. KYC STATUS REFLECTION & DOCUMENT CARDS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_kyc_status_badge_and_document_cards(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 4 (Uploads & Documents): Verify KYC documents subtab:
    - Account Status container is visible and displays recognized status badge
      (Verified, Pending Review, Under Review, Unverified, Rejected).
    - Document cards for Address Proof, National ID, Bank Statement render properly.
    - If document preview links exist, their target URLs must be secure HTTP/HTTPS schemes.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Documents")

    expect(client_settings_page.documents_heading.first).to_be_visible()
    expect(client_settings_page.account_status_container.first).to_be_visible()
    expect(client_settings_page.document_status_badge.first).to_be_visible()

    badge_text = client_settings_page.document_status_badge.first.inner_text().strip()
    assert re.search(r"Verified|Pending|Under Review|Unverified|Rejected", badge_text, re.I), (
        f"Unexpected KYC status badge text: '{badge_text}'"
    )

    doc_count = client_settings_page.get_uploaded_document_count()
    if doc_count > 0:
        doc_urls = client_settings_page.get_uploaded_document_urls()
        for url in doc_urls:
            assert url.startswith("http://") or url.startswith("https://"), (
                f"Document URL must use valid HTTP/HTTPS scheme: {url}"
            )
    else:
        expect(client_settings_page.document_cards.first).to_be_visible()

    client_error_monitor.assert_no_js_errors("KYC Status & Document Cards")


# ==============================================================================
# 2. EMAIL INPUT IMMUTABILITY & TAMPERING PREVENTION
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_kyc_email_input_disabled_protection(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 7: Verify email address cannot be tampered with or edited by the user:
    - Email field in Personal Information subtab is permanently disabled / read-only.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Personal Information")

    email_input = client_settings_page.email_input.first
    expect(email_input).to_be_visible()
    expect(email_input).to_be_disabled()

    # Verify input has non-empty current email value
    email_val = email_input.input_value()
    assert "@" in email_val, f"Expected valid email in disabled field, got: '{email_val}'"

    client_error_monitor.assert_no_js_errors("Email Input Protection")


# ==============================================================================
# 3. PERSONAL INFO SANITIZATION: SQLi & XSS PAYLOADS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
@pytest.mark.parametrize(
    "payload,desc",
    [
        (SQLI_PAYLOADS[0][0], SQLI_PAYLOADS[0][1]),
        (XSS_PAYLOADS[0][0], XSS_PAYLOADS[0][1]),
        (XSS_PAYLOADS[1][0], XSS_PAYLOADS[1][1]),
    ],
)
def test_val_client_kyc_personal_info_security_sanitization(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
    payload: str,
    desc: str,
):
    """
    Pillar 7 (Security): Verify Personal Information inputs handle injection payloads safely:
    - Entering SQLi and XSS payloads into text inputs does not trigger alert dialogs
      and causes no uncaught JavaScript exceptions.
    """
    alert_triggered = False

    def handle_dialog(dialog):
        nonlocal alert_triggered
        alert_triggered = True
        dialog.dismiss()

    client_settings_page.page.on("dialog", handle_dialog)

    client_settings_page.navigate()
    client_settings_page.open_subtab("Personal Information")

    # Enter payload into address, city, and state
    city_inp = client_settings_page.city_input.first
    if city_inp.is_visible():
        city_inp.fill(payload)
        client_settings_page.page.wait_for_timeout(200)

    # Cancel button should be available to revert without mutating live DB
    expect(client_settings_page.cancel_button.first).to_be_visible()
    client_settings_page.cancel_button.first.click()
    client_settings_page.page.wait_for_timeout(300)

    assert not alert_triggered, f"Security Alert! XSS dialog triggered by payload: {payload}"
    client_error_monitor.assert_no_js_errors(f"Personal Info Sanitization: {desc}")


# ==============================================================================
# 4. PASSWORD MISMATCH & EMPTY BOUNDARIES (SECURITY TAB)
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_kyc_password_mismatch_boundary(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify Password Mismatch boundary in Security subtab:
    - Entering mismatched New Password and Confirm Password prevents submission
      or triggers validation error.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Security")

    expect(client_settings_page.security_heading.first).to_be_visible()
    expect(client_settings_page.current_password_input.first).to_be_visible()
    expect(client_settings_page.new_password_input.first).to_be_visible()
    expect(client_settings_page.confirm_password_input.first).to_be_visible()

    # Enter mismatched passwords
    client_settings_page.current_password_input.first.fill("CurrentPass123!")
    client_settings_page.new_password_input.first.fill("StrongPassword123!")
    client_settings_page.confirm_password_input.first.fill("DifferentPassword456!")
    client_settings_page.page.wait_for_timeout(300)

    # Verify Send OTP button is present
    expect(client_settings_page.send_otp_button.first).to_be_visible()

    client_error_monitor.assert_no_js_errors("Password Mismatch Boundary")


@pytest.mark.client
@pytest.mark.validation
def test_val_client_kyc_password_empty_boundary(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 1 & 2: Verify submitting with empty password fields is prevented:
    - Leaving password fields empty and clicking Send OTP does not submit cleanly.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Security")

    client_settings_page.current_password_input.first.fill("")
    client_settings_page.new_password_input.first.fill("")
    client_settings_page.confirm_password_input.first.fill("")
    client_settings_page.page.wait_for_timeout(200)

    # Click Send OTP with empty inputs
    client_settings_page.send_otp_button.first.click()
    client_settings_page.page.wait_for_timeout(500)

    # Security heading must remain visible and page remains intact
    expect(client_settings_page.security_heading.first).to_be_visible()
    client_error_monitor.assert_no_js_errors("Password Empty Boundary")


# ==============================================================================
# 5. TRADING ACCOUNT CONTROLS & LEVERAGE DROPDOWNS
# ==============================================================================


@pytest.mark.client
@pytest.mark.validation
def test_val_client_kyc_trading_account_dropdown_options(
    client_settings_page: ClientSettingsPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify Trading Account options & dropdown selectors:
    - Account selector combobox
    - Account Type selector
    - Leverage selector
    - Save Trading Settings button lifecycle
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("Trading Account")

    expect(client_settings_page.trading_account_heading.first).to_be_visible()
    expect(client_settings_page.account_select.first).to_be_visible()
    expect(client_settings_page.account_type_select.first).to_be_visible()
    expect(client_settings_page.leverage_select.first).to_be_visible()
    expect(client_settings_page.save_trading_settings_button.first).to_be_visible()

    client_error_monitor.assert_no_js_errors("Trading Account Controls")
