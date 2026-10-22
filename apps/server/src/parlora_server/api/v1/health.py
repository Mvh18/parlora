"""Liveness and readiness probes."""

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from parlora_server import __version__
from parlora_server.api.problems import ProblemError

# A readiness check answers True when its dependency is usable.
ReadinessCheck = Callable[[], Awaitable[bool]]

router = APIRouter(prefix="/health", tags=["health"])


class Liveness(BaseModel):
    status: Literal["ok"]
    version: str = Field(description="Version of the running server.")


class Readiness(BaseModel):
    status: Literal["ok"]
    checks: dict[str, str] = Field(
        description=(
            "State of each dependency, keyed by name. Today only `database`; "
            "clients must accept new keys and values."
        ),
        examples=[{"database": "ok"}],
    )


@router.get("/live", summary="Liveness: the process is up")
async def live() -> Liveness:
    return Liveness(status="ok", version=__version__)


@router.get(
    "/ready",
    summary="Readiness: every dependency is usable",
    responses={503: {"description": "A dependency is unavailable; `checks` says which."}},
)
async def ready(request: Request) -> Readiness:
    checks: Mapping[str, ReadinessCheck] = request.app.state.readiness_checks
    outcomes = await asyncio.gather(*(check() for check in checks.values()))
    results = {
        name: "ok" if passed else "unavailable"
        for name, passed in zip(checks, outcomes, strict=True)
    }
    if not all(outcomes):
        raise ProblemError(503, "A dependency is unavailable.", extensions={"checks": results})
    return Readiness(status="ok", checks=results)
