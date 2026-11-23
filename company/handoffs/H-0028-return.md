# RETURN H-0028
- **From:** creative-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):** 12 distinct recipes written with beats (shares sum to 100 %), hook rule, pacing, preset, typed params, 2-3 principle ids each, and a needs column. Honest tiering against today's ops: 4 fully buildable (R01, R03, R07, R08), 7 buildable in degraded core form (R02, R04, R05, R06, R09, R10, R12), 1 not worth building (R11, no speech, no text). Escalation test (fewer than 6 buildable): not triggered if "buildable" includes degraded core (11), but the strictly-full count is 4, which is below 6. Reported rather than hidden. Biggest unlocks: text overlay, per-beat caption style, reorder op.
- **ARTIFACTS:** company/handoffs/H-0028-recipes.md; company/handoffs/H-0028-return.md
- **EVIDENCE:** read `docs/CAPABILITIES.md` (audio tracks UNSUPPORTED_FIELD; captions from ASR words only); `src/edit/ops.py` (`set_caption_style` is global and fails with E_OP_PRESET with no captions; `trim` keeps one window; `add_zoom` instant, scale range); `src/presets.py` (clean / bold_box / hook). Shares verified by hand: R01 10+65+15+10; R02 15+50+20+15; R03 15+25+30+30; R04 35+25+30+10; R05 12+75+13; R06 15+45+20+20; R07 12+63+15+10; R08 12+38+35+15; R09 10+30+30+20+10; R10 15+25+40+20; R11 15+55+20+10; R12 12+63+15+10; each = 100.
- **DONE-WHEN CHECK:**
  - 12 distinct recipes covering talking-head tip, product demo, testimonial, before/after, listicle, event/offer, behind-the-scenes, FAQ, story hook, trend-format, music-only, bilingual: ✅ (R01-R12)
  - Every param has type, default, range; every share sums to 100 %: ✅ (ranges for start_at_s are "0 to source length", a data-dependent bound; item_count/length_s etc. are numeric). Shares: see EVIDENCE.
  - Needs column honest against CAPABILITIES.md: ✅ (section 0 and backlog table 5 name each unsupported item and why).
- **DEVIATIONS FROM BRIEF:** The brief asked for "a table"; 11 columns per recipe do not fit one markdown table, so there is an index table plus one field block per recipe (same columns) and a backlog table. Tiering A/B/C added to make "buildable" countable.
- **OPEN QUESTIONS:**
  1. (Operator/Founder) Does the escalate-if rule count degraded recipes? Strictly-full = 4 (<6); with degraded core = 11. I proceeded and flag it; if strict, H-0029 should wait for text overlay + per-beat style.
  2. (research-lead) Arabic/French pace multipliers (x0.95 / x1.05) and every wpm figure are guesses: dev clips are English. Needs Arabic timing data.
  3. (engineering-lead) Are the presets inside the style guide safe zone (18-72 % height, right 12 % clear)? I did not measure; assurance/engineering to confirm in H-0029.
  4. (Founder) Principles are SG or J (uncalibrated); calibrate against FOUNDER_TASTE.md before ADR-0009 explanations quote them.
- **CONFIDENCE:** Medium (structure sound and checked against code; pacing numbers and principle weights are uncalibrated judgment).
- **NEXT RECOMMENDED STEP:** H-0029 formalises R01, R03, R07, R08 first (tier A); product-lead decides whether to prioritise the text-overlay op, which unblocks 8 recipes.
