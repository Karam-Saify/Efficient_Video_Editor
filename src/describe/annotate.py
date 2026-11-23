"""Footage Intelligence v0: one source video -> annotation record, descriptions to-do, storyboard; corrections in.

Layout (all git-ignored):
    cache/<video_id>/meta.json, transcript.<model>.<lang>.json, scenes.json, keyframes/   (shared with src.ingest)
    cache/<video_id>/describe/annotation.json        the record (schemas/annotation.schema.json)
    cache/<video_id>/describe/descriptions.todo.json at most 4 keyframes for a Claude Code session to describe
    cache/<video_id>/describe/corrections/<sha>.json every imported correction file, kept verbatim
    cache/<video_id>/storyboard/index.html           offline storyboard with an Export corrections button

All times are integer ms computed here (I-4). No LLM is called (ADR-0023 zero cost); descriptions come from a
session that reads only the listed keyframes (CLAUDE.md rule 1, I-3).
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from src.common import CACHE, ROOT, probe, read_json, video_id, write_json
from src.describe.audio import VAD, audio_signals
from src.describe.roles import RULES_VERSION, suggest_roles
from src.describe.schema import validate_annotation
from src.manifest import StageError, run_stage, sha256_file

STAGE_VERSION = "1"
MAX_DESCRIBED = 4
MAX_DESCRIPTION_CHARS = 300
TODO_FORMAT = "descriptions.todo/0.1"
CORRECTIONS_FORMAT = "storyboard-corrections/0.1"
ROLES = ("hook", "product_intro", "demo", "proof", "cta", "other")


def ms(seconds: float) -> int:
    return int(round(seconds * 1000))


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_record(path: Path, rec: dict[str, Any]) -> str:
    errs = validate_annotation(rec)
    if errs:
        raise StageError("annotation record invalid, not written: " + "; ".join(map(str, errs[:5])))
    write_json(path, rec)
    return sha256_file(path)


def pick_described(n_scenes: int, k: int = MAX_DESCRIBED) -> list[int]:
    """Scene indices whose keyframe gets a description: all if <= k, else k spread evenly (first and last in)."""
    if n_scenes <= k:
        return list(range(n_scenes))
    return [i * (n_scenes - 1) // (k - 1) for i in range(k)]


def keyframe_times(start: int, end: int, per_scene: int) -> list[int]:
    """Same spacing as src.ingest.keyframes, in integer ms."""
    return [start + (end - start) * (k + 1) // (per_scene + 1) for k in range(per_scene)]


def build_record(
    *, vid: str, rights_id: str, meta: dict[str, Any], transcript: dict[str, Any], scenes_s: list[dict[str, Any]],
    keyframe_dir: Path, audio: dict[str, Any], speech: list[tuple[int, int]], asr_model: str, language: str,
    scene_detector: str, per_scene: int = 1,
) -> dict[str, Any]:
    dur = ms(meta["duration"])
    lang = transcript.get("language") or "und"
    segs = []
    for i, s in enumerate(transcript.get("segments", [])):
        a, b = min(ms(s["start"]), dur), min(ms(s["end"]), dur)
        segs.append({"id": i, "start_ms": a, "end_ms": max(a, b), "label_origin": "machine",
                     "text": {"value": s.get("text", ""), "label_origin": "machine"},
                     "language": {"value": lang, "label_origin": "machine"}})
    spans = []
    for sc in scenes_s:
        a, b = ms(sc["start"]), min(ms(sc["end"]), dur)
        if b > a:
            spans.append((int(sc["id"]), a, b))
    if not spans:
        spans = [(0, 0, dur)]
    roles = suggest_roles([(a, b) for _, a, b in spans], speech)
    scenes = []
    for (sid, a, b), role in zip(spans, roles, strict=True):
        kfs = []
        for k, t in enumerate(keyframe_times(a, b, per_scene)):
            f = keyframe_dir / f"scene{sid:03d}_{k}.jpg"
            if f.is_file():
                kfs.append({"file": f"keyframes/{f.name}", "t_ms": t, "sha256": sha256_file(f),
                            "label_origin": "machine"})
        scenes.append({"id": sid, "start_ms": a, "end_ms": b, "label_origin": "machine", "keyframes": kfs,
                       "description": {"value": None, "label_origin": "machine"},
                       "role": {"value": role, "label_origin": "machine"}})
    from faster_whisper import __version__ as fw

    return {
        "record_type": "source", "annotation_version": "0.1", "video_id": vid, "rights_id": rights_id,
        "media": {"duration_ms": dur, "width": int(meta.get("width") or 1), "height": int(meta.get("height") or 1),
                  "fps": meta.get("fps") or 0, "has_audio": bool(meta["has_audio"])},
        "provenance": {"asr_model": asr_model, "asr_language_requested": language, "scene_detector": scene_detector,
                       "vad": f"faster-whisper {fw} silero {json.dumps(VAD, sort_keys=True)}",
                       "rules_version": RULES_VERSION, "describer": None},
        "transcript": {"label_origin": "machine", "language": {"value": lang, "label_origin": "machine"},
                       "language_probability": float(transcript.get("language_probability") or 0.0),
                       "segments": segs},
        "audio": audio,
        "scenes": scenes,
    }


def todo_for(rec: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    base = cache_root / rec["video_id"]
    items = []
    for i in pick_described(len(rec["scenes"])):
        sc = rec["scenes"][i]
        if not sc["keyframes"]:
            continue
        kf = sc["keyframes"][0]
        p = (base / kf["file"]).resolve()
        items.append({"scene_id": sc["id"], "keyframe": kf["file"], "keyframe_sha256": kf["sha256"],
                      "path": p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix(),
                      "start_ms": sc["start_ms"], "end_ms": sc["end_ms"], "description": None})
    return {
        "format": TODO_FORMAT, "video_id": rec["video_id"], "describer": None,
        "instructions": (f"Read ONLY the listed keyframe images (max {MAX_DESCRIBED}; never the video). For each, "
                         f"write one plain sentence (<= {MAX_DESCRIPTION_CHARS} chars) of what is visible: people, "
                         "product, action, on-screen text. No times, no numbers you did not read. Set `describer` "
                         "to 'claude-code-session <model id>'. Then run: python -m src.describe apply-descriptions "
                         "<video> <this file>"),
        "items": items,
    }


def _scene_detector() -> str:
    from scenedetect import __version__ as sd

    return f"scenedetect {sd} ContentDetector"


def has_human_or_described(rec: dict[str, Any]) -> bool:
    if rec.get("provenance", {}).get("describer"):
        return True
    return "human_verified" in json.dumps(rec)


def annotate(
    video: Path, rights_id: str, *, asr_model: str = "large-v3-turbo", language: str = "auto",
    transcript_path: Path | None = None, cache_root: Path = CACHE, force: bool = False,
) -> Path:
    """Run ingest pieces (cached) + audio signals + roles; write record, to-do and storyboard. Returns record path."""
    from src.describe.storyboard import write_storyboard
    from src.ingest.__main__ import asr_language, detect_scenes, keyframes, transcribe, transcript_name

    src = video.resolve()
    if not src.is_file():
        raise StageError(f"video not found: {video}")
    vid = video_id(src)
    base = cache_root / vid
    out = base / "describe"
    rec_p = out / "annotation.json"
    if rec_p.exists() and not force and has_human_or_described(read_json(rec_p)):
        raise StageError(f"{rec_p} holds descriptions or human_verified labels; refusing to overwrite (use --force)")
    base.mkdir(parents=True, exist_ok=True)
    meta_p = base / "meta.json"
    if not meta_p.exists():
        write_json(meta_p, {"video_id": vid, **probe(src)})
    meta = read_json(meta_p)
    if transcript_path is not None:
        tr = read_json(transcript_path)
        asr_label = f"external:{transcript_path.name}"
    else:
        tr_p = base / transcript_name(asr_model, language)
        tr = read_json(tr_p) if tr_p.exists() else transcribe(src, tr_p, asr_model, asr_language(language), 5)
        asr_label = asr_model
    sc_p = base / "scenes.json"
    scenes_s = read_json(sc_p) if sc_p.exists() else detect_scenes(src, sc_p)
    keyframes(src, scenes_s, base / "keyframes", 1)
    words = sum(len(s.get("words") or s.get("text", "").split()) for s in tr.get("segments", []))
    config = {"rights_id": rights_id, "asr_model": asr_label, "language": language, "max_described": MAX_DESCRIBED,
              "rules_version": RULES_VERSION, "vad": VAD, "stage_version": STAGE_VERSION}

    def work(inputs: list[Path], out_dir: Path, cfg: dict[str, Any]) -> str:
        audio, speech = audio_signals(src, bool(meta["has_audio"]), ms(meta["duration"]), words)
        rec = build_record(vid=vid, rights_id=rights_id, meta=meta, transcript=tr, scenes_s=scenes_s,
                           keyframe_dir=base / "keyframes", audio=audio, speech=speech, asr_model=asr_label,
                           language=language, scene_detector=_scene_detector())
        write_record(out_dir / "annotation.json", rec)
        write_json(out_dir / "descriptions.todo.json", todo_for(rec, cache_root))
        return "ok"

    inputs = [src, meta_p, sc_p, base / "keyframes"] + ([transcript_path] if transcript_path else [])
    if force:
        (out / "manifest.json").unlink(missing_ok=True)
    run_stage("describe", inputs, out, config, work, tools=("ffmpeg",))
    write_storyboard(rec_p, base / "storyboard" / "index.html")
    return rec_p


def record_path(video: Path, cache_root: Path = CACHE) -> Path:
    p = cache_root / video_id(video.resolve()) / "describe" / "annotation.json"
    if not p.is_file():
        raise StageError(f"no annotation record for {video}; run: python -m src.describe annotate {video} "
                         "--rights-id ...")
    return p


def apply_descriptions(video: Path, todo_path: Path, cache_root: Path = CACHE) -> Path:
    from src.describe.storyboard import write_storyboard

    rec_p = record_path(video, cache_root)
    rec = read_json(rec_p)
    todo = read_json(todo_path)
    if todo.get("format") != TODO_FORMAT or todo.get("video_id") != rec["video_id"]:
        raise StageError("descriptions file is not a to-do for this video")
    describer = todo.get("describer")
    if not isinstance(describer, str) or not describer.strip():
        raise StageError("descriptions file must name its `describer` (e.g. 'claude-code-session <model id>')")
    items = todo.get("items") or []
    if len(items) > MAX_DESCRIBED:
        raise StageError(f"{len(items)} described keyframes > {MAX_DESCRIBED} (CLAUDE.md rule 1)")
    by_id = {sc["id"]: sc for sc in rec["scenes"]}
    for it in items:
        sc = by_id.get(it.get("scene_id"))
        if sc is None or not sc["keyframes"] or sc["keyframes"][0]["sha256"] != it.get("keyframe_sha256"):
            raise StageError(f"to-do item {it.get('scene_id')!r} does not match a scene keyframe of this record")
        d = it.get("description")
        if d is None:
            continue
        if not isinstance(d, str) or not d.strip() or len(d) > MAX_DESCRIPTION_CHARS:
            raise StageError(f"scene {sc['id']}: description must be 1..{MAX_DESCRIPTION_CHARS} chars")
        if sc["description"]["label_origin"] == "human_verified":
            continue  # a partner's word is never overwritten by a model
        sc["description"] = {"value": d.strip(), "label_origin": "machine"}
    rec["provenance"]["describer"] = describer.strip()[:120]
    write_record(rec_p, rec)
    write_storyboard(rec_p, rec_p.parent.parent / "storyboard" / "index.html")
    return rec_p


def _verify(label: dict[str, Any], value: Any) -> dict[str, Any]:
    machine = label["machine_value"] if "machine_value" in label else label["value"]
    return {"value": value, "label_origin": "human_verified", "machine_value": machine}


def import_corrections(video: Path, corr_path: Path, cache_root: Path = CACHE) -> Path:
    """Store a storyboard export as human_verified labels; the machine value stays in machine_value."""
    from src.describe.storyboard import write_storyboard

    rec_p = record_path(video, cache_root)
    raw = corr_path.read_bytes()
    corr = json.loads(raw.decode("utf-8"))
    rec = read_json(rec_p)
    if corr.get("format") != CORRECTIONS_FORMAT or corr.get("video_id") != rec["video_id"]:
        raise StageError("not a storyboard corrections file for this video")
    if corr.get("record_sha256") != sha256_file(rec_p):
        raise StageError("corrections were made on an older storyboard; regenerate it and correct again")
    new = copy.deepcopy(rec)
    scenes = {sc["id"]: sc for sc in new["scenes"]}
    segs = {sg["id"]: sg for sg in new["transcript"]["segments"]}
    for c in corr.get("scenes", []):
        sc = scenes.get(c.get("scene_id"))
        if sc is None:
            raise StageError(f"unknown scene_id {c.get('scene_id')!r}")
        if c.get("role") not in ROLES:
            raise StageError(f"scene {sc['id']}: role {c.get('role')!r} not in {ROLES}")
        desc = c.get("description")
        desc = desc.strip() if isinstance(desc, str) and desc.strip() else None
        sc["description"] = _verify(sc["description"], desc)
        sc["role"] = _verify(sc["role"], c["role"])
    for c in corr.get("segments", []):
        sg = segs.get(c.get("segment_id"))
        if sg is None:
            raise StageError(f"unknown segment_id {c.get('segment_id')!r}")
        sg["text"] = _verify(sg["text"], str(c.get("text", "")))
        sg["language"] = _verify(sg["language"], c.get("language"))
    digest = sha256_bytes(raw)
    new["provenance"].setdefault("corrections", []).append({"sha256": digest, "corrected_on": corr.get("corrected_on")})
    keep = rec_p.parent / "corrections" / f"{digest}.json"
    keep.parent.mkdir(parents=True, exist_ok=True)
    write_record(rec_p, new)  # validates first; nothing is written on an invalid result
    keep.write_bytes(raw)
    write_storyboard(rec_p, rec_p.parent.parent / "storyboard" / "index.html")
    return rec_p
