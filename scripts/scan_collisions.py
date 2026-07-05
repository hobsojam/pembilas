"""
Scans data/search-index.json for forms with both a verified and an
unverified entry (mixed collisions) -- run after every batch's
`npm run build:index` to catch cases where a newly-annotated slot
collides with an existing mechanical derivation (or vice versa).

For each hit, decide which side is the real derivation and mark the
other's annotations.json slot state "unused" with a notes field starting
"collision triage (#48): ...", then rebuild and re-run this until it
reports zero. This has never once cleared on the first try in this
repo's history -- budget time for it.

Usage:
    python scripts/scan_collisions.py [path/to/search-index.json]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

root_dir = Path(__file__).parent.parent


def main():
    index_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root_dir / 'data' / 'search-index.json'
    idx = json.loads(index_path.read_text(encoding='utf-8'))

    byform = defaultdict(list)
    for e in idx:
        byform[e[0]].append(e)
    mixed = {f: es for f, es in byform.items() if any(len(e) == 4 for e in es) and any(len(e) == 3 for e in es)}

    if not mixed:
        print('OK: no mixed verified/unverified collisions')
        return
    for form, entries in mixed.items():
        print(form, entries)
    sys.exit(1)


if __name__ == '__main__':
    main()
