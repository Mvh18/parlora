# parlora-server

The Parlora server: a FastAPI application that exposes the versioned
`/api/v1` HTTP API in front of the domain core (`parlora-core`). It reports
liveness and readiness, serves the language and CEFR catalogues, and answers
every error with an RFC 9457 problem document. The OpenAPI contract is
exported to `contracts/openapi.json` with `just openapi`.
