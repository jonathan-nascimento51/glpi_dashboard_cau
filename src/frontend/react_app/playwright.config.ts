import { defineConfig, devices } from '@playwright/test';

// Make sure Playwright only looks for E2E tests, not unit tests
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5174',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
