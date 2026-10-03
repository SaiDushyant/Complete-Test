"""
Reusable Validation Testing Payloads and Security Attack Vectors.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md
"""

from __future__ import annotations

from typing import List, Tuple

# ==============================================================================
# 1. SQL INJECTION (SQLi) ATTACK VECTORS
# ==============================================================================

SQLI_PAYLOADS: List[Tuple[str, str]] = [
    ("' OR '1'='1", "Classic boolean SQLi authentication bypass"),
    ("\" OR \"\"=\"", "Double-quote boolean SQLi"),
    ("admin' --", "Comment truncation SQLi"),
    ("10098; DROP TABLE users;--", "Stacked SQL query injection"),
    ("10098 UNION SELECT 1,2,3--", "UNION-based database extraction"),
    ("' OR 1=1#", "Hash comment boolean injection"),
]

# ==============================================================================
# 2. CROSS-SITE SCRIPTING (XSS) ATTACK VECTORS
# ==============================================================================

XSS_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.pwned=1</script>", "Reflected/Stored script tag XSS"),
    ("\"><img src=x onerror=alert(1)>", "Image onerror event handler XSS"),
    ("<svg/onload=window.xss_detected=true>", "SVG onload inline execution XSS"),
    ("javascript:alert(document.cookie)", "Javascript scheme URL injection"),
    ("<iframe src=\"javascript:alert(1)\">", "Iframe embedded script XSS"),
]

# ==============================================================================
# 3. BOUNDARY NUMBERS & NUMERIC INPUT TEST CASES
# ==============================================================================

BOUNDARY_AMOUNTS: List[Tuple[str, str]] = [
    ("0", "Zero amount boundary"),
    ("-10.00", "Negative decimal amount"),
    ("-1", "Negative integer amount"),
    ("0.0001", "Sub-cent micro fractional amount"),
    ("100000000.00", "Excessive large hundred-million amount"),
    ("abc", "Alphabetic non-numeric string"),
    ("!@#$%", "Special characters string"),
    ("1e10", "Scientific exponential notation string"),
    ("   ", "Whitespace-only input"),
]

# ==============================================================================
# 4. DATE PICKER & BOUNDARY RANGES
# ==============================================================================

DATE_BOUNDARY_PAYLOADS: List[Tuple[str, str, str]] = [
    ("2026-12-31", "2026-01-01", "Inverted date range: From > To"),
    ("2035-01-01", "2035-12-31", "Future date range beyond system epoch"),
    ("1990-01-01", "1990-12-31", "Past date range before system inception"),
    ("invalid-date", "invalid-date", "Malformed non-date string format"),
]

# ==============================================================================
# 5. DISALLOWED FILE EXTENSIONS & MIME TYPES
# ==============================================================================

DISALLOWED_FILE_PAYLOADS: List[Tuple[str, str, str]] = [
    ("shell.php", "<?php echo 'malicious shell'; ?>", "Server-side executable PHP script"),
    ("malicious.pdf.exe", "MZ\x90\x00\x03\x00\x00\x00", "Double extension Windows executable"),
    ("exploit.svg", "<svg xmlns=\"http://www.w3.org/2000/svg\"><script>alert(1)</script></svg>", "SVG with embedded JavaScript"),
    ("zero_byte.png", "", "Corrupted 0-byte image file"),
]
