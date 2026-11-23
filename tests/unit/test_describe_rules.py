"""H-0035: roles-v0 rules and audio flags (pure functions)."""
from __future__ import annotations

from src.describe.audio import flags, overlap_ms
from src.describe.roles import suggest_roles


def test_single_scene_is_hook() -> None:
    assert suggest_roles([(0, 9000)], []) == ["hook"]


def test_two_scenes_hook_then_cta() -> None:
    assert suggest_roles([(0, 3000), (3000, 6000)], []) == ["hook", "cta"]


def test_middle_scenes_by_speech_and_length() -> None:
    scenes = [(0, 2000), (2000, 4000), (4000, 8000), (8000, 8500), (8500, 12000), (12000, 14000)]
    speech = [(4000, 6500)]
    assert suggest_roles(scenes, speech) == ["hook", "product_intro", "proof", "other", "demo", "cta"]


def test_roles_are_deterministic() -> None:
    scenes = [(i * 1000, i * 1000 + 1000) for i in range(10)]
    assert suggest_roles(scenes, [(0, 5000)]) == suggest_roles(scenes, [(0, 5000)])


def test_overlap() -> None:
    assert overlap_ms((1000, 3000), [(0, 1500), (2500, 9000)]) == 1000


def test_few_words_over_speech_is_asr_suspicious_never_no_speech() -> None:
    f = flags(True, False, speech_ratio=0.7, speech_ms=12000, word_count=0)
    assert f == ["ASR_SUSPICIOUS"]
    assert not any("NO_SPEECH" in x for x in f)


def test_normal_rate_is_not_suspicious() -> None:
    assert flags(True, False, 0.7, 12000, 30) == []  # 150 wpm


def test_short_speech_not_judged() -> None:
    assert flags(True, False, 0.2, 2000, 0) == []


def test_low_vad_and_silent_and_no_stream() -> None:
    assert flags(True, True, 0.0, 0, 0) == ["SILENT_TRACK", "LOW_VAD_SPEECH"]
    assert flags(False, True, 0.0, 0, 0) == ["NO_AUDIO_STREAM"]
