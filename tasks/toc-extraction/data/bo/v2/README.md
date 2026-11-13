---
pretty_name: Tibetan TOC extraction (sa-bcad headings)
license: mit
language:
- bo
task_categories:
- text-generation
- token-classification
tags:
- tibetan
- buddhism
- table-of-contents
- sa-bcad
- benchmark
size_categories:
- n<1K
configs:
- config_name: default
  data_files:
  - split: test
    path: test.jsonl
dataset_info:
  features:
  - name: id
    dtype: string
  - name: input
    dtype: string
  - name: target
    struct:
    - name: entries
      list:
      - name: title
        dtype: string
      - name: level
        dtype: int64
      - name: start
        dtype: int64
      - name: anchor
        dtype: string
  - name: metadata
    struct:
    - name: subset
      dtype: string
    - name: book
      dtype: string
    - name: book_title
      dtype: string
    - name: author
      dtype: string
    - name: chars
      dtype: int64
    - name: headings
      dtype: int64
  splits:
  - name: test
    num_bytes: 1136635
    num_examples: 85
  download_size: 1136635
  dataset_size: 1136635
---

# toc-extraction / bo / v2

- **Version:** 2.0.0 (see [CHANGELOG.md](../../../CHANGELOG.md)).
- **Purpose:** find the sa-bcad (ས་བཅད) outline headings in passages of Tibetan commentary whose formatting and line breaks were stripped, with their nesting level and start position.
- **Items:** 85 passages, 394 headings, in one file: [`test.jsonl`](./test.jsonl).
- **Source and license:** public-domain texts, data MIT (details below).
- **References made by:** built automatically from the EPUBs' outline markup; silver standard (details below).

## How this benchmark works

The whole benchmark is one file, `test.jsonl`. Each line is one **item**: a question and its correct answer.

```json
{
  "id": "IBA-LWS-08-045",
  "input": "གསུམ་པ་བསྡུ་བ་ནི། སྲིད་པ་བཞི་བཤད་ན། ...",
  "target": {"entries": [{"title": "བསྡུ་བ", "level": 1, "start": 0, "anchor": "གསུམ་པ་བསྡུ་བ་ནི། སྲིད་པ་བཞི་བཤད་ན། དེ་ད"}]},
  "metadata": {"subset": "same-book", "book": "IBA-LWS-08", "book_title": "A Lamp Illuminating the Intent of Vasubandhu", "author": "Jamyang Loter Wangpo", "chars": 514, "headings": 1}
}
```

| Field | What it is |
| --- | --- |
| `id` | The item's permanent ID. |
| `input` | **The question.** The passage the skill reads. A skill gets only this. |
| `target` | **The answer.** Every heading in the passage, in reading order: `title`, `level` (1 = the shallowest level in this passage), `start` (character offset in `input`) and `anchor` (its first 40 characters, verbatim). |
| `metadata` | Facts about the item, used to break the score down: `subset` (`same-book` or `held-out-book`), the book, its length and its number of headings. Never shown to the skill. |

This is the same shape that Hugging Face datasets, lm-evaluation-harness and Inspect use (`input` / `target` / `metadata`). It loads with `datasets.load_dataset("json", data_files="test.jsonl")`.

**To test a skill:** give it each `input`, and save what it returns as one line per item in a `predictions.jsonl`: `{"id": "...", "output": {"entries": [...]}}`. Then score it:

```bash
python3 tasks/toc-extraction/scorer/score.py --language bo \
  --data tasks/toc-extraction/data/bo/v2/test.jsonl --predictions predictions.jsonl > scores.json
```

The headline number is `structure_f1`: how many headings were found at the right place **and** level, balancing headings missed against headings invented. It is counted over all 394 headings (micro F1), so passages with many headings weigh more. `scores.json` also breaks it down by subset. Runs, with every skill output, are kept in [`results/bo/runs/`](../../../results/bo/runs/), and the scores feed the [leaderboard](https://buddhistai.github.io/buddhist-benchmarks/tasks/toc-extraction/bo/).

### Worked example 1: a correct answer

- **Question** (`IBA-LWS-08-045`, 514 characters) starts with གསུམ་པ་བསྡུ་བ་ནི། ...
- **Answer:** one heading, "Third: the summary" (བསྡུ་བ), level 1, at position 0.
- **A skill's output** (TOC extraction (sa-bcad method) on Claude Sonnet 5.5): `{"entries": [{"title": "Third: the summary (bsdu ba)", "level": 1, "anchor": "གསུམ་པ་བསྡུ་བ་ནི། སྲིད་པ་བཞི་བཤད་ན། ..."}]}`
- **Score:** the output's `anchor` is found at position 0, where the answer's heading starts, and the level matches. 1 found of 1 expected, nothing extra: F1 = **1.0**. The title's wording doesn't matter in this set, only position and level.

### Worked example 2: an extra heading

- **Question** (`IBA-LWS-08-067`, 616 characters) has two outline transitions: གཉིས་པ་སྡོམ་མིན་གྱི་འཐོབ་ཚུལ་ནི། at the start and གསུམ་པ་བར་མའི་འཐོབ་ཚུལ་ནི། in the middle.
- **Answer:** only the first one.
- **A skill's output:** both, each at level 1.
- **Score:** 1 matched and 1 extra, so precision is 1/2 and recall 1/1: F1 = **0.67** for this item. Every skill predicts the second heading, and it reads like a real sa-bcad heading. So the answer is probably what's wrong here. Wrong answers are fixed in patch versions: [open an issue](https://github.com/BuddhistAI/buddhist-benchmarks/issues).

## About this data set

- **Subsets** (`metadata.subset`):
  - `same-book` (76 items, 369 headings): Jamyang Loter Wangpo, *A Lamp Illuminating the Intent of Vasubandhu* (མཛོད་ཀྱི་མཆན་འགྲེལ་དབྱིག་གཉེན་དགོངས་པ་གསལ་བའི་སྒྲོན་མེ).
  - `held-out-book` (9 items, 25 headings; one item has no heading): Chenga Chökyi Gyalpo, *The Jewel Garland*. No skill was tuned on this book.
- **How the items were chosen:** every passage of up to 6,500 characters of the two books, cut at heading boundaries, except 48 passages of the first book that were used to optimise skills. Those stay in [BuddhistAI/toc-extraction-tibetan](https://github.com/BuddhistAI/toc-extraction-tibetan) as training data.
- **Source and license:** the texts are public domain. Digital editions from EPUBs (IBA-LWS-08, RCP-FM-07); the EPUBs and the build script are in BuddhistAI/toc-extraction-tibetan `benchmark/`. This data set is MIT.
- **How the answers were made:** built automatically by `build_dataset.py` from the EPUBs' `Tibetan-Sabche` outline paragraphs. Levels are reconstructed from the outline grammar (ལ་གཉིས / ལ་གསུམ announcements and ordinals), so this is a silver standard. The *Jewel Garland* answers are known to miss real headings.
- **Scoring mode:** the outline titles are labels, not text that appears verbatim, so this set is scored in **position mode**. A predicted heading must give `start` or a verbatim `anchor`, and it matches an answer heading that starts within 3 characters of it.
- **Shared resource versions:** none.
- **History:** 2.0.0 has exactly the same items and answers as 1.0.0, in the standard one-file format. Scores on the two are identical (checked by re-scoring every stored run). 1.0.0, in the old `inputs/` + `references/` layout, is at tag `toc-extraction/bo@1.0.0`.

## Citation

```bibtex
@misc{buddhistai_toc_extraction_bo,
  title  = {Tibetan TOC extraction (sa-bcad headings), version 2.0.0},
  author = {{BuddhistAI} and {WeBuddhist}},
  year   = {2026},
  url    = {https://github.com/BuddhistAI/buddhist-benchmarks/tree/main/tasks/toc-extraction/data/bo/v2}
}
```
