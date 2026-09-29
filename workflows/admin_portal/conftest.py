"""
Admin Portal Conftest.
Automatically loads shared browser fixtures and portal-specific fixtures.
"""

from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

from workflows.admin_portal.fixtures.admin_fixtures import (
    admin_active_users_page,
    admin_cron_jobs_page,
    admin_dashboard_page,
    admin_login_page,
    admin_oxapay_page,
    admin_order_edit_log_page,
    admin_page,
    admin_settings_page,
    admin_symbol_configuration_page,
    admin_symbol_list_page,
    admin_user_group_page,
    admin_user_bonus_page,
    admin_user_transaction_log_page,
    admin_user_order_report_page,
    admin_refer_report_page,
    admin_lp_execution_config_page,
    authenticated_admin_context,
    authenticated_admin_page,
    user_management_page,
)
import inspect
from datetime import datetime

import pytest

from config.settings import settings
from workflows.shared.utils.screenshot import sanitize_filename

REPORT_DIR = settings.workflow_reports_dir / "admin_portal"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_REPORT = REPORT_DIR / "admin_portal_test_report.txt"


def _latest_failure_screenshot(test_name: str):
    clean_name = sanitize_filename(test_name)
    screenshots = sorted(settings.screenshots_dir.glob(f"{clean_name}_failure_*.png"))
    if screenshots:
        return str(screenshots[-1])
    return None

def _get_test_meaning(item):
    test_name = item.name

    readable_map = {
        "test_admin_settings_page_renders_expected_fields": (
            "This test checks whether the Admin Settings page loads with the required fields and buttons visible."
        ),
        "test_admin_can_update_basic_project_settings": (
            "This test verifies that an admin can enter project details and submit the settings form successfully."
        ),
        "test_admin_settings_page_renders_all_elements": (
            "This test checks whether the full Admin Settings page displays every expected field and control."
        ),
        "test_admin_settings_submit_returns_success_status_mocked": (
            "This test validates that valid settings submission returns a success response."
        ),
        "test_admin_settings_invalid_user_limit_returns_error_status_mocked": (
            "This test verifies that invalid input, such as a bad user limit, is rejected with an error response."
        ),
        "test_admin_settings_publish_maintenance_button_is_clickable": (
            "This test checks whether the maintenance publish action is clickable and responds correctly."
        ),
        "test_admin_settings_switches_are_interactable": (
            "This test checks whether the Admin Settings page lets the user switch the visibility setting and the cent account switch on and off correctly."
        ),
        "test_admin_settings_logo_upload_control_exists": (
            "This test checks whether the logo upload field is available for selecting an image file."
        ),
        "test_admin_cron_jobs_page_renders_table_and_columns": (
    "This test checks whether the Cron Jobs page loads the job table and the required schedule columns."
),
"test_admin_cron_jobs_modal_opens_with_expected_fields": (
    "This test checks whether the Cron Jobs edit modal opens and shows the expected form fields without changing any job data."
),
"test_admin_cron_jobs_mocked_success_response_when_save_clicked": (
    "This test verifies the mocked save flow for the Cron Jobs form without modifying the live admin configuration."
),
"test_admin_cron_jobs_mocked_error_response_when_save_clicked": (
    "This test verifies that a mocked validation failure is handled correctly without making any live admin changes."
),
    }

    return readable_map.get(test_name, "This test checks the basic Admin Settings page behavior and confirms the expected result.")


def _append_summary_report(text: str, report_path=SUMMARY_REPORT):
    with report_path.open("a", encoding="utf-8") as report_file:
        report_file.write(text + "\n\n")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call":
        return

    is_cron_jobs_test = item.path.name == "test_admin_cron_jobs_page.py"
    is_lp_config_test = item.path.name == "test_admin_lp_execution_config_page.py"
    is_oxapay_test = item.path.name == "test_admin_oxapay_page.py"
    is_user_order_report_test = item.path.name == "test_admin_user_order_report_page.py"
    is_refer_report_test = item.path.name == "test_admin_refer_report_page.py"
    is_order_edit_log_test = item.path.name == "test_admin_order_edit_log_page.py"
    is_user_transaction_log_test = item.path.name == "test_admin_user_transaction_log_page.py"
    is_active_users_test = item.path.name == "test_admin_active_users_page.py"
    is_user_bonus_test = item.path.name == "test_admin_user_bonus_page.py"
    is_symbol_config_test = item.path.name == "test_admin_symbol_configuration_page.py"
    is_symbol_list_test = item.path.name == "test_admin_symbol_list_page.py"
    is_user_group_test = item.path.name == "test_admin_user_group_page.py"
    report_path = CRON_JOBS_REPORT if is_cron_jobs_test else LP_CONFIG_REPORT if is_lp_config_test else OXAPAY_REPORT if is_oxapay_test else USER_ORDER_REPORT if is_user_order_report_test else REFER_REPORT if is_refer_report_test else ORDER_EDIT_LOG_REPORT if is_order_edit_log_test else USER_TRANSACTION_LOG_REPORT if is_user_transaction_log_test else ACTIVE_USERS_REPORT if is_active_users_test else USER_BONUS_REPORT if is_user_bonus_test else SYMBOL_CONFIG_REPORT if is_symbol_config_test else SYMBOL_LIST_REPORT if is_symbol_list_test else USER_GROUP_REPORT if is_user_group_test else SUMMARY_REPORT
    status = "PASSED" if report.passed else "FAILED"
    screenshot_path = None

    if report.failed:
        page = item.funcargs.get("authenticated_admin_page")
        if (is_cron_jobs_test or is_oxapay_test or is_active_users_test or is_user_bonus_test or is_symbol_config_test or is_symbol_list_test or is_user_group_test) and page:
            screenshot_path = (
                settings.screenshots_dir
                / f"{sanitize_filename(item.name)}_failure_{datetime.now():%Y%m%d_%H%M%S}.png"
            )
            page.screenshot(path=str(screenshot_path), full_page=True)
        else:
            screenshot_path = _latest_failure_screenshot(item.name)

    if is_cron_jobs_test or is_lp_config_test or is_oxapay_test or is_user_order_report_test or is_refer_report_test or is_order_edit_log_test or is_user_transaction_log_test or is_active_users_test or is_user_bonus_test or is_symbol_config_test or is_symbol_list_test or is_user_group_test:
        meaning = inspect.cleandoc(item.function.__doc__ or item.name)
    else:
        meaning = _get_test_meaning(item)

    reason = (
        "Test completed successfully"
        if report.passed
        else str(report.longrepr)
    )
    if screenshot_path:
        reason += f". Screenshot saved: {screenshot_path}"

    _append_summary_report(
        f"Test: {item.nodeid}\n"
        f"Meaning: {meaning}\n"
        f"Status: {status}\n"
        f"Reason: {reason}",
        report_path,
    )

CRON_JOBS_REPORT = REPORT_DIR / "cron_jobs_test_report.txt"
LP_CONFIG_REPORT = REPORT_DIR / "lp_execution_config_test_report.txt"
OXAPAY_REPORT = REPORT_DIR / "oxapay_test_report.txt"
USER_ORDER_REPORT = REPORT_DIR / "user_order_report_test_report.txt"
REFER_REPORT = REPORT_DIR / "refer_report_test_report.txt"
ORDER_EDIT_LOG_REPORT = REPORT_DIR / "order_edit_log_test_report.txt"
USER_TRANSACTION_LOG_REPORT = REPORT_DIR / "user_transaction_log_test_report.txt"
ACTIVE_USERS_REPORT = REPORT_DIR / "active_users_test_report.txt"
USER_BONUS_REPORT = REPORT_DIR / "user_bonus_test_report.txt"
SYMBOL_CONFIG_REPORT = REPORT_DIR / "symbol_config_test_report.txt"
SYMBOL_LIST_REPORT = REPORT_DIR / "symbol_list_test_report.txt"
USER_GROUP_REPORT = REPORT_DIR / "user_group_test_report.txt"



