const STEMS = ["갑","을","병","정","무","기","경","신","임","계"];
const BRANCHES = ["자","축","인","묘","진","사","오","미","신","유","술","해"];
const LOOKUP_BINARY_URL = new URL("../data/calendar-lookup.bin", import.meta.url);
const LOOKUP_META_URL = new URL("../data/calendar-lookup-metadata.json", import.meta.url);
const MS_PER_DAY = 24 * 60 * 60 * 1000;

const OFFSETS = {
  solarYear: 0,
  solarMonth: 2,
  solarDay: 3,
  lunarYear: 4,
  lunarMonth: 6,
  lunarDay: 7,
  isLeap: 8,
  yearStem: 9,
  yearDz: 10,
  monthStem: 11,
  monthDz: 12,
  dayStem: 13,
  dayDz: 14,
};
const HOURS_OFFSET = 15;

const lookupState = {
  loadingPromise: null,
  view: null,
  recordSize: 0,
  recordCount: 0,
  startTimestamp: 0,
  lunarIndex: null,
};

async function ensureLookupLoaded() {
  if (lookupState.loadingPromise) {
    return lookupState.loadingPromise;
  }

  lookupState.loadingPromise = (async () => {
    const [metaResponse, binaryResponse] = await Promise.all([
      fetch(LOOKUP_META_URL, { cache: "no-store" }),
      fetch(LOOKUP_BINARY_URL, { cache: "no-store" }),
    ]);
    if (!metaResponse.ok || !binaryResponse.ok) {
      throw new Error("사주 데이터 로드에 실패했습니다.");
    }

    const metadata = await metaResponse.json();
    const buffer = await binaryResponse.arrayBuffer();
    if (buffer.byteLength !== metadata.record_count * metadata.record_size) {
      throw new Error("사주 데이터 크기 불일치");
    }

    lookupState.view = new DataView(buffer);
    lookupState.recordSize = metadata.record_size;
    lookupState.recordCount = metadata.record_count;
    lookupState.startTimestamp = Date.UTC(
      metadata.start_year,
      metadata.start_month - 1,
      metadata.start_day,
    );

    lookupState.lunarIndex = new Map();
    for (let idx = 0; idx < lookupState.recordCount; idx += 1) {
      const base = idx * lookupState.recordSize;
      const lunarYear = lookupState.view.getUint16(base + OFFSETS.lunarYear, true);
      const lunarMonth = lookupState.view.getUint8(base + OFFSETS.lunarMonth);
      const lunarDay = lookupState.view.getUint8(base + OFFSETS.lunarDay);
      const isLeap = lookupState.view.getUint8(base + OFFSETS.isLeap);
      const key = buildLunarKey(lunarYear, lunarMonth, lunarDay, isLeap);
      if (!lookupState.lunarIndex.has(key)) {
        lookupState.lunarIndex.set(key, idx);
      }
    }
  })();

  return lookupState.loadingPromise;
}

function buildLunarKey(year, month, day, leap) {
  return `${year}-${month}-${day}-${leap}`;
}

function ensureYearMonthDay(year, month, day) {
  if (!Number.isInteger(year)) {
    throw new Error("연도는 정수여야 합니다.");
  }
  if (month < 1 || month > 12) {
    throw new Error("월은 1~12 사이여야 합니다.");
  }
  if (day < 1 || day > 31) {
    throw new Error("일은 1~31 사이여야 합니다.");
  }
}

function getSolarIndex(year, month, day) {
  const target = new Date(Date.UTC(year, month - 1, day));
  if (
    target.getUTCFullYear() !== year ||
    target.getUTCMonth() + 1 !== month ||
    target.getUTCDate() !== day
  ) {
    throw new Error("유효한 양력 날짜를 입력해주세요.");
  }

  const diff = target.getTime() - lookupState.startTimestamp;
  const index = Math.round(diff / MS_PER_DAY);
  if (index < 0 || index >= lookupState.recordCount) {
    throw new Error("지원 범위를 벗어났습니다 (1900-01-01 ~ 2099-12-31).");
  }
  return index;
}

function readRecord(index) {
  const base = index * lookupState.recordSize;
  const view = lookupState.view;
  const solarYear = view.getUint16(base + OFFSETS.solarYear, true);
  const solarMonth = view.getUint8(base + OFFSETS.solarMonth);
  const solarDay = view.getUint8(base + OFFSETS.solarDay);
  const lunarYear = view.getUint16(base + OFFSETS.lunarYear, true);
  const lunarMonth = view.getUint8(base + OFFSETS.lunarMonth);
  const lunarDay = view.getUint8(base + OFFSETS.lunarDay);
  const isLeap = view.getUint8(base + OFFSETS.isLeap);
  const yearStem = view.getUint8(base + OFFSETS.yearStem);
  const yearBranch = view.getUint8(base + OFFSETS.yearDz);
  const monthStem = view.getUint8(base + OFFSETS.monthStem);
  const monthBranch = view.getUint8(base + OFFSETS.monthDz);
  const dayStem = view.getUint8(base + OFFSETS.dayStem);
  const dayBranch = view.getUint8(base + OFFSETS.dayDz);

  const hours = [];
  let offset = base + HOURS_OFFSET;
  for (let i = 0; i < 24; i += 1) {
    const stem = view.getUint8(offset);
    const branch = view.getUint8(offset + 1);
    hours.push({ stem, branch });
    offset += 2;
  }

  return {
    solarYear,
    solarMonth,
    solarDay,
    lunarYear,
    lunarMonth,
    lunarDay,
    isLeap,
    yearStem,
    yearBranch,
    monthStem,
    monthBranch,
    dayStem,
    dayBranch,
    hours,
  };
}

function formatYmd(year, month, day) {
  const paddedMonth = String(month).padStart(2, "0");
  const paddedDay = String(day).padStart(2, "0");
  return `${year}-${paddedMonth}-${paddedDay}`;
}

function formatGz(stem, branch) {
  const stemLabel = STEMS[stem] ?? "?";
  const branchLabel = BRANCHES[branch] ?? "?";
  return `${stemLabel}${branchLabel}`;
}

function parseInteger(value, name, min, max) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || !Number.isInteger(parsed)) {
    throw new Error(`${name}은 정수여야 합니다.`);
  }
  if (min !== undefined && parsed < min) {
    throw new Error(`${name}은 ${min} 이상이어야 합니다.`);
  }
  if (max !== undefined && parsed > max) {
    throw new Error(`${name}은 ${max} 이하이어야 합니다.`);
  }
  return parsed;
}

export async function calculateSaju(input) {
  await ensureLookupLoaded();

  const calendar = (input.calendar || "solar").toLowerCase();
  const year = parseInteger(input.year, "연도", 1900, 2099);
  const month = parseInteger(input.month, "월", 1, 12);
  const day = parseInteger(input.day, "일", 1, 31);
  ensureYearMonthDay(year, month, day);
  const hour = parseInteger(input.hour ?? 0, "시", 0, 23);
  const leap = Number(input.leap) ? 1 : 0;

  let index;
  if (calendar === "solar") {
    index = getSolarIndex(year, month, day);
  } else if (calendar === "lunar") {
    const key = buildLunarKey(year, month, day, leap);
    index = lookupState.lunarIndex.get(key);
    if (index === undefined) {
      throw new Error("해당 음력 날짜가 존재하지 않거나 윤달 설정이 잘못되었습니다.");
    }
  } else {
    throw new Error("calendar는 solar 또는 lunar 여야 합니다.");
  }

  const record = readRecord(index);
  const hourGz = record.hours[hour];
  if (!hourGz) {
    throw new Error("시(hour)가 범위를 벗어났습니다.");
  }

  return {
    solar: formatYmd(record.solarYear, record.solarMonth, record.solarDay),
    lunar: formatYmd(record.lunarYear, record.lunarMonth, record.lunarDay),
    gz_year: formatGz(record.yearStem, record.yearBranch),
    gz_month: formatGz(record.monthStem, record.monthBranch),
    gz_day: formatGz(record.dayStem, record.dayBranch),
    gz_hour: formatGz(hourGz.stem, hourGz.branch),
    leap_month: calendar === "lunar" && Boolean(leap),
    message: "계산을 완료했습니다.",
  };
}
