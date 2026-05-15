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

**Case 1 — Local:**
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

**Case 2 — OpenAI:**
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

**Case 3 — Both (OpenAI takes priority if key is set):**
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

# Case 3 — Both:
claude mcp add whisper-transcribe uvx --env OPENAI_API_KEY=sk-... --env WHISPER_MODEL=base -- "whisper-transcribe-mcp[all]"
```

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

---

## Available Tools

### `transcribe_file`
Transcribes an audio file by path (mp3, wav, m4a, ogg, flac, webm, etc.).

**Parameters:**
- `file_path` (required): Absolute path to the audio file
- `language` (optional): Language code (`es`, `en`, `fr`, etc.). Auto-detected if not provided.
- `model_size` (optional): Local model size. Ignored with the OpenAI backend.

**Response:**
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

---

### `transcribe_base64`
Transcribes audio provided as a base64-encoded string. Useful for programmatic integrations.

**Parameters:**
- `audio_base64` (required): Base64-encoded audio data
- `extension` (optional, default `mp3`): File extension (`mp3`, `wav`, `ogg`, etc.)
- `language` (optional): Language code
- `model_size` (optional): Local model size

---

### `list_models`
Shows the active backend configuration and available local models.

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

## License

MIT — see [LICENSE](LICENSE)
