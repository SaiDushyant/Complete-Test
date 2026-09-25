"""
Client Portal Watchlist Workflow Tests.
Validates instrument symbol tabs and watchlist interaction for Client Portal.
Maintained by Developer 3 (Client Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_watchlist_page import ClientWatchlistPage


@pytest.mark.client
@pytest.mark.regression
def test_client_watchlist_symbols_tab(client_watchlist_page: ClientWatchlistPage):
    """
    Verify that an authenticated client can access and view the watchlist symbols tab.
    Preserves and standardizes the behavioral session validation on Client Portal.
    """
    client_watchlist_page.open_all_symbols()

    symbols_count = client_watchlist_page.page.locator(".watchlist-tab[data-info='symbols']").count()
    assert symbols_count > 0, (
        "Expected at least one '.watchlist-tab[data-info=\"symbols\"]' element on Client Portal watchlist."
    )
