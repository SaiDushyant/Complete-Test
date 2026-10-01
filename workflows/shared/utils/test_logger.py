"""
Standardized Test Result Logger, Runtime Diagnostics Aggregator, and History Manager.

Captures test outcomes (PASSED, FAILED, SKIPPED), extracts human-readable
meanings from test docstrings, records invisible background runtime diagnostics
(JS errors, console warnings, failed network requests, HTTP 4xx/5xx), and produces
formatted text logs and structured JSON reports.

Automatically archives previous test runs into timestamped history folders:
    reports/workflows/logs/history/<RunType> - DD-MM-YYYY_HH-MM-SS/
keeping the active log directory fresh, clean, and isolated per test execution.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
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
    return "Global", "shared"


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
        first_para = doc.strip().split("\n\n")[0].strip()
        cleaned = " ".join(line.strip() for line in first_para.splitlines() if line.strip())
        if cleaned:
            if not cleaned.endswith((".", "!", "?")):
                cleaned += "."
            return cleaned

    name = test_name or getattr(item_or_doc, "name", "")
    if name.startswith("test_"):
        name = name[5:]
    humanized = name.replace("_", " ").capitalize()
    return f"{humanized}."


@dataclass
class TestResultRecord:
    """Represents the execution outcome, metadata, and runtime diagnostics of a single test."""
    __test__ = False
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
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def format_block(self) -> str:
        """Format the test record into the standardized multi-line string block."""
        return (
            f"Test: {self.test_id}\n"
            f"Meaning: {self.meaning}\n"
            f"Status: {self.status}\n"
            f"Reason: {self.reason}"
        )

    def format_diagnostics_block(self) -> str:
        """Format hidden runtime diagnostics into a clear human-readable section."""
        lines = [
            "🔍 HIDDEN RUNTIME DIAGNOSTICS:",
            "-" * 70,
        ]
        if not self.diagnostics:
            lines.append("  Telemetry: Not captured / Non-browser test")
            return "\n".join(lines)

        js_errs = self.diagnostics.get("js_error_items") or []
        console_errs = self.diagnostics.get("console_error_items") or []
        failed_reqs = self.diagnostics.get("failed_request_items") or []
        http_errs = self.diagnostics.get("http_error_items") or []

        # 1. JS Runtime Errors
        if js_errs:
            lines.append(f"  • Uncaught JavaScript Errors: {len(js_errs)}")
            for i, err in enumerate(js_errs, 1):
                err_text = err.get("error", str(err)) if isinstance(err, dict) else str(err)
                lines.append(f"    {i}. {err_text}")
        else:
            lines.append("  • Uncaught JavaScript Errors: None (Clean)")

        # 2. Console Errors
        if console_errs:
            lines.append(f"  • Browser Console Errors: {len(console_errs)}")
            for i, err in enumerate(console_errs, 1):
                msg = err.get("text", str(err)) if isinstance(err, dict) else str(err)
                loc = err.get("location", "") if isinstance(err, dict) else ""
                loc_str = f" (at {loc})" if loc else ""
                lines.append(f"    {i}. {msg}{loc_str}")
        else:
            lines.append("  • Browser Console Errors: None (Clean)")

        # 3. Failed Network Requests
        if failed_reqs:
            lines.append(f"  • Failed Network Requests: {len(failed_reqs)}")
            for i, req in enumerate(failed_reqs, 1):
                method = req.get("method", "REQ") if isinstance(req, dict) else ""
                url = req.get("url", "") if isinstance(req, dict) else ""
                fail = req.get("failure", "") if isinstance(req, dict) else ""
                lines.append(f"    {i}. [{method}] {url} -> {fail}")
        else:
            lines.append("  • Failed Network Requests: None (Clean)")

        # 4. HTTP 4xx/5xx Responses
        if http_errs:
            lines.append(f"  • HTTP 4xx/5xx Responses: {len(http_errs)}")
            for i, res in enumerate(http_errs, 1):
                status = res.get("status", "") if isinstance(res, dict) else ""
                stext = res.get("status_text", "") if isinstance(res, dict) else ""
                url = res.get("url", "") if isinstance(res, dict) else ""
                lines.append(f"    {i}. [{status} {stext}] {url}")
        else:
            lines.append("  • HTTP 4xx/5xx Responses: None (Clean)")

        lines.append("-" * 70)
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to JSON-serializable dictionary."""
        return {
            "test_id": self.test_id,
            "meaning": self.meaning,
            "status": self.status,
            "reason": self.reason,
            "portal_name": self.portal_name,
            "portal_slug": self.portal_slug,
            "duration_seconds": round(self.duration, 3),
            "timestamp": self.timestamp,
            "error_traceback": self.error_traceback if self.status == "FAILED" else "",
            "diagnostics": self.diagnostics,
        }


class GlobalTestLogger:
    """
    Global test execution tracker and history manager.
    Collects results across all test modules, aggregates hidden runtime diagnostics,
    rotates past runs into timestamped history folders, and exports formatted reports.
    """

    _instance: Optional[GlobalTestLogger] = None

    def __init__(self, logs_dir: Optional[Path] = None):
        self.logs_dir = logs_dir or (settings.reports_dir / "workflows" / "logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir = self.logs_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.individual_dir = self.logs_dir / "individual"
        self.individual_dir.mkdir(parents=True, exist_ok=True)

        self.records: List[TestResultRecord] = []
        self._session_initialized = False

    @classmethod
    def get_instance(cls) -> GlobalTestLogger:
        """Singleton accessor for test session coordination."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def detect_run_type(self, hint: Optional[str] = None) -> str:
        """
        Infer a human-readable run type label from command-line arguments or hint.
        Examples: 'Full-Suite', 'Admin-Portal', 'Client-Portal', 'Trade-Terminal',
                  'Shared-Portal', 'UI-Regression', 'Smoke-Tests', 'test_admin_orders'
        """
        if hint:
            clean_hint = re.sub(r"[^\w\-.]", "_", hint).strip("_")
            return clean_hint

        cmd_str = " ".join(sys.argv)

        # Check for specific runner scripts or pytest targets
        if "run_admin_tests" in cmd_str or "admin_portal" in cmd_str:
            return "Admin-Portal"
        if "run_client_tests" in cmd_str or "client_portal" in cmd_str:
            return "Client-Portal"
        if "run_trade_tests" in cmd_str or "trade_terminal" in cmd_str:
            return "Trade-Terminal"
        if "run_shared_tests" in cmd_str or "workflows/shared" in cmd_str:
            return "Shared-Portal"
        if "run_ui_tests" in cmd_str or "ui_regression" in cmd_str:
            return "UI-Regression"
        if "run_smoke_tests" in cmd_str or "-m smoke" in cmd_str:
            return "Smoke-Tests"
        if "run_regression_tests" in cmd_str:
            return "Regression-Tests"

        # Check for single test file in arguments
        for arg in sys.argv:
            if "test_" in arg and (".py" in arg or "::" in arg):
                file_part = arg.split("::")[0]
                stem = Path(file_part).stem
                return sanitize_filename(stem)

        if "run_all_workflows" in cmd_str or "workflows/" in cmd_str or "pytest" in cmd_str:
            return "Full-Suite"

        return "Test-Run"

    def prepare_fresh_session(self, run_type_hint: Optional[str] = None) -> Optional[Path]:
        """
        Archive previous test logs into history/ and prepare a clean session.
        Returns the Path to the archived history folder, or None if no prior logs existed.
        """
        if self._session_initialized:
            return None

        self._session_initialized = True
        self.records.clear()

        # Check if there are active log files from a previous run to archive
        active_files = [
            self.logs_dir / "global_test_summary.txt",
            self.logs_dir / "global_test_results.json",
            self.logs_dir / "global_failed_tests.txt",
            self.logs_dir / "global_passed_tests.txt",
            self.logs_dir / "global_skipped_tests.txt",
            self.logs_dir / "summary_report.json",
            self.logs_dir / "test_results.json",
        ]
        has_active_files = any(f.exists() and f.stat().st_size > 0 for f in active_files)
        has_individual_logs = self.individual_dir.exists() and any(self.individual_dir.glob("*/*.json"))
        has_legacy_dirs = (self.logs_dir / "client_portal").exists() or (self.logs_dir / "trade_terminal").exists()

        archived_dir: Optional[Path] = None

        if has_active_files or has_individual_logs or has_legacy_dirs:
            # Determine archive folder name
            timestamp_str = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            run_label = self.detect_run_type(run_type_hint)
            folder_name = f"{run_label} - {timestamp_str}"
            archived_dir = self.history_dir / folder_name
            archived_dir.mkdir(parents=True, exist_ok=True)

            # Move active summary and result files into history
            for f in active_files:
                if f.exists():
                    try:
                        shutil.move(str(f), str(archived_dir / f.name))
                    except Exception as e:
                        logger.debug(f"Could not move {f.name} to history: {e}")

            # Move individual directory into history
            if self.individual_dir.exists() and any(self.individual_dir.iterdir()):
                target_indiv = archived_dir / "individual"
                try:
                    shutil.move(str(self.individual_dir), str(target_indiv))
                except Exception as e:
                    logger.debug(f"Could not move individual/ to history: {e}")

            # Clean up any legacy flat directories
            for leg_name in ("client_portal", "trade_terminal"):
                leg_path = self.logs_dir / leg_name
                if leg_path.exists():
                    try:
                        shutil.move(str(leg_path), str(archived_dir / leg_name))
                    except Exception:
                        shutil.rmtree(str(leg_path), ignore_errors=True)

            logger.info(f"Archived previous test session to: {archived_dir}")

        # Re-create fresh individual portal directories
        self.individual_dir.mkdir(parents=True, exist_ok=True)
        for portal_slug in ("admin_portal", "client_portal", "trade_terminal", "shared", "ui_regression"):
            (self.individual_dir / portal_slug).mkdir(parents=True, exist_ok=True)

        return archived_dir

    def record_test(
        self,
        test_id: str,
        meaning: str,
        status: str,
        reason: str,
        duration: float = 0.0,
        captured_output: str = "",
        error_traceback: str = "",
        diagnostics: Optional[Dict[str, Any]] = None,
        portal_name: Optional[str] = None,
        portal_slug: Optional[str] = None,
    ) -> TestResultRecord:
        """Record a test outcome, attach runtime diagnostics, and persist individual test log."""
        if not portal_name or not portal_slug:
            detected_name, detected_slug = detect_portal(test_id)
            portal_name = portal_name or detected_name
            portal_slug = portal_slug or detected_slug

        # Prevent duplicate recording if multiple hooks fire
        for existing in self.records:
            if existing.test_id == test_id:
                if diagnostics and not existing.diagnostics:
                    existing.diagnostics = diagnostics
                    self._write_individual_log(existing)
                    self._update_global_logs()
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
            diagnostics=diagnostics or {},
        )
        self.records.append(record)

        # Write individual test log file (TXT + JSON)
        self._write_individual_log(record)

        # Update running global text and JSON logs
        self._update_global_logs()

        return record

    def _write_individual_log(self, record: TestResultRecord) -> Path:
        """Write a dedicated log file for an individual test including diagnostics."""
        safe_name = sanitize_filename(record.test_id)
        portal_indiv_dir = self.individual_dir / record.portal_slug
        portal_indiv_dir.mkdir(parents=True, exist_ok=True)
        file_path = portal_indiv_dir / f"{safe_name}.txt"
        json_path = portal_indiv_dir / f"{safe_name}.json"

        lines = [
            f"{record.portal_name} Test Execution Log",
            "=" * 70,
            record.format_block(),
            f"Duration: {record.duration:.3f}s",
            f"Timestamp: {record.timestamp}",
            "=" * 70,
            "",
            record.format_diagnostics_block(),
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

        # Atomic JSON record for robust multi-worker / xdist aggregation
        try:
            with open(json_path, "w", encoding="utf-8") as f_json:
                json.dump(record.to_dict(), f_json, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Failed writing individual test json: {e}")

        return file_path

    def _get_all_aggregated_records(self) -> List[TestResultRecord]:
        """
        Aggregate records from both in-memory list and individual JSON files on disk.
        Provides process-safe multi-worker (pytest-xdist) consolidation.
        """
        records_by_id: Dict[str, TestResultRecord] = {r.test_id: r for r in self.records}

        if self.individual_dir.exists():
            for json_file in self.individual_dir.glob("*/*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        test_id = data.get("test_id")
                        if test_id and test_id not in records_by_id:
                            records_by_id[test_id] = TestResultRecord(
                                test_id=test_id,
                                meaning=data.get("meaning", ""),
                                status=data.get("status", "PASSED"),
                                reason=data.get("reason", ""),
                                portal_name=data.get("portal_name", "Global"),
                                portal_slug=data.get("portal_slug", "shared"),
                                duration=data.get("duration_seconds", 0.0),
                                timestamp=data.get("timestamp", ""),
                                error_traceback=data.get("error_traceback", ""),
                                diagnostics=data.get("diagnostics", {}),
                            )
                        elif test_id and test_id in records_by_id:
                            # Merge diagnostics if missing in memory
                            if not records_by_id[test_id].diagnostics and data.get("diagnostics"):
                                records_by_id[test_id].diagnostics = data.get("diagnostics")
                except Exception:
                    pass

        return list(records_by_id.values())

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
            lines.append("")

        lines.append(f"{total_label}: {len(items)}")
        return "\n".join(lines) + "\n"

    def _update_global_logs(self) -> None:
        """Persist aggregated global text files and canonical JSON report."""
        all_records = self._get_all_aggregated_records()
        passed_records = [r for r in all_records if r.status == "PASSED"]
        failed_records = [r for r in all_records if r.status == "FAILED"]
        skipped_records = [r for r in all_records if r.status == "SKIPPED"]

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

        # 4. Overall Execution Summary File (TXT)
        summary_path = self.logs_dir / "global_test_summary.txt"
        summary_lines = [
            "Test Suite Execution Summary",
            "=" * 70,
            f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Tests Run: {len(all_records)}",
            f"Total Passed:    {len(passed_records)}",
            f"Total Failed:    {len(failed_records)}",
            f"Total Skipped:   {len(skipped_records)}",
            "=" * 70,
            "",
            "Portal Breakdown:",
        ]

        # Group by portal
        portals: Dict[str, Dict[str, int]] = {}
        portal_durations: Dict[str, float] = {}
        for r in all_records:
            if r.portal_name not in portals:
                portals[r.portal_name] = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "TOTAL": 0}
                portal_durations[r.portal_name] = 0.0
            portals[r.portal_name][r.status] = portals[r.portal_name].get(r.status, 0) + 1
            portals[r.portal_name]["TOTAL"] = portals[r.portal_name].get("TOTAL", 0) + 1
            portal_durations[r.portal_name] += r.duration

        for portal, counts in sorted(portals.items()):
            summary_lines.append(
                f"- {portal}: {counts.get('PASSED', 0)} Passed, "
                f"{counts.get('FAILED', 0)} Failed, "
                f"{counts.get('SKIPPED', 0)} Skipped (Total: {counts.get('TOTAL', 0)})"
            )

        # Add Runtime Diagnostics Overview to TXT summary
        diagnostic_flagged = [r for r in all_records if r.diagnostics and not r.diagnostics.get("clean", True)]
        clean_diagnostic_count = len([r for r in all_records if r.diagnostics and r.diagnostics.get("clean", True)])

        summary_lines.extend([
            "",
            "=" * 70,
            "Runtime Diagnostics Overview (Background Telemetry):",
            f"- Tests with 100% Clean Diagnostics: {clean_diagnostic_count}",
            f"- Tests with Hidden Browser / Network Flags: {len(diagnostic_flagged)}",
        ])

        if diagnostic_flagged:
            summary_lines.append("-" * 70)
            summary_lines.append("Tests with Hidden Diagnostic Warnings:")
            for r in diagnostic_flagged[:15]:
                js_count = len(r.diagnostics.get("js_error_items") or [])
                console_count = len(r.diagnostics.get("console_error_items") or [])
                failed_count = len(r.diagnostics.get("failed_request_items") or [])
                http_count = len(r.diagnostics.get("http_error_items") or [])
                parts = []
                if js_count:
                    parts.append(f"{js_count} JS Error(s)")
                if console_count:
                    parts.append(f"{console_count} Console Error(s)")
                if failed_count:
                    parts.append(f"{failed_count} Failed Req(s)")
                if http_count:
                    parts.append(f"{http_count} HTTP 4xx/5xx")
                flag_str = ", ".join(parts) if parts else "Warnings detected"
                summary_lines.append(f"• {r.test_id}")
                summary_lines.append(f"  └─ {flag_str}")
            if len(diagnostic_flagged) > 15:
                summary_lines.append(f"• ... and {len(diagnostic_flagged) - 15} more tests with diagnostic flags.")

        summary_lines.append("=" * 70)

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines) + "\n")

        # 5. Global Structured JSON Report
        total_count = len(all_records)
        pass_rate = round((len(passed_records) / max(total_count, 1)) * 100, 2)
        total_dur = round(sum(r.duration for r in all_records), 3)

        json_summary = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_count,
                "passed": len(passed_records),
                "failed": len(failed_records),
                "skipped": len(skipped_records),
                "pass_rate_percentage": pass_rate,
                "total_duration_seconds": total_dur,
                "diagnostics": {
                    "total_clean_tests": clean_diagnostic_count,
                    "total_flagged_tests": len(diagnostic_flagged),
                },
                "portal_breakdown": {
                    portal: {
                        "total": counts.get("TOTAL", 0),
                        "passed": counts.get("PASSED", 0),
                        "failed": counts.get("FAILED", 0),
                        "skipped": counts.get("SKIPPED", 0),
                        "duration_seconds": round(portal_durations.get(portal, 0.0), 3),
                    }
                    for portal, counts in sorted(portals.items())
                },
            },
            "failed_tests": [r.to_dict() for r in failed_records],
            "skipped_tests": [r.to_dict() for r in skipped_records],
            "diagnostic_flagged_tests": [r.to_dict() for r in diagnostic_flagged],
            "all_tests": [r.to_dict() for r in all_records],
        }

        # Save to primary canonical JSON report
        json_file_path = self.logs_dir / "global_test_results.json"
        try:
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(json_summary, f, indent=2, ensure_ascii=False)
        except Exception as json_err:
            logger.warning(f"Failed to write global JSON report: {json_err}")

    def finalize(self) -> None:
        """Called at pytest session finish to ensure all logs are flushed."""
        self._update_global_logs()
        logger.info(
            f"Global test logs finalized at: {self.logs_dir} "
            f"({len(self.records)} total records)"
        )
