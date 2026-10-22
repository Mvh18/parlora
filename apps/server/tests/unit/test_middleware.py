"""Request ids, security headers and the CORS allow-list (design D8, D19)."""

import uuid
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from parlora_server.config import Settings
from parlora_server.main import create_app

pytestmark = pytest.mark.unit


def test_generates_a_request_id_when_none_is_sent(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")

    assert uuid.UUID(response.headers["x-request-id"])


def test_echoes_a_valid_inbound_request_id(client: TestClient) -> None:
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": "web-42.abc_DEF"})

    assert response.headers["x-request-id"] == "web-42.abc_DEF"


@pytest.mark.parametrize(
    "inbound",
    ["a" * 500, "abc\tdef", "abc def", "id;drop", "ñandú".encode(), ""],
)
def test_replaces_an_invalid_inbound_request_id(client: TestClient, inbound: str | bytes) -> None:
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": inbound})

    assert uuid.UUID(response.headers["x-request-id"])


def test_request_id_is_also_set_on_error_problems(client: TestClient) -> None:
    response = client.get("/api/v1/nope", headers={"X-Request-ID": "err-1"})

    assert response.headers["x-request-id"] == "err-1"
    assert response.json()["request_id"] == "err-1"


def test_security_headers_on_every_response(client: TestClient) -> None:
    for path in ("/api/v1/health/live", "/api/v1/nope"):
        response = client.get(path)
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["referrer-policy"] == "no-referrer"


def preflight(client: TestClient, origin: str) -> dict[str, str]:
    response = client.options(
        "/api/v1/languages",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )
    return dict(response.headers)


def test_disallowed_origin_gets_no_cors_header(client: TestClient) -> None:
    headers = preflight(client, "https://evil.example")

    assert "access-control-allow-origin" not in headers


def test_allowed_integrator_origin_is_echoed(make_settings: Callable[..., Settings]) -> None:
    app = create_app(make_settings(cors_origins=["http://localhost:8000"]))

    with TestClient(app) as client:
        headers = preflight(client, "http://localhost:8000")
        actual = client.get("/api/v1/languages", headers={"Origin": "http://localhost:8000"})

    assert headers["access-control-allow-origin"] == "http://localhost:8000"
    assert actual.headers["access-control-allow-origin"] == "http://localhost:8000"
    # Browsers may read the request id, to quote it when reporting an error.
    assert "x-request-id" in actual.headers["access-control-expose-headers"].lower()
