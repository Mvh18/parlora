"""Private artefacts and secrets must never be committed."""

import pytest

from tests.repo.helpers import is_ignored

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "path",
    [
        ".claude/x",
        "openspec/x",
        "ROADMAP.md",
        "CLAUDE.local.md",
        ".env",
        ".env.local",
        "apps/server/.env.production",
        "recordings/session.wav",
        "models/kokoro.onnx",
    ],
)
def test_private_paths_are_ignored(path: str) -> None:
    assert is_ignored(path), f"{path} must be git-ignored"


@pytest.mark.parametrize(
    "path",
    [
        ".env.example",
        "tests/fixtures/synthetic/hello.wav",
    ],
)
def test_allowed_paths_are_not_ignored(path: str) -> None:
    assert not is_ignored(path), f"{path} must not be git-ignored"
