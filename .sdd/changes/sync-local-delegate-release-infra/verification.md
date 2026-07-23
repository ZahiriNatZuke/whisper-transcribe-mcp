# Verification: Align release and MCP registry infrastructure with local-delegate

## Environment

- Revision: `b34084e` plus the uncommitted change set (no commit requested).
- Relevant runtime and tool versions: CPython 3.10.20, uv lock with 113 packages, Ruff 0.16.0,
  pytest 9.1.1, gitleaks 8.30.1, official MCP schema 2025-12-11.

## Evidence

| Requirement | Check performed | Result | Evidence |
| --- | --- | --- | --- |
| REQ-001 | Parsed workflow YAML; ran lock, Ruff, format, pytest, pre-commit, and gitleaks locally | Pass | CI mirrors commands; 10 tests passed; no leaks |
| REQ-002 | `uv sync --locked --group dev`; `pre-commit run --all-files` | Pass | 86 packages checked; gitleaks/Ruff/format hooks passed |
| REQ-003 | Validator against live official JSON Schema; inspected wheel METADATA | Pass | Versions 1.1.1 aligned; `mcp-name` present in built metadata |
| REQ-004 | Workflow inspection, schema/tag validation, pinned publisher checksum and idempotency review | Pass with deferred E2E | No tag/upload performed; actual OIDC proof waits for next release |
| REQ-005 | `bash -n release.sh`; invalid-version execution; recovery/idempotency code review | Pass | Syntax valid and malformed version rejected before mutation |
| REQ-006 | Compared community/config inventory with `local-delegate` | Pass | Changelog, contribution/conduct docs, publishing guide, issue/PR templates added |
| REQ-007 | `uv run pytest -q` | Pass | 10 focused tests, no model downloads or API calls |

## Quality checks

- [x] Project-native tests pass.
- [x] Lint, formatting, metadata validation, shell syntax, and build checks pass.
- [x] Secret scanning passes (working files through pre-commit; history through redacted gitleaks).
- [x] No unrelated tracked changes are present; user-owned untracked `.codex/` and `AGENTS.md`
  were preserved.

## Deviations and residual risk

- GitHub OIDC exchanges, PyPI upload, Registry publication, and GitHub Release creation were not
  run because the approved scope explicitly excludes publishing a release. The workflow follows
  the current official Registry Actions flow and pins/checksums publisher v1.7.9.
- Workflow YAML was parsed locally, but only GitHub can validate runner-specific behavior and OIDC
  claims end to end. The existing `pypi` GitHub environment was confirmed through the GitHub API.
- Registry installation metadata cannot encode the project's mutually optional extras as a user
  choice. The README explicitly directs users to install `[local]`, `[openai]`, or `[all]`.
