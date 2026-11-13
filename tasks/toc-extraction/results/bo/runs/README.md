# Runs

One folder per skill variant, model and data version: `<date>-<skill>-<variant>-<skill-version>-<short-commit>-<model>/`. The format is in [docs/results.md](../../../../../docs/results.md).

- `result.json`: the leaderboard row (mean and standard deviation over repeats, per split). Required.
- `run.json`, `scores.json`, `outputs/<item-id>.json`: one repeat's run details, scorer output and outputs, so anyone can re-score it. Encouraged.

`LEADERBOARD.md` and the site are generated from these files by `scripts/build_leaderboards.py`.
