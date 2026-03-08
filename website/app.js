const button = document.querySelector("#golden-case-btn");
const resultsContainer = document.querySelector("#results");
const statusLabel = document.querySelector("#status");
let cached = null;

button?.addEventListener("click", async () => {
  if (cached) {
    renderResults(cached);
    return;
  }

  button.disabled = true;
  statusLabel.textContent = "골든 케이스 데이터를 불러오는 중입니다...";

  try {
    const response = await fetch("data/golden_case_results.json", { cache: "no-store" });
    if (!response.ok) throw new Error("로드 실패");
    const payload = await response.json();
    cached = payload;
    renderResults(payload);
  } catch (err) {
    statusLabel.textContent = "데이터 로드에 실패했습니다.";
    console.error(err);
    button.disabled = false;
  }
});

function renderResults(payload) {
  if (!payload?.golden_case) return;
  const { input, programs, last_updated } = payload.golden_case;
  statusLabel.textContent = `입력: ${input.datetime} (${input.timezone}) · 업데이트: ${last_updated}`;
  resultsContainer.innerHTML = programs
    .map((program) => buildCard(program))
    .join("\n");
}

function buildCard(program) {
  const { name, pillars, conversion, notes } = program;
  const pillarItems = ["year", "month", "day", "hour"]
    .map((key) => `${key}=${pillars[key]}`)
    .join(" · ");

  return `
    <article class="card">
      <h2>${name}</h2>
      <div class="pillars">${pillarItems}</div>
      <dl>
        <div>
          <dt>양력</dt>
          <dd>${conversion.solar}</dd>
        </div>
        <div>
          <dt>음력</dt>
          <dd>${conversion.lunar}${conversion.leap_month ? ' (윤달)' : ''}</dd>
        </div>
      </dl>
      <p class="conversion"><strong>월단</strong> ${conversion.lunar_month_name} · ${notes}</p>
    </article>
  `.trim();
}
