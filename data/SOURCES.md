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

## frequency-id-50k.txt

**License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

Indonesian word-frequency list (50,000 entries) from [HermitDave/FrequencyWords](https://github.com/hermitdave/FrequencyWords) (2018 dataset), derived from the [OpenSubtitles](https://www.opensubtitles.org/) corpus. Used by `scripts/frequency-rank.py` to target annotation batches at the highest-frequency uncovered roots (issue #14, frequency-driven mode). The spoken-subtitle register suits the learner audience.

## Gloss review (not a committed data file)

`scripts/gloss-review.py` (issue #61) cross-checks machine-generated `words.json` glosses (see the extract-dict.py note above) against English Wiktionary sense glosses, via the [kaikki.org](https://kaikki.org/dictionary/Indonesian/) Wiktextract JSONL dump for Indonesian — a third-party extraction of Wiktionary, itself CC BY-SA. A gloss is flagged when it shares no word stem with any Wiktionary sense, which is the signature of an inversion artifact that promoted a rare/wrong sense to primary (e.g. `indonesia` = "neural network", traced to a garbage English↔Indonesian pairing in the upstream FreeDict TEI itself).

Neither the kaikki dump (~60 MB) nor the FreeDict TEI (~1 MB) is committed; both are downloaded on demand (URLs are in this file and the script's docstring). The script's output is a **ranked review list**, not an autofix — roughly 1 in 4 flagged glosses turned out to be a correct-but-differently-phrased translation rather than a genuine error, so a human picks and words the actual fixes.

## affixes.json

**License:** authored by the project contributors.

Hand-authored reference data on Bahasa Indonesia affix rules and nasal assimilation patterns, based on standard Indonesian grammar descriptions.

## annotations.json

**License:** authored by the project contributors.

Hand-curated per-word affix applicability and derived meanings. Grows incrementally as words are annotated.
