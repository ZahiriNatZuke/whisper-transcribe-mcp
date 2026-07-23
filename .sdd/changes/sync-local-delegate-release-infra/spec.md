# Specification: Align release and MCP registry infrastructure with local-delegate

## Summary

Bring `whisper-transcribe-mcp` to feature parity with `local-delegate` for reproducible quality
checks, releases, official MCP Registry discovery, and contributor-facing documentation.

## Requirements

- **REQ-001:** Pushes to `main` and pull requests run lockfile validation, lint, formatting,
  unit tests, and secret scanning.
- **REQ-002:** Developers can install one dev environment and enable pre-commit hooks that run
  secret scanning, lint autofix, and formatting.
- **REQ-003:** The repository contains a valid official MCP Registry descriptor whose server and
  package versions match the project version and whose PyPI ownership marker is included in the
  package README.
- **REQ-004:** Pushing a semantic `vX.Y.Z` tag validates version alignment, builds and publishes
  idempotently to PyPI with Trusted Publishing, then publishes the same version to the official
  MCP Registry through GitHub OIDC without stored publishing credentials.
- **REQ-005:** The release helper and publishing documentation keep `pyproject.toml`, `uv.lock`,
  `server.json`, changelog, tag, and GitHub Release coordinated, and fail before mutation on an
  invalid version or unsuitable working tree.
- **REQ-006:** Contributor documentation and GitHub templates expose the same quality, security,
  changelog, and support expectations as the sibling project, adapted to Whisper backends.
- **REQ-007:** Focused tests cover backend selection helpers, input validation, fallback, base64
  cleanup/delegation, post-processing, and model metadata without requiring audio models or API
  calls.

## Acceptance scenarios

### Scenario: release path

- **Given** a clean `main` checkout whose manifest versions equal `X.Y.Z` and whose checks pass
- **When** tag `vX.Y.Z` is pushed
- **Then** the workflow publishes the package to PyPI and the matching descriptor to the MCP
  Registry using OIDC, with no repository publishing token.

### Scenario: pull request

- **Given** a proposed code or configuration change
- **When** a pull request is opened or updated
- **Then** lockfile, Ruff, pytest, and gitleaks checks report independently.

## Edge cases and failure behavior

- A tag that does not match both manifests fails before publishing.
- A rerun skips package files already present on PyPI.
- Registry publication waits/retries for PyPI metadata availability.
- Release preparation rejects malformed versions, a non-`main` branch, a dirty tracked working
  tree, or an existing tag.
- The next release, not the already-published 1.1.1 artifact, is the first automated Registry
  publication because ownership proof must already exist on PyPI.

## Non-functional requirements

- No secrets or personal configuration are committed; gitleaks checks full Git history in CI.
- Third-party publisher binary is version-pinned and checksum-verified.
- Runtime supports the existing Python >=3.10 contract and keeps backend extras optional.
- CI and local commands use the same locked dev environment.

## Non-goals

- No tag, GitHub Release, PyPI upload, or Registry publication is executed in this change.
- No transcription API behavior or dependency-extra redesign.
- No modifications to `local-delegate` or GitHub repository protection settings.

## Traceability

REQ-001 -> Tasks 2, 4; REQ-002 -> Tasks 1, 2; REQ-003 -> Tasks 3, 4; REQ-004 -> Task 3;
REQ-005 -> Tasks 3, 4; REQ-006 -> Task 4; REQ-007 -> Task 2.
