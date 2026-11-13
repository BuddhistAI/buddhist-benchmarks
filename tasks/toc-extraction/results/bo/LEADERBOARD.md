# toc-extraction: Tibetan (`bo`) leaderboard

Headline metric: `structure_f1` (see [TASK.md](../../TASK.md)). Higher is better. Rows are only ranked against rows on the same data version and model ([VERSIONING.md](../../../../VERSIONING.md)). Values are the mean ± standard deviation of 3 runs at temperature 1.0. Each run folder holds the outputs of one of those runs.

Currently promoted in buddhist-skills: [`toc-extraction-tibetan`](https://github.com/BuddhistAI/buddhist-skills/tree/main/skills/toc-extraction-tibetan) 1.0.0 (variant sabcad-outliner-toc), promoted 2026-11-13. Full report: [toc-extraction-tibetan REPORT.md](https://github.com/BuddhistAI/toc-extraction-tibetan/blob/main/REPORT.md).

## Data 1.0.0 (`data/bo/v1/`)

`sabcad-outliner` and `sabcad-outliner+script` are a .docx outliner skill run through a benchmark adapter. They can't ship as a TOC skill as they are; `sabcad-outliner-toc` is the shippable form.

### claude-haiku-5-5

| Rank | Skill | Skill ref | Data | Model | structure_f1 | title_f1 | level_acc | Date | Run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | sabcad-outliner 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner` | 1.0.0 | claude-haiku-5-5 | 0.859 ± 0.017 | 0.919 ± 0.015 | 0.935 ± 0.029 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-sabcad-outliner-1.0.0-3253458-haiku-5-5/) |
| 2 | sabcad-outliner+script 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner` | 1.0.0 | claude-haiku-5-5 | 0.831 ± 0.012 | 0.888 ± 0.011 | 0.936 ± 0.003 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-sabcad-outliner+script-1.0.0-3253458-haiku-5-5/) |
| 3 | gepa-v1 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/gepa-v1` | 1.0.0 | claude-haiku-5-5 | 0.824 ± 0.012 | 0.940 ± 0.010 | 0.877 ± 0.010 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-gepa-v1-1.0.0-3253458-haiku-5-5/) |
| 4 | sabcad-outliner-toc 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner-toc` | 1.0.0 | claude-haiku-5-5 | 0.823 ± 0.022 | 0.893 ± 0.020 | 0.922 ± 0.009 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-sabcad-outliner-toc-1.0.0-3253458-haiku-5-5/) |
| 5 | seed 0.1.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/seed` | 1.0.0 | claude-haiku-5-5 | 0.741 ± 0.022 | 0.880 ± 0.007 | 0.842 ± 0.029 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-seed-0.1.0-3253458-haiku-5-5/) |

### claude-sonnet-5-5

| Rank | Skill | Skill ref | Data | Model | structure_f1 | title_f1 | level_acc | Date | Run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | sabcad-outliner+script 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner` | 1.0.0 | claude-sonnet-5-5 | 0.968 ± 0.001 | 0.973 ± 0.001 | 0.995 ± 0.000 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-sabcad-outliner+script-1.0.0-3253458-sonnet-5-5/) |
| 2 | sabcad-outliner-toc 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner-toc` | 1.0.0 | claude-sonnet-5-5 | 0.962 ± 0.007 | 0.967 ± 0.007 | 0.995 ± 0.000 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-sabcad-outliner-toc-1.0.0-3253458-sonnet-5-5/) |
| 3 | seed 0.1.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/seed` | 1.0.0 | claude-sonnet-5-5 | 0.951 ± 0.005 | 0.958 ± 0.001 | 0.992 ± 0.004 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-seed-0.1.0-3253458-sonnet-5-5/) |
| 4 | gepa-v1 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/gepa-v1` | 1.0.0 | claude-sonnet-5-5 | 0.949 ± 0.020 | 0.974 ± 0.006 | 0.974 ± 0.015 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-gepa-v1-1.0.0-3253458-sonnet-5-5/) |
| 5 | sabcad-outliner 1.0.0 | `BuddhistAI/toc-extraction-tibetan@3253458:variants/sabcad-outliner` | 1.0.0 | claude-sonnet-5-5 | 0.946 ± 0.014 | 0.972 ± 0.002 | 0.973 ± 0.014 | 2026-11-13 | [run](./runs/2026-11-13-toc-extraction-tibetan-sabcad-outliner-1.0.0-3253458-sonnet-5-5/) |
