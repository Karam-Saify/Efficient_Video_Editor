# Engineering Conventions
- Python 3.11+, type hints, `ruff` + `pytest`. Node only for Remotion.
- Layout: `src/<stage>/`, `src/prompts/`, `schemas/`, `tests/{unit,fixtures,golden}/`, `cache/` (git-ignored), `samples/` (git-ignored; tracked via manifest).
- Commits: Conventional Commits (`feat:`, `fix:`, `test:`, `chore:`, `docs:`) + trailers `Role:`, `Tier:`, `Reviewed-by:` (T2).
- Branches: `main` protected by habit: T2 work on `t2/<handoff-id>`, merged only after Assurance ACCEPT.
- Never commit: `.env`, API keys, media files, `cache/`, `data/heldout/` contents.
- Time units: always integer milliseconds in data; frames computed only at render.
- Text: UTF-8 everywhere; Arabic strings never normalised silently (no stripping diacritics unless the style guide says so).
- Logs: JSON lines; no print debugging left in `main`.
