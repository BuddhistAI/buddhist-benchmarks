# Changelog: toc-extraction benchmark

Versions follow [semantic versioning](../../VERSIONING.md), per language data set:

- **major**: the scorer or the input/output format changed. Old scores are not comparable.
- **minor**: new items were added (usually new corner cases). Each new item has a note saying what it tests and where it came from.
- **patch**: wrong references were fixed.

Every leaderboard row records the version it was scored on. A new version means re-running the current best skill and the challengers.

## bo 2.0.0 (2026-11-13)

- **Format change (major):** the data set is now one standard JSONL file, `data/bo/v2/test.jsonl`, one item per line with `id`, `input` (the passage), `target` (the correct TOC) and `metadata` (subset, book, length, number of headings). The `inputs/`, `references/` and `items.json` of 1.0.0 are gone; the README is a Hugging Face dataset card.
- Same 85 items and the same answers as 1.0.0.
- Scorer 2.0.0: reads `--data test.jsonl --predictions predictions.jsonl` (or a folder of `<id>.json`), and reports scores per subset. Matching and metrics are unchanged, and re-scoring all 10 stored runs gives identical numbers, so the leaderboard rows carry over.
- 1.0.0 stays available at tag `toc-extraction/bo@1.0.0`.

## bo 1.0.0 (2026-11-13)

- First Tibetan data set, `data/bo/v1/`: 85 passages, 394 headings (see its README).
- Scorer 1.0.0: adds position mode (`start` / `anchor`) next to title matching, and reports `scorer_version`.
