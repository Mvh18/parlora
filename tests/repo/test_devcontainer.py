"""The Dev Container runs the same runtimes the project pins."""

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def base_image_version(repo_root: Path, image: str) -> str:
    dockerfile = (repo_root / ".devcontainer" / "Dockerfile").read_text(encoding="utf-8")
    match = re.search(rf"^FROM {image}:([\d.]+)-", dockerfile, re.MULTILINE)
    assert match, f"no pinned {image} base image in .devcontainer/Dockerfile"
    return match.group(1)


def test_python_base_image_matches_python_version(repo_root: Path) -> None:
    pinned = (repo_root / ".python-version").read_text(encoding="utf-8").strip()
    version = base_image_version(repo_root, "python")
    assert version.startswith(f"{pinned}."), f"python {version} does not match {pinned}"


def test_node_base_image_matches_nvmrc(repo_root: Path) -> None:
    pinned = (repo_root / ".nvmrc").read_text(encoding="utf-8").strip()
    version = base_image_version(repo_root, "node")
    assert version.split(".")[0] == pinned, f"node {version} does not match {pinned}"


def test_dependabot_does_not_propose_other_runtime_lines(repo_root: Path) -> None:
    """Python and Node move by an explicit decision, not by a Dependabot PR."""
    config = yaml.safe_load((repo_root / ".github" / "dependabot.yml").read_text("utf-8"))
    docker = next(u for u in config["updates"] if u["package-ecosystem"] == "docker")
    ignored = {rule["dependency-name"]: set(rule["update-types"]) for rule in docker["ignore"]}
    assert ignored["python"] >= {"version-update:semver-major", "version-update:semver-minor"}
    assert ignored["node"] >= {"version-update:semver-major"}
