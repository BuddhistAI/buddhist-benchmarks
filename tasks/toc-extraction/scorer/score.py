#!/usr/bin/env python3
"""Score toc-extraction outputs against references.

python3 score.py --outputs DIR --references DIR [--inputs DIR] [--language bo] > scores.json

Each DIR holds <item-id>.json files in the format described in ../TASK.md.
Two matching modes, chosen per item:
- position: every reference entry has "start" (a character offset into the input). Predicted entries are placed by
  their "start", or by finding their "anchor" verbatim in the input, and match a reference entry within TOL chars.
  Needs the input text (--inputs, default: the "inputs" folder next to --references).
- title: otherwise, titles are matched in order by normalized similarity.
Deterministic, standard library only.
"""
import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SCORER_VERSION = "1.0.0"
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs", required=True, type=Path)
    ap.add_argument("--references", required=True, type=Path)
    ap.add_argument("--inputs", type=Path, help="input texts, for position mode (default: inputs/ next to --references)")
    ap.add_argument("--language", default="", help="ISO code of the data set, for script-specific normalization")
    args = ap.parse_args()
    inputs = args.inputs or args.references.parent / "inputs"

    items, totals = {}, {"n_pred": 0, "n_ref": 0, "matched": 0, "matched_level": 0}
    for ref_path in sorted(args.references.glob("*.json")):
        ref = json.loads(ref_path.read_text(encoding="utf-8"))["entries"]
        out_path = args.outputs / ref_path.name
        pred = json.loads(out_path.read_text(encoding="utf-8"))["entries"] if out_path.exists() else []
        in_path = inputs / f"{ref_path.stem}.txt"
        text = in_path.read_text(encoding="utf-8") if in_path.exists() else None
        s = score_item(pred, ref, args.language, text)
        s["missing_output"] = not out_path.exists()
        items[ref_path.stem] = s
        for k in totals:
            totals[k] += s[k]

    result = {
        "task": "toc-extraction",
        "scorer_version": SCORER_VERSION,
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
