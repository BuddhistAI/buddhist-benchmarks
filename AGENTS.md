# Notes for agents working in this repo

- Organized by task, then language: `tasks/<task>/data/<lang-code>/<version>/`. Task IDs live in `tasks/index.json`; language codes come from buddhist-skills `languages.json`.
- One scorer per task, shared by every language. Language-specific normalization goes inside the scorer, keyed by language code.
- Data sets: one standard `test.jsonl` (`id`, `input`, `target`, `metadata`) plus a Hugging Face dataset-card README per version folder (template: `tasks/toc-extraction/data/bo/v2/`). Never change items or answers without a version bump (VERSIONING.md).
- Leaderboard rows cite an exact skill commit (`owner/repo@commit:path`), model, and data version. Do not compare rows across data versions.
- Example sets (version `example`) are for format checks only and never go on a leaderboard.
- Leaderboards (`LEADERBOARD.md`, the README table, the site) are generated from `runs/*/result.json` and `skills.json` by `scripts/build_leaderboards.py`. Never edit them by hand. Format: `docs/results.md`.
- Run `python3 scripts/check.py` before pushing.
