"""Audio signals for the annotation record: loudness (ffmpeg ebur128), speech coverage (silero VAD bundled
with faster-whisper), per-second energy and a music/ambience proxy (numpy). Local, free, CPU only.

Rule (Founder, S1 correction): few words is evidence the ASR failed, not that nobody speaks. So a low word rate
over VAD speech is `ASR_SUSPICIOUS`; low VAD coverage is `LOW_VAD_SPEECH`. Nothing here says "no speech".
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np

SR = 16000
VAD = {"threshold": 0.5, "min_speech_duration_ms": 250, "min_silence_duration_ms": 500, "speech_pad_ms": 100}
SILENCE_DBFS = -50.0  # 100 ms frames quieter than this count as silence
SUSPICIOUS_WPM = 60.0  # words per VAD-speech minute; conversational speech is ~120-180
MIN_SPEECH_FOR_RATE_MS = 3000  # below this, the word rate is too noisy to judge
LOW_SPEECH_RATIO = 0.10


def load_audio(src: Path) -> np.ndarray:
    from src.ingest.__main__ import load_audio as _load

    return _load(src)


def ebur128(src: Path) -> tuple[float | None, float | None]:
    """(integrated LUFS, loudness range LU) from ffmpeg's ebur128 summary; None when not reported."""
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-hide_banner", "-i", str(src), "-vn", "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    ).stderr
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else err
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    lra = re.search(r"LRA:\s+(-?[\d.]+) LU", summary)
    return (float(i.group(1)) if i else None, float(lra.group(1)) if lra else None)


def speech_intervals_ms(audio: np.ndarray) -> list[tuple[int, int]]:
    from faster_whisper.vad import VadOptions, get_speech_timestamps

    ts = get_speech_timestamps(audio, VadOptions(**VAD), sampling_rate=SR)
    return [(int(t["start"]) * 1000 // SR, int(t["end"]) * 1000 // SR) for t in ts]


def frame_db(audio: np.ndarray, frame: int) -> np.ndarray:
    import numpy as np

    n = len(audio) // frame
    if n == 0:
        return np.zeros(0)
    x = audio[: n * frame].reshape(n, frame).astype(np.float64)
    rms = np.sqrt(np.mean(x * x, axis=1))
    return 20 * np.log10(np.maximum(rms, 1e-6))


def flags(has_audio: bool, silent: bool, speech_ratio: float, speech_ms: int, word_count: int) -> list[str]:
    if not has_audio:
        return ["NO_AUDIO_STREAM"]
    out: list[str] = []
    if silent:
        out.append("SILENT_TRACK")
    if speech_ratio < LOW_SPEECH_RATIO:
        out.append("LOW_VAD_SPEECH")
    if speech_ms >= MIN_SPEECH_FOR_RATE_MS and word_count * 60000 / speech_ms < SUSPICIOUS_WPM:
        out.append("ASR_SUSPICIOUS")
    return out


def overlap_ms(a: tuple[int, int], spans: list[tuple[int, int]]) -> int:
    return sum(max(0, min(a[1], e) - max(a[0], s)) for s, e in spans)


def audio_signals(
    src: Path, has_audio: bool, duration_ms: int, word_count: int
) -> tuple[dict[str, Any], list[tuple[int, int]]]:
    """(audio block for the record, VAD speech intervals in ms)."""
    if not has_audio:
        block = {"label_origin": "machine", "integrated_lufs": None, "loudness_range_lu": None, "speech_ratio": 0.0,
                 "word_count": word_count, "words_per_speech_min": None, "nonspeech_sound_ratio": 0.0,
                 "energy_db_1s": [], "flags": flags(False, True, 0.0, 0, word_count)}
        return block, []
    audio = load_audio(src)
    lufs, lra = ebur128(src)
    speech = speech_intervals_ms(audio)
    speech_ms = sum(e - s for s, e in speech)
    db100 = frame_db(audio, SR // 10)
    loud = [i for i, d in enumerate(db100) if d > SILENCE_DBFS]
    nonspeech_loud = [i for i in loud if overlap_ms((i * 100, i * 100 + 100), speech) == 0]
    ratio = round(min(1.0, speech_ms / duration_ms), 3) if duration_ms else 0.0
    block = {
        "label_origin": "machine",
        "integrated_lufs": lufs,
        "loudness_range_lu": lra,
        "speech_ratio": ratio,
        "word_count": word_count,
        "words_per_speech_min": round(word_count * 60000 / speech_ms, 1) if speech_ms else None,
        "nonspeech_sound_ratio": round(len(nonspeech_loud) / len(db100), 3) if len(db100) else 0.0,
        "energy_db_1s": [round(float(d), 1) for d in frame_db(audio, SR)],
        "flags": flags(True, not loud, ratio, speech_ms, word_count),
    }
    return block, speech
