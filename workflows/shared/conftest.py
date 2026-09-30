"""
Shared Workflows Conftest.
Provides isolated browser sessions and dedicated report generation for cross-portal workflows in workflows/shared.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)
from workflows.shared.utils.test_logger import extract_test_meaning

SHARED_REPORTS_DIR = Path(__file__).resolve().parent / "reports"
SHARED_PASSED_FILE = SHARED_REPORTS_DIR / "passed.txt"

_shared_test_results: List[Dict[str, str]] = []
_shared_passed_tests: List[Dict[str, str]] = []


def _write_shared_passed_results() -> None:
    SHARED_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Shared Workflows Passed Test Results",
        "",
    ]
    for item in _shared_passed_tests:
        lines.extend([
            f"Test: {item['test']}",
            f"Meaning: {item['meaning']}",
            "Status: PASSED",
            "Reason: Test completed successfully",
            "",
        ])
    lines.append(f"Total Passed: {len(_shared_passed_tests)}")
    lines.append("")
    SHARED_PASSED_FILE.write_text("\n".join(lines), encoding="utf-8")


def pytest_sessionstart(session) -> None:
    _shared_test_results.clear()
    SHARED_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if SHARED_PASSED_FILE.exists():
        content = SHARED_PASSED_FILE.read_text(encoding="utf-8")
        matches = re.findall(r"Test:\s*([^\n]+)\nMeaning:\s*([^\n]+)", content)
        for test_id, meaning in matches:
            if not any(t["test"] == test_id for t in _shared_passed_tests):
                _shared_passed_tests.append({"test": test_id, "meaning": meaning})


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.passed:
        meaning = extract_test_meaning(item)
        existing = next((t for t in _shared_passed_tests if t["test"] == rep.nodeid), None)
        if existing:
            existing["meaning"] = meaning
        else:
            _shared_passed_tests.append({"test": rep.nodeid, "meaning": meaning})
        _write_shared_passed_results()


def pytest_sessionfinish(session, exitstatus) -> None:
    _write_shared_passed_results()
