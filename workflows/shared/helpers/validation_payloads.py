"""
<<<<<<< HEAD
Validation and Security Test Payloads & Attack Vectors.
Shared datasets for SQL injection, XSS, boundary numbers, date ranges,
disallowed file formats, email/phone/password validation across all portals.
"""

from __future__ import annotations

from typing import List, Tuple

# ==============================================================================
# 1. SQL INJECTION (SQLi) ATTACK VECTORS
# ==============================================================================

SQLI_PAYLOADS: List[Tuple[str, str]] = [
    ("' OR '1'='1", "SQLi Auth Bypass Single Quote Tautology"),
    ('" OR ""="', "SQLi Auth Bypass Double Quote Tautology"),
    ("admin' --", "SQLi Comment Truncation"),
    ("' OR 1=1#", "SQLi Hash Comment Bypass"),
    ("10098 OR 1=1", "SQLi Numeric Parameter Tautology"),
    ("10098; DROP TABLE users;--", "SQLi Stacked Query Dropping Table"),
    ("10098 UNION SELECT 1,2,3,4,5--", "SQLi Union-Based Extraction"),
    ("price ASC; SELECT * FROM credentials", "SQLi Column Order Injection"),
    ("'; WAITFOR DELAY '0:0:5'--", "SQLi Time-based Blind Injection"),
    ("Rejected: ' OR (SELECT COUNT(*) FROM admin) > 0 --", "SQLi Remarks Field Injection"),
]

SQLI_PAYLOADS_SHORT: List[Tuple[str, str]] = SQLI_PAYLOADS[:5]

# ==============================================================================
# 2. CROSS-SITE SCRIPTING (XSS) ATTACK VECTORS
# ==============================================================================

XSS_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1;</script>", "Reflected/Stored XSS Standard Script Tag"),
    ('"><img src=x onerror=window.xss_detected=1>', "DOM/Attribute Breakout Image OnError XSS"),
    ("<svg/onload=window.xss_detected=1>", "Inline SVG Auto-Executing Onload XSS"),
    ('<iframe src="javascript:window.xss_detected=1"></iframe>', "Iframe JavaScript URI XSS"),
    ('<body onload=window.xss_detected=1>', "Body Tag Onload XSS"),
]

XSS_PAYLOADS_SHORT: List[Tuple[str, str]] = XSS_PAYLOADS[:3]

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

INVALID_AMOUNTS: List[Tuple[str, str]] = [
    ("0", "Zero amount"),
    ("-1", "Negative integer amount"),
    ("-0.01", "Negative fractional amount"),
    ("abc", "Alphabetic in amount field"),
    ("!@#$%", "Special chars in amount field"),
    ("99999999999", "Overflow amount"),
]

# ==============================================================================
# 4. LOT SIZE BOUNDARIES (Trading)
# ==============================================================================

INVALID_LOT_SIZES: List[Tuple[str, str]] = [
    ("0.00", "Sub-minimum zero lot size"),
    ("-1.00", "Negative lot size integer"),
    ("-0.01", "Negative fractional lot size"),
    ("0.0001", "Sub-micro fractional lot precision"),
    ("100.01", "Excessive volume above maximum lot limit"),
    ("99999", "Astronomical volume input"),
    ("0.015", "Invalid non-standard step increment"),
]

VALID_LOT_SIZES: List[Tuple[str, str]] = [
    ("0.01", "Minimum standard micro lot"),
    ("0.10", "Mini lot volume"),
    ("1.00", "Standard lot"),
    ("5.00", "Multi-lot volume"),
    ("10.00", "Institutional lot size"),
]

# ==============================================================================
# 5. NUMERIC PRICE BOUNDARIES (SL, TP, Trigger)
# ==============================================================================

INVALID_PRICE_VALUES: List[Tuple[str, str]] = [
    ("0", "Zero price (invalid level)"),
    ("-1.5000", "Negative price"),
    ("-0.0001", "Tiny negative price"),
    ("99999999", "Astronomical price overflow"),
]

# ==============================================================================
# 6. EMAIL FORMAT PAYLOADS
# ==============================================================================

INVALID_EMAILS: List[Tuple[str, str]] = [
    ("abc", "No @ symbol"),
    ("abc@", "No domain after @"),
    ("@test.com", "No local part before @"),
    ("abc test@test.com", "Space in local part"),
    ("abc@.com", "Domain starts with dot"),
    ("abc@test", "No TLD"),
    ("ab@c@test.com", "Multiple @ symbols"),
]

SQLI_EMAIL_PAYLOADS: List[Tuple[str, str]] = [
    ("' OR '1'='1", "SQLi Auth Bypass in Email"),
    ('" OR ""="', "SQLi Double Quote Bypass in Email"),
    ("admin'--", "SQLi Comment Truncation in Email"),
    ("' OR 1=1#", "SQLi Hash Bypass in Email"),
]

XSS_EMAIL_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1;</script>", "XSS Script Tag in Email"),
    ('"><img src=x onerror=window.xss_detected=1>', "XSS Image OnError in Email"),
    ("<svg/onload=window.xss_detected=1>", "XSS SVG Onload in Email"),
]

# ==============================================================================
# 7. PASSWORD WEAKNESS PAYLOADS
# ==============================================================================

WEAK_PASSWORDS: List[Tuple[str, str]] = [
    ("123456", "Numeric sequence"),
    ("password", "Common dictionary word"),
    ("qwerty", "Keyboard pattern"),
    ("abc123", "Alphanumeric pattern"),
    ("pass", "Too short"),
    ("        ", "Whitespace only"),
]

# ==============================================================================
# 8. PHONE NUMBER VALIDATION PAYLOADS
# ==============================================================================

INVALID_PHONE_NUMBERS: List[Tuple[str, str]] = [
    ("abcdefgh", "Alphabetic phone number"),
    ("+++--", "Special chars only"),
    ("123", "Too short"),
    ("12345678901234567890", "Too long (20 digits)"),
    ("' OR 1=1--", "SQLi in phone field"),
    ("<script>window.xss_detected=1</script>", "XSS in phone field"),
]

VALID_PHONE_NUMBERS: List[Tuple[str, str]] = [
    ("+919876543210", "International format with country code"),
    ("9876543210", "10-digit local format"),
]

# ==============================================================================
# 9. NAME / TEXT FIELD FUZZING
# ==============================================================================

SQLI_NAME_PAYLOADS: List[Tuple[str, str]] = [
    ("' OR 1=1--", "SQLi in name field"),
    ("'; DROP TABLE users;--", "SQLi Drop Table in name"),
]

XSS_NAME_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1;</script>", "XSS Script Tag in name"),
    ("<svg/onload=window.xss_detected=1>", "XSS SVG Onload in name"),
]

# ==============================================================================
# 10. DATE FIELD & BOUNDARY RANGES
# ==============================================================================

DATE_BOUNDARY_PAYLOADS: List[Tuple[str, str, str]] = [
    ("2026-12-31", "2026-01-01", "Inverted date range: From > To"),
    ("2035-01-01", "2035-12-31", "Future date range beyond system epoch"),
    ("1990-01-01", "1990-12-31", "Past date range before system inception"),
    ("invalid-date", "invalid-date", "Malformed non-date string format"),
]

INVALID_DATE_PAYLOADS: List[Tuple[str, str, str]] = [
    ("2026-10-05", "2026-09-01", "Inverted range: From > To"),
    ("2099-01-01", "2099-12-31", "Far future dates"),
    ("2000-01-01", "2000-01-01", "Same day (valid boundary)"),
]

SQLI_DATE_PAYLOADS: List[Tuple[str, str]] = [
    ("2026-01-01' OR '1'='1", "SQLi in From Date field"),
    ("2026-01-01; DROP TABLE history;--", "SQLi Stacked Query in Date"),
]

XSS_DATE_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1</script>", "XSS in Date field"),
    ("<svg/onload=window.xss_detected=1>", "SVG XSS in Date field"),
]

DATE_FUZZ_PAYLOADS: List[Tuple[str, str]] = [
    ("9999-99-99", "Invalid calendar date"),
    ("2026-02-31", "Feb 31 invalid date"),
    ("invalid-date", "String text in date input"),
    ("0000-00-00", "Zero date"),
    ("2026/12/31", "Slash separated date"),
]

# ==============================================================================
# 11. SEARCH / GENERAL INPUT FUZZING
# ==============================================================================

SEARCH_FUZZ_PAYLOADS: List[Tuple[str, str]] = [
    ("NONEXISTENT_SYMBOL_XYZ_99999", "Non-existent Symbol"),
    ("EUR/USD", "Slash Separator"),
    ("EUR-USD", "Dash Separator"),
    ("EUR USD", "Space Separator"),
    ("<script>alert('search')</script>", "XSS in Search Input"),
    ("' OR '1'='1", "SQLi in Search Input"),
    ("SELECT * FROM symbols", "SQL Query in Search Input"),
    ("`~!@#$%^&*()_+=[]{}|;:',.<>?/", "Special Character Blast"),
]

# ==============================================================================
# 12. REFERRAL / OPTIONAL TEXT FIELD FUZZING
# ==============================================================================

SQLI_REFERRAL_PAYLOADS: List[Tuple[str, str]] = [
    ("'; DROP TABLE users;--", "SQLi Drop Table in referral"),
    ("' OR 1=1--", "SQLi Tautology in referral"),
]

XSS_REFERRAL_PAYLOADS: List[Tuple[str, str]] = [
    ("<svg onload=window.xss_detected=1>", "XSS SVG Onload in referral"),
    ("<script>window.xss_detected=1</script>", "XSS Script in referral"),
]

# ==============================================================================
# 13. DISALLOWED FILE EXTENSIONS & MIME TYPES
# ==============================================================================

DISALLOWED_FILE_PAYLOADS: List[Tuple[str, str, str]] = [
    ("shell.php", "<?php echo 'malicious shell'; ?>", "Server-side executable PHP script"),
    ("malicious.pdf.exe", "MZ\x90\x00\x03\x00\x00\x00", "Double extension Windows executable"),
    ("exploit.svg", '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', "SVG with embedded JavaScript"),
    ("zero_byte.png", "", "Corrupted 0-byte image file"),
]
=======
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

>>>>>>> origin/feature/client-portal-validation-dhanya
