"""
Standardized Test Result Logger and Text Report Generator.

Captures test outcomes (PASSED, FAILED, SKIPPED), extracts human-readable
meanings from test docstrings, and produces formatted text logs at both
global and portal levels in the standardized structure:

    <Portal Name> Passed Test Results

    Test: workflows/admin_portal/tests/test_admin_example.py::test_admin_login_page_renders_form_elements
    Meaning: The Admin login page displays the username and password fields.
    Status: PASSED
    Reason: Test completed successfully

    Total Passed: 1

Saves results into dedicated text files so failures and specific issues
can be rapidly identified and inspected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("test_logger")


def sanitize_filename(name: str) -> str:
    """Sanitize a test nodeid or string for filesystem usage."""
    return re.sub(r"[^\w\-_.]", "_", name).strip("_")


def detect_portal(nodeid: str) -> Tuple[str, str]:
    """
    Detect portal name and slug from test node ID or file path.
    Returns (Portal Display Name, portal_slug).
    """
    if "admin_portal" in nodeid:
        return "Admin Portal", "admin_portal"
    if "trade_terminal" in nodeid:
        return "Trade Terminal", "trade_terminal"
    if "client_portal" in nodeid:
        return "Client Portal", "client_portal"
    if "ui_regression" in nodeid:
        return "UI Regression", "ui_regression"
    return "Global", "global"


def extract_test_meaning(item_or_doc: Any, test_name: str = "") -> str:
    """
    Extract a concise, human-readable meaning for a test.
    Prefers the test function docstring, falling back to a humanized function name.
    """
    doc: Optional[str] = None
    if hasattr(item_or_doc, "obj") and getattr(item_or_doc.obj, "__doc__", None):
        doc = item_or_doc.obj.__doc__
    elif isinstance(item_or_doc, str):
        doc = item_or_doc

    if doc:
        # Take the first paragraph
        first_para = doc.strip().split("\n\n")[0].strip()
        # Collapse multiple lines/whitespace
        cleaned = " ".join(line.strip() for line in first_para.splitlines() if line.strip())
        if cleaned:
            if not cleaned.endswith((".", "!", "?")):
                cleaned += "."
            return cleaned

    # Fallback to test function name
    name = test_name or getattr(item_or_doc, "name", "")
    if name.startswith("test_"):
        name = name[5:]
    humanized = name.replace("_", " ").capitalize()
    return f"{humanized}."


@dataclass
class TestResultRecord:
    """Represents the execution outcome and metadata of a single test."""
    test_id: str
    meaning: str
    status: str  # "PASSED", "FAILED", "SKIPPED"
    reason: str
    portal_name: str
    portal_slug: str
    duration: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    captured_output: str = ""
    error_traceback: str = ""

    def format_block(self) -> str:
        """Format the test record into the standardized multi-line string block."""
        return (
            f"Test: {self.test_id}\n"
            f"Meaning: {self.meaning}\n"
            f"Status: {self.status}\n"
            f"Reason: {self.reason}"
        )


class GlobalTestLogger:
    """
    Global test execution tracker.
    Collects results across all test modules and exports formatted text logs
    to reports/workflows/logs/.
    """

    _instance: Optional[GlobalTestLogger] = None

    def __init__(self, logs_dir: Optional[Path] = None):
        self.logs_dir = logs_dir or (settings.reports_dir / "workflows" / "logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.individual_dir = self.logs_dir / "individual"
        self.individual_dir.mkdir(parents=True, exist_ok=True)

        self.records: List[TestResultRecord] = []

    @classmethod
    def get_instance(cls) -> GlobalTestLogger:
        """Singleton accessor for test session coordination."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def record_test(
        self,
        test_id: str,
        meaning: str,
        status: str,
        reason: str,
        duration: float = 0.0,
        captured_output: str = "",
        error_traceback: str = "",
        portal_name: Optional[str] = None,
        portal_slug: Optional[str] = None,
    ) -> TestResultRecord:
        """Record a test outcome and immediately persist individual test log."""
        if not portal_name or not portal_slug:
            detected_name, detected_slug = detect_portal(test_id)
            portal_name = portal_name or detected_name
            portal_slug = portal_slug or detected_slug

        # Prevent duplicate recording if multiple conftests trigger hook
        for existing in self.records:
            if existing.test_id == test_id:
                return existing

        record = TestResultRecord(
            test_id=test_id,
            meaning=meaning,
            status=status.upper(),
            reason=reason,
            portal_name=portal_name,
            portal_slug=portal_slug,
            duration=duration,
            captured_output=captured_output,
            error_traceback=error_traceback,
        )
        self.records.append(record)

        # Write individual test log file
        self._write_individual_log(record)

        # Update running global text logs
        self._update_global_logs()

        return record

    def _write_individual_log(self, record: TestResultRecord) -> Path:
        """Write a dedicated log file for an individual test for rapid issue identification."""
        safe_name = sanitize_filename(record.test_id)
        portal_indiv_dir = self.individual_dir / record.portal_slug
        portal_indiv_dir.mkdir(parents=True, exist_ok=True)
        file_path = portal_indiv_dir / f"{safe_name}.txt"

        lines = [
            f"{record.portal_name} Test Execution Log",
            "=" * 70,
            record.format_block(),
            f"Duration: {record.duration:.3f}s",
            f"Timestamp: {record.timestamp}",
            "=" * 70,
        ]

        if record.error_traceback:
            lines.extend([
                "",
                "FAILURE TRACEBACK & REASON:",
                "-" * 70,
                record.error_traceback.strip(),
                "-" * 70,
            ])

        if record.captured_output:
            lines.extend([
                "",
                "CAPTURED CONSOLE / STANDARD OUTPUT:",
                "-" * 70,
                record.captured_output.strip(),
                "-" * 70,
            ])

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return file_path

    def _format_section(
        self,
        header_title: str,
        items: List[TestResultRecord],
        total_label: str,
    ) -> str:
        """Format a list of test records into the requested section structure."""
        lines = [header_title, ""]
        if not items:
            lines.append("None")
            lines.append("")
            lines.append(f"{total_label}: 0")
            return "\n".join(lines) + "\n"

        for item in items:
            lines.append(item.format_block())
            lines.append("")  # blank line between items

        lines.append(f"{total_label}: {len(items)}")
        return "\n".join(lines) + "\n"

    def _update_global_logs(self) -> None:
        """Persist aggregated global text files."""
        passed_records = [r for r in self.records if r.status == "PASSED"]
        failed_records = [r for r in self.records if r.status == "FAILED"]
        skipped_records = [r for r in self.records if r.status == "SKIPPED"]

        # 1. Global Passed Tests File
        passed_path = self.logs_dir / "global_passed_tests.txt"
        with open(passed_path, "w", encoding="utf-8") as f:
            f.write(
                self._format_section(
                    header_title="Global Passed Test Results",
                    items=passed_records,
                    total_label="Total Passed",
                )
            )

        # 2. Global Failed Tests File
        failed_path = self.logs_dir / "global_failed_tests.txt"
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(
                self._format_section(
                    header_title="Global Failed Test Results",
                    items=failed_records,
                    total_label="Total Failed",
                )
            )

        # 3. Global Skipped Tests File
        skipped_path = self.logs_dir / "global_skipped_tests.txt"
        with open(skipped_path, "w", encoding="utf-8") as f:
            f.write(
                self._format_section(
                    header_title="Global Skipped Test Results",
                    items=skipped_records,
                    total_label="Total Skipped",
                )
            )

        # 4. Overall Execution Summary File
        summary_path = self.logs_dir / "global_test_summary.txt"
        summary_lines = [
            "Test Suite Execution Summary",
            "=" * 70,
            f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Tests Run: {len(self.records)}",
            f"Total Passed:    {len(passed_records)}",
            f"Total Failed:    {len(failed_records)}",
            f"Total Skipped:   {len(skipped_records)}",
            "=" * 70,
            "",
            "Portal Breakdown:",
        ]

        # Group by portal
        portals: Dict[str, Dict[str, int]] = {}
        for r in self.records:
            if r.portal_name not in portals:
                portals[r.portal_name] = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0}
            portals[r.portal_name][r.status] = portals[r.portal_name].get(r.status, 0) + 1

        for portal, counts in sorted(portals.items()):
            summary_lines.append(
                f"- {portal}: {counts.get('PASSED', 0)} Passed, "
                f"{counts.get('FAILED', 0)} Failed, "
                f"{counts.get('SKIPPED', 0)} Skipped"
            )

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines) + "\n")

    def finalize(self) -> None:
        """Called at pytest session finish to ensure all logs are flushed."""
        self._update_global_logs()
        logger.info(
            f"Global test logs finalized at: {self.logs_dir} "
            f"({len(self.records)} total records)"
        )
