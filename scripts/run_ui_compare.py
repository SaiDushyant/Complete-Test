#!/usr/bin/env python3
"""
UI DOM Regression Comparison Runner (Comparison Only).

Compares existing baseline DOM snapshots against live web pages without re-crawling.
Detects missing elements, added elements, attribute changes, style mutations,
and tracks runtime telemetry errors (Console JS errors, uncaught exceptions, HTTP/network failures).

Default execution mode: HEADLESS (use --headed to visually watch page visits).

Usage:
    python scripts/run_ui_compare.py [OPTIONS]

Examples:
    python scripts/run_ui_compare.py                         # Compare both Admin and Client portals
    python scripts/run_ui_compare.py --portal admin          # Compare only Admin Portal
    python scripts/run_ui_compare.py --portal client         # Compare only Client Portal
    python scripts/run_ui_compare.py --headed                # Visually inspect page comparison
    python scripts/run_ui_compare.py --viewports desktop     # Only compare desktop viewport
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
UI_REGRESSION_DIR = ROOT_DIR / "ui_regression"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(UI_REGRESSION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_REGRESSION_DIR))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UI DOM Regression Comparison Runner (Comparison Only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--portal",
        choices=["admin", "client", "both"],
        default="both",
        help="Portal to compare: admin, client, or both (default: both)",
    )
    parser.add_argument(
        "--viewports",
        nargs="+",
        default=None,
        help="Viewports to compare: desktop, mobile, tablet (default: all)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in visible/headed mode (default: headless)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save comparison reports",
    )
    return parser.parse_args()


async def main_async():
    args = parse_arguments()
    headless = not args.headed

    print("=" * 80)
    print("🔍 UI DOM REGRESSION COMPARISON RUNNER")
    print("=" * 80)
    print(f"  Target Portal(s)    : {args.portal.upper()}")
    print(f"  Execution Mode      : {'HEADED (Visible Browser)' if args.headed else 'HEADLESS (Background)'}")
    print(f"  Viewports           : {args.viewports or 'All configured'}")
    print("=" * 80)
    print()

    # Set environment variables
    os.environ["BROWSER_HEADLESS"] = "false" if args.headed else "true"
    os.environ["CRAWLER_HEADLESS"] = "false" if args.headed else "true"

    reports_generated = []

    # 1. Admin Portal Comparison
    if args.portal in ("admin", "both"):
        print("\n" + "=" * 60)
        print("🏢 Starting Admin Portal Comparison...")
        print("=" * 60)
        from ui_regression.comparer.run_comparer_admin import run_comparer_workflow as run_admin_compare

        admin_out_dir = Path(args.output_dir) if args.output_dir else (ROOT_DIR / "reports" / "ui_regression")
        admin_report = await run_admin_compare(
            viewports=args.viewports,
            output_dir=admin_out_dir,
            headless=headless,
        )
        reports_generated.append(("Admin Portal", admin_report))

    # 2. Client Portal Comparison
    if args.portal in ("client", "both"):
        print("\n" + "=" * 60)
        print("👤 Starting Client Portal Comparison...")
        print("=" * 60)
        from ui_regression.comparer.run_comparer import run_comparer_workflow as run_client_compare

        client_out_dir = Path(args.output_dir) if args.output_dir else (ROOT_DIR / "reports" / "ui_regression")
        client_report = await run_client_compare(
            viewports=args.viewports,
            output_dir=client_out_dir,
            headless=headless,
        )
        reports_generated.append(("Client Portal", client_report))

    print()
    print("=" * 80)
    print("📊 COMPARISON REPORTS GENERATED")
    print("=" * 80)
    for portal_name, report_path in reports_generated:
        print(f"  - {portal_name:<16}: {report_path}")
    print("=" * 80)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
