"""
Universal Mock Router for Playwright Network Interception.

Provides fluent, thread-safe, and isolated route interception, payload mocking,
network error injection, latency simulation, and request payload capture.
Designed for offline and server-mocked testing across all portals.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Union
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Page, Route, Request

from workflows.shared.utils.logger import get_logger

logger = get_logger("mock_router")


class MockRouter:
    """
    High-level route interceptor and mock manager for Playwright pages.
    Allows registering JSON mock responses, HTTP status overrides, artificial
    network latency, connection aborts, and captured request telemetry.
    """

    def __init__(self, page: Page):
        self.page = page
        self._active_routes: List[Union[str, Pattern]] = []
        self._captured_requests: List[Dict[str, Any]] = []

    @property
    def captured_requests(self) -> List[Dict[str, Any]]:
        """Access list of intercepted requests recorded by capture_requests()."""
        return list(self._captured_requests)

    def mock_json(
        self,
        url_pattern: Union[str, Pattern],
        data: Any,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        delay_ms: int = 0,
    ) -> MockRouter:
        """
        Intercept matching endpoint pattern and return the specified JSON payload.

        Args:
            url_pattern: Glob string or regex pattern (e.g., "**/api/v1/orders**")
            data: Python dict or list to be serialized as JSON response body.
            status: HTTP status code (default 200).
            headers: Optional extra response headers.
            delay_ms: Optional simulated network latency in milliseconds.
        """
        resp_headers = {"Content-Type": "application/json"}
        if headers:
            resp_headers.update(headers)

        body_str = json.dumps(data) if not isinstance(data, str) else data

        def handler(route: Route):
            req = route.request
            logger.debug(f"[MockRouter] Intercepted [{req.method}] {req.url} -> Status {status}")
            if delay_ms > 0:
                self.page.wait_for_timeout(delay_ms)
            route.fulfill(
                status=status,
                headers=resp_headers,
                body=body_str,
            )

        self.page.route(url_pattern, handler)
        self._active_routes.append(url_pattern)
        return self

    def mock_error(
        self,
        url_pattern: Union[str, Pattern],
        status: int = 500,
        error_message: str = "Internal Server Error",
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        delay_ms: int = 0,
    ) -> MockRouter:
        """
        Simulate backend API failures with standardized error envelopes.

        Args:
            url_pattern: Endpoint URL glob or regex.
            status: Error status (400, 401, 403, 404, 422, 429, 500, 502, 503, 504).
            error_message: Human-readable error message.
            error_code: Optional machine-readable error code (e.g., "INVALID_CREDENTIALS").
            extra_data: Optional extra keys merged into the response payload.
            delay_ms: Simulated network delay before error return.
        """
        payload = {
            "success": False,
            "status": status,
            "error": error_message,
            "message": error_message,
        }
        if error_code:
            payload["error_code"] = error_code
        if extra_data:
            payload.update(extra_data)

        return self.mock_json(
            url_pattern=url_pattern,
            data=payload,
            status=status,
            delay_ms=delay_ms,
        )

    def mock_abort(
        self,
        url_pattern: Union[str, Pattern],
        error_code: str = "failed",
    ) -> MockRouter:
        """
        Simulate network connection dropouts or offline state (e.g. DNS failure, connection refused).

        Args:
            url_pattern: Endpoint URL glob or regex.
            error_code: Playwright abort reason: 'aborted', 'accessdenied', 'addressunreachable',
                        'blockedbyclient', 'blockedbyresponse', 'connectionaborted',
                        'connectionclosed', 'connectionfailed', 'connectionrefused',
                        'connectionreset', 'internetdisconnected', 'timedout', 'failed'.
        """
        def handler(route: Route):
            logger.debug(f"[MockRouter] Aborting [{route.request.method}] {route.request.url} ({error_code})")
            route.abort(error_code)

        self.page.route(url_pattern, handler)
        self._active_routes.append(url_pattern)
        return self

    def capture_requests(
        self,
        url_pattern: Union[str, Pattern],
        mock_response_data: Optional[Any] = None,
        status: int = 200,
    ) -> MockRouter:
        """
        Intercepts requests matching url_pattern and records their HTTP method, headers,
        query parameters, and post_data for test assertions.
        """
        def handler(route: Route):
            req = route.request
            post_data = None
            try:
                post_data = req.post_data_json if req.post_data else None
            except Exception:
                post_data = req.post_data

            record = {
                "url": req.url,
                "method": req.method,
                "headers": req.headers,
                "post_data": post_data,
                "query_params": parse_qs(urlparse(req.url).query),
            }
            self._captured_requests.append(record)
            logger.debug(f"[MockRouter] Captured request: {req.method} {req.url}")

            if mock_response_data is not None:
                route.fulfill(
                    status=status,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps(mock_response_data),
                )
            else:
                route.continue_()

        self.page.route(url_pattern, handler)
        self._active_routes.append(url_pattern)
        return self

    def mock_custom(
        self,
        url_pattern: Union[str, Pattern],
        handler_fn: Callable[[Route], None],
    ) -> MockRouter:
        """
        Register a custom callback function to handle complex routing logic.
        """
        self.page.route(url_pattern, handler_fn)
        self._active_routes.append(url_pattern)
        return self

    def unroute(self, url_pattern: Union[str, Pattern]) -> None:
        """Remove mock handler for a specific URL pattern."""
        try:
            self.page.unroute(url_pattern)
            if url_pattern in self._active_routes:
                self._active_routes.remove(url_pattern)
        except Exception as e:
            logger.debug(f"Failed to unroute {url_pattern}: {e}")

    def clear(self) -> None:
        """Remove all active mock handlers and reset captured telemetry."""
        for pattern in list(self._active_routes):
            try:
                self.page.unroute(pattern)
            except Exception:
                pass
        self._active_routes.clear()
        self._captured_requests.clear()
