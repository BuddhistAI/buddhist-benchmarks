# Evaluate your solution

Built a tool, a skill, a prompt or a model that works with Buddhist texts? Score it on an open benchmark here and it appears on the [leaderboard](https://buddhistai.github.io/buddhist-benchmarks/) next to everything else, with its score and cost. Anyone can submit; your code can stay in your own repo.

## 1. Pick a benchmark

| You built | Use |
| --- | --- |
| A tool or skill for a text task (TOC extraction, alignment, cleanup, ...) | A task here: [tasks/index.json](tasks/index.json), current coverage in [STATE.md](STATE.md) |
| A model or assistant that answers questions about Buddhism | [BuddhistBench](https://github.com/BuddhistAI/buddhist-bench) (submission steps in its [docs/results.md](https://github.com/BuddhistAI/buddhist-bench/blob/main/docs/results.md)) |
| Something no benchmark covers yet | Propose a new task (step 4) |

Each task's `TASK.md` explains the input, the expected output and the metric. Each data set is one standard JSONL file (`id`, `input`, `target`, `metadata`) that also loads with Hugging Face `datasets`.

## 2. Run and score

Run your solution on every item's `input` and save `predictions.jsonl`, one line per item: `{"id": ..., "output": ...}`. Then score it with the task's own scorer:

```bash
python3 tasks/<task>/scorer/score.py --language <code> \
  --data tasks/<task>/data/<code>/v<major>/test.jsonl \
  --predictions predictions.jsonl > scores.json
```

Run at least 3 times if your solution is not deterministic. Never tune on the test set.

## 3. Submit

Open a pull request that adds `tasks/<task>/results/<code>/runs/<run>/` with:

- `result.json`: one leaderboard row (format and an example in [docs/results.md](docs/results.md)), citing the exact commit of your solution, the model, the data version and the token usage, so cost can be compared fairly;
- your outputs and `scores.json`, so anyone can re-score them;
- a line for your solution in that language's `skills.json`, with a short description of the approach and who made it.

Run `python3 scripts/check.py`. Once merged, the leaderboards and [STATE.md](STATE.md) rebuild themselves. If your solution is the best shippable one, it can be promoted to [buddhist-skills](https://github.com/BuddhistAI/buddhist-skills) so people can install it.

Closed or commercial tools are welcome too: include the outputs and say in `skills.json` how others can get the tool.

## 4. Propose a new benchmark

If your work is on a task or language that has no benchmark yet, that is a gap worth filling. Start a thread in [Discussions](https://github.com/orgs/BuddhistAI/discussions) or open an issue here with the task, a few example inputs and outputs, and how it should be scored. Adding test data for an existing task is described in [CONTRIBUTING.md](CONTRIBUTING.md).

Running your own leaderboard elsewhere? Add it to [external.json](external.json) and it is shown on our overview, linked to yours.
