# Publishing to Hugging Face

GitHub is the source of truth: data, scorers, reviews and every change happen here through pull requests. Each released data set is then published automatically to the [BuddhistAI](https://huggingface.co/BuddhistAI) organization on Hugging Face, so researchers can find it there and load it with `datasets`. Nothing is edited on Hugging Face by hand.

## What goes where

| GitHub | Hugging Face |
| --- | --- |
| release tag `<task>/<lang>@<version>`, e.g. `toc-extraction/bo@2.0.0` | dataset `BuddhistAI/<task>-<language>`, e.g. [`BuddhistAI/toc-extraction-tibetan`](https://huggingface.co/datasets/BuddhistAI/toc-extraction-tibetan), tag `v2.0.0` |
| `tasks/<task>/data/<lang>/v<major>/` at that tag | the JSONL files and the README dataset card, with relative links pointed at GitHub and a header naming the source commit |
| `tasks/<task>/TASK.md`, `CHANGELOG.md`, `scorer/score.py`, `LICENSE` | copied next to the data, so the dataset can be scored on its own |
| every `result.json` (with `skills.json` display names) | [`BuddhistAI/buddhist-benchmarks-results`](https://huggingface.co/datasets/BuddhistAI/buddhist-benchmarks-results), one row per run, linking to the [leaderboard site](https://buddhistai.github.io/buddhist-benchmarks/) |

The language part of the name is the full English name from buddhist-skills [`languages.json`](https://github.com/BuddhistAI/buddhist-skills/blob/main/languages.json), the same suffix the skill uses (`toc-extraction-tibetan`). The Hugging Face `main` branch always holds the newest version; every version stays loadable by its tag:

```python
from datasets import load_dataset
ds = load_dataset("BuddhistAI/toc-extraction-tibetan", revision="v2.0.0")  # pin the version you report
```

Example sets (`example/`) are never published. Tags from before the standard format (`toc-extraction/bo@1.0.0`) are skipped.

## How a release reaches Hugging Face

1. A pull request bumps a data set's version (README `**Version:**` line, task `CHANGELOG.md`; see [VERSIONING.md](../VERSIONING.md)) and is merged.
2. The `leaderboards` workflow ([pages.yml](../.github/workflows/pages.yml)) creates the missing release tag (`scripts/tag_releases.py`).
3. The `hf-sync` workflow ([hf-sync.yml](../.github/workflows/hf-sync.yml)) runs when `leaderboards` finishes (tags pushed by the workflow token cannot start workflows themselves), on any tag pushed by a person, and by hand from the Actions tab.
4. It first does a dry run for every release: export from the tag, check the card, load every config with `datasets` and compare row counts with the card. Then, if the `HF_TOKEN` secret is set, it uploads each version Hugging Face does not have yet, tags it `v<version>`, and refreshes the results dataset. Without the secret it stops after the dry run and the run stays green.

Re-running is safe: versions already on Hugging Face are skipped, and an unchanged results table makes no new commit.

## The HF_TOKEN secret

One Hugging Face token with **write access to the BuddhistAI organization**, saved as the GitHub Actions secret `HF_TOKEN`. The workflow creates the dataset repos on first publish, so the token must be allowed to create repos in the org, not only push to existing ones.

- **Hugging Face:** simplest is a token of type **Write** (huggingface.co/settings/tokens → Create new token → Write) from an account with the admin or write role in BuddhistAI. A fine-grained token also works if, under the BuddhistAI org permissions, it may create repos and write their contents.
- **GitHub:** an organization secret covers every repo: BuddhistAI → Settings → Secrets and variables → Actions → New organization secret, name `HF_TOKEN`, repository access buddhist-benchmarks and buddhist-bench. A repository secret on each repo works too.

## Running it locally

```bash
pip install datasets huggingface_hub
python3 scripts/hf_sync.py plan                 # releases and their Hugging Face names
python3 scripts/hf_sync.py check                # dry run: export and load everything into build/hf
HF_TOKEN=... python3 scripts/hf_sync.py push    # publish what is missing (normally CI does this)
```
