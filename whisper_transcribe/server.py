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

GPT_MODEL = "gpt-5.4-nano"

DEFAULT_POST_PROCESS_PROMPT = (
    "You are a transcription correction assistant. "
    "Fix spelling errors, grammar, and punctuation in the transcribed text. "
    "Preserve the original meaning, tone, and language. "
    "Do not add, remove, or summarize content. "
    "Return only the corrected text, no explanations."
)


def _get_local_model(model_size: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, {"error": "faster-whisper not installed. Run: pip install 'whisper-transcribe-mcp[local]'"}

    global _local_model
    if _local_model is None or _local_model.model_size_or_path != model_size:
        _local_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _local_model, None


def _transcribe_local(path: str, language: str | None, model_size: str) -> dict:
    model, err = _get_local_model(model_size)
    if err:
        return err

    try:
        segments, info = model.transcribe(str(path), language=language, beam_size=5)
        segment_list = [
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
            for s in segments
        ]
    except Exception as e:
        return {"error": f"Transcription failed: {e}"}

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
        from openai import OpenAI
    except ImportError:
        return {"error": "openai package not installed. Run: pip install 'whisper-transcribe-mcp[openai]'"}

    try:
        client = OpenAI(timeout=60.0)
        with open(path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
            )
    except Exception as e:
        return {"error": str(e), "_openai_failed": True}

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
        from openai import OpenAI
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
    except Exception as e:
        return {"error": str(e)}


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
        model_size: Local model size: tiny, base, small, medium, large-v3.
                    Ignored when using the OpenAI backend.
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
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
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
        extension: File extension for the temp file (mp3, wav, m4a, ogg, etc.).
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
    try:
        audio_bytes = base64.b64decode(audio_base64, validate=True)
    except Exception as e:
        return {"error": f"Invalid base64 data: {e}"}

    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        return transcribe_file(
            tmp_path,
            language=language,
            model_size=model_size,
            post_process=post_process,
            post_process_prompt=post_process_prompt,
        )
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
        "post_process_model": GPT_MODEL,
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
