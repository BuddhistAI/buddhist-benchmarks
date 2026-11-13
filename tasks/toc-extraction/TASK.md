# Task: toc-extraction

Given the full text of a work, list its table of contents: every section title, its nesting level, and where it starts.

Skills for this task are named `toc-extraction-<language>` in [buddhist-skills](https://github.com/BuddhistAI/buddhist-skills), for example `toc-extraction-tibetan`.

## Input

One UTF-8 plain-text file per item: `inputs/<item-id>.txt`. The text is as found in the source (it may include OCR noise). Page breaks, where known, are marked on a line of their own as `[page N]`.

## Output

One JSON file per item: `<item-id>.json`.

```json
{
  "entries": [
    {"title": "ལེའུ་དང་པོ།", "level": 1, "page": "1"},
    {"title": "...", "level": 2, "page": "3"}
  ]
}
```

- `title`: the title exactly as it appears in the text (do not translate or normalize it).
- `level`: 1 for top-level sections, 2 for their subsections, and so on.
- `page`: the page label where the section starts, if the input has page markers. Optional; not scored yet.
- `start` (optional): character offset in the input where the section's heading starts.
- `anchor` (optional): the first characters of the heading (40 is enough), copied verbatim from the input.
- Entries are in reading order.

References in `data/<code>/<version>/references/` use the same format.

## Scoring

Scorer version: **1.0.0** (`SCORER_VERSION` in `scorer/score.py`, also printed in `scores.json`).

`scorer/score.py` matches predicted entries to reference entries one to one, in one of two modes, chosen per item:

- **Position mode**, when every reference entry has `start`. A predicted entry is placed at its `start`, or where its `anchor` is found verbatim in the input (searching forward from the previous entry). It matches a reference entry that starts within 3 characters. Use this when outline titles are labels that do not appear verbatim in the text, as in the Tibetan sa-bcad sets.
- **Title mode**, otherwise. Entries are matched in order; two titles match when their normalized similarity is at least 0.9. Normalization is per script and lives in the scorer (for Tibetan: strip leading yig mgo marks, trailing shad and tsheg, and whitespace).

Reported metrics:

| Metric | Meaning |
| --- | --- |
| `title_f1` | F1 over matched titles, ignoring level. |
| `structure_f1` | F1 where a match also needs the same level. **Headline score.** |
| `level_accuracy` | Share of matched titles with the correct level. |

Scores are micro-averaged over all entries in the data set.

## Data sets

| Language | Version | Items | Status |
| --- | --- | --- | --- |
| Tibetan (`bo`) | `v1` (1.0.0) | 85 | Sa-bcad headings in stripped commentary passages, position mode. Silver references. |
| Tibetan (`bo`) | `example` | 1 | Format example only, synthetic. Not for leaderboards. |

Versions and what changed in each: [CHANGELOG.md](./CHANGELOG.md).
