import affixData from '../../data/affixes.json'
import { deriveForm as derive } from './derive.js'

const { rules } = affixData.nasalAssimilation

// The derivation logic itself lives in derive.js (shared with
// scripts/build-index.mjs, see #60); this module just binds the
// nasal-assimilation rules from affixes.json.
export function deriveForm(root, affixId) {
  return derive(root, affixId, rules)
}

export const affixes = affixData.affixes
