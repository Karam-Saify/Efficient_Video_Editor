"""EXP-006 render step (H-0006): follows company/experiments/EXP-006.md §5 exactly.

Run from the repo root:  .venv/bin/python experiments/exp006_render.py

Strings are read programmatically from company/positions/04-creative/ARABIC_QA.md and
checked against the fingerprint table in EXP-006.md §4 before anything is rendered.
This script never looks at or judges the images; it only records sizes and hashes.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_REL = "render/frames_check"
OUT = ROOT / OUT_REL
QA = ROOT / "company/positions/04-creative/ARABIC_QA.md"
PREREG = ROOT / "company/experiments/EXP-006.md"
RIGHTS = ROOT / "company/positions/05-assurance/DATA_RIGHTS.md"
IDS = [f"AR-{i:02d}" for i in range(1, 11)]

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
    "uname -a",
    "nproc",
    "date -u +%Y-%m-%dT%H:%M:%SZ",
]


def die(msg: str) -> None:
    print(f"STOP: {msg}", file=sys.stderr)
    sys.exit(2)


def table_rows(path: Path) -> list[list[str]]:
    """Rows of markdown tables whose first cell is an AR-xx id. Cells lose only the
    single table-padding spaces (strip(' ')), nothing else, and are not normalised."""
    rows = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        if re.match(r"^\| AR-\d\d \|", line):
            cells = line.split("|")[1:-1]
            rows.append([c.strip(" ") for c in cells])
    return rows


def fingerprint(s: str) -> tuple[int, str]:
    return len(s), hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    # 5.1 preconditions
    rr = [ln for ln in RIGHTS.read_text(encoding="utf-8").split("\n") if ln.startswith("| RR-001 ")]
    if len(rr) != 1 or "pending" in rr[0] or "Yes" not in rr[0]:
        die("5.1.1 RR-001 not recorded")
    fm = subprocess.run(["fc-match", "Noto Sans Arabic"], capture_output=True, text=True).stdout
    if not fm.startswith("NotoSansArabic-Regular.ttf"):
        die(f"5.1.2 fc-match resolved {fm!r}")
    if OUT.exists() and any(OUT.iterdir()):
        die(f"5.1.3 {OUT_REL}/ is not empty")
    OUT.mkdir(parents=True, exist_ok=True)

    # Step 1: environment
    with open(OUT / "ENV.txt", "w", encoding="utf-8", newline="\n") as f:
        for cmd in ENV_COMMANDS:
            r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, cwd=ROOT)
            f.write(f"$ {cmd}\n{r.stdout}{r.stderr}\n")

    # Step 2: strings, fingerprints, .ass files
    qa = {r[0]: r[1] for r in table_rows(QA) if len(r) == 3}
    pre = {r[0]: r for r in table_rows(PREREG) if len(r) == 5}
    if sorted(qa) != IDS or sorted(pre) != IDS:
        die(f"string tables incomplete: QA={sorted(qa)} PREREG={sorted(pre)}")
    lines, ok_all = [], True
    for i in IDS:
        s = qa[i]
        ass_path = OUT / f"{i}.ass"
        with open(ass_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(ASS_TEMPLATE.format(text=s))
        raw = ass_path.read_bytes()
        dlg = [ln for ln in raw.decode("utf-8").split("\n") if ln.startswith("Dialogue:")]
        text = dlg[0][len(DIALOGUE_PREFIX) :]
        n, h = fingerprint(text)
        exp_n, exp_h = int(pre[i][3]), pre[i][4]
        ok = (
            n == exp_n
            and h == exp_h
            and text == s == pre[i][1]
            and len(dlg) == 1
            and not raw.startswith(b"\xef\xbb\xbf")
            and b"\r" not in raw
            and not any(c in text for c in "{}\\")
        )
        ok_all &= ok
        lines.append(
            f"{i}  {'OK' if ok else 'MISMATCH'}  codepoints={n} (expected {exp_n})  "
            f"sha256_16={h} (expected {exp_h})  same_as_prereg_text={s == pre[i][1]}\n"
            f"    codepoints: {' '.join(f'U+{ord(c):04X}' for c in text)}\n"
            f"    utf8_hex:   {text.encode('utf-8').hex()}\n"
        )
    lines.append(f"ALL_MATCH={ok_all}\n")
    (OUT / "strings_check.txt").write_text("".join(lines), encoding="utf-8", newline="\n")
    if not ok_all:
        die("fingerprint mismatch (invalidating per §8); not rendering")

    # Step 3: renders (exact §5.3 command, run from repo root)
    with open(OUT / "render.log", "w", encoding="utf-8", newline="\n") as log:
        for i in IDS:
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=0x808080:s=1080x1920:r=30:d=1",
                "-vf",
                f"ass=filename={OUT_REL}/{i}.ass:shaping=complex,format=rgb24",
                "-frames:v",
                "1",
                f"{OUT_REL}/{i}.png",
            ]
            log.write(f"=== {i} $ {' '.join(cmd)}\n")
            log.flush()
            r = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            log.write(f"=== {i} exit={r.returncode}\n")
            if r.returncode != 0:
                die(f"ffmpeg failed for {i}")

    # Step 4: warnings + checksums
    log_text = (OUT / "render.log").read_text(encoding="utf-8")
    pat = re.compile(r"fallback|glyph .*not found|selecting one more font", re.I)
    warn = [ln for ln in log_text.split("\n") if pat.search(ln)]
    print("font-fallback / glyph warnings:", warn or "none")
    sums = []
    for ext in ("png", "ass"):
        for i in IDS:
            p = OUT / f"{i}.{ext}"
            sums.append(f"{sha256_file(p)}  {OUT_REL}/{p.name}\n")
    (OUT / "SHA256SUMS").write_text("".join(sums), encoding="utf-8", newline="\n")
    print("done:", OUT_REL)


if __name__ == "__main__":
    main()
