import logging
from dataclasses import dataclass
from datetime import date
from typing import Dict, NamedTuple, Optional

import sxtwl

STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
EXPECTED_FIELDS = [
    "expected_solar_ymd",
    "expected_lunar_ymd",
    "expected_gz_year",
    "expected_gz_month",
    "expected_gz_day",
    "expected_gz_hour",
]


class CaseInput(NamedTuple):
    case_id: str
    input_calendar: str
    is_leap_month: int
    year: int
    month: int
    day: int
    hour: int
    minute: int
    gender: str
    legacy_source: str
    note: str
    category: str


def format_ymd(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def gz_to_str(gz: sxtwl.GZ) -> str:
    return f"{STEMS[gz.tg]}{BRANCHES[gz.dz]}"


def to_case_input(raw: Dict[str, str]) -> CaseInput:
    return CaseInput(
        case_id=raw["case_id"],
        input_calendar=raw["input_calendar"],
        is_leap_month=int(raw["is_leap_month"]),
        year=int(raw["year"]),
        month=int(raw["month"]),
        day=int(raw["day"]),
        hour=int(raw["hour"]),
        minute=int(raw["minute"]),
        gender=raw.get("gender", "M"),
        legacy_source=raw.get("legacy_source", "canonical"),
        note=raw.get("note", ""),
        category=raw.get("category", "general"),
    )


def resolve_solar(case: CaseInput) -> sxtwl.Day:
    if case.input_calendar == "lunar":
        lunar_day = sxtwl.fromLunar(case.year, case.month, case.day, bool(case.is_leap_month))
        return lunar_day
    return sxtwl.fromSolar(case.year, case.month, case.day)


def build_expected_payload(case: CaseInput) -> Dict[str, str]:
    log = logging.getLogger(__name__)
    solar_day = resolve_solar(case)
    solar_year = solar_day.getSolarYear()
    solar_month = solar_day.getSolarMonth()
    solar_day_of_month = solar_day.getSolarDay()
    lunar_year = solar_day.getLunarYear()
    lunar_month = solar_day.getLunarMonth()
    lunar_day_of_month = solar_day.getLunarDay()

    lunar_ymd = format_ymd(lunar_year, lunar_month, lunar_day_of_month)
    solar_ymd = format_ymd(solar_year, solar_month, solar_day_of_month)

    expected = {
        "expected_solar_ymd": solar_ymd,
        "expected_lunar_ymd": lunar_ymd,
        "expected_gz_year": gz_to_str(solar_day.getYearGZ()),
        "expected_gz_month": gz_to_str(solar_day.getMonthGZ()),
        "expected_gz_day": gz_to_str(solar_day.getDayGZ()),
        "expected_gz_hour": gz_to_str(solar_day.getHourGZ(case.hour)),
    }

    log.debug("case %s -> %s", case.case_id, expected)
    return expected


def build_actual_payload(case: CaseInput, module: str) -> Dict[str, str]:
    payload = build_expected_payload(case)
    payload["module"] = module
    payload["case_id"] = case.case_id
    return payload


def _is_mismatch(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() not in {"false", "0", "", "none"}


def summary_from_runs(cases: Dict[str, CaseInput], modules: Dict[str, str], module_rows: Dict[str, list]) -> Dict[str, object]:
    total = len(cases)
    mismatches = 0
    module_summary = {}
    for module_key, rows in module_rows.items():
        mismatch = sum(1 for row in rows if _is_mismatch(row.get("mismatched")))
        module_summary[module_key] = {"name": modules[module_key], "cases": len(rows), "mismatch": mismatch}
        mismatches += mismatch

    return {"total": total, "mismatch": mismatches, "module_summary": module_summary}
