# Notes for agents working in this repo

## Start here (every BuddhistAI repo)

- Read the maintainer handbook first: https://buddhistai.github.io/knowledge-base/handbook/ (source: BuddhistAI/knowledge-base `handbook/`). Follow its rules and conventions.
- Check the Development board for cards assigned to you: https://github.com/orgs/BuddhistAI/projects/3. Status and next steps: `handbook/status.md`.
- Rules: plain English for non-native readers, no idioms. "Buddhist tasks", not only texts. "Top performance" and "Best value". Neutral credits: WeBuddhist is one contributor among others. Never invent data, scores, votes or links. Never edit generated files by hand.
- buddhist-benchmarks stays clean (short `result.json`, outputs, scores). Provenance records (`buddhistai/provenance@1`) live in the skill's own repo.
- When you change something the handbook describes, update the handbook in the same pull request.
- Before you change anything users see (pages, forms, install steps, app screens), write a design in `docs/designs/` and run an EGM review with our personas: skills `buddhistai-elephant` and `buddhistai-ux-review` (handbook `ux.md`). Small text or bug fixes skip this.
- EGM artifact directory: docs/designs
- This repo: task benchmarks, scorers, results and the leaderboard site. Run `python3 scripts/build_leaderboards.py`, then `python3 scripts/check.py`.

## This repo

- Organized by task, then language: `tasks/<task>/data/<lang-code>/<version>/`, each holding one standard `test.jsonl` (`id`, `input`, `target`, `metadata`) and a Hugging Face dataset-card README (template: `tasks/toc-extraction/data/bo/v2/`). Task IDs live in `tasks/index.json`; language codes come from buddhist-skills `languages.json`.
- One scorer per task, shared by every language. Language-specific normalization goes inside the scorer, keyed by language code.
- Data sets are semver-versioned (VERSIONING.md): adding items is minor, fixing references is patch, both in place in `v<major>/` with a README version bump and a task CHANGELOG entry; scorer or format changes are major and get a new `v<major>/` folder (older majors live only at their tag). Never change items or references without bumping the version.
- Leaderboard rows cite an exact skill commit (`owner/repo@commit:path`), model, and data version. Do not compare rows across data versions.
- Example sets (version `example`) are for format checks only and never go on a leaderboard.
- Leaderboards (`LEADERBOARD.md`, the README table, the site) are generated from `runs/*/result.json` and `skills.json` by `scripts/build_leaderboards.py`. Never edit them by hand. Format: `docs/results.md`.
- Run `python3 scripts/check.py` before pushing.
