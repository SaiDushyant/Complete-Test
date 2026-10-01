# Complete Test Automation Framework

A unified, production-grade automated testing platform built with Python and Playwright. The repository provides two logically independent, complementary testing systems designed for high-confidence web application validation:

```text
                        COMPLETE-TEST REPOSITORY
                                   │
              ┌────────────────────┴────────────────────┐
              │                                         │
              ▼                                         ▼
       ui_regression/                              workflows/
       (29 tests)                                 (915 tests)
              │                                         │
       DOM / Structure                            Behavior / E2E
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
| **[How to Run Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/HOW_TO_RUN.md)** | Complete CLI operational guide, execution recipes, parallel testing, and reporting formats. |
| **[Scripts & Test Runners Catalog](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/scripts/README.md)** | Detailed documentation of every script in `scripts/`, flags, and usage recommendations. |
| **[Architecture Overview](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/architecture.md)** | Explains why UI regression and behavioral workflows are intentionally separated, and details boundary isolation. |
| **[Developer Onboarding Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/developer-guide.md)** | Complete walkthrough from environment setup to creating Page Objects, writing tests, and opening PRs. |
| **[Workflow Testing Guide](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/workflow-testing.md)** | Page Object Model patterns, fixture injection, wait strategies, assertions, screenshot/trace capture, and debugging. |
| **[Git & GitHub Team Workflow](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/git-workflow.md)** | Branching strategy, setup commands for all OS, safe rebasing, merge conflict resolution, and PR guidelines. |
| **[Domain Ownership Matrix](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/docs/ownership.md)** | Directory ownership boundaries for Developer 1 (Trade), Developer 2 (Admin), and Developer 3 (Client). |
| **[UI Regression Engine Reference](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/DOCUMENTATION.md)** | Deep technical dive into the 6-tier DOM matching algorithm, canonical routing, and noise filtering. |

---

## 🏛️ Two Testing Layers (944 Total Tests)

### 1. `ui_regression/` — DOM Structural Regression & Drift Detection (29 Tests)
> **Answers**: *"Has the UI or DOM structure changed unexpectedly from the approved baseline?"*
- Crawls web applications across 5 responsive breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`).
- Extracts canonical live element trees and compares against version-controlled ground truth baselines.
- Employs a 6-tier element matching algorithm with dynamic noise filtering (suppressing false drift from timestamps, market ticks, dynamic account IDs, and loading skeletons).
- Captures live runtime diagnostics: Console JS errors, uncaught exceptions, HTTP 4xx/5xx responses, and network failures.
- Preserves version-controlled baselines under `ui_regression/element_output/` and `ui_regression/element_output_admin/`.

### 2. `workflows/` — Behavioral, Functional & E2E Testing (915 Tests)
> **Answers**: *"Can a user successfully complete critical application workflows and journeys?"*
- Tests end-to-end user actions (authentication, navigation, form inputs, trade actions, administrative controls).
- Organized into three strictly isolated portal domains:
  - **Trade Terminal** (`workflows/trade_terminal/` — 162 tests) — Maintained by Developer 1
  - **Admin Portal** (`workflows/admin_portal/` — 397 tests) — Maintained by Developer 2
  - **Client Portal** (`workflows/client_portal/` — 171 tests) — Maintained by Developer 3
  - **Shared & Integrations** (`workflows/shared/` — 185 tests) — Cross-portal E2E and multi-system validation
- Shared infrastructure (`workflows/shared/`) provides `BasePage`, browser lifecycle fixtures, common assertions, waits, and multi-process safe logging.

---

## 🚀 Quick Execution Guide

```bash
# 1. Activate Environment
conda activate playwright-env

# 2. Master Runner - Run all workflows headless (fastest)
python scripts/run_all_workflows.py

# 3. Dynamic Parallel Execution across 4 workers (zero idle wait time)
python scripts/run_all_workflows.py -n 4 --dist loadfile

# 4. Smoke Test Suite (< 2 mins)
python scripts/run_smoke_tests.py

# 5. Visual Debugging (Headed mode with slow-motion delay)
python scripts/run_all_workflows.py --headed --slowmo 200

# 6. Full UI Regression Pipeline (Re-crawl + Compare + Diagnostics)
python scripts/run_ui_full_pipeline.py
```

---

## 📁 Repository Directory Structure

```text
Complete-Test/
│
├── ui_regression/                    # DOM-level structural/UI regression testing
│   ├── crawler/                      # Multi-viewport crawler & element extractor
│   ├── comparer/                     # 6-tier matching engine & drift comparer
│   ├── element_output/               # Version-controlled baseline snapshots (Client)
│   ├── element_output_admin/         # Version-controlled baseline snapshots (Admin)
│   └── tests/                        # DOM regression unit & accuracy tests (29 tests)
│
├── workflows/                        # Behavioral / Functional / E2E workflow testing (915 tests)
│   ├── trade_terminal/               # Developer 1: Trade Terminal tests & pages
│   │   ├── pages/                    # Page Objects (LoginPage, OrderEntryPage, WatchlistPage, etc.)
│   │   ├── tests/                    # Behavioral workflow test suites
│   │   ├── fixtures/                 # Portal fixtures & session state injection
│   │   └── utils/                    # Portal-specific helper functions
│   │
│   ├── admin_portal/                 # Developer 2: Admin Portal tests & pages
│   │   ├── pages/                    # Admin Console Page Objects
│   │   ├── tests/                    # Admin workflow test suites (Orders A/B/C, Managers, Roles)
│   │   ├── fixtures/                 # Admin fixtures & session state injection
│   │   └── utils/                    # Admin-specific helper functions
│   │
│   ├── client_portal/                # Developer 3: Client Portal tests & pages
│   │   ├── pages/                    # Client Portal Page Objects (Dashboard, Wallet, Deposit, etc.)
│   │   ├── tests/                    # Client workflow test suites (31 Auth Negative Scenarios)
│   │   ├── fixtures/                 # Client fixtures & session state injection
│   │   └── utils/                    # Client-specific helper functions
│   │
│   └── shared/                       # Cross-portal reusable infrastructure & E2E
│       ├── pages/                    # BasePage with high-level Playwright wrappers
│       ├── fixtures/                 # Browser lifecycle & auth caching fixtures
│       ├── utils/                    # Robust wait helpers, logger, screenshots, diagnostics
│       ├── assertions/               # Readable assertion helper functions
│       └── tests/                    # Cross-portal E2E lifecycles & user management tests
│
├── scripts/                          # Automated CLI runners & utility tools
│   ├── run_all_workflows.py (.sh)    # Master workflow runner across all portals
│   ├── run_smoke_tests.py            # Fast smoke test runner
│   ├── run_regression_tests.py       # Full functional regression runner
│   ├── run_shared_tests.py           # Cross-portal integration runner
│   ├── run_admin_tests.py (.sh)      # Admin portal runner
│   ├── run_client_tests.py (.sh)     # Client portal runner
│   ├── run_trade_tests.py (.sh)      # Trade terminal runner
│   ├── run_ui_compare.py             # UI DOM drift comparison runner
│   ├── run_ui_crawl.py               # UI baseline crawler runner
│   ├── run_ui_full_pipeline.py       # Full UI crawl + compare + diagnostics pipeline
│   ├── run_ui_tests.py (.sh)         # UI regression pytest assertion runner
│   ├── status.py                     # CLI report inspector
│   └── README.md                     # Complete documentation for all scripts
│
├── reports/                          # Standardized test execution outputs
│   ├── workflows/logs/               # Dual format JSON & TXT execution logs
│   │   ├── global_test_results.json  # Structured JSON dataset of all test outcomes
│   │   ├── summary_report.json       # Master metrics JSON summary
│   │   ├── global_test_summary.txt   # Human-readable summary report
│   │   ├── global_passed_tests.txt   # Block formatted list of passed tests
│   │   ├── global_failed_tests.txt   # Detailed failure traceback logs
│   │   └── individual/               # Per-test isolated stdout/trace logs
│   └── ui_regression/                # UI DOM comparison reports
│       ├── comparison_report_admin.json
│       └── comparison_report.json
│
├── config/                           # Central configuration management
│   └── settings.py                   # Strongly typed dataclass settings loaded from .env
├── conftest.py                       # Root pytest conftest & multi-worker hooks
├── pytest.ini                        # Pytest configuration & registered markers
└── .env                              # Environment variables & credentials
```

---

## 📊 Standardized Dual-Format Reports

Every test execution automatically generates both **JSON** and **TXT** formatted reports in `reports/workflows/logs/`:
- **JSON**: Machine-readable dataset containing timestamps, pass rates, durations, and portal breakdowns.
- **TXT**: Formatted blocks including Test ID, human-readable Docstring meaning, status, and failure tracebacks.
- **Isolation**: Single-module runs update and scope logs to the active module; full test runs aggregate all modules into consolidated master reports.
