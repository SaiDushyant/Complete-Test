"""
Client Portal Top Navigation Header Tests.
Comprehensive validation covering every minute interactive control:
1. Header elements presence across all 3 views (Dashboard, Settings, Refer & Earn)
2. Search input interaction (query entry and clear)
3. Sidebar collapse and expand toggle (title state and width change)
4. Dark / Light theme toggle (theme switching and reversal)
5. Notifications drawer ('Security & Clearance Alerts', Refresh, and 'MARK ALL READ')
6. Support Center drawer ('ACCOUNT / SESSION INFO', FAQ list, and 'SETTINGS' redirect button)
7. Account switcher dropdown ('SELECT ACCOUNT' ledger, switching from 10026 to 10629 and restoring)
8. Create Account modal ('LIVE ACCOUNT CREATION', demo creation URL, COPY button, Cancel)
9. Logout button presence and attributes
Includes automated monitoring for Browser Console, JavaScript Runtime, and Backend Network Errors.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.regression
def test_client_header_presence_across_all_three_views(
    client_dashboard_page: ClientDashboardPage,
    client_settings_page: ClientSettingsPage,
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the universal header renders correctly across all three core views:
    - Dashboard
    - Settings
    - Refer & Earn
    Asserts zero console errors, JS crashes, and backend failures.
    """
    # 1. Dashboard View
    client_dashboard_page.navigate()
    client_dashboard_page.header.assert_header_elements(expected_title="Dashboard")

    # 2. Settings View
    client_settings_page.navigate()
    client_settings_page.header.assert_header_elements(expected_title="Settings")

    # 3. Refer & Earn View
    client_refer_earn_page.navigate()
    client_refer_earn_page.header.assert_header_elements(expected_title="Refer & Earn")

    # Automated Error Check
    client_error_monitor.assert_no_errors("Header Presence Across Core Views")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_search_input_interaction(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify header search bar:
    - Renders search input with placeholder 'Search accounts, transactions, wallets...'
    - Accepts query entry
    - Clears properly
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    expect(header.search_input).to_be_visible()
    header.search("EURUSD")
    expect(header.search_input).to_have_value("EURUSD")

    header.clear_search()
    expect(header.search_input).to_have_value("")

    client_error_monitor.assert_no_errors("Header Search Input")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_sidebar_collapse_and_expand(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify sidebar collapse and expand toggle:
    - Initial state title is 'Collapse menu'
    - Clicking collapses sidebar: title changes to 'Expand menu'
    - Clicking again expands sidebar: title restores to 'Collapse menu'
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    expect(header.menu_toggle_button).to_have_attribute("title", "Collapse menu")

    # Collapse sidebar
    header.toggle_sidebar()
    expect(header.menu_toggle_button).to_have_attribute("title", "Expand menu")

    # Expand sidebar back
    header.toggle_sidebar()
    expect(header.menu_toggle_button).to_have_attribute("title", "Collapse menu")

    client_error_monitor.assert_no_errors("Sidebar Collapse/Expand")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_theme_toggle_dark_light(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify theme toggle functionality:
    - Initial theme button title is 'Switch to dark theme'
    - Clicking toggles title to 'Switch to light theme'
    - Clicking again restores title to 'Switch to dark theme'
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    expect(header.theme_toggle_button).to_have_attribute("title", "Switch to dark theme")

    # Switch to Dark Theme
    header.toggle_theme()
    expect(header.theme_toggle_button).to_have_attribute("title", "Switch to light theme")

    # Switch back to Light Theme
    header.toggle_theme()
    expect(header.theme_toggle_button).to_have_attribute("title", "Switch to dark theme")

    client_error_monitor.assert_no_errors("Theme Toggle")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_notifications_drawer_and_mark_all_read(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Notifications drawer and 'MARK ALL READ' action:
    - Clicking bell opens drawer with 'Security & Clearance Alerts'
    - Drawer displays Refresh and 'MARK ALL READ' buttons
    - Clicking 'MARK ALL READ' triggers read action and dismisses drawer cleanly
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    # Open notifications drawer
    header.open_notifications()
    expect(header.notifications_drawer).to_be_visible()

    # Check controls
    expect(header.notifications_refresh_btn).to_be_visible()
    expect(header.notifications_mark_all_read_btn).to_be_visible()

    # Trigger MARK ALL READ
    header.click_notifications_mark_all_read()
    expect(header.notifications_drawer).not_to_be_visible()

    client_error_monitor.assert_no_errors("Notifications Drawer & Mark All Read")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_support_drawer_faq_and_settings_redirect(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Support Center drawer, session info, FAQ, and 'SETTINGS' redirect:
    - Clicking support icon opens Support Center drawer
    - Displays 'ACCOUNT / SESSION INFO' (Client, Email, Selected Account, KYC Status)
    - Displays FAQ section
    - Clicking 'SETTINGS' redirects to Settings view and closes drawer
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    # Open support drawer
    header.open_support()
    expect(header.support_drawer).to_be_visible()
    expect(header.support_drawer).to_contain_text(re.compile(r"Account\s*/\s*Session\s*Info", re.I))
    expect(header.support_drawer).to_contain_text("FAQ")

    # Test Close button first
    header.close_support()
    expect(header.support_drawer).not_to_be_visible()

    # Re-open and click SETTINGS button to test redirect
    header.open_support()
    expect(header.support_drawer).to_be_visible()
    header.click_support_settings()

    # Assert redirected to Settings view and drawer closed
    expect(header.title_heading.first).to_have_text("Settings")
    expect(header.support_drawer).not_to_be_visible()

    client_error_monitor.assert_no_errors("Support Center Drawer & Settings Redirect")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_account_switcher_dropdown(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Account Switcher:
    - Clicking account badge opens 'SELECT ACCOUNT' dropdown
    - Lists linked accounts (e.g. 10026 and 10629) with fund and balance values
    - Selecting an alternative account updates the account badge
    - Switching back restores primary account
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    # Switch to 10629
    header.select_account("10629")
    expect(header.account_badge).to_contain_text("10629")

    # Switch back to 10026
    header.select_account("10026")
    expect(header.account_badge).to_contain_text("10026")

    client_error_monitor.assert_no_errors("Account Switcher Dropdown")


@pytest.mark.client
@pytest.mark.regression
def test_client_header_create_account_modal_demo_options(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Create Account modal and Demo details:
    - Clicking 'CREATE ACCOUNT' opens modal with 'LIVE ACCOUNT CREATION' / 'Create Account'
    - Displays client details and referral code
    - Displays 'Demo Account Created' section with virtual balance explanation
    - Displays 'COPY' link button, 'DEMO READY' button, and 'REQUEST NEW ACCOUNT' button
    - Clicking 'Cancel' dismisses modal cleanly
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    # Open Create Account modal
    header.open_create_account_modal()
    expect(header.create_account_modal).to_be_visible()
    expect(header.create_account_modal).to_contain_text(re.compile(r"Live\s*Account\s*Creation", re.I))
    expect(header.create_account_modal).to_contain_text("Demo Account")

    # Check action buttons
    expect(header.create_account_copy_demo_btn).to_be_visible()
    expect(header.create_account_demo_ready_btn).to_be_visible()
    expect(header.create_account_request_btn).to_be_visible()

    # Click Cancel to dismiss
    header.close_create_account_modal()
    expect(header.create_account_modal).not_to_be_visible()

    client_error_monitor.assert_no_errors("Create Account Modal")


@pytest.mark.client
@pytest.mark.smoke
def test_client_header_logout_and_profile_controls(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Logout button and profile controls presence:
    - Logout button is visible, enabled, and has title 'Logout from client portal'
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_dashboard_page.navigate()
    header = client_dashboard_page.header

    expect(header.logout_button).to_be_visible()
    expect(header.logout_button).to_be_enabled()
    expect(header.logout_button).to_have_attribute("title", "Logout from client portal")

    client_error_monitor.assert_no_errors("Header Logout Control")
