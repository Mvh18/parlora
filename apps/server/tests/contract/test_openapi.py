"""The committed OpenAPI contract matches the code and stays versioned (design D8)."""

import difflib
import json
from pathlib import Path
from typing import Any

import pytest

from parlora_server import __version__
from parlora_server.contract import render_openapi

pytestmark = pytest.mark.contract

CONTRACT = Path(__file__).resolve().parents[4] / "contracts" / "openapi.json"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


@pytest.fixture(scope="module")
def generated() -> str:
    return render_openapi()


@pytest.fixture(scope="module")
def document(generated: str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(generated)
    return loaded


def operations(document: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    return [
        (path, method, operation)
        for path, item in document["paths"].items()
        for method, operation in item.items()
        if method in HTTP_METHODS
    ]


def test_committed_contract_matches_the_code(generated: str) -> None:
    committed = CONTRACT.read_text(encoding="utf-8")
    if committed != generated:
        diff = "".join(
            difflib.unified_diff(
                committed.splitlines(keepends=True),
                generated.splitlines(keepends=True),
                fromfile="committed",
                tofile="generated",
            )
        )
        pytest.fail(f"contracts/openapi.json is out of date; run `just openapi`.\n{diff}")


def test_every_path_is_versioned(document: dict[str, Any]) -> None:
    unversioned = [path for path in document["paths"] if not path.startswith("/api/v1/")]
    assert document["paths"]
    assert not unversioned


def test_info_version_is_the_package_version(document: dict[str, Any]) -> None:
    assert document["info"]["version"] == __version__


def test_operation_ids_are_unique_and_readable(document: dict[str, Any]) -> None:
    ids = [operation["operationId"] for _, _, operation in operations(document)]
    assert len(ids) == len(set(ids))
    assert "health_live" in ids
    assert all(identifier.replace("_", "").isalnum() for identifier in ids)


def test_errors_are_documented_as_problem_documents(document: dict[str, Any]) -> None:
    problem = {"$ref": "#/components/schemas/Problem"}
    for path, method, operation in operations(document):
        for status, response in operation["responses"].items():
            if not status.startswith("2"):
                content = response["content"]
                assert content == {"application/problem+json": {"schema": problem}}, (
                    f"{method.upper()} {path} {status}"
                )
        assert "default" in operation["responses"], f"{method.upper()} {path}"


def test_readiness_documents_its_503(document: dict[str, Any]) -> None:
    assert "503" in document["paths"]["/api/v1/health/ready"]["get"]["responses"]
