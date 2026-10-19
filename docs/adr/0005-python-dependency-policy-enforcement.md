# ADR 0005 — Python dependency policy enforcement

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** #9 (spike, time-boxed to two hours)

## Context

The repository security baseline must stop a pull request that adds a Python
dependency with a known vulnerability or a disallowed licence (ADR 0004:
no GPL or AGPL in the Parlora process; reviewed LGPL and MPL-2.0 allowed;
unknown licences fail). GitHub offers this through the dependency graph,
`actions/dependency-review-action` and Dependabot, but all three depend on
GitHub parsing `uv.lock`, and support for a uv workspace (`packages/core` and
`apps/server` sharing one lockfile) was not confirmed.

The spike had to decide which tool is the merge gate for Python dependencies
and which is advisory.

## Questions

1. Does the repository's dependency graph list packages from `uv.lock`, direct
   and transitive?
2. Does dependency review flag a known-vulnerable and a GPL-licensed Python
   package added in a test pull request?
3. Does Dependabot open version and security updates for the `uv` ecosystem in
   this workspace layout?
4. If any answer is no, do `pip-audit` (on an exported requirements file) and a
   licence report from the lockfile cover the gap?

## Setup

- Windows 11, uv 0.13.0, pip-audit 2.10.1, pip-licenses 5.5.5.
- Lockfile on `main` after #11: 71 third-party packages exported with
  `uv export --frozen --all-packages --all-groups --no-hashes --no-emit-workspace`.
- Test packages were added only through `uv run --with` or a scratch copy of
  the exported file; neither `uv.lock` nor `pyproject.toml` changed.

## Findings

### Questions 1–3 — not answered

The spike could not use authenticated GitHub access from the maintainer's
machine (no push, no `gh`), and the dependency-graph SBOM endpoint returns
`404` to anonymous requests. The maintainer chose to close the spike on the
local evidence instead of extending the timebox. GitHub's support for
`uv.lock` is therefore **unverified** for this repository.

### Question 4 — yes, both gaps are covered locally

**Vulnerabilities.** `pip-audit -r <exported> --disable-pip --no-deps` reports
no known vulnerabilities for the current lockfile (about 9 s, mostly tool
installation). With `jinja2==2.10` appended to a scratch copy it reports
four advisories (PYSEC-2019-217, PYSEC-2021-66, PYSEC-2026-1473,
PYSEC-2026-1474) and exits `1`, so it works as a CI gate. `--no-deps` is
correct here because the export already contains the full resolved set.

**Licences.** `pip-licenses` reads the metadata of the installed environment,
not `uv.lock`, so the check runs after `uv sync --frozen --all-packages
--all-groups`. With `--fail-on "General Public License;GPL" --partial-match`:

| Environment                      | Result                                  |
| -------------------------------- | --------------------------------------- |
| Current lockfile                 | exit `0`                                |
| Plus `phonemizer` 3.4.0 (GPLv3+) | exit `1`, names the package and licence |

Limitations observed:

- Partial matching on `GPL` also matches LGPL, so the reviewed LGPL packages
  from ADR 0004 (`soxr`, `num2words`) must be excluded explicitly with
  `--ignore-packages`, which keeps the exception list visible in one place.
- Licence strings come from free-form package metadata and are not
  normalised (`MIT`, `MIT License`, `BSD License`). Matching on substrings of
  the denied families is reliable; an allow-list of exact strings would not be.
- Packages with no licence metadata appear as `UNKNOWN` and must be denied
  explicitly.
- The installed set depends on the platform; CI checks the Linux set, which
  is the one shipped in the server image.

## Decision

1. **Gate (required, part of `ci-ok`):** a `python-deps` job in
   `security.yml` that
   - exports the lockfile and runs `pip-audit --disable-pip --no-deps`;
   - runs `uv sync --frozen --all-packages --all-groups`, then
     `pip-licenses --partial-match --fail-on "General Public License;GPL;UNKNOWN"
--ignore-packages soxr num2words` (the ignore list grows only with a
     reviewed, documented exception).
2. **Advisory (enabled, not trusted for Python):** GitHub's dependency graph,
   `dependency-review-action` and Dependabot for the `uv` ecosystem. They stay
   configured because they cost nothing and fully cover the npm, Docker and
   GitHub Actions ecosystems, and dependency review remains a required gate for
   those ecosystems. Their Python results are informational until verified.
3. **Name-based denials stay** in `.github/dependency-review-config.yml`
   (`phonemizer`, `phonemizer-fork`, `espeakng-loader`) as a second line of
   defence.
4. **Revisit:** when authenticated access is available, repeat questions 1–3
   (dependency graph SBOM, a dependency-graph compare between a test branch and
   `main`, a Dependabot run). If all pass, dependency review may become the
   Python gate and this ADR is superseded.

## Consequences

- The Python policy never depends on an unverified GitHub feature: a
  vulnerable or GPL package fails CI even if GitHub does not see it.
- Two tools in CI instead of one; the extra job takes well under a minute.
- The LGPL exception list lives in the workflow and must be kept in sync with
  ADR 0004 and `NOTICE`.
- Vulnerability data comes from the PyPI advisory database (pip-audit's
  default), which can differ from the GitHub Advisory Database used by
  Dependabot.

## Options ruled out

- **Dependency review as the only Python gate:** relies on `uv.lock` parsing
  that this spike could not confirm.
- **Licence check from `uv.lock` alone:** the lockfile has no licence data;
  reading it would need a network lookup per package.
- **Exact-string licence allow-list:** brittle against unnormalised metadata.
- **Extending the spike timebox:** rejected by the maintainer; the gate above
  is safe either way.
