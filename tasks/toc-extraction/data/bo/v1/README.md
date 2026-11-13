# toc-extraction / bo / v1

- **Version:** 1.0.0 (see [CHANGELOG.md](../../../CHANGELOG.md)).
- **Purpose:** first real Tibetan benchmark. Find the sa-bcad (ས་བཅད) outline headings in passages of Tibetan commentary whose formatting and line breaks were stripped, with their nesting level and start position.
- **Items:** 85 passages of up to 6,500 characters, cut at heading boundaries, 394 headings in all. `items.json` lists each item with its subset:
  - `same-book` (76 items, 369 headings): Jamyang Loter Wangpo, *A Lamp Illuminating the Intent of Vasubandhu* (མཛོད་ཀྱི་མཆན་འགྲེལ་དབྱིག་གཉེན་དགོངས་པ་གསལ་བའི་སྒྲོན་མེ).
  - `held-out-book` (9 items, 25 headings; one item has no heading): Chenga Chökyi Gyalpo, *The Jewel Garland*.
- **How they were chosen:** every passage of the two books, except 48 passages of the first book that were used to optimise skills (they stay in [BuddhistAI/toc-extraction-tibetan](https://github.com/BuddhistAI/toc-extraction-tibetan) as training data) and passages over 6,500 characters.
- **Source and license:** the texts are public domain. Digital editions from EPUBs (IBA-LWS-08, RCP-FM-07); the EPUBs and the build script are in BuddhistAI/toc-extraction-tibetan `benchmark/`. Data here is MIT.
- **References made by:** built automatically by `build_dataset.py` from the EPUBs' `Tibetan-Sabche` outline paragraphs. Levels are reconstructed from the outline grammar (ལ་གཉིས / ལ་གསུམ announcements and ordinals), so this is a silver standard: report wrong references as an issue, and they will be fixed in a patch version.
- **Shared resource versions:** none.

## Format notes

Each reference entry has `title`, `level`, `start` (character offset in the input) and `anchor` (the first 40 characters of the heading, verbatim). Because the outline titles are labels, not text that appears verbatim, this set is scored in **position mode**: a predicted entry must give `start` or a verbatim `anchor`, and matches a reference entry that starts within 3 characters of it. `level` is relative to the passage: 1 is the shallowest level present in that passage.

Origin: [BuddhistAI/toc-extraction-tibetan](https://github.com/BuddhistAI/toc-extraction-tibetan) benchmark 1.0.0, exported with `scripts/export_buddhist_benchmarks.py`.
