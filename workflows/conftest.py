"""
Root Conftest for Behavioral Workflow Tests (workflows/).
Configures test reporting hooks, shared browser lifecycle, and failure diagnostics.
"""

import pytest

# Export shared browser and context fixtures across all workflow test suites
from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)


from workflows.shared.utils.test_logger import (
    GlobalTestLogger,
    extract_test_meaning,
)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution outcome (setup, call, teardown).
    Attaches the result to request.node as rep_setup, rep_call, rep_teardown
    so fixtures can detect test failure and trigger screenshots/tracing.
    Also logs the test outcome to the global text reporting engine.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Process outcome during test execution call phase, or if setup failed
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
            # Extract clean failure message
            long_text = str(getattr(rep, "longreprtext", rep.longrepr))
            lines = [l.strip() for l in long_text.splitlines() if l.strip()]
            reason = lines[-1] if lines else "Test execution failed"
            if rep.when == "setup":
                reason = f"Setup failure: {reason}"
            error_tb = long_text

        try:
            GlobalTestLogger.get_instance().record_test(
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
    """Finalize all global text logs at the end of the pytest session."""
    try:
        GlobalTestLogger.get_instance().finalize()
    except Exception:
        pass
