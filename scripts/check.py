#!/usr/bin/env python3
"""Check the benchmark repo layout.

python3 scripts/check.py              # local checks
python3 scripts/check.py --languages  # also check data folder codes against buddhist-skills languages.json
"""
import json
import subprocess
import tempfile
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES_URL = "https://raw.githubusercontent.com/BuddhistAI/buddhist-skills/main/languages.json"
README_FIELDS = ["Version", "Purpose", "Items", "Source and license", "References made by"]

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
            front = text.split("\n---", 1)[0] if text.startswith("---\n") else ""
            if "\nlicense:" not in front or "data_files" not in front:
                errors.append(f"{rel}/README.md: needs Hugging Face YAML front matter with license and configs/data_files")
            if d.name != "example":
                for field in README_FIELDS:
                    if f"**{field}:**" not in text:
                        errors.append(f"{rel}/README.md: missing '**{field}:**'")
        for old in ("inputs", "references", "items.json"):
            if (d / old).exists():
                errors.append(f"{rel}: old layout ({old}); data sets are one JSONL file (see CONTRIBUTING.md)")
        files = sorted(d.glob("*.jsonl"))
        if not files:
            errors.append(f"{rel}: no .jsonl data file")
        for f in files:
            item_ids = []
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"{rel}/{f.name}:{n}: not JSON ({e})")
                    continue
                missing = [k for k in ("id", "input", "target") if k not in row]
                if missing:
                    errors.append(f"{rel}/{f.name}:{n}: missing {', '.join(missing)}")
                item_ids.append(row.get("id"))
            if len(item_ids) != len(set(item_ids)):
                errors.append(f"{rel}/{f.name}: duplicate ids")
            # The scorer must give a perfect score to the answers themselves.
            with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        row = json.loads(line)
                        tmp.write(json.dumps({"id": row["id"], "output": row["target"]}, ensure_ascii=False) + "\n")
            out = subprocess.run(
                [sys.executable, str(tdir / "scorer" / "score.py"), "--language", code, "--data", str(f), "--predictions", tmp.name],
                capture_output=True, text=True,
            )
            Path(tmp.name).unlink()
            if out.returncode != 0:
                errors.append(f"{rel}/{f.name}: scorer failed: {out.stderr.strip()[-300:]}")
            else:
                sc = json.loads(out.stdout)
                if sc[sc["headline"]] != 1.0:
                    errors.append(f"{rel}/{f.name}: answers do not score 1.0 against themselves ({sc['headline']}={sc[sc['headline']]})")
        if d.name != "example" and not (tdir / "results" / code / "skills.json").exists():
            errors.append(f"tasks/{tid}/results/{code}: missing skills.json")

# Leaderboards are generated from result.json files and must be up to date.
out = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_leaderboards.py"), "--check"], capture_output=True, text=True)
if out.returncode != 0:
    errors.append("leaderboards: " + out.stdout.strip())

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
