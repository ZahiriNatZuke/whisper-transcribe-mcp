#!/usr/bin/env python3
"""Whisper MCP server — local faster-whisper or OpenAI Whisper API backend."""

import os
import tempfile
import base64
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("whisper-transcribe")

DEFAULT_MODEL = os.environ.get("WHISPER_MODEL", "base")
_USE_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))

_local_model = None


def _get_local_model(model_size: str):
    from faster_whisper import WhisperModel
    global _local_model
    if _local_model is None or _local_model.model_size_or_path != model_size:
        _local_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _local_model


def _transcribe_local(path: str, language: str | None, model_size: str) -> dict:
    model = _get_local_model(model_size)
    segments, info = model.transcribe(str(path), language=language, beam_size=5)
    segment_list = [
        {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
        for s in segments
    ]
    return {
        "text": " ".join(s["text"] for s in segment_list),
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "segments": segment_list,
        "backend": "local",
        "model": model_size,
    }


def _transcribe_openai(path: str, language: str | None) -> dict:
    from openai import OpenAI
    client = OpenAI()
    with open(path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language=language,
            response_format="verbose_json",
        )
    segments = result.segments or []
    return {
        "text": result.text,
        "language": result.language,
        "language_probability": 1.0,
        "segments": [
            {"start": s.start, "end": s.end, "text": s.text}
            for s in segments
        ],
        "backend": "openai",
        "model": "whisper-1",
    }


@mcp.tool()
def transcribe_file(
    file_path: str,
    language: str | None = None,
    model_size: str | None = None,
) -> dict:
    """Transcribe an audio file to text.

    Args:
        file_path: Absolute path to the audio file (mp3, wav, m4a, ogg, flac, etc.)
        language: Language code (e.g. 'es', 'en', 'fr'). Auto-detected if not provided.
        model_size: Local model size: tiny, base, small, medium, large-v3.
                    Ignored when using the OpenAI backend.
                    Defaults to WHISPER_MODEL env var (currently: {DEFAULT_MODEL}).

    Returns:
        dict with 'text', 'language', 'segments', 'backend', and 'model'.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    if _USE_OPENAI:
        return _transcribe_openai(str(path), language)
    return _transcribe_local(str(path), language, model_size or DEFAULT_MODEL)


@mcp.tool()
def transcribe_base64(
    audio_base64: str,
    extension: str = "mp3",
    language: str | None = None,
    model_size: str | None = None,
) -> dict:
    """Transcribe audio provided as a base64-encoded string.

    Args:
        audio_base64: Base64-encoded audio data.
        extension: File extension for the temp file (mp3, wav, m4a, ogg, etc.).
        language: Language code. Auto-detected if not provided.
        model_size: Local model size. Ignored when using the OpenAI backend.

    Returns:
        dict with 'text', 'language', 'segments', 'backend', and 'model'.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        return {"error": f"Invalid base64 data: {e}"}

    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        return transcribe_file(tmp_path, language=language, model_size=model_size)
    finally:
        os.unlink(tmp_path)


@mcp.tool()
def list_models() -> dict:
    """List available Whisper model sizes and current configuration."""
    return {
        "active_backend": "openai" if _USE_OPENAI else "local",
        "default_local_model": DEFAULT_MODEL,
        "current_loaded_model": _local_model.model_size_or_path if _local_model else None,
        "local_models": [
            {"name": "tiny",     "params": "39M",  "speed": "~32x", "note": "Fastest, least accurate"},
            {"name": "base",     "params": "74M",  "speed": "~16x", "note": "Good balance"},
            {"name": "small",    "params": "244M", "speed": "~6x",  "note": "Better accuracy"},
            {"name": "medium",   "params": "769M", "speed": "~2x",  "note": "High accuracy"},
            {"name": "large-v3", "params": "1.5G", "speed": "~1x",  "note": "Best accuracy, slowest"},
        ],
        "openai_model": "whisper-1 (set OPENAI_API_KEY to activate)",
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
