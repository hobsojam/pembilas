"""
Checks newly-verified forms for prefix near-misses in
data/search-index.json (batch 7 lesson): a verified slot can produce a
longer junk form that starts with a real verified form and pollutes
autocomplete (e.g. `kawasan.pe_an` -> `pengawasanan`, a nonsense
near-miss for the real `pengawasan`). The collision scanner
(scan_collisions.py) only catches exact-form collisions, not this.

Most hits are benign -- real unrelated words that happen to share a
prefix (abu/abugida is desirable autocomplete, not a bug). Only chase
hits where the "other root" is a nonsense mechanical guess rather than
an actual word.

Usage:
    python scripts/scan_near_miss.py <verified_form> [<verified_form> ...]
"""
import json
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: scan_near_miss.py <verified_form> [<verified_form> ...]')
    forms = sys.argv[1:]
    idx = json.loads((root_dir / 'data' / 'search-index.json').read_text(encoding='utf-8'))

    found = False
    for vf in forms:
        longer = [e for e in idx if e[0] != vf and e[0].startswith(vf) and len(e) == 3]
        if longer:
            found = True
            print(f'{vf}:')
            for e in longer:
                print('  ', e)

    if not found:
        print('OK: no near-miss forms found')


if __name__ == '__main__':
    main()
