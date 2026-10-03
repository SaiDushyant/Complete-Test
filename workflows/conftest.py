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


from pathlib import Path


from config.settings import settings


def pytest_sessionstart(session):
    """Archive prior test runs and prepare fresh log session on test startup."""
    if not hasattr(session.config, "workerinput"):
        try:
            target_hint = None
            is_val = False
            if hasattr(session.config, "args"):
                for arg in session.config.args:
                    if "test_val_" in arg or "validation" in arg:
                        is_val = True
                    if "test_" in arg and not target_hint:
                        target_hint = Path(arg.split("::")[0]).stem
            suite_dir = settings.validation_reports_dir if is_val else settings.workflow_reports_dir
            GlobalTestLogger.get_instance(suite_dir=suite_dir).prepare_fresh_session(run_type_hint=target_hint)
        except Exception:
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution outcome (setup, call, teardown).
    Attaches the result to request.node as rep_setup, rep_call, rep_teardown
    so fixtures can detect test failure and trigger screenshots/tracing.
    Also logs the test outcome and runtime diagnostics to the global text reporting engine.
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

        # Extract runtime diagnostics telemetry from page if available
        diag_data = {}
        try:
            page_obj = None
            if hasattr(item, "funcargs"):
                for val in item.funcargs.values():
                    if hasattr(val, "_diagnostics"):
                        page_obj = val
                        break
                    elif hasattr(val, "page") and hasattr(val.page, "_diagnostics"):
                        page_obj = val.page
                        break
            if page_obj and hasattr(page_obj, "_diagnostics"):
                d = page_obj._diagnostics
                diag_data = {
                    "clean": not d.has_errors(),
                    "uncaught_js_errors": len(d.page_errors),
                    "console_errors": len(d.get_console_errors()),
                    "console_warnings": len(d.get_console_warnings()),
                    "failed_requests": len(d.failed_requests),
                    "http_errors": len(d.http_errors),
                    "js_error_items": d.page_errors,
                    "console_error_items": d.get_console_errors(),
                    "failed_request_items": d.failed_requests,
                    "http_error_items": d.http_errors,
                }
        except Exception:
            pass

        try:
            GlobalTestLogger.get_instance().record_test(
                test_id=item.nodeid,
                meaning=meaning,
                status=status,
                reason=reason,
                duration=rep.duration,
                captured_output=captured,
                error_traceback=error_tb,
                diagnostics=diag_data,
            )
        except Exception:
            pass


def pytest_sessionfinish(session, exitstatus):
    """Finalize all global text logs at the end of the pytest session."""
    try:
        GlobalTestLogger.get_instance().finalize()
    except Exception:
        pass

