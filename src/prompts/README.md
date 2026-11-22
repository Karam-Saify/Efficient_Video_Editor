# Prompts
Versioned prompt templates for LLM stages (`score`, `edit`), one file per prompt and version,
e.g. `score.v1.md`. The prompt version is part of the stage config, so changing it changes the
`config_hash` and forces a rerun (see `src/manifest.py`). Empty until Phase 2.
