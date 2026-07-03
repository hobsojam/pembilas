/**
 * Pure affix derivation, shared by the app (src/lib/affixEngine.js) and the
 * index build script (scripts/build-index.mjs). Deliberately has no imports —
 * especially not affixes.json — so plain Node and Vite can both load it; the
 * caller supplies the nasal-assimilation `rules` from data/affixes.json.
 *
 * Before #60 each caller carried its own copy of these functions, and the
 * copies drifted twice (ter- r-elision, per-...-an) — keep this the single
 * source of truth.
 */

export function applyNasal(root, rules) {
  for (const rule of rules) {
    for (const s of rule.startsWith) {
      if (root.toLowerCase().startsWith(s)) {
        const stem = rule.dropInitial ? root.slice(s.length) : root
        return rule.prefix + stem
      }
    }
  }
  return 'me' + root
}

export function applyPeNasal(root, rules) {
  // pe- follows the same assimilation as me- but with pe/pem/pen/peng/peny
  return applyNasal(root, rules).replace(/^me/, 'pe')
}

export function deriveForm(root, affixId, rules) {
  switch (affixId) {
    case 'me':     return applyNasal(root, rules)
    case 'ber':    return root.startsWith('r') ? 'be' + root : 'ber' + root
    case 'di':     return 'di' + root
    case 'ter':    return root.startsWith('r') ? 'te' + root : 'ter' + root
    case 'ke':     return 'ke' + root
    case 'se':     return 'se' + root
    case 'pe':     return applyPeNasal(root, rules)
    case 'an':     return root + 'an'
    case 'kan':    return root + 'kan'
    case 'i':      return root + 'i'
    case 'nya':    return root + 'nya'
    case 'lah':    return root + 'lah'
    case 'me_kan': return applyNasal(root, rules) + 'kan'
    case 'me_i':   return applyNasal(root, rules) + 'i'
    case 'pe_an':  return applyPeNasal(root, rules) + 'an'
    case 'ke_an':  return 'ke' + root + 'an'
    case 'ber_an': return (root.startsWith('r') ? 'be' : 'ber') + root + 'an'
    case 'per_an': return (root.startsWith('r') ? 'pe' : 'per') + root + 'an'
    default:       return root
  }
}
