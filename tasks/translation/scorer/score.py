#!/usr/bin/env python3
"""Scorer for the translation task (meaning-unit coverage).

python3 scorer/score.py --language bo-fr --data data/bo-fr/v1/test.jsonl \
    --predictions predictions.jsonl --judgments judgments.jsonl > scores.json

The method comes from Drupchen, "Two strategies for improving machine translation from Tibetan"
(2026, §9) and "Subtracting the Typological Baseline" (2026, §9), CC BY 4.0, in the BuddhistAI
knowledge base (papers/). It does not use BLEU or chrF, because they reward literal translations.

Each reference lists the item's meaning units. A judge (scorer/judge.py, a pinned model and prompt)
reads the source, the units and the translation, and labels each unit. This file only counts:
it reads the judge's labels and the translation text, so scoring is reproducible from the files.

Unit labels and their value:
  delivered 1.0 · shifted 0.5 · thinned 0.5 · absent 0.0     (units whose channel is text or outside)
  rendered / not-rendered                                     (units whose channel is absent: only counted)

Metrics (micro-averaged over units or items, also per metadata.subset):
  unit_coverage         mean unit value. Headline score.
  matrix_verb_early     share of items whose main verb comes early in the French sentence (colophons)
  epithet_as_slot       share of items where the author's humble epithet stays a phrase, not a sentence
  target_order          share of items where the slots are re-ordered for French, not kept in source order
  wrongly_rendered      count of units marked "correctly absent" that the translation still renders
  unlicensed_connectives  mean count per item of French connectives (ainsi, donc, c'est pourquoi ...)
                        that no source particle licenses (target.licensed_connectives). Lower is better.

Format check: if an item's output is its own reference (a dict with "units"), every unit counts as
delivered and every colophon measure as correct, so the references score 1.0 against themselves.
"""
import argparse, json, re, sys, unicodedata

SCORER_VERSION = "0.1.0"
JUDGE_VERSION = "0.1.0"  # must match scorer/judge.py
UNIT_VALUE = {"delivered": 1.0, "shifted": 0.5, "thinned": 0.5, "absent": 0.0}

# French connectives that translators supply between colophon slots. Key = normalized form.
CONNECTIVES = {
    "fr": ["ainsi", "donc", "c'est pourquoi", "c'est ainsi que", "par consequent", "de ce fait",
           "des lors", "aussi", "alors", "en consequence", "pour cette raison", "c'est donc"],
}


def normalize(text, language):
    t = unicodedata.normalize("NFKD", str(text)).lower().replace("’", "'")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.split())


def target_lang(language):
    return language.split("-")[-1] if "-" in language else language


def count_connectives(text, language, licensed):
    t = normalize(text, language)
    allowed = {normalize(x, language) for x in licensed}
    n = 0
    for c in CONNECTIVES.get(target_lang(language), []):
        if c in allowed:
            continue
        n += len(re.findall(r"(?<![\w'])" + re.escape(c) + r"(?![\w])", t))
    return n


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def score_item(item, output, judgment, language):
    tgt = item["target"]
    units = tgt["units"]
    perfect = isinstance(output, dict) and output.get("units") == units
    labels = {} if perfect else (judgment or {}).get("units", {})
    vals, wrong = [], 0
    for u in units:
        if u.get("channel", "text") == "absent":
            if not perfect and labels.get(u["id"]) == "rendered":
                wrong += 1
            continue
        vals.append(1.0 if perfect else UNIT_VALUE.get(labels.get(u["id"], "absent"), 0.0))
    res = {"unit_values": vals, "wrongly_rendered": wrong}
    if tgt.get("genre") == "colophon":
        j = {} if perfect else (judgment or {})
        res["matrix_verb_early"] = 1.0 if perfect or j.get("matrix_verb") == "early" else 0.0
        res["epithet_as_slot"] = 1.0 if perfect or j.get("epithet") == "slot" else 0.0
        res["target_order"] = 1.0 if perfect or j.get("slot_order") == "target" else 0.0
    text = "" if perfect else (output.get("text", "") if isinstance(output, dict) else str(output or ""))
    res["unlicensed_connectives"] = count_connectives(text, language, tgt.get("licensed_connectives", []))
    return res


def aggregate(results):
    vals = [v for r in results for v in r["unit_values"]]
    out = {"items": len(results), "units": len(vals),
           "unit_coverage": round(sum(vals) / len(vals), 4) if vals else 0.0,
           "wrongly_rendered": sum(r["wrongly_rendered"] for r in results),
           "unlicensed_connectives": round(sum(r["unlicensed_connectives"] for r in results) / len(results), 4) if results else 0.0}
    for k in ("matrix_verb_early", "epithet_as_slot", "target_order"):
        xs = [r[k] for r in results if k in r]
        if xs:
            out[k] = round(sum(xs) / len(xs), 4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--judgments", help="judge.py output; required for real runs")
    ap.add_argument("--language", default="bo-fr")
    a = ap.parse_args()
    items = load(a.data)
    preds = {p["id"]: p.get("output", "") for p in load(a.predictions)}
    judg = {j["id"]: j for j in load(a.judgments)} if a.judgments else {}
    if judg:
        bad = {j.get("judge_version") for j in judg.values()} - {JUDGE_VERSION}
        if bad:
            sys.exit(f"judgments were made with judge version {bad}, this scorer needs {JUDGE_VERSION}")
    by = {}
    for it in items:
        r = score_item(it, preds.get(it["id"], ""), judg.get(it["id"]), a.language)
        by.setdefault("all", []).append(r)
        sub = it.get("metadata", {}).get("subset")
        if sub:
            by.setdefault(sub, []).append(r)
    scores = {k: aggregate(v) for k, v in by.items()}
    report = {"scorer_version": SCORER_VERSION, "judge_version": JUDGE_VERSION, "headline": "unit_coverage",
              "unit_coverage": scores["all"]["unit_coverage"], "items": len(items),
              "missing": sum(1 for it in items if it["id"] not in preds),
              "unjudged": 0 if not a.judgments else sum(1 for it in items if it["id"] not in judg),
              "scores": scores}
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
