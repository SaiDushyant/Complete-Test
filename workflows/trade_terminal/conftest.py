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
    authenticated_trade_context,
    authenticated_trade_page,
    order_entry_page,
    positions_page,
    trade_login_page,
    trade_page,
    trading_dashboard_page,
)
from workflows.trade_terminal.utils.trade_logger import TradeTerminalLogger
from workflows.shared.utils.test_logger import extract_test_meaning
import pytest


@pytest.fixture(scope="session")
def trade_portal_logger() -> TradeTerminalLogger:
    """Fixture providing access to the Trade Terminal portal logger instance."""
    return TradeTerminalLogger.get_instance()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Portal-level hook to capture Trade Terminal test results into dedicated portal text files.
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
            TradeTerminalLogger.get_instance().record_test(
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
    """Finalize Trade Terminal portal logs."""
    try:
        TradeTerminalLogger.get_instance().finalize()
    except Exception:
        pass
