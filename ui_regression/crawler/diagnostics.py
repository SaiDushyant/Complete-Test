"""
Diagnostic Telemetry & Runtime Error Monitor for UI Regression Crawlers and Comparers.
Monitors and captures:
- Console messages (errors, warnings)
- Uncaught JavaScript exceptions (page errors)
- Failed network requests (CORS failures, net::ERR_*, aborted requests)
- HTTP error responses (HTTP 4xx / 5xx)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from playwright.async_api import Error as PlaywrightError, Page, Request, Response


class AsyncPageDiagnostics:
    """
    Real-time observer attached to an asynchronous Playwright Page instance.
    Monitors invisible background errors (Console, JS runtime, Network failures, HTTP 4xx/5xx).
    """

    def __init__(self, page: Page):
        self.page = page
        self.console_messages: List[Dict[str, Any]] = []
        self.page_errors: List[Dict[str, Any]] = []
        self.failed_requests: List[Dict[str, Any]] = []
        self.http_errors: List[Dict[str, Any]] = []
        self._current_context: Dict[str, str] = {"url": "", "view_name": "", "viewport": ""}

        # Attach Playwright listeners
        self._attach_listeners()

    def set_context(self, url: str, view_name: str = "", viewport: str = "") -> None:
        """Set the active page / view context for attributed error tracking."""
        self._current_context = {
            "url": url,
            "view_name": view_name,
            "viewport": viewport,
        }

    def _attach_listeners(self) -> None:
        """Register event listeners on the underlying page."""
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_page_error)
        self.page.on("requestfailed", self._handle_request_failed)
        self.page.on("response", self._handle_response)

    def _handle_console(self, msg) -> None:
        msg_type = (msg.type or "").lower()
        # Capture errors and warnings
        if msg_type in ("error", "warning"):
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": msg_type,
                "text": msg.text,
                "location": msg.location if hasattr(msg, "location") else {},
                "url": self._current_context.get("url", ""),
                "view_name": self._current_context.get("view_name", ""),
                "viewport": self._current_context.get("viewport", ""),
            }
            self.console_messages.append(entry)

    def _handle_page_error(self, error: Exception) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(error),
            "url": self._current_context.get("url", ""),
            "view_name": self._current_context.get("view_name", ""),
            "viewport": self._current_context.get("viewport", ""),
        }
        self.page_errors.append(entry)

    def _handle_request_failed(self, request: Request) -> None:
        failure = request.failure
        failure_text = failure if isinstance(failure, str) else (failure.get("errorText") if isinstance(failure, dict) else str(failure or "Unknown Network Error"))
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "url": request.url,
            "resource_type": request.resource_type,
            "failure": failure_text,
            "page_url": self._current_context.get("url", ""),
            "view_name": self._current_context.get("view_name", ""),
            "viewport": self._current_context.get("viewport", ""),
        }
        self.failed_requests.append(entry)

    def _handle_response(self, response: Response) -> None:
        status = response.status
        if status >= 400:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "status_text": response.status_text,
                "method": response.request.method,
                "url": response.url,
                "page_url": self._current_context.get("url", ""),
                "view_name": self._current_context.get("view_name", ""),
                "viewport": self._current_context.get("viewport", ""),
            }
            self.http_errors.append(entry)

    def get_summary(self) -> Dict[str, Any]:
        """Return a statistical summary of all captured diagnostics."""
        console_errs = [c for c in self.console_messages if c.get("type") == "error"]
        console_warns = [c for c in self.console_messages if c.get("type") == "warning"]
        return {
            "total_errors": len(console_errs) + len(self.page_errors) + len(self.failed_requests) + len(self.http_errors),
            "console_errors_count": len(console_errs),
            "console_warnings_count": len(console_warns),
            "js_page_errors_count": len(self.page_errors),
            "failed_requests_count": len(self.failed_requests),
            "http_errors_count": len(self.http_errors),
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        """Return full diagnostic records and summary."""
        console_errs = [c for c in self.console_messages if c.get("type") == "error"]
        console_warns = [c for c in self.console_messages if c.get("type") == "warning"]
        return {
            "summary": self.get_summary(),
            "console_errors": console_errs,
            "console_warnings": console_warns,
            "js_page_errors": self.page_errors,
            "failed_requests": self.failed_requests,
            "http_errors": self.http_errors,
        }

    def get_current_slice_and_reset(self) -> Dict[str, Any]:
        """
        Get diagnostics recorded since the last slice and reset the buffers.
        Useful when tracking per-page or per-view metrics.
        """
        diagnostics = self.get_diagnostics()
        self.console_messages = []
        self.page_errors = []
        self.failed_requests = []
        self.http_errors = []
        return diagnostics
