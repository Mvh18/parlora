"""Fixtures shared by the server's unit, integration and contract suites."""

import os
from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient

from parlora_server.config import Settings
from parlora_server.main import create_app

# A database URL nothing listens on: unit tests never reach PostgreSQL.
UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://parlora:parlora@127.0.0.1:1/parlora"


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Drop every PARLORA_ variable so the developer's environment cannot leak in."""
    for name in os.environ:
        if name.upper().startswith("PARLORA_"):
            monkeypatch.delenv(name)


@pytest.fixture
def make_settings(clean_env: None) -> Callable[..., Settings]:
    def make(**overrides: object) -> Settings:
        values: dict[str, object] = {"database": {"url": UNREACHABLE_DATABASE_URL}}
        values.update(overrides)
        return Settings(_env_file=None, **values)  # type: ignore[arg-type]

    return make


@pytest.fixture
def settings(make_settings: Callable[..., Settings]) -> Settings:
    return make_settings()


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    # Server errors become 500 responses, as they do behind uvicorn.
    with TestClient(create_app(settings), raise_server_exceptions=False) as test_client:
        yield test_client
