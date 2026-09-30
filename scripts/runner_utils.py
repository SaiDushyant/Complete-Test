"""
Shared utilities and environment resolution for test runner scripts.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent.parent

COMMON_PYTEST_PATHS = [
    Path("/opt/miniconda3/envs/playwright-env/bin/pytest"),
    Path.home() / "miniconda3" / "envs" / "playwright-env" / "bin" / "pytest",
]


def resolve_pytest_cmd() -> List[str]:
    """
    Resolves the best pytest invocation command.
    Prioritizes current sys.executable if pytest is importable,
    otherwise falls back to known conda environment pytests or system pytest.
    """
    try:
        import pytest  # noqa: F401
        return [sys.executable, "-m", "pytest"]
    except ImportError:
        pass

    for candidate in COMMON_PYTEST_PATHS:
        if candidate.exists() and candidate.is_file():
            return [str(candidate)]

    system_pytest = shutil.which("pytest")
    if system_pytest:
        return [system_pytest]

    return [sys.executable, "-m", "pytest"]
