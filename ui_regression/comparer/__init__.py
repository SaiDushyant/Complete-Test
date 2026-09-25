"""
Playwright DOM Element Comparer & Drift Detection Package.
"""

from comparer.comparer import ElementComparer, NoiseFilter
from comparer.comparer_config import BASELINE_DIR, COMPARISON_REPORT_FILE

__all__ = [
    "ElementComparer",
    "NoiseFilter",
    "BASELINE_DIR",
    "COMPARISON_REPORT_FILE",
]
