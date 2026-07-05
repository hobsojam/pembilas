---
name: frequency-batch
description: Run the next frequency-driven annotation batch for issue #14 in the bahasa-affix repo — rank candidates by corpus frequency, propose, annotate, verify, and ship as a PR. Trigger on "next batch", "batch N", or similar phrasing alone, even without further detail.
---

Assumes the previous batch's PR is merged.

## 0. Sync

```
git checkout main && git pull
git branch -d frequency-batch-<N-1>   # delete the just-merged branch
git checkout -b frequency-batch-<N>
npm run build:index
python scripts/frequency-rank.py 40
```

## 1. Survey the ranked list — don't take it at face value

For every candidate, check before including it in the batch:

- **Already covered?** `grep` the root in `data/annotations.json` and in the base root's slots. Many high scorers are duplicate headwords of an already-annotated base (e.g. `kejahatan` when `jahat.ke_an` already exists) — these get tagged `pos:"derived"` instead of annotated fresh.
- **Coincidental homograph?** If a form's mechanical derivation looks semantically unrelated to its label (e.g. `kekanan` attributed to `kan`, the tag-question particle), check the actual index entry (`[e for e in idx if e[0]==form]`) before assuming.
- **Missing base root?** If the top form is itself a derived form with no independent base in `words.json` (e.g. `mengganggu`/`gangguan` existing with no `ganggu`), consider adding the base as a new root — this has repeatedly unlocked richer families than expected (see `latih` in batch 10, which cascaded into 4 duplicate discoveries).
- **Grammaticalized / no productive derivation?** If the corpus data shows only the bare form + `-nya`, or the word is a function word/conjunction/interjection, add it to `SKIP` in `scripts/frequency-rank.py` instead of forcing a thin annotation — **actually edit the file**, don't just describe the intent in a commit message (this has been forgotten before and only caught because the same words resurfaced unchanged next batch).

Pull current glosses for the finalized list (`words[r]['gloss']`) and fix anything clearly wrong (duplicated words, wrong sense, vulgar-register mismatches) while you're there — this is now the primary gloss-quality mechanism (see #61's closure).

## 2. Propose on #14

Post a comment covering: the root list, any new roots and why, any `pos:"derived"` tags and why, gloss fixes, SKIP additions, deferred candidates. Then proceed directly to implementation (the user has established this delegation — no need to wait for a separate go-ahead each batch).

## 3. Write the apply script

A Python script that: adds `NEW_WORDS` to `words.json`, applies `GLOSS_FIXES`, tags `POS_DERIVED` roots, and writes `BATCH` slots into `annotations.json`.

**Before running it**, audit every tuple in `BATCH` for the right element count (this repo's convention is `(state, gloss, notes|None)` — exactly 3 elements). An extra trailing `None` has recurred multiple times:

```
python scripts/audit_batch_tuples.py path/to/apply_batch_N.py
```

If the script fails partway through (e.g. an unmet assert), check `git status -s data/words.json` — `words.json` is written before `annotations.json` in most of these scripts, so a mid-script crash can leave a partial write. `git checkout -- data/words.json` before re-running if so.

## 4. Validate, rebuild, triage collisions

```
npm run validate:data
npm run build:index
```

Then scan for mixed verified/unverified collisions:

```
python scripts/scan_collisions.py
```

For each hit, determine which side is the real derivation and mark the other's slot `unused` with a `notes` field starting `"collision triage (#48): ..."`. Rebuild and re-scan until it reports zero. **This has never once cleared on the first try in this repo's history — budget time for it.**

## 5. Two extra checks this repo's history says are worth doing every time

**Prefix near-miss check** (batch 7 lesson): the collision scanner above only catches *exact*-form collisions. A newly-annotated slot can also produce a *longer* junk form that starts with a real verified form and pollutes autocomplete (e.g. `kawasan.pe_an` → `pengawasanan`, a nonsense near-miss for the real `pengawasan`). Check every new verified form:

```
python scripts/scan_near_miss.py <verified_form> [<verified_form> ...]
```

Most hits are benign (real unrelated words sharing a prefix, e.g. `abu`/`abugida` — that's desirable autocomplete, not a bug). Only chase ones where the "other root" is a nonsense mechanical guess.

**Cascading-duplicate re-scan** (batch 10/11 lesson): after adding a new base root, re-check ALL of that root's newly-derived forms against `words.json` for pre-existing separate headwords — adding one base has repeatedly revealed 2-4 duplicates at once (`latih` → melatih/berlatih/pelatih/latihan; `mampu` → memampukan/kemampuan), not just the one duplicate that originally prompted the addition.

## 6. Full check suite + live verification

```
npm run lint
npm test
npx playwright test --reporter=line
```

Then actually drive the app (`npm run dev`, Playwright browser tools) and search for at least one collision-fix and one rich new family. Don't skip this — it's caught real bugs the mechanical scans missed (the near-miss pattern above was found this way, not by scanning).

## 7. Ship

Commit, push, open the PR. **Before writing commit/PR prose that describes what changed, verify it against the actual diff** (`git diff HEAD~1 HEAD -- <file> | grep -c <thing>`) rather than trusting memory of what you intended to do — a batch-8 commit message once claimed a SKIP-list edit that was never made.

```
gh pr checks <N> --watch --interval 20
```

## Housekeeping

Delete the local branch for the merged PR before starting the next batch. Keep `frequency-rank.py`'s `SKIP` set and docstring in sync with what's actually excluded.
