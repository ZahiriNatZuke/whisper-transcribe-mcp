# Implementation plan: Align release and MCP registry infrastructure with local-delegate

## Approach

Adopt the sibling project's `uv`/Ruff/pytest/pre-commit conventions, add focused tests around the
existing single-module server, and use one tag-triggered workflow that publishes the underlying
PyPI artifact before its Registry metadata. Adapt every copied convention to this package rather
than copying backend-specific details.

## Ordered tasks

1. **Standardize the development environment**
   - Files or modules: `pyproject.toml`, `.python-version`, `uv.lock`, `.gitignore`
   - Requirements covered: REQ-002
   - Verification: `uv lock --check`, metadata/build inspection, Socket dependency scores
   - Rollback or recovery: remove dev-only group/config and regenerate the lockfile
2. **Add automated quality checks**
   - Files or modules: `tests/`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`
   - Requirements covered: REQ-001, REQ-002, REQ-007
   - Verification: Ruff check/format, pytest, pre-commit all-files, workflow syntax inspection
   - Rollback or recovery: checks are isolated configuration/tests and do not affect runtime
3. **Implement coordinated PyPI and MCP Registry release**
   - Files or modules: `server.json`, `.github/workflows/publish.yml`, `release.sh`, README marker
   - Requirements covered: REQ-003, REQ-004, REQ-005
   - Verification: JSON Schema validation, version consistency script, build metadata, shell syntax
   - Rollback or recovery: no tag or external publication occurs during implementation
4. **Document and expose project conventions**
   - Files or modules: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
     `docs/publishing.md`, GitHub issue/PR templates
   - Requirements covered: REQ-001, REQ-003, REQ-005, REQ-006
   - Verification: link/content review and build confirms README is packaged
   - Rollback or recovery: documentation-only files can be reverted independently

## Test strategy

- Unit: pytest with monkeypatch/fakes; no model download or network API call.
- Integration: build wheel/sdist and inspect metadata/contents; validate lockfile and descriptor.
- End-to-end or manual: dry-run release preconditions and inspect generated workflow commands;
  actual registry publication is deferred to the next real release.
- Security and secret scanning: pre-commit all files and CI gitleaks full-history job.

## Migration and compatibility

- No runtime dependency or API change. The release trigger changes from GitHub Release events to
  version tags; `release.sh` still creates a GitHub Release after pushing the tag. The next version
  must be configured as a PyPI Trusted Publisher for the existing `pypi` environment (already
  present in GitHub) and will establish the Registry entry.

## Plan review

- [x] Every requirement maps to at least one task and verification step.
- [x] Risky or destructive operations have safeguards and rollback.
- [x] Dependencies and configuration changes are explicit.
- [x] The plan does not include unrelated work.

Adversarial review: no blocking finding. The only external operation is future tag-triggered
publication; local verification cannot prove OIDC authorization, so documentation records the
one-time PyPI trusted-publisher prerequisite and the workflow fails closed on version mismatch.
