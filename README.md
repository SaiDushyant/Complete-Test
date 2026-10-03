# Complete Test Automation Framework

A unified, production-grade automated testing platform built with Python and Playwright. The repository provides two logically independent, complementary testing systems designed for high-confidence web application validation:

```text
                        COMPLETE-TEST REPOSITORY
                                   │
              ┌────────────────────┴────────────────────┐
              │                                         │
              ▼                                         ▼
       ui_regression/                              workflows/
       (29 tests)                                 (1,354 tests)
              │                                         │
       DOM / Structure                         Behavioral & Validation
              │                                         │
       crawler + comparer                       ┌───────┼───────┐
                                                │       │       │
                                              Trade   Admin   Client
                                             Terminal Portal  Portal
```

---

## 📑 Core Documentation Index

| Documentation Guide | Description |
| :--- | :--- |
| **[How to Run Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/HOW_TO_RUN.md)** | Complete CLI operational guide, execution recipes, parallel testing, validation suites, and reporting formats. |
| **[Validation Testing Specification](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/VALIDATION_TESTING_SPECIFICATION.md)** | Definitive specification for 434 validation tests across Admin, Client, and Trade portals, attack vectors, and element catalogs. |
| **[Mock Testing Specification](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/MOCK_TESTING_SPECIFICATION.md)** | Definitive specification and implementation guide for Playwright network mocking, MockRouter, error injection, and test catalog. |
| **[Scripts & Test Runners Catalog](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/scripts/README.md)** | Detailed documentation of every script in `scripts/`, flags, and usage recommendations. |
| **[Architecture Overview](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/architecture.md)** | Explains why UI regression and behavioral workflows are intentionally separated, and details boundary isolation. |
| **[Developer Onboarding Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/developer-guide.md)** | Complete walkthrough from environment setup to creating Page Objects, writing tests, and opening PRs. |
| **[Workflow Testing Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/workflow-testing.md)** | Page Object Model patterns, fixture injection, wait strategies, assertions, screenshot/trace capture, and debugging. |
| **[Git & GitHub Team Workflow](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/git-workflow.md)** | Branching strategy, setup commands for all OS, safe rebasing, merge conflict resolution, and PR guidelines. |
| **[Domain Ownership Matrix](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/ownership.md)** | Directory ownership boundaries for Developer 1 (Trade), Developer 2 (Admin), and Developer 3 (Client). |
| **[UI Regression Engine Reference](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/DOCUMENTATION.md)** | Deep technical dive into the 6-tier DOM matching algorithm, canonical routing, and noise filtering. |

---

## 🏛️ Two Testing Layers (1,383 Total Tests)

### 1. `ui_regression/` — DOM Structural Regression & Drift Detection (29 Tests)
> **Answers**: *"Has the UI or DOM structure changed unexpectedly from the approved baseline?"*
- Crawls web applications across 5 responsive breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`).
- Extracts canonical live element trees and compares against version-controlled ground truth baselines.
- Employs a 6-tier element matching algorithm with dynamic noise filtering (suppressing false drift from timestamps, market ticks, dynamic account IDs, and loading skeletons).
- Captures live runtime diagnostics: Console JS errors, uncaught exceptions, HTTP 4xx/5xx responses, and network failures.
- Preserves version-controlled baselines under `ui_regression/element_output/` and `ui_regression/element_output_admin/`.

### 2. `workflows/` — Behavioral Workflows & Validation Testing (1,354 Tests)
> **Answers**: *"Can a user successfully complete critical application workflows and are all inputs, boundaries, and math calculations strictly validated?"*
- Co-locates both **End-to-End Workflow Journeys** (`test_<portal>_*.py`) and **Element-Level Validation Suites** (`test_val_<portal>_*.py` — 434 tests):
  - **Trade Terminal** (`workflows/trade_terminal/` — 395 tests: 175 workflow + 220 validation tests) — Maintained by Developer 1
  - **Admin Portal** (`workflows/admin_portal/` — 554 tests: 425 workflow + 129 validation tests) — Maintained by Developer 2
  - **Client Portal** (`workflows/client_portal/` — 246 tests: 161 workflow + 85 validation tests) — Maintained by Developer 3
  - **Shared & Integrations** (`workflows/shared/` — 159 tests) — Cross-portal E2E, Manager Hierarchy Isolation, A/B Book Lifecycle, Financial Calculation Verification
- Shared infrastructure (`workflows/shared/`) provides `BasePage`, shared attack vectors (`validation_payloads.py`), financial math assertions (`math_assertions.py`), browser lifecycle fixtures, error monitors, and multi-process safe logging.

---

## 🚀 Quick Execution Guide

```bash
# 1. Activate Environment
conda activate playwright-env

# 2. Run Entire Platform Validation Suite (434 Tests)
pytest -m validation -v

# 3. Run Validation by Specific Portal
pytest workflows/trade_terminal/tests/test_val_trade_*.py -v
pytest workflows/admin_portal/tests/test_val_admin_*.py -v
pytest workflows/client_portal/tests/test_val_client_*.py -v

# 4. Master Runner - Run all workflows headless
python scripts/run_all_workflows.py

# 5. Dynamic Parallel Execution across 4 workers
python scripts/run_all_workflows.py -n 4 --dist loadfile

# 6. Smoke Test Suite (< 2 mins)
python scripts/run_smoke_tests.py

# 7. Visual Debugging (Headed mode with slow-motion delay)
pytest workflows/client_portal/tests/test_val_client_deposit.py -v --headed --slowmo 300

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
│   ├── validations/                  # Active validation logs, screenshots, diagnostics, traces
│   │   └── history/                  # Timestamped past validation run snapshots
│   ├── workflows/                    # Active workflow logs, screenshots, traces
│   │   └── history/                  # Timestamped past workflow run snapshots
│   └── ui_regression/                # DOM drift comparison reports & snapshots
│       └── history/
│
├── ui_regression/                    # DOM-level structural/UI regression testing (29 tests)
│   ├── crawler/                      # Multi-viewport crawler & element extractor
│   ├── comparer/                     # 6-tier matching engine & drift comparer
│   ├── element_output/               # Version-controlled baseline snapshots (Client)
│   ├── element_output_admin/         # Version-controlled baseline snapshots (Admin)
│   └── tests/                        # DOM regression unit & accuracy tests
│
├── workflows/                        # Single Top-Level Testing Hierarchy (1,354 tests)
│   ├── conftest.py                   # Shared browser fixture export
│   │
│   ├── trade_terminal/               # Developer 1 Domain: Trade Terminal (395 tests)
│   │   ├── pages/                    # Trade POMs (LoginPage, OrderEntryPage, WatchlistPage, etc.)
│   │   ├── fixtures/                 # Trade fixtures & authenticated contexts
│   │   └── tests/                    # Workflow (test_trade_*.py) & Validation (test_val_trade_*.py)
│   │
│   ├── admin_portal/                 # Developer 2 Domain: Admin Portal (554 tests)
│   │   ├── pages/                    # Admin POMs (AdminLoginPage, UserManagementPage, etc.)
│   │   ├── fixtures/                 # Admin fixtures & authenticated contexts
│   │   └── tests/                    # Workflow (test_admin_*.py) & Validation (test_val_admin_*.py)
│   │
│   ├── client_portal/                # Developer 3 Domain: Client Portal (246 tests)
│   │   ├── pages/                    # Client POMs (ClientLoginPage, ClientDepositPage, etc.)
│   │   ├── fixtures/                 # Client fixtures & authenticated contexts
│   │   └── tests/                    # Workflow (test_client_*.py) & Validation (test_val_client_*.py)
│   │
│   └── shared/                       # Reusable infrastructure & shared helpers
│       ├── pages/base_page.py        # Abstract BasePage with resilient Playwright helpers
│       ├── helpers/                  # validation_payloads.py (SQLi/XSS/boundaries), math_assertions.py
│       ├── fixtures/                 # browser_fixtures.py, auth_fixtures.py
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
