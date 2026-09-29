"""
Trade Terminal Portal Logger and Text Report Generator.

Provides portal-level test result logging specifically for the Trade Terminal suite.
Generates structured text files in reports/workflows/logs/trade_terminal/:
- trade_passed_tests.txt
- trade_failed_tests.txt
- trade_skipped_tests.txt
- trade_summary.txt
- tests/<test_node_id>.txt (detailed individual test log)

Formats outputs matching the standardized layout:

    Trade Terminal Passed Test Results

    Test: workflows/trade_terminal/tests/test_trade_login.py::test_trade_login_form_elements_displayed
    Meaning: Verify that the Trade Terminal login form renders all required inputs...
    Status: PASSED
    Reason: Test completed successfully

    Total Passed: 1
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config.settings import settings
from workflows.shared.utils.logger import get_logger
from workflows.shared.utils.test_logger import (
    TestResultRecord,
    extract_test_meaning,
    sanitize_filename,
)

logger = get_logger("trade_logger")


class TradeTerminalLogger:
    """
    Dedicated Trade Terminal test result logger.
    Manages portal-specific logs and text report artifacts.
    """

    _instance: Optional[TradeTerminalLogger] = None

    def __init__(self, portal_logs_dir: Optional[Path] = None):
        base_logs = settings.reports_dir / "workflows" / "logs"
        self.portal_dir = portal_logs_dir or (base_logs / "trade_terminal")
        self.portal_dir.mkdir(parents=True, exist_ok=True)
        self.individual_dir = self.portal_dir / "tests"
        self.individual_dir.mkdir(parents=True, exist_ok=True)

        self.records: List[TestResultRecord] = []

    @classmethod
    def get_instance(cls) -> TradeTerminalLogger:
        """Singleton instance for Trade Terminal portal test execution."""
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
    ) -> TestResultRecord:
        """Record Trade Terminal test result and persist dedicated text files."""
        # Avoid duplicate recordings
        for existing in self.records:
            if existing.test_id == test_id:
                return existing

        record = TestResultRecord(
            test_id=test_id,
            meaning=meaning,
            status=status.upper(),
            reason=reason,
            portal_name="Trade Terminal",
            portal_slug="trade_terminal",
            duration=duration,
            captured_output=captured_output,
            error_traceback=error_traceback,
        )
        self.records.append(record)

        # Write individual test log
        self._write_individual_log(record)

        # Update portal level passed / failed files
        self._update_portal_logs()

        return record

    def _write_individual_log(self, record: TestResultRecord) -> Path:
        """Save a dedicated text log file for this specific Trade Terminal test."""
        safe_name = sanitize_filename(record.test_id)
        log_path = self.individual_dir / f"{safe_name}.txt"

        lines = [
            "Trade Terminal Test Execution Log",
            "=" * 70,
            record.format_block(),
            f"Duration: {record.duration:.3f}s",
            f"Timestamp: {record.timestamp}",
            "=" * 70,
        ]

        if record.error_traceback:
            lines.extend([
                "",
                "FAILURE REASON & TRACEBACK:",
                "-" * 70,
                record.error_traceback.strip(),
                "-" * 70,
            ])

        if record.captured_output:
            lines.extend([
                "",
                "CAPTURED CONSOLE & RUNTIME OUTPUT:",
                "-" * 70,
                record.captured_output.strip(),
                "-" * 70,
            ])

        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return log_path

    def _format_section(
        self,
        status_title: str,
        items: List[TestResultRecord],
        total_label: str,
    ) -> str:
        """Format test records in the standardized structure."""
        lines = [f"Trade Terminal {status_title} Test Results", ""]
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

    def _update_portal_logs(self) -> None:
        """Write out Trade Terminal passed, failed, and summary text files."""
        passed_records = [r for r in self.records if r.status == "PASSED"]
        failed_records = [r for r in self.records if r.status == "FAILED"]
        skipped_records = [r for r in self.records if r.status == "SKIPPED"]

        # 1. Trade Terminal Passed Tests File
        passed_file = self.portal_dir / "trade_passed_tests.txt"
        with open(passed_file, "w", encoding="utf-8") as f:
            f.write(
                self._format_section(
                    status_title="Passed",
                    items=passed_records,
                    total_label="Total Passed",
                )
            )

        # 2. Trade Terminal Failed Tests File
        failed_file = self.portal_dir / "trade_failed_tests.txt"
        with open(failed_file, "w", encoding="utf-8") as f:
            f.write(
                self._format_section(
                    status_title="Failed",
                    items=failed_records,
                    total_label="Total Failed",
                )
            )

        # 3. Trade Terminal Skipped Tests File
        skipped_file = self.portal_dir / "trade_skipped_tests.txt"
        with open(skipped_file, "w", encoding="utf-8") as f:
            f.write(
                self._format_section(
                    status_title="Skipped",
                    items=skipped_records,
                    total_label="Total Skipped",
                )
            )

        # 4. Trade Terminal Summary File
        summary_file = self.portal_dir / "trade_summary.txt"
        summary_lines = [
            "Trade Terminal Execution Summary",
            "=" * 70,
            f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Tests:   {len(self.records)}",
            f"Total Passed:  {len(passed_records)}",
            f"Total Failed:  {len(failed_records)}",
            f"Total Skipped: {len(skipped_records)}",
            "=" * 70,
        ]
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines) + "\n")

    def finalize(self) -> None:
        """Finalize and flush portal logs."""
        self._update_portal_logs()
        logger.info(
            f"Trade Terminal portal logs finalized at: {self.portal_dir} "
            f"({len(self.records)} tests recorded)"
        )
