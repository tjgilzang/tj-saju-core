import { calculateSaju } from './saju-input-client.js';

const form = document.querySelector('#sajuForm');
const statusLabel = document.querySelector('#statusMessage');
const executeButton = document.querySelector('#executeButton');
const solarDateNode = document.querySelector('#resultSolarDate');
const solarMessageNode = document.querySelector('#resultSolarMessage');
const lunarDateNode = document.querySelector('#resultLunarDate');
const lunarLeapNode = document.querySelector('#resultLunarLeap');
const gzNodes = {
  year: document.querySelector('#resultGzYear'),
  month: document.querySelector('#resultGzMonth'),
  day: document.querySelector('#resultGzDay'),
  hour: document.querySelector('#resultGzHour'),
};

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  executeButton.disabled = true;
  statusLabel.textContent = '간지를 계산 중입니다...';
  try {
    const params = collectParams(new FormData(form));
    const payload = await calculateSaju(params);
    renderResults(payload, params);
    statusLabel.textContent = payload.message || '간지가 준비되었습니다.';
  } catch (error) {
    console.error(error);
    statusLabel.textContent = '사주 계산에 실패했습니다. 입력을 다시 확인해주세요.';
    restorePlaceholders();
  } finally {
    executeButton.disabled = false;
  }
});

function collectParams(formData) {
  const calendar = formData.get('calendar') ?? 'solar';
  const leap = document.querySelector('#leapToggle')?.checked ? '1' : '0';

  return {
    year: formData.get('year') ?? '',
    month: formData.get('month') ?? '',
    day: formData.get('day') ?? '',
    hour: formData.get('hour') ?? '0',
    minute: formData.get('minute') ?? '0',
    calendar,
    gender: formData.get('gender') ?? 'M',
    leap,
  };
}

function renderResults(payload, params) {
  solarDateNode.textContent = payload.solar ?? '--';
  solarMessageNode.textContent = payload.message ?? '양력 영역';
  lunarDateNode.textContent = payload.lunar ?? '--';
  const leapFlag = payload.leap_month || Number(params.leap) === 1;
  lunarLeapNode.textContent = leapFlag ? '예' : '아니오';

  setGz('year', payload.gz_year);
  setGz('month', payload.gz_month);
  setGz('day', payload.gz_day);
  setGz('hour', payload.gz_hour);
}

function setGz(field, value) {
  const node = gzNodes[field];
  if (node) {
    node.textContent = value ?? '--';
  }
}

function restorePlaceholders() {
  solarDateNode.textContent = '--';
  solarMessageNode.textContent = '-';
  lunarDateNode.textContent = '--';
  lunarLeapNode.textContent = '-';
  Object.keys(gzNodes).forEach((key) => {
    const node = gzNodes[key];
    if (node) {
      node.textContent = '--';
    }
  });
}
