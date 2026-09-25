# Repository Audit & Clean-Up Report

This document records the comprehensive repository audit, clean-up operations, architectural restructuring decisions, and security audit conducted across this codebase.

---

## 1. Initial State Inventory

Before making any changes, the repository was audited across all directories, scripts, tests, dependencies, and configuration files.

### Key Components Discovered
1. **DOM Regression Engine**: Completed multi-viewport crawling and drift detection framework (`crawler/` and `comparer/`).
2. **DOM Baseline Snapshots**:
   - `element_output/`: 116 JSON snapshots of Client Portal across 5 viewports (`sm`, `md`, `lg`, `xl`, `2xl`).
   - `element_output_admin/`: 216 JSON snapshots of Admin Portal across 5 viewports.
   - `element_output_old/`: 37 unversioned legacy single-viewport JSON snapshots from an obsolete early crawl.
3. **Behavioral Workflows**: Initial foundational structure under `workflows/` covering `trade_terminal/`, `admin_portal/`, `client_portal/`, and `shared/`.
4. **Obsolete Root Assets**:
   - Flat `pages/` directory (`pages/auth/login_page.py`, `pages/watchlist/watchlist_page.py`) left over from early prototype tasks.
   - Root `tests/` directory (`test_baseline_live_urls.py`, `test_comparer_accuracy.py`, `test_viewports.py`, and `tests/auth/test_auth.py`).
   - Root `status.py` utility script hardcoding `comparison_report_admin.json`.
   - Root runtime artifacts: `comparison_report.json` (2.8 MB), `comparison_report_admin.json` (328 KB), `auth_state.json` (1.3 KB), `auth_state_admin.json` (587 B).
   - `.vscode/settings.json` containing local conda environment manager paths.

---

## 2. What Was Removed and Rationale

| File / Directory Removed | Classification | Rationale |
| :--- | :--- | :--- |
| `element_output_old/` (37 files) | **Obsolete Artifacts** | Pre-multi-viewport single-breakpoint crawl outputs superseded by `element_output/`. Had no viewport metadata and was not referenced in code. |
| Root `pages/` (`pages/auth/`, `pages/watchlist/`) | **Duplicate / Obsolete Code** | Early prototypes replaced by modern Page Objects in `workflows/client_portal/pages/` and `workflows/shared/pages/base_page.py`. |
| Root `status.py` | **Relocated Script** | Moved and enhanced as `scripts/status.py` with multi-path resolution and CLI argument support. |
| `tests/auth/test_auth.py` | **Relocated Test** | Watchlist session test was migrated into the Client Portal behavioral suite as `workflows/client_portal/tests/test_client_watchlist.py`. |
| Root `tests/` | **Restructured Directory** | The 3 DOM regression test suites were moved under `ui_regression/tests/`. |
| `__pycache__/` and `*.pyc` across all directories | **Python Bytecode Caches** | Generated runtime artifacts. Removed and excluded via `.gitignore`. |
| `.pytest_cache/` | **Test Runner Cache** | Generated test cache. Removed and excluded via `.gitignore`. |
| Root `comparison_report*.json` | **Generated Report Artifacts** | Generated run outputs from past crawls. Moved to `reports/ui_regression/` and ignored by Git. |
| Root `auth_state*.json` | **Session Storage States** | Active session cookie dumps. Moved to `auth/` and strictly ignored by Git. |
| `.vscode/` | **IDE Metadata** | Machine-specific editor configuration. Ignored by Git. |

---

## 3. What Was Preserved (Intact & Untouched)

### Core DOM Regression Framework
The user instruction strictly required:
> *"Do NOT rewrite the crawler or comparer. Do NOT change their algorithms simply to make the folder structure cleaner. Do NOT remove working functionality."*

The following were preserved 100% intact:
1. **6-Tier Matching Algorithm**: `ui_regression/comparer/comparer.py` (Unique locators, Unique IDs with FIFO deque matching, Semantic data-* attributes, specific non-bare locators, Tag+Classes+Text fallbacks, and noise filtering).
2. **Multi-Viewport Crawling Engine**: `ui_regression/crawler/crawler.py` (BFS crawl, in-DOM views, canonical route defrag, 5-viewport switching).
3. **Dynamic Noise Filter**: `NoiseFilter` class in `comparer.py` (normalizing market ticks, prices, timestamps, table cells, and SVG paths).
4. **All 29 Existing DOM Regression Tests**: All 29 unit and accuracy tests in `test_baseline_live_urls.py`, `test_comparer_accuracy.py`, and `test_viewports.py` pass with 100% accuracy.
5. **Existing CLI Entry Points**: Preserved CLI options for `run_crawler.py`, `run_crawler_admin.py`, `run_comparer.py`, and `run_comparer_admin.py`.

---

## 4. Baseline Snapshot Decision & Rationale

A critical decision was required regarding `element_output/` and `element_output_admin/`:

### Decision: Authoritative Regression Baselines (Git-Tracked)
- **Investigation**: We examined `ui_regression/comparer/run_comparer.py` and `ui_regression/tests/test_comparer_accuracy.py`. The comparison engine requires pre-recorded baseline JSON files to compare live pages against. Specifically, `test_comparer_baseline_snapshot_accuracy` loads `home_view_dashboard_sm_43cd3bc8.json` to verify that element matching accuracy is $\ge 95\%$.
- **Conclusion**: `element_output/` (116 files) and `element_output_admin/` (216 files) are **authoritative ground truth baselines**, not temporary outputs. Without them, a developer cloning the repository would be unable to run the comparer or execute DOM regression tests.
- **Action Taken**: 
  - Moved them under `ui_regression/element_output/` and `ui_regression/element_output_admin/`.
  - Removed `element_output/` and `element_output_admin/` from `.gitignore` so they remain fully version-controlled.
  - Documented them as intentional repository assets.

---

## 5. Dependency Audit

Inspected `requirements.txt`:
```text
playwright
pytest
python-dotenv
```
- **Finding**: All workflow utilities (`dataclasses`, `logging`, `pathlib`, `typing`, `json`, `re`, `urllib.parse`) are Python Standard Library modules.
- **Assessment**: No unnecessary, heavy, or competing dependencies exist.
- **Action Taken**: Maintained the clean, minimal 3-dependency footprint without adding unneeded packages.

---

## 6. Security Audit Findings & Remediation

| Potential Security Risk | Audit Finding | Remediation Applied |
| :--- | :--- | :--- |
| **Passwords in Code** | No plaintext passwords found in Python source files. | Passwords read dynamically from `.env` via `config/settings.py`. |
| **Local `.env` File** | `.env` exists locally with developer credentials. | `.gitignore` rigorously ignores `.env`, `.env.local`, `.env.*`. Committed `.env.example` contains only blank placeholders. |
| **Authentication Session States** | `auth_state.json` and `auth_state_admin.json` contain active authentication session cookies and tokens. | Relocated from repository root into `auth/`. Excluded from Git via `.gitignore` (`auth/*.json` and `auth_state*.json`). |
| **Hardcoded Local Paths** | No hardcoded `/Users/...` machine paths in codebase; all paths use `Path(__file__).resolve().parent`. | Preserved portable, relative path calculations across all modules. |

> ⚠️ **Team Note on Credential Rotation**: If credentials were ever tested on public or non-secure machines in earlier iterations, ensure those credentials are rotated in your staging environment.
