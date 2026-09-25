# How to Run the Project: CLI Commands, Configuration & Option Guide

This comprehensive guide details how to configure and run the **Playwright Multi-Viewport DOM Regression & Drift Detection Framework**, explaining every command-line option, why it exists, and real-world usage scenarios.

---

## Table of Contents

1. [System Architecture & Workflow Overview](#1-system-architecture--workflow-overview)
2. [Environment Configuration (`.env`)](#2-environment-configuration-env)
3. [Crawler Commands & Options (Capturing Baseline Snapshots)](#3-crawler-commands--options-capturing-baseline-snapshots)
   - [3.1 Client Portal Crawler (`crawler.run_crawler`)](#31-client-portal-crawler-crawlerrun_crawler)
   - [3.2 Admin Console Crawler (`crawler.run_crawler_admin`)](#32-admin-console-crawler-crawlerrun_crawler_admin)
4. [Comparer Commands & Options (Live Drift Detection)](#4-comparer-commands--options-live-drift-detection)
   - [4.1 Client Portal Comparer (`comparer.run_comparer`)](#41-client-portal-comparer-comparerrun_comparer)
   - [4.2 Admin Console Comparer (`comparer.run_comparer_admin`)](#42-admin-console-comparer-comparerrun_comparer_admin)
5. [Automated Test Suite (`pytest`)](#5-automated-test-suite-pytest)
6. [Quick Status Inspector (`scripts/status.py`)](#6-quick-status-inspector-scriptsstatuspy)
7. [Practical Execution Recipes](#7-practical-execution-recipes)

---

## 1. System Architecture & Workflow Overview

The framework operates in two distinct phases across two distinct web application suites:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: BASELINE CRAWLING                      │
│                                                                        │
│  [BASELINE_URL / BASELINE_ADMIN_BASE_URL]                              │
│         │                                                              │
│         ▼                                                              │
│  Run Crawler across 5 Viewports (sm, md, lg, xl, 2xl)                  │
│         │                                                              │
│         ▼                                                              │
│  Generate Baseline JSON Snapshots in element_output/ or element_output_admin/
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: LIVE COMPARISON & DRIFT AUDIT              │
│                                                                        │
│  [LIVE_URL / LIVE_ADMIN_BASE_URL]                                      │
│  (Can be same site OR a different environment, e.g. UAT / Pre-Prod)    │
│         │                                                              │
│         ▼                                                              │
│  Live In-Memory DOM Extraction across Viewports                        │
│         │                                                              │
│         ▼                                                              │
│  Canonical Route Matching + 6-Tier Element Diffing + Noise Filter      │
│         │                                                              │
│         ▼                                                              │
│  Output comparison_report.json or comparison_report_admin.json         │
└────────────────────────────────────────────────────────────────────────┘
```

### The Two Application Suites

1. **Client Portal (Trading Site)**:
   - Includes public pages (`/login/`, `/register/`, `/reset/`) and authenticated trading views (watchlists, order execution, MAM account tabs, position grids).
   - Crawled with `crawler.run_crawler` $\to$ snapshots stored in `element_output/`.
   - Compared with `comparer.run_comparer` $\to$ report saved to `comparison_report.json`.

2. **Admin Management Console**:
   - Includes admin login and administrative dashboards (`Controlbase/Dashboard`, user managers, trade reports, withdrawal queues).
   - Crawled with `crawler.run_crawler_admin` $\to$ snapshots stored in `element_output_admin/`.
   - Compared with `comparer.run_comparer_admin` $\to$ report saved to `comparison_report_admin.json`.

---

## 2. Environment Configuration (`.env`)

Before running commands, configure your `.env` file (copied from `.env.example`).

Each environment has its own independent settings and credentials:

```env
# ============================================================
# CLIENT PORTAL: BASELINE SETTINGS & CREDENTIALS
# ============================================================
BASELINE_URL=https://stage.xtremenext.com/
BASELINE_TEST_USER_EMAIL=10009
BASELINE_TEST_USER_PASSWORD=Temp@123
BASELINE_POST_LOGIN_URL_PATTERN=**/dashboard**

# ============================================================
# CLIENT PORTAL: LIVE SETTINGS & CREDENTIALS
# ============================================================
# Live URL can be identical to BASELINE_URL or point to another site
LIVE_URL=https://stage.xtremenext.com/
LIVE_TEST_USER_EMAIL=10009
LIVE_TEST_USER_PASSWORD=Temp@123
LIVE_POST_LOGIN_URL_PATTERN=**/dashboard**

ENABLE_TRADE_TESTS=false

# ============================================================
# ADMIN PANEL: BASELINE SETTINGS & CREDENTIALS
# ============================================================
BASELINE_ADMIN_BASE_URL=https://stage.xtremenext.com/admin/Controlbase/Dashboard
BASELINE_ADMIN_LOGIN_URL=https://stage.xtremenext.com/admin/Login/index
BASELINE_ADMIN_USER_USERNAME=madmin
BASELINE_ADMIN_USER_PASSWORD=Test@1234
BASELINE_ADMIN_POST_LOGIN_URL_PATTERN=**/admin/Controlbase/**

# ============================================================
# ADMIN PANEL: LIVE SETTINGS & CREDENTIALS
# ============================================================
LIVE_ADMIN_BASE_URL=https://stage.xtremenext.com/admin/Controlbase/Dashboard
LIVE_ADMIN_LOGIN_URL=https://stage.xtremenext.com/admin/Login/index
LIVE_ADMIN_USER_USERNAME=madmin
LIVE_ADMIN_USER_PASSWORD=Test@1234
LIVE_ADMIN_POST_LOGIN_URL_PATTERN=**/admin/Controlbase/**

# ============================================================
# CRAWLER SAFETY & TIMEOUT SETTINGS
# ============================================================
CRAWLER_MAX_DEPTH=10
CRAWLER_MAX_PAGES=100
CRAWLER_WAIT_AFTER_LOAD=1000
CRAWLER_TIMEOUT=60000
CRAWLER_HEADLESS=true
```

### Why Each Setting Exists

| Setting | Purpose / Why It Exists |
| :--- | :--- |
| `BASELINE_URL` | Specifies the source application URL to crawl and establish ground-truth element snapshots. |
| `LIVE_URL` | Specifies the live target URL to audit during comparison. Can be set to staging, a PR preview deployment, or production without modifying baseline files. |
| `BASELINE_TEST_USER_EMAIL` / `PASSWORD` | Credentials used when crawling the baseline application. |
| `LIVE_TEST_USER_EMAIL` / `PASSWORD` | Independent credentials used for the live application (essential if staging and production use distinct user accounts). |
| `BASELINE_ADMIN_BASE_URL` | Entry dashboard URL for the admin baseline crawl. |
| `LIVE_ADMIN_BASE_URL` | Live target admin dashboard URL during comparison. |
| `BASELINE_ADMIN_LOGIN_URL` / `LIVE_ADMIN_LOGIN_URL` | Explicit login endpoints for administrative authentication. |
| `BASELINE_ADMIN_USER_USERNAME` / `PASSWORD` | Administrative credentials for baseline crawl. |
| `LIVE_ADMIN_USER_USERNAME` / `PASSWORD` | Independent administrative credentials for live comparison. |
| `CRAWLER_MAX_DEPTH` | Maximum link hops followed from the start URL to prevent infinite crawling. |
| `CRAWLER_MAX_PAGES` | Cap on the number of pages crawled per viewport to bound execution time. |
| `CRAWLER_WAIT_AFTER_LOAD` | Milliseconds to wait after `domcontentloaded` for SPA javascript widgets (charts, tickers) to stabilize. |
| `CRAWLER_TIMEOUT` | Maximum millisecond timeout for page loads and login transitions. |
| `CRAWLER_HEADLESS` | Boolean (`true` or `false`) controlling default browser visibility. |

---

## 3. Crawler Commands & Options (Capturing Baseline Snapshots)

### 3.1 Client Portal Crawler (`crawler.run_crawler`)

Captures baseline JSON snapshots of the Client Portal across responsive viewports.

#### Basic Command
```bash
python -m ui_regression.crawler.run_crawler
```

#### Full Command with All Options
```bash
python -m ui_regression.crawler.run_crawler \
    --start-url https://stage.xtremenext.com/ \
    --viewports sm,md,lg,xl,2xl \
    --output-dir ui_regression/element_output \
    --workers 5 \
    --max-pages 100 \
    --max-depth 10 \
    --headed
```

#### Detailed Options Table

| Option | Type | Default | Why This Option Exists |
| :--- | :--- | :--- | :--- |
| `--start-url` (alias: `--baseline-url`) | `string` | `BASELINE_URL` from `.env` | **Override entry URL**: Allows you to crawl a specific environment branch or sub-path without altering `.env`. |
| `--viewports` | `string` | `sm,md,lg,xl,2xl` | **Granular testing**: Lets you crawl only specific viewport widths (e.g. `--viewports sm,xl`) to speed up runs when focusing on mobile or desktop only. |
| `--output-dir` | `string` | `element_output` | **Snapshot versioning**: Allows saving snapshots to a custom directory (e.g. `--output-dir element_output_v2.0` or `--output-dir baseline_backup`) to preserve release milestones. |
| `--workers` | `int` | `5` | **Concurrency control**: Number of parallel browser workers running viewport crawls simultaneously. Set to `1` or `2` on low-memory machines/CI, or `5` for maximum speed. |
| `--max-pages` | `int` | `100` | **Safety limit**: Restricts total pages crawled per viewport to prevent runaway execution on large sites. |
| `--max-depth` | `int` | `10` | **Crawl depth control**: Limits how many navigation steps deep the crawler will explore from the root page. |
| `--headed` | `flag` | Headless (`False`) | **Visual debugging**: Launches visible Chromium browser windows so you can visually inspect crawler interaction and navigation in real time. |

---

### 3.2 Admin Console Crawler (`crawler.run_crawler_admin`)

Captures baseline JSON snapshots of the Admin Management Console.

#### Basic Command
```bash
python -m ui_regression.crawler.run_crawler_admin
```

#### Full Command with All Options
```bash
python -m ui_regression.crawler.run_crawler_admin \
    --start-url https://stage.xtremenext.com/admin/Controlbase/Dashboard \
    --viewports sm,md,lg,xl,2xl \
    --output-dir ui_regression/element_output_admin \
    --workers 5 \
    --max-pages 100 \
    --max-depth 10 \
    --headed
```

#### Detailed Options Table

| Option | Type | Default | Why This Option Exists |
| :--- | :--- | :--- | :--- |
| `--start-url` (alias: `--baseline-url`) | `string` | `BASELINE_ADMIN_BASE_URL` from `.env` | **Admin entry point override**: Allows pointing the admin crawler to a specific admin controller or staging host. |
| `--viewports` | `string` | `sm,md,lg,xl,2xl` | **Admin responsiveness**: Select which viewport widths to capture for the admin interface. |
| `--output-dir` | `string` | `element_output_admin` | **Directory isolation**: Keeps admin snapshots separate from client portal snapshots. |
| `--workers` | `int` | `5` | **Parallelism**: Concurrently crawls admin pages across viewports. |
| `--max-pages` | `int` | `100` | **Execution boundary**: Maximum admin views to crawl per viewport. |
| `--max-depth` | `int` | `10` | **Navigation depth**: Maximum admin menu levels to traverse. |
| `--headed` | `flag` | Headless (`False`) | **Visual monitoring**: Enables watching the admin login and table navigation on-screen. |

---

## 4. Comparer Commands & Options (Live Drift Detection)

### 4.1 Client Portal Comparer (`comparer.run_comparer`)

Performs live extraction of the client application and compares elements against existing baseline snapshots.

#### Basic Command
```bash
python -m ui_regression.comparer.run_comparer
```

#### Cross-Environment Command (Baseline on Stage vs Live on Preview)
```bash
python -m ui_regression.comparer.run_comparer \
    --live-url https://preview.xtremenext.com/ \
    --baseline-url https://stage.xtremenext.com/
```

#### Full Command with All Options
```bash
python -m ui_regression.comparer.run_comparer \
    --live-url https://preview.xtremenext.com/ \
    --baseline-url https://stage.xtremenext.com/ \
    --viewports sm,md,lg,xl,2xl \
    --baseline-dir ui_regression/element_output \
    --report-file reports/ui_regression/comparison_report.json \
    --workers 5 \
    --no-noise-filter \
    --headed
```

#### Detailed Options Table

| Option | Type | Default | Why This Option Exists |
| :--- | :--- | :--- | :--- |
| `--live-url` | `string` | `LIVE_URL` from `.env` | **Target environment selection**: Specifies the live site to crawl and audit. You can point this to a PR preview URL, local server (`http://localhost:3000`), or staging site to detect drift without modifying `.env`. |
| `--baseline-url` | `string` | `BASELINE_URL` from `.env` | **Cross-domain canonical route mapping**: Required when comparing two different hosts (e.g. `stage` vs `preview`). It strips the baseline host prefix so `/dashboard` on `stage` pairs with `/dashboard` on `preview`. |
| `--viewports` | `string` | `sm,md,lg,xl,2xl` | **Targeted comparison**: Focuses drift detection on specific viewport widths (e.g. `--viewports sm` to test only mobile layouts). |
| `--baseline-dir` | `string` | `element_output` | **Baseline directory selection**: Chooses which baseline snapshot directory to compare against (e.g. comparing against an older release milestone). |
| `--report-file` | `string` | `comparison_report.json` | **CI/CD artifact naming**: Allows specifying custom output file paths (e.g. `--report-file reports/build_104_drift.json`) for CI pipelines. |
| `--workers` | `int` | `5` | **Worker pool sizing**: Concurrently extracts live DOM across all 5 viewports in memory, accelerating comparison runs. |
| `--no-noise-filter` | `flag` | Filter enabled (`False`) | **Raw element diff inspection**: Disables intelligent regex masking for tickers, dates, times, and hashes. Useful when developers need to see exact raw string diffs. |
| `--headed` | `flag` | Headless (`False`) | **Visual debugging**: Displays the browser window during live extraction to inspect UI rendering and interactions. |

---

### 4.2 Admin Console Comparer (`comparer.run_comparer_admin`)

Performs live extraction of the Admin Console and compares elements against existing admin baseline snapshots.

#### Basic Command
```bash
python -m ui_regression.comparer.run_comparer_admin
```

#### Cross-Environment Command (Admin Baseline on Stage vs Live on Preview)
```bash
python -m ui_regression.comparer.run_comparer_admin \
    --live-url https://preview.xtremenext.com/admin/Controlbase/Dashboard \
    --baseline-url https://stage.xtremenext.com/admin/Controlbase/Dashboard
```

#### Full Command with All Options
```bash
python -m ui_regression.comparer.run_comparer_admin \
    --live-url https://preview.xtremenext.com/admin/Controlbase/Dashboard \
    --baseline-url https://stage.xtremenext.com/admin/Controlbase/Dashboard \
    --viewports sm,md,lg,xl,2xl \
    --baseline-dir ui_regression/element_output_admin \
    --report-file reports/ui_regression/comparison_report_admin.json \
    --workers 5 \
    --headed
```

#### Detailed Options Table

| Option | Type | Default | Why This Option Exists |
| :--- | :--- | :--- | :--- |
| `--live-url` | `string` | `LIVE_ADMIN_BASE_URL` from `.env` | **Live admin target**: The live admin dashboard URL to crawl and compare. |
| `--baseline-url` | `string` | `BASELINE_ADMIN_BASE_URL` from `.env` | **Admin route canonicalization**: Enables route matching between different admin server hostnames. |
| `--viewports` | `string` | `sm,md,lg,xl,2xl` | **Admin viewport filter**: Audit specific screen breakpoints for the admin console. |
| `--baseline-dir` | `string` | `element_output_admin` | **Admin snapshot directory**: Directory containing admin baseline snapshots. |
| `--report-file` | `string` | `comparison_report_admin.json` | **Admin report location**: Destination path for the admin comparison JSON report. |
| `--workers` | `int` | `5` | **Concurrency**: Number of parallel viewport workers. |
| `--no-noise-filter` | `flag` | Filter enabled (`False`) | **Raw diff mode**: Disables table cell dynamic normalization and noise filtering. |
| `--headed` | `flag` | Headless (`False`) | **Visual monitoring**: Launches visible browser windows during admin extraction. |

---

## 5. Automated Test Suite (`pytest`)

The repository includes an automated verification suite covering baseline/live URLs, canonical routes, cascade prevention, duplicate ID FIFO ordering, and noise suppression.

### Run All DOM Regression Tests
```bash
pytest ui_regression/ -v
# or:
./scripts/run_dom_regression.sh
```

### Run Specific Test Modules

```bash
# Test baseline/live URLs, canonical route matching & domain masking
pytest ui_regression/tests/test_baseline_live_urls.py -v

# Test matching accuracy, cascade prevention & table cell normalization
pytest ui_regression/tests/test_comparer_accuracy.py -v

# Test 5-viewport definitions, snapshot keys & viewport isolation
pytest ui_regression/tests/test_viewports.py -v
```

---

## 6. Quick Status Inspector (`scripts/status.py`)

To quickly inspect existing comparison reports without manually parsing JSON:

```bash
python scripts/status.py
```

This outputs an instant terminal summary of total views compared, baseline elements, live elements, unchanged matches, and drift percentages.

---

## 7. Practical Execution Recipes

### Recipe 1: First-Time Setup & Baseline Capture
```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Configure .env
cp .env.example .env
# Edit .env with your credentials

# 3. Crawl Client Portal baseline (all 5 viewports)
python -m ui_regression.crawler.run_crawler

# 4. Crawl Admin Console baseline (all 5 viewports)
python -m ui_regression.crawler.run_crawler_admin
```

---

### Recipe 2: Daily CI/CD Drift Audit on Staging
```bash
# Audit Client Portal
python -m ui_regression.comparer.run_comparer

# Audit Admin Console
python -m ui_regression.comparer.run_comparer_admin

# Print quick status
python scripts/status.py
```

---

### Recipe 3: Testing a Pre-Production Release Branch
Compare fixed staging baselines against a live pre-production deployment:
```bash
python -m ui_regression.comparer.run_comparer \
    --live-url https://preprod.xtremenext.com/ \
    --report-file reports/ui_regression/preprod_drift_report.json
```

---

### Recipe 4: Rapid Mobile-Only Debugging (Headed)
When investigating a mobile layout bug on small screens (`sm: 640px`):
```bash
python -m ui_regression.comparer.run_comparer \
    --viewports sm \
    --headed
```

---

### Recipe 5: Low-Memory / Single-Core Execution
For CI/CD runners or virtual machines with limited RAM:
```bash
python -m ui_regression.comparer.run_comparer \
    --workers 1 \
    --viewports sm,xl
```
