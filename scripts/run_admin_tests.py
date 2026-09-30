#!/usr/bin/env python3
"""
Admin Portal Test Runner.

Executes all automated workflow tests for the Admin Management Portal
(Manager Management, Order Management, Categories A/B/C, User Margins,
Symbol Configurations, Subgroups, Book Reports, and Admin Roles).

Default execution mode: HEADLESS (use --headed to visually watch tests).

Usage:
    python scripts/run_admin_tests.py [OPTIONS]

Examples:
    python scripts/run_admin_tests.py                   # Run all admin tests headless
    python scripts/run_admin_tests.py --headed          # Run admin tests in headed browser
    python scripts/run_admin_tests.py -m orders         # Run only admin orders tests
    python scripts/run_admin_tests.py -k "category_a"   # Run Category A order lifecycle tests
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from scripts.runner_utils import resolve_pytest_cmd


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Admin Portal Test Runner (workflows/admin_portal/tests/).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="Launch visible browser window (default: headless)",
    )
    parser.add_argument(
        "-k",
        "--expression",
        type=str,
        default=None,
        help="Pytest substring filter expression for test names",
    )
    parser.add_argument(
        "-m",
        "--marker",
        type=str,
        default=None,
        help="Pytest marker expression (e.g. 'orders', 'category_a', 'category_b', 'category_c')",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Increase verbosity level (-v, -vv)",
    )
    parser.add_argument(
        "-n",
        "--workers",
        type=str,
        default=None,
        help="Number of parallel pytest workers (e.g. -n 4)",
    )
    parser.add_argument(
        "--slowmo",
        type=int,
        default=None,
        help="Slow down Playwright execution by N milliseconds",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    admin_tests_dir = ROOT_DIR / "workflows" / "admin_portal" / "tests"

    print("=" * 80)
    print("🏢 ADMIN PORTAL TEST RUNNER")
    print("=" * 80)
    print(f"  Target Suite        : {admin_tests_dir}")
    print(f"  Execution Mode      : {'HEADED' if args.headed else 'HEADLESS'}")
    if args.marker:
        print(f"  Marker Filter (-m)  : {args.marker}")
    if args.expression:
        print(f"  Name Filter (-k)    : {args.expression}")
    print("=" * 80)
    print()

    cmd = resolve_pytest_cmd() + [str(admin_tests_dir)]

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
        cmd.extend(["-n", str(args.workers)])

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    if args.headed:
        env["BROWSER_HEADLESS"] = "false"
        env["CRAWLER_HEADLESS"] = "false"
    else:
        env["BROWSER_HEADLESS"] = "true"
        env["CRAWLER_HEADLESS"] = "true"

    result = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env)

    logs_dir = ROOT_DIR / "reports" / "workflows" / "logs"
    print()
    print("=" * 80)
    print("📊 ADMIN PORTAL REPORTS GENERATED")
    print("=" * 80)
    print(f"  📄 Text Summary  : {logs_dir / 'global_test_summary.txt'}")
    print(f"  📊 JSON Results  : {logs_dir / 'global_test_results.json'}")
    print("=" * 80)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
