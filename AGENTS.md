# Notes for agents working in this repo

- Organized by task, then language: `tasks/<task>/data/<lang-code>/<version>/`. Task IDs live in `tasks/index.json`; language codes come from buddhist-skills `languages.json`.
- One scorer per task, shared by every language. Language-specific normalization goes inside the scorer, keyed by language code.
- Never edit a published data version; add a new one.
- Leaderboard rows cite an exact skill commit (`owner/repo@commit:path`), model, and data version. Do not compare rows across data versions.
- Example sets (version `example`) are for format checks only and never go on a leaderboard.
- Leaderboards (`LEADERBOARD.md`, the README table, the site) are generated from `runs/*/result.json` and `skills.json` by `scripts/build_leaderboards.py`. Never edit them by hand. Format: `docs/results.md`.
- Run `python3 scripts/check.py` before pushing.
