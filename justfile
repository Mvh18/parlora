# Parlora task runner. Recipes are thin calls to uv, pnpm and docker so they
# behave the same in bash (Linux, Dev Container) and PowerShell (Windows).
# Anything non-trivial belongs in scripts/*.py, never in shell.

set shell := ["bash", "-euo", "pipefail", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# List the available recipes
default:
    @just --list --unsorted

# Install dependencies from the lockfiles (unchanged) and the git hooks
setup:
    uv sync --locked
    pnpm install --frozen-lockfile
    uv run pre-commit install --install-hooks

# Start the local stack and the web dev server
dev:
    @echo 'dev: not available yet - the Compose stack and the web app arrive with the local runtime and web shell work.'

# Start the Compose stack (PostgreSQL + server)
up:
    @echo 'up: not available yet - compose.yaml arrives with the local runtime work.'

# Stop the Compose stack
down:
    @echo 'down: not available yet - compose.yaml arrives with the local runtime work.'

# Format Python and everything Prettier handles
fmt:
    uv run ruff format .
    uv run ruff check --fix .
    pnpm exec prettier --write .

# Lint and check formatting without changing files
lint:
    uv run ruff check .
    uv run ruff format --check .
    pnpm exec prettier --check .

# Type-check Python (mypy --strict)
typecheck:
    uv run mypy

# Run every test suite
test: test-repo test-core test-server test-web

# Run the repository invariant tests
test-repo:
    uv run pytest tests/repo

# Run the domain core tests with its coverage gate
test-core:
    @echo 'test-core: nothing to run yet - packages/core arrives with the domain core work.'

# Run the server tests with its coverage gate
test-server:
    @echo 'test-server: nothing to run yet - apps/server arrives with the server API work.'

# Run the web unit tests with its coverage gate
test-web:
    @echo 'test-web: nothing to run yet - apps/web arrives with the web shell work.'

# Run the Playwright smoke tests
e2e:
    @echo 'e2e: nothing to run yet - the smoke tests arrive with the web shell work.'

# Export the OpenAPI contract to contracts/openapi.json
openapi:
    @echo 'openapi: not available yet - the API arrives with the server API work.'

# Generate the TypeScript API client from the OpenAPI contract
gen-client:
    @echo 'gen-client: not available yet - the client arrives with the web shell work.'

# Scan the working tree for secrets
security:
    uv run pre-commit run gitleaks --all-files

# Run every gate CI runs (except jobs that need GitHub)
check: lint typecheck test security
