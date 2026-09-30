#!/usr/bin/env python3
"""
Trade Terminal Test Runner.

Executes all automated workflow tests for the Web Trading Terminal
(Watchlist, Symbol Search, Buy/Sell Orders, Positions, Margin Level,
API Access, Settings, and Copy Trading Manager/Follower Replication).

Default execution mode: HEADLESS (use --headed to visually watch tests).

Usage:
    python scripts/run_trade_tests.py [OPTIONS]

Examples:
    python scripts/run_trade_tests.py                   # Run all trade terminal tests headless
    python scripts/run_trade_tests.py --headed          # Run trade tests in headed browser
    python scripts/run_trade_tests.py -m mam            # Run MAM replication tests
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
        description="Trade Terminal Test Runner (workflows/trade_terminal/tests/).",
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
        help="Pytest marker expression (e.g. 'mam', 'pamm', 'trade')",
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
    trade_tests_dir = ROOT_DIR / "workflows" / "trade_terminal" / "tests"

    print("=" * 80)
    print("📈 TRADE TERMINAL TEST RUNNER")
    print("=" * 80)
    print(f"  Target Suite        : {trade_tests_dir}")
    print(f"  Execution Mode      : {'HEADED' if args.headed else 'HEADLESS'}")
    if args.marker:
        print(f"  Marker Filter (-m)  : {args.marker}")
    if args.expression:
        print(f"  Name Filter (-k)    : {args.expression}")
    print("=" * 80)
    print()

    cmd = resolve_pytest_cmd() + [str(trade_tests_dir)]

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
    print("📊 TRADE TERMINAL REPORTS GENERATED")
    print("=" * 80)
    print(f"  📄 Text Summary  : {logs_dir / 'global_test_summary.txt'}")
    print(f"  📊 JSON Results  : {logs_dir / 'global_test_results.json'}")
    print("=" * 80)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
