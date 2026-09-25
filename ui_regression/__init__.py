"""
UI Regression and DOM Drift Detection Framework.

Contains:
- crawler: Multi-viewport live and baseline DOM extraction engine
- comparer: 6-tier element matching and noise-filtered drift comparison engine
- element_output: Authoritative client portal DOM baseline snapshots
- element_output_admin: Authoritative admin console DOM baseline snapshots
- tests: Unit and integration tests for crawler, comparer, and viewport regression
"""

import sys
from pathlib import Path

# Ensure ui_regression root and subpackages are resolvable
_UI_REGRESSION_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _UI_REGRESSION_DIR.parent

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_UI_REGRESSION_DIR) not in sys.path:
    sys.path.insert(0, str(_UI_REGRESSION_DIR))
