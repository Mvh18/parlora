"""Helpers shared by repository invariant tests."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def is_ignored(path: str) -> bool:
    """True when git would ignore `path` (whether or not it exists)."""
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", path],
        cwd=REPO_ROOT,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore failed for {path!r}")
    return result.returncode == 0
