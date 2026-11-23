# H-0028 Recipes: editorial content of 12 recipes (creative-lead, 2026-11-23)
Content spec only (no code, no schema). Engineering formalises in H-0029. Basis: ADR-0007..0010, `docs/CAPABILITIES.md`, `src/edit/ops.py`, `src/presets.py`, `company/positions/04-creative/STYLE_GUIDE.md`. No asset is used, so no rights record is touched.

## 0. Ground rules that apply to every recipe
**What today's ops can do (checked in `src/edit/ops.py` / `src/presets.py`):** `trim` (keep ONE output window), `delete_words` (cut words out), `set_duration` (cut silence longest-first, then the tail), `add_zoom` (instant punch-in, scale 1.0-2.0, no ease, captions not zoomed), `set_caption_style` (ONE preset for ALL captions: `clean` white/bottom third, `bold_box` white on box/bottom third, `hook` large yellow/upper third).
**What today's ops cannot do (so every recipe inherits it):** reorder or splice shots; style captions per beat; insert on-screen text that was not spoken (captions are rebuilt from ASR words); music/SFX (`tracks.audio` is UNSUPPORTED_FIELD); b-roll; transitions; stickers; speed ramps; zoom easing; captions on a source with no speech (`set_caption_style` fails with E_OP_PRESET "no captions").
**Tiers (the honest count):**
- **A = fully buildable.** Every beat, the hook rule and the pacing are achievable with today's ops. "Needs" are optional enhancements only.
- **B = core buildable, degraded.** A watchable version exists with today's ops, but a named required piece (reorder, overlay, per-beat style) is missing, so it will look weaker than the recipe intends.
- **C = not worth building yet.** Expressible only as trim + zoom with no text; not a product.
**Language behaviour (ADR-0010), common to all.** Captions are never translated or "corrected": the ASR words are kept, so Lebanese stays Lebanese (never normalised to MSA). Each caption's direction follows its first strong character (ASS Encoding -1). Chunking: <= ~12 words and <= 2 lines on screen. Target speech density after tightening is written for English; apply x0.95 for ar and x1.05 for fr. **These multipliers are uncalibrated guesses: the dev clips are English, I have no Arabic or French timing data (OPEN Q2).** A mixed line (ar with an en/fr word, or digits) renders in the EXP-008 pair, but EXP-008-results.md recorded a Sev-2 font-switch defect (Latin/digit glyphs about 1.6x the alef height). Until the per-script size fix passes, no recipe may put a mixed-script line in the golden set.
**Hook, universal:** the first 1.5 s must carry a claim, question, number or visible payoff; the first word starts within 0.3 s of frame 0 (`set_duration` leaves 120 ms pad, so this holds after tightening). No greeting or throat-clearing in the first 2 s: cut it with `delete_words`.
**Safe zone:** presets already sit in the bottom third (clean, bold_box) or upper third (hook); the style guide wants captions between 18% and 72% of height and nothing in the right 12%. I have not measured the presets against this: OPEN Q3.

## 1. Index
| id | name | niche -> goal | caption preset | tier |
|---|---|---|---|---|
| R01 | One-tip talking head | coaches, consultants, educators -> authority + follows | clean | A |
| R02 | Product demo | e-commerce, gadgets, beauty -> purchase intent | bold_box | B |
| R03 | Testimonial | clinics, courses, services -> trust + leads | clean | A |
| R04 | Before/after reveal | renovation, beauty, fitness -> proof + shares | bold_box | B |
| R05 | Listicle (N things) | finance, education, fitness -> saves + follows | bold_box | B |
| R06 | Event / offer promo | restaurants, retail, salons -> footfall + bookings | bold_box | B |
| R07 | Behind the scenes | makers, cafes, studios -> relatability + follows | clean | A |
| R08 | FAQ answer | clinics, lawyers, real estate -> search-like trust + leads | bold_box | A |
| R09 | Story hook | founders, personal brands -> watch time + follows | clean | B |
| R10 | Trend format | creators, brands riding a format -> reach | hook | B |
| R11 | Music-only promo | venues, product reels, sports -> reach | none possible | C |
| R12 | Bilingual ar/en | education, tech, expat services -> reach in two audiences | bold_box | B |

Tier count: **A = 4 (R01, R03, R07, R08), B = 7, C = 1.**

## 2. Shared params (typed; each recipe lists its defaults and ranges)
| name | type | creator's words | maps to |
|---|---|---|---|
| length_s | int (s) | "How long" | `set_duration` |
| cut_fillers | bool | "Remove ums and pauses" | `delete_words` + `set_duration` |
| punch_in_every_s | float (s) | "How often to zoom in" | `add_zoom` spacing (style guide: <= 1 per 3 s) |
| punch_in_strength | float | "How strong the zoom" | `add_zoom` scale (style guide 1.05-1.20) |
| caption_look | enum {clean, bold_box, hook} | "Caption style" | `set_caption_style` |
| start_at_s | float (s) | "Start from this moment" | `trim` start |

## 3. Recipes
Each block is one table row, with the 11 brief columns as fields. Shares sum to 100 % in every recipe.

### R01 One-tip talking head (tier A)
- **Use-case:** coach / consultant / educator; goal: authority and follows.
- **Beats (share):** Hook claim 10 | Tip body 65 | Recap 15 | CTA line 10 (=100).
- **Hook rule:** begin at the sentence that states the benefit or the mistake; delete any greeting in the first 2 s; first caption on screen at <= 0.3 s.
- **Pacing (en base):** hook 170-190 wpm; body 150-170 wpm; recap 150 wpm; CTA 130 wpm. Cut interval: tighten silence everywhere, no beat holds dead air > 0.4 s.
- **Captions:** clean. **Sound:** wanted: speech + soft music bed -18 to -22 dB ducked; available: speech only.
- **Params:** length_s:int=35 [20-60]; cut_fillers:bool=true; punch_in_every_s:float=4 [3-8]; punch_in_strength:float=1.10 [1.05-1.20]; caption_look:enum=clean.
- **Language:** ar: same shape, x0.95 pace, hook caption RTL; en/fr: same; mixed: keep the brand/term in its own script, see mixed-line gate above.
- **Principles:** P-HOOK-3S, P-MUTED-CAPTION, P-ZOOM-RHYTHM.
- **Needs (optional, none blocks):** music bed (audio track); hook-style caption on the first beat only (per-beat style); keyword highlight (`emphasis`).

### R02 Product demo (tier B)
- **Use-case:** e-commerce, gadgets, beauty; goal: purchase intent.
- **Beats:** Problem/hook 15 | Demo 50 | Result 20 | Price + CTA 15 (=100).
- **Hook rule:** first line names the problem or the result ("done in 10 seconds"), not the product name.
- **Pacing:** hook 170 wpm; demo 140-160 wpm with a punch-in at each new action; result 150 wpm; CTA 130 wpm. Cut interval in demo: 3-5 s.
- **Captions:** bold_box. **Sound:** wanted: speech + whoosh/click SFX + music; available: speech only.
- **Params:** length_s:int=30 [15-45]; cut_fillers:bool=true; punch_in_every_s:float=3 [3-6]; punch_in_strength:float=1.15 [1.05-1.20]; caption_look:enum=bold_box.
- **Language:** ar/en/fr: spoken product names stay as spoken (Latin brand inside Arabic is a mixed line); price digits come from ASR and must be eyeballed by Arabic QA.
- **Principles:** P-HOOK-3S, P-SHOW-DONT-TELL, P-CTA-ONE.
- **Needs:** product close-up inserts (b-roll/second shot); price + CTA text card (text overlay, because captions only show spoken words); SFX; per-beat caption style.

### R03 Testimonial (tier A)
- **Use-case:** clinic, course, service business; goal: trust and leads.
- **Beats:** Result hook 15 | Problem before 25 | Turning point 30 | Outcome + recommendation 30 (=100).
- **Hook rule:** start at the customer's most specific outcome sentence (a number, a duration, a named change). If none exists in the first 10 s, the recipe misses (log to RECIPE_BACKLOG).
- **Pacing:** 130-150 wpm throughout; keep natural pauses (do NOT cut fillers by default: the human voice is the proof). Cut interval 6-10 s; zoom only at the turning point.
- **Captions:** clean. **Sound:** wanted: speech only or very quiet bed; available: speech.
- **Params:** length_s:int=40 [25-60]; cut_fillers:bool=false; punch_in_every_s:float=8 [3-12]; punch_in_strength:float=1.08 [1.05-1.15]; caption_look:enum=clean.
- **Language:** dialect fidelity matters most here: a customer speaking Lebanese is shown in Lebanese spelling; never swap in MSA words. fr/en: same.
- **Principles:** P-SOCIAL-PROOF-SPECIFIC, P-MUTED-CAPTION, P-ONE-IDEA.
- **Needs (optional):** name/title lower third (text overlay); star/logo card.

### R04 Before/after reveal (tier B)
- **Use-case:** renovation, beauty, fitness; goal: proof and shares.
- **Beats:** Before 35 | Build/process 25 | Reveal 30 | CTA 10 (=100).
- **Hook rule:** the first 1.5 s must show or state the contrast ("this became this"). With today's ops the source must be one continuous take where both states appear; the recipe cannot show the "after" first.
- **Pacing:** before 140 wpm or silent; build 3-4 s cut interval; reveal: one punch-in 1.20 for 0.8 s at the 65 % mark; CTA 130 wpm.
- **Captions:** bold_box. **Sound:** wanted: music riser then drop at the reveal; available: none.
- **Params:** length_s:int=25 [15-40]; start_at_s:float=0 [0-source length]; punch_in_strength:float=1.20 [1.05-1.20]; caption_look:enum=bold_box.
- **Language:** if the take is silent, captions do not exist (see C-grade note in R11); ar/en/fr identical otherwise.
- **Principles:** P-CONTRAST-REVEAL, P-HOOK-3S, P-PAYOFF-END.
- **Needs (required):** two-source or reordered shots (after-first hook); transition/wipe; "قبل / بعد" label overlay; music riser.

### R05 Listicle, N things (tier B)
- **Use-case:** finance, education, fitness; goal: saves and follows.
- **Beats:** Promise hook 12 | N items sharing 75 equally (75/N each) | Close + CTA 13 (=100).
- **Hook rule:** the number and the payoff in the first sentence ("3 mistakes that cost you X"); item count in the hook must equal item_count.
- **Pacing:** hook 175 wpm; items 150-170 wpm, one punch-in at the start of each item (every 3-6 s); close 140 wpm. Item cut interval: one beat per item.
- **Captions:** bold_box. **Sound:** wanted: tick SFX per item; available: none.
- **Params:** item_count:int=3 [2-7]; length_s:int=35 [20-60]; cut_fillers:bool=true; punch_in_strength:float=1.10 [1.05-1.20]; caption_look:enum=bold_box.
- **Language:** ar numbers in the hook come from ASR (word or digit); do not rewrite them. mixed: fine if no Latin digit/word sits mid-RTL line until the size fix passes.
- **Principles:** P-LIST-COUNT, P-HOOK-3S, P-MUTED-CAPTION.
- **Needs (required for full effect):** "1 / 2 / 3" number badges (text overlay); item transitions; SFX. Today the source must already be spoken in item order (no reorder).

### R06 Event / offer promo (tier B)
- **Use-case:** restaurant, retail, salon; goal: footfall and bookings.
- **Beats:** Offer hook 15 | Details (what/when/where) 45 | Urgency 20 | CTA 20 (=100).
- **Hook rule:** lead with the offer itself ("50 % until Friday"); never open with the business name.
- **Pacing:** hook 175 wpm; details 150 wpm with a punch-in on the date/price word; urgency 160 wpm; CTA 130 wpm and held >= 2 s.
- **Captions:** bold_box. **Sound:** wanted: upbeat music + sting; available: none.
- **Params:** length_s:int=25 [15-40]; cut_fillers:bool=true; punch_in_every_s:float=3 [3-6]; punch_in_strength:float=1.15 [1.05-1.20]; caption_look:enum=bold_box.
- **Language:** dates, prices, addresses are the highest-risk strings: Arabic QA checks digit shaping and order on every one; keep ASR spelling, never convert digits silently.
- **Principles:** P-HOOK-3S, P-CTA-ONE, P-URGENCY-SPECIFIC.
- **Needs (required):** date/price/place end card (text overlay: captions only show what was said); music; countdown sticker.

### R07 Behind the scenes (tier A)
- **Use-case:** maker, cafe, studio; goal: relatability and follows.
- **Beats:** Curiosity hook 12 | Process 63 | Human moment 15 | Soft CTA 10 (=100).
- **Hook rule:** a "you never see this" or a surprising fact in the first sentence; no intro.
- **Pacing:** loose 130-160 wpm; cut interval 5-8 s; keep ambient pauses up to 0.8 s (set_duration only removes gaps longest-first, so use a generous length_s).
- **Captions:** clean. **Sound:** wanted: ambient + light music; available: source audio.
- **Params:** length_s:int=35 [20-60]; cut_fillers:bool=false; punch_in_every_s:float=6 [3-12]; punch_in_strength:float=1.06 [1.05-1.15]; caption_look:enum=clean.
- **Language:** casual dialect is the point; leave spelling as spoken, including colloquial forms.
- **Principles:** P-AUTHENTIC-TONE, P-HOOK-3S, P-PAYOFF-END.
- **Needs (optional):** time-lapse/speed ramp; music; b-roll.

### R08 FAQ answer (tier A when the question is spoken)
- **Use-case:** clinic, lawyer, real-estate, telecom; goal: search-like trust and leads.
- **Beats:** Question 12 | Short answer 38 | Reason or example 35 | Next step 15 (=100).
- **Hook rule:** the question is the first caption, within 0.5 s, then the answer's first sentence is the verdict (yes / no / a number). If the speaker never says the question, the recipe needs a title overlay and drops to tier B.
- **Pacing:** question 150 wpm; answer 145-160 wpm; reason 140-155 wpm; next step 130 wpm. Zoom once at the verdict.
- **Captions:** bold_box. **Sound:** speech only; available: speech.
- **Params:** length_s:int=30 [20-50]; cut_fillers:bool=true; punch_in_strength:float=1.10 [1.05-1.20]; caption_look:enum=bold_box.
- **Language:** question and answer in the same language as spoken; if the question is Arabic and a term is Latin, mixed-line gate applies.
- **Principles:** P-Q-FIRST, P-ANSWER-FIRST, P-MUTED-CAPTION.
- **Needs (optional):** question title card overlay (only required when the question is unspoken); keyword highlight.

### R09 Story hook (tier B)
- **Use-case:** founder, personal brand; goal: watch time and follows.
- **Beats:** Cold-open peak line 10 | Setup 30 | Escalation 30 | Twist/payoff 20 | Loop/CTA 10 (=100).
- **Hook rule:** open on the most intriguing line. Today `trim` can only start the video at that line (start_at_s); it cannot lift the peak line to the front and then replay the setup. So this runs as "start at the intrigue" only.
- **Pacing:** setup 140 wpm; escalation accelerates 150 -> 175 wpm, cut interval shrinks 6 s -> 3 s; twist: a 0.4 s pause then 140 wpm; loop line echoes the hook words.
- **Captions:** clean. **Sound:** wanted: tension bed then silence at the twist; available: none.
- **Params:** length_s:int=45 [30-60]; start_at_s:float=0 [0-source length]; cut_fillers:bool=true; punch_in_every_s:float=5 [3-8]; punch_in_strength:float=1.12 [1.05-1.20]; caption_look:enum=clean.
- **Language:** ar storytelling keeps dialect; do not move to MSA for "polish".
- **Principles:** P-OPEN-LOOP, P-HOOK-3S, P-PAYOFF-END.
- **Needs (required):** reorder/splice (cold open then setup); music bed; per-beat style.

### R10 Trend format (tier B)
- **Use-case:** creators and brands riding a known format; goal: reach.
- **Beats:** Hook 15 | Setup 25 | Punchline/drop 40 | Loop 20 (=100).
- **Hook rule:** the format's recognisable first beat in <= 1 s; no explanation.
- **Pacing:** fast: cut interval 2-3 s, 170-190 wpm, one punch-in per 3 s, hard cap length 20 s.
- **Captions:** hook (large, yellow, upper third) for the whole video; this is acceptable for a <= 20 s format only. **Sound:** wanted: the trending audio; available: none, and no rights record exists for any trending track, so I will not use one.
- **Params:** length_s:int=18 [10-25]; punch_in_every_s:float=3 [3-5]; punch_in_strength:float=1.15 [1.05-1.20]; caption_look:enum=hook.
- **Language:** format text is usually en; ar version = same beats with Arabic ASR words, no translation of the trend's catchphrase unless the creator does it.
- **Principles:** P-HOOK-3S, P-TREND-RECOGNITION, P-LOOP-END.
- **Needs (required):** trend audio (needs a rights record in DATA_RIGHTS.md first); template text overlay; transitions; stickers.

### R11 Music-only promo (tier C)
- **Use-case:** venue, product reel, sports; goal: reach.
- **Beats:** Visual hook 15 | Showcase 55 | Brand/offer card 20 | Loop 10 (=100).
- **Hook rule:** strongest visual in frame 0-1 s; chosen by start_at_s (no scoring op exists).
- **Pacing:** cut interval 2-3 s on a music beat grid (beat detection not available); one punch-in per 3 s.
- **Captions:** none possible (no words: `set_caption_style` raises E_OP_PRESET). **Sound:** wanted: licensed music bed; available: source audio only.
- **Params:** length_s:int=15 [8-30]; start_at_s:float=0 [0-source length]; punch_in_every_s:float=3 [3-6]; punch_in_strength:float=1.12 [1.05-1.20].
- **Language:** not applicable until a text overlay exists; then ar/en/fr brand card per ADR-0010.
- **Principles:** P-HOOK-VISUAL, P-ZOOM-RHYTHM, P-LOOP-END.
- **Needs (required):** text overlay (brand/offer card); music from a rights-cleared library (none recorded); beat-synced cuts; transitions.

### R12 Bilingual ar/en (tier B, ship-gated)
- **Use-case:** education, tech, expat services; goal: reach in two audiences.
- **Beats:** Hook in the dominant language 12 | Body 63 | Key terms restated in both languages 15 | CTA 10 (=100).
- **Hook rule:** the hook is in one language only (the audience's primary), so the caption reads cleanly; the second language arrives in the key-term beat.
- **Pacing:** 140-160 wpm; slow to x0.9 on the key-term beat; punch-in on each restated term.
- **Captions:** bold_box (box gives the Latin run a stable background). **Sound:** speech; available: speech.
- **Params:** length_s:int=40 [25-60]; cut_fillers:bool=true; punch_in_every_s:float=5 [3-8]; punch_in_strength:float=1.10 [1.05-1.20]; caption_look:enum=bold_box.
- **Language:** ar line with an en word: whole caption stays RTL and the Latin run keeps its own order; en line with an ar word: LTR base. Both depend on the EXP-008 size-parity fix: today the Latin glyphs render about 1.6x the Arabic alef height (Sev-2). **Veto note: this recipe may not enter the golden set or a demo until that fix passes judging.**
- **Principles:** P-CODESWITCH-DIR, P-DIALECT-FAITHFUL, P-MUTED-CAPTION.
- **Needs (required):** per-script size factor in the caption renderer (EXP-008 O1); optional second-language label overlay.

## 4. Principles
Evidence status: **SG** = from the Style Guide v0 (itself uncalibrated); **J** = Creative judgment, uncalibrated against the Founder or real view data. None is a measured finding yet. ADR-0009 explanations may quote the text but must not claim an effect size.
| id | principle text | status |
|---|---|---|
| P-HOOK-3S | State the claim, question, number or payoff within the first 3 s; the first 1.5 s decide the scroll. | SG |
| P-HOOK-VISUAL | With no speech, the strongest image must be in the first second. | J |
| P-MUTED-CAPTION | Most Shorts are watched muted, so captions must carry the full meaning and sit in the safe zone. | SG |
| P-ZOOM-RHYTHM | Punch-in 1.05-1.20, at most one per 3 s, so emphasis is not noise. | SG |
| P-PAYOFF-END | The last second delivers the payoff or loops back to the hook. | SG |
| P-LOOP-END | A last line that echoes the first invites a replay. | J |
| P-ONE-IDEA | One Short, one idea; cut anything that serves a second. | J |
| P-SOCIAL-PROOF-SPECIFIC | A specific outcome (number, time, name) from a real person is believed more than a general praise. | J |
| P-CTA-ONE | One call to action, held long enough to read. | J |
| P-URGENCY-SPECIFIC | A dated, concrete deadline beats "limited time". | J |
| P-SHOW-DONT-TELL | Show the product doing the thing while the line is spoken. | J |
| P-CONTRAST-REVEAL | The before and after must be in the same framing so the change reads instantly. | J |
| P-LIST-COUNT | A stated number sets an expectation the viewer stays to see completed. | J |
| P-AUTHENTIC-TONE | Unpolished, real process footage reads as honest; over-cutting kills it. | J |
| P-Q-FIRST | Show the viewer's question first; they recognise their own problem. | J |
| P-ANSWER-FIRST | Give the verdict before the reasoning. | J |
| P-OPEN-LOOP | Withholding the resolution keeps the viewer through the setup. | J |
| P-TREND-RECOGNITION | A trend format works through instant recognition; explaining it kills it. | J |
| P-CODESWITCH-DIR | Each line keeps its own script direction; a switch never reorders or translates the text. | SG (ARABIC_QA + EXP-008) |
| P-DIALECT-FAITHFUL | Spoken dialect is kept in the caption; never rewritten into MSA. | SG (ARABIC_QA) |

## 5. Renderer backlog from the "needs" columns (priority = recipes unblocked)
| need | recipes | note |
|---|---|---|
| Text overlay (unspoken text: title, price/date card, number badges, lower third, labels) | R02 R03 R04 R05 R06 R08 R11 R12 | single biggest unlock |
| Per-beat / per-range caption style | R01 R02 R07 R09 (hook look on first beat) | `set_caption_style` is global |
| Reorder / splice (cold open, after-first) | R04 R09 | needs a new op, not a renderer change only |
| Music bed + ducking (and a rights-cleared library) | R01 R02 R04 R06 R07 R09 R10 R11 | `tracks.audio` UNSUPPORTED today; no track has a rights record |
| Per-script size factor for mixed captions | R12 and every mixed line | EXP-008 O1, Sev-2 |
| Transitions, SFX, b-roll, stickers, speed ramp, zoom ease | R02 R04 R05 R10 R11 R07 | cosmetic or secondary |
