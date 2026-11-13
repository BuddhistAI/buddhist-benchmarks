# Changelog: toc-extraction benchmark

Versions follow [semantic versioning](../../VERSIONING.md), per language data set:

- **major**: the scorer or the input/output format changed. Old scores are not comparable.
- **minor**: new items were added (usually new corner cases). Each new item has a note saying what it tests and where it came from.
- **patch**: wrong references were fixed.

Every leaderboard row records the version it was scored on. A new version means re-running the current best skill and the challengers.

## bo 1.0.0 (2026-11-13)

- First Tibetan data set, `data/bo/v1/`: 85 passages, 394 headings (see its README).
- Scorer 1.0.0: adds position mode (`start` / `anchor`) next to title matching, and reports `scorer_version`.
