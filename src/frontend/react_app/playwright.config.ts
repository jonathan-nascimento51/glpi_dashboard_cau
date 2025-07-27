import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Look for test files in the "tests" directory, relative to this configuration file.
  testDir: './tests',
  // Run your local dev server before starting the tests.
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5174/',
    // @ts-expect-error: process is provided by Node.js, and Playwright config runs in Node context
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:5174',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
