# Technical Documentation: Multi-Viewport DOM Regression & Drift Detection Engine

## Table of Contents
1. [Introduction](#1-introduction)
2. [Root Cause Analysis of False Drifts](#2-root-cause-analysis-of-false-drifts)
3. [The 6-Tier Matching Algorithm](#3-the-6-tier-matching-algorithm)
4. [Noise Filtering & Dynamic Value Masking](#4-noise-filtering--dynamic-value-masking)
5. [Cross-Environment Comparison & Canonical Routing](#5-cross-environment-comparison--canonical-routing)
6. [Accuracy Metrics & Verification](#6-accuracy-metrics--verification)
7. [CLI & Programmatic API](#7-cli--programmatic-api)
8. [Maintenance & Adding New Views](#8-maintenance--adding-new-views)

---

## 1. Introduction

This system is an automated regression test and DOM drift detection framework designed to detect visual and structural regressions across web applications. It tests responsive web applications at five distinct viewport breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`) and ensures that dynamic applications (such as live trading dashboards, financial market charts, and real-time administrative consoles) can be compared reliably without false-positive drift alerts.

---

## 2. Root Cause Analysis of False Drifts

Prior to the current architecture, two primary failure modes caused significant false-positive drift:

### 2.1 The Domino Cascade Effect (Bare Tag Pairing in Pass 4)
- **Problem**: Approximately 85% of elements in modern web apps are generic tags (`span`, `div`, `h6`) without unique IDs. When comparing elements sequentially using bare tag locators (`b_loc == "span"`), a single missing or added element (such as an extra live ticker row or an ephemeral banner) shifted the alignment index by 1. Every subsequent element in document order was paired with an off-by-one neighbor (`baseline[i]` paired with `live[i-1]`), creating cascades of 500+ false element modifications.
- **Solution**: Pass 4 now strictly enforces `b_loc and b_loc.lower() != b_tag`. Generic bare tags are never matched sequentially in Pass 4; instead, they proceed to Pass 5 where they are matched by **Tag + Classes + Text** or **Tag + Semantic Attributes**.

### 2.2 Duplicate ID Collisions Across Tabs
- **Problem**: Complex single-page apps (such as order entry forms with *Market*, *Limit*, and *Stop* tabs) reuse identical input IDs (e.g. 11 instances of `id="email"`, 2 instances of `id="navtoggle"`, 2 instances of `id="tab-1"`). When a standard hash map `live_id_map[(tag, id)] = idx` was populated, subsequent instances overwrote earlier ones, retaining only the last element. This caused cross-tab pairing errors (e.g. elements in the Market tab paired against the Stop tab).
- **Solution**: `live_id_map` is now built as a `defaultdict(deque)`. Elements with identical IDs are stored in document order and matched using FIFO `deque.popleft()`, ensuring accurate, tab-consistent pairing.

### 2.3 Table Cell Record Differences vs. UI Controls
- **Problem**: In data tables (such as Multi-Account Manager / MAM account lists or closed trade histories), dynamic user names and ticket numbers caused hundreds of diffs.
- **Solution**: The DOM extractor annotates elements with `in_table_cell = Boolean(element.closest && element.closest("td, th"))`. The comparer identifies table data cells and normalizes non-action text values to `[TABLE_DATA_CELL]`, preserving strict diffs for interactive controls (*Edit*, *Delete*, *Open*, *Close*).

---

## 3. The 6-Tier Matching Algorithm

The matching process in `ElementComparer.match_and_diff_elements` runs in $O(N)$ time through six specialized passes:

```
Baseline Elements + Live Elements
               │
               ▼
   [Tier 1: Unique Locators]       --> Matched if is_unique=True and locator is non-bare
               │ (Unmatched)
               ▼
   [Tier 2: Unique ID (FIFO)]      --> Matched by (tag, normalized_id) via document-order deque
               │ (Unmatched)
               ▼
   [Tier 3: Semantic Attributes]   --> Matched by data-testid, data-nav, data-page, data-symbol, etc.
               │ (Unmatched)
               ▼
   [Tier 4: Specific Locators]     --> Matched by non-bare CSS selectors (e.g. button.btn-primary)
               │ (Unmatched)
               ▼
   [Tier 5: Fallback Matching]
      ├── 5a: Tag + Classes + Text
      ├── 5b: Tag + Text
      └── 5c: Tag + Classes
               │ (Unmatched)
               ▼
   [Tier 6: Document Tag Align]    --> Remaining bare tags matched in document order
```

---

## 4. Noise Filtering & Dynamic Value Masking

`NoiseFilter` provides regex and set-based normalization:

1. **Relative Times**: `\b(?:\d+\s+(?:days?|hours?|hrs?|minutes?|mins?|seconds?|secs?)\s*)+ago\b` $\to$ `[RELATIVE_TIME]`
2. **Timestamps & Clocks**: `10:45:23`, `10:45 AM` $\to$ `[TIME]`
3. **Dates**: `2026-09-24`, `24/09/2026`, `Sep 24, 2026` $\to$ `[DATE]`
4. **Prices & Currencies**: `$ 1.13823`, `€12.50`, `50.5 USDT` $\to$ `[PRICE]`
5. **Formatted Numbers & Floats**: `2,904`, `1,234.56`, `0.08` $\to$ `[NUMBER]`, `[FLOAT]`
6. **Percentages**: `18.7%`, `-0.44%`, `+4.96%` $\to$ `[PERCENT]`
7. **Position Counters**: `Positions (5)`, `Pending Orders (0)` $\to$ `[POSITIONS_COUNT]`
8. **Dynamic IDs & Tokens**: `tradingview_*`, `gridRectMask*`, `Svgjs*`, `apexcharts*` $\to$ normalized deterministic IDs
9. **Ignored Attributes**: `x, y, dx, dy, cx, cy, points, fill, stroke, d, style, data-v-*, data-session, data-csrf`
10. **Cross-Environment URLs & Domains**: When `LIVE_URL != BASELINE_URL`, URLs in text and attributes (`href`, `src`, `action`) pointing to the baseline domain are masked to `[BASE_URL]` / `[BASE_DOMAIN]` for baseline elements, and live domain references are masked for live elements.

---

## 5. Cross-Environment Comparison & Canonical Routing

When testing pre-production, staging, or preview deployments against fixed baseline snapshots:
- **Canonical Route Matching**: Compares views by path and query (`/analytics?tab=overview`) rather than full absolute URLs. This eliminates 100% false `PAGE_MISSING_IN_LIVE` and `NEW_PAGE_IN_LIVE` errors when hostnames differ.
- **Isolated Authentication States**: Prevents live session cookies from corrupting or overwriting baseline session cache by keeping distinct `auth_state.json` and `auth_state_live.json` files.
- **Independent Credentials**: Allows specifying environment-specific credentials (e.g. `LIVE_TEST_USER_EMAIL`, `LIVE_ADMIN_USER_USERNAME`) if credentials differ between baseline and live environments.

---

## 6. Accuracy Metrics & Verification

Accuracy is evaluated across two dimensions:

### 6.1 Element-Level Matching Accuracy
$$\text{Element Accuracy} = \frac{\text{Total Matched Unchanged Elements}}{\text{Total Baseline Elements}} \times 100\%$$

- **Admin Console Suite**: **99.93%** element accuracy (263,397 matched unchanged out of 263,586 elements).
- **Trading / Client Suite**: **97.29%** element accuracy after cascade elimination.
- **Overall System Element Accuracy**: **99.50%** across all combined suites.

### 6.2 View-Level Stability
$$\text{View Accuracy} = \frac{\text{Total Views With Zero Drift}}{\text{Total Views Compared}} \times 100\%$$

- **Admin Console**: 199 out of 215 views (92.6%) have zero drift.
- **Client Portal**: Public and authenticated root views match cleanly.

---

## 7. CLI & Programmatic API

### 7.1 Running Comparisons

```bash
# Compare Client Portal against ui_regression/element_output/
python -m ui_regression.comparer.run_comparer --viewports sm,md,lg,xl,2xl

# Compare live with a different target URL (cross-environment):
python -m ui_regression.comparer.run_comparer --live-url https://preview.xtremenext.com/ --viewports sm,md,lg,xl,2xl

# Compare Admin Console against ui_regression/element_output_admin/
python -m ui_regression.comparer.run_comparer_admin --viewports sm,md,lg,xl,2xl

# Compare live Admin with a different target URL:
python -m ui_regression.comparer.run_comparer_admin --live-url https://preview.xtremenext.com/admin/Controlbase/Dashboard --viewports sm,md,lg,xl,2xl

# Headed mode for visual debugging
python -m ui_regression.comparer.run_comparer --viewports sm --headed
```

### 7.2 Programmatic Usage

```python
from pathlib import Path
from ui_regression.comparer.comparer import ElementComparer, NoiseFilter

noise_filter = NoiseFilter(enabled=True)
comparer = ElementComparer(baseline_dir=Path("ui_regression/element_output"), noise_filter=noise_filter)

# Load baseline snapshots
baselines = comparer.load_baseline_snapshots()

# Run comparison
report = comparer.compare_all(baselines, live_snapshots)
comparer.save_report(report, Path("reports/ui_regression/comparison_report.json"))
```

---

## 8. Maintenance & Adding New Views

### 8.1 Adding a New In-DOM View (SPA Sub-View)
To add a new in-DOM view (such as a modal or secondary tab):
1. In `ui_regression/crawler/crawler.py` (or `ui_regression/crawler/run_crawler_admin.py`), define the trigger selector for the view in `IN_DOM_VIEWS`.
2. Ensure the trigger action waits for network idle or selector visibility.
3. Rerun the crawler to capture baseline snapshots for all 5 viewports:
   ```bash
   python -m ui_regression.crawler.run_crawler --viewports sm,md,lg,xl,2xl
   ```
4. Verify tests pass:
   ```bash
   pytest ui_regression/tests/
   ```
