# Complete Test Automation Framework

A unified, production-grade automated testing platform built with Python and Playwright. The repository provides two logically independent, complementary testing systems designed for high-confidence web application validation:

```text
                        COMPLETE-TEST REPOSITORY
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ui_regression/         workflows/            mock testing/
       (29 tests)            (1,389 tests)          (269 tests)
              │                    │                    │
       DOM / Structure      Live Validation       Network Mocking
              │             & User Journeys       & Fault Injection
       crawler + comparer   ┌──────┼──────┐       ┌─────┼─────┐
                            Trade Admin Client    Trade Admin Client
```

---

## 📑 Core Documentation Index

| Documentation Guide | Description |
| :--- | :--- |
| **[How to Run Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/HOW_TO_RUN.md)** | Complete CLI operational guide, execution recipes, parallel testing, validation suites, mock testing, and reporting formats. |
| **[Validation Testing Specification](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/VALIDATION_TESTING_SPECIFICATION.md)** | Definitive specification for 434 validation tests across Admin, Client, and Trade portals, attack vectors, and element catalogs. |
| **[Mock Testing Specification](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/MOCK_TESTING_SPECIFICATION.md)** | Definitive specification and implementation guide for 269 mock tests, Playwright network interception, MockRouter, and fault injection. |
| **[Scripts & Test Runners Catalog](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/scripts/README.md)** | Detailed documentation of every script in `scripts/`, flags, and usage recommendations. |
| **[Architecture Overview](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/architecture.md)** | Explains why UI regression, behavioral workflows, and mock suites are structured, and details boundary isolation. |
| **[Developer Onboarding Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/developer-guide.md)** | Complete walkthrough from environment setup to creating Page Objects, writing tests, and opening PRs. |
| **[Workflow Testing Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/workflow-testing.md)** | Page Object Model patterns, fixture injection, wait strategies, assertions, screenshot/trace capture, and debugging. |
| **[Git & GitHub Team Workflow](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/git-workflow.md)** | Branching strategy, setup commands for all OS, safe rebasing, merge conflict resolution, and PR guidelines. |
| **[Domain Ownership Matrix](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/ownership.md)** | Directory ownership boundaries for Developer 1 (Trade), Developer 2 (Admin), and Developer 3 (Client). |
| **[UI Regression Engine Reference](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/DOCUMENTATION.md)** | Deep technical dive into the 6-tier DOM matching algorithm, canonical routing, and noise filtering. |

---

## 🏛️ Three Comprehensive Testing Layers (1,687 Total Tests)

### 1. `ui_regression/` — DOM Structural Regression & Drift Detection (29 Tests)
> **Answers**: *"Has the UI or DOM structure changed unexpectedly from the approved baseline?"*
- Crawls web applications across 5 responsive breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`).
- Extracts canonical live element trees and compares against version-controlled ground truth baselines.
- Employs a 6-tier element matching algorithm with dynamic noise filtering.
- Preserves version-controlled baselines under `ui_regression/element_output/` and `ui_regression/element_output_admin/`.

### 2. `workflows/` — Behavioral Workflows & Validation Testing (1,389 Tests)
> **Answers**: *"Can a user successfully complete critical application workflows and are all inputs, boundaries, and math calculations strictly validated?"*
- Co-locates both **End-to-End Workflow Journeys** (`test_<portal>_*.py` — 955 tests) and **Element-Level Validation Suites** (`test_val_<portal>_*.py` — 434 tests):
  - **Trade Terminal** (`workflows/trade_terminal/` — 395 tests: 175 workflow + 220 validation tests) — Maintained by Developer 1
  - **Admin Portal** (`workflows/admin_portal/` — 572 tests: 443 workflow + 129 validation tests) — Maintained by Developer 2
  - **Client Portal** (`workflows/client_portal/` — 246 tests: 161 workflow + 85 validation tests) — Maintained by Developer 3
  - **Shared & Integrations** (`workflows/shared/` — 176 tests) — Cross-portal E2E, Manager Hierarchy Isolation, A/B Book Lifecycle, Financial Calculation Verification

### 3. Mock Testing & Network Interception Layer (269 Tests)
> **Answers**: *"How does the frontend react under severe API errors, 429 rate limits, network disconnects, and edge-case account states?"*
- 100% offline network interception using `MockRouter` and `page.route()`.
- **Trade Terminal Mock Suite** (`workflows/trade_terminal/tests/mock/` — 96 tests across 13 suites): Order execution, quotes, positions, chart feeds, account metrics, API keys, and server 500/502/503/504 errors.
- **Client Portal Mock Suite** (`workflows/client_portal/tests/mock/` — 92 tests across 7 suites): Auth/security, payment gateways, withdrawals, wallet transfers, KYC, PAMM/MAM, settings, and rate limiting.
- **Admin Portal Mock Suite** (`workflows/admin_portal/tests/mock/` — 81 tests across 22 suites): SuperAdmin auth, user CRUD, deposit/withdrawal approvals, KYC review, LP feeds, risk books, and cron triggers.

---

## 🚀 Quick Execution Guide

```bash
# 1. Activate Environment
conda activate playwright-env

# 2. Run Entire Platform Mock Testing Suite (269 Tests in ~16s)
python scripts/run_mock_tests.py --portal all

# 3. Run Portal-Specific Mock Tests
python scripts/run_mock_tests.py --portal trade
python scripts/run_mock_tests.py --portal admin
python scripts/run_mock_tests.py --portal client

# 4. Run Platform Validation Suite (434 Tests)
pytest -m validation -v

# 5. Master Runner - Run all workflows headless
python scripts/run_all_workflows.py

# 6. Dynamic Parallel Execution across 4 workers
python scripts/run_mock_tests.py -n 4

# 7. Smoke Test Suite (< 2 mins)
python scripts/run_smoke_tests.py

# 8. Full UI Regression Pipeline (Re-crawl + Compare + Diagnostics)
python scripts/run_ui_full_pipeline.py
```

---

## 📁 Repository Directory Structure

```text
Complete-Test/
│
├── config/                           # Centralized configuration loaded from .env
│   └── settings.py
│
├── auth/                             # Cached authentication storage states (gitignored)
│
├── reports/                          # Segregated multi-suite reporting and history
│   ├── validations/                  # Active validation logs, screenshots, diagnostics, traces & history
│   ├── mock/                         # Active mock test logs, results JSON, individual traces & history
│   ├── workflows/                    # Active workflow logs, screenshots, traces & history
│   └── ui_regression/                # DOM drift comparison reports & history
│
├── ui_regression/                    # DOM-level structural/UI regression testing (29 tests)
│   ├── crawler/                      # Multi-viewport crawler & element extractor
│   ├── comparer/                     # 6-tier matching engine & drift comparer
│   ├── element_output/               # Version-controlled baseline snapshots (Client)
│   ├── element_output_admin/         # Version-controlled baseline snapshots (Admin)
│   └── tests/                        # DOM regression unit & accuracy tests
│
├── workflows/                        # Core Testing Hierarchy (1,658 tests)
│   ├── conftest.py                   # Shared browser fixture export
│   │
│   ├── trade_terminal/               # Developer 1 Domain: Trade Terminal (491 tests)
│   │   ├── pages/                    # Trade POMs (LoginPage, OrderEntryPage, WatchlistPage, etc.)
│   │   ├── fixtures/                 # Trade fixtures & authenticated contexts
│   │   └── tests/                    # Workflow (test_trade_*.py), Validation (test_val_trade_*.py), Mock (tests/mock/)
│   │
│   ├── admin_portal/                 # Developer 2 Domain: Admin Portal (653 tests)
│   │   ├── pages/                    # Admin POMs (AdminLoginPage, UserManagementPage, etc.)
│   │   ├── fixtures/                 # Admin fixtures & authenticated contexts
│   │   └── tests/                    # Workflow (test_admin_*.py), Validation (test_val_admin_*.py), Mock (tests/mock/)
│   │
│   ├── client_portal/                # Developer 3 Domain: Client Portal (338 tests)
│   │   ├── pages/                    # Client POMs (ClientLoginPage, ClientDepositPage, etc.)
│   │   ├── fixtures/                 # Client fixtures & authenticated contexts
│   │   └── tests/                    # Workflow (test_client_*.py), Validation (test_val_client_*.py), Mock (tests/mock/)
│   │
│   └── shared/                       # Reusable infrastructure & shared helpers (176 tests)
│       ├── mocks/                    # MockRouter, MockScenarios, mock_data datasets
│       ├── pages/base_page.py        # Abstract BasePage with resilient Playwright helpers
│       ├── helpers/                  # validation_payloads.py, math_assertions.py
│       ├── fixtures/                 # browser_fixtures.py, auth_fixtures.py, mock_fixtures.py
│       ├── utils/                    # test_logger.py, diagnostics.py, error_monitor.py, waits.py
│       ├── constants/                # timeouts.py, viewports.py, routes.py
│       └── assertions/               # Domain-agnostic assertion wrappers
│
├── scripts/                          # Test execution CLI runners
├── docs/                             # Engineering architecture & testing specifications
├── .env.example                      # Environment variables template
├── .gitignore                        # Git exclusion rules
├── conftest.py                       # Root pytest conftest (telemetry hooks, session routing)
├── pytest.ini                        # Pytest discovery settings and markers
└── requirements.txt                  # Minimal Python dependencies
```

---

## 📊 Dual-Format Reporting & History Management

The framework produces both **structured JSON reports** and **human-readable summaries**:

1. **Active Summary** (`reports/validations/logs/global_test_summary.txt`):
   - Total Tests Run, Passed, Failed, and Skipped.
   - Portal-by-portal breakdown.
   - Invisible runtime diagnostics overview (uncaught JS errors, console errors, HTTP 4xx/5xx responses).
2. **Detailed JSON Report** (`reports/validations/logs/global_test_results.json`):
   - Machine-parseable JSON array containing full execution duration, timestamps, docstring meanings, and diagnostics telemetry per test.
3. **Automated Suite-Level History**:
   - On each new run, previous run artifacts (`logs/`, `screenshots/`, `diagnostics/`, `traces/`) are archived into `reports/<suite>/history/<RunType> - DD-MM-YYYY_HH-MM-SS/`, keeping active directories clean while preserving audit history.
