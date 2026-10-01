"""
Client Portal Conftest.
Automatically loads shared browser fixtures, portal fixtures, error monitoring, and dedicated reporting.
"""

import pytest

from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

from workflows.client_portal.fixtures.client_fixtures import (
    authenticated_client_context,
    authenticated_client_page,
    client_copy_trading_page,
    client_dashboard_page,
    client_deposit_page,
    client_error_monitor,
    client_header,
    client_internal_transfer_page,
    client_login_page,
    client_mam_page,
    client_page,
    client_pamm_page,
    client_profile_page,
    client_refer_earn_page,
    client_settings_page,
    client_sidebar,
    client_wallet_page,
    client_withdraw_page,
)


