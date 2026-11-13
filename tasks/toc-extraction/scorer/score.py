#!/usr/bin/env python3
"""Score toc-extraction outputs against references.

python3 score.py --outputs DIR --references DIR [--language bo] > scores.json

Each DIR holds <item-id>.json files in the format described in ../TASK.md.
Deterministic, standard library only.
"""
import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

THRESHOLD = 0.9


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


def f1(tp, n_pred, n_ref):
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_ref if n_ref else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def score_item(pred, ref, language):
    pairs = match(pred, ref, language)
    level_ok = sum(1 for i, j in pairs if pred[i].get("level") == ref[j].get("level"))
    return {"n_pred": len(pred), "n_ref": len(ref), "matched": len(pairs), "matched_level": level_ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs", required=True, type=Path)
    ap.add_argument("--references", required=True, type=Path)
    ap.add_argument("--language", default="", help="ISO code of the data set, for script-specific normalization")
    args = ap.parse_args()

    items, totals = {}, {"n_pred": 0, "n_ref": 0, "matched": 0, "matched_level": 0}
    for ref_path in sorted(args.references.glob("*.json")):
        ref = json.loads(ref_path.read_text(encoding="utf-8"))["entries"]
        out_path = args.outputs / ref_path.name
        pred = json.loads(out_path.read_text(encoding="utf-8"))["entries"] if out_path.exists() else []
        s = score_item(pred, ref, args.language)
        s["missing_output"] = not out_path.exists()
        items[ref_path.stem] = s
        for k in totals:
            totals[k] += s[k]

    result = {
        "task": "toc-extraction",
        "headline": "structure_f1",
        "structure_f1": round(f1(totals["matched_level"], totals["n_pred"], totals["n_ref"]), 4),
        "title_f1": round(f1(totals["matched"], totals["n_pred"], totals["n_ref"]), 4),
        "level_accuracy": round(totals["matched_level"] / totals["matched"], 4) if totals["matched"] else 0.0,
        "totals": totals,
        "items": items,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
