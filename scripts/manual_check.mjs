// Reusable manual UI verification for frequency-batch work (issue #14).
// Replaces writing a fresh throwaway Playwright script every batch cycle.
// Requires `npm run preview` already running (localhost:4173).
//
// Usage:
//     node scripts/manual_check.mjs word1 word2 word3 ...
import { chromium } from 'playwright';

const queries = process.argv.slice(2);
if (queries.length === 0) {
  console.error('usage: node scripts/manual_check.mjs <query> [<query> ...]');
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage();
for (const q of queries) {
  await page.goto('http://localhost:4173/pembilas/');
  await page.fill('input[type="search"], input[type="text"]', q);
  await page.waitForTimeout(400);
  console.log(`=== query: ${q} ===`);
  console.log((await page.locator('body').innerText()).slice(0, 900));
  console.log();
}
await browser.close();
