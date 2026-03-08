import { expect, test } from '@playwright/test';

test('Mismatch 대시보드 버튼 → 상태 업데이트', async ({ page }) => {
  const tracing = page.context().tracing;
  await tracing.start({ screenshots: true, snapshots: true });
  try {
    await page.goto('http://127.0.0.1:4173/reports/mismatch_dashboard.html', {
      waitUntil: 'networkidle',
    });
    const refreshBtn = page.getByRole('button', { name: '리포트 새로고침' });
    await expect(refreshBtn).toBeVisible();
    await refreshBtn.click();
    const statusBadge = page.locator('#statusBadge');
    await expect(statusBadge).toHaveText('mismatch 0', { timeout: 10_000 });
    await page.waitForTimeout(600);
    await page.screenshot({ path: 'reports/playwright/screenshot-mismatch-dashboard.png', fullPage: true });
  } finally {
    await tracing.stop({ path: 'reports/playwright/trace-mismatch-dashboard.zip' });
  }
});
