"""H-0024 G3: ingest auto-detects the language by default and records it in the transcript."""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

import src.ingest.__main__ as ing


def test_default_language_is_auto_and_overridable() -> None:
    assert ing.build_parser().parse_args(["x.mp4"]).language == "auto"
    assert ing.build_parser().parse_args(["x.mp4", "--language", "ar"]).language == "ar"
    assert ing.STAGE_DEFAULTS["language"] == "auto"
    assert ing.asr_language("auto") is None and ing.asr_language("fr") == "fr"


def test_transcript_cache_name_includes_language_request() -> None:
    assert ing.transcript_name("large-v3-turbo", "auto") == "transcript.large-v3-turbo.auto.json"
    assert ing.transcript_name("tiny", "ar") == "transcript.tiny.ar.json"


def test_transcribe_records_detected_language(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    class FakeModel:
        def __init__(self, name: str, **kw: object) -> None:
            seen["model"] = name

        def transcribe(self, audio: object, language: str | None = None, **kw: object):
            seen["language"] = language
            info = types.SimpleNamespace(language="fr", language_probability=0.9876, duration=2.0)
            return iter([]), info

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    monkeypatch.setattr(ing, "load_audio", lambda src: None)
    out = tmp_path / "t.json"
    data = ing.transcribe(Path("x.mp4"), out, "tiny", ing.asr_language("auto"), 5)
    assert seen["language"] is None  # None = let faster-whisper detect
    assert data["language"] == "fr" and data["language_probability"] == 0.988
    assert data["language_requested"] == "auto"
    assert '"language": "fr"' in out.read_text(encoding="utf-8")
