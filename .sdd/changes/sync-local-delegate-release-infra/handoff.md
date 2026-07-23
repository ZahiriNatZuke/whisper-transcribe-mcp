# Handoff: Align release and MCP registry infrastructure with local-delegate

## Current state

- SDD status: ready to close after quality/conformance/memory gates.
- Last completed gate: plan (quality and conformance evidence prepared).
- Current revision: `b34084e` plus uncommitted implementation; no commit requested.

## What changed

- Added reproducible `uv` development, tests, Ruff/pre-commit/gitleaks CI, official Registry
  metadata, coordinated PyPI/Registry tag publishing, hardened release preparation, changelog,
  contributor/community files, and publishing documentation.

## Decisions

- Registry namespace is `io.github.ZahiriNatZuke/whisper-transcribe-mcp` and PyPI verification is
  anchored by the exact README marker.
- The next package release is the first eligible Registry publication; 1.1.1 is immutable and
  lacks that marker on PyPI.
- `mcp-publisher` is pinned to v1.7.9 with the official linux-amd64 SHA-256; update both together.
- Keep runtime backend dependencies optional; Registry users choose an extra from the README.

## Next action

- Review/commit this change. For the next release, prepare the changelog section and run
  `./release.sh X.Y.Z`, then verify PyPI and Registry workflow output.

## Memory

- Canonical note: not created; project documentation and SDD artifacts are sufficient, and the
  user did not explicitly authorize persistent memory writes.
- Indexes updated: none.
