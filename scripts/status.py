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

    summary = data.get("summary", {})
    telemetry = summary.get("telemetry", {})
    telemetry_errors = data.get("telemetry_errors", [])

    print("=" * 100)
    print(f"STATUS SUMMARY: {report_path.name}")
    print("=" * 100)

    print(f"Total pages/views : {len(pages)}")
    print(f"Unique statuses   : {len(status_counts)}")
    print()

    for status, count in status_counts.most_common():
        print(f"  {status:<22}: {count}")

    if telemetry or telemetry_errors:
        print()
        print("-" * 100)
        print("DIAGNOSTIC TELEMETRY & RUNTIME ERRORS:")
        print("-" * 100)
        print(f"  Console Errors (JS)      : {telemetry.get('console_errors_count', 0)}")
        print(f"  Console Warnings         : {telemetry.get('console_warnings_count', 0)}")
        print(f"  Uncaught JS Exceptions   : {telemetry.get('js_page_errors_count', 0)}")
        print(f"  Failed Network Requests  : {telemetry.get('failed_requests_count', 0)}")
        print(f"  HTTP 4xx/5xx Errors      : {telemetry.get('http_errors_count', 0)}")
        print(f"  Total Runtime Issues     : {telemetry.get('total_errors', len(telemetry_errors))}")

        if telemetry_errors:
            print("\n  🚨 SPECIFIC ERROR INCIDENTS:")
            for idx, err in enumerate(telemetry_errors[:20], 1):
                kind = err.get("kind", "error")
                url = err.get("url", "")
                vp = err.get("viewport", "")
                detail = err.get("detail", {})
                vp_str = f" [{vp}]" if vp else ""

                if kind == "console_error":
                    loc = detail.get("location", {})
                    loc_str = f" ({loc.get('url', '')}:{loc.get('lineNumber', '')})" if loc and loc.get("url") else ""
                    print(f"    {idx}. [Console Error]{vp_str} {url}: {detail.get('text', '')}{loc_str}")
                elif kind == "js_page_error":
                    print(f"    {idx}. [JS Exception]{vp_str} {url}: {detail.get('error', '')}")
                elif kind == "network_failed_request":
                    print(f"    {idx}. [Failed Request]{vp_str} {url}: {detail.get('url', '')} -> {detail.get('failure', '')}")
                elif kind == "http_error":
                    print(f"    {idx}. [HTTP Error]{vp_str} {url}: {detail.get('status', '')} {detail.get('status_text', '')} -> {detail.get('url', '')}")

            if len(telemetry_errors) > 20:
                print(f"    ... and {len(telemetry_errors) - 20} more runtime errors.")
        else:
            print("\n  ✅ Zero runtime errors, uncaught exceptions, or network failures recorded.")

    print()
    print("=" * 100)
    print("PAGES BY STATUS")
    print("=" * 100)

    for status, status_pages in pages_by_status.items():
        print()
        print(f"\n[{status}] - {len(status_pages)} pages")
        print("-" * 100)

        for page in status_pages:
            vp = page.get("viewport") or ""
            vp_str = f" [{vp}]" if vp else ""
            print(f"URL:    {page.get('url')}{vp_str}")
            print(f"Title:  {page.get('title')}")
            print(f"Type:   {page.get('type')}")
            print(f"File:   {page.get('baseline_file')}")

            stats = page.get("statistics", {})
            diag_sum = stats.get("diagnostics_summary", {})
            c_errs = diag_sum.get("console_errors_count", 0)
            js_errs = diag_sum.get("js_page_errors_count", 0)
            net_errs = diag_sum.get("failed_requests_count", 0)
            http_errs = diag_sum.get("http_errors_count", 0)

            print(
                f"Stats:  "
                f"baseline={stats.get('baseline_element_count', 0)}, "
                f"live={stats.get('live_element_count', 0)}, "
                f"modified={stats.get('modified', 0)}, "
                f"missing={stats.get('missing', 0)}, "
                f"added={stats.get('added', 0)} | "
                f"errors=(Console:{c_errs}, JS:{js_errs}, Net:{net_errs}, HTTP:{http_errs})"
            )
            print("-" * 100)


if __name__ == "__main__":
    target_report = resolve_report_file()
    find_all_statuses(target_report)
