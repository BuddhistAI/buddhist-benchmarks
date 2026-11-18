# Task: translation

Given a source passage and a short context sheet, produce a translation into the target language.

Skills for this task are named `translation-<source>-to-<target>` in [buddhist-skills](https://github.com/BuddhistAI/buddhist-skills), for example `translation-tibetan-to-french`. Task page: [knowledge base](https://buddhistai.github.io/knowledge-base/tasks/translation.html).

**Status:** planned. The scorer and a format example exist. The first real data set, Tibetan colophons into French (`data/bo-fr/v1/`), is being collected. Nothing goes on a leaderboard until it has real items.

## Why not BLEU or chrF

Reference-overlap metrics measure how close a translation is to one reference text. From Tibetan, that rewards literal translations: verb-final order, repeated clauses and concrete images copied into the target. The method used here comes from Drupchen, [Two strategies for improving machine translation from Tibetan](https://buddhistai.github.io/knowledge-base/papers/two-strategies-for-machine-translation-from-tibetan/) (§9) and [Subtracting the Typological Baseline](https://buddhistai.github.io/knowledge-base/papers/subtracting-the-typological-baseline/) (§9, §11.3), CC BY 4.0. A translation is scored on whether it carries the source's **meaning units**, not on its form.

## Data format

Data sets are per language pair: `data/<source>-<target>/v<major>/test.jsonl`, for example `data/bo-fr/v1/`. One item per line:

```json
{
  "id": "colophon-001",
  "input": {
    "source": "<Tibetan text>",
    "genre": "colophon",
    "context": {"pivot": "none", "reader": "...", "delivery": "composed in writing", "format": "...", "terminology": "..."}
  },
  "target": {
    "genre": "colophon",
    "units": [
      {"id": "u1", "slot": "request", "channel": "text", "gloss": "it was written at the request of ..."},
      {"id": "u2", "slot": "verb", "channel": "text", "gloss": "the author composed it"}
    ],
    "matrix_verb": "u2",
    "licensed_connectives": []
  },
  "metadata": {"subset": "colophon", "source_language": "bo", "target_language": "fr"}
}
```

- `input.source`: the passage, Unicode, as in the edition used.
- `input.context`: the answers to the five context questions of the method (pivot language, reader and register, how the source was delivered, target format, who decides terms). Skills may use it.
- `target.units`: the meaning units, written by an expert who reads the source language. `gloss` is a short plain-English statement of the unit (English, so the same units can score any target language). `slot` names the colophon slot (`closing`, `request`, `requester`, `place`, `date`, `author-epithet`, `aspiration`, `verb`) or is empty for prose.
- `channel`: `text` (must be in the translation's text), `outside` (may be carried by layout: a heading, numbering, a note) or `absent` (correctly left out, for example a particle that hands a turn to an interpreter).
- `target.licensed_connectives`: French connectives that a source particle does justify (for example `ainsi` for a real causal particle). Others count as invented.
- How to write items: [data/bo-fr/AUTHORING.md](data/bo-fr/AUTHORING.md).

## Output

`predictions.jsonl`, one line per item: `{"id": "<item id>", "output": "<the translation as plain text>"}`. A skill may also return `{"text": "...", "flags": [...]}`; only `text` is scored.

## Scoring

Scorer version: **0.1.0**, judge version **0.1.0**.

1. `scorer/judge.py` (needs an API key, costs money) asks a pinned judge model, `claude-opus-5-5` at effort `medium`, to label each unit of each item: `delivered`, `shifted`, `thinned` or `absent`; units with channel `absent` are `rendered` or `not-rendered`. The judge sees the source, the units and the translation, never a reference translation. For colophons it also says where the main verb is, whether the author's epithet stays a phrase, and whether the slots keep source order. It writes `judgments.jsonl` with token counts.
2. `scorer/score.py` reads the judgments and the translations and counts. It needs no API.

| Metric | Meaning |
| --- | --- |
| `unit_coverage` | Mean unit value: delivered 1, shifted 0.5, thinned 0.5, absent 0. **Headline score.** |
| `matrix_verb_early` | Share of colophons whose main verb comes early in the French sentence (not stranded after 60 words, not lost). |
| `epithet_as_slot` | Share of colophons where the author's humble epithet stays a phrase, not a new sentence. |
| `target_order` | Share of colophons whose slots are re-ordered for the target language. |
| `unlicensed_connectives` | Mean count per item of French connectives (*ainsi, donc, c'est pourquoi* ...) that no source particle licenses. Lower is better. Counted by the scorer, without the judge. |
| `wrongly_rendered` | Number of units marked "correctly absent" that the translation still renders. |

```bash
python3 scorer/judge.py --data data/bo-fr/v1/test.jsonl --predictions predictions.jsonl --out judgments.jsonl
python3 scorer/score.py --language bo-fr --data data/bo-fr/v1/test.jsonl \
  --predictions predictions.jsonl --judgments judgments.jsonl > scores.json
```

The judge is a model, so its labels can be wrong. Keep `judgments.jsonl` with every run so others can check them, and report the judge's token counts in the run's cost. A human check of a sample of labels is part of moving a data set from Draft to Reviewed.

## Cost

One item is about 150 Tibetan words. One judge call reads about 1,500 tokens and writes about 1,000 (with thinking). At list prices (2026-11): about **$0.03 per item with `claude-opus-5-5`**, so about $1 for 30 items. The translation runs cost more: see the [experiment plan](https://github.com/BuddhistAI/knowledge-base/blob/main/experiments/2026-11-tibetan-french-translation/PLAN.md) (about $55 for 30 items, 3 systems, 2 models, 3 repeats).
