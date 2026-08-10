import { test, expect } from '@playwright/test';

test('captures the local reference at wide and narrow viewports', async ({ page }, testInfo) => {
  const errors: string[] = [];
  const failedRequests: string[] = [];
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });
  page.on('pageerror', error => errors.push(error.message));
  page.on('requestfailed', request => failedRequests.push(request.url()));

  await page.goto('http://127.0.0.1:4173');
  await expect(page.getByRole('heading', { name: 'Reference workspace' })).toBeVisible();
  const initialAria = await page.locator('body').ariaSnapshot();
  await testInfo.attach('initial-aria.yml', {
    body: initialAria,
    contentType: 'text/yaml'
  });

  await page.getByRole('button', { name: 'Menu' }).click();
  await expect(page.getByRole('status')).toHaveText('Navigation open');
  await page.getByRole('button', { name: 'Use dark theme' }).click();
  await expect(page.getByRole('button', { name: 'Use light theme' })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('wide-dark.png'), fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  const narrowAria = await page.locator('body').ariaSnapshot();
  await testInfo.attach('narrow-aria.yml', {
    body: narrowAria,
    contentType: 'text/yaml'
  });
  await page.screenshot({ path: testInfo.outputPath('narrow-dark.png'), fullPage: true });

  expect(errors).toEqual([]);
  expect(failedRequests).toEqual([]);
});

test('optionally captures a supplied public reference', async ({ page }, testInfo) => {
  const url = process.env.UI_STUDIO_PUBLIC_URL;
  test.skip(!url, 'Set UI_STUDIO_PUBLIC_URL to include the public-reference case.');
  await page.goto(url!);
  await expect(page.locator('body')).toBeVisible();
  const aria = await page.locator('body').ariaSnapshot();
  await testInfo.attach('public-aria.yml', { body: aria, contentType: 'text/yaml' });
  await page.screenshot({ path: testInfo.outputPath('public.png'), fullPage: true });
});
