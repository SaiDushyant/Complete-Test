"""
Validation and Security Test Payloads — Extended.
Reusable datasets for SQL injection, XSS, boundary conditions,
email/phone/password format validation, and date fuzzing across all portals.
"""

from typing import List, Tuple

# ─────────────────────────────────────────────
# SQL Injection Payloads
# ─────────────────────────────────────────────
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

# Shorter subset for parametrize where full list is too long
SQLI_PAYLOADS_SHORT: List[Tuple[str, str]] = SQLI_PAYLOADS[:5]

# ─────────────────────────────────────────────
# XSS Payloads
# ─────────────────────────────────────────────
XSS_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1;</script>", "Reflected/Stored XSS Standard Script Tag"),
    ('"><img src=x onerror=window.xss_detected=1>', "DOM/Attribute Breakout Image OnError XSS"),
    ("<svg/onload=window.xss_detected=1>", "Inline SVG Auto-Executing Onload XSS"),
    ('<iframe src="javascript:window.xss_detected=1"></iframe>', "Iframe JavaScript URI XSS"),
    ('<body onload=window.xss_detected=1>', "Body Tag Onload XSS"),
]

# Shorter subset for parametrize
XSS_PAYLOADS_SHORT: List[Tuple[str, str]] = XSS_PAYLOADS[:3]

# ─────────────────────────────────────────────
# Lot Size Boundaries
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Numeric Price Field Boundaries (SL, TP, Trigger)
# ─────────────────────────────────────────────
INVALID_PRICE_VALUES: List[Tuple[str, str]] = [
    ("0", "Zero price (invalid level)"),
    ("-1.5000", "Negative price"),
    ("-0.0001", "Tiny negative price"),
    ("99999999", "Astronomical price overflow"),
]

# ─────────────────────────────────────────────
# Email Format Payloads
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Password Weakness Payloads
# ─────────────────────────────────────────────
WEAK_PASSWORDS: List[Tuple[str, str]] = [
    ("123456", "Numeric sequence"),
    ("password", "Common dictionary word"),
    ("qwerty", "Keyboard pattern"),
    ("abc123", "Alphanumeric pattern"),
    ("pass", "Too short"),
    ("        ", "Whitespace only"),
]

# ─────────────────────────────────────────────
# Phone Number Validation Payloads
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Name / Text Field Fuzzing
# ─────────────────────────────────────────────
SQLI_NAME_PAYLOADS: List[Tuple[str, str]] = [
    ("' OR 1=1--", "SQLi in name field"),
    ("'; DROP TABLE users;--", "SQLi Drop Table in name"),
]

XSS_NAME_PAYLOADS: List[Tuple[str, str]] = [
    ("<script>window.xss_detected=1;</script>", "XSS Script Tag in name"),
    ("<svg/onload=window.xss_detected=1>", "XSS SVG Onload in name"),
]

# ─────────────────────────────────────────────
# Date Field Payloads
# ─────────────────────────────────────────────
INVALID_DATE_PAYLOADS: List[Tuple[str, str, str]] = [
    # (from_date, to_date, description)
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

# ─────────────────────────────────────────────
# Search / General Input Fuzzing
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Referral / Optional Text Field Fuzzing
# ─────────────────────────────────────────────
SQLI_REFERRAL_PAYLOADS: List[Tuple[str, str]] = [
    ("'; DROP TABLE users;--", "SQLi Drop Table in referral"),
    ("' OR 1=1--", "SQLi Tautology in referral"),
]

XSS_REFERRAL_PAYLOADS: List[Tuple[str, str]] = [
    ("<svg onload=window.xss_detected=1>", "XSS SVG Onload in referral"),
    ("<script>window.xss_detected=1</script>", "XSS Script in referral"),
]

# ─────────────────────────────────────────────
# Numeric Amount Field Payloads (PAMM, deposits)
# ─────────────────────────────────────────────
INVALID_AMOUNTS: List[Tuple[str, str]] = [
    ("0", "Zero amount"),
    ("-1", "Negative integer amount"),
    ("-0.01", "Negative fractional amount"),
    ("abc", "Alphabetic in amount field"),
    ("!@#$%", "Special chars in amount field"),
    ("99999999999", "Overflow amount"),
]
