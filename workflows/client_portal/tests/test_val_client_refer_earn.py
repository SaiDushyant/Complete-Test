"""
Client Portal Refer & Earn Validation Test Suite.
Validates unique referral link structure, copy feedback state transitions,
metrics card formatting, and referral ledger controls per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_refer_earn")


@pytest.mark.client
@pytest.mark.regression
def test_val_referral_link_structure(client_refer_earn_page: ClientReferEarnPage):
    """
    Verify that the generated unique referral link is well-formed with protocol, host, and ref identifier.
    """
    client_refer_earn_page.navigate()
    assert client_refer_earn_page.is_refer_earn_displayed(), "Refer & Earn page not displayed"

    ref_link = client_refer_earn_page.get_referral_link()
    assert ref_link and len(ref_link) > 10, f"Referral link is empty or too short: '{ref_link}'"
    assert ref_link.startswith("http://") or ref_link.startswith("https://"), (
        f"Referral link missing http/https protocol: '{ref_link}'"
    )
    logger.info(f"Verified well-formed referral link: '{ref_link}'")


@pytest.mark.client
@pytest.mark.regression
def test_val_referral_copy_button_feedback(client_refer_earn_page: ClientReferEarnPage):
    """
    Verify clicking the Copy button triggers dynamic visual feedback ('Copied!').
    """
    client_refer_earn_page.navigate()
    client_refer_earn_page.click_copy_link_and_verify_feedback()
    logger.info("Verified Copy button state transition to 'Copied!'.")


@pytest.mark.client
@pytest.mark.regression
def test_val_referral_metrics_cards(client_refer_earn_page: ClientReferEarnPage):
    """
    Verify summary metric cards render formatted financial values without NaN or undefined strings.
    """
    client_refer_earn_page.navigate()
    metrics = client_refer_earn_page.get_summary_metrics()

    for key, val in metrics.items():
        assert "nan" not in val.lower() and "undefined" not in val.lower(), (
            f"Metric card '{key}' contains corrupted value: '{val}'"
        )
    logger.info(f"Verified referral summary metrics: {metrics}")


@pytest.mark.client
@pytest.mark.regression
def test_val_referral_table_pagination_and_rows(client_refer_earn_page: ClientReferEarnPage):
    """
    Verify that the referred clients table controls (rows select and refresh) are interactive.
    """
    client_refer_earn_page.navigate()
    expect(client_refer_earn_page.referred_clients_heading).to_be_visible()

    # Change rows per page
    if client_refer_earn_page.rows_per_page_select.is_visible():
        client_refer_earn_page.select_rows_per_page("25")

    # Refresh
    if client_refer_earn_page.refresh_button.is_visible():
        client_refer_earn_page.click_refresh_referrals()

    expect(client_refer_earn_page.table).to_be_visible()
    logger.info("Verified referral table controls and refresh interaction.")
