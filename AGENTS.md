# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`whisper-transcribe-mcp` is a Python MCP (Model Context Protocol) server that exposes audio transcription tools using either **faster-whisper** (local, offline) or the **OpenAI Whisper API** (cloud). Published on PyPI and consumed via `uvx` or `pip`.

## Development Setup

```bash
# Install the locked development environment with all optional backends
uv sync --group dev --extra all

# Run the same checks as CI
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

## Running the Server Locally

```bash
# Local backend
WHISPER_MODEL=base python -m whisper_transcribe.server

# OpenAI backend
OPENAI_API_KEY=sk-... python -m whisper_transcribe.server
```

## Building and Publishing

```bash
# Build the package
uv build

# Release a new version from a clean main branch. This synchronizes pyproject.toml,
# uv.lock, and server.json, waits for CI, tags the release, and creates the GitHub release.
./release.sh 1.2.3
```

Pushing the version tag triggers `.github/workflows/publish.yml`, which publishes first to PyPI
and then to the official MCP Registry using OIDC. See `docs/publishing.md` for the full checklist.

## Architecture

The entire server lives in a single file: `whisper_transcribe/server.py`.

- Built on **FastMCP** (`fastmcp>=3.0`), which handles MCP protocol, tool registration, and stdio transport.
- Backend selection is determined at startup by the presence of `OPENAI_API_KEY` — there is no runtime switching.
- The local `WhisperModel` is lazily loaded and cached in `_local_model` (module-level global), and reloaded only if the requested `model_size` changes.
- `transcribe_base64` delegates to `transcribe_file` after writing a temp file, then cleans it up.

### Optional dependency groups (`pyproject.toml`)

| Extra | Installs | Enables |
|---|---|---|
| `[local]` | `faster-whisper` | Local CPU inference |
| `[openai]` | `openai` | OpenAI Whisper API |
| `[all]` | both | Auto-selects based on env |

Missing extras produce a descriptive `{"error": "..."}` dict — not exceptions — so the MCP caller always gets a JSON response.

## Key Design Decisions

- **No ffmpeg requirement**: `faster-whisper` bundles what it needs; this is explicitly called out in the README for Windows/Linux users.
- **OIDC trusted publishing**: `uv publish` uploads to PyPI, then `mcp-publisher` registers the
  matching `server.json`; both use GitHub OIDC, so no publishing tokens are stored in the repo.
- **Synchronized release metadata**: `pyproject.toml`, `uv.lock`, and both versions in
  `server.json` must match the semantic version tag.
- The `model_size` parameter in tools is silently ignored when `OPENAI_API_KEY` is set.
