from __future__ import annotations

from pathlib import Path

import pytest

from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

from workflows.admin_portal.fixtures.admin_fixtures import (
    admin_dashboard_page,
    admin_login_page,
    admin_page,
    authenticated_admin_context,
    authenticated_admin_page,
    user_management_page,
)


REPORTS_DIR = Path(__file__).resolve().parent / "reports"
TEST_RESULTS_FILE = REPORTS_DIR / "test_results.txt"
PASSED_DIR = REPORTS_DIR / "passed"
PASSED_FILE = PASSED_DIR / "passed.txt"

_test_results: list[dict[str, str]] = []
_passed_tests: list[str] = []


TEST_DESCRIPTIONS = {
    "test_admin_login_page_renders_form_elements": (
        "The Admin login page displays the username and password fields."
    ),
    "test_admin_can_view_management_dashboard": (
        "The administrator can log in and open the Admin Dashboard."
    ),
    "test_admin_user_management_page_loads": (
        "The Admin User Management page opens and displays the users table."
    ),
    "test_admin_user_management_has_create_user_action": (
        "The User Management page shows the Add User/Create Account button."
    ),
    "test_admin_user_management_search_is_available": (
        "The User Management page shows the search field."
    ),
    "test_admin_profile_menu_shows_admin_details": (
        "The Admin profile menu opens and shows the admin name and role."
    ),
    "test_admin_profile_menu_has_logout_link": (
        "The Admin profile menu contains a working Logout link."
    ),
    "test_admin_theme_toggle_is_visible": (
        "The Admin Dashboard displays the theme switch button."
    ),
    "test_admin_notifications_are_available": (
        "The Admin Dashboard displays notifications and the Mark all read option."
    ),
    "test_admin_sidebar_menu_button_is_visible": (
        "The Admin Dashboard displays the button used to open the sidebar menu."
    ),
    "test_admin_dashboard_kpi_values_are_numeric": (
        "The Dashboard KPI cards display valid numeric values."
    ),
    "test_admin_dashboard_charts_are_rendered": (
        "The Dashboard displays both the Deposits vs Withdrawals and "
        "A-Book vs B-Book charts."
    ),
    "test_admin_dashboard_heading_is_displayed": (
        "The Admin Dashboard displays the Dashboard heading."
    ),
    "test_admin_dashboard_main_kpi_cards_are_displayed": (
        "The Dashboard displays the Deposit, Withdrawal, and User KPI cards."
    ),
    "test_admin_dashboard_book_sections_are_displayed": (
        "The Dashboard displays both the A-Book and B-Book sections."
    ),
}


def _get_test_description(test_name: str) -> str:
    """Return a clear explanation for a test result."""
    test_id = test_name.rsplit("::", 1)[-1]

    if test_id.startswith(
        "test_admin_sidebar_link_is_visible_and_correct["
    ):
        sidebar_item = test_id.split("[", 1)[1].rsplit("]", 1)[0]

        return (
            f"The Admin sidebar '{sidebar_item}' link is visible "
            f"and points to the correct page."
        )

    function_name = test_id

    return TEST_DESCRIPTIONS.get(
        function_name,
        "The Admin Portal test completed successfully.",
    )


def _load_existing_passed_tests() -> None:
    """Load previously passed tests without deleting them."""
    if not PASSED_FILE.exists():
        return

    for line in PASSED_FILE.read_text(
        encoding="utf-8"
    ).splitlines():
        if line.startswith("Test: "):
            test_name = line.removeprefix("Test: ").strip()

            if test_name and test_name not in _passed_tests:
                _passed_tests.append(test_name)


def _write_test_results() -> None:
    """Write results from the current test run."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    passed_count = sum(
        result["status"] == "PASSED"
        for result in _test_results
    )
    failed_count = sum(
        result["status"] == "FAILED"
        for result in _test_results
    )

    lines = [
        "Admin Portal Test Results",
        "",
    ]

    for result in _test_results:
        lines.extend(
            [
                f"Test: {result['test']}",
                f"Meaning: {_get_test_description(result['test'])}",
                f"Status: {result['status']}",
                "",
            ]
        )

    lines.extend(
        [
            f"Total: {len(_test_results)}",
            f"Passed: {passed_count}",
            f"Failed: {failed_count}",
        ]
    )

    TEST_RESULTS_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _write_passed_results() -> None:
    """Write all passed tests without deleting older passed tests."""
    PASSED_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "Admin Portal Passed Test Results",
        "",
    ]

    for test_name in _passed_tests:
        lines.extend(
            [
                f"Test: {test_name}",
                f"Meaning: {_get_test_description(test_name)}",
                "Status: PASSED",
                "Reason: Test completed successfully",
                "",
            ]
        )

    lines.append(
        f"Total Passed: {len(_passed_tests)}"
    )

    PASSED_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def pytest_sessionstart(session) -> None:
    """Prepare reports without deleting previous passed tests."""
    _test_results.clear()
    _passed_tests.clear()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    PASSED_DIR.mkdir(parents=True, exist_ok=True)

    _load_existing_passed_tests()

    _write_test_results()
    _write_passed_results()


def pytest_runtest_logreport(report) -> None:
    """Record each Admin test result."""
    if report.when == "call":
        status = "PASSED" if report.passed else "FAILED"
    elif report.when == "setup" and report.failed:
        status = "FAILED"
    else:
        return

    _test_results.append(
        {
            "test": report.nodeid,
            "status": status,
        }
    )

    _write_test_results()

    if status == "PASSED":
        if report.nodeid not in _passed_tests:
            _passed_tests.append(report.nodeid)

        _write_passed_results()


def pytest_sessionfinish(session, exitstatus) -> None:
    """Write final Admin reports."""
    _write_test_results()
    _write_passed_results()