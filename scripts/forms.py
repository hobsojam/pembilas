"""
Batch form-frequency lookup for frequency-batch survey work (issue #14).

For each given root, prints every mechanically-generated surface form
attributed to it in the search index, sorted by corpus frequency
(zero-frequency forms omitted). Replaces the repeated one-off
`python3 -c "..."` snippets used to decide which slots are worth
annotating.

Usage:
    python scripts/forms.py <root> [<root> ...]
"""
import json
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: forms.py <root> [<root> ...]')

    targets = set(sys.argv[1:])
    index = json.loads((root_dir / 'data' / 'search-index.json').read_text(encoding='utf-8'))
    freq = {}
    for line in (root_dir / 'data' / 'frequency-id-50k.txt').open(encoding='utf-8'):
        w, c = line.split()
        freq[w] = int(c)

    byroot = {}
    for form, root, *_ in index:
        if root in targets:
            byroot.setdefault(root, []).append((form, freq.get(form, 0)))

    for t in sys.argv[1:]:
        forms = sorted(byroot.get(t, []), key=lambda x: -x[1])
        print(t, '->', [f for f in forms if f[1] > 0])


if __name__ == '__main__':
    main()
