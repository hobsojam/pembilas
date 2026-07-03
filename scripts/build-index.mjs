/**
 * Pre-builds the search index from words.json + affixes.json.
 * Run with: npm run build:index
 * Output: data/search-index.json — a sorted array of [form, root, affixId|null]
 */
import { readFileSync, writeFileSync } from 'fs'
import { fileURLToPath, pathToFileURL } from 'url'
import { dirname, join } from 'path'
// Shared with src/lib/affixEngine.js (#60) — re-exported because this
// script is the natural import site for Node-side consumers and tests.
export { deriveForm } from '../src/lib/derive.js'
import { deriveForm } from '../src/lib/derive.js'

// --- build index ---

export function buildIndex({ words, affixes, annotations, rules }) {
  // Every word's own root, e.g. "bilai" -- used to catch generated forms
  // that collide with an unrelated dictionary headword (see issue: "bila"
  // + "-i" mechanically produces "bilai", which is actually its own
  // unrelated root).
  const rootWords = new Set(words.map(w => w.root))

  // Entries are [form, root, affixId|null] with a trailing 1 appended to
  // (ids, not display labels, so renaming a label in affixes.json is safe);
  // "verified" entries: root self-entries and slots annotated state "valid".
  // The flag is sparse (only ~6% of entries carry it) to keep the generated
  // file small; a missing flag means the form was mechanically derived from
  // an un-annotated slot and nobody has reviewed it (#48).
  const entries = []
  const seen = new Set()

  function add(form, root, affixId, verified) {
    const key = form + '\0' + root
    if (!seen.has(key)) {
      seen.add(key)
      entries.push(verified ? [form, root, affixId, 1] : [form, root, affixId])
    }
  }

  for (const word of words) {
    add(word.root, word.root, null, true)
    for (const affix of affixes) {
      const ann = annotations[word.root]?.[affix.id]
      if (ann?.state === 'unused') continue

      // An annotation's `form` overrides the algorithmic one for lexically
      // irregular derivations (see affixEngine.js / #16).
      const form = ann?.form ?? deriveForm(word.root, affix.id, rules)
      if (form === word.root) continue
      const verified = ann?.state === 'valid'
      // A mechanical derivation that collides with a dictionary headword is
      // dropped (the headword's own entry wins), but a curated one is kept:
      // many headwords are themselves lexicalized derivations (menarik,
      // berteriak, laporan, ...), and hiding the annotated parse shadowed
      // 173 curated slots from search entirely (#52/#56).
      if (rootWords.has(form) && !verified) continue

      add(form, word.root, affix.id, verified)
    }
  }

  // Within a form: verified entries before unverified ones (the search UI's
  // prefix scan surfaces curated derivations first), and a root's own entry
  // (null affix id) before derived readings of the same surface string.
  entries.sort(
    (a, b) =>
      a[0].localeCompare(b[0]) ||
      (b[3] ?? 0) - (a[3] ?? 0) ||
      (a[2] === null ? 0 : 1) - (b[2] === null ? 0 : 1)
  )
  return entries
}

function main() {
  const root = join(dirname(fileURLToPath(import.meta.url)), '..')
  const wordsData = JSON.parse(readFileSync(join(root, 'data/words.json'), 'utf8'))
  const affixData = JSON.parse(readFileSync(join(root, 'data/affixes.json'), 'utf8'))
  const annotations = JSON.parse(readFileSync(join(root, 'data/annotations.json'), 'utf8'))

  const words = wordsData.words
  const { rules } = affixData.nasalAssimilation
  const affixes = affixData.affixes

  const entries = buildIndex({ words, affixes, annotations, rules })

  writeFileSync(join(root, 'data/search-index.json'), JSON.stringify(entries))

  console.log(`Built search index: ${entries.length} entries from ${words.length} roots`)
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main()
}
