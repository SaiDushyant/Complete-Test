# Test Automation Framework

A unified, production-grade automated testing platform built with Python and Playwright. The repository provides two logically independent, complementary testing systems designed for high-confidence web application validation:

```text
                 TEST AUTOMATION REPOSITORY
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      ui_regression/                workflows/
             │                           │
       DOM / Structure              Behavior / E2E
             │                           │
       crawler + comparer       ┌────────┼────────┐
                                │        │        │
                              Trade    Admin    Client
```

---

## 📑 Core Documentation Index

| Documentation Guide | Description |
| :--- | :--- |
| **[Architecture Overview](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/architecture.md)** | Explains why UI regression and behavioral workflows are intentionally separated, and details boundary isolation. |
| **[Developer Onboarding Guide](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/developer-guide.md)** | Complete 15-step walkthrough from cloning the repository to creating Page Objects, writing tests, and opening PRs. |
| **[Workflow Testing Guide](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/workflow-testing.md)** | Page Object Model patterns, fixture injection, wait strategies, assertions, screenshot/trace capture, and debugging. |
| **[Git & GitHub Team Workflow](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/git-workflow.md)** | Branching strategy, setup commands for all OS, safe rebasing, merge conflict resolution, and PR guidelines. |
| **[Domain Ownership Matrix](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/ownership.md)** | Directory ownership boundaries for Developer 1 (Trade), Developer 2 (Admin), and Developer 3 (Client). |
| **[Repository Cleanup Report](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/repository-cleanup.md)** | Full audit of repository restructuring, files removed, baselines preserved, and security audit details. |
| **[UI Regression Engine Reference](file:///Users/xtremenext_viji/Code/Playwrite/new/DOCUMENTATION.md)** | Deep technical dive into the 6-tier DOM matching algorithm, canonical routing, and noise filtering. |
| **[UI Regression CLI Guide](file:///Users/xtremenext_viji/Code/Playwrite/new/HOW_TO_RUN.md)** | Operational guide and CLI flags for running crawlers and comparers across 5 viewports. |

---

## 🏛️ Two Testing Layers

### 1. `ui_regression/` — DOM Structural Regression & Drift Detection
> **Answers**: *"Has the UI or DOM structure changed unexpectedly from the approved baseline?"*
- Crawls web applications across 5 responsive breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`).
- Extracts canonical live element trees and compares against version-controlled ground truth baselines.
- Employs a 6-tier element matching algorithm with dynamic noise filtering (suppressing false drift from timestamps, market ticks, dynamic account IDs, and loading skeletons).
- Preserves version-controlled baselines under `ui_regression/element_output/` and `ui_regression/element_output_admin/`.

### 2. `workflows/` — Behavioral, Functional & E2E Testing
> **Answers**: *"Can a user successfully complete critical application workflows and journeys?"*
- Tests end-to-end user actions (authentication, navigation, form inputs, trade actions, administrative controls).
- Organized into three strictly isolated portal domains:
  - **Trade Terminal** (`workflows/trade_terminal/`) — Maintained by Developer 1
  - **Admin Portal** (`workflows/admin_portal/`) — Maintained by Developer 2
  - **Client Portal** (`workflows/client_portal/`) — Maintained by Developer 3
- Shared infrastructure (`workflows/shared/`) provides `BasePage`, browser lifecycle fixtures, common assertions, waits, and logging.

---

## 📁 Repository Directory Structure

```text
Playwrite/new/
│
├── ui_regression/                    # DOM-level structural/UI regression testing
│   ├── crawler/                      # Multi-viewport crawler & element extractor
│   ├── comparer/                     # 6-tier matching engine & drift comparer
│   ├── element_output/               # Version-controlled baseline snapshots (Client)
│   ├── element_output_admin/         # Version-controlled baseline snapshots (Admin)
│   └── tests/                        # DOM regression unit & accuracy tests
│
├── workflows/                        # Behavioral / Functional / E2E workflow testing
│   ├── trade_terminal/               # Developer 1 Domain: Trade Terminal tests & pages
│   │   ├── pages/                    # Page Objects (LoginPage, OrderEntryPage, etc.)
│   │   ├── tests/                    # Behavioral workflow test suites
│   │   ├── fixtures/                 # Portal fixtures & session state injection
│   │   ├── test_data/                # Portal-specific test payloads & constants
│   │   └── utils/                    # Portal-specific helper functions
│   │
│   ├── admin_portal/                 # Developer 2 Domain: Admin Portal tests & pages
│   │   ├── pages/                    # Admin Console Page Objects
│   │   ├── tests/                    # Admin workflow test suites
│   │   ├── fixtures/                 # Admin fixtures & session state injection
│   │   ├── test_data/                # Admin test roles, payloads, and mock data
│   │   └── utils/                    # Admin-specific helper functions
│   │
│   ├── client_portal/                # Developer 3 Domain: Client Portal tests & pages
│   │   ├── pages/                    # Client Portal Page Objects (Dashboard, Watchlist, etc.)
│   │   ├── tests/                    # Client workflow test suites
│   │   ├── fixtures/                 # Client fixtures & session state injection
│   │   ├── test_data/                # Client profile, KYC, and deposit test data
│   │   └── utils/                    # Client-specific helper functions
│   │
│   └── shared/                       # Cross-portal reusable infrastructure
│       ├── pages/                    # BasePage with high-level Playwright wrappers
│       ├── fixtures/                 # Browser lifecycle & auth caching fixtures
│       ├── utils/                    # Robust wait helpers, logger, screenshots
│       ├── constants/                # Common timeouts, viewports, canonical routes
│       ├── assertions/               # Readable assertion helper functions
│       └── test_data/                # Common test generators
│
├── config/                           # Central configuration management
│   ├── settings.py                   # Strongly typed dataclass settings loaded from .env
│   └── environments/                 # Environment profiles (staging, prod, local)
│
├── auth/                             # Storage state sessions (gitignored, session cookies)
├── reports/                          # Segregated run artifacts (gitignored)
│   ├── ui_regression/                # DOM drift comparison reports (JSON)
│   └── workflows/                    # Failure screenshots, traces, and HTML reports
│
├── scripts/                          # Convenience execution scripts
│   ├── run_dom_regression.sh         # Execute DOM regression test suite
│   ├── run_all_workflows.sh          # Execute all behavioral workflows
│   ├── run_trade_tests.sh            # Execute Trade Terminal workflows (Dev 1)
│   ├── run_admin_tests.sh            # Execute Admin Portal workflows (Dev 2)
│   ├── run_client_tests.sh           # Execute Client Portal workflows (Dev 3)
│   └── status.py                     # Report status inspector utility
│
├── docs/                             # Engineering documentation
│   ├── architecture.md
│   ├── developer-guide.md
│   ├── workflow-testing.md
│   ├── git-workflow.md
│   ├── ownership.md
│   └── repository-cleanup.md
│
├── .github/
│   └── pull_request_template.md      # Standardized pull request template
│
├── .env.example                      # Documented environment variable template
├── .gitignore                        # Comprehensive Git ignore rules
├── conftest.py                       # Root test configuration & failure hooks
├── pytest.ini                        # Pytest configuration & registered markers
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# 1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <repository-folder>

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\Activate.ps1 # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binaries
playwright install chromium
```

### 2. Environment Configuration

Create your local `.env` from the provided template:

```bash
cp .env.example .env
```

Open `.env` and fill in credentials for your assigned portal:
- **Developer 1 (Trade)**: Set `TRADE_USERNAME` and `TRADE_PASSWORD`
- **Developer 2 (Admin)**: Set `ADMIN_USERNAME` and `ADMIN_PASSWORD`
- **Developer 3 (Client)**: Set `CLIENT_USERNAME` and `CLIENT_PASSWORD`

> 🔒 **Security Notice**: `.env` and `auth/*.json` contain sensitive local credentials and session cookies. They are strictly ignored by `.gitignore` and must **never** be committed.

---

## 🧪 Running Tests

### Running DOM Regression Tests (`ui_regression/`)

```bash
# Run all DOM regression unit & accuracy tests
pytest ui_regression/

# Or using the convenience script
./scripts/run_dom_regression.sh

# Run specific DOM regression test suites
pytest ui_regression/tests/test_comparer_accuracy.py
pytest ui_regression/tests/test_viewports.py
pytest ui_regression/tests/test_baseline_live_urls.py

# Run live DOM comparison against baselines across 5 viewports
python -m ui_regression.comparer.run_comparer --headed

# Run live Admin DOM comparison
python -m ui_regression.comparer.run_comparer_admin --headed

# Inspect generated report status
python scripts/status.py
```

### Running Behavioral Workflow Tests (`workflows/`)

```bash
# Run all behavioral workflow suites across all portals
pytest workflows/

# Or using the convenience script
./scripts/run_all_workflows.sh
```

### Portal-Specific Workflow Execution

```bash
# Developer 1: Trade Terminal
pytest workflows/trade_terminal/
# or: ./scripts/run_trade_tests.sh
# or by marker: pytest -m trade

# Developer 2: Admin Portal
pytest workflows/admin_portal/
# or: ./scripts/run_admin_tests.sh
# or by marker: pytest -m admin

# Developer 3: Client Portal
pytest workflows/client_portal/
# or: ./scripts/run_client_tests.sh
# or by marker: pytest -m client
```

### Marker-Based Execution

```bash
# Run fast smoke tests across all portals
pytest -m smoke

# Run full regression suites
pytest -m regression

# Run UI regression tests
pytest -m ui
```

---

## 👥 Git Workflow Overview

The team follows a trunk-based feature-branch model centered around `main`:

```text
main (Protected)
 │
 ├── feature/trade-<feature>    (Developer 1)
 ├── feature/admin-<feature>    (Developer 2)
 └── feature/client-<feature>   (Developer 3)
```

1. Always branch from the latest `origin/main`.
2. Confine work to your assigned portal directory (`workflows/trade_terminal/`, `workflows/admin_portal/`, or `workflows/client_portal/`).
3. Communicate shared infrastructure changes in `workflows/shared/` or `config/`.
4. Run your portal tests and the DOM regression suite before pushing:
   ```bash
   pytest ui_regression/
   pytest workflows/<your_portal>/
   ```
5. Push your feature branch and open a Pull Request using the `.github/pull_request_template.md`.

For full details, rebase instructions, and conflict resolution, see **[Git Workflow Guide](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/git-workflow.md)**.
