"""The domain core stays a framework-free workspace member."""

import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_core_has_no_runtime_dependencies(repo_root: Path) -> None:
    pyproject = tomllib.loads(
        (repo_root / "packages/core/pyproject.toml").read_text(encoding="utf-8")
    )
    assert pyproject["project"]["name"] == "parlora-core"
    assert pyproject["project"]["dependencies"] == []


def test_core_is_typed(repo_root: Path) -> None:
    assert (repo_root / "packages/core/src/parlora_core/py.typed").is_file()


def test_core_is_a_locked_workspace_member(repo_root: Path) -> None:
    lock = tomllib.loads((repo_root / "uv.lock").read_text(encoding="utf-8"))
    assert "parlora-core" in lock["manifest"]["members"]
