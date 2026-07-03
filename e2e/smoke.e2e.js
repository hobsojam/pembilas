import { test, expect } from '@playwright/test'

// Smoke tests for the seams the unit tests structurally can't cover:
// the real lazy-loaded search index, the built bundle, and the
// search -> word page flow driven through the production build.

test('searching a derived form lands on the curated word page', async ({ page }) => {
  await page.goto('/pembilas/')

  const input = page.getByRole('combobox', { name: /search root or derived form/i })
  await input.fill('menulis')

  // The real 6MB index is a lazy chunk; the option appears once it loads.
  await page.getByRole('option', { name: /tulis/ }).first().click()

  await expect(page.getByRole('heading', { name: /derived forms/i })).toBeVisible()
  await expect(page.getByRole('cell', { name: 'menulis', exact: true })).toBeVisible()
  await expect(page.getByRole('cell', { name: 'to write (active)' })).toBeVisible()
})

test('an un-annotated derivation shows the mechanical row instead of a dead end (#53)', async ({ page }) => {
  await page.goto('/pembilas/')

  const input = page.getByRole('combobox', { name: /search root or derived form/i })
  // "abaktinal" (abactinal, zoology) is deliberately obscure: it will never
  // be curated, so this arrival stays on the mechanical-row path even as
  // annotation batches grow.
  await input.fill('mengabaktinal')
  await page.getByRole('option', { name: /abaktinal/ }).first().click()

  await expect(page.getByText('mechanically derived — not yet reviewed')).toBeVisible()
})
