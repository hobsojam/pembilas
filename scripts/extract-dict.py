"""
Reproducible derivation of data/words.json glosses from the FreeDict
eng-ind dictionary (see data/SOURCES.md for the upstream tarball URL).

The original words.json was produced by naively inverting the English ->
Indonesian dictionary: each Indonesian word's gloss became the sorted,
comma-joined set of English headwords that listed it as a translation.
That promotes obscure senses to primary glosses (ulangan = "deuteronomy",
pemalu = "sheep" -- see issue #61). This script re-derives glosses with
two improvements:

  1. English headwords that are proper nouns (pos "pn" or capitalized)
     are excluded from the gloss unless they are the only source.
  2. Remaining headwords are ranked by their total sense count across the
     dictionary -- an in-corpus commonness proxy that needs no external
     frequency list -- and the gloss is capped at the top 3.

Roots whose *only* sources are proper-noun headwords get pos "proper"
(issue #62); everything else keeps pos "word".

Only glosses that still byte-match the naive inversion are rewritten:
every hand-curated or hand-added gloss is left untouched. That safety
check only covers the *gloss* field, though -- a root a human explicitly
un-tagged from pos:"proper" back to pos:"word" (because the mechanical
proper-noun classification was wrong for it, e.g. ulangan, whose only
inversion source is "Deuteronomy" the Bible book, but whose real
everyday meaning is "test/exam") would otherwise be silently re-tagged
proper on the next run, since "proper_only and pos=='word'" is exactly
the state such an override leaves behind. MANUAL_POS_OVERRIDES below is
the explicit denylist that protects those decisions; see issue #52.

Usage:
    python scripts/extract-dict.py path/to/eng-ind.tei          # dry run
    python scripts/extract-dict.py path/to/eng-ind.tei --apply  # rewrite words.json
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = '{http://www.tei-c.org/ns/1.0}'
GLOSS_HEAD_CAP = 3

root_dir = Path(__file__).parent.parent
WORDS_PATH = root_dir / 'data' / 'words.json'

# Roots where a human reviewed the mechanical proper-noun classification
# and decided it was wrong, keeping (or restoring) pos:"word" -- exempt
# from automatic re-tagging on future runs. Add an entry here whenever a
# PR hand-overrides what this script would otherwise produce.
MANUAL_POS_OVERRIDES = {
    'ulangan': 'only inversion source is "Deuteronomy" (pn); real meaning is test/exam/quiz, invisible to the TEI-based classifier (#52)',
}


def parse_tei(tei_path):
    """Return (inversion, richness): indonesian -> [(english, pos)], english -> sense count."""
    tree = ET.parse(tei_path)
    inversion = {}
    richness = {}
    for entry in tree.getroot().iter(NS + 'entry'):
        orth = entry.find(f'.//{NS}orth')
        if orth is None or not orth.text:
            continue
        eng = orth.text.strip()
        pos_el = entry.find(f'.//{NS}pos')
        pos = pos_el.text.strip() if pos_el is not None and pos_el.text else '?'
        senses = entry.findall(f'.//{NS}sense')
        richness[eng] = richness.get(eng, 0) + max(len(senses), 1)
        for quote in entry.findall(f'.//{NS}quote'):
            ind = (quote.text or '').strip().lower()
            if ind:
                inversion.setdefault(ind, []).append((eng, pos))
    return inversion, richness


def is_proper(eng, pos):
    return pos == 'pn' or (eng[:1].isupper())


def naive_gloss(heads):
    """The original extraction: sorted, comma-joined, lowercased English heads."""
    return ', '.join(sorted({e.lower() for e, _ in heads}, key=str.lower))


def improved_gloss(heads, richness):
    common = [(e, p) for e, p in heads if not is_proper(e, p)]
    pool = common or heads
    ranked = sorted({e.lower() for e, _ in pool},
                    key=lambda e: (-richness.get(e, richness.get(e.capitalize(), 0)), e))
    return ', '.join(ranked[:GLOSS_HEAD_CAP])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    apply = '--apply' in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    inversion, richness = parse_tei(args[0])

    data = json.loads(WORDS_PATH.read_text(encoding='utf-8'))
    regl = tagged = untouched = missing = 0
    for w in data['words']:
        heads = inversion.get(w['root'])
        if not heads:
            missing += 1
            continue
        proper_only = all(is_proper(e, p) for e, p in heads)
        if proper_only and w.get('pos') == 'word' and w['root'] not in MANUAL_POS_OVERRIDES:
            w['pos'] = 'proper'
            tagged += 1
        if w['gloss'].lower() == naive_gloss(heads):
            new = improved_gloss(heads, richness)
            if new != w['gloss']:
                w['gloss'] = new
                regl += 1
        else:
            untouched += 1  # hand-curated; never overwritten

    print(f'{regl} glosses regenerated, {tagged} roots tagged pos:proper, '
          f'{untouched} hand-curated glosses preserved, {missing} roots not in the inversion')
    if apply:
        with WORDS_PATH.open('w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f'wrote {WORDS_PATH}')
    else:
        print('dry run -- pass --apply to rewrite data/words.json')


if __name__ == '__main__':
    main()
