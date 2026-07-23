# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.2...HEAD
[1.1.2]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/releases/tag/v1.0.0
