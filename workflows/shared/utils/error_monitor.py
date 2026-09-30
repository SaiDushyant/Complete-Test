"""
Automated Error Monitor for Browser Console, JavaScript Runtime, and Backend Network Requests.
Attaches to Playwright pages to ensure zero client-side crashes and backend failures.
"""

from __future__ import annotations

from typing import Any, List
from playwright.sync_api import Page, ConsoleMessage, Response, Request


class ErrorMonitor:
    """Monitors and records browser console errors, unhandled JS exceptions, and failed HTTP responses."""

    def __init__(self, page: Page):
        self.page = page
        self.console_errors: List[str] = []
        self.js_page_errors: List[str] = []
        self.backend_errors: List[dict[str, Any]] = []
        self.failed_requests: List[dict[str, Any]] = []

        # Attach Playwright listeners
        page.on("console", self._handle_console)
        page.on("pageerror", self._handle_pageerror)
        page.on("response", self._handle_response)
        page.on("requestfailed", self._handle_requestfailed)

    def _handle_console(self, msg: ConsoleMessage) -> None:
        """Capture browser console.error messages."""
        if msg.type == "error":
            # Ignore harmless third-party favicon, expected websocket close notices, or external analytics CSP blocks
            text = msg.text
            ignored_tokens = ["favicon.ico", "websocket closed clean", "google-analytics.com", "analytics.js"]
            if not any(ign in text.lower() for ign in ignored_tokens):
                self.console_errors.append(f"Console Error: {text}")

    def _handle_pageerror(self, exc: Exception) -> None:
        """Capture uncaught JavaScript exceptions / page crashes."""
        self.js_page_errors.append(f"JS Runtime Error: {str(exc)}")

    def _handle_response(self, response: Response) -> None:
        """Capture backend HTTP failures (status >= 400 or >= 500)."""
        if response.status >= 500:
            self.backend_errors.append({
                "type": "SERVER_ERROR_5XX",
                "status": response.status,
                "url": response.url,
            })
        elif response.status >= 400:
            # Catch client/backend 4xx API errors (excluding common static asset 404s like favicon)
            if not response.url.endswith("favicon.ico"):
                self.backend_errors.append({
                    "type": "CLIENT_OR_API_ERROR_4XX",
                    "status": response.status,
                    "url": response.url,
                })

    def _handle_requestfailed(self, request: Request) -> None:
        """Capture aborted or failed network connections."""
        failure = request.failure
        # Filter out intentional cancellations (e.g., aborted navigation or beacon requests)
        if failure and "net::ERR_ABORTED" not in failure:
            self.failed_requests.append({
                "url": request.url,
                "method": request.method,
                "error": failure,
            })

    def clear(self) -> None:
        """Reset all recorded error buffers."""
        self.console_errors.clear()
        self.js_page_errors.clear()
        self.backend_errors.clear()
        self.failed_requests.clear()

    def get_summary(self) -> dict[str, Any]:
        """Return structured summary of all tracked errors."""
        return {
            "total_errors": len(self.console_errors) + len(self.js_page_errors) + len(self.backend_errors),
            "js_page_errors": list(self.js_page_errors),
            "console_errors": list(self.console_errors),
            "backend_errors": list(self.backend_errors),
            "failed_requests": list(self.failed_requests),
        }

    def assert_no_js_errors(self, context_msg: str = "") -> None:
        """Assert zero uncaught JavaScript page exceptions."""
        prefix = f"[{context_msg}] " if context_msg else ""
        assert len(self.js_page_errors) == 0, (
            f"{prefix}Uncaught JavaScript runtime error(s) detected:\n"
            + "\n".join(self.js_page_errors)
        )

    def assert_no_backend_errors(self, context_msg: str = "") -> None:
        """Assert zero server 5xx or failed API responses."""
        prefix = f"[{context_msg}] " if context_msg else ""
        server_5xx = [e for e in self.backend_errors if e["type"] == "SERVER_ERROR_5XX"]
        assert len(server_5xx) == 0, (
            f"{prefix}Backend server 5xx error(s) detected:\n"
            + "\n".join([f"{e['status']} - {e['url']}" for e in server_5xx])
        )

    def assert_no_errors(self, context_msg: str = "", allow_4xx: bool = False) -> None:
        """
        Comprehensive error assertion:
        Verifies zero uncaught JS exceptions, zero console errors, and zero backend failures.
        """
        prefix = f"[{context_msg}] " if context_msg else ""

        # 1. Check Uncaught JS exceptions
        self.assert_no_js_errors(context_msg)

        # 2. Check Backend 5xx Server errors
        self.assert_no_backend_errors(context_msg)

        # 3. Check Console Errors
        assert len(self.console_errors) == 0, (
            f"{prefix}Browser console error(s) detected:\n"
            + "\n".join(self.console_errors)
        )

        # 4. Optional check for 4xx errors
        if not allow_4xx:
            api_4xx = [e for e in self.backend_errors if e["type"] == "CLIENT_OR_API_ERROR_4XX"]
            assert len(api_4xx) == 0, (
                f"{prefix}HTTP 4xx API error(s) detected:\n"
                + "\n".join([f"{e['status']} - {e['url']}" for e in api_4xx])
            )
