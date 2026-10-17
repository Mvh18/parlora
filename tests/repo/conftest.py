"""Fixtures for repository invariant tests."""

from pathlib import Path

import pytest

from tests.repo.helpers import REPO_ROOT


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT
