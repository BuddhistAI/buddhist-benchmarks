# Runs

One folder per run: `<YYYY-MM-DD>-<skill-name>-<short-commit>-<model>/`, containing:

- `outputs/<item-id>.json`: what the skill produced for each input.
- `scores.json`: the output of `scorer/score.py`.
- `run.json`: what was run, so anyone can repeat it:

```json
{
  "task": "toc-extraction",
  "language": "bo",
  "data": "v1",
  "skill": "toc-extraction-tibetan",
  "skill_ref": "BuddhistAI/buddhist-skills@3f2a1c9:drafts/toc-extraction-tibetan/webuddhist-v1",
  "model": "<model id>",
  "harness": "<agent and version, e.g. Claude Code 2.x>",
  "date": "2026-11-13",
  "by": "<organization>"
}
```
