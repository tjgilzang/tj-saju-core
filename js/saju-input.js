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

const CGI_ENDPOINT = new URL('cgi-bin/saju_calc.py', window.location.href);

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  executeButton.disabled = true;
  statusLabel.textContent = '간지를 계산 중입니다...';
  try {
    const params = collectParams(new FormData(form));
    const url = `${CGI_ENDPOINT.origin}${CGI_ENDPOINT.pathname}?${params.toString()}`;
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`CGI 응답 오류: ${response.status} ${response.statusText} \n${text}`);
    }
    const payload = await response.json();
    if (payload.error) {
      throw new Error(payload.error);
    }
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
  const params = new URLSearchParams();
  params.set('year', formData.get('year') ?? '');
  params.set('month', formData.get('month') ?? '');
  params.set('day', formData.get('day') ?? '');
  params.set('hour', formData.get('hour') ?? '0');
  params.set('minute', formData.get('minute') ?? '0');

  const calendar = formData.get('calendar') ?? 'solar';
  params.set('calendar', calendar);

  const gender = formData.get('gender') ?? 'M';
  params.set('gender', gender);

  const leap = document.querySelector('#leapToggle')?.checked ? '1' : '0';
  params.set('leap', leap);

  return params;
}

function renderResults(payload, params) {
  solarDateNode.textContent = payload.solar ?? '--';
  solarMessageNode.textContent = payload.message ?? '양력 영역';
  lunarDateNode.textContent = payload.lunar ?? '--';
  lunarLeapNode.textContent = payload.leap_month === true || params.get('leap') === '1' ? '예' : '아니오';

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
    gzNodes[key].textContent = '--';
  });
}
