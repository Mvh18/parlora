"""Errors are RFC 9457 problem documents without traces, settings or secrets."""

from collections.abc import Iterator

import pytest
from fastapi import APIRouter, Query
from fastapi.testclient import TestClient

from parlora_server.config import Settings
from parlora_server.main import create_app

pytestmark = pytest.mark.unit

PROBLEM_JSON = "application/problem+json"
PROBLEM_FIELDS = {"type", "title", "status", "detail", "instance", "request_id"}


@pytest.fixture
def faulty_client(settings: Settings) -> Iterator[TestClient]:
    """An app with extra routes that fail on purpose."""
    app = create_app(settings)
    router = APIRouter(prefix="/api/v1/_test")

    @router.get("/boom")
    def boom() -> None:
        raise RuntimeError("database password is hunter2")

    @router.get("/typed")
    def typed(count: int = Query(..., ge=1)) -> dict[str, int]:
        return {"count": count}

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


def assert_problem(response_json: dict[str, object], status: int, instance: str) -> None:
    assert response_json.keys() >= PROBLEM_FIELDS
    assert response_json["type"] == "about:blank"
    assert response_json["status"] == status
    assert response_json["instance"] == instance
    assert isinstance(response_json["title"], str)
    assert response_json["title"]


def test_unknown_route_is_a_404_problem(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM_JSON
    assert_problem(response.json(), 404, "/api/v1/does-not-exist")
    assert response.json()["title"] == "Not Found"


def test_wrong_method_is_a_405_problem(client: TestClient) -> None:
    response = client.post("/api/v1/health/live")

    assert response.status_code == 405
    assert response.headers["content-type"] == PROBLEM_JSON
    assert "GET" in response.headers["allow"]
    assert_problem(response.json(), 405, "/api/v1/health/live")


def test_invalid_input_is_a_422_problem_with_field_errors(faulty_client: TestClient) -> None:
    # A fixed request id: a generated one may itself contain "-5" (see the last assertion).
    response = faulty_client.get(
        "/api/v1/_test/typed", params={"count": "-5"}, headers={"X-Request-ID": "fixed-id"}
    )

    assert response.status_code == 422
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert_problem(body, 422, "/api/v1/_test/typed")
    assert body["errors"] == [
        {"loc": ["query", "count"], "msg": "Input should be greater than or equal to 1"}
    ]
    assert "-5" not in response.text, "rejected input is not echoed back"


def test_unhandled_exception_is_a_generic_500_problem(faulty_client: TestClient) -> None:
    response = faulty_client.get("/api/v1/_test/boom", headers={"X-Request-ID": "trace-me-1"})

    assert response.status_code == 500
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert_problem(body, 500, "/api/v1/_test/boom")
    assert body["request_id"] == "trace-me-1"
    assert response.headers["x-request-id"] == "trace-me-1"
    assert response.headers["x-content-type-options"] == "nosniff"
    for leak in ("hunter2", "RuntimeError", "Traceback", "File "):
        assert leak not in response.text
