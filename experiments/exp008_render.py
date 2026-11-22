"""EXP-008 instrument (H-0015): implements company/experiments/EXP-008.md §5.4 steps 1-9 exactly.

Run from the repo root:  .venv/bin/python experiments/exp008_render.py

The 10 strings are read programmatically from company/positions/04-creative/ARABIC_QA.md; the
expected fingerprints and tagged-text table are read programmatically from the LOCKED EXP-008.md.
The run-splitting rule (§5.3) is implemented here in code. This script never views, describes or
judges any image; it only records sizes (ffprobe) and hashes.

Exit code 0: all steps passed. Exit code 2: STOP (precondition fail, INVALID or instrument defect);
the reason is printed on stderr and the files written so far stay in render/exp008/.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTRUMENT = Path(__file__).resolve()
OUT_REL = "render/exp008"
OUT = ROOT / OUT_REL
CTRL_REL = f"{OUT_REL}/control"
EXP006_LOG_REL = "render/frames_check/render.log"
QA = ROOT / "company/positions/04-creative/ARABIC_QA.md"
PREREG = ROOT / "company/experiments/EXP-008.md"
RIGHTS = ROOT / "company/positions/05-assurance/DATA_RIGHTS.md"
IDS = [f"AR-{i:02d}" for i in range(1, 11)]

# §5.1 declared set
FONT = {
    "A": ("Noto Sans Arabic", "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
          "504d7407d86875acf7d04dfaa0fd7524d0b8797723bc4aa18022f29db25b0b6e", "RR-001"),
    "L": ("Noto Sans", "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
          "89c3c497f618fdaa0b2d1e98fef93582f28c71debd2c4a8cdf41f190ced2909d", "RR-011"),
}
DECLARED = {FONT["A"][1], FONT["L"][1]}
TAG = {"A": "{\\fnNoto Sans Arabic}", "L": "{\\fnNoto Sans}"}

# §5.3 Step A ranges (inclusive)
A_RANGES = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)]
L_RANGES = [(0x0021, 0x007E), (0x00A1, 0x024F), (0x2010, 0x2027), (0x2030, 0x205E)]
L_EXCLUDED = {0x00AD}
# U+061C ARABIC LETTER MARK lies inside the A range U+0600-U+06FF but is named explicitly in the §5.3
# X row; the explicit X example wins (fail loudly). It occurs in none of the 10 strings (§4 integrity).
A_EXCLUDED = {0x061C}

# §5.5 control
CTRL_RAW = "مرحبا " + "ก"
CTRL_CLASSES = ["A"] * 6 + ["L"]  # hand-specified assignment, bypasses §5.3 on purpose
CTRL_TEXT = "مرحبا " + TAG["L"] + "ก"
CTRL_EXPECT = (21, "2f344988a2bbdda1")
C0_EXPECT = ["U+0E01 not in NotoSans-Regular.ttf"]
C2_EXPECT = ["AR-05", "AR-08", "AR-10"]

ASS_TEMPLATE = (
    "[Script Info]\n"
    "ScriptType: v4.00+\n"
    "PlayResX: 1080\n"
    "PlayResY: 1920\n"
    "WrapStyle: 0\n"
    "ScaledBorderAndShadow: yes\n"
    "\n"
    "[V4+ Styles]\n"
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
    "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
    "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
    "Style: Default,Noto Sans Arabic,72,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
    "0,0,0,0,100,100,0,0,1,4,0,5,60,60,60,-1\n"
    "\n"
    "[Events]\n"
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,{text}\n"
)
DIALOGUE_PREFIX = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,"

ENV_COMMANDS = [
    "ffmpeg -version | head -3",
    "ffmpeg -hide_banner -filters | grep -w ass",
    "dpkg -l libass9 libharfbuzz0b libfribidi0 fonts-noto-core | grep ^ii",
    'fc-match "Noto Sans Arabic"',
    'fc-match -v "Noto Sans Arabic" | grep file',
    'fc-match "Noto Sans"',
    'fc-match -v "Noto Sans" | grep file',
    f"sha256sum {FONT['A'][1]} {FONT['L'][1]}",
    "sha256sum experiments/exp008_render.py",
    "uname -a",
    "nproc",
    "date -u +%Y-%m-%dT%H:%M:%SZ",
]

# §5.4 step 7 log checker regexes
RULE_A = re.compile(r"Glyph 0x[0-9a-f]+ not found", re.I)
RULE_B = re.compile(r"fontselect: \((.+), (\d+), (\d+)\) -> ([^,]+),")
RULE_B_NOFALLBACK = re.compile(r"fontselect: failed to find any fallback", re.I)
PREFIX = re.compile(r"^\[[^\]]* @ 0x[0-9a-f]+\] ")  # ffmpeg context prefix (pointer varies per run)


class Stop(Exception):
    pass


# ---------------------------------------------------------------- §5.3 run-splitting rule
def classify_cp(c: str) -> str:
    """Step A: class of one code point (A, L, S or X)."""
    o = ord(c)
    if o == 0x20:
        return "S"
    if o not in A_EXCLUDED and any(a <= o <= b for a, b in A_RANGES):
        return "A"
    if o not in L_EXCLUDED and any(a <= o <= b for a, b in L_RANGES):
        return "L"
    return "X"


def classify(s: str) -> list[str]:
    """Steps A+B: per-code-point class with spaces resolved. Raises ValueError on class X."""
    k = [classify_cp(c) for c in s]
    bad = [f"U+{ord(c):04X}" for c, x in zip(s, k, strict=True) if x == "X"]
    if bad:
        raise ValueError(f"class-X code point(s): {bad}")
    i = 0
    while i < len(k):
        if k[i] != "S":
            i += 1
            continue
        j = i
        while j < len(k) and k[j] == "S":
            j += 1
        left = k[i - 1] if i > 0 else None
        right = k[j] if j < len(k) else None
        v = left if (left is not None and right is not None and left == right) else "A"
        k[i:j] = [v] * (j - i)
        i = j
    return k


def tag(s: str, k: list[str]) -> str:
    """Step C: emit {\\fn...} tags at class changes, starting from A; never a trailing tag."""
    cur, out = "A", []
    for c, x in zip(s, k, strict=True):
        if x != cur:
            out.append(TAG[x])
            cur = x
        out.append(c)
    return "".join(out)


def split_runs(s: str) -> tuple[str, str, list[str]]:
    """Raw string -> (tagged text, runs string like 'A5 L13 A7', classes)."""
    k = classify(s)
    runs: list[list] = []
    for x in k:
        if runs and runs[-1][0] == x:
            runs[-1][1] += 1
        else:
            runs.append([x, 1])
    return tag(s, k), " ".join(f"{a}{n}" for a, n in runs), k


# ---------------------------------------------------------------- helpers
def fingerprint(s: str) -> tuple[int, str]:
    return len(s), hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def sha256_file(p: Path | str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def table_rows(path: Path) -> list[list[str]]:
    """Cells of markdown table rows whose first cell is an AR-xx id (only table padding stripped)."""
    rows = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        if re.match(r"^\| AR-\d\d \|", line):
            rows.append([c.strip(" ") for c in line.split("|")[1:-1]])
    return rows


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=ROOT).stdout


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def charset(path: str) -> set[int]:
    """Coverage source fixed by §5.4 step 3: fc-query --format='%{charset}' on the declared file."""
    faces = run(["fc-query", "--format=%{index}\n", path]).split()
    if len(faces) != 1:
        raise Stop(f"INVALID: fc-query reports {len(faces)} faces for {path}")
    toks = run(["fc-query", "--format=%{charset}", path]).split()
    if not toks:
        raise Stop(f"INVALID: fc-query returned no charset for {path}")
    cps: set[int] = set()
    for t in toks:
        a, _, b = t.partition("-")
        cps.update(range(int(a, 16), int(b or a, 16) + 1))
    return cps


def missing(s: str, k: list[str], cs: dict[str, set[int]]) -> list[str]:
    return [f"U+{ord(c):04X} not in {Path(FONT[x][1]).name}" for c, x in zip(s, k, strict=True) if ord(c) not in cs[x]]


def check_log(lines: list[str]) -> dict:
    """§5.4 step 7 on one log's lines: rule (a), rule (b), resolved files, fontselect lines."""
    a_hits, b_hits, files, fs_lines = [], [], set(), []
    for raw in lines:
        ln = PREFIX.sub("", raw)
        if RULE_A.search(ln):
            a_hits.append(ln)
        if "fontselect" in ln:
            fs_lines.append(ln)
        if RULE_B_NOFALLBACK.search(ln):
            b_hits.append(ln)
            continue
        if "fontselect:" in ln:
            m = RULE_B.search(ln)
            if " -> " not in ln or m is None or not m.group(4).strip():
                b_hits.append(ln)
                continue
            path = m.group(4)
            files.add(path)
            if path not in DECLARED:
                b_hits.append(ln)
    return {"flagged": bool(a_hits or b_hits), "rule_a": a_hits, "rule_b": b_hits,
            "files": sorted(files), "fontselect": fs_lines}


def attribute_exp006(lines: list[str]) -> dict[str, list[str]]:
    """Split the EXP-006 single log into per-string event groups by its 'Added subtitle file:' lines."""
    groups: dict[str, list[str]] = {}
    cur = None
    for ln in lines:
        m = re.search(r"Added subtitle file: '[^']*/(AR-\d\d)\.ass'", ln)
        if m:
            cur = m.group(1)
        if cur is not None:
            groups.setdefault(cur, []).append(ln)
    return groups


def render(ass_rel: str, png_rel: str, log_rel: str) -> None:
    """§5.4 step 8 command, from the repo root, stdout+stderr to the string's own log."""
    cmd = ["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i", "color=c=0x808080:s=1080x1920:r=30:d=1",
           "-vf", f"ass=filename={ass_rel}:shaping=complex,format=rgb24", "-frames:v", "1", png_rel]
    with open(ROOT / log_rel, "wb") as fh:
        r = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise Stop(f"ffmpeg exit {r.returncode} for {png_rel}")


def write_ass(path: Path, text: str) -> str:
    """Write the .ass file and return the Dialogue text read back from disk (checked by caller)."""
    write(path, ASS_TEMPLATE.format(text=text))
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise Stop(f"INVALID: {path.name} has BOM or CR")
    dlg = [ln for ln in raw.decode("utf-8").split("\n") if ln.startswith("Dialogue:")]
    if len(dlg) != 1:
        raise Stop(f"INVALID: {path.name} has {len(dlg)} Dialogue lines")
    body = dlg[0][len(DIALOGUE_PREFIX):]
    stripped = body.replace(TAG["A"], "").replace(TAG["L"], "")
    if any(c in stripped for c in "{}\\"):
        raise Stop(f"INVALID: {path.name} contains an override tag other than the two allowed")
    return body


# ---------------------------------------------------------------- procedure
def preconditions() -> None:
    rights = RIGHTS.read_text(encoding="utf-8").split("\n")
    for role in ("A", "L"):
        rr = FONT[role][3]
        rows = [ln for ln in rights if ln.startswith(f"| {rr} ")]
        if len(rows) != 1 or "pending" in rows[0] or "| Yes" not in rows[0] or "recorded" not in rows[0]:
            raise Stop(f"PRECONDITION 5.1.1 failed: {rr} not recorded / commercial use not Yes")
    for role in ("A", "L"):
        fam, path, sha, _ = FONT[role]
        files = re.findall(r'file: "([^"]+)"', run(["fc-match", "-v", fam]))
        if files != [path]:
            raise Stop(f"PRECONDITION 5.1.2 failed: fc-match {fam!r} -> {files}")
        if sha256_file(path) != sha:
            raise Stop(f"PRECONDITION 5.1.2 failed: sha256 mismatch for {path}")
    if OUT.exists() and any(OUT.iterdir()):
        raise Stop(f"PRECONDITION 5.1.3 failed: {OUT_REL}/ is not empty")
    if run(["git", "status", "--porcelain", "--", "render/frames_check"]).strip():
        raise Stop("PRECONDITION 5.1.3 failed: render/frames_check/ is modified")
    text = PREREG.read_text(encoding="utf-8")
    if "- **Lock:** LOCKED" not in text:
        raise Stop("PRECONDITION 5.1.4 failed: EXP-008 not LOCKED")
    if not re.search(r"^- Engineering \(feasibility.*\): engineering-lead, \d{4}-\d\d-\d\d", text, re.M) or \
       not re.search(r"^- Creative \(judging.*\): creative-lead, \d{4}-\d\d-\d\d", text, re.M):
        raise Stop("PRECONDITION 5.1.4 failed: consultation sign-offs not filled")


def main() -> int:
    preconditions()
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / CTRL_REL).mkdir(parents=True, exist_ok=True)

    # Step 1: environment + instrument hash
    instrument_sha = sha256_file(INSTRUMENT)
    env = []
    for cmd in ENV_COMMANDS:
        r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, cwd=ROOT)
        env.append(f"$ {cmd}\n{r.stdout}{r.stderr}\n")
    env.append(f"instrument experiments/exp008_render.py sha256 (step 1) = {instrument_sha}\n")
    write(OUT / "ENV.txt", "".join(env))

    # Step 2: strings, raw + tagged fingerprints
    qa = {r[0]: r[1] for r in table_rows(QA) if len(r) == 3}
    raw_tab = {r[0]: r for r in table_rows(PREREG) if len(r) == 5}
    tag_tab = {r[0]: r for r in table_rows(PREREG) if len(r) == 6}
    if sorted(qa) != IDS or sorted(raw_tab) != IDS or sorted(tag_tab) != IDS:
        raise Stop("INVALID: string tables incomplete")
    out, ok_all, items = [], True, {}
    for i in IDS:
        s = qa[i]
        try:
            tagged, runs, k = split_runs(s)
        except ValueError as e:
            raise Stop(f"INVALID: {i} {e}") from e
        n, h = fingerprint(s)
        tn, th = fingerprint(tagged)
        exp_t = tag_tab[i]
        exp_text = s if exp_t[1] == "unchanged (raw)" else exp_t[1].strip("`")
        ok = (
            s == raw_tab[i][1]
            and (n, h) == (int(raw_tab[i][3]), raw_tab[i][4])
            and runs == exp_t[2]
            and k.count("L") == int(exp_t[3])
            and (tn, th) == (int(exp_t[4]), exp_t[5])
            and tagged == exp_text
        )
        ok_all &= ok
        items[i] = (s, tagged, k)
        out.append(f"{i}  {'OK' if ok else 'MISMATCH'}  raw codepoints={n} sha256_16={h} "
                   f"(expected {raw_tab[i][3]} {raw_tab[i][4]})  runs={runs} (expected {exp_t[2]})  "
                   f"L={k.count('L')} (expected {exp_t[3]})  tagged codepoints={tn} sha256_16={th} "
                   f"(expected {exp_t[4]} {exp_t[5]})\n")
        for c, x in zip(s, k, strict=True):
            out.append(f"    U+{ord(c):04X}  {x}  {Path(FONT[x][1]).name}\n")
    out.append(f"ALL_MATCH={ok_all}\n")
    write(OUT / "strings_check.txt", "".join(out))
    if not ok_all:
        raise Stop("INVALID: fingerprint or tagged-text mismatch (§8); not rendering")

    # Step 3: coverage check; Step 4: C0
    cs = {"A": charset(FONT["A"][1]), "L": charset(FONT["L"][1])}
    cov, cov_ok = [], True
    for i in IDS:
        s, _, k = items[i]
        miss = missing(s, k, cs)
        cov_ok &= not miss
        cov.append(f"{i}  missing={miss}\n")
    cov.append(f"COVERAGE_OK={cov_ok}\n")
    c0 = missing(CTRL_RAW, CTRL_CLASSES, cs)
    c0_ok = c0 == C0_EXPECT
    cov.append(f"\n# Control C0 (CTRL-01 hand assignment, not one of the 10)\nCTRL-01  missing={c0}  "
               f"expected={C0_EXPECT}  C0_OK={c0_ok}\n")
    write(OUT / "coverage_check.txt", "".join(cov))
    if not cov_ok:
        raise Stop("INVALID: COVERAGE_OK=False; not rendering")
    if not c0_ok:
        raise Stop("INSTRUMENT DEFECT: C0 did not report exactly U+0E01")

    lc = []

    def log_section(name: str, res: dict) -> None:
        lc.append(f"== {name}  FLAGGED={res['flagged']}  rule_a={len(res['rule_a'])}  "
                  f"rule_b={len(res['rule_b'])}  files={[Path(f).name for f in res['files']]}\n")
        for ln in res["fontselect"]:
            lc.append(f"    fontselect | {ln}\n")
        for ln in res["rule_a"]:
            lc.append(f"    rule(a)    | {ln}\n")
        for ln in res["rule_b"]:
            lc.append(f"    rule(b)    | {ln}\n")

    # Step 5: C2 on the EXP-006 log (read as text only)
    groups = attribute_exp006((ROOT / EXP006_LOG_REL).read_text(encoding="utf-8").split("\n"))
    lc.append(f"# Control C2: {EXP006_LOG_REL}, events attributed by 'Added subtitle file:' lines\n")
    c2_flagged = []
    for i in IDS:
        res = check_log(groups.get(i, []))
        log_section(f"C2 {i}", res)
        if res["flagged"]:
            c2_flagged.append(i)
    c2_ok = c2_flagged == C2_EXPECT
    lc.append(f"C2 flagged={c2_flagged} expected={C2_EXPECT} C2_OK={c2_ok}\n\n")
    if not c2_ok:
        write(OUT / "logcheck.txt", "".join(lc))
        raise Stop("INSTRUMENT DEFECT: C2 did not flag exactly AR-05, AR-08, AR-10")

    # Step 6: C1 known-fallback control render
    if fingerprint(CTRL_TEXT) != CTRL_EXPECT:
        raise Stop(f"INSTRUMENT DEFECT: CTRL-01 text fingerprint {fingerprint(CTRL_TEXT)} != {CTRL_EXPECT}")
    if write_ass(ROOT / CTRL_REL / "CTRL-01.ass", CTRL_TEXT) != CTRL_TEXT:
        raise Stop("INSTRUMENT DEFECT: CTRL-01 Dialogue read-back differs")
    render(f"{CTRL_REL}/CTRL-01.ass", f"{CTRL_REL}/CTRL-01.png", f"{CTRL_REL}/CTRL-01.log")
    c1 = check_log((ROOT / CTRL_REL / "CTRL-01.log").read_text(encoding="utf-8").split("\n"))
    lc.append("# Control C1: render/exp008/control/CTRL-01.log (never judged, never viewed)\n")
    log_section("C1 CTRL-01", c1)
    c1_ok = bool(c1["rule_a"]) and bool(c1["fontselect"])
    lc.append(f"C1 rule_a_fired={bool(c1['rule_a'])} rule_b_fired={bool(c1['rule_b'])} "
              f"fontselect_visible={bool(c1['fontselect'])} C1_OK={c1_ok}\n")
    ctrl_ok = c0_ok and c1_ok and c2_ok
    lc.append(f"CTRL_OK={ctrl_ok}\n\n")
    if not ctrl_ok:
        write(OUT / "logcheck.txt", "".join(lc))
        raise Stop("INSTRUMENT DEFECT: C1 control not detected")

    # Step 8: render the 10 strings, then step 7 checker on each log
    lc.append("# Real strings AR-01..AR-10 (one log each)\n")
    log_ok = True
    for i in IDS:
        s, tagged, k = items[i]
        if write_ass(OUT / f"{i}.ass", tagged) != tagged:
            raise Stop(f"INVALID: {i} Dialogue read-back differs from tagged text")
        render(f"{OUT_REL}/{i}.ass", f"{OUT_REL}/{i}.png", f"{OUT_REL}/{i}.log")
        res = check_log((OUT / f"{i}.log").read_text(encoding="utf-8").split("\n"))
        want = sorted({FONT["A"][1]} | ({FONT["L"][1]} if "L" in k else set()))
        clean = not res["flagged"] and res["files"] == want
        log_ok &= clean
        log_section(i, res)
        lc.append(f"    {i} CLEAN={clean} expected_files={[Path(f).name for f in want]}\n")
    lc.append(f"LOG_OK={log_ok}\n")
    write(OUT / "logcheck.txt", "".join(lc))

    # Step 9: ffprobe, instrument hash, SHA256SUMS
    probe, size_ok = [], True
    for i in IDS:
        r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                 "stream=codec_name,width,height,pix_fmt", "-of", "csv=p=0", f"{OUT_REL}/{i}.png"]).strip()
        size_ok &= r == "png,1080,1920,rgb24"
        probe.append(f"{OUT_REL}/{i}.png  {r}\n")
    instrument_sha2 = sha256_file(INSTRUMENT)
    hash_ok = instrument_sha2 == instrument_sha
    probe.append(f"PNG_OK={size_ok}\ninstrument sha256 step1={instrument_sha} step9={instrument_sha2} "
                 f"INSTRUMENT_UNCHANGED={hash_ok}\n")
    write(OUT / "ffprobe.txt", "".join(probe))
    sums = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS":
            sums.append(f"{sha256_file(p)}  {p.relative_to(ROOT).as_posix()}\n")
    write(OUT / "SHA256SUMS", "".join(sums))

    print(f"COVERAGE_OK={cov_ok} CTRL_OK={ctrl_ok} LOG_OK={log_ok} PNG_OK={size_ok} "
          f"INSTRUMENT_UNCHANGED={hash_ok}")
    if not (log_ok and size_ok and hash_ok):
        raise Stop("INVALID: see logcheck.txt / ffprobe.txt")
    print("done:", OUT_REL)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        print(f"STOP: {e}", file=sys.stderr)
        sys.exit(2)
