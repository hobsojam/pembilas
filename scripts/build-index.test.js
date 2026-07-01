import { describe, it, expect } from 'vitest'
import affixData from '../data/affixes.json'
import realAnnotations from '../data/annotations.json'
import { deriveForm, buildIndex } from './build-index.mjs'

const { rules } = affixData.nasalAssimilation

describe('deriveForm', () => {
  it('applies nasal assimilation for me-', () => {
    expect(deriveForm('tulis', 'me', rules)).toBe('menulis')
  })

  it('falls back to the root for an unknown affix id', () => {
    expect(deriveForm('tulis', 'bogus', rules)).toBe('tulis')
  })
})

describe('buildIndex', () => {
  const affixes = [
    { id: 'me', label: 'me-' },
    { id: 'pe_an', label: 'pe-...-an' },
  ]
  const words = [{ root: 'gunung' }, { root: 'tulis' }]

  it('uses an annotation form override instead of the algorithmic derivation (#16)', () => {
    const annotations = {
      gunung: {
        pe_an: { state: 'valid', gloss: 'mountain range', form: 'pegunungan' },
      },
    }
    const entries = buildIndex({ words, affixes, annotations, rules })

    expect(entries).toContainEqual(['pegunungan', 'gunung', 'pe-...-an'])
    // The algorithmic (wrong) nasal-assimilated form must not sneak in too.
    expect(entries.some(([form]) => form === 'penggunungan')).toBe(false)
  })

  it('skips slots marked unused', () => {
    const annotations = { tulis: { me: { state: 'unused', gloss: '' } } }
    const entries = buildIndex({ words, affixes, annotations, rules })
    expect(entries.some(([, root, label]) => root === 'tulis' && label === 'me-')).toBe(false)
  })

  it("always includes each word's own root with a null label", () => {
    const entries = buildIndex({ words, affixes, annotations: {}, rules })
    expect(entries).toContainEqual(['gunung', 'gunung', null])
    expect(entries).toContainEqual(['tulis', 'tulis', null])
  })
})

describe('real irregular-word data (#16 regression)', () => {
  it('gunung.pe_an is overridden to the irregular pegunungan', () => {
    expect(realAnnotations.gunung.pe_an).toEqual({
      state: 'valid',
      gloss: 'mountain range',
      form: 'pegunungan',
    })
  })

  it('tahu.me_i is overridden to the irregular mengetahui', () => {
    expect(realAnnotations.tahu.me_i.state).toBe('valid')
    expect(realAnnotations.tahu.me_i.form).toBe('mengetahui')
  })

  it('percaya.me_i is overridden to the irregular mempercayai', () => {
    expect(realAnnotations.percaya.me_i.state).toBe('valid')
    expect(realAnnotations.percaya.me_i.form).toBe('mempercayai')
  })

  it('arti.pe_an is overridden to the irregular pengertian', () => {
    expect(realAnnotations.arti.pe_an.state).toBe('valid')
    expect(realAnnotations.arti.pe_an.form).toBe('pengertian')
  })

  it('mulai.per_an is overridden to the irregular permulaan', () => {
    expect(realAnnotations.mulai.per_an.state).toBe('valid')
    expect(realAnnotations.mulai.per_an.form).toBe('permulaan')
  })

  it('kerja.pe is overridden to the irregular pekerja', () => {
    expect(realAnnotations.kerja.pe.state).toBe('valid')
    expect(realAnnotations.kerja.pe.form).toBe('pekerja')
  })

  it('khawatir.me_kan is fixed via the new "kh" nasal-assimilation rule, no override needed', () => {
    // Unlike the other five, khawatir turned out to be a missing phonological
    // rule (the "kh" digraph never drops before nasal prefixes) rather than
    // a truly lexical irregularity, so this one has no `form` override --
    // deriveForm() computes "mengkhawatirkan" correctly on its own now.
    expect(realAnnotations.khawatir.me_kan.state).toBe('valid')
    expect(realAnnotations.khawatir.me_kan.form).toBeUndefined()
    expect(deriveForm('khawatir', 'me_kan', rules)).toBe('mengkhawatirkan')
  })
})
