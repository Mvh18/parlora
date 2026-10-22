"""The server is a typed workspace member whose settings are all documented."""

import os
import re
import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel

from parlora_server.config import ENV_PREFIX, NESTED_DELIMITER, Settings, load_settings

pytestmark = pytest.mark.unit

DOCUMENTED = re.compile(r"^(?P<name>PARLORA_[A-Z0-9_]+)=", re.MULTILINE)


def env_vars(model: type[BaseModel], prefix: str = ENV_PREFIX) -> set[str]:
    """Every environment variable a settings model reads, nested groups included."""
    names: set[str] = set()
    for field_name, field in model.model_fields.items():
        name = prefix + field_name.upper()
        annotation = field.annotation
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            names |= env_vars(annotation, name + NESTED_DELIMITER)
        else:
            names.add(name)
    return names


def documented(repo_root: Path) -> set[str]:
    text = (repo_root / ".env.example").read_text(encoding="utf-8")
    return {match["name"] for match in DOCUMENTED.finditer(text)}


def test_every_setting_is_documented_in_env_example(repo_root: Path) -> None:
    missing = env_vars(Settings) - documented(repo_root)
    assert not missing, f".env.example lacks {sorted(missing)}"


def test_env_example_documents_no_unknown_server_setting(repo_root: Path) -> None:
    # Compose-only variables (host ports, local runtime work) will need an allow-list here.
    unknown = documented(repo_root) - env_vars(Settings)
    assert not unknown, f".env.example documents unknown settings {sorted(unknown)}"


def test_env_example_shows_the_defaults(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.upper().startswith(ENV_PREFIX):
            monkeypatch.delenv(name)

    from_example = load_settings(env_file=repo_root / ".env.example")

    assert from_example == Settings(_env_file=None)


def test_server_is_typed(repo_root: Path) -> None:
    assert (repo_root / "apps/server/src/parlora_server/py.typed").is_file()


def test_server_is_a_locked_workspace_member(repo_root: Path) -> None:
    lock = tomllib.loads((repo_root / "uv.lock").read_text(encoding="utf-8"))
    assert "parlora-server" in lock["manifest"]["members"]


def test_alembic_has_a_single_baseline(repo_root: Path) -> None:
    versions = sorted((repo_root / "apps/server/alembic/versions").glob("*.py"))
    assert [path.name for path in versions] == ["0001_baseline.py"]
