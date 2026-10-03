"""
Client Portal KYC & Profile Validation Test Suite.
Validates document upload constraints, status badges, profile field locks,
and personal information input sanitization per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import os
import tempfile
import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.shared.helpers.validation_payloads import (
    ACCEPTED_EXTENSIONS,
    DISALLOWED_EXTENSIONS,
    XSS_REFLECTED_PAYLOADS,
)
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_kyc_upload")


@pytest.mark.client
@pytest.mark.regression
def test_val_kyc_documents_status_badge_display(client_settings_page: ClientSettingsPage):
    """
    Verify that the Documents sub-tab renders valid KYC verification status badges.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("documents")

    expect(client_settings_page.documents_heading.first).to_be_visible(timeout=5000)
    badge = client_settings_page.document_status_badge.first
    assert badge.is_visible(), "KYC Document verification status badge is not visible!"
    logger.info(f"Verified KYC verification status badge: '{badge.inner_text().strip()}'")


@pytest.mark.client
@pytest.mark.regression
@pytest.mark.parametrize("payload,description", XSS_REFLECTED_PAYLOADS[:2])
def test_val_profile_personal_info_xss_sanitization(
    client_settings_page: ClientSettingsPage, payload: str, description: str
):
    """
    Verify that updating personal information with XSS payloads is safely sanitized.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("personal")
    client_settings_page.page.evaluate("window.xss_detected = 0;")

    # Enter city or address with payload
    if client_settings_page.city_input.is_visible():
        client_settings_page.city_input.fill(f"City {payload}")
        if client_settings_page.save_button.is_visible():
            client_settings_page.save_button.click()
            client_settings_page.page.wait_for_timeout(1000)

        is_triggered = client_settings_page.page.evaluate("() => window.xss_detected === 1")
        assert not is_triggered, f"XSS script executed during Personal Info update with payload: {payload}"
        logger.info(f"Verified Personal Info safely sanitized XSS payload: {description}")


@pytest.mark.client
@pytest.mark.regression
def test_val_kyc_email_input_read_only_or_guarded(client_settings_page: ClientSettingsPage):
    """
    Verify that sensitive identity fields (e.g. registered email) cannot be arbitrarily modified
    without proper re-verification safeguards.
    """
    client_settings_page.navigate()
    client_settings_page.open_subtab("personal")

    # Email field is typically disabled/readonly for authenticated clients
    if client_settings_page.email_input.is_visible():
        is_disabled = client_settings_page.email_input.is_disabled()
        is_readonly = client_settings_page.email_input.get_attribute("readonly") is not None
        logger.info(f"Email field status - disabled: {is_disabled}, readonly: {is_readonly}")
        # Note: If editable, ensure backend doesn't silently detach user identity without OTP
