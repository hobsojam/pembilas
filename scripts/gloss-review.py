"""
Generates a frequency-ranked review list of suspicious glosses (issue #61).

A words.json gloss is suspicious when it is still machine-generated (it
byte-matches the FreeDict inversion, naive or improved -- see
extract-dict.py) AND it shares no word stem with any of the word's sense
glosses in English Wiktionary (via the kaikki.org wiktextract dump).
That combination is the signature of a wrong-primary-sense inversion
artifact (ruas = "expression", kesempatan = "accident").

The output is a REVIEW list, not an auto-fix: sampling showed ~15% of
raw kaikki-derived replacements would be regressions (sense-order and
phrasing artifacts), so a human picks and words the actual fixes.
Entries are ranked by corpus frequency (frequency-rank.py's scoring) so
review effort goes to the glosses users actually see.

Neither source file is committed (61 MB / 1 MB); URLs are documented in
data/SOURCES.md.

Usage:
    python scripts/gloss-review.py path/to/eng-ind.tei path/to/kaikki-Indonesian.jsonl [N]
"""
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

root_dir = Path(__file__).parent.parent

# extract-dict.py has a hyphen in its name, so import it by path
_spec = importlib.util.spec_from_file_location('extract_dict', root_dir / 'scripts' / 'extract-dict.py')
extract_dict = importlib.util.module_from_spec(_spec)
_argv, sys.argv = sys.argv, ['extract-dict', 'unused']
try:
    _spec.loader.exec_module(extract_dict)
except SystemExit:
    pass
sys.argv = _argv

SKIP_PREFIXES = ('synonym of', 'alternative spelling of', 'alternative form of',
                 'colloquial form of', 'nonstandard spelling of', 'obsolete spelling of',
                 'informal form of', 'contraction of', 'abbreviation of', 'initialism of',
                 'clipping of', 'syllabic abbreviation', 'basic form of', 'active of',
                 'passive of', 'plural of', 'imperative of', 'stative of')


def clean_sense(text):
    text = re.sub(r'\([^)]*\)', '', text).strip().rstrip('.').rstrip(',').rstrip(';')
    return text.split(':')[0].strip()


def kaikki_senses(entries):
    out = []
    for e in entries:
        if e.get('pos') == 'name':
            continue
        for s in e.get('senses', []):
            if any(t in ('form-of', 'alt-of') for t in s.get('tags', [])):
                continue
            glosses = s.get('glosses') or []
            if not glosses:
                continue
            t = clean_sense(glosses[-1])
            if not t or t.lower().startswith(SKIP_PREFIXES):
                continue
            if t.lower() not in [o.lower() for o in out]:
                out.append(t)
    return out


def stems(text):
    words = re.findall(r'[a-z]+', text.lower())
    return {w[:5] for w in words if len(w) >= 4} | {w for w in words if len(w) < 4}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tei_path, kaikki_path = sys.argv[1], sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    inversion, richness = extract_dict.parse_tei(tei_path)

    kaikki = defaultdict(list)
    with open(kaikki_path, encoding='utf-8') as f:
        for line in f:
            e = json.loads(line)
            kaikki[e.get('word', '').lower()].append(e)

    freq = {}
    with (root_dir / 'data' / 'frequency-id-50k.txt').open(encoding='utf-8') as f:
        for line in f:
            token, count = line.split()
            freq[token] = int(count)
    index = json.loads((root_dir / 'data' / 'search-index.json').read_text(encoding='utf-8'))
    score = defaultdict(int)
    for form, root, *_ in index:
        n = freq.get(form)
        if n:
            score[root] += n

    words = json.loads((root_dir / 'data' / 'words.json').read_text(encoding='utf-8'))['words']
    rows = []
    for w in words:
        if w.get('pos') == 'proper':
            continue
        heads = inversion.get(w['root'])
        if not heads:
            continue
        machine = (w['gloss'].lower() == extract_dict.naive_gloss(heads) or
                   w['gloss'] == extract_dict.improved_gloss(heads, richness))
        if not machine:
            continue
        senses = kaikki_senses(kaikki.get(w['root'], []))
        if not senses:
            continue
        if stems(w['gloss']) & stems(' '.join(senses)):
            continue
        rows.append((score.get(w['root'], 0), w['root'], w['gloss'], senses[:4]))

    rows.sort(key=lambda r: -r[0])
    print(f'{len(rows)} suspicious glosses; top {top_n}:')
    for s, root, gloss, senses in rows[:top_n]:
        print(f'{root:15}{s:>9}  {gloss[:30]:32} | ' + ' / '.join(x[:40] for x in senses[:3]))


if __name__ == '__main__':
    main()
