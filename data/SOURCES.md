# Data Sources

## words.json

**License:** [Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)](https://creativecommons.org/licenses/by-sa/3.0/legalcode)

This file is derived from the **English-Bahasa Indonesia FreeDict+WikDict dictionary** (version 2025.11.23, 15,262 headwords), which is itself derived from:

- [Wiktionary](https://www.wiktionary.org/) — the free dictionary
- [DBnary](http://kaiko.getalp.org/about-dbnary/) — structured extraction of Wiktionary data
- [WikDict](http://www.wikdict.com/) — bilingual dictionary generation from DBnary
- [FreeDict](https://freedict.org/) — open dictionary project, maintainer Karl Bartel

The original dictionary was downloaded from:
`https://download.freedict.org/dictionaries/eng-ind/2025.11.23/freedict-eng-ind-2025.11.23.src.tar.xz`

The data was inverted (English→Indonesian to Indonesian→English) and reformatted as JSON. The original one-off inversion script was never committed; `scripts/extract-dict.py` is the committed, reproducible replacement (issue #61). It re-derives glosses from the TEI source with two refinements over the naive inversion:

- English headwords that are proper nouns (TEI pos `pn`, or capitalized) are excluded from a gloss unless they are the word's only source; roots whose *only* sources are proper nouns carry `pos: "proper"` (issue #62)
- remaining English headwords are ranked by their total sense count across the dictionary (an in-corpus commonness proxy) and capped at 3 per gloss

The script only rewrites glosses that still byte-match the naive inversion — hand-curated glosses are never overwritten. Roots added by annotation batches (with hand-written glosses) are not part of the inversion at all.

## affixes.json

**License:** authored by the project contributors.

Hand-authored reference data on Bahasa Indonesia affix rules and nasal assimilation patterns, based on standard Indonesian grammar descriptions.

## annotations.json

**License:** authored by the project contributors.

Hand-curated per-word affix applicability and derived meanings. Grows incrementally as words are annotated.
