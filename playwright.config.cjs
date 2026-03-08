const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/playwright',
  timeout: 120_000,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
});
