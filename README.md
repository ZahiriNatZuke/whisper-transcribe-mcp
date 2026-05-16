# whisper-transcribe-mcp

[![PyPI version](https://img.shields.io/pypi/v/whisper-transcribe-mcp)](https://pypi.org/project/whisper-transcribe-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

MCP server for audio transcription using **faster-whisper** (local, free, offline) or **OpenAI Whisper API** (cloud, requires API key). Works with Claude Desktop and Claude Code on macOS, Windows, and Linux.

---

## Prerequisites

### macOS

**Option A — uv (recommended):**
```bash
brew install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Option B — Python:**
Python 3.10+ is included in macOS 12.3+. You can also install it with `brew install python`.

---

### Windows

**Option A — uv (recommended):**
```powershell
winget install astral-sh.uv
```
Or download the installer from [astral.sh/uv](https://astral.sh/uv).

**Option B — Python:**
Download Python 3.10+ from [python.org](https://python.org). During installation, check **"Add Python to PATH"**.

> No need to install ffmpeg or any compiler — everything is bundled in the package.

---

### Linux

**Option A — uv (recommended):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Option B — Python:**
```bash
# Debian/Ubuntu
sudo apt install python3.12 python3.12-venv

# Fedora
sudo dnf install python3.12

# Arch
sudo pacman -S python
```

> No additional system dependencies required.

---

## Installation

### Option A — uvx (recommended, no permanent install)

`uvx` automatically downloads and installs the package in an isolated environment. Only requires `uv` to be installed.

```bash
# Local backend:
uvx "whisper-transcribe-mcp[local]"

# OpenAI backend:
uvx "whisper-transcribe-mcp[openai]"

# Both backends:
uvx "whisper-transcribe-mcp[all]"
```

### Option B — pip

```bash
# Local backend:
pip install "whisper-transcribe-mcp[local]"

# OpenAI backend:
pip install "whisper-transcribe-mcp[openai]"

# Both backends:
pip install "whisper-transcribe-mcp[all]"
```

---

## Use Cases

### Case 1 — Local backend only (free, works offline)

Uses `faster-whisper` to transcribe locally. The model is downloaded from HuggingFace on first use (~74MB for `base`) and cached.

**Install:**
```bash
pip install "whisper-transcribe-mcp[local]"
```

**Environment variables:**
```
WHISPER_MODEL=base   # or tiny, small, medium, large-v3
```

---

### Case 2 — OpenAI backend only (best accuracy, requires API key)

Uses OpenAI's `whisper-1` model. Requires an API key and internet connection. No local model downloads.

**Install:**
```bash
pip install "whisper-transcribe-mcp[openai]"
```

**Environment variables:**
```
OPENAI_API_KEY=sk-...
```

---

### Case 3 — Both backends (OpenAI if key present, local as fallback)

If `OPENAI_API_KEY` is set, OpenAI is used automatically. Otherwise falls back to local faster-whisper.

**Install:**
```bash
pip install "whisper-transcribe-mcp[all]"
```

---

## Configuration

### Claude Desktop

Config file location by operating system:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Add the entry inside `"mcpServers"`:

> **Windows note:** Claude Desktop runs in a restricted environment and may not have `uvx` in its PATH, and it may use a Python version (e.g. 3.14) for which `ctranslate2` (a dependency of `faster-whisper`) does not yet have prebuilt wheels. Two fixes are required:
> 1. Use the **full path** to `uvx.exe` instead of just `uvx`. Run `where.exe uvx` in PowerShell to find it (usually `C:\Users\<YourUser>\.local\bin\uvx.exe`).
> 2. Force Python 3.12 via the `--python 3.12` flag so that a compatible wheel is used.

**Case 1 — Local:**

macOS / Linux:
```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "uvx",
      "args": ["whisper-transcribe-mcp[local]"],
      "env": {
        "WHISPER_MODEL": "base"
      }
    }
  }
}
```

Windows:
```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "C:\\Users\\<YourUser>\\.local\\bin\\uvx.exe",
      "args": ["--python", "3.12", "whisper-transcribe-mcp[local]"],
      "env": {
        "WHISPER_MODEL": "base"
      }
    }
  }
}
```

**Case 2 — OpenAI:**

macOS / Linux:
```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "uvx",
      "args": ["whisper-transcribe-mcp[openai]"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

Windows:
```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "C:\\Users\\<YourUser>\\.local\\bin\\uvx.exe",
      "args": ["--python", "3.12", "whisper-transcribe-mcp[openai]"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

**Case 3 — Both (OpenAI takes priority if key is set):**

macOS / Linux:
```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "uvx",
      "args": ["whisper-transcribe-mcp[all]"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "WHISPER_MODEL": "base"
      }
    }
  }
}
```

Windows:
```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "C:\\Users\\<YourUser>\\.local\\bin\\uvx.exe",
      "args": ["--python", "3.12", "whisper-transcribe-mcp[all]"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "WHISPER_MODEL": "base"
      }
    }
  }
}
```

Restart Claude Desktop after editing the file.

---

### Claude Code

Works the same on macOS, Windows, and Linux. Requires `uv` installed.

Claude Code config file location:

| OS | Global | Per project |
|---|---|---|
| macOS / Linux | `~/.claude.json` | `.claude/settings.json` (project root) |
| Windows | `C:\Users\<user>\.claude.json` | `.claude\settings.json` (project root) |

The easiest way to add the server is via the Claude Code CLI, which updates the config file automatically:

```bash
# Case 1 — Local:
claude mcp add whisper-transcribe uvx -- "whisper-transcribe-mcp[local]"

# Case 2 — OpenAI:
claude mcp add whisper-transcribe uvx --env OPENAI_API_KEY=sk-... -- "whisper-transcribe-mcp[openai]"

# Case 3 — Both (OpenAI with local fallback):
claude mcp add whisper-transcribe uvx --env OPENAI_API_KEY=sk-... --env WHISPER_MODEL=base -- "whisper-transcribe-mcp[all]"
```

> **Windows + `[all]`:** Add `--python 3.12` before the package name to avoid `ctranslate2` wheel issues. Edit `~/.claude.json` directly and use `"args": ["--python", "3.12", "whisper-transcribe-mcp[all]"]`.

To add it globally (available in all projects), use `--scope user`:

```bash
claude mcp add --scope user whisper-transcribe uvx -- "whisper-transcribe-mcp[local]"
```

Or edit `~/.claude.json` directly and add inside `"mcpServers"`:

```json
{
  "mcpServers": {
    "whisper-transcribe": {
      "command": "uvx",
      "args": ["whisper-transcribe-mcp[local]"],
      "env": {
        "WHISPER_MODEL": "base"
      }
    }
  }
}
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `base` | Local model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `OPENAI_API_KEY` | — | If set, activates the OpenAI backend instead of local |

### Backend selection and fallback (`[all]` only)

When installed with `[all]`, the backend is chosen at startup:

- `OPENAI_API_KEY` **set** → OpenAI is used. If the API call fails at runtime (network error, invalid key, quota exceeded), the server automatically falls back to local `faster-whisper` and includes a `"fallback_reason"` field in the response.
- `OPENAI_API_KEY` **not set** → local `faster-whisper` is used directly, no fallback attempted.

---

## Available Tools

### `transcribe_file`
Transcribes an audio file by path (mp3, wav, m4a, ogg, flac, webm, etc.).

**Parameters:**
- `file_path` (required): Absolute path to the audio file
- `language` (optional): Language code (`es`, `en`, `fr`, etc.). Auto-detected if not provided.
- `model_size` (optional): Local model size. Ignored with the OpenAI backend.
- `post_process` (optional, default `false`): If `true`, passes the transcription through GPT-4.1 to fix spelling, grammar, and punctuation. Requires the `openai` package (`[openai]` or `[all]`).
- `post_process_prompt` (optional): Custom system prompt for GPT post-processing. Use it to provide domain-specific context, proper nouns, or product names that Whisper may have misspelled. Falls back to a generic correction prompt if not provided.

**Response (without post-processing):**
```json
{
  "text": "Full transcription...",
  "language": "en",
  "language_probability": 0.99,
  "segments": [
    { "start": 0.0, "end": 4.2, "text": "First segment..." }
  ],
  "backend": "local",
  "model": "base"
}
```

**Response (with `post_process: true`):**
```json
{
  "text": "Corrected transcription...",
  "raw_text": "Original transcription from Whisper...",
  "post_process_model": "gpt-4.1",
  "language": "en",
  "language_probability": 0.99,
  "segments": [...],
  "backend": "local",
  "model": "base"
}
```

If post-processing fails, `text` retains the original transcription and a `post_process_error` field is added.

---

### `transcribe_base64`
Transcribes audio provided as a base64-encoded string. Useful for programmatic integrations.

**Parameters:**
- `audio_base64` (required): Base64-encoded audio data
- `extension` (optional, default `mp3`): File extension (`mp3`, `wav`, `ogg`, etc.)
- `language` (optional): Language code
- `model_size` (optional): Local model size
- `post_process` (optional, default `false`): Same as in `transcribe_file`.
- `post_process_prompt` (optional): Same as in `transcribe_file`.

---

### `list_models`
Shows the active backend configuration, available local models, and the GPT model used for post-processing.

---

## Local Model Sizes

| Model | Size | Relative Speed | Notes |
|---|---|---|---|
| `tiny` | 39 MB | ~32x | Fastest, least accurate |
| `base` | 74 MB | ~16x | Good balance (default) |
| `small` | 244 MB | ~6x | Better accuracy |
| `medium` | 769 MB | ~2x | High accuracy |
| `large-v3` | 1.5 GB | ~1x | Best accuracy, slowest |

Models are downloaded automatically from HuggingFace on first use and cached locally.

---

## Troubleshooting

### MCP not loading in Claude Desktop on Windows

**Symptom:** The server fails to start with a dependency resolution error like:

```
ctranslate2>=4.6.1 has no wheels with a matching platform tag (e.g., `win32`)
hint: You require CPython 3.14 (`cp314`), but we only found wheels for `ctranslate2` with: `cp39`, `cp310`, `cp311`, `cp312`, `cp313`
```

**Cause:** Two issues combined:
1. Claude Desktop does not include the user's local `bin` in its PATH, so `uvx` must be referenced by full path.
2. Claude Desktop's `uvx` may pick a Python version (e.g. 3.14) for which `ctranslate2` — a native dependency of `faster-whisper` — does not yet have prebuilt wheels for Windows.

**Fix:** Use the full path to `uvx.exe` and force Python 3.12 explicitly:

```json
"whisper-transcribe": {
  "command": "C:\\Users\\<YourUser>\\.local\\bin\\uvx.exe",
  "args": ["--python", "3.12", "whisper-transcribe-mcp[local]"],
  "env": { "WHISPER_MODEL": "base" }
}
```

To find your exact `uvx.exe` path, run in PowerShell:
```powershell
where.exe uvx
```

---

## License

MIT — see [LICENSE](LICENSE)
