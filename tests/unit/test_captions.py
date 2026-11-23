"""H-0024 G3: transcript -> caption track (output-time ms by code) and script-based `dir`."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.bidi import first_strong_dir, text_dir
from src.captions import caption_track
from src.validate import validate

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("text, expected", [
    ("مرحبا بكم في القناة", "rtl"),  # ar
    ("Link in bio", "ltr"),  # en
    ("Bonjour à tous, ça va ?", "ltr"),  # fr
    ("שלום לכולם", "rtl"),  # he
    ("جربت iPhone 16 Pro امبارح بالليل", "rtl"),  # mixed ar + English, mostly Arabic letters
    ("New iPhone review يا جماعة", "ltr"),  # mixed, mostly Latin letters
    ("سلام دوستان", "rtl"),  # fa (Persian letters are AL)
    ("250 2026 !?", "ltr"),  # no strong characters
])
def test_text_dir_follows_strong_characters(text: str, expected: str) -> None:
    assert text_dir(text) == expected


def test_first_strong_dir() -> None:
    assert first_strong_dir("iPhone جديد جدا جدا") == "ltr"
    assert first_strong_dir("١٠٪ خصم") == "rtl"
    assert first_strong_dir("250") is None


def W(w: str, s: float, e: float) -> dict:
    return {"w": w, "start": s, "end": e, "p": 0.9}


TRANSCRIPT = {
    "language": "ar", "language_probability": 0.97,
    "segments": [
        {"id": 0, "start": 1.0, "end": 3.0, "text": "السعر الحقيقي هون",
         "words": [W("السعر", 1.0, 1.4), W("الحقيقي", 1.4, 2.0), W("هون", 2.1, 2.9)]},
        {"id": 1, "start": 5.0, "end": 7.2, "text": "Link in bio",
         "words": [W("Link", 5.0, 5.3), W("in", 5.3, 5.5), W("bio", 5.5, 7.2)]},
    ],
}


def test_caption_track_maps_source_time_to_output_time() -> None:
    clips = [{"id": "c1", "source": "s", "in_ms": 1000, "out_ms": 3000},  # output 0..2000
             {"id": "c2", "source": "s", "in_ms": 5000, "out_ms": 7000}]  # output 2000..4000
    caps = caption_track(TRANSCRIPT, clips, "s", max_words=2)
    assert caps == [
        {"id": "cap1", "text": "السعر الحقيقي", "start_ms": 0, "end_ms": 1000, "dir": "rtl"},
        {"id": "cap2", "text": "هون", "start_ms": 1100, "end_ms": 1900, "dir": "rtl"},
        {"id": "cap3", "text": "Link in", "start_ms": 2000, "end_ms": 2500, "dir": "ltr"},
        {"id": "cap4", "text": "bio", "start_ms": 2500, "end_ms": 4000, "dir": "ltr"},  # clamped to clip end
    ]
    for c in caps:
        assert all(isinstance(c[k], int) for k in ("start_ms", "end_ms"))


def test_words_outside_clips_are_dropped_and_clip_order_wins() -> None:
    clips = [{"id": "c2", "source": "s", "in_ms": 5000, "out_ms": 5500},
             {"id": "c1", "source": "s", "in_ms": 1000, "out_ms": 1400}]
    caps = caption_track(TRANSCRIPT, clips, "s")
    assert [(c["text"], c["start_ms"], c["end_ms"]) for c in caps] == [("Link in", 0, 500), ("السعر", 500, 900)]


def test_other_sources_and_max_ms_split() -> None:
    clips = [{"id": "c1", "source": "s", "in_ms": 0, "out_ms": 8000}]
    assert caption_track(TRANSCRIPT, clips, "other") == []
    caps = caption_track(TRANSCRIPT, clips, "s", max_words=10, max_ms=1000)
    assert [c["text"] for c in caps] == ["السعر الحقيقي", "هون", "Link in", "bio"]


def test_caption_track_is_valid_in_a_timeline() -> None:
    clips = [{"id": "c1", "source": "srcA", "in_ms": 1000, "out_ms": 3000},
             {"id": "c2", "source": "srcA", "in_ms": 5000, "out_ms": 7000}]
    tl = {"version": "0.1", "canvas": {"width": 1080, "height": 1920, "fps": 30}, "target_duration_ms": 4000,
          "sources": [{"id": "srcA", "path": "tests/fixtures/media/src_a.txt", "duration_ms": 10000}],
          "tracks": {"video": clips, "captions": caption_track(TRANSCRIPT, clips, "srcA")}}
    assert validate(tl, base_dir=ROOT) == []


def test_segment_without_word_timestamps_is_one_unit() -> None:
    tr = {"segments": [{"id": 0, "start": 0.0, "end": 1.0, "text": "Hello there", "words": []}]}
    caps = caption_track(tr, [{"id": "c", "source": "s", "in_ms": 0, "out_ms": 2000}], "s")
    assert caps == [{"id": "cap1", "text": "Hello there", "start_ms": 0, "end_ms": 1000, "dir": "ltr"}]


def test_deterministic() -> None:
    clips = [{"id": "c1", "source": "s", "in_ms": 0, "out_ms": 8000}]
    assert caption_track(TRANSCRIPT, clips, "s") == caption_track(TRANSCRIPT, clips, "s")
