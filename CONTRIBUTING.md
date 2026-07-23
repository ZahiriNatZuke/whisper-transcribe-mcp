# Contributing to whisper-transcribe-mcp

Thanks for helping improve the project. It is a Python MCP server managed with
[`uv`](https://docs.astral.sh/uv/).

## Development environment

```bash
uv sync --group dev
uv run pytest -q
uv run ruff check .
uv run ruff format .
```

Python 3.10 or newer is supported. Tests must not download Whisper models or call paid APIs;
mock backend boundaries instead.

## Run the server locally

Install the backend you need, then start the entry point:

```bash
uv sync --extra local       # or: --extra openai / --extra all
uv run whisper-transcribe-mcp
```

## Project rules

- Keep `faster-whisper` and `openai` optional; the base package must still start and return clear
  missing-extra errors.
- Never commit API keys, personal MCP configurations, audio containing private data, or generated
  model files. Gitleaks runs in pre-commit and CI.
- Update `CHANGELOG.md` under `Unreleased` for user-visible changes.
- Keep `pyproject.toml` and `server.json` versions aligned for releases.

## Pull requests

1. Create a branch from `main`.
2. Run `uv lock --check`, Ruff, formatting, and pytest.
3. Update documentation and the changelog when behavior changes.
4. Explain the change and its verification in the pull request.

## Pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

The hooks scan for secrets, apply Ruff fixes, and format Python files.
