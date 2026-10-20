## Summary

<!--
What changes and why, in a short paragraph. Mention the motivation, the
technical decision or the external constraint if the title does not make it
obvious. Breaking changes and dependencies on other PRs belong here too.
-->

**Main changes:**

1. **<Area>**: <what it does and why>

Closes #<!-- issue number -->
<!-- Part of #<epic> — when the issue is a sub-issue -->

## How to test

<!--
Minimum steps for a reviewer, derived from the issue's acceptance criteria:
1. `just setup` (first time) …
2. …
3. Check that …
-->

---

<!-- Optional sections — delete the ones that do not apply. -->

## Breaking changes

<!--
What breaks and what consumers (API clients, the web app, integrators) must
update. Must match the `BREAKING CHANGE:` footer.
-->

## Review guide

<!-- Where to start reading; design decisions worth knowing. -->

## Screenshots

| Before | After |
| ------ | ----- |
|        |       |

---

## Type of change

- [ ] feat — new user-facing capability
- [ ] fix — corrects incorrect behaviour
- [ ] perf — performance only
- [ ] refactor — no behaviour change
- [ ] docs
- [ ] test
- [ ] build — build system or dependencies
- [ ] ci — pipelines and workflows
- [ ] chore — everything else

## Deploy considerations

- [ ] Database migration (`alembic upgrade head`)
- [ ] New or changed environment variables (`.env.example` updated)
- [ ] Compose / Dockerfile changes (rebuild required)
- [ ] API contract changed (`contracts/openapi.json` and the web client regenerated)
- [ ] New model or runtime download required

## Checklist

- [ ] PR title follows Conventional Commits (it becomes the squash commit)
- [ ] Tests added or updated; coverage gates pass
- [ ] `just check` passes locally
- [ ] Self-review of the diff complete
- [ ] Docs updated (README, AGENTS.md, ADR) where behaviour or workflow changed
- [ ] No secrets, credentials, personal data, real voice recordings, model weights or local paths in the diff
- [ ] CLA signed (external contributors)
