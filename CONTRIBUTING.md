# Contributing

## Add test data for your language

1. Create `tasks/<task>/data/<code>/<version>/` with `inputs/`, `references/`, and a `README.md` that states: purpose, number of items, source and license of the texts, who made the references, and any shared resource versions (with commit).
2. Use the next version number (`v1`, `v2`, ...). Never change a published version: fix mistakes in a new version, so old scores stay meaningful.
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

A scorer change can move every score. Bump a `scorer_version` note in `TASK.md`, re-score existing runs where outputs are available, and mention it in the PR.
