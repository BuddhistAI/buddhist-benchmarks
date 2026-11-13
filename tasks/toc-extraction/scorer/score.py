#!/usr/bin/env python3
"""Score toc-extraction predictions against a data set.

python3 score.py --data ../data/bo/v2/test.jsonl --predictions predictions.jsonl [--language bo] > scores.json

--data          the data set: JSONL, one item per line: {"id", "input", "target": {"entries": [...]}, "metadata"}.
--predictions   what the skill produced, either a JSONL file of {"id", "output": {"entries": [...]}} lines,
                or a folder of <id>.json files each holding {"entries": [...]}. Missing items score as empty.
Formats: ../TASK.md. Two matching modes, chosen per item:
- position: every target entry has "start" (a character offset into the input). Predicted entries are placed by
  their "start", or by finding their "anchor" verbatim in the input, and match a target entry within TOL chars.
- title: otherwise, titles are matched in order by normalized similarity.
Reports micro-averaged metrics over all items, and per metadata.subset. Deterministic, standard library only.
"""
import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SCORER_VERSION = "2.0.0"  # 2.0.0: reads the JSONL format; matching and metrics unchanged from 1.0.0
THRESHOLD = 0.9
TOL = 3  # chars of slack in position mode (e.g. a missing leading ༈ and space)


def normalize(title, language):
    t = unicodedata.normalize("NFC", title)
    if language == "bo":
        t = re.sub(r"^[༁-༊།-༔\s]+", "", t)  # yig mgo, shad, etc. at the start
        t = re.sub(r"[་༌།-༔\s]+$", "", t)  # tsheg and shad at the end
        t = re.sub(r"[།-༔]", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def similar(a, b):
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def match(pred, ref, language):
    """Order-preserving one-to-one matching (longest common subsequence on similar titles)."""
    p = [normalize(e["title"], language) for e in pred]
    r = [normalize(e["title"], language) for e in ref]
    n, m = len(p), len(r)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if similar(p[i], r[j]) >= THRESHOLD:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    pairs, i, j = [], 0, 0
    while i < n and j < m:
        if similar(p[i], r[j]) >= THRESHOLD and dp[i][j] == 1 + dp[i + 1][j + 1]:
            pairs.append((i, j))
            i, j = i + 1, j + 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def locate(pred, text):
    """Start offset of each predicted entry: its "start", else its "anchor" found verbatim after the previous one."""
    out, cur = [], 0
    for e in pred:
        if isinstance(e.get("start"), int):
            out.append(e["start"])
            continue
        a = (e.get("anchor") or "").strip()
        p = text.find(a, cur) if a else -1
        out.append(p if p >= 0 else None)
        if p >= 0:
            cur = p + 1
    return out


def match_positions(pred, ref, text):
    """Greedy one-to-one matching on start offset (within TOL), in reading order."""
    starts = locate(pred, text)
    used, pairs = set(), []
    for i, ps in enumerate(starts):
        if ps is None:
            continue
        best = None
        for j, r in enumerate(ref):
            if j in used or abs(r["start"] - ps) > TOL:
                continue
            if best is None or abs(r["start"] - ps) < abs(ref[best]["start"] - ps):
                best = j
        if best is not None:
            used.add(best)
            pairs.append((i, best))
    return pairs


def f1(tp, n_pred, n_ref):
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_ref if n_ref else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def score_item(pred, ref, language, text=None):
    position = bool(ref) and all(isinstance(e.get("start"), int) for e in ref) and text is not None
    pairs = match_positions(pred, ref, text) if position else match(pred, ref, language)
    level_ok = sum(1 for i, j in pairs if pred[i].get("level") == ref[j].get("level"))
    return {"n_pred": len(pred), "n_ref": len(ref), "matched": len(pairs), "matched_level": level_ok,
            "mode": "position" if position else "title"}


def load_predictions(path):
    if path.is_dir():
        return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in path.glob("*.json")}
    preds = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            preds[row["id"]] = row["output"]
    return preds


def metrics(t):
    return {
        "structure_f1": round(f1(t["matched_level"], t["n_pred"], t["n_ref"]), 4),
        "title_f1": round(f1(t["matched"], t["n_pred"], t["n_ref"]), 4),
        "level_accuracy": round(t["matched_level"] / t["matched"], 4) if t["matched"] else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=Path, help="data set JSONL (id, input, target, metadata)")
    ap.add_argument("--predictions", required=True, type=Path, help="predictions JSONL (id, output) or a folder of <id>.json")
    ap.add_argument("--language", default="", help="ISO code of the data set, for script-specific normalization")
    args = ap.parse_args()
    preds = load_predictions(args.predictions)

    keys = ("n_pred", "n_ref", "matched", "matched_level")
    items, totals, subsets = {}, dict.fromkeys(keys, 0), {}
    for line in args.data.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        ref = row["target"]["entries"]
        out = preds.get(row["id"])
        s = score_item(out["entries"] if out else [], ref, args.language, row["input"])
        s["missing_output"] = out is None
        items[row["id"]] = s
        sub = subsets.setdefault((row.get("metadata") or {}).get("subset") or "all", dict.fromkeys(keys, 0))
        for k in keys:
            totals[k] += s[k]
            sub[k] += s[k]

    result = {
        "task": "toc-extraction",
        "scorer_version": SCORER_VERSION,
        "headline": "structure_f1",
        **metrics(totals),
        "totals": totals,
        "by_subset": {k: {**metrics(v), "totals": v} for k, v in sorted(subsets.items())} if len(subsets) > 1 else {},
        "items": items,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
