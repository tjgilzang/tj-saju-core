const fs = require('fs');
const path = require('path');
const { test, expect } = require('@playwright/test');

const REPORT_DIR = path.resolve(__dirname, '..', '..', 'reports', 'playwright');
const LOG_PATH = path.join(REPORT_DIR, 'firestore_status.log');
const TRACE_PATH = path.join(REPORT_DIR, 'firestore_status_trace.zip');
const SCREENSHOT_PATH = path.join(REPORT_DIR, 'firestore_status.png');
const UI_URL = 'http://127.0.0.1:8000/ui/index.html';

const appendLog = (line) => {
  fs.appendFileSync(LOG_PATH, `${new Date().toISOString()} ${line}\n`);
};

test.beforeEach(() => {
  fs.writeFileSync(LOG_PATH, '');
  appendLog('Playwright 테스트 시작');
});

test('Firestore 대시보드에서 요약 카드 검증', async ({ page, context }) => {
  page.on('console', (message) => {
    appendLog(`[console] ${message.type().toUpperCase()}: ${message.text()}`);
  });
  await context.tracing.start({ screenshots: true, snapshots: true });
  appendLog('페이지 로드 시작');
  await page.goto(UI_URL, { waitUntil: 'networkidle' });
  appendLog('페이지 로드 완료');
  const summary = page.locator('#status-summary');
  await expect(summary).toContainText('처리됨');
  await expect(summary).toContainText('성공');
  await expect(summary).toContainText('실패');
  await expect(summary).not.toContainText('요약 정보를 불러오는 중입니다');
  const timestamp = page.locator('#status-timestamp');
  await expect(timestamp).toHaveText(/^생성 시각:/);
  const items = page.locator('#program-summaries > li');
  await expect(items).toHaveCount(4);
  await expect(items.first()).toContainText('정상');
  await page.screenshot({ path: SCREENSHOT_PATH, fullPage: true });
  appendLog('스크린샷 저장 완료');
  await context.tracing.stop({ path: TRACE_PATH });
  appendLog('트레이스 저장 완료');
});
