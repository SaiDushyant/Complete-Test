"""
Client Portal Wallet Validation Test Suite.
Validates summary card metrics, account-to-wallet routing, and transaction ledger controls
per VALIDATION_TESTING_SPECIFICATION.md.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.client_portal.pages.client_wallet_page import ClientWalletPage
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_val_client_wallet")

pytestmark = [pytest.mark.client, pytest.mark.validation]


@pytest.mark.client
@pytest.mark.regression
def test_val_wallet_summary_cards(client_wallet_page: ClientWalletPage):
    """
    Verify that Wallet Management summary cards (Client Wallet, IB Wallet) render with valid balance values.
    """
    client_wallet_page.navigate()
    assert client_wallet_page.is_wallet_displayed(), "Wallet page not displayed"

    expect(client_wallet_page.client_wallet_card).to_be_visible()
    expect(client_wallet_page.ib_wallet_card).to_be_visible()

    client_text = client_wallet_page.client_wallet_card.inner_text()
    ib_text = client_wallet_page.ib_wallet_card.inner_text()

    assert "nan" not in client_text.lower() and "undefined" not in client_text.lower(), (
        f"Client Wallet card contains corrupted text: '{client_text}'"
    )
    assert "nan" not in ib_text.lower() and "undefined" not in ib_text.lower(), (
        f"IB Wallet card contains corrupted text: '{ib_text}'"
    )
    logger.info("Verified Wallet summary cards display cleanly without corrupted values.")


@pytest.mark.client
@pytest.mark.regression
def test_val_wallet_account_to_wallet_navigation(client_wallet_page: ClientWalletPage):
    """
    Verify clicking 'ACCOUNT TO WALLET' action button navigates to Internal Transfer or opens transfer drawer.
    """
    client_wallet_page.navigate()
    client_wallet_page.click_account_to_wallet()

    # Should land on Internal Transfer page or display internal transfer form
    client_wallet_page.page.wait_for_timeout(1000)
    has_transfer_context = (
        "transfer" in client_wallet_page.page.url.lower()
        or client_wallet_page.internal_transfer_heading.is_visible()
        or client_wallet_page.page.locator("text=/internal transfer|transfer details/i").is_visible()
    )
    assert has_transfer_context, "Clicking ACCOUNT TO WALLET failed to navigate to transfer interface!"
    logger.info("Verified ACCOUNT TO WALLET navigation action.")


@pytest.mark.client
@pytest.mark.regression
def test_val_wallet_history_table_controls(client_wallet_page: ClientWalletPage):
    """
    Verify Wallet Accounts and Transfer History tables render valid column headers and row selectors.
    """
    client_wallet_page.navigate()
    accounts_headers = client_wallet_page.get_accounts_table_headers()
    assert len(accounts_headers) > 0, "Wallet Accounts table missing headers"

    history_headers = client_wallet_page.get_history_table_headers()
    assert len(history_headers) > 0, "Wallet Transfer History table missing headers"

    if client_wallet_page.history_rows_select.is_visible():
        client_wallet_page.select_history_rows_per_page("25")

    logger.info(f"Verified Wallet table headers: Accounts={accounts_headers}, History={history_headers}")
