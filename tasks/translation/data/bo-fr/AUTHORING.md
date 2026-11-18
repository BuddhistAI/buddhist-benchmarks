# How to write the Tibetan colophon items (bo-fr v1)

Drupchen's advice: colophons are where translators most often fail, and they are a good first test set. They are short and formulaic, so the slots are fixed and scoring is mechanical. They are published with the source facing. And nobody can say their structure was a style choice ([Two strategies §9.3](https://buddhistai.github.io/knowledge-base/papers/two-strategies-for-machine-translation-from-tibetan/paper.html)).

## Target

- **30 colophons** for v1 (the method says: run on 20 before committing to 200). Small but diverse.
- Mix: canonical (Kangyur and Tengyur translators' colophons), treatises by known authors, and modern compositions. Short ones (one sentence) and long ones (60 words or more before the verb).
- Every colophon is real and comes from a named edition.

## Sources

- The Tibetan text must be public domain or under an MIT-compatible license (for example CC0 e-texts). Record the edition, the volume and folio or page, and the e-text source with its license and revision in the item's `metadata` and in `v1/SOURCE.md`.
- Do not copy a published translation into the data. The references are meaning units, not a translation.

## Writing the units

For each colophon, a person who reads classical Tibetan writes:

1. The list of **meaning units**: one per thing the colophon asserts (who asked, how they asked, who wrote it, the author's epithet, where, when, the aspiration, the verb). Write each `gloss` as one short plain-English sentence.
2. The `slot` of each unit and its `channel` (`text`, `outside` or `absent`).
3. Which unit is the **matrix verb** (`target.matrix_verb`).
4. Any French connective a real source particle licenses (`target.licensed_connectives`). Usually none.
5. The context sheet in `input.context`.

An AI may propose a first list of units, but a human must check and correct every item before it is added, and the item records who did it (`metadata.units_by`, `metadata.checked_by`). Never add an item no human has checked.

## Maturity

- **Draft:** 30 real items, units by one reader.
- **Reviewed:** a second reader of Tibetan checks every unit list, and someone checks a sample of the judge's labels against their own.

## Item ids

`colophon-001`, `colophon-002`, ... Ids are permanent. Never reuse or renumber them.
