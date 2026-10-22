"""The application is built by a factory, with no side effects at import time."""

import os
import subprocess
import sys

import pytest
from fastapi import FastAPI

from parlora_server.config import Settings
from parlora_server.main import create_app

pytestmark = pytest.mark.unit


def test_import_has_no_side_effects() -> None:
    # A fresh interpreter, so modules cached by other tests cannot hide an
    # import-time connection or a module-level app.
    probe = (
        "import socket, sys\n"
        "def deny(*args, **kwargs):\n"
        "    raise AssertionError('network access during import')\n"
        "socket.socket.connect = deny\n"
        "socket.create_connection = deny\n"
        "import parlora_server.main as main\n"
        "assert not hasattr(main, 'app'), 'module-level app found'\n"
    )
    result = subprocess.run(  # noqa: S603 - fixed interpreter and script
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PARLORA_DATABASE__URL": "not a url"},
    )
    assert result.returncode == 0, result.stderr


def test_factory_builds_independent_apps(settings: Settings) -> None:
    first, second = create_app(settings), create_app(settings)

    assert isinstance(first, FastAPI)
    assert first is not second
    assert first.state.settings is settings


def test_openapi_metadata(settings: Settings) -> None:
    from parlora_server import __version__

    app = create_app(settings)

    assert app.title == "Parlora API"
    assert app.version == __version__
    assert app.openapi_url == "/api/v1/openapi.json"
    assert app.docs_url == "/api/v1/docs"
    assert app.redoc_url is None
