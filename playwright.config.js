import { defineConfig } from '@playwright/test'

// End-to-end smoke tests against the production build (`vite preview`
// serves dist/ under the /pembilas/ base path, matching GitHub Pages).
// Files are named *.e2e.js so Vitest's default *.{test,spec}.js glob
// never picks them up.
export default defineConfig({
  testDir: 'e2e',
  testMatch: '**/*.e2e.js',
  use: {
    baseURL: 'http://localhost:4173',
  },
  webServer: {
    command: 'npm run preview',
    url: 'http://localhost:4173/pembilas/',
    reuseExistingServer: !process.env.CI,
  },
})
