#!/usr/bin/env python3
"""
Master CLI Runner for Mock Testing Suites.
Executes mock server tests across Trade Terminal, Admin Portal, and Client Portal
with custom filtering, parallel workers, headed mode, and detailed reporting.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.runner_utils import resolve_pytest_cmd


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Mock Server & Network Interception Test Suites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_mock_tests.py
  python scripts/run_mock_tests.py --portal trade
  python scripts/run_mock_tests.py --portal admin
  python scripts/run_mock_tests.py --portal client
  python scripts/run_mock_tests.py --headed --slowmo 200
  python scripts/run_mock_tests.py -n 4
        """,
    )

    parser.add_argument(
        "--portal",
        choices=["trade", "admin", "client", "all"],
        default="all",
        help="Filter mock tests by portal domain (default: all)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="Launch visible browser window (default: headless)",
    )
    parser.add_argument(
        "--slowmo",
        type=int,
        default=None,
        help="Slow down test execution in milliseconds",
    )
    parser.add_argument(
        "-k",
        "--expression",
        dest="expression",
        type=str,
        default=None,
        help="Filter tests by keyword expression (pytest -k)",
    )
    parser.add_argument(
        "-m",
        "--marker",
        dest="marker",
        type=str,
        default="mock",
        help="Pytest marker expression (default: 'mock')",
    )
    parser.add_argument(
        "-n",
        "--workers",
        dest="workers",
        type=str,
        default=None,
        help="Run tests in parallel using pytest-xdist (e.g. -n 4)",
    )
    parser.add_argument(
        "--dist",
        dest="dist",
        type=str,
        default="loadfile",
        choices=["load", "loadfile", "loadgroup", "worksteal"],
        help="pytest-xdist distribution mode (default: loadfile)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Increase verbosity level (-v, -vv)",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # Determine target test paths based on portal selection
    target_paths = []
    if args.portal in ("trade", "all"):
        target_paths.append(str(ROOT_DIR / "workflows" / "trade_terminal" / "tests" / "mock"))
    if args.portal in ("admin", "all"):
        target_paths.append(str(ROOT_DIR / "workflows" / "admin_portal" / "tests" / "mock"))
    if args.portal in ("client", "all"):
        target_paths.append(str(ROOT_DIR / "workflows" / "client_portal" / "tests" / "mock"))

    # Build pytest command line
    cmd = resolve_pytest_cmd() + target_paths

    if args.marker:
        cmd.extend(["-m", args.marker])

    if args.verbose > 0:
        cmd.append("-" + "v" * args.verbose)

    if args.headed:
        cmd.append("--headed")

    if args.slowmo is not None:
        cmd.extend(["--slowmo", str(args.slowmo)])

    if args.expression:
        cmd.extend(["-k", args.expression])

    if args.workers:
        cmd.extend(["-n", str(args.workers), "--dist", args.dist])

    print("=" * 80)
    print("🚀 LAUNCHING MOCK TESTING SUITE")
    print("=" * 80)
    print(f"  Portal Scope    : {args.portal.upper()}")
    print(f"  Execution Mode  : {'HEADED' if args.headed else 'HEADLESS'}")
    print(f"  Marker Filter   : {args.marker}")
    if args.expression:
        print(f"  Name Filter     : {args.expression}")
    print(f"  Target Paths    : {', '.join(target_paths)}")
    print("=" * 80 + "\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    if args.headed:
        env["BROWSER_HEADLESS"] = "false"
    else:
        env["BROWSER_HEADLESS"] = "true"

    result = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
