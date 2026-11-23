# Playbook: Engineering

## SOP-E1: Any T2 change
1. Read the brief, the relevant ADRs, and `ARCHITECTURE.md`.
2. If an interface changes: update `schemas/` + fixtures (≥ 5 valid, ≥ 5 invalid) + validator first; commit separately.
3. Write the failing test first, then the code.
4. Run the full test suite + the golden-set smoke run (`make smoke` once it exists).
5. Produce the reproduction command: a single line Assurance can run from a clean checkout.
6. Write the RETURN with: diff summary, test output path, reproduction command, tokens/minutes impact.
7. Do **not** merge. Assurance reviews; merge after ACCEPT. Commit trailers: `Role: engineering`, `Tier: T2`, `Reviewed-by: assurance-lead (<review id>)`.

## SOP-E2: Adding an LLM call to the pipeline
1. Justify in the brief why code cannot do it (Constitution I-3, I-4).
2. Define the input text format (no raw video), the output JSON schema, and the validator.
3. Prompt lives in `src/prompts/<name>.md` with a version header; changing it = T2 + golden regression run.
4. Wrap the call with: structured output, a validator, max 2 retries that feed back the validator error,
   token logging (`usage.jsonl`: stage, model ID, input/output tokens, latency, attempt number).
5. Record the model ID in `run.json`. A model change = T2 with a golden regression run.

## SOP-E3: Dependency intake
Name · version (pinned) · license (must allow commercial use) · why · alternatives considered · size.
Assurance confirms the license and adds it to the data/asset rights register.

## SOP-E4: Emergency (red `main`, data at risk)
1. Stop feature work. Revert to the last green commit if the fix is not obvious within 15 minutes.
2. Write `HALT:` in STATE.md if data is at risk.
3. Open `company/incidents/INC-<n>.md` from the template; Assurance owns the postmortem.

## SOP-E5: Stage contract (every pipeline stage)
- CLI: `python -m src.<stage> --input <path> --out <dir> [--config <yaml>]`
- Reads only declared inputs; writes only into `cache/<video_id>/<stage>/`.
- Writes `manifest.json`: input hashes, output hashes, config hash, versions, duration, tokens.
- Skips work if the manifest shows identical inputs + config (caching = Constitution rule "cache everything").
- Exit codes: 0 ok · 2 validation failure · 3 dependency failure · 1 other.
