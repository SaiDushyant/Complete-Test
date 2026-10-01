# How to Run the Complete Test Framework: CLI & Execution Guide

This comprehensive guide details how to configure, execute, and inspect all test suites in the **Complete Test Framework** across both **Behavioral Workflow Testing** (920 tests across all portals) and **UI DOM Structural Regression Testing**.

---

## 📑 Table of Contents

1. [Quick Start & Overview](#1-quick-start--overview)
2. [Environment Setup & Configuration (`.env`)](#2-environment-setup--configuration-env)
3. [Master & Specialized Workflow Test Runners (`scripts/`)](#3-master--specialized-workflow-test-runners-scripts)
   - [3.1 Master Runner (`run_all_workflows.py`)](#31-master-runner-run_all_workflowspy)
   - [3.2 Smoke Test Runner (`run_smoke_tests.py`)](#32-smoke-test-runner-run_smoke_testspy)
   - [3.3 Regression Test Runner (`run_regression_tests.py`)](#33-regression-test-runner-run_regression_testspy)
   - [3.4 Shared & Cross-Portal Runner (`run_shared_tests.py`)](#34-shared--cross-portal-runner-run_shared_testspy)
   - [3.5 Portal-Specific Runners (`admin`, `client`, `trade`)](#35-portal-specific-runners-admin-client-trade)
4. [UI DOM Regression & Drift Detection Runners](#4-ui-dom-regression--drift-detection-runners)
   - [4.1 Level 1: Comparison Only (`run_ui_compare.py`)](#41-level-1-comparison-only-run_ui_comparepy)
   - [4.2 Level 2: Re-Crawl & Baseline Update (`run_ui_crawl.py`)](#42-level-2-re-crawl--baseline-update-run_ui_crawlpy)
   - [4.3 Level 3: Full UI Pipeline (`run_ui_full_pipeline.py`)](#43-level-3-full-ui-pipeline-run_ui_full_pipelinepy)
   - [4.4 Level 4: UI Pytest Suite (`run_ui_tests.py`)](#44-level-4-ui-pytest-suite-run_ui_testspy)
   - [4.5 Diagnostics Status Inspector (`scripts/status.py`)](#45-diagnostics-status-inspector-scriptsstatuspy)
5. [High-Performance Parallel Execution (`pytest-xdist`)](#5-high-performance-parallel-execution-pytest-xdist)
6. [Headed vs Headless Execution Modes](#6-headed-vs-headless-execution-modes)
7. [Dual-Format Reporting Architecture (JSON + TXT)](#7-dual-format-reporting-architecture-json--txt)
8. [Practical Execution Recipes](#8-practical-execution-recipes)

---

## 1. Quick Start & Overview

The repository provides two logically independent, complementary testing systems:

```
                            COMPLETE-TEST FRAMEWORK
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 │                                           │
                 ▼                                           ▼
      workflows/ (920 tests)                       ui_regression/ (29 tests)
  Behavioral / Functional / E2E                   DOM Drift & Structural Accuracy
                 │                                           │
   ┌─────────────┼─────────────┐                ┌────────────┴────────────┐
   │             │             │                │                         │
 Admin        Client         Trade          Crawler                   Comparer
Portal        Portal       Terminal        (Baselines)             (Drift Diffing)
```

### Quick Commands Cheat Sheet

```bash
# Activate Conda environment
conda activate playwright-env

# 1. Run all behavioral tests headless (fastest)
python scripts/run_all_workflows.py

# 2. Run in parallel across 4 workers with dynamic work-stealing
python scripts/run_all_workflows.py -n 4

# 3. Run all critical smoke tests
python scripts/run_smoke_tests.py

# 4. Run tests with visible browser (headed) and slow motion delay
python scripts/run_all_workflows.py --headed --slowmo 200

# 5. Run full UI DOM regression pipeline (re-crawl + compare + diagnostics report)
python scripts/run_ui_full_pipeline.py
```

---

## 2. Environment Setup & Configuration (`.env`)

Before running tests, ensure your `.env` file is present in the repository root (copied from `.env.example`).

```env
# ============================================================
# CLIENT PORTAL & BASELINE CONFIGURATION
# ============================================================
BASELINE_URL=https://stage.xtremenext.com/
BASELINE_TEST_USER_EMAIL=10009
BASELINE_TEST_USER_PASSWORD=Temp@123
BASELINE_POST_LOGIN_URL_PATTERN=**/dashboard**

# ============================================================
# TRADE TERMINAL CREDENTIALS
# ============================================================
TRADE_TERMINAL_URL=https://stage.xtremenext.com/
TRADE_LOGIN_URL=https://stage.xtremenext.com/login/
TRADE_USERNAME=10009
TRADE_PASSWORD=Temp@123

# ============================================================
# ADMIN MANAGEMENT PORTAL
# ============================================================
BASELINE_ADMIN_BASE_URL=https://stage.xtremenext.com/admin/Controlbase/Dashboard
BASELINE_ADMIN_LOGIN_URL=https://stage.xtremenext.com/admin/Login/index
BASELINE_ADMIN_USER_USERNAME=madmin
BASELINE_ADMIN_USER_PASSWORD=Test@1234
BASELINE_ADMIN_POST_LOGIN_URL_PATTERN=**/admin/Controlbase/**

# ============================================================
# BROWSER & EXECUTION FLAGS
# ============================================================
BROWSER_HEADLESS=true
CRAWLER_HEADLESS=true
BROWSER_TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true
TRACE_ON_FAILURE=true
```

---

## 3. Master & Specialized Workflow Test Runners (`scripts/`)

All scripts in `scripts/` are directly executable via Python or standard Bash wrappers:

### 3.1 Master Runner (`run_all_workflows.py`)
Executes all behavioral workflow tests across all portals.
```bash
# Run all workflows headless
python scripts/run_all_workflows.py

# Filter by portal
python scripts/run_all_workflows.py --portal admin
python scripts/run_all_workflows.py --portal client
python scripts/run_all_workflows.py --portal trade
python scripts/run_all_workflows.py --portal shared

# Filter by marker or keyword
python scripts/run_all_workflows.py -m "smoke"
python scripts/run_all_workflows.py -k "test_deposit"

# Parallel execution with 4 workers
python scripts/run_all_workflows.py -n 4
```

### 3.2 Smoke Test Runner (`run_smoke_tests.py`)
Executes critical user path sanity checks (`-m smoke`) across all portals in under 2 minutes.
```bash
python scripts/run_smoke_tests.py
python scripts/run_smoke_tests.py --headed
```

### 3.3 Regression Test Runner (`run_regression_tests.py`)
Executes the comprehensive functional regression test suite across all portals.
```bash
python scripts/run_regression_tests.py
python scripts/run_regression_tests.py -n 4
```

### 3.4 Shared & Cross-Portal Runner (`run_shared_tests.py`)
Executes cross-portal integration tests under `workflows/shared/tests/` (Admin user discovery, manage user matrix, sync reflection, practical account details).
```bash
python scripts/run_shared_tests.py
python scripts/run_shared_tests.py -k "manage_user"
```

### 3.5 Portal-Specific Runners (`admin`, `client`, `trade`)
```bash
# Admin Portal (Manager Management, Orders A/B/C, User Margins, Roles, Book Reports)
python scripts/run_admin_tests.py
python scripts/run_admin_tests.py -m orders

# Client Portal (Dashboard, Accounts, Deposits, Withdrawals, KYC Uploads, PAMM/MAM)
python scripts/run_client_tests.py
python scripts/run_client_tests.py -k "withdraw"

# Trade Terminal (Watchlist, Orders, Positions, TradingView/BlackTrader Charts, API Tokens)
python scripts/run_trade_tests.py
python scripts/run_trade_tests.py -m mam
```

---

## 4. UI DOM Regression & Drift Detection Runners

The UI regression system provides multi-viewport DOM baseline snapshot comparisons and real-time JavaScript runtime error tracking.

### 4.1 Level 1: Comparison Only (`run_ui_compare.py`)
Compares live webpage DOMs against existing baseline JSON snapshots without re-crawling.
```bash
# Compare both portals across all viewports
python scripts/run_ui_compare.py

# Compare only Admin portal in desktop viewport
python scripts/run_ui_compare.py --portal admin --viewports desktop

# Compare with visible browser window
python scripts/run_ui_compare.py --headed
```

### 4.2 Level 2: Re-Crawl & Baseline Update (`run_ui_crawl.py`)
Re-crawls application pages to generate/update baseline snapshots under `ui_regression/element_output/` and `ui_regression/element_output_admin/`.
```bash
python scripts/run_ui_crawl.py
python scripts/run_ui_crawl.py --portal admin --max-depth 5
```

### 4.3 Level 3: Full UI Pipeline (`run_ui_full_pipeline.py`)
Sequentially re-crawls baselines, runs DOM comparison with runtime error logging, and displays formatted status.
```bash
# Complete end-to-end UI audit
python scripts/run_ui_full_pipeline.py

# Skip re-crawl and execute comparison + status inspector
python scripts/run_ui_full_pipeline.py --skip-crawl
```

### 4.4 Level 4: UI Pytest Suite (`run_ui_tests.py`)
Runs the 29 automated Pytest assertions in `ui_regression/tests/` to verify baseline completeness and noise filter correctness.
```bash
python scripts/run_ui_tests.py
```

### 4.5 Diagnostics Status Inspector (`scripts/status.py`)
Parses generated comparison reports and prints a clear breakdown of page drift and runtime errors (Console JS, Uncaught exceptions, HTTP 4xx/5xx).
```bash
python scripts/status.py reports/ui_regression/comparison_report_admin.json
python scripts/status.py reports/ui_regression/comparison_report.json
```

---

## 5. High-Performance Parallel Execution (`pytest-xdist`)

All workflow runners support parallel test execution via `pytest-xdist` using dynamic work-stealing:

```bash
# Run with automatic worker count based on available CPU cores
python scripts/run_all_workflows.py -n auto

# Run with 4 workers using module-level distribution
python scripts/run_all_workflows.py -n 4 --dist loadfile

# Run with fine-grained per-test work-stealing
python scripts/run_all_workflows.py -n 4 --dist load
```

### How Dynamic Work-Stealing Works:
- Pytest distributes modules/tests dynamically into a shared queue.
- When a worker finishes a test or module, it **immediately picks up the next task from the backlog without waiting** for slower workers.
- Each worker process runs an isolated browser process with its own session state.
- `GlobalTestLogger` atomically collects results across all worker processes into unified master JSON and TXT reports.

---

## 6. Headed vs Headless Execution Modes

By default, **all scripts run in Headless mode** (`HEADLESS=true`) for optimal speed and CI/CD compatibility.

To run with a visible browser for visual debugging or live inspection:
```bash
# Launch visible Chromium browser window
python scripts/run_all_workflows.py --headed

# Add an observable 300ms delay between Playwright actions
python scripts/run_all_workflows.py --headed --slowmo 300
```

---

## 7. Dual-Format Reporting Architecture (JSON + TXT)

The test framework produces dual-format reports in `reports/workflows/logs/`:

| Report File | Format | Description |
| :--- | :--- | :--- |
| `reports/workflows/logs/global_test_results.json` | **JSON** | Complete structured dataset of all test outcomes, durations, and metadata. |
| `reports/workflows/logs/summary_report.json` | **JSON** | Master metrics JSON with portal-by-portal breakdown and pass percentages. |
| `reports/workflows/logs/global_test_summary.txt` | **TXT** | Human-readable summary of executed tests, passed/failed totals, and portal counts. |
| `reports/workflows/logs/global_passed_tests.txt` | **TXT** | Detailed block log of all passed tests with human-readable docstring meanings. |
| `reports/workflows/logs/global_failed_tests.txt` | **TXT** | Failure diagnostic log with exact traceback, error line, and reason. |
| `reports/workflows/logs/global_skipped_tests.txt` | **TXT** | Log of skipped tests and skip rationale. |
| `reports/workflows/logs/individual/<portal>/<test>.txt` | **TXT** | Individual test run log with captured stdout/stderr. |
| `reports/ui_regression/comparison_report_admin.json` | **JSON** | DOM element drift and runtime telemetry error log for Admin Portal. |
| `reports/ui_regression/comparison_report.json` | **JSON** | DOM element drift and runtime telemetry error log for Client Portal. |

### Single-Module Runs vs Full-Suite Runs:
- **Single Module Run**: Overwrites previous module logs to keep active logs scoped cleanly to the module under test.
- **Full Test Run**: Aggregates all modules across all three portals into the master reports without dropping any test.

---

## 8. Practical Execution Recipes

### Recipe 1: Fast Pull Request Validation (< 2 mins)
```bash
conda activate playwright-env
python scripts/run_smoke_tests.py -n 4
```

### Recipe 2: Pre-Merge Full Regression Run
```bash
python scripts/run_regression_tests.py -n 4
```

### Recipe 3: Admin Management Feature Testing
```bash
python scripts/run_admin_tests.py -m "orders or category_a" --headed --slowmo 200
```

### Recipe 4: Complete System Audit & DOM Drift Check
```bash
# 1. Run all behavioral workflows
python scripts/run_all_workflows.py -n 4

# 2. Run UI regression comparison
python scripts/run_ui_compare.py

# 3. View status report
python scripts/status.py
```
