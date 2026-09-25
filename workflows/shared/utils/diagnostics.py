"""
Diagnostic Telemetry & Runtime Error Monitor for Workflow Tests.
Tracks console messages, uncaught JavaScript exceptions (page errors),
failed network requests, and HTTP 4xx/5xx error responses.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.sync_api import Page, Request, Response

from config.settings import settings
from workflows.shared.utils.logger import get_logger
from workflows.shared.utils.screenshot import sanitize_filename

logger = get_logger("diagnostics")


class PageDiagnostics:
    """
    Real-time observer attached to a Playwright Page instance.
    Monitors and records invisible background errors (Console, JS runtime, Network).
    """

    def __init__(self, page: Page):
        self.page = page
        self.console_messages: List[Dict[str, Any]] = []
        self.page_errors: List[Dict[str, Any]] = []
        self.failed_requests: List[Dict[str, Any]] = []
        self.http_errors: List[Dict[str, Any]] = []

        # Attach Playwright listeners
        self._attach_listeners()

    def _attach_listeners(self) -> None:
        """Register asynchronous event listeners on the underlying page."""
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_page_error)
        self.page.on("requestfailed", self._handle_request_failed)
        self.page.on("response", self._handle_response)

    def _handle_console(self, msg) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": msg.type,
            "text": msg.text,
            "location": msg.location,
        }
        self.console_messages.append(entry)
        if msg.type == "error":
            logger.warning(f"Browser Console Error: {msg.text} (Location: {msg.location})")
        elif msg.type == "warning":
            logger.debug(f"Browser Console Warning: {msg.text}")

    def _handle_page_error(self, error: Exception) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
        }
        self.page_errors.append(entry)
        logger.error(f"Uncaught JavaScript Page Error: {error}")

    def _handle_request_failed(self, request: Request) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": request.url,
            "resource_type": request.resource_type,
            "failure": request.failure,
        }
        self.failed_requests.append(entry)
        logger.warning(
            f"Network Request Failed: [{request.method}] {request.url} - Reason: {request.failure}"
        )

    def _handle_response(self, response: Response) -> None:
        if response.status >= 400:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "method": response.request.method,
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
                "resource_type": response.request.resource_type,
            }
            self.http_errors.append(entry)
            logger.warning(
                f"HTTP Error Response: [{response.status} {response.status_text}] {response.url}"
            )

    # =========================================================================
    # Error Query Methods
    # =========================================================================

    def get_console_errors(self) -> List[Dict[str, Any]]:
        """Return list of console messages of type 'error'."""
        return [m for m in self.console_messages if m["type"] == "error"]

    def get_console_warnings(self) -> List[Dict[str, Any]]:
        """Return list of console messages of type 'warning'."""
        return [m for m in self.console_messages if m["type"] == "warning"]

    def get_page_errors(self) -> List[Dict[str, Any]]:
        """Return list of uncaught JavaScript exceptions."""
        return list(self.page_errors)

    def get_failed_requests(self) -> List[Dict[str, Any]]:
        """Return list of dropped or aborted network requests."""
        return list(self.failed_requests)

    def get_http_errors(self) -> List[Dict[str, Any]]:
        """Return list of responses with HTTP status >= 400."""
        return list(self.http_errors)

    def has_errors(self) -> bool:
        """Check if any uncaught JS errors, console errors, or network errors occurred."""
        return bool(
            self.page_errors
            or self.get_console_errors()
            or self.failed_requests
            or self.http_errors
        )

    def clear(self) -> None:
        """Reset all recorded diagnostics collections."""
        self.console_messages.clear()
        self.page_errors.clear()
        self.failed_requests.clear()
        self.http_errors.clear()

    # =========================================================================
    # Reporting & Artifact Serialization
    # =========================================================================

    def format_report(self) -> str:
        """Generate human-readable diagnostic breakdown."""
        lines = []
        lines.append("=" * 70)
        lines.append(f"🔍 PAGE RUNTIME DIAGNOSTICS REPORT")
        lines.append(f"URL: {self.page.url}")
        lines.append(f"Title: {self.page.title()}")
        lines.append(f"Timestamp: {datetime.now().isoformat()}")
        lines.append("=" * 70)

        # 1. Uncaught JS
        lines.append(f"\n[1] Uncaught JavaScript Runtime Errors ({len(self.page_errors)}):")
        if self.page_errors:
            for i, err in enumerate(self.page_errors, 1):
                lines.append(f"  {i}. {err['error']}")
        else:
            lines.append("  None (clean JS execution)")

        # 2. Console Errors
        console_errs = self.get_console_errors()
        lines.append(f"\n[2] Console Errors ({len(console_errs)}):")
        if console_errs:
            for i, err in enumerate(console_errs, 1):
                lines.append(f"  {i}. {err['text']} (at {err['location']})")
        else:
            lines.append("  None (clean console)")

        # 3. Failed Network Requests
        lines.append(f"\n[3] Failed Network Requests ({len(self.failed_requests)}):")
        if self.failed_requests:
            for i, req in enumerate(self.failed_requests, 1):
                lines.append(f"  {i}. [{req['method']}] {req['url']} -> {req['failure']}")
        else:
            lines.append("  None (all network calls completed)")

        # 4. HTTP 4xx/5xx Responses
        lines.append(f"\n[4] HTTP 4xx/5xx Responses ({len(self.http_errors)}):")
        if self.http_errors:
            for i, res in enumerate(self.http_errors, 1):
                lines.append(f"  {i}. [{res['status']} {res['status_text']}] {res['url']}")
        else:
            lines.append("  None (all responses returned 2xx/3xx)")

        lines.append("=" * 70)
        return "\n".join(lines)

    def save_report(
        self,
        test_name: str,
        destination_dir: Optional[Path] = None,
    ) -> Path:
        """
        Persist structured JSON diagnostics alongside a human-readable text file.
        """
        target_dir = destination_dir or settings.diagnostics_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_name = sanitize_filename(test_name)
        json_path = target_dir / f"diagnostics_{clean_name}_{timestamp}.json"
        txt_path = target_dir / f"diagnostics_{clean_name}_{timestamp}.log"

        payload = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "url": self.page.url,
            "title": self.page.title(),
            "counts": {
                "uncaught_js_errors": len(self.page_errors),
                "console_errors": len(self.get_console_errors()),
                "console_warnings": len(self.get_console_warnings()),
                "failed_network_requests": len(self.failed_requests),
                "http_errors": len(self.http_errors),
            },
            "page_errors": self.page_errors,
            "console_errors": self.get_console_errors(),
            "console_warnings": self.get_console_warnings(),
            "failed_requests": self.failed_requests,
            "http_errors": self.http_errors,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(self.format_report())

        logger.info(f"Saved diagnostic telemetry to: {json_path}")
        return json_path

    # =========================================================================
    # Strict Assertions for Behavioral Tests
    # =========================================================================

    def assert_no_javascript_errors(self) -> None:
        """Assert that zero unhandled JavaScript runtime exceptions occurred."""
        if self.page_errors:
            err_msgs = "\n".join([f"- {e['error']}" for e in self.page_errors])
            raise AssertionError(
                f"Page encountered {len(self.page_errors)} uncaught JavaScript runtime error(s):\n{err_msgs}"
            )

    def assert_no_console_errors(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """
        Assert that zero console.error calls were issued, excluding optional allowed patterns.
        """
        ignored = ignored_patterns or []
        filtered = []
        for err in self.get_console_errors():
            text = err["text"]
            if not any(pattern in text for pattern in ignored):
                filtered.append(err)

        if filtered:
            err_msgs = "\n".join([f"- {e['text']} (at {e['location']})" for e in filtered])
            raise AssertionError(
                f"Page encountered {len(filtered)} console error(s):\n{err_msgs}"
            )

    def assert_no_failed_requests(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """
        Assert that no network requests were dropped or aborted.
        """
        ignored = ignored_patterns or []
        filtered = []
        for req in self.failed_requests:
            url = req["url"]
            if not any(pattern in url for pattern in ignored):
                filtered.append(req)

        if filtered:
            req_msgs = "\n".join(
                [f"- [{r['method']}] {r['url']} (Reason: {r['failure']})" for r in filtered]
            )
            raise AssertionError(
                f"Page encountered {len(filtered)} failed network request(s):\n{req_msgs}"
            )

    def assert_no_http_errors(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """
        Assert that no network requests returned HTTP status >= 400.
        """
        ignored = ignored_patterns or []
        filtered = []
        for res in self.http_errors:
            url = res["url"]
            if not any(pattern in url for pattern in ignored):
                filtered.append(res)

        if filtered:
            res_msgs = "\n".join([f"- [{r['status']}] {r['url']}" for r in filtered])
            raise AssertionError(
                f"Page received {len(filtered)} HTTP 4xx/5xx error response(s):\n{res_msgs}"
            )

    def assert_clean_diagnostics(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert that JS runtime, console, and network requests are all free of errors."""
        self.assert_no_javascript_errors()
        self.assert_no_console_errors(ignored_patterns=ignored_patterns)
        self.assert_no_failed_requests(ignored_patterns=ignored_patterns)
        self.assert_no_http_errors(ignored_patterns=ignored_patterns)
