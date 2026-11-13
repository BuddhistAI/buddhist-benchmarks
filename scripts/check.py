#!/usr/bin/env python3
"""Check the benchmark repo layout.

python3 scripts/check.py              # local checks
python3 scripts/check.py --languages  # also check data folder codes against buddhist-skills languages.json
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES_URL = "https://raw.githubusercontent.com/BuddhistAI/buddhist-skills/main/languages.json"
README_FIELDS = ["Purpose", "Items", "Source and license", "References made by"]

errors, warnings = [], []
index = json.loads((ROOT / "tasks" / "index.json").read_text(encoding="utf-8"))
ids = [t["id"] for t in index["tasks"]]
if len(ids) != len(set(ids)):
    errors.append("tasks/index.json: duplicate task IDs")

codes_seen = set()
for task in index["tasks"]:
    tid, status = task["id"], task.get("status")
    tdir = ROOT / "tasks" / tid
    if status not in ("active", "planned"):
        errors.append(f"{tid}: status must be active or planned")
    if status == "planned":
        continue
    for required in ["TASK.md", "scorer/score.py"]:
        if not (tdir / required).exists():
            errors.append(f"tasks/{tid}: missing {required}")
    data_dirs = sorted(p for p in (tdir / "data").glob("*/*") if p.is_dir())
    if not data_dirs:
        errors.append(f"tasks/{tid}: active task has no data set")
    for d in data_dirs:
        rel = d.relative_to(ROOT)
        code = d.parent.name
        codes_seen.add(code)
        readme = d / "README.md"
        if not readme.exists():
            errors.append(f"{rel}: missing README.md")
        else:
            text = readme.read_text(encoding="utf-8")
            for field in README_FIELDS:
                if f"**{field}:**" not in text:
                    errors.append(f"{rel}/README.md: missing '**{field}:**'")
        inputs = {p.stem for p in (d / "inputs").glob("*")}
        refs = {p.stem for p in (d / "references").glob("*")}
        if not inputs:
            errors.append(f"{rel}: no inputs")
        if inputs != refs:
            errors.append(f"{rel}: inputs and references do not match: {sorted(inputs ^ refs)}")
        if not (tdir / "results" / code / "LEADERBOARD.md").exists():
            errors.append(f"tasks/{tid}/results/{code}: missing LEADERBOARD.md")
        # The scorer must give a perfect score to the references themselves.
        out = subprocess.run(
            [sys.executable, str(tdir / "scorer" / "score.py"), "--language", code, "--outputs", str(d / "references"), "--references", str(d / "references")],
            capture_output=True, text=True,
        )
        if out.returncode != 0:
            errors.append(f"{rel}: scorer failed: {out.stderr.strip()[-300:]}")
        else:
            s = json.loads(out.stdout)
            if s[s["headline"]] != 1.0:
                errors.append(f"{rel}: references do not score 1.0 against themselves ({s['headline']}={s[s['headline']]})")

for p in sorted((ROOT / "tasks").iterdir()):
    if p.is_dir() and p.name not in ids:
        errors.append(f"tasks/{p.name}: folder not listed in tasks/index.json")

if "--languages" in sys.argv:
    try:
        with urllib.request.urlopen(LANGUAGES_URL, timeout=20) as r:
            known = {l["code"] for l in json.load(r)["languages"]}
        for code in sorted(codes_seen - known):
            errors.append(f"language code {code!r} is not in buddhist-skills languages.json")
    except Exception as e:
        warnings.append(f"could not fetch languages.json ({e}); codes not checked")

for w in warnings:
    print(f"warning: {w}")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(ids)} task(s), {len(codes_seen)} language(s) with data")
