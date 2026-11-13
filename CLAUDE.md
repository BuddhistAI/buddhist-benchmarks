# Notes for agents working in this repo

- Organized by task, then language: `tasks/<task>/data/<lang-code>/<version>/`. Task IDs live in `tasks/index.json`; language codes come from buddhist-skills `languages.json`.
- One scorer per task, shared by every language. Language-specific normalization goes inside the scorer, keyed by language code.
- Data sets are semver-versioned (VERSIONING.md): adding items is minor, fixing references is patch, both in place in `v<major>/` with a README version bump and a task CHANGELOG entry; scorer or format changes are major and get a new `v<major>/` folder. Never change items or references without bumping the version.
- Leaderboard rows cite an exact skill commit (`owner/repo@commit:path`), model, and data version. Do not compare rows across data versions.
- Example sets (version `example`) are for format checks only and never go on a leaderboard.
- Run `python3 scripts/check.py` before pushing.
