"""
Standardized HTTP Error Envelopes for Mock Testing.
Provides mock error payloads for status codes 400, 401, 403, 404, 422, 429, 500, 502, 503, 504.
"""

from typing import Any, Dict

HTTP_400_BAD_REQUEST: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Bad Request",
    "message": "The request payload was malformed or failed validation rules.",
}

HTTP_401_UNAUTHORIZED: Dict[str, Any] = {
    "status": 401,
    "success": False,
    "error": "Unauthorized",
    "message": "Authentication session token has expired or is invalid. Please log in again.",
    "code": "SESSION_EXPIRED",
}

HTTP_403_FORBIDDEN: Dict[str, Any] = {
    "status": 403,
    "success": False,
    "error": "Forbidden",
    "message": "Access to the requested resource is denied by role security policy.",
    "code": "ACCESS_DENIED",
}

HTTP_404_NOT_FOUND: Dict[str, Any] = {
    "status": 404,
    "success": False,
    "error": "Not Found",
    "message": "The requested entity or endpoint could not be found on server.",
}

HTTP_422_UNPROCESSABLE_ENTITY: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Unprocessable Entity",
    "message": "Validation failed for one or more fields.",
    "errors": {
        "amount": ["Amount must be greater than or equal to $10.00."],
        "email": ["Email address format is invalid."],
    },
}

HTTP_429_TOO_MANY_REQUESTS: Dict[str, Any] = {
    "status": 429,
    "success": False,
    "error": "Too Many Requests",
    "message": "Rate limit exceeded. Please wait 60 seconds before retrying.",
    "retry_after_seconds": 60,
}

HTTP_500_INTERNAL_SERVER_ERROR: Dict[str, Any] = {
    "status": 500,
    "success": False,
    "error": "Internal Server Error",
    "message": "An unexpected error occurred on the server. Our engineering team has been notified.",
}

HTTP_502_BAD_GATEWAY: Dict[str, Any] = {
    "status": 502,
    "success": False,
    "error": "Bad Gateway",
    "message": "Upstream liquidity bridge or execution gateway failed to respond.",
}

HTTP_503_SERVICE_UNAVAILABLE: Dict[str, Any] = {
    "status": 503,
    "success": False,
    "error": "Service Unavailable",
    "message": "System is currently undergoing scheduled maintenance. Please check back shortly.",
    "maintenance_until": "2026-10-03T18:00:00Z",
}

HTTP_504_GATEWAY_TIMEOUT: Dict[str, Any] = {
    "status": 504,
    "success": False,
    "error": "Gateway Timeout",
    "message": "The request to the upstream trading server timed out.",
}
