import { test, expect } from '@playwright/test';

test('home page shows Deploy link', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('link', { name: /deploy now/i })).toBeVisible();
});
