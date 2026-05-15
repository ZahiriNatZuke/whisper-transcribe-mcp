# whisper-transcribe-mcp

[![PyPI version](https://img.shields.io/pypi/v/whisper-transcribe-mcp)](https://pypi.org/project/whisper-transcribe-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

MCP server for audio transcription using **faster-whisper** (local, free, offline) or **OpenAI Whisper API** (cloud, requires API key). Works with Claude Desktop and Claude Code on macOS, Windows, and Linux.

---

## Requisitos previos

### macOS

**Opción A — uv (recomendado):**
```bash
brew install uv
# o
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Opción B — Python:**
Python 3.10+ ya viene en macOS 12.3+. También podés instalarlo con `brew install python`.

---

### Windows

**Opción A — uv (recomendado):**
```powershell
winget install astral-sh.uv
```
O descargá el installer desde [astral.sh/uv](https://astral.sh/uv).

**Opción B — Python:**
Descargá Python 3.10+ desde [python.org](https://python.org). Durante la instalación, marcá **"Add Python to PATH"**.

> No se necesita instalar ffmpeg ni compiladores adicionales — todo viene bundleado en el paquete.

---

### Linux

**Opción A — uv (recomendado):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Opción B — Python:**
```bash
# Debian/Ubuntu
sudo apt install python3.12 python3.12-venv

# Fedora
sudo dnf install python3.12

# Arch
sudo pacman -S python
```

> No se necesitan dependencias de sistema adicionales.

---

## Instalación

### Opción A — uvx (recomendada, sin instalar nada permanente)

`uvx` descarga e instala el paquete automáticamente en un entorno aislado cada vez que lo usás. Solo necesitás `uv` instalado.

```bash
# Backend local:
uvx "whisper-transcribe-mcp[local]"

# Backend OpenAI:
uvx "whisper-transcribe-mcp[openai]"

# Ambos backends:
uvx "whisper-transcribe-mcp[all]"
```

### Opción B — pip

```bash
# Backend local:
pip install "whisper-transcribe-mcp[local]"

# Backend OpenAI:
pip install "whisper-transcribe-mcp[openai]"

# Ambos backends:
pip install "whisper-transcribe-mcp[all]"
```

---

## Casos de uso

### Caso 1 — Solo backend local (gratis, funciona sin internet)

Usa `faster-whisper` para transcribir localmente. El modelo se descarga de HuggingFace la primera vez (~74MB para `base`) y queda cacheado.

**Instalación:**
```bash
pip install "whisper-transcribe-mcp[local]"
```

**Variables de entorno:**
```
WHISPER_MODEL=base   # o tiny, small, medium, large-v3
```

---

### Caso 2 — Solo backend OpenAI (mejor precisión, requiere API key)

Usa el modelo `whisper-1` de OpenAI. Requiere una API key y conexión a internet. No descarga modelos locales.

**Instalación:**
```bash
pip install "whisper-transcribe-mcp[openai]"
```

**Variables de entorno:**
```
OPENAI_API_KEY=sk-...
```

---

### Caso 3 — Ambos instalados (OpenAI si hay key, local como fallback)

Si `OPENAI_API_KEY` está presente en el entorno, usa OpenAI automáticamente. Si no, usa faster-whisper local.

**Instalación:**
```bash
pip install "whisper-transcribe-mcp[all]"
```

---

## Configuración

### Claude Desktop

La ruta del archivo de configuración según tu sistema operativo:

| OS | Ruta |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Agregá la entrada dentro de `"mcpServers"`:

**Caso 1 — Local:**
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

**Caso 2 — OpenAI:**
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

**Caso 3 — Ambos (OpenAI tiene prioridad si hay key):**
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

Reiniciá Claude Desktop después de editar el archivo.

---

### Claude Code

Funciona igual en macOS, Windows y Linux. Requiere `uv` instalado.

El archivo de configuración de Claude Code se ubica en:

| OS | Global | Por proyecto |
|---|---|---|
| macOS / Linux | `~/.claude.json` | `.claude/settings.json` (raíz del proyecto) |
| Windows | `C:\Users\<usuario>\.claude.json` | `.claude\settings.json` (raíz del proyecto) |

La forma más simple de agregar el servidor es con el CLI de Claude Code, que modifica ese archivo automáticamente:

```bash
# Caso 1 — Local:
claude mcp add whisper-transcribe uvx -- "whisper-transcribe-mcp[local]"

# Caso 2 — OpenAI:
claude mcp add whisper-transcribe uvx --env OPENAI_API_KEY=sk-... -- "whisper-transcribe-mcp[openai]"

# Caso 3 — Ambos:
claude mcp add whisper-transcribe uvx --env OPENAI_API_KEY=sk-... --env WHISPER_MODEL=base -- "whisper-transcribe-mcp[all]"
```

Para agregarlo globalmente (disponible en todos los proyectos), añadí el flag `--global`:

```bash
claude mcp add --global whisper-transcribe uvx -- "whisper-transcribe-mcp[local]"
```

O editá el archivo `~/.claude.json` directamente y agregá dentro de `"mcpServers"`:

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

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `WHISPER_MODEL` | `base` | Tamaño del modelo local: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `OPENAI_API_KEY` | — | Si está presente, activa el backend de OpenAI en lugar del local |

---

## Herramientas disponibles

### `transcribe_file`
Transcribe un archivo de audio por ruta (mp3, wav, m4a, ogg, flac, webm, etc.).

**Parámetros:**
- `file_path` (requerido): Ruta absoluta al archivo de audio
- `language` (opcional): Código de idioma (`es`, `en`, `fr`, etc.). Se autodetecta si no se indica.
- `model_size` (opcional): Tamaño del modelo local. Ignorado con el backend de OpenAI.

**Respuesta:**
```json
{
  "text": "Transcripción completa...",
  "language": "es",
  "language_probability": 0.99,
  "segments": [
    { "start": 0.0, "end": 4.2, "text": "Primer segmento..." }
  ],
  "backend": "local",
  "model": "base"
}
```

---

### `transcribe_base64`
Transcribe audio provisto como string en base64. Útil para integraciones programáticas.

**Parámetros:**
- `audio_base64` (requerido): Audio codificado en base64
- `extension` (opcional, default `mp3`): Extensión del archivo (`mp3`, `wav`, `ogg`, etc.)
- `language` (opcional): Código de idioma
- `model_size` (opcional): Tamaño del modelo local

---

### `list_models`
Muestra la configuración activa y los modelos locales disponibles.

---

## Modelos locales disponibles

| Modelo | Tamaño | Velocidad relativa | Notas |
|---|---|---|---|
| `tiny` | 39 MB | ~32x | Más rápido, menos preciso |
| `base` | 74 MB | ~16x | Buen balance (default) |
| `small` | 244 MB | ~6x | Mejor precisión |
| `medium` | 769 MB | ~2x | Alta precisión |
| `large-v3` | 1.5 GB | ~1x | Máxima precisión, más lento |

Los modelos se descargan automáticamente desde HuggingFace en el primer uso y quedan cacheados localmente.

---

## Licencia

MIT — ver [LICENSE](LICENSE)
