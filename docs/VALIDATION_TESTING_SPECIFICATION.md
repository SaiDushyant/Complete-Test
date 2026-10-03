# Comprehensive Validation Testing Specification & Element Catalog

This document defines the **Validation Testing Architecture**, **Testing Rules**, and **Page-by-Page Element Inventory** for the complete platform. It serves as the definitive technical standard for AI agents and test engineers implementing automated validation suites across the **Admin Portal**, **Client Portal**, and **Trade Terminal**.

---

## 1. What is Validation Testing?

Validation Testing verifies **element-level behavior, boundary conditions, input sanitization, form logic, button states, and on-page mathematical calculations**.

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE 6 PILLARS OF VALIDATION TESTING                          │
├──────────────────────────┬──────────────────────────┬────────────────────────────────────┤
│ 1. Textbox & Inputs      │ 2. Buttons & Actions     │ 3. Dropdowns & Selects             │
│ • Empty / Whitespace     │ • Empty form submissions │ • Unselected default state         │
│ • Min / Max boundaries   │ • Double-click prevention│ • Dependent dropdown update        │
│ • Special chars & string │ • Disabled state rules   │ • Search filtering options         │
│ • SQLi & XSS payloads    │ • SweetAlert error modals│ • Dynamic options reflection       │
├──────────────────────────┼──────────────────────────┼────────────────────────────────�```text
workflows/
│
├── admin_portal/                             # Admin Validation Suites (9 suites / 129 tests)
│   ├── pages/                                # Page Object Models
│   ├── fixtures/                             # Authenticated fixtures & page state
│   └── tests/
│       ├── test_val_admin_orders_calc.py     # 🧮 Order calculations, A/B Book totals, user margins
│       ├── test_val_admin_order_inputs.py    # 📝 Order entry, lot sizes, edit modal input boundaries
│       ├── test_val_admin_user_management.py # 👤 Add/edit user form inputs, password & email checks
│       ├── test_val_admin_user_document.py   # 📄 KYC document status transitions & remarks validation
│       ├── test_val_admin_deposit_withdraw.py# 💳 Deposit/withdraw approval, rejection, and credit inputs
│       ├── test_val_admin_leads_import.py    # 📊 Lead creation, CSV/Excel file validation, bad rows
│       ├── test_val_admin_mam_pamm.py        # 👥 Allocation percentages, follower lot calculations
│       ├── test_val_admin_role_permission.py # 🛡️ Role CRUD inputs & permission button states
│       └── test_val_admin_date_filters.py    # 📅 Date range boundaries ("From > To") across all 10 logs
│
├── client_portal/                            # Client Validation Suites (13 suites / 85 tests)
│   ├── pages/                                # Page Object Models
│   ├── fixtures/                             # Client authenticated fixtures
│   └── tests/
│       ├── test_val_all_elements_labels_dropdowns.py # 🔍 Exhaustive labels, dropdowns, checkboxes
│       ├── test_val_client_auth_inputs.py    # 🔐 2-step signup inputs, weak passwords, SQLi/XSS
│       ├── test_val_client_deposit.py        # 💳 Min/max deposit bounds, proof dropzone extensions
│       ├── test_val_client_withdraw.py       # 🚫 Zero/negative amounts, KYC locks, margin buffers
│       ├── test_val_client_internal_transfer.py# 🔁 Account-to-wallet arithmetic, balance exhaustion
│       ├── test_val_client_kyc_upload.py     # 📁 Allowed document formats, file size constraints
│       ├── test_val_client_copy_trading.py   # 📈 Investment minimums, profit-share deductions
│       ├── test_val_client_dashboard.py      # 📊 Dashboard metrics cards formatting
│       ├── test_val_client_mam.py            # 👥 MAM search SQLi/XSS resilience & modal lifecycles
│       ├── test_val_client_pamm.py           # 📊 PAMM investment bounds & manager search
│       ├── test_val_client_refer_earn.py     # 🔗 Referral link integrity & metrics cards
│       ├── test_val_client_wallet.py         # 💼 Wallet summary cards & ledger controls
│       └── test_val_client_security_edge_cases.py # 🛡️ Open redirect, logout invalidation, localStorage
│
├── trade_terminal/                           # Trade Terminal Validation Suites (13 suites / 220 tests)
│   ├── pages/                                # Page Object Models
│   ├── fixtures/                             # Trade terminal context & telemetry
│   └── tests/
│       ├── test_val_trade_order_entry.py     # 📈 Lot sizes (0.01-100), SL/TP inverted logic rules
│       ├── test_val_trade_account_metrics.py # 🧮 Live calculations: Balance, Equity, Free Margin, %
│       ├── test_val_trade_watchlist.py       # 🔍 Symbol search, empty search state, ticker replace
│       ├── test_val_trade_network_resilience.py# 📡 WebSocket disconnect, offline banner, auto-reconnect
│       ├── test_val_trade_login.py           # 🔐 Login empty submission, SQLi/XSS, password masking
│       ├── test_val_trade_register.py        # 📝 2-step registration boundaries, terms, referrals
│       ├── test_val_trade_positions.py       # 📊 Inline SL/TP edit, partial close, bulk actions
│       ├── test_val_trade_order_history.py   # 📅 Date range inverted/future boundaries, fuzzing
│       ├── test_val_trade_settings.py        # ⚙️ Directionality, theme toggle, copy multiplier bounds
│       ├── test_val_trade_password_reset.py  # 🔑 Password reset link, email format, token expiry
│       ├── test_val_trade_api_access.py      # 🔌 API token generation, copy feedback, revoke states
│       ├── test_val_trade_profile_menu.py    # 👤 User info display, logout session invalidation
│       └── test_val_trade_support.py         # 💬 Support & fund submenu link integrity
│
└── shared/
    ├── helpers/
    │   ├── validation_payloads.py            # Reusable SQLi, XSS, boundary number, and date payloads
    │   └── math_assertions.py                # Reusable financial & margin calculation formulas
    └── utils/
        ├── test_logger.py                    # Multi-suite test result logger & history manager
        └── diagnostics.py                    # Runtime telemetry (console errors, HTTP 4xx/5xx headers)
```alance exhaustion
│       ├── test_val_client_kyc_upload.py     # 📁 Allowed document formats, file size constraints
│       └── test_val_client_copy_trading.py   # 📈 Investment minimums, profit-share deductions
│
├── trade_terminal/
│   ├── pages/                                # Page Object Models
│   ├── fixtures/                             # Trade terminal context & telemetry
│   └── tests/
│       ├── test_val_trade_order_entry.py     # 📈 Lot sizes (0.01-100), SL/TP inverted logic rules
│       ├── test_val_trade_account_metrics.py # 🧮 Live calculations: Balance, Equity, Free Margin, %
│       ├── test_val_trade_watchlist.py       # 🔍 Symbol search, empty search state, ticker replace
│       └── test_val_trade_network_resilience.py# 📡 WebSocket disconnect, offline banner, auto-reconnect
│
└── shared/
    ├── helpers/
    │   ├── validation_payloads.py            # Reusable SQLi, XSS, boundary number, and date payloads
    │   └── math_assertions.py                # Reusable financial & margin calculation formulas
    └── conftest.py
```

---

## 3. Page-by-Page Element Catalog & Validation Matrix

*(Extracted from recorded live crawler DOM analysis in `ui_regression/element_output/` and `ui_regression/element_output_admin/`)*

### A. Admin Portal Pages

#### 1. Orders & Financial Calculations Subsystem
- **Pages**: `admin_Controlbase_aBook`, `admin_Controlbase_bBook`, `admin_Controlbase_aBookUserMargin`, `admin_Controlbase_bBookUserMargin`, `admin_Controlbase_order_open`, `admin_Controlbase_order_closed`, `admin_Controlbase_order_all`, `admin_Controlbase_orderEditLog`
- **Key Elements**:
  - `#order_id`, `#lot_size`, `#open_price`, `#close_price`, `#sl`, `#tp`, `#comment`
  - `#btnSearch`, `#btnApply`, `#btnReset`, `#btnExportExcel`, `#btnExportPdf`
  - Table Footers: Total Volume, Total PnL, Total Margin, Total Commission
- **Validation Tests to Implement**:
  - **Lot Size Input**: Test `0`, `-1`, `0.0001`, `10000`, `abc`, `' OR 1=1` $\rightarrow$ must show validation error.
  - **SL/TP Logic**: For Buy orders: assert $\text{SL} < \text{Open} < \text{TP}$. Inverted values must trigger error.
  - **Column Calculations**: Assert table footer `Total Volume` equals $\sum \text{Row Volume}$, and `Total PnL` equals $\sum \text{Row PnL}$.
  - **A-Book vs B-Book User Margin**: Verify $\text{User Margin} = (\text{Lot} \times \text{Contract Size} \times \text{Price}) / \text{Leverage}$.

#### 2. User & KYC Document Subsystem
- **Pages**: `admin_Controlbase_user`, `admin_Controlbase_userDocument`, `admin_Controlbase_activeUsers`, `admin_Controlbase_clientAccountRequests`
- **Key Elements**:
  - Modals: `#addNewUserModal`, `#editUserModal`, `#verifyDocModal`, `#remarkModal`
  - Inputs: `#userName`, `#userEmail`, `#userPhone`, `#password`, `#groupSelect`, `#leverageSelect`
  - Buttons: `.btnVerify`, `.btnReject`, `.btnDelete`, `.btnEdit`, `#btnSaveUser`
- **Validation Tests to Implement**:
  - **User Creation Form**: Empty submit $\rightarrow$ highlight all required fields in red.
  - **Email Format**: Validate `user@`, `@test.com`, `user space@test.com` are rejected.
  - **Document Rejection Workflow**: Clicking `Reject` must mandate non-empty remarks in `#remarkModal` before saving.
  - **KYC Status Reflection**: Marking user `Verified` must lock file inputs in Client Portal Settings.

#### 3. Deposit & Withdrawal Management Subsystem
- **Pages**: `admin_Controlbase_deposit`, `admin_Controlbase_withdraw`, `admin_Controlbase_creditList`, `admin_Controlbase_payment`
- **Key Elements**:
  - Buttons: `.btnApprove`, `.btnReject`, `.btnAddCredit`, `.btnDeductCredit`
  - Inputs: `#creditAmount`, `#creditRemarks`, `#depositStatusSelect`
- **Validation Tests to Implement**:
  - **Credit Input**: Negative amounts and zero values blocked.
  - **Deposit Approval**: Approving deposit must update status to `Approved` and update user balance accurately.

#### 4. Lead Management Subsystem
- **Pages**: `admin_Controlbase_leads`, `admin_Controlbase_referReport`
- **Key Elements**:
  - `#addLeadModal`, `#bulkUploadModal`, `#fileUploadInput`, `#leadName`, `#leadEmail`, `#leadPhone`
- **Validation Tests to Implement**:
  - **Bulk Upload**: Uploading `.txt`, `.exe`, or malformed CSV $\rightarrow$ reject with format error message.
  - **Empty Lead Submit**: Submitting empty lead modal $\rightarrow$ trigger validation tooltips.

---

### B. Client Portal Pages

#### 1. Authentication & Registration
- **Pages**: `login`, `register`, `reset`
- **Key Elements**:
  - `#email`, `#password`, `#confirm_password`, `#first_name`, `#last_name`, `#phone`, `#terms_checkbox`, `#btn_submit`
- **Validation Tests to Implement**:
  - **Password Strength**: Mandate $\ge 8$ chars, uppercase, lowercase, digit, and special char. Reject weak passwords (`123456`, `password`).
  - **Password Mismatch**: Confirm password $\ne$ password shows immediate inline error.
  - **Terms Checkbox**: Submitting with `#terms_checkbox` unchecked blocks form submission.

#### 2. Deposit & Withdrawal Forms
- **Pages**: `client-portal_view_deposit`, `client-portal_view_withdraw`
- **Key Elements**:
  - `#deposit_amount`, `#withdraw_amount`, `#payment_method_select`, `#deposit_proof_dropzone`, `#btn_submit_deposit`, `#btn_submit_withdraw`
- **Validation Tests to Implement**:
  - **Deposit Amount**: Min deposit (\$10) and max deposit (\$100,000) boundaries. Zero/negative amounts blocked.
  - **Proof Upload**: Dropzone rejects `.exe`, `.sh`, `.php` files; accepts `.png`, `.jpg`, `.pdf`.
  - **Withdrawal Constraints**: 
    - Attempting to withdraw amount $>$ Account Balance $\rightarrow$ shows "Insufficient balance".
    - Withdrawing when KYC is `Not Verified` $\rightarrow$ shows "KYC verification required before withdrawal".

#### 3. Internal Transfer & Wallet
- **Pages**: `client-portal_view_wallet`, `client-portal_view_internal_transfer`
- **Key Elements**:
  - `#from_account_select`, `#to_account_select`, `#transfer_amount`, `#btn_transfer`
- **Validation Tests to Implement**:
  - **Same Account Transfer**: Selecting identical `From` and `To` account triggers "Source and destination accounts must be different".
  - **Transfer Arithmetic**: Transferring $\$X$ must reduce source by exactly $\$X$ and increase destination by $\$X$.

---

### C. Trade Terminal Pages

#### 1. Order Entry Popup
- **Pages**: `home`, `home_view_dashboard`, `home_view_chart`
- **Key Elements**:
  - `#order_popup`, `#lot_input`, `#order_type_tabs` (Market, Limit, Stop HFT), `#sl_input`, `#tp_input`, `#trigger_price_input`, `#btn_buy`, `#btn_sell`
- **Validation Tests to Implement**:
  - **Lot Size Validation**:
    - `0.00` $\rightarrow$ Rejected ("Lot size must be $\ge 0.01$").
    - `100.01` $\rightarrow$ Rejected ("Exceeds maximum allowable lot size").
    - `0.015` $\rightarrow$ Rejected or rounded to valid step (`0.01`).
  - **Limit Order Prices**:
    - Buy Limit with price $\ge$ current Market Price $\rightarrow$ Rejected.
    - Sell Limit with price $\le$ current Market Price $\rightarrow$ Rejected.
  - **Stop Loss / Take Profit Validation**:
    - Buy order with $\text{SL} \ge \text{Price}$ or $\text{TP} \le \text{Price}$ $\rightarrow$ Immediate validation alert.

#### 2. Account Metrics & Formulas
- **Pages**: `home_view_accountlist`, `home_view_position`
- **Key Elements**:
  - `#account_balance`, `#account_equity`, `#used_margin`, `#free_margin`, `#margin_level_percentage`
- **Validation Tests to Implement**:
  - **Live Math Assertions**:
    $$\text{Equity} = \text{Balance} + \text{Floating PnL}$$
    $$\text{Free Margin} = \text{Equity} - \text{Used Margin}$$
    $$\text{Margin Level \%} = \left(\frac{\text{Equity}}{\text{Used Margin}}\right) \times 100$$
  - **Margin Call Indicator**: When Margin Level $\% \le 100\%$, verify warning banner or red styling is applied.

---

## 4. Comprehensive Security Validation & Vulnerability Prevention

Security validation tests ensure that the platform is fortified against client-side exploitation, input tampering, token spoofing, and sensitive data leakage.

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             SECURITY VALIDATION MATRIX                                   │
├──────────────────────────┬──────────────────────────┬────────────────────────────────────┤
│ 1. Injection Attacks     │ 2. Request & Token Forgery│ 3. Data Leakage & Session Flags   │
│ • SQL Injection (SQLi)   │ • CSRF Token Verification│ • Browser Console Credential Leak  │
│ • Cross-Site Scripting   │ • Hidden Input Tampering │ • Local/Session Storage Inspection │
│ • Header/CRLF Injection  │ • IDOR Role Escalation   │ • HttpOnly, Secure, SameSite Flags │
├──────────────────────────┼──────────────────────────┼────────────────────────────────────┤
│ 4. File Upload Exploits  │ 5. Redirection & Auth    │ 6. Rate Limiting & Brute Force     │
│ • Double extension (.php)│ • Open Redirect (?url=)  │ • Multi-attempt login lockout      │
│ • SVG embedded script    │ • Password cleartext mask│ • Replay transaction prevention    │
│ • MIME-type spoofing     │ • Session invalidation   │ • Rapid double-submit handling     │
└──────────────────────────┴──────────────────────────┴────────────────────────────────────┘
```

---

### A. SQL Injection (SQLi) Input Validation
All textboxes, search inputs, date fields, and query parameters across all portals must neutralize SQL injection attempts:

| Attack Vector | Test Payloads | Target Fields | Verification Assertions |
|---|---|---|---|
| **Authentication Bypass** | `' OR '1'='1`<br>`" OR ""="`<br>`admin' --`<br>`' OR 1=1#` | Login username/email, password, reset token | • Login rejected with *"Invalid credentials"*<br>• Zero authentication state written<br>• No SQL syntax dump in response |
| **Numeric Parameter Injection** | `10098 OR 1=1`<br>`10098; DROP TABLE users;`<br>`10098 UNION SELECT 1,2,3` | Account ID search, Order ID search, Deposit ID lookup | • Search displays *"No records found"* or sanitized match<br>• No database errors (`SQLSTATE`, `syntax error`, `mysql_`) |
| **Filter & Sort Column Injection** | `price ASC; SELECT * FROM credentials`<br>`'; WAITFOR DELAY '0:0:5'--` | DataTable column sort, custom filters | • Default sort applied or input rejected<br>• Query response time remains nominal (< 1.5s) |
| **Form & Remarks Injection** | `Rejected: ' OR (SELECT COUNT(*) FROM admin) > 0 --` | Admin Remarks modal, Lead notes, Comment inputs | • Text treated as literal characters<br>• Displays exact string `Rejected: ' OR ...` in Client Portal |

---

### B. Cross-Site Scripting (XSS) & Content Injection
Verifies that malicious JavaScript cannot execute when rendered in the DOM:

| XSS Type | Test Payloads | Target Fields | Verification Assertions |
|---|---|---|---|
| **Reflected XSS** | `<script>alert('XSS')</script>`<br>`"><img src=x onerror=alert(1)>`<br>`javascript:alert(document.cookie)` | Search inputs, URL query params, custom date filters | • Script does NOT execute (zero browser alert dialogs)<br>• Text is HTML-entity encoded in DOM (`&lt;script&gt;`) |
| **Stored XSS** | `<svg/onload=window.xss_detected=true>`<br>`<iframe src="javascript:alert(1)">`<br>`<a href="javascript:alert(1)">Click</a>` | User first/last name, Symbol description, Lead comments, Group names | • Stored data displays cleanly without executing handlers<br>• `window.xss_detected` remains `undefined` |
| **DOM-based XSS** | `#"><img src=x onerror=prompt(1)>`<br>`?redirect=javascript:void(0)` | Hash routing, redirection URLs, tab hash anchors | • Router ignores script scheme<br>• Fallback to default dashboard view |

---

### C. Cross-Site Request Forgery (CSRF) & State Modification Tokens
Every state-changing HTTP request (`POST`, `PUT`, `DELETE`, `PATCH`) must validate anti-forgery tokens:

```python
def test_val_csrf_token_presence_in_forms(authenticated_admin_page):
    """Verify that all state-changing forms contain a valid, non-empty CSRF token."""
    authenticated_admin_page.goto("/admin/Controlbase/user")
    
    # Locate all form elements
    forms = authenticated_admin_page.locator("form")
    for i in range(forms.count()):
        form = forms.nth(i)
        csrf_input = form.locator("input[name='_csrf'], input[name='csrf_token'], input[name='token']")
        assert csrf_input.count() > 0, f"Form {i} is missing CSRF protection input."
        token_val = csrf_input.first.get_attribute("value")
        assert token_val and len(token_val) >= 16, "CSRF token is empty or too short."
```

- **Tampered Token Rejection**: Altering the CSRF token in DOM to `tampered_invalid_token` before submission must result in HTTP `403 Forbidden` or `419 Authentication Timeout`, and zero database state change.

---

### D. Sensitive Data & Console Leakage Prevention
Ensures that runtime telemetry and client storage never expose confidential credentials:

| Audit Check | Test Procedure | Security Assertion |
|---|---|---|
| **Browser Console Logging** | Inspect all console messages via `PageDiagnostics` during login, deposit, and order flows | • Cleartext passwords (`password=...`) MUST NOT appear in `console.log` / `console.error`<br>• Full credit card numbers or raw secret keys must be suppressed |
| **LocalStorage & SessionStorage** | Read `window.localStorage` and `window.sessionStorage` keys post-login | • Auth tokens should use `HttpOnly` cookies, or if in storage, MUST NOT store unencrypted passwords or admin bypass flags |
| **Network Request Body Masking** | Monitor outbound `fetch` / `XHR` network requests | • Sensitive password inputs must only be sent over encrypted HTTPS `POST` payloads |

---

### E. Client-Side Parameter Tampering & Hidden Input Security
Validates that manipulating client-side hidden fields cannot bypass permissions or alter pricing:

1. **Hidden Permission Flags**:
   - In Admin Portal, modifying `#editUserDoc` or `#deleteUserDoc` hidden input value from `0` to `1` $\rightarrow$ Server-side authorization must still reject the delete request.
2. **Hidden Fee / Spread Tampering**:
   - Modifying hidden markup or fee calculation fields $\rightarrow$ Order execution must recalculate using server-side config.
3. **Account ID Tampering (IDOR)**:
   - Modifying the hidden `account_id` or `user_id` inside withdrawal form to another user's ID $\rightarrow$ Server rejects with *"Unauthorized account transaction"*.

---

### F. File Upload Security & Dropzone MIME Bypasses
For deposit slips (`client-portal_view_deposit`), KYC documents (`userDocument`), and Lead bulk imports (`leads`):

| Test Payload | Description | Expected Security Outcome |
|---|---|---|
| `shell.php` | Server-side executable script | **Rejected**: "Unsupported file format. Only JPG, PNG, PDF allowed." |
| `malicious.pdf.exe` | Double extension bypass | **Rejected**: Blocked based on final extension. |
| `exploit.svg` (with `<script>`) | SVG containing embedded JavaScript | **Sanitized or Rejected**: Converted or stripped of active scripts. |
| `zero_byte.png` | 0-byte corrupted empty file | **Rejected**: "File is empty or corrupted." |
| `oversized_50mb.pdf` | Exceeds 10MB upload limit | **Rejected**: "File size exceeds maximum allowable limit (10MB)." |

---

### G. Open Redirect & Authentication Edge Cases
1. **Open Redirection Parameter**:
   - Attempting `https://stage.xtremenext.com/login?redirect=https://attacker-domain.com`
   - **Assertion**: After login, user is redirected strictly to internal dashboard (`/client-portal` or `/admin/Controlbase/Dashboard`), never to external hosts.
2. **Brute-Force Rate Limiting Response**:
   - Submitting 5 consecutive invalid passwords for a user account.
   - **Assertion**: Form displays rate-limiting delay or CAPTCHA requirement before 6th attempt.
3. **Session Invalidation on Logout**:
   - After clicking Logout, navigating browser "Back" button or reusing old session cookie $\rightarrow$ Must redirect to `/login` and block access to cached dashboard data.

---

## 5. Standardized Test Code Pattern

When writing validation and security tests, use parameterized fixtures and explicit input assertions:

```python
import pytest
from playwright.sync_api import Page, expect

# 1. Parameterized security payloads for input textboxes
SQLI_XSS_PAYLOADS = [
    ("' OR '1'='1", "SQL Injection Authentication Bypass"),
    ("<script>window.pwned=1</script>", "Stored/Reflected XSS Script Tag"),
    ("\"><img src=x onerror=alert(1)>", "Image Tag Event Handler XSS"),
    ("10098; DROP TABLE users;--", "Stacked SQL Query Injection"),
    ("admin'--", "Comment Truncation SQLi"),
]

@pytest.mark.parametrize("payload,description", SQLI_XSS_PAYLOADS)
def test_val_admin_search_security_sanitization(admin_dashboard_page, payload, description):
    """Verify that global and table search inputs sanitize SQLi and XSS payloads."""
    admin_dashboard_page.navigate()
    search_input = admin_dashboard_page.page.locator("input[type='search']").first
    search_input.fill(payload)
    search_input.press("Enter")
    
    # 1. Verify no uncaught script execution
    xss_executed = admin_dashboard_page.page.evaluate("() => window.pwned === 1")
    assert not xss_executed, f"XSS payload executed: {description}"
    
    # 2. Verify clean empty state or sanitized query display
    table_body = admin_dashboard_page.page.locator("table tbody").first
    expect(table_body).not_to_contain_text("SQLSTATE")
    expect(table_body).not_to_contain_text("syntax error")
```

---

## 6. Execution Commands

```bash
# Run all validation and security tests
pytest workflows/ -m validation

# Run security-specific validation suites
pytest workflows/ -k "test_val_security or test_val_auth"

# Run with limited parallel workers to avoid server rate-limiting
pytest workflows/ -m validation -n 2 --slowmo 100
```

