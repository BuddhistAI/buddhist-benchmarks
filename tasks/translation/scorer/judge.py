#!/usr/bin/env python3
"""Judge for the translation task: label each meaning unit of each item.

python3 scorer/judge.py --data data/bo-fr/v1/test.jsonl --predictions predictions.jsonl \
    --out judgments.jsonl [--model claude-opus-5-5]

Needs the `anthropic` package and an API key (ANTHROPIC_API_KEY, or a profile from `ant auth login`).
This costs money: see TASK.md for an estimate before you run it.

The judge sees the source, the expert's meaning units (with their channel) and the translation.
It never sees a reference translation, so it cannot reward closeness to one. It labels each unit:
  delivered  the unit's meaning is in the translation, wherever it is placed
  shifted    present, but its meaning changed (for example a different modality or agent)
  thinned    present, but part of its content is missing
  absent     not in the translation (for units whose channel is "text" or "outside")
  rendered / not-rendered   for units whose channel is "absent" (correctly left out)
For colophons it also reports where the main verb is, whether the author's epithet stays a phrase,
and whether the slots keep source order. Labels go to judgments.jsonl with token counts.

Change the prompt or the default model only with a new JUDGE_VERSION (and a major data version).
"""
import argparse, json, sys

JUDGE_VERSION = "0.1.0"
DEFAULT_MODEL = "claude-opus-5-5"
EFFORT = "medium"

SYSTEM = """You check whether a translation carries the meaning units of its source. You are given the source text, a list of meaning units written by an expert, and one translation.

Rules:
- Judge meaning, not form. A unit may be expressed anywhere in the sentence, split, merged with another unit, or carried by a different construction. Before you mark a unit "absent", look for its meaning elsewhere in the translation.
- Do not penalise normal target-language re-encoding: changed word order, a verb moved earlier, repetition turned into a scalar adverb, a concrete image stated plainly. These are not losses.
- "shifted" means the meaning changed (a different agent, tense or modality that changes what is asserted). "thinned" means part of the content is missing.
- A unit with channel "outside" may be carried by layout (a heading, numbering, a note). Count it as delivered if the translation shows it that way.
- A unit with channel "absent" should not appear as text. Label it "rendered" if the translation still renders it, otherwise "not-rendered".
- For a colophon: matrix_verb is "early" if the main verb of the colophon (who composed or wrote it) comes in the first half of the French sentence it belongs to, "stranded" if it comes at the end after all the slots, "lost" if there is no main verb for it. epithet is "slot" if the author's humble self-description stays a phrase attached to the name, "predication" if it became its own clause or sentence. slot_order is "source" if the slots keep the Tibetan order, "target" if they were re-ordered.
- For other genres, give "n/a" for matrix_verb, epithet and slot_order.
Answer only in the JSON format requested."""


def schema(unit_ids):
    return {
        "type": "object",
        "properties": {
            "units": {"type": "object",
                      "properties": {u: {"type": "string", "enum": ["delivered", "shifted", "thinned", "absent", "rendered", "not-rendered"]} for u in unit_ids},
                      "required": unit_ids, "additionalProperties": False},
            "matrix_verb": {"type": "string", "enum": ["early", "stranded", "lost", "n/a"]},
            "epithet": {"type": "string", "enum": ["slot", "predication", "n/a"]},
            "slot_order": {"type": "string", "enum": ["source", "target", "n/a"]},
            "notes": {"type": "string"},
        },
        "required": ["units", "matrix_verb", "epithet", "slot_order", "notes"],
        "additionalProperties": False,
    }


def prompt(item, translation):
    t = item["target"]
    units = "\n".join(f'- {u["id"]} [{u.get("slot", "")}; channel: {u.get("channel", "text")}]: {u["gloss"]}' for u in t["units"])
    return (f"Genre: {t.get('genre', 'prose')}\n\nSource ({item.get('metadata', {}).get('source_language', 'bo')}):\n{item['input']['source'] if isinstance(item['input'], dict) else item['input']}\n\n"
            f"Meaning units:\n{units}\n\nTranslation:\n{translation}\n\nLabel every unit, then give matrix_verb, epithet, slot_order and short notes.")


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    a = ap.parse_args()
    import anthropic
    client = anthropic.Anthropic()
    preds = {p["id"]: p.get("output", "") for p in load(a.predictions)}
    usage = {"input_tokens": 0, "output_tokens": 0}
    with open(a.out, "w", encoding="utf-8") as out:
        for item in load(a.data):
            text = preds.get(item["id"], "")
            text = text.get("text", "") if isinstance(text, dict) else str(text)
            ids = [u["id"] for u in item["target"]["units"]]
            r = client.messages.create(
                model=a.model, max_tokens=16000, system=SYSTEM,
                messages=[{"role": "user", "content": prompt(item, text)}],
                output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": schema(ids)}},
            )
            if r.stop_reason == "refusal":
                sys.exit(f"{item['id']}: the judge refused ({r.stop_details}); stop and report it")
            j = json.loads(next(b.text for b in r.content if b.type == "text"))
            usage["input_tokens"] += r.usage.input_tokens
            usage["output_tokens"] += r.usage.output_tokens
            out.write(json.dumps({"id": item["id"], "judge_version": JUDGE_VERSION, "model": a.model, **j,
                                  "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}},
                                 ensure_ascii=False) + "\n")
    print(json.dumps({"judge_version": JUDGE_VERSION, "model": a.model, "usage": usage}), file=sys.stderr)


if __name__ == "__main__":
    main()
