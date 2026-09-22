# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.3] - 2026-09-22

### Security

- Require `fastmcp>=3.2.0` (fixes GHSA-vv7q-7jx5-f767, GHSA-rww4-4w9c-7733, GHSA-m8x7-r2rg-vh5g)
  and `mcp>=1.28.1` (fixes GHSA-vj7q-gjh5-988w, GHSA-jpw9-pfvf-9f58, GHSA-hvrp-rf83-w775).
- `transcribe_base64` only accepts known audio extensions, so the temp file can no longer be
  written outside the temp directory; the temp file is removed even if writing it fails.
- `model_size` and `language` are validated against allowlists before reaching the backend.
- OpenAI errors are returned as a short summary (type and HTTP status); details go to stderr.
- PyPI releases now include PEP 740 provenance attestations, and all GitHub Actions are pinned
  by commit SHA with Dependabot updates.

### Added

- `WHISPER_POST_PROCESS_MODEL` environment variable to choose the post-processing model.

### Fixed

- The development lockfile installs the `[local]` extra on Python 3.10 again (onnxruntime 1.24+
  has no CPython 3.10 wheels).
- Corrected the pinned `mcp-publisher` checksum and added a manual, idempotent release retry that
  skips the PyPI upload when the immutable version already exists.

## [1.1.2] - 2026-07-23

### Added

- Reproducible `uv` development environment, tests, Ruff checks, and pre-commit hooks.
- CI checks for the lockfile, lint, formatting, tests, release metadata, and secrets.
- Official MCP Registry metadata and OIDC-based publication after PyPI releases.
- Contributor documentation and GitHub issue/pull-request templates.

### Changed

- Releases are triggered by version tags and validate synchronized package/Registry metadata.

## [1.1.1] - 2026-05-16

### Fixed

- Hardened transcription behavior around invalid inputs and backend failures.

## [1.1.0] - 2026-05-16

### Added

- Optional GPT post-processing and fallback from the OpenAI backend to local transcription.

## [1.0.1] - 2026-05-15

### Fixed

- Corrected the Claude Code MCP scope flag in the documentation.

## [1.0.0] - 2026-05-15

### Added

- Stable cross-platform documentation and `uvx` installation workflow.

[Unreleased]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.3...HEAD
[1.1.3]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/releases/tag/v1.0.0
