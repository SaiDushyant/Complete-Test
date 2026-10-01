"""
Reusable Validation & Security Testing Payloads for Client Portal, Admin Portal, and Trade Terminal.
Reference: docs/VALIDATION_TESTING_SPECIFICATION.md
"""

from __future__ import annotations
from typing import List, Tuple

# SQL Injection Payloads for Text/Auth/Search inputs
SQLI_AUTH_PAYLOADS: List[Tuple[str, str]] = [
    ("' OR '1'='1", "Classic OR 1=1 string bypass"),
    ('" OR ""="', "Double quote string bypass"),
    ("admin' --", "Comment truncation authentication bypass"),
    ("' OR 1=1#", "Hash comment authentication bypass"),
    ("admin'/*", "Inline comment block authentication bypass"),
]

SQLI_NUMERIC_PAYLOADS: List[Tuple[str, str]] = [
    ("10098 OR 1=1", "Numeric parameter OR injection"),
    ("10098; DROP TABLE users;--", "Stacked SQL statement injection"),
    ("10098 UNION SELECT 1,2,3--", "Union based information schema injection"),
]

# Cross-Site Scripting (XSS) Payloads
XSS_REFLECTED_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1</script>", "Basic script tag injection"),
    ("\"><img src=x onerror=window.xss_detected=1>", "Image tag error event handler injection"),
    ("<svg/onload=window.xss_detected=1>", "SVG onload event handler injection"),
    ("javascript:window.xss_detected=1", "JavaScript URI scheme payload"),
]

# Weak Passwords for validation checks
WEAK_PASSWORDS: List[Tuple[str, str]] = [
    ("123456", "Too short and numeric only"),
    ("password", "Dictionary common word"),
    ("Pass1", "Under minimum length (< 8 chars)"),
    ("alllowercase123!", "Missing uppercase character"),
    ("ALLUPPERCASE123!", "Missing lowercase character"),
    ("NoSpecialChars123", "Missing special symbol character"),
    ("NoDigits!Password", "Missing numeric digit"),
]

# Invalid / Malformed Emails
INVALID_EMAILS: List[Tuple[str, str]] = [
    ("invalid_email", "Missing @ symbol and domain"),
    ("user@", "Missing domain name"),
    ("@example.com", "Missing local part"),
    ("user space@example.com", "Contains illegal whitespace"),
    ("user@domain..com", "Consecutive dots in domain"),
]

# Disallowed & Malicious File Upload extensions
DISALLOWED_FILE_EXTENSIONS: List[str] = [
    ".exe",
    ".php",
    ".sh",
    ".py",
    ".bat",
    ".vbs",
    ".js",
]

# Allowed File Extensions for Dropzones
ALLOWED_DOCUMENT_EXTENSIONS: List[str] = [
    ".png",
    ".jpg",
    ".jpeg",
    ".pdf",
]

# Aliases for convenience across test suites
SQLI_PAYLOADS = SQLI_AUTH_PAYLOADS + SQLI_NUMERIC_PAYLOADS
DISALLOWED_EXTENSIONS = DISALLOWED_FILE_EXTENSIONS
ACCEPTED_EXTENSIONS = ALLOWED_DOCUMENT_EXTENSIONS

NUMERIC_BOUNDARY_VALUES: List[Tuple[str, str]] = [
    ("0", "Zero amount"),
    ("-1", "Negative 1 boundary"),
    ("-500.50", "Negative floating point value"),
    ("0.0001", "Sub-penny fractional precision"),
    ("999999999999999", "Astronomical integer value exceeding capacity"),
]

