import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  outputDir: 'test-results',
  reporter: 'line',
  use: {
    ...devices['Desktop Chrome'],
    screenshot: 'only-on-failure'
  }
});
