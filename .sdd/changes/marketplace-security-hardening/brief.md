# Brief (lightweight): Marketplace security findings hardening

## Problem

mcp-marketplace.io rated v1.1.2 at 4.2/10: 3 fastmcp advisories (critical/high/medium, reachable
through the `fastmcp>=3.0` floor), raw OpenAI error messages, broad exception handling, temp-file
cleanup, and unvalidated `language`/`model_size`. PyPI releases had OIDC but no provenance.

## Changes

- REQ-1 Dependency floors: `fastmcp>=3.2.0`, `mcp>=1.28.1` (all GHSA fixed versions).
- REQ-2 `extension` allowlist (blocked temp-path escape) and `mkstemp` + `unlink(missing_ok)`.
- REQ-3 `model_size` / `language` allowlists; `file_path` must be a regular file.
- REQ-4 OpenAI errors summarized (type + HTTP status), raw text to stderr; narrower excepts.
- REQ-5 `WHISPER_POST_PROCESS_MODEL` env var (default `gpt-5.4-nano`).
- REQ-6 Publish via `pypa/gh-action-pypi-publish` with PEP 740 attestations; actions pinned by
  SHA; Dependabot for actions; `pypi` environment limited to `v*` tags and `main`.
- REQ-7 Lockfile constraint so `[local]` installs on Python 3.10 (onnxruntime<1.24).

## Verification

Ruff lint/format, 16 pytest tests (6 new), Registry schema validation, `bash -n release.sh`,
`uv build`, end-to-end local transcription with `tiny`, fastmcp 4.0.5 import smoke test,
Socket depscore for every new/changed dependency (all >= 0.7).

## Out of scope

Marketplace re-scan cadence is controlled by mcp-marketplace.io.
