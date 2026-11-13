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
- `page`: the page label where the section starts, if the input has page markers. Optional; not scored in v1.
- Entries are in reading order.

References in `data/<code>/<version>/references/` use the same format.

## Scoring

`scorer/score.py` matches predicted entries to reference entries in order, one to one. Two titles match when their normalized similarity is at least 0.9. Normalization is per script and lives in the scorer (for Tibetan: strip leading yig mgo marks, trailing shad and tsheg, and whitespace).

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
| Tibetan (`bo`) | `example` | 1 | Format example only, synthetic. Not for leaderboards. |
