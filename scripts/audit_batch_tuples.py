"""
Audits an apply script's BATCH dict for malformed slot tuples (#14 workflow).

Each batch's apply script defines a BATCH dict of
{root: {affix_id: (state, gloss, notes|None)}} slots -- exactly 3 elements
per tuple. An extra trailing None (or a missing element) has slipped in
more than once across past batches and silently corrupts annotations.json,
so this is run before every batch's apply script executes.

Usage:
    python scripts/audit_batch_tuples.py path/to/apply_batch_N.py
"""
import ast
import sys


def main():
    if len(sys.argv) != 2:
        sys.exit('usage: audit_batch_tuples.py path/to/apply_batch_N.py')
    script_path = sys.argv[1]
    tree = ast.parse(open(script_path, encoding='utf-8').read())
    bad = []

    class V(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'BATCH':
                for rk, rd in zip(node.value.keys, node.value.values):
                    for ak, tup in zip(rd.keys, rd.values):
                        if len(tup.elts) != 3:
                            bad.append((rk.value, ak.value, len(tup.elts)))

    V().visit(tree)

    if bad:
        for root, affix, n in bad:
            print(f'BAD: {root} {affix} has {n} elements (expected 3)')
        sys.exit(1)
    print(f'OK: all BATCH tuples in {script_path} have 3 elements')


if __name__ == '__main__':
    main()
