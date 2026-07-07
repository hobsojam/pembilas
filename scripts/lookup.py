"""
Batch-lookup helper for frequency-batch survey work (issue #14).

For each given root, prints its words.json entry, its annotations.json
entry (if any), and its corpus frequency (bare form). Replaces the
repeated one-off `python3 -c "..."` snippets used during survey.

Usage:
    python scripts/lookup.py <root> [<root> ...]
"""
import json
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: lookup.py <root> [<root> ...]')

    words = {w['root']: w for w in json.loads((root_dir / 'data' / 'words.json').read_text(encoding='utf-8'))['words']}
    ann = json.loads((root_dir / 'data' / 'annotations.json').read_text(encoding='utf-8'))
    freq = {}
    for line in (root_dir / 'data' / 'frequency-id-50k.txt').open(encoding='utf-8'):
        w, c = line.split()
        freq[w] = int(c)

    for root in sys.argv[1:]:
        w = words.get(root)
        a = ann.get(root)
        f = freq.get(root, 0)
        print(f'{root} (freq={f})')
        print(f'  word: {w}')
        print(f'  ann:  {a}')


if __name__ == '__main__':
    main()
