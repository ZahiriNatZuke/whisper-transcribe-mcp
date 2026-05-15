# whisper-transcribe-mcp

MCP server for audio transcription using **faster-whisper** (local, free, offline) or **OpenAI Whisper API** (cloud, requires API key).

## Installation

### Option A — uvx (no install needed, recommended)

```bash
# Local backend (downloads model on first use):
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

# Both:
pip install "whisper-transcribe-mcp[all]"
```

## Configuration

### Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

**Local backend (default):**
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

**OpenAI backend:**
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

### Claude Code

```bash
claude mcp add whisper-transcribe uvx -- "whisper-transcribe-mcp[local]"
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `base` | Local model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `OPENAI_API_KEY` | — | If set, uses OpenAI Whisper API instead of local model |

## Tools

### `transcribe_file`
Transcribe an audio file by path (mp3, wav, m4a, ogg, flac, etc.).

### `transcribe_base64`
Transcribe audio provided as a base64-encoded string.

### `list_models`
Show available models and current backend configuration.

## Local Model Sizes

| Model | Size | Speed | Notes |
|---|---|---|---|
| tiny | 39M | ~32x | Fastest |
| base | 74M | ~16x | Good balance (default) |
| small | 244M | ~6x | Better accuracy |
| medium | 769M | ~2x | High accuracy |
| large-v3 | 1.5G | ~1x | Best accuracy |

Models are downloaded automatically from HuggingFace on first use and cached locally.

## License

MIT
