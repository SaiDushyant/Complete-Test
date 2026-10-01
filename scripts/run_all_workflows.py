#!/usr/bin/env python3
"""
Master Test Runner: Complete Behavioral Workflow Test Suite.

Executes all automated behavioral workflow tests across all portals
(Admin Portal, Client Portal, Trade Terminal, Cross-Portal Integrations).
Produces standardized TXT and JSON reports in reports/workflows/logs/.

Default execution mode: HEADLESS (headed mode is disabled by default).
Use --headed to launch a visible browser window for debugging.

Usage:
    python scripts/run_all_workflows.py [OPTIONS]

Examples:
    python scripts/run_all_workflows.py                     # All workflows headless
    python scripts/run_all_workflows.py --headed            # All workflows headed
    python scripts/run_all_workflows.py --portal admin      # Only Admin portal workflows
    python scripts/run_all_workflows.py -m smoke            # Only smoke tests
    python scripts/run_all_workflows.py -m regression       # Only regression tests
    python scripts/run_all_workflows.py -k "test_login"     # Pattern match by test name
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Set up project root in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from scripts.runner_utils import resolve_pytest_cmd

PORTAL_DIRECTORIES = {
    "all": ROOT_DIR / "workflows",
    "admin": ROOT_DIR / "workflows" / "admin_portal" / "tests",
    "client": ROOT_DIR / "workflows" / "client_portal" / "tests",
    "trade": ROOT_DIR / "workflows" / "trade_terminal" / "tests",
    "shared": ROOT_DIR / "workflows" / "shared" / "tests",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Master Test Runner: Complete Behavioral Workflow Test Suite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--portal",
        choices=["all", "admin", "client", "trade", "shared"],
        default="all",
        help="Target portal/module to execute (default: all)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="Launch visible browser window (default: headless)",
    )
    parser.add_argument(
        "-m",
        "--marker",
        type=str,
        default=None,
        help="Pytest marker expression (e.g., 'smoke', 'regression', 'critical', 'orders')",
    )
    parser.add_argument(
        "-k",
        "--expression",
        type=str,
        default=None,
        help="Pytest substring filter expression for test names",
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
        help="Number of parallel pytest workers (e.g. -n 4 or -n auto)",
    )
    parser.add_argument(
        "--dist",
        type=str,
        default="loadfile",
        choices=["load", "loadfile", "loadgroup", "worksteal"],
        help="Parallel test distribution mode (default: loadfile for module-level dynamic work stealing)",
    )
    parser.add_argument(
        "--slowmo",
        type=int,
        default=None,
        help="Slow down Playwright execution by N milliseconds (useful with --headed)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory for test execution logs",
    )
    return parser.parse_args()


def run_workflows(args: argparse.Namespace) -> int:
    target_path = PORTAL_DIRECTORIES.get(args.portal, ROOT_DIR / "workflows")
    
    print("=" * 80)
    print("🚀 MASTER BEHAVIORAL WORKFLOW RUNNER")
    print("=" * 80)
    print(f"  Target Portal/Suite : {args.portal.upper()} ({target_path})")
    print(f"  Execution Mode      : {'HEADED (Visible Browser)' if args.headed else 'HEADLESS (Background)'}")
    if args.marker:
        print(f"  Marker Filter (-m)  : {args.marker}")
    if args.expression:
        print(f"  Name Filter (-k)    : {args.expression}")
    if args.slowmo:
        print(f"  SlowMo Delay        : {args.slowmo}ms")
    print("=" * 80)
    print()

    # Build pytest command
    cmd = resolve_pytest_cmd() + [str(target_path)]

    if args.verbose > 0:
        cmd.append("-" + "v" * args.verbose)

    if args.headed:
        cmd.append("--headed")

    if args.slowmo is not None:
        cmd.extend(["--slowmo", str(args.slowmo)])

    if args.marker:
        cmd.extend(["-m", args.marker])

    if args.expression:
        cmd.extend(["-k", args.expression])

    if args.workers:
        cmd.extend(["-n", str(args.workers), "--dist", args.dist])

    # Setup environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    if args.headed:
        env["BROWSER_HEADLESS"] = "false"
        env["CRAWLER_HEADLESS"] = "false"
    else:
        env["BROWSER_HEADLESS"] = "true"
        env["CRAWLER_HEADLESS"] = "true"

    if args.output_dir:
        env["REPORTS_LOGS_DIR"] = str(Path(args.output_dir).resolve())

    # Execute pytest
    result = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env)

    # Print summary location pointers
    logs_dir = Path(args.output_dir) if args.output_dir else (ROOT_DIR / "reports" / "workflows" / "logs")
    print()
    print("=" * 80)
    print("📊 EXECUTION ARTIFACTS & REPORTS GENERATED")
    print("=" * 80)
    print(f"  📄 Text Summary Report   : {logs_dir / 'global_test_summary.txt'}")
    print(f"  📄 Passed Tests List     : {logs_dir / 'global_passed_tests.txt'}")
    print(f"  📄 Failed Tests List     : {logs_dir / 'global_failed_tests.txt'}")
    print(f"  📄 Skipped Tests List    : {logs_dir / 'global_skipped_tests.txt'}")
    print(f"  📊 JSON Master Results   : {logs_dir / 'global_test_results.json'}")
    print(f"  📊 JSON Summary Report   : {logs_dir / 'summary_report.json'}")
    print(f"  📁 Individual Test Logs  : {logs_dir / 'individual'}")
    print("=" * 80)

    return result.returncode


def main():
    args = parse_arguments()
    exit_code = run_workflows(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
