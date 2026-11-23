# Data policy (owner: Assurance)
Created 2026-11-23 to hold ADR-0013; extend only by ADR.

## Sensitive personal data: edit diffs (ADR-0013)
Edit diffs = a user's ops lists, revisions, prompts, chat turns and timeline versions (`cache/<id>/edit/history/` and any future server copy).
1. Treated as sensitive personal data, at the same level as the user's footage.
2. Minimise: store only what undo/redo and the recipe backlog need; strip source paths and platform IDs when exporting.
3. Never used for model training or shared with third parties without explicit, revocable opt-in.
4. Deleted on request with the user's media; retention limit to be set before any external user (M-gate item).
5. Logs of recipe misses (`RECIPE_BACKLOG.md`) contain no user content: only recipe id, failure reason and anonymised param shapes.
