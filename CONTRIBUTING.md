# Contributing

You do not need to write code to help. Besides adding data and results (below), you can:

- **Review a benchmark as an expert.** Check the items and correct answers in a field you know. [Review a benchmark](https://github.com/BuddhistAI/buddhist-benchmarks/issues/new?template=expert-review.yml). You are credited by name in the dataset card, and a full review moves the benchmark up to maturity level 3, Reviewed.
- **Donate compute or API credits.** Evaluations cost money; supporters pay for them, so testing is free for everyone. [Donate compute or API credits](https://github.com/BuddhistAI/buddhist-benchmarks/issues/new?template=donate-compute.yml). A donation never changes a score or a ranking.
- **Propose a benchmark** from material your team already uses: [Propose a benchmark](https://github.com/BuddhistAI/buddhist-benchmarks/issues/new?template=propose-benchmark.yml).

New to this? The [tutorials](https://buddhistai.github.io/knowledge-base/learn/) teach the steps. Who decides what: [Governance](https://buddhistai.github.io/knowledge-base/governance.html).

## Add test data for your language

1. Create `tasks/<task>/data/<code>/v1/` with `test.jsonl` (one item per line: `id`, `input`, `target`, `metadata`; see the task's `TASK.md`) and a `README.md` dataset card: Hugging Face YAML front matter (license, language, `configs` pointing at `test.jsonl`), then version, purpose, number of items, source and license of the texts, who made the answers, any shared resource versions (with commit), and a worked example. [toc-extraction/bo/v2](./tasks/toc-extraction/data/bo/v2/README.md) is the template.
2. Data sets are versioned with semver (see [VERSIONING.md](./VERSIONING.md)): new corner cases are a minor bump, fixed references a patch bump, a scorer or format change a major bump (new `v<N>/` folder). Record every change in the task's `CHANGELOG.md`.
3. Create `tasks/<task>/results/<code>/skills.json` (see [docs/results.md](./docs/results.md)); `LEADERBOARD.md` is generated once the first result is in.
4. Run `python3 scripts/check.py`.
5. Once merged, CI tags the release (`<task>/<code>@<version>`) and publishes it to Hugging Face as `BuddhistAI/<task>-<language>`, tag `v<version>` ([docs/huggingface.md](./docs/huggingface.md)). Never edit the Hugging Face copy; change the data here and bump the version.

Prefer texts that represent real work: real OCR, real editions, real page layouts. 30 or more items is a good first set; say in the README how they were chosen.

## Submit a run

Add a run folder with a `result.json` ([docs/results.md](./docs/results.md)) and keep a [provenance record](https://buddhistai.github.io/knowledge-base/handbook/provenance.html) of the run in your own repo (not here), run `python3 scripts/build_leaderboards.py`, and open a PR. Include your outputs, so anyone can re-score them. Never edit `LEADERBOARD.md` or the README table by hand: they are generated, and CI rebuilds the site on every push to `main`.

## Propose a new task

Open an issue describing the task, an input/output format, and how it would be scored. Once agreed:

1. Add it to `tasks/index.json` (status `planned`).
2. Write `tasks/<task>/TASK.md` and `scorer/score.py`. The scorer must work for every language; put script-specific normalization in the scorer, keyed by language code.
3. Add a first data set, then set the status to `active`.

## Change a scorer

A scorer change can move every score. Bump `SCORER_VERSION` in `scorer/score.py` and in `TASK.md`, bump the major version of every data set of that task (see [VERSIONING.md](./VERSIONING.md)), re-score existing runs where outputs are available, and mention it in the PR.
