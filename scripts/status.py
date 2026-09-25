"""
Report Status Inspector.
Parses a DOM comparison report JSON and prints a comprehensive breakdown of
page drift statuses, baseline vs live element counts, and detailed drift statistics.

Usage:
    python scripts/status.py [path_to_report.json]
Default report:
    reports/ui_regression/comparison_report_admin.json (fallback: comparison_report_admin.json)
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DEFAULT_REPORT_CANDIDATES = [
    ROOT_DIR / "reports" / "ui_regression" / "comparison_report_admin.json",
    ROOT_DIR / "comparison_report_admin.json",
    ROOT_DIR / "reports" / "ui_regression" / "comparison_report.json",
    ROOT_DIR / "comparison_report.json",
]


def resolve_report_file() -> Path:
    if len(sys.argv) > 1:
        custom_path = Path(sys.argv[1])
        if custom_path.exists():
            return custom_path
        print(f"Warning: Specified report file '{custom_path}' does not exist.")

    for candidate in DEFAULT_REPORT_CANDIDATES:
        if candidate.exists():
            return candidate

    return DEFAULT_REPORT_CANDIDATES[0]


def find_all_statuses(report_file):
    report_path = Path(report_file)
    if not report_path.exists():
        print(f"Report file not found: {report_path}")
        print("Run comparer first to generate comparison report:")
        print("  python -m ui_regression.comparer.run_comparer_admin")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("pages", [])

    # Group pages by status
    pages_by_status = defaultdict(list)

    for page in pages:
        status = page.get("status", "UNKNOWN")
        pages_by_status[status].append(page)

    # Status counts
    status_counts = Counter(
        page.get("status", "UNKNOWN")
        for page in pages
    )

    print("=" * 100)
    print(f"STATUS SUMMARY: {report_path.name}")
    print("=" * 100)

    print(f"Total pages: {len(pages)}")
    print(f"Unique statuses: {len(status_counts)}")
    print()

    for status, count in status_counts.most_common():
        print(f"{status}: {count}")

    print()
    print("=" * 100)
    print("PAGES BY STATUS")
    print("=" * 100)

    for status, status_pages in pages_by_status.items():
        print()
        print(f"\n[{status}] - {len(status_pages)} pages")
        print("-" * 100)

        for page in status_pages:
            print(f"URL:    {page.get('url')}")
            print(f"Title:  {page.get('title')}")
            print(f"Type:   {page.get('type')}")
            print(f"File:   {page.get('baseline_file')}")

            stats = page.get("statistics", {})

            print(
                f"Stats:  "
                f"baseline={stats.get('baseline_element_count', 0)}, "
                f"live={stats.get('live_element_count', 0)}, "
                f"modified={stats.get('modified', 0)}, "
                f"missing={stats.get('missing', 0)}, "
                f"added={stats.get('added', 0)}"
            )
            print("-" * 100)


if __name__ == "__main__":
    target_report = resolve_report_file()
    find_all_statuses(target_report)
