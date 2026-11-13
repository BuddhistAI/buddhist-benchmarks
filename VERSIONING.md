# Versioning benchmarks

Benchmarks grow: every time someone finds a case that a skill gets wrong, it should become a test item. So each task's data set for each language has a [semantic version](https://semver.org), `MAJOR.MINOR.PATCH`, and every score names the version it was measured on.

| Change | Bump | Example |
| --- | --- | --- |
| Scorer logic, metric, or input/output format changes | **major** | `1.4.2` → `2.0.0` |
| New items added (new corner cases) | **minor** | `1.4.2` → `1.5.0` |
| Wrong references fixed, no items added | **patch** | `1.4.2` → `1.4.3` |

## Where versions live

- **Folder:** `tasks/<task>/data/<code>/v<MAJOR>/`. Minor and patch changes are made in place in that folder; a major change starts a new folder (`v2/`). Only the current major version stays on `main`; older ones are at their git tag.
- **Exact version:** the data set's `README.md` (`**Version:**` line) and the task's `CHANGELOG.md`.
- **Git tag:** each release is tagged `<task>/<code>@<version>`, for example `toc-extraction/bo@1.0.0`, so any older version can be checked out exactly.
- **Scorer:** `SCORER_VERSION` in `scorer/score.py`, printed in every `scores.json`. Changing it is a major change for every language of that task.

## Adding corner cases (minor)

1. Add a line to the data set's JSONL file, with `metadata.note` saying what it tests (for example "heading split by a page break") and `metadata.origin` (where the case was found: a run, an issue, a user report).
3. Bump the version in the README and add a CHANGELOG entry listing the new items.
4. Tag the release after merge.

## What happens to the leaderboard

Leaderboard rows record the data version. Rows on different versions are never ranked against each other. After a new version, re-run the currently promoted skill and the open challengers on it, and start a new table section for that version. Older sections stay as history.
