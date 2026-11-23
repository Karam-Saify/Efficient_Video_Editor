# ADR-0014: Timeline `provenance.recipe` (additive, meta only)
- **Status:** Proposed · **Date:** 2026-11-23 · **Proposer:** engineering-lead (H-0029) · **Door:** two-way · **Review:** Assurance H-0029 review, then M1 gate

**Context.** ADR-0009 needs every explanation to come from decision provenance. A recipe-compiled timeline must say which recipe (id + version), which param values (the full fill, defaults included), which principle ids, and which recipe fields compiled to nothing (UNRENDERED). Timeline v0 `provenance` had only `selection`, `prompt_versions`, `model_ids`.

**Decision.** Add one optional object `provenance.recipe` = `{id, version, params, principles, unrendered}` to `schemas/timeline.schema.json` (all five keys required inside it, `additionalProperties: false`). It is `meta` in `src/capabilities.py` (never a render instruction, so never UNSUPPORTED_FIELD). `id` matches `^(R[0-9]{2}|[a-z][a-z0-9_]*)$` so named recipes such as `photos_to_video` fit. The ADR-0006 dev marker stays in `provenance.selection` (H-0026 F2), not here.

**Why not an existing field.** Packing structured data into the free-text `selection` string would make ADR-0009 explanations parse prose; `prompt_versions`/`model_ids` mean something else.

**Compatibility.** Additive and optional: every existing valid timeline stays valid (`tests/unit/test_recipes.py::test_existing_timeline_fixtures_still_valid`; full suite green). Fixtures: 5 valid + 6 invalid under `tests/fixtures/timelines/provenance/`.

**Consequences.** Timelines carry the fill, which ADR-0013 treats as edit data (sensitive); no personal text is in it today (params are numbers/enums). Revisit if a free-text param is ever added.
