"""Required root files exist and carry the expected content."""

import json
import re
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REQUIRED_FILES = [
    "LICENSE",
    "README.md",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    "pyproject.toml",
    ".python-version",
    "uv.lock",
    "package.json",
    "pnpm-workspace.yaml",
    "pnpm-lock.yaml",
    ".nvmrc",
    "justfile",
    ".pre-commit-config.yaml",
    ".devcontainer/Dockerfile",
    ".devcontainer/devcontainer.json",
    ".github/workflows/ci.yml",
]


@pytest.mark.parametrize("name", REQUIRED_FILES)
def test_required_file_exists(repo_root: Path, name: str) -> None:
    assert (repo_root / name).is_file(), f"missing {name}"


def test_license_is_polyform_noncommercial(repo_root: Path) -> None:
    text = (repo_root / "LICENSE").read_text(encoding="utf-8")
    assert "PolyForm Noncommercial License 1.0.0" in text
    assert re.search(r"^Required Notice: Copyright .+", text, re.MULTILINE)


def test_python_is_pinned_to_312(repo_root: Path) -> None:
    assert (repo_root / ".python-version").read_text(encoding="utf-8").strip() == "3.12"
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["requires-python"] == "==3.12.*"


def test_node_and_pnpm_are_pinned(repo_root: Path) -> None:
    assert (repo_root / ".nvmrc").read_text(encoding="utf-8").strip() == "24"
    package = json.loads((repo_root / "package.json").read_text(encoding="utf-8"))
    assert re.fullmatch(r"pnpm@\d+\.\d+\.\d+(\+sha\d+\.[0-9a-f]+)?", package["packageManager"])
    assert package["engines"]["node"].startswith(">=24")


def test_pytest_markers_are_strict(repo_root: Path) -> None:
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_cfg = pyproject["tool"]["pytest"]["ini_options"]
    assert "--strict-markers" in pytest_cfg["addopts"]
    declared = {m.split(":")[0] for m in pytest_cfg["markers"]}
    assert declared == {"unit", "integration", "contract", "gpu", "slow"}
