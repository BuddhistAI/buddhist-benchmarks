# Notes for agents working in this repo

- Organized by task, then language: `tasks/<task>/data/<lang-code>/<version>/`, each holding one standard `test.jsonl` (`id`, `input`, `target`, `metadata`) and a Hugging Face dataset-card README (template: `tasks/toc-extraction/data/bo/v2/`). Task IDs live in `tasks/index.json`; language codes come from buddhist-skills `languages.json`.
- One scorer per task, shared by every language. Language-specific normalization goes inside the scorer, keyed by language code.
- Data sets are semver-versioned (VERSIONING.md): adding items is minor, fixing references is patch, both in place in `v<major>/` with a README version bump and a task CHANGELOG entry; scorer or format changes are major and get a new `v<major>/` folder (older majors live only at their tag). Never change items or references without bumping the version.
- Leaderboard rows cite an exact skill commit (`owner/repo@commit:path`), model, and data version. Do not compare rows across data versions.
- Example sets (version `example`) are for format checks only and never go on a leaderboard.
- Leaderboards (`LEADERBOARD.md`, the README table, the site) are generated from `runs/*/result.json` and `skills.json` by `scripts/build_leaderboards.py`. Never edit them by hand. Format: `docs/results.md`.
- Run `python3 scripts/check.py` before pushing.
