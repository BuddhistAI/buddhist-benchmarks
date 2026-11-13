# Results format

Every leaderboard and the site at https://buddhistai.github.io/buddhist-benchmarks/ are generated from small JSON files. Nothing on a leaderboard is typed by hand.

## Where things live

```
tasks/<task>/results/<lang>/
  skills.json                 every skill on this leaderboard: status, approach, links (hand-edited)
  runs/<run-id>/
    result.json               the leaderboard row (this file is what the site reads)
    run.json, scores.json     optional: one repeat's scorer output and run details
    outputs/<item-id>.json    optional but encouraged: what the skill produced, so anyone can re-score it
  LEADERBOARD.md              generated
models.json                   model display names and price tiers
```

`<run-id>` is `<date>-<skill>-<variant>-<skill-version>-<short-commit>-<model-slug>`. One run folder is one skill variant, one model and one data version, averaged over its repeats.

## result.json

```json
{
  "schema": "buddhist-benchmarks/result@1",
  "task": "toc-extraction",
  "language": "bo",
  "data_version": "2.0.0",
  "scorer_version": "2.0.0",
  "skill": "toc-extraction-tibetan",
  "variant": "sabcad-outliner-toc",
  "skill_version": "1.0.0",
  "skill_ref": "BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner-toc",
  "model": "claude-sonnet-5-5",
  "temperature": 1.0,
  "repeats": 3,
  "harness": "toc-extraction-tibetan benchmark/bench_skills.py (DSPy 3.5.0 ChainOfThought)",
  "headline": "structure_f1",
  "scores": {
    "all":           {"structure_f1": {"mean": 0.9617, "std": 0.0066, "runs": [0.9548, 0.9625, 0.9678]}, "title_f1": {...}, "level_accuracy": {...}},
    "same-book":     {...},
    "held-out-book": {...}
  },
  "cost_usd": null,
  "date": "2026-11-13",
  "by": "WeBuddhist",
  "report": "https://github.com/BuddhistAI/toc-extraction-tibetan/blob/main/REPORT.md"
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `schema` | yes | `buddhist-benchmarks/result@1`. |
| `task`, `language` | yes | Must match the folder. |
| `data_version`, `scorer_version` | yes | Exact semver of the data set and scorer. Rows are only ranked against rows on the same data version. |
| `skill`, `variant`, `skill_version` | yes | The skill's name in buddhist-skills, the variant name (a key in `skills.json`), and its `metadata.version`. |
| `skill_ref` | yes | `owner/repo@commit:path` of exactly what was run. |
| `model` | yes | Model ID; must be in `models.json`. |
| `repeats` | yes | How many times the whole set was run. |
| `headline` | yes | The task's headline metric (from TASK.md). |
| `scores` | yes | Per split, per metric: `mean`, `std` (sample standard deviation over repeats, 0 for one repeat) and `runs`. `all` is required; other splits are the data set's subsets (`metadata.subset` in `test.jsonl`). |
| `cost_usd` | yes | Total API cost of all repeats, or `null` if not recorded. |
| `date`, `by` | yes | Date of the run and who ran it. |
| `temperature`, `harness`, `report`, `notes` | no | Run settings, a link to a write-up, free text. |

## skills.json

One per task and language. `skills.<variant>` has `status` (`promoted`, `challenger`, `baseline` or `reference`, the last for runs that can't ship as this task's skill), `ships`, `approach` (two sentences on what makes it different), `made_by` and `source` (a link to the skill at the tested commit). `promoted` names the variant in buddhist-skills; `notes` and `splits` are shown on the site.

## Adding a result

1. Run the skill on the data set and score it with the task's scorer, at least 3 repeats for models with a fixed temperature.
2. Write `runs/<run-id>/result.json` (labs can generate it, e.g. toc-extraction-tibetan `scripts/to_result_json.py`), and add the variant to `skills.json` if it is new.
3. Run `python3 scripts/build_leaderboards.py` and `python3 scripts/check.py`, then commit. On `main`, CI rebuilds the site.

## BuddhistBench

BuddhistBench model runs live in [buddhist-bench](https://github.com/BuddhistAI/buddhist-bench) in their own format (its `docs/results.md`: `run.json` + `scores.json`). The site reads them at build time and skips dry runs and example splits.

## External leaderboards

`external.json` lists leaderboards other organizations run, such as BDRC's Tibetan OCR leaderboard. The overview shows each as a card that links out; on CI the build reads their live top rows (`--fetch-external`, one parser per site). Nothing there is scored here.

Display options in `skills.json`: `name` shows a readable name instead of the variant id (the id stays in `result.json` and skill refs), and `hidden: true` keeps a skill's results in the repo but leaves it off every leaderboard.

Before and after: `baseline` in `skills.json` names the no-skill run (the model with only a plain task prompt). It is shown as the "before" row, never ranked, and every skill's gain is its score minus the baseline's on the same model and passages.
