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
from workflows.client_portal.utils.client_logger import ClientPortalLogger
from workflows.shared.utils.test_logger import extract_test_meaning


@pytest.fixture(scope="session")
def client_portal_logger() -> ClientPortalLogger:
    """Fixture providing access to the Client Portal logger instance."""
    return ClientPortalLogger.get_instance()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Portal-level hook to capture Client Portal test results into dedicated portal text files.
    """
    outcome = yield
    rep = outcome.get_result()

    should_record = (rep.when == "call") or (rep.when == "setup" and rep.failed)
    if should_record:
        meaning = extract_test_meaning(item)
        captured = ""
        if hasattr(rep, "capstdout") and rep.capstdout:
            captured += f"--- STDOUT ---\n{rep.capstdout}\n"
        if hasattr(rep, "capstderr") and rep.capstderr:
            captured += f"--- STDERR ---\n{rep.capstderr}\n"

        if rep.passed:
            status = "PASSED"
            reason = "Test completed successfully"
            error_tb = ""
        elif rep.skipped:
            status = "SKIPPED"
            reason = getattr(rep, "wasxfail", None) or "Test skipped"
            error_tb = str(rep.longrepr) if hasattr(rep, "longrepr") else ""
        else:
            status = "FAILED"
            long_text = str(getattr(rep, "longreprtext", rep.longrepr))
            lines = [l.strip() for l in long_text.splitlines() if l.strip()]
            reason = lines[-1] if lines else "Test execution failed"
            if rep.when == "setup":
                reason = f"Setup failure: {reason}"
            error_tb = long_text

        try:
            ClientPortalLogger.get_instance().record_test(
                test_id=item.nodeid,
                meaning=meaning,
                status=status,
                reason=reason,
                duration=rep.duration,
                captured_output=captured,
                error_traceback=error_tb,
            )
        except Exception:
            pass


def pytest_sessionfinish(session, exitstatus):
    """Finalize Client Portal logs."""
    try:
        ClientPortalLogger.get_instance().finalize()
    except Exception:
        pass
