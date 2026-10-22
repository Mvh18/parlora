"""The coverage gate enforces line and branch thresholds separately."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def report(tmp_path: Path, lines: tuple[int, int], branches: tuple[int, int]) -> Path:
    path = tmp_path / "coverage.json"
    totals = {
        "covered_lines": lines[0],
        "num_statements": lines[1],
        "covered_branches": branches[0],
        "num_branches": branches[1],
    }
    path.write_text(json.dumps({"totals": totals}), encoding="utf-8")
    return path


def gate(repo_root: Path, path: Path, threshold: str = "95") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "coverage_gate.py"),
            str(path),
            "--lines",
            threshold,
            "--branches",
            threshold,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_passes_when_both_metrics_meet_the_threshold(repo_root: Path, tmp_path: Path) -> None:
    result = gate(repo_root, report(tmp_path, lines=(95, 100), branches=(19, 20)))
    assert result.returncode == 0, result.stdout


def test_fails_on_branch_shortfall_even_with_full_lines(repo_root: Path, tmp_path: Path) -> None:
    result = gate(repo_root, report(tmp_path, lines=(100, 100), branches=(47, 50)))
    assert result.returncode == 1
    assert "branches 94.00% < 95%" in result.stdout


def test_fails_on_line_shortfall(repo_root: Path, tmp_path: Path) -> None:
    result = gate(repo_root, report(tmp_path, lines=(90, 100), branches=(10, 10)))
    assert result.returncode == 1
    assert "lines 90.00% < 95%" in result.stdout


def test_no_branches_counts_as_fully_covered(repo_root: Path, tmp_path: Path) -> None:
    result = gate(repo_root, report(tmp_path, lines=(10, 10), branches=(0, 0)))
    assert result.returncode == 0, result.stdout
