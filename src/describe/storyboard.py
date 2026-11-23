"""Static, self-contained storyboard (one HTML file per video). Works offline: keyframes are inlined as data URIs,
CSS and JS are inline, and a Content-Security-Policy forbids every network fetch. Rendered server-side, so the
same record always gives the same bytes; JS only collects edits and downloads them as JSON (Export corrections).
"""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import Any

from src.common import read_json
from src.manifest import sha256_file

ROLE_NAMES = {
    "hook": "Hook · الخطّاف", "product_intro": "Product intro · تقديم المنتج", "demo": "Demo · عرض",
    "proof": "Proof · دليل", "cta": "Call to action · دعوة للشراء", "other": "Other · غير ذلك",
}
CSP = "default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'"

CSS = """
:root{--bg:#fafaf8;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#deddd6;--warn:#fff4d6;--accent:#1f5fbf}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;
--card:#22221f;--line:#3a3a35;--warn:#3d3214;--accent:#7fb0ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px}h1{font-size:20px;margin:0 0 4px}.muted{color:var(--muted)}
.warn{background:var(--warn);padding:10px 12px;border-radius:8px;margin:12px 0}
.scene,.seg{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;margin:12px 0}
.scene{display:grid;grid-template-columns:160px 1fr;gap:12px}.scene img{width:160px;border-radius:6px}
.noimg{width:160px;height:120px;border:1px dashed var(--line);border-radius:6px;
display:flex;align-items:center;justify-content:center}
textarea,select,input[type=text]{width:100%;font:inherit;color:inherit;background:transparent;
border:1px solid var(--line);border-radius:6px;padding:6px}
label{display:block;font-size:13px;color:var(--muted);margin-top:6px}
button{font:inherit;padding:10px 16px;border-radius:8px;border:0;background:var(--accent);color:#fff;cursor:pointer}
.bar{position:sticky;bottom:0;background:var(--bg);padding:12px 0;border-top:1px solid var(--line)}
@media (max-width:560px){.scene{grid-template-columns:1fr}.scene img,.noimg{width:100%}}
"""

JS = """
function v(el){return el.value}
document.getElementById('export').addEventListener('click',function(){
  var meta=JSON.parse(document.getElementById('meta').textContent);
  var out={format:'storyboard-corrections/0.1',video_id:meta.video_id,record_sha256:meta.record_sha256,
           corrected_on:new Date().toISOString().slice(0,10),scenes:[],segments:[]};
  document.querySelectorAll('.scene').forEach(function(s){
    var d=s.querySelector('.desc'),r=s.querySelector('.role'),c=s.querySelector('.confirm');
    if(c.checked||v(d)!==d.dataset.orig||v(r)!==r.dataset.orig){
      out.scenes.push({scene_id:Number(s.dataset.scene),description:v(d),role:v(r)});}});
  document.querySelectorAll('.seg').forEach(function(s){
    var t=s.querySelector('.text'),l=s.querySelector('.lang'),c=s.querySelector('.confirm');
    if(c.checked||v(t)!==t.dataset.orig||v(l)!==l.dataset.orig){
      out.segments.push({segment_id:Number(s.dataset.seg),text:v(t),language:v(l).trim().toLowerCase()});}});
  if(!out.scenes.length&&!out.segments.length){alert('Nothing changed or confirmed yet. / لم يتغيّر شيء بعد.');return;}
  var blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='corrections-'+meta.video_id+'.json';document.body.appendChild(a);a.click();a.remove();
});
"""


def _e(s: Any) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _secs(t_ms: int) -> str:
    return f"{t_ms // 1000}.{(t_ms % 1000) // 100}"


def _img(base: Path, rel: str) -> str:
    data = base64.b64encode((base / rel).read_bytes()).decode("ascii")
    return f'<img alt="keyframe" src="data:image/jpeg;base64,{data}">'


def render(rec: dict[str, Any], record_sha256: str, base: Path) -> str:
    flags = rec["audio"]["flags"]
    parts = [
        "<!doctype html>", '<html lang="ar" dir="ltr"><head><meta charset="utf-8">',
        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>Storyboard {_e(rec['video_id'])}</title><style>{CSS}</style></head><body><main>",
        f"<h1>Storyboard · {_e(rec['video_id'])}</h1>",
        f'<p class="muted">{_secs(rec["media"]["duration_ms"])} s · {len(rec["scenes"])} scenes · '
        f'language {_e(rec["transcript"]["language"]["value"])} · rights {_e(rec["rights_id"])}</p>',
        "<p>Check each scene. Fix the description or role if it is wrong, or tick <b>Correct</b> if it is right. "
        "Then press <b>Export corrections</b> and send the file back.<br>"
        '<span dir="rtl">راجع كل مشهد. صحّح الوصف أو الدور إذا كان خطأ، أو اختر <b>صحيح</b> إذا كان صحيحاً. '
        "ثم اضغط <b>تصدير التصحيحات</b> وأرسل الملف.</span></p>",
    ]
    if "ASR_SUSPICIOUS" in flags:
        parts.append('<p class="warn">Speech was detected but the transcript has very few words: the automatic '
                     'transcript is probably wrong. Please type what is said. <span dir="rtl">يوجد كلام لكن '
                     "النص الآلي شبه فارغ، على الأرجح خطأ. اكتب ما يُقال من فضلك.</span></p>")
    base_dir = base
    for sc in rec["scenes"]:
        img = (_img(base_dir, sc["keyframes"][0]["file"]) if sc["keyframes"]
               else '<div class="noimg muted">no frame</div>')
        desc = sc["description"]["value"] or ""
        role = sc["role"]["value"]
        opts = "".join(f'<option value="{k}"{" selected" if k == role else ""}>{_e(n)}</option>'
                       for k, n in ROLE_NAMES.items())
        done = " (verified)" if sc["role"]["label_origin"] == "human_verified" else ""
        parts.append(
            f'<section class="scene" data-scene="{sc["id"]}">{img}<div>'
            f'<b>Scene {sc["id"]}</b> <span class="muted">{_secs(sc["start_ms"])}–{_secs(sc["end_ms"])} s{done}</span>'
            f'<label>Description · الوصف</label><textarea class="desc" dir="auto" rows="2" maxlength="2000" '
            f'data-orig="{_e(desc)}">{_e(desc)}</textarea>'
            f'<label>Role · الدور (suggested by rules)</label>'
            f'<select class="role" data-orig="{_e(role)}">{opts}</select>'
            '<label><input type="checkbox" class="confirm"> Correct · صحيح</label></div></section>'
        )
    parts.append("<h2>Transcript · النص</h2>")
    if not rec["transcript"]["segments"]:
        parts.append('<p class="muted">The automatic transcript is empty. This does not mean nobody speaks.</p>')
    for sg in rec["transcript"]["segments"]:
        t, lang = sg["text"]["value"] or "", sg["language"]["value"]
        parts.append(
            f'<div class="seg" data-seg="{sg["id"]}">'
            f'<span class="muted">{_secs(sg["start_ms"])}–{_secs(sg["end_ms"])} s</span>'
            f'<textarea class="text" dir="auto" rows="2" maxlength="2000" data-orig="{_e(t)}">{_e(t)}</textarea>'
            f'<label>Language code (ar, en, fr…)</label><input type="text" class="lang" maxlength="3" '
            f'data-orig="{_e(lang)}" value="{_e(lang)}">'
            '<label><input type="checkbox" class="confirm"> Correct · صحيح</label></div>'
        )
    meta = json.dumps({"video_id": rec["video_id"], "record_sha256": record_sha256}, sort_keys=True)
    parts += [
        '<div class="bar"><button id="export" type="button">Export corrections · تصدير التصحيحات</button></div>',
        f'</main><script type="application/json" id="meta">{meta.replace("<", "\\u003c")}</script>',
        f"<script>{JS}</script></body></html>",
    ]
    return "\n".join(parts) + "\n"


def write_storyboard(record_path: Path, out: Path) -> Path:
    rec = read_json(record_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rec, sha256_file(record_path), record_path.parent.parent), encoding="utf-8")
    return out
