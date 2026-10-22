"""Fail when line or branch coverage falls below its threshold.

coverage.py's own `fail_under` checks a single blended percentage, which lets
full line coverage hide missing branches. This gate reads a JSON report
(`--cov-report=json:<path>`) and checks each metric on its own.

Usage: coverage_gate.py REPORT --lines 95 --branches 95
"""

import argparse
import json
import sys
from pathlib import Path


def percent(covered: int, total: int) -> float:
    return 100.0 if total == 0 else 100.0 * covered / total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path)
    parser.add_argument("--lines", type=float, required=True)
    parser.add_argument("--branches", type=float, required=True)
    args = parser.parse_args()

    totals = json.loads(args.report.read_text(encoding="utf-8"))["totals"]
    metrics = {
        "lines": (percent(totals["covered_lines"], totals["num_statements"]), args.lines),
        "branches": (percent(totals["covered_branches"], totals["num_branches"]), args.branches),
    }

    failed = False
    for name, (actual, threshold) in metrics.items():
        ok = actual >= threshold
        failed |= not ok
        print(
            f"{'ok  ' if ok else 'FAIL'} {name} {actual:.2f}% {'>=' if ok else '<'} {threshold:g}%"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
