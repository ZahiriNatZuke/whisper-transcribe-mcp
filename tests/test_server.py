from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace

import whisper_transcribe.server as server


def test_transcribe_file_rejects_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.wav"

    assert server.transcribe_file(str(missing)) == {"error": f"File not found: {missing}"}


def test_transcribe_file_rejects_empty_file(tmp_path: Path) -> None:
    empty = tmp_path / "empty.wav"
    empty.touch()

    assert server.transcribe_file(str(empty)) == {"error": f"File is empty: {empty}"}


def test_openai_failure_falls_back_to_local(monkeypatch, tmp_path: Path) -> None:
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"audio")
    monkeypatch.setattr(server, "_USE_OPENAI", True)
    monkeypatch.setattr(
        server,
        "_transcribe_openai",
        lambda path, language: {"error": "cloud unavailable", "_openai_failed": True},
    )
    monkeypatch.setattr(
        server,
        "_transcribe_local",
        lambda path, language, model: {
            "text": "hello",
            "language": "en",
            "segments": [],
            "backend": "local",
            "model": model,
        },
    )

    result = server.transcribe_file(str(audio), model_size="small")

    assert result["backend"] == "local"
    assert result["model"] == "small"
    assert result["fallback_reason"] == "cloud unavailable"


def test_transcribe_base64_delegates_and_cleans_up(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_transcribe(path: str, **kwargs):
        temp_path = Path(path)
        captured["path"] = temp_path
        captured["contents"] = temp_path.read_bytes()
        captured["kwargs"] = kwargs
        return {"text": "done"}

    monkeypatch.setattr(server, "transcribe_file", fake_transcribe)

    result = server.transcribe_base64(
        base64.b64encode(b"audio-bytes").decode(),
        extension="wav",
        language="es",
        model_size="tiny",
        post_process=True,
        post_process_prompt="Keep names.",
    )

    assert result == {"text": "done"}
    assert captured["contents"] == b"audio-bytes"
    assert captured["kwargs"] == {
        "language": "es",
        "model_size": "tiny",
        "post_process": True,
        "post_process_prompt": "Keep names.",
    }
    assert not captured["path"].exists()


def test_transcribe_base64_rejects_invalid_data() -> None:
    result = server.transcribe_base64("not base64!")

    assert result["error"].startswith("Invalid base64 data:")


def test_apply_post_process_preserves_transcript_on_error(monkeypatch) -> None:
    monkeypatch.setattr(server, "_post_process", lambda text, prompt: {"error": "rate limited"})

    result = server._apply_post_process({"text": "raw", "backend": "local"}, None)

    assert result == {"text": "raw", "backend": "local", "post_process_error": "rate limited"}


def test_apply_post_process_replaces_text_and_keeps_raw(monkeypatch) -> None:
    monkeypatch.setattr(server, "_post_process", lambda text, prompt: {"text": "corrected"})

    result = server._apply_post_process({"text": "raw", "backend": "local"}, "custom")

    assert result["text"] == "corrected"
    assert result["raw_text"] == "raw"
    assert result["post_process_model"] == server.GPT_MODEL


def test_list_models_reports_loaded_model(monkeypatch) -> None:
    monkeypatch.setattr(server, "_USE_OPENAI", False)
    monkeypatch.setattr(server, "_local_model", SimpleNamespace(model_size_or_path="medium"))

    result = server.list_models()

    assert result["active_backend"] == "local"
    assert result["current_loaded_model"] == "medium"
    assert {model["name"] for model in result["local_models"]} == {
        "tiny",
        "base",
        "small",
        "medium",
        "large-v3",
    }
