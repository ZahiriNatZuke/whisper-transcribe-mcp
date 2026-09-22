#!/usr/bin/env python3
"""Whisper MCP server — local faster-whisper or OpenAI Whisper API backend."""

import base64
import os
import re
import sys
import tempfile
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("whisper-transcribe")

DEFAULT_MODEL = os.environ.get("WHISPER_MODEL", "base")
_USE_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))

_local_model = None

GPT_MODEL = os.environ.get("WHISPER_POST_PROCESS_MODEL", "gpt-5.4-nano")

LOCAL_MODELS = (
    "tiny",
    "tiny.en",
    "base",
    "base.en",
    "small",
    "small.en",
    "medium",
    "medium.en",
    "large-v1",
    "large-v2",
    "large-v3",
    "large-v3-turbo",
    "turbo",
    "distil-small.en",
    "distil-medium.en",
    "distil-large-v2",
    "distil-large-v3",
)
AUDIO_EXTENSIONS = ("mp3", "wav", "m4a", "ogg", "oga", "flac", "webm", "mp4", "mpeg", "mpga", "aac")
_LANGUAGE_RE = re.compile(r"^[a-z]{2,3}$")

DEFAULT_POST_PROCESS_PROMPT = (
    "You are a transcription correction assistant. "
    "Fix spelling errors, grammar, and punctuation in the transcribed text. "
    "Preserve the original meaning, tone, and language. "
    "Do not add, remove, or summarize content. "
    "Return only the corrected text, no explanations."
)


def _validate_options(language: str | None, model_size: str | None) -> dict | None:
    if language is not None and not _LANGUAGE_RE.fullmatch(language):
        return {"error": f"Invalid language code: {language!r}. Use an ISO 639-1 code like 'es'."}
    if model_size is not None and model_size not in LOCAL_MODELS:
        return {"error": f"Unknown model_size: {model_size!r}. Valid: {', '.join(LOCAL_MODELS)}"}
    return None


def _openai_error_message(exc: Exception) -> str:
    """Summarize an OpenAI error without echoing the raw API response."""
    print(f"[whisper-transcribe] OpenAI error: {exc!r}", file=sys.stderr)
    status = getattr(exc, "status_code", None)
    suffix = f" (HTTP {status})" if status else ""
    return f"OpenAI request failed: {type(exc).__name__}{suffix}"


def _get_local_model(model_size: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, {
            "error": "faster-whisper not installed. Run: pip install 'whisper-transcribe-mcp[local]'"
        }

    global _local_model
    if _local_model is None or _local_model.model_size_or_path != model_size:
        _local_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _local_model, None


def _transcribe_local(path: str, language: str | None, model_size: str) -> dict:
    model, err = _get_local_model(model_size)
    if err:
        return err

    try:
        from av.error import FFmpegError
    except ImportError:
        FFmpegError = RuntimeError

    try:
        segments, info = model.transcribe(str(path), language=language, beam_size=5)
        segment_list = [
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
            for s in segments
        ]
    except (FFmpegError, OSError, RuntimeError, ValueError) as e:
        return {"error": f"Transcription failed: {type(e).__name__}: {e}"}

    return {
        "text": " ".join(s["text"] for s in segment_list),
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "segments": segment_list,
        "backend": "local",
        "model": model_size,
    }


def _transcribe_openai(path: str, language: str | None) -> dict:
    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        return {
            "error": "openai package not installed. Run: pip install 'whisper-transcribe-mcp[openai]'"
        }

    try:
        client = OpenAI(timeout=60.0)
        with open(path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
            )
    except (OpenAIError, OSError) as e:
        return {"error": _openai_error_message(e), "_openai_failed": True}

    segments = result.segments or []
    return {
        "text": result.text,
        "language": result.language,
        "language_probability": 1.0,
        "segments": [
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
            for s in segments
        ],
        "backend": "openai",
        "model": "whisper-1",
    }


def _post_process(text: str, system_prompt: str | None) -> dict:
    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        return {"error": "openai package not installed. Post-processing requires the openai extra."}

    try:
        client = OpenAI(timeout=30.0)
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt or DEFAULT_POST_PROCESS_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return {"text": response.choices[0].message.content}
    except OpenAIError as e:
        return {"error": _openai_error_message(e)}


def _apply_post_process(result: dict, system_prompt: str | None) -> dict:
    if "error" in result:
        return result

    gpt = _post_process(result["text"], system_prompt)
    if "error" in gpt:
        result["post_process_error"] = gpt["error"]
    else:
        result["raw_text"] = result["text"]
        result["text"] = gpt["text"]
        result["post_process_model"] = GPT_MODEL

    return result


@mcp.tool()
def transcribe_file(
    file_path: str,
    language: str | None = None,
    model_size: str | None = None,
    post_process: bool = False,
    post_process_prompt: str | None = None,
) -> dict:
    """Transcribe an audio file to text.

    Args:
        file_path: Absolute path to the audio file (mp3, wav, m4a, ogg, flac, etc.)
        language: Language code (e.g. 'es', 'en', 'fr'). Auto-detected if not provided.
        model_size: Local model size: tiny, base, small, medium, large-v3 (plus the .en,
                    turbo, and distil variants). Ignored when using the OpenAI backend.
                    Defaults to the WHISPER_MODEL environment variable (default: 'base').
        post_process: If True, passes the transcription through GPT to fix spelling,
                      grammar, and punctuation. Requires the openai package.
        post_process_prompt: Custom system prompt for post-processing. Use this to provide
                             domain-specific context, proper nouns, or product names that
                             Whisper may have misspelled. Falls back to a generic correction
                             prompt if not provided.

    Returns:
        dict with 'text', 'language', 'segments', 'backend', and 'model'.
        When post_process=True, also includes 'raw_text' (original transcription)
        and 'post_process_model'. If post-processing fails, includes 'post_process_error'
        and 'text' retains the original transcription.
    """
    invalid = _validate_options(language, model_size)
    if invalid:
        return invalid

    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        return {"error": f"File not found: {file_path}"}
    if path.stat().st_size == 0:
        return {"error": f"File is empty: {file_path}"}

    if _USE_OPENAI:
        result = _transcribe_openai(str(path), language)
        if result.pop("_openai_failed", False):
            openai_error = result["error"]
            local = _transcribe_local(str(path), language, model_size or DEFAULT_MODEL)
            if "error" not in local:
                local["fallback_reason"] = openai_error
                result = local
            else:
                result["openai_error"] = openai_error
                return result
    else:
        result = _transcribe_local(str(path), language, model_size or DEFAULT_MODEL)

    if post_process:
        result = _apply_post_process(result, post_process_prompt)

    return result


@mcp.tool()
def transcribe_base64(
    audio_base64: str,
    extension: str = "mp3",
    language: str | None = None,
    model_size: str | None = None,
    post_process: bool = False,
    post_process_prompt: str | None = None,
) -> dict:
    """Transcribe audio provided as a base64-encoded string.

    Args:
        audio_base64: Base64-encoded audio data.
        extension: Audio format of the data (mp3, wav, m4a, ogg, flac, webm, mp4, etc.).
        language: Language code. Auto-detected if not provided.
        model_size: Local model size. Ignored when using the OpenAI backend.
        post_process: If True, passes the transcription through GPT to fix spelling,
                      grammar, and punctuation. Requires the openai package.
        post_process_prompt: Custom system prompt for post-processing. Use this to provide
                             domain-specific context, proper nouns, or product names.

    Returns:
        dict with 'text', 'language', 'segments', 'backend', and 'model'.
        When post_process=True, also includes 'raw_text' and 'post_process_model'.
    """
    extension = extension.lower().lstrip(".")
    if extension not in AUDIO_EXTENSIONS:
        return {
            "error": f"Unsupported extension: {extension!r}. Valid: {', '.join(AUDIO_EXTENSIONS)}"
        }
    invalid = _validate_options(language, model_size)
    if invalid:
        return invalid

    try:
        audio_bytes = base64.b64decode(audio_base64, validate=True)
    except ValueError as e:
        return {"error": f"Invalid base64 data: {e}"}

    fd, tmp_path = tempfile.mkstemp(suffix=f".{extension}", prefix="whisper-")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(audio_bytes)
        return transcribe_file(
            tmp_path,
            language=language,
            model_size=model_size,
            post_process=post_process,
            post_process_prompt=post_process_prompt,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@mcp.tool()
def list_models() -> dict:
    """List available Whisper model sizes and current configuration."""
    return {
        "active_backend": "openai" if _USE_OPENAI else "local",
        "default_local_model": DEFAULT_MODEL,
        "current_loaded_model": _local_model.model_size_or_path if _local_model else None,
        "local_models": [
            {"name": "tiny", "params": "39M", "speed": "~32x", "note": "Fastest, least accurate"},
            {"name": "base", "params": "74M", "speed": "~16x", "note": "Good balance"},
            {"name": "small", "params": "244M", "speed": "~6x", "note": "Better accuracy"},
            {"name": "medium", "params": "769M", "speed": "~2x", "note": "High accuracy"},
            {
                "name": "large-v3",
                "params": "1.5G",
                "speed": "~1x",
                "note": "Best accuracy, slowest",
            },
        ],
        "openai_model": "whisper-1 (set OPENAI_API_KEY to activate)",
        "post_process_model": GPT_MODEL,
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
