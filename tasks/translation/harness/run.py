#!/usr/bin/env python3
"""Run one arm of the Tibetan→French translation comparison and log real token counts.

python3 harness/run.py --arm units --skill ../../../translation-tibetan-to-french/variants/drupchen-method-units-v1 \
    --data data/bo-fr/v1/test.jsonl --model claude-opus-5-5 --out runs/<run-id>/repeat-1

Arms:
  no-skill  the model alone: "Translate this Tibetan into French", with the item's context sheet
  onepass   the skill's SKILL.md and references as the system prompt, one call
  units     three calls: (1) context + meaning units + flags from the Tibetan; (2) French from the
            units only, in a new conversation without the Tibetan; (3) audit with both texts
Writes predictions.jsonl ({"id", "output"}), calls.jsonl (every call with its usage) and usage.json.
Costs money. --dry-run prints the prompts' sizes and makes no call.
"""
import argparse, json, re, sys
from pathlib import Path

PLAIN = "Translate this Tibetan text into French."


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def skill_text(skill):
    p = Path(skill)
    parts = [(p / "SKILL.md").read_text(encoding="utf-8")]
    for r in sorted((p / "references").glob("*.md")):
        parts.append(f"\n\n<reference file=\"references/{r.name}\">\n{r.read_text(encoding='utf-8')}\n</reference>")
    return "".join(parts)


def context(item):
    c = item["input"].get("context", {}) if isinstance(item["input"], dict) else {}
    return "\n".join(f"- {k}: {v}" for k, v in c.items())


def source(item):
    return item["input"]["source"] if isinstance(item["input"], dict) else item["input"]


def section(text, name):
    m = re.search(rf"^##\s*{name}\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M)
    return (m.group(1) if m else text).strip()


class Caller:
    def __init__(self, model, dry, log):
        self.model, self.dry, self.log = model, dry, log
        self.usage = {"input_tokens": 0, "output_tokens": 0, "calls": 0}
        if not dry:
            import anthropic
            self.client = anthropic.Anthropic()

    def __call__(self, item_id, step, system, user):
        if self.dry:
            self.log.write(json.dumps({"id": item_id, "step": step, "system_chars": len(system), "user_chars": len(user)}) + "\n")
            return "## Traduction\n(dry run)\n"
        with self.client.messages.stream(model=self.model, max_tokens=32000, system=system,
                                         messages=[{"role": "user", "content": user}]) as s:
            r = s.get_final_message()
        if r.stop_reason == "refusal":
            sys.exit(f"{item_id} {step}: refusal ({r.stop_details}); stop and report it")
        text = "".join(b.text for b in r.content if b.type == "text")
        u = {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}
        for k in u:
            self.usage[k] += u[k]
        self.usage["calls"] += 1
        self.log.write(json.dumps({"id": item_id, "step": step, "model": self.model, "usage": u, "stop_reason": r.stop_reason, "text": text}, ensure_ascii=False) + "\n")
        return text


def run_item(arm, item, call, skill):
    ctx, src = context(item), source(item)
    if arm == "no-skill":
        return call(item["id"], "translate", PLAIN, f"Context:\n{ctx}\n\nTibetan:\n{src}").strip()
    if arm == "onepass":
        out = call(item["id"], "translate", skill, f"Context sheet:\n{ctx}\n\nTibetan:\n{src}\n\nTranslate into French. Follow the skill's output format.")
        return section(out, "Traduction")
    # units: three separate conversations
    s1 = call(item["id"], "units", skill,
              f"Context sheet:\n{ctx}\n\nTibetan:\n{src}\n\nDo stage 0 and stage 1 only: the context sheet, the feature sort, the meaning units with their channel and slot, and the flags. Do not write the French translation.")
    sealed = re.sub(r"[\u0F00-\u0FFF][\u0F00-\u0FFF\s]*", "[bo] ", s1)  # no Tibetan text reaches stage 2
    s2 = call(item["id"], "compose", skill,
              f"Stage 2. You do not have the Tibetan. Write the French only from this material.\n\n{sealed}\n\nFollow the skill's output format; give the Traduction section and the Signalements.")
    s3 = call(item["id"], "audit", skill,
              f"Stage 3 audit.\n\nTibetan:\n{src}\n\nStage 1 output:\n{s1}\n\nFrench draft:\n{section(s2, 'Traduction')}\n\nCheck only meaning-unit coverage. Fix real losses, then give the final text in the skill's output format.")
    return section(s3, "Traduction")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["no-skill", "onepass", "units"], required=True)
    ap.add_argument("--skill", help="draft folder with SKILL.md and references/ (not for no-skill)")
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.arm != "no-skill" and not a.skill:
        sys.exit("--skill is required for this arm")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    skill = skill_text(a.skill) if a.skill else ""
    with open(out / "calls.jsonl", "w", encoding="utf-8") as log, open(out / "predictions.jsonl", "w", encoding="utf-8") as preds:
        call = Caller(a.model, a.dry_run, log)
        items = load(a.data)
        for item in items:
            preds.write(json.dumps({"id": item["id"], "output": run_item(a.arm, item, call, skill)}, ensure_ascii=False) + "\n")
    usage = {**call.usage, "items": len(items), "estimated": False, "arm": a.arm, "model": a.model, "skill": a.skill}
    (out / "usage.json").write_text(json.dumps(usage, indent=2), encoding="utf-8")
    print(json.dumps(usage))


if __name__ == "__main__":
    main()
