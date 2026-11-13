#!/usr/bin/env python3
"""Publish released data sets (and the results table) from GitHub to Hugging Face.

GitHub is the source of truth. Each release tag <task>/<lang>@<version> becomes a
Hugging Face dataset repo BuddhistAI/<task>-<language name> (language names from
buddhist-skills languages.json), with a matching tag v<version>. The repo's main
branch always holds the newest version; older versions stay loadable by tag:

    load_dataset("BuddhistAI/toc-extraction-tibetan", revision="v2.0.0")

python3 scripts/hf_sync.py plan                 # releases, their HF repo, publishable or not
python3 scripts/hf_sync.py export TAG --out DIR # build the HF folder for one release tag
python3 scripts/hf_sync.py results --out DIR    # build the results dataset (all result.json rows)
python3 scripts/hf_sync.py validate DIR         # check the card and load it with `datasets`
python3 scripts/hf_sync.py check                # export + validate every release and the results (dry run)
python3 scripts/hf_sync.py push                 # publish what Hugging Face does not have yet (needs HF_TOKEN)

Run by .github/workflows/hf-sync.yml. Example sets (version `example`) are never published.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HF_ORG = "BuddhistAI"
GH_REPO = "BuddhistAI/buddhist-benchmarks"
SITE = "https://buddhistai.github.io/buddhist-benchmarks/"
RESULTS_REPO = f"{HF_ORG}/buddhist-benchmarks-results"
LANGUAGES_URL = "https://raw.githubusercontent.com/BuddhistAI/buddhist-skills/main/languages.json"
TAG_RE = re.compile(r"^(?P<task>[a-z0-9-]+)/(?P<lang>[a-z]{2,3}(?:-[A-Za-z0-9]+)*)@(?P<version>\d+\.\d+\.\d+)$")
# Files shipped next to the data so the HF repo is usable on its own.
EXTRA = {"TASK.md": "tasks/{task}/TASK.md", "CHANGELOG.md": "tasks/{task}/CHANGELOG.md",
         "scorer/score.py": "tasks/{task}/scorer/score.py", "LICENSE": "LICENSE"}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def semver(v):
    return tuple(int(x) for x in v.split("."))


def language_names():
    local = ROOT.parent / "buddhist-skills" / "languages.json"
    try:
        data = json.loads(local.read_text(encoding="utf-8")) if local.exists() else \
            json.load(urllib.request.urlopen(LANGUAGES_URL, timeout=20))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"could not read languages.json ({e})")
    return {l["code"]: l["name"] for l in data["languages"]}


def releases():
    """Every release tag, oldest version first, with its HF repo and whether it can be published."""
    names = language_names()
    out = []
    for tag in git("tag", "--list", "*@*").split():
        m = TAG_RE.match(tag)
        if not m:
            continue
        task, lang, version = m["task"], m["lang"], m["version"]
        folder = f"tasks/{task}/data/{lang}/v{version.split('.')[0]}"
        files = git("ls-tree", "-r", "--name-only", tag, folder).split()
        reason = None
        if lang not in names:
            reason = f"language {lang!r} not in languages.json"
        elif f"{folder}/README.md" not in files or not any(f.endswith(".jsonl") for f in files):
            reason = "not in the standard format (README.md card + JSONL) at this tag"
        out.append({"tag": tag, "task": task, "lang": lang, "version": version, "folder": folder,
                    "repo": f"{HF_ORG}/{task}-{names.get(lang, lang)}", "hf_tag": f"v{version}",
                    "commit": git("rev-list", "-n1", tag).strip(), "skip": reason})
    return sorted(out, key=lambda r: (r["repo"], semver(r["version"])))


def front_matter(text):
    if not text.startswith("---\n"):
        sys.exit("README.md has no YAML front matter")
    end = text.index("\n---", 4)
    return text[4:end], text[end + 4:].lstrip("\n")


def rewrite_links(body, folder, commit, kept):
    """Relative links: keep them if the file ships to HF, else point at GitHub at the release commit."""
    def fix(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"^[a-z]+:|^#", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        resolved = os.path.normpath(os.path.join(folder, path))
        if resolved.startswith(folder + "/") and os.path.relpath(resolved, folder) in kept:
            return f"[{label}]({os.path.relpath(resolved, folder)}{'#' + anchor if anchor else ''})"
        for hf_name, src in EXTRA.items():
            if resolved == src.format(task=folder.split("/")[1]):
                return f"[{label}]({hf_name}{'#' + anchor if anchor else ''})"
        kind = "tree" if not os.path.splitext(resolved)[1] else "blob"
        return f"[{label}](https://github.com/{GH_REPO}/{kind}/{commit}/{resolved}{'#' + anchor if anchor else ''})"
    return re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", fix, body)


def export(rel, out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "src.tar"
        paths = [rel["folder"]] + [p.format(task=rel["task"]) for p in EXTRA.values()]
        present = set(git("ls-tree", "-r", "--name-only", rel["tag"]).split())
        paths = [p for p in paths if p == rel["folder"] or p in present]
        git("archive", "--format=tar", "-o", str(archive), rel["tag"], *paths)
        with tarfile.open(archive) as t:
            t.extractall(tmp, filter="data")
        src = Path(tmp) / rel["folder"]
        kept = sorted(str(p.relative_to(src)) for p in src.rglob("*") if p.is_file() and p.name != "README.md")
        for name in kept:
            (out / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src / name, out / name)
        for hf_name, path in EXTRA.items():
            p = Path(tmp) / path.format(task=rel["task"])
            if p.exists():
                (out / hf_name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, out / hf_name)
        yaml, body = front_matter((src / "README.md").read_text(encoding="utf-8"))
    short = rel["commit"][:7]
    banner = (
        f"> **Source of truth:** [{GH_REPO}](https://github.com/{GH_REPO}/tree/{rel['commit']}/{rel['folder']}), "
        f"release `{rel['tag']}` (commit `{short}`). This copy is published automatically; report errors and "
        f"propose fixes on GitHub. Leaderboard: {SITE}\n>\n"
        f"> ```python\n> from datasets import load_dataset\n"
        f"> ds = load_dataset(\"{rel['repo']}\", revision=\"{rel['hf_tag']}\")  # pin the version you report\n> ```\n"
        f">\n> Score predictions with `scorer/score.py` (same scorer as the leaderboard). Report the data version "
        f"({rel['version']}) with every result; do not compare results across versions.\n"
    )
    body = rewrite_links(body, rel["folder"], rel["commit"], kept)
    lines = body.split("\n", 1)
    body = lines[0] + "\n\n" + banner + ("\n" + lines[1] if len(lines) > 1 else "")
    (out / "README.md").write_text(f"---\n{yaml}\n---\n\n{body}", encoding="utf-8")
    return out


def results(out):
    """One row per leaderboard run, from tasks/*/results/*/runs/*/result.json and skills.json."""
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "data").mkdir(parents=True)
    # Last commit that touched results, so an unchanged table makes no new Hugging Face commit.
    head = git("log", "-1", "--format=%H", "--", "tasks/*/results", "docs/results.md").strip()
    rows = []
    for f in sorted(ROOT.glob("tasks/*/results/*/runs/*/result.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        skills = json.loads((f.parents[2] / "skills.json").read_text(encoding="utf-8")) if (f.parents[2] / "skills.json").exists() else {}
        s = skills.get("skills", {}).get(r.get("variant"), {})
        if s.get("hidden"):
            continue
        h = r["scores"]["all"][r["headline"]] if "all" in r["scores"] else {}
        rows.append({
            "run_id": f.parent.name, "task": r["task"], "language": r["language"],
            "data_version": r["data_version"], "scorer_version": r["scorer_version"],
            "skill": r["skill"], "variant": r["variant"], "skill_name": s.get("name", r["variant"]),
            "skill_status": s.get("status"), "skill_version": r["skill_version"], "skill_ref": r["skill_ref"],
            "model": r["model"], "repeats": r["repeats"], "headline": r["headline"],
            "headline_mean": h.get("mean"), "headline_std": h.get("std"),
            "scores": json.dumps(r["scores"], ensure_ascii=False),
            "input_tokens": r.get("usage", {}).get("input_tokens"), "output_tokens": r.get("usage", {}).get("output_tokens"),
            "usage_estimated": r.get("usage", {}).get("estimated"), "cost_usd": r.get("cost_usd"),
            "date": r["date"], "by": r["by"], "report": r.get("report"),
            "result_url": f"https://github.com/{GH_REPO}/blob/{head}/{f.relative_to(ROOT)}",
        })
    with (out / "data" / "runs.jsonl").open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    card = f"""---
license: mit
pretty_name: BuddhistAI skill leaderboard results
tags:
- buddhism
- leaderboard
- benchmark-results
configs:
- config_name: default
  data_files:
  - split: runs
    path: data/runs.jsonl
---

# BuddhistAI skill leaderboard results

Every run on the BuddhistAI skill leaderboards, one row per skill variant × model × data version. Generated from the `result.json` files in [{GH_REPO}](https://github.com/{GH_REPO}) (commit `{head[:7]}`); do not edit here.

- **Leaderboard site:** {SITE}
- **Data sets:** each benchmark is its own dataset in the [{HF_ORG}](https://huggingface.co/{HF_ORG}) org, tagged by version.
- **Columns:** see [docs/results.md](https://github.com/{GH_REPO}/blob/{head}/docs/results.md). `scores` is the full per-subset score object as a JSON string; `headline_mean` is the headline metric on all items. `skill_ref` pins the exact skill commit that was run.
- **Comparing rows:** only rows with the same `task`, `language` and `data_version` are comparable.

{len(rows)} runs. License: MIT. Founded and maintained by WeBuddhist.
"""
    (out / "README.md").write_text(card, encoding="utf-8")
    return out


def validate(folder):
    """Card metadata parses, every data file exists, and `datasets` loads every config with the declared counts."""
    from huggingface_hub import DatasetCard
    import datasets
    folder = Path(folder)
    card = DatasetCard.load(folder / "README.md")
    meta = card.data.to_dict()
    errs = []
    if not meta.get("license"):
        errs.append("card has no license")
    declared = {s["name"]: s.get("num_examples") for s in (meta.get("dataset_info") or {}).get("splits", [])}
    for cfg in meta.get("configs", []):
        for df in cfg["data_files"]:
            if not (folder / df["path"]).exists():
                errs.append(f"{df['path']} listed in the card but missing")
        if errs:
            break
        ds = datasets.load_dataset(str(folder), cfg["config_name"])
        for split, d in ds.items():
            if declared.get(split) not in (None, len(d)):
                errs.append(f"{cfg['config_name']}/{split}: card says {declared[split]} rows, loaded {len(d)}")
            print(f"  {cfg['config_name']}/{split}: {len(d)} rows, columns {d.column_names}")
    if errs:
        sys.exit(f"{folder}: " + "; ".join(errs))
    return meta


def hf_tags(api, repo):
    from huggingface_hub.utils import RepositoryNotFoundError
    try:
        return {t.name for t in api.list_repo_refs(repo, repo_type="dataset").tags}
    except RepositoryNotFoundError:
        return set()


def upload(api, folder, repo, message, tag=None):
    api.create_repo(repo, repo_type="dataset", exist_ok=True)
    # delete_patterns removes files the new version no longer has (.gitattributes is always kept).
    api.upload_folder(folder_path=str(folder), repo_id=repo, repo_type="dataset",
                      commit_message=message, delete_patterns=["*", "**/*"])
    if tag:
        api.create_tag(repo, tag=tag, repo_type="dataset", tag_message=message, exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    e = sub.add_parser("export"); e.add_argument("tag"); e.add_argument("--out", required=True)
    r = sub.add_parser("results"); r.add_argument("--out", required=True)
    v = sub.add_parser("validate"); v.add_argument("folder")
    c = sub.add_parser("check"); c.add_argument("--out", default="build/hf")
    p = sub.add_parser("push"); p.add_argument("--out", default="build/hf")
    p.add_argument("--tag", help="only this release tag"); p.add_argument("--no-results", action="store_true")
    args = ap.parse_args()

    rels = releases()
    if args.cmd == "plan":
        for x in rels:
            print(f"{x['tag']:32} -> {x['repo']}@{x['hf_tag']}" + (f"  SKIP: {x['skip']}" if x["skip"] else ""))
    elif args.cmd == "export":
        rel = next((x for x in rels if x["tag"] == args.tag), None) or sys.exit(f"no release tag {args.tag}")
        if rel["skip"]:
            sys.exit(f"{args.tag}: {rel['skip']}")
        print(export(rel, args.out))
    elif args.cmd == "results":
        print(results(args.out))
    elif args.cmd == "validate":
        validate(args.folder)
    elif args.cmd == "check":
        for x in rels:
            if x["skip"]:
                print(f"skip {x['tag']}: {x['skip']}")
                continue
            print(f"{x['tag']} -> {x['repo']}@{x['hf_tag']}")
            validate(export(x, Path(args.out) / x["tag"].replace("/", "_")))
        print(f"results -> {RESULTS_REPO}")
        validate(results(Path(args.out) / "_results"))
        print("dry run OK: every release and the results table export and load")
    elif args.cmd == "push":
        token = os.environ.get("HF_TOKEN")
        if not token:
            print("HF_TOKEN not set: nothing published (run `check` for a dry run)")
            return
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        by_repo = {}
        for x in rels:
            if not x["skip"] and (not args.tag or x["tag"] == args.tag):
                by_repo.setdefault(x["repo"], []).append(x)
        for repo, versions in by_repo.items():
            have = hf_tags(api, repo)
            todo = [x for x in versions if x["hf_tag"] not in have]
            for x in todo:
                print(f"publish {x['tag']} -> {repo}@{x['hf_tag']}")
                folder = export(x, Path(args.out) / x["tag"].replace("/", "_"))
                validate(folder)
                upload(api, folder, repo, f"Release {x['tag']} ({x['commit'][:7]})", x["hf_tag"])
            newest = max((x for x in rels if x["repo"] == repo and not x["skip"]), key=lambda x: semver(x["version"]))
            if todo and todo[-1] is not newest:
                # An older version was back-filled: put the newest back on main.
                upload(api, export(newest, Path(args.out) / "_newest"), repo, f"Restore {newest['tag']} on main")
            if not todo:
                print(f"{repo}: up to date ({', '.join(sorted(have))})")
        if not args.no_results:
            folder = results(Path(args.out) / "_results")
            validate(folder)
            upload(api, folder, RESULTS_REPO, f"Results at {git('rev-parse', '--short', 'HEAD').strip()}")
            print(f"results -> {RESULTS_REPO}")


if __name__ == "__main__":
    main()
