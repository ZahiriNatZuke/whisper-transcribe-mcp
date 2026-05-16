# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`whisper-transcribe-mcp` is a Python MCP (Model Context Protocol) server that exposes audio transcription tools using either **faster-whisper** (local, offline) or the **OpenAI Whisper API** (cloud). Published on PyPI and consumed via `uvx` or `pip`.

## Development Setup

```bash
# Install with all optional backends (recommended for development)
pip install -e ".[all]"

# Or with uv
uv pip install -e ".[all]"
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
python -m build

# Release a new version (bumps version in pyproject.toml, commits, pushes, creates GitHub release)
# PyPI publish is triggered automatically via GitHub Actions on release
./release.sh 1.2.3
```

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
- **OIDC trusted publisher**: PyPI publish uses `pypa/gh-action-pypi-publish` with OIDC (`id-token: write`), so no PyPI token secrets are needed in the repo.
- The `model_size` parameter in tools is silently ignored when `OPENAI_API_KEY` is set.
