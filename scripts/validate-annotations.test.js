import { describe, it, expect } from 'vitest'
import { validateAnnotations } from './validate-annotations.mjs'

const knownAffixIds = new Set(['me', 'pe_an', 'ber'])

describe('validateAnnotations', () => {
  it('accepts a well-formed valid entry', () => {
    const errors = validateAnnotations(
      { tulis: { me: { state: 'valid', gloss: 'to write' } } },
      knownAffixIds
    )
    expect(errors).toEqual([])
  })

  it('accepts a well-formed unused entry', () => {
    const errors = validateAnnotations(
      { tulis: { ber: { state: 'unused', gloss: '' } } },
      knownAffixIds
    )
    expect(errors).toEqual([])
  })

  it('flags an unknown affix id', () => {
    const errors = validateAnnotations(
      { tulis: { bogus: { state: 'valid', gloss: 'x' } } },
      knownAffixIds
    )
    expect(errors).toEqual(['tulis.bogus: unknown affix id (not in data/affixes.json)'])
  })

  it('flags an invalid state', () => {
    const errors = validateAnnotations(
      { tulis: { me: { state: 'weird', gloss: 'x' } } },
      knownAffixIds
    )
    expect(errors).toContain('tulis.me: state must be "valid" or "unused", got "weird"')
  })

  it('flags a valid entry with an empty gloss', () => {
    const errors = validateAnnotations(
      { tulis: { me: { state: 'valid', gloss: '' } } },
      knownAffixIds
    )
    expect(errors).toContain('tulis.me: state is "valid" but gloss is empty')
  })

  it('accepts a valid entry with a non-empty form override (#16)', () => {
    const errors = validateAnnotations(
      { gunung: { pe_an: { state: 'valid', gloss: 'mountain range', form: 'pegunungan' } } },
      knownAffixIds
    )
    expect(errors).toEqual([])
  })

  it('flags an empty form override', () => {
    const errors = validateAnnotations(
      { gunung: { pe_an: { state: 'valid', gloss: 'mountain range', form: '' } } },
      knownAffixIds
    )
    expect(errors).toContain('gunung.pe_an: form is present but empty (must be a non-empty string)')
  })

  it('flags a form override on a non-valid entry', () => {
    const errors = validateAnnotations(
      { gunung: { ber: { state: 'unused', gloss: '', form: 'shouldnt-be-here' } } },
      knownAffixIds
    )
    expect(errors).toContain(
      'gunung.ber: form is set but state is not "valid" (an unused slot has nothing to override)'
    )
  })

  it('accepts non-empty notes on an unused entry (#14)', () => {
    const errors = validateAnnotations(
      {
        hati: {
          me: {
            state: 'unused',
            gloss: '',
            notes: 'the real verb is the compound "memperhatikan", which no single affix id models',
          },
        },
      },
      knownAffixIds
    )
    expect(errors).toEqual([])
  })

  it('accepts non-empty notes alongside a valid entry', () => {
    const errors = validateAnnotations(
      { tulis: { me: { state: 'valid', gloss: 'to write', notes: 'some context' } } },
      knownAffixIds
    )
    expect(errors).toEqual([])
  })

  it('flags empty notes', () => {
    const errors = validateAnnotations(
      { tulis: { me: { state: 'valid', gloss: 'to write', notes: '' } } },
      knownAffixIds
    )
    expect(errors).toContain('tulis.me: notes is present but empty (must be a non-empty string)')
  })

  describe('annotated roots must exist in words.json (#56)', () => {
    const knownRoots = new Set(['tulis'])

    it('accepts an annotated root that is a known word', () => {
      const errors = validateAnnotations(
        { tulis: { me: { state: 'valid', gloss: 'to write' } } },
        knownAffixIds,
        knownRoots
      )
      expect(errors).toEqual([])
    })

    it('flags an annotated root missing from words.json', () => {
      const errors = validateAnnotations(
        { tarik: { me: { state: 'valid', gloss: 'to pull' } } },
        knownAffixIds,
        knownRoots
      )
      expect(errors).toContain(
        'tarik: annotated root is not in data/words.json, so its annotations are unreachable in the app (#56)'
      )
    })

    it('skips the check when no root set is provided (backward compatible)', () => {
      const errors = validateAnnotations(
        { tarik: { me: { state: 'valid', gloss: 'to pull' } } },
        knownAffixIds
      )
      expect(errors).toEqual([])
    })
  })
})
