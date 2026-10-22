"""Request ids and security headers on every HTTP response (design D8).

A pure ASGI middleware rather than `BaseHTTPMiddleware`, so it adds no task
per request and leaves streaming responses (WebRTC signalling later) intact.
"""

import re
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}

# Inbound ids are echoed into headers and logs, so only short, plain tokens pass.
_VALID_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,128}", re.ASCII)


def response_headers(request_id: str) -> dict[str, str]:
    return {REQUEST_ID_HEADER: request_id, **SECURITY_HEADERS}


def request_id_of(request: Request) -> str | None:
    request_id = getattr(request.state, "request_id", None)
    return request_id if isinstance(request_id, str) else None


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        inbound = Headers(scope=scope).get(REQUEST_ID_HEADER, "")
        request_id = inbound if _VALID_REQUEST_ID.fullmatch(inbound) else str(uuid.uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in response_headers(request_id).items():
                    headers[name] = value
            await send(message)

        await self.app(scope, receive, send_with_headers)
