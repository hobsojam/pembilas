"""
Checks what surface form a (root, affix) pair actually generates in the
mechanical search index, before annotating it as valid.

Exists because peN-/meN- nasal substitution has irregular exceptions
(e.g. petani/pedagang keep their initial consonant instead of
nasalizing) that a assumed "root + affix = expected word" mapping can
get wrong -- this has caused real mistakes across frequency batches
(tualang/petualang, penglihatan, tani/petani). Run this before adding
any "pe" (and, more cautiously, "pe_an"/"per_an") slot on a t/k/p/s-
initial root to confirm the generated form matches what you intend to
annotate.

Usage:
    python scripts/verify_slot.py <root> <affix> [<affix> ...]
"""
import json
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent


def main():
    if len(sys.argv) < 3:
        sys.exit('usage: verify_slot.py <root> <affix> [<affix> ...]')

    root = sys.argv[1]
    affixes = set(sys.argv[2:])
    index = json.loads((root_dir / 'data' / 'search-index.json').read_text(encoding='utf-8'))

    found = {e[2]: e[0] for e in index if e[1] == root and e[2] in affixes}
    for affix in sys.argv[2:]:
        if affix in found:
            print(f'{root}.{affix} -> {found[affix]}')
        else:
            print(f'{root}.{affix} -> (no mechanical form found)')


if __name__ == '__main__':
    main()
