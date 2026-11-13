# Contributing

## Add test data for your language

1. Create `tasks/<task>/data/<code>/v1/` with `inputs/`, `references/`, and a `README.md` that states: version, purpose, number of items, source and license of the texts, who made the references, and any shared resource versions (with commit).
2. Data sets are versioned with semver (see [VERSIONING.md](./VERSIONING.md)): new corner cases are a minor bump, fixed references a patch bump, a scorer or format change a major bump (new `v<N>/` folder). Record every change in the task's `CHANGELOG.md`.
3. Create `tasks/<task>/results/<code>/LEADERBOARD.md` if it does not exist yet.
4. Run `python3 scripts/check.py`.

Prefer texts that represent real work: real OCR, real editions, real page layouts. 30 or more items is a good first set; say in the README how they were chosen.

## Submit a run

Follow `tasks/<task>/results/<code>/runs/README.md`, add your row to the leaderboard, and open a PR. Include your outputs, so anyone can re-score them.

## Propose a new task

Open an issue describing the task, an input/output format, and how it would be scored. Once agreed:

1. Add it to `tasks/index.json` (status `planned`).
2. Write `tasks/<task>/TASK.md` and `scorer/score.py`. The scorer must work for every language; put script-specific normalization in the scorer, keyed by language code.
3. Add a first data set, then set the status to `active`.

## Change a scorer

A scorer change can move every score. Bump `SCORER_VERSION` in `scorer/score.py` and in `TASK.md`, bump the major version of every data set of that task (see [VERSIONING.md](./VERSIONING.md)), re-score existing runs where outputs are available, and mention it in the PR.
