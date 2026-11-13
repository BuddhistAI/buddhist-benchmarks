#!/usr/bin/env python3
"""Print the release tags (<task>/<lang>@<version>) that the data sets on this commit should have.

python3 scripts/tag_releases.py          # one tag per line, read from each data folder's README **Version:** line
CI creates any that are missing (.github/workflows/pages.yml), so a version bump merged to main is tagged automatically.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for readme in sorted(ROOT.glob('tasks/*/data/*/v*/README.md')):
    m = re.search(r'\*\*Version:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+)', readme.read_text(encoding='utf-8'))
    if m:
        task, lang = readme.parts[-5], readme.parts[-3]
        print(f'{task}/{lang}@{m.group(1)}')
