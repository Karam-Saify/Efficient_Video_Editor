# BRIEF H-0028 (Week 1 · C, part 1 of 2)
- **To:** creative-lead · **Tier / Milestone:** T1 (fast lane: content spec, no runtime code) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** Define the editorial content of 12 recipes. Under ADR-0008, a small model picks and fills recipes, so the recipes *are* the product's taste. Engineering will formalise them into a typed schema and compiler in H-0029.
2. **Inputs:** `company/decisions/ADR-0007..0013`; `docs/CAPABILITIES.md` (what the renderer can draw today); `src/edit/ops.py` docstrings (ops available: trim, delete_words, set_caption_style, add_zoom, set_duration); caption presets `clean`, `bold_box`, `hook`; your own style guide / rubric files in `company/positions/04-creative/`; `quarantine/dev/dev_manifest.csv` (dev clip types: mostly English talking-head, some music-only).
3. **Constraints:**
   - Each recipe must be expressible with today's ops. Anything that is not (music bed, sound FX, b-roll, transitions, emoji stickers) goes in a separate "needs" column with a short reason. This becomes the renderer backlog, and is never faked.
   - Arabic-first and code-switching (ADR-0010): say, for each recipe, how it behaves for ar, en, fr and mixed lines.
   - Keep params few and typed: a name, a type, a default, a range, and what a creator would call it in plain words.
   - Explanations come from provenance (ADR-0009): give each recipe 1–3 principle ids (e.g. `P-HOOK-3S`) with a one-line principle text.
4. **Output:** `company/handoffs/H-0028-recipes.md` with a table of 12 recipes. Columns: id, name, use-case (business niche + goal), structure beats (ordered, with target share of duration), hook rule, pacing curve (words/min or cut interval per beat), caption style preset, sound (wanted vs available), params (name:type=default [range]), principle ids, needs-not-yet-rendered. Then a principles table. Return at `company/handoffs/H-0028-return.md`.
5. **Done when:**
   - [ ] 12 recipes are distinct by use case, covering at least: talking-head tip, product demo, testimonial, before/after, listicle, event/offer promo, behind-the-scenes, FAQ answer, story hook, trend-format, music-only promo, bilingual ar/en.
   - [ ] Every param has a type, default and range. Every duration share sums to 100 %.
   - [ ] Each recipe's "needs" column is honest against CAPABILITIES.md.
6. **Out of scope:** code, schema files, tests, renderer changes.
7. **Effort budget:** max 20 tool calls.
8. **Escalate if:** fewer than 6 recipes can be built with today's ops (that would mean the renderer must grow before recipes are worth formalising).
9. **Termination condition:** both files written. Commit them (`Role: creative-lead`, `Tier: T1`), but do not push.
10. **Consulted:** engineering-lead consumes this in H-0029.
