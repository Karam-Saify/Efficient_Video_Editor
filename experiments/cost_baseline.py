"""H-0027 cost baseline: measure every unique dev clip end to end, then price it.

    .venv/bin/python experiments/cost_baseline.py measure   # cold run -> experiments/results/H-0027_*.json
    .venv/bin/python experiments/cost_baseline.py report    # prints the docs/COST_BASELINE.md tables from that file

`measure` (dev clips are internal-only, ADR-0006; nothing here is committed except the numbers file):
- dedupes quarantine/dev/*.mp4 by sha256 (Download (2) == Download (4)), shortest first;
- deletes the clip's cached transcript / scenes / keyframes / edit / timings, so every stage runs cold;
- writes a per-clip ops file (default `clean` captions: a no-speech clip has none to restyle;
  set_duration to min(30 s, source); one 1.2x zoom) and runs
  `python -m src.demo` (ingest ASR -> captions + ops -> render 1080x1920), which records `ingest`, `edit`,
  `render` in cache/<video_id>/timings.json;
- then runs `python -m src.ingest <clip>` with the transcript cached, i.e. scenes + keyframes only, recorded as
  `scenes_keyframes` (the code half of "understanding").

`report` holds every price as a cited assumption (ASSUMPTIONS) and every LLM token count as a formula over the
measured transcript size (ESTIMATE); no number in the tables is typed by hand.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.common import cache_dir, probe, video_id  # noqa: E402
from src.timings import (  # noqa: E402
    TIMINGS,
    compute_cost,
    llm_cost,
    percentile,
    planning_cost,
    record,
    run_measured,
    storage_cost,
    tree_bytes,
)

DEV = ROOT / "quarantine" / "dev"
OUT = ROOT / "out" / "h0027"
RESULTS = ROOT / "experiments" / "results" / "H-0027_cost_measurements.json"
MODEL, LANGUAGE = "large-v3-turbo", "auto"

# ---- assumptions (each with its source; see docs/COST_BASELINE.md §2) ----
ASSUMPTIONS: dict[str, Any] = {
    # AWS Fargate Linux/x86 us-east-1 on-demand: $0.000011244 per vCPU-second, $0.000001235 per GB-second
    # (https://aws.amazon.com/fargate/pricing/, fetched 2026-11-23) -> x 3600.
    "vcpu_hour_usd": 0.000011244 * 3600,
    "gb_hour_usd": 0.000001235 * 3600,
    # Cloudflare R2 Standard: $0.015 / GB-month, egress free (https://developers.cloudflare.com/r2/pricing/,
    # fetched 2026-11-23). Free tier (10 GB-month) ignored: marginal cost at scale.
    "storage_gb_month_usd": 0.015,
    # Retention (our assumption, two-way door): source + cache + export kept 30 days for re-edits, then deleted.
    "retention_months": 1.0,
    # Anthropic list prices, claude-api skill model table (cached 2026-11-03), USD per 1M tokens.
    "haiku_5_5": {"input_usd_per_mtok": 0.10, "output_usd_per_mtok": 0.50},
    "sonnet_5_5": {"input_usd_per_mtok": 2.00, "output_usd_per_mtok": 10.00},
    "opus_5_5": {"input_usd_per_mtok": 4.00, "output_usd_per_mtok": 20.00},
}
CEILING, STRETCH = 0.01, 0.005

# ---- LLM token estimate (ADR-0008; no LLM exists yet, so every row using this is an ESTIMATE) ----
ESTIMATE: dict[str, Any] = {
    "chars_per_token_latin": 4.0,   # engineering heuristic for English text
    "chars_per_token_arabic": 2.0,  # Arabic tokenises ~2x worse (heuristic; to be replaced by count_tokens)
    # understanding (small model, once per video): fixed system + rubric, then the transcript as numbered
    # segments (+6 tokens/segment for id + ms bounds) + the scene list (+6 tokens/scene); out: ~15 tok/segment.
    "und_fixed_in": 800, "und_per_segment_in": 6, "und_per_scene_in": 6, "und_per_segment_out": 15, "und_min_out": 50,
    # planning, small model: system + recipe catalogue + segment scores (5 tok/segment) + user ask; out: params.
    "plan_small_fixed_in": 2500, "plan_small_per_segment_in": 5, "plan_small_out": 300,
    # planning, big model on a miss: system + tools + full transcript + recipe catalogue; out: a timeline diff.
    "plan_big_fixed_in": 5000, "plan_big_out": 1500,
    "miss_rate": 0.2,  # default assumption; the report sweeps 0, 0.1, 0.2, 0.5, 1.0
}


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while b := f.read(1 << 20):
            h.update(b)
    return h.hexdigest()


def unique_clips() -> tuple[list[tuple[Path, str]], list[str]]:
    seen: dict[str, Path] = {}
    dupes: list[str] = []
    for p in sorted(DEV.glob("*.mp4")):
        d = _sha256(p)
        if d in seen:
            dupes.append(f"{p.name} == {seen[d].name}")
        else:
            seen[d] = p
    clips = sorted(((p, d) for d, p in seen.items()), key=lambda x: probe(x[0])["duration"])
    return clips, dupes


def measure(only: list[str]) -> None:
    clips, dupes = unique_clips()
    data: dict[str, Any] = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.is_file() else {}
    data.update({"brief": "H-0027", "asr_model": MODEL, "language": LANGUAGE, "duplicates": dupes,
                 "unique_clips": len(clips), "clips": data.get("clips", {})})
    for video, digest in clips:
        if only and video.name not in only:
            continue
        cdir = cache_dir(video_id(video))
        for rel in (f"transcript.{MODEL}.{LANGUAGE}.json", "scenes.json", "keyframes", "edit", TIMINGS):
            t = cdir / rel
            shutil.rmtree(t) if t.is_dir() else t.unlink(missing_ok=True)
        dur_ms = int(probe(video)["duration"] * 1000)
        stem = video.stem.replace(" ", "_").replace("(", "").replace(")", "")
        ops = OUT / "ops" / stem / "short.json"
        ops.parent.mkdir(parents=True, exist_ok=True)
        ops.write_text(json.dumps({"ops": [
            {"op": "set_duration", "target_ms": min(30000, dur_ms)},
            {"op": "add_zoom", "at": {"fraction": 0.1}, "scale": 1.2, "duration_ms": 1000},
        ]}), encoding="utf-8")
        print(f"== {video.name} ({dur_ms} ms)", flush=True)
        cmd = [sys.executable, "-m", "src.demo", "--video", str(video), "--ops", str(ops), "--out", str(OUT),
               "--language", LANGUAGE, "--model", MODEL]
        rc, out, err, demo_m = run_measured(cmd, cwd=ROOT)
        if rc != 0:
            raise SystemExit(f"demo failed on {video.name}: {err.strip()[-500:]}")
        result = json.loads(out.strip().splitlines()[-1])
        rc, _, err, sk = run_measured([sys.executable, "-m", "src.ingest", str(video), "--model", MODEL,
                                       "--language", LANGUAGE], cwd=ROOT)
        if rc != 0:
            raise SystemExit(f"scenes failed on {video.name}: {err.strip()[-500:]}")
        sk["bytes"] = tree_bytes([cdir / "scenes.json", cdir / "keyframes"])
        record(cdir / TIMINGS, "scenes_keyframes", sk)
        tr = json.loads((cdir / f"transcript.{MODEL}.{LANGUAGE}.json").read_text(encoding="utf-8"))
        text = " ".join(s["text"] for s in tr["segments"])
        arabic = sum("؀" <= c <= "ۿ" for c in text)
        data["clips"][video.name] = {
            "sha256": digest, "video_id": video_id(video), "source_ms": dur_ms,
            "source_bytes": video.stat().st_size, "export_ms": result["timeline_ms"],
            "language": tr["language"], "segments": len(tr["segments"]),
            "words": sum(len(s["words"]) for s in tr["segments"]),
            "text_chars": len(text), "arabic_chars": arabic,
            "scenes": len(json.loads((cdir / "scenes.json").read_text(encoding="utf-8"))),
            "asr_runtime_sec_self_reported": tr["runtime_sec"],
            "demo_total": demo_m,
            "stages": json.loads((cdir / TIMINGS).read_text(encoding="utf-8"))["stages"],
        }
        RESULTS.parent.mkdir(parents=True, exist_ok=True)
        RESULTS.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        st = data["clips"][video.name]["stages"]
        print("   " + "  ".join(f"{k}: cpu {v['cpu_s']}s wall {v['wall_s']}s rss {v['peak_rss_mb']}MB"
                                for k, v in sorted(st.items())), flush=True)


# ---- pricing ----

def tokens(c: dict[str, Any], e: dict[str, Any]) -> dict[str, float]:
    lat = c["text_chars"] - c["arabic_chars"]
    tr_tok = lat / e["chars_per_token_latin"] + c["arabic_chars"] / e["chars_per_token_arabic"]
    seg = c["segments"]
    und_in = e["und_fixed_in"] + tr_tok + seg * e["und_per_segment_in"] + c["scenes"] * e["und_per_scene_in"]
    und_out = max(e["und_min_out"], seg * e["und_per_segment_out"])
    return {"transcript": tr_tok, "und_in": und_in, "und_out": und_out,
            "plan_small_in": e["plan_small_fixed_in"] + seg * e["plan_small_per_segment_in"],
            "plan_small_out": e["plan_small_out"],
            "plan_big_in": e["plan_big_fixed_in"] + tr_tok + seg * e["und_per_segment_in"],
            "plan_big_out": e["plan_big_out"]}


def price_clip(c: dict[str, Any], a: dict[str, Any], e: dict[str, Any], *, miss_rate: float,
               big: str = "sonnet_5_5", on_device: bool = False) -> dict[str, float]:
    st, t = c["stages"], tokens(c, e)
    asr = 0.0 if on_device else compute_cost(st["ingest"], a)
    rend = 0.0 if on_device else compute_cost(st["render"], a)
    und = compute_cost(st["scenes_keyframes"], a) + llm_cost(t["und_in"], t["und_out"], a["haiku_5_5"])
    plan = compute_cost(st["edit"], a) + planning_cost(t["plan_small_in"], t["plan_small_out"], t["plan_big_in"],
                                                       t["plan_big_out"], a["haiku_5_5"], a[big], miss_rate=miss_rate)
    nbytes = c["source_bytes"] + sum(int(s.get("bytes", 0)) for s in st.values())
    sto = storage_cost(nbytes, a)
    return {"asr": asr, "understanding": und, "planning": plan, "render": rend, "storage": sto,
            "total": asr + und + plan + rend + sto}


STAGES = ("asr", "understanding", "planning", "render", "storage")


def report() -> None:
    d = json.loads(RESULTS.read_text(encoding="utf-8"))
    a, e, clips = ASSUMPTIONS, ESTIMATE, d["clips"]
    names = sorted(clips, key=lambda n: clips[n]["source_ms"])
    u = 1e3  # print in milli-dollars (m$ = $0.001) for readability

    print("### Measured resources per clip × stage (cold cache, 2 vCPU Xeon 8370C)\n")
    print("| clip | src s | export s | lang | words | stage | wall s | CPU s | peak RSS MB | bytes |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for n in names:
        c = clips[n]
        for k in ("ingest", "scenes_keyframes", "edit", "render"):
            s = c["stages"][k]
            print(f"| {n} | {c['source_ms'] / 1000:.1f} | {c['export_ms'] / 1000:.1f} | {c['language']} | "
                  f"{c['words']} | {k} | {s['wall_s']:.1f} | {s['cpu_s']:.1f} | {s['peak_rss_mb']:.0f} | "
                  f"{s.get('bytes', 0)} |")
        print(f"| {n} | | | | | source | | | | {c['source_bytes']} |")

    print(f"\n### Cost per clip × stage, m$ (miss rate {e['miss_rate']}, big model Sonnet 5.5; "
          "understanding/planning LLM parts are ESTIMATES)\n")
    print("| clip | " + " | ".join(STAGES) + " | total | vs $0.01 | vs $0.005 |")
    print("|---|" + "---|" * (len(STAGES) + 3))
    rows = {n: price_clip(clips[n], a, e, miss_rate=e["miss_rate"]) for n in names}
    for n in names:
        r = rows[n]
        print(f"| {n} | " + " | ".join(f"{r[s] * u:.3f}" for s in STAGES) + f" | **{r['total'] * u:.3f}** | "
              f"{'under' if r['total'] <= CEILING else 'OVER'} | {'under' if r['total'] <= STRETCH else 'OVER'} |")
    for q, label in ((50, "median"), (90, "P90 (nearest rank)")):
        vals = {s: percentile([rows[n][s] for n in names], q) for s in (*STAGES, "total")}
        tv = vals["total"]
        print(f"| **{label}** | " + " | ".join(f"{vals[s] * u:.3f}" for s in STAGES) + f" | **{tv * u:.3f}** | "
              f"{'under' if tv <= CEILING else 'OVER'} | {'under' if tv <= STRETCH else 'OVER'} |")

    print("\n### Share of the median-clip cost by stage (mean of per-clip shares)\n")
    shares = {s: sum(rows[n][s] / rows[n]["total"] for n in names) / len(names) for s in STAGES}
    for s in sorted(STAGES, key=lambda s: -shares[s]):
        print(f"- {s}: {shares[s] * 100:.1f}%  (median {percentile([rows[n][s] for n in names], 50) * u:.3f} m$)")

    print("\n### Sensitivity: miss rate × big model, median / P90 total (m$)\n")
    print("| miss rate | big = Sonnet 5.5 median | P90 | big = Opus 5.5 median | P90 |")
    print("|---|---|---|---|---|")
    for mr in (0.0, 0.1, 0.2, 0.5, 1.0):
        cells = []
        for big in ("sonnet_5_5", "opus_5_5"):
            tot = [price_clip(clips[n], a, e, miss_rate=mr, big=big)["total"] for n in names]
            cells += [f"{percentile(tot, 50) * u:.3f}", f"{percentile(tot, 90) * u:.3f}"]
        print(f"| {mr} | " + " | ".join(cells) + " |")

    print("\n### Client-side alternative (ASR + render on the user's device: cost to us = 0)\n")
    tot = [price_clip(clips[n], a, e, miss_rate=e["miss_rate"], on_device=True)["total"] for n in names]
    print(f"median {percentile(tot, 50) * u:.3f} m$, P90 {percentile(tot, 90) * u:.3f} m$")

    print("\n### Levers (median $ saved per export, from the same model)\n")
    base = [rows[n]["total"] for n in names]
    med = percentile(base, 50)
    lev = {
        "render on device (ffmpeg.wasm / native app)": [rows[n]["render"] for n in names],
        "ASR on device (whisper.cpp / platform STT)": [rows[n]["asr"] for n in names],
        "retention 30 d -> 7 d (source + cache + export)": [rows[n]["storage"] * (1 - 7 / 30) for n in names],
        "miss rate 0.2 -> 0.1 (more recipes / small-model retry before escalating)": [
            rows[n]["total"] - price_clip(clips[n], a, e, miss_rate=0.1)["total"] for n in names],
    }
    for k, v in sorted(lev.items(), key=lambda kv: -percentile(kv[1], 50)):
        print(f"- {k}: saves median {percentile(v, 50) * u:.3f} m$ ({percentile(v, 50) / med * 100:.0f}% of median)")

    print("\n### Token estimates (per clip)\n")
    print("| clip | transcript tok | understanding in/out | plan small in/out | plan big in/out |")
    print("|---|---|---|---|---|")
    for n in names:
        t = tokens(clips[n], e)
        print(f"| {n} | {t['transcript']:.0f} | {t['und_in']:.0f}/{t['und_out']:.0f} | "
              f"{t['plan_small_in']:.0f}/{t['plan_small_out']:.0f} | {t['plan_big_in']:.0f}/{t['plan_big_out']:.0f} |")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--only", action="append", default=[], help="clip file name (repeatable)")
    sub.add_parser("report")
    a = ap.parse_args()
    measure(a.only) if a.cmd == "measure" else report()


if __name__ == "__main__":
    main()
