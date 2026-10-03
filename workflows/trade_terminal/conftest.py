"""
Trade Terminal Portal Conftest.
Automatically loads shared browser fixtures and portal-specific fixtures.
"""

# Import shared browser fixtures
from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

# Import trade terminal portal fixtures
from workflows.trade_terminal.fixtures.trade_fixtures import (
    api_access_page,
    authenticated_trade_context,
    authenticated_trade_page,
    blacktrader_chart_page,
    history_page,
    navigation_bar_page,
    order_entry_page,
    positions_page,
    profile_menu_page,
    trade_error_monitor,
    trade_login_page,
    trade_page,
    trading_chart_page,
    trading_dashboard_page,
    tradingview_chart_page,
    watchlist_page,
)


