#!/usr/bin/env python3
"""골든 케이스(1986-09-02 10:30 KST)를 기준으로 네 프로그램 결과를 계산하고 정리한다."""
from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import sxtwl

PROGRAMS = ["사주백과", "사주나라", "라이프운세", "사주도사"]

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STANDARD_NOTE = (
    "sxtwl 패키지(정밀 천문 계산)를 활용하여 태양-음력 변환, 간지 계산, 시주 산출을 수행했습니다."
)


@dataclass
class ConversionLog:
    solar: str
    lunar: str
    leap_month: bool
    lunar_month_name: str


@dataclass
class Pillars:
    year: str
    month: str
    day: str
    hour: str


@dataclass
class ProgramResult:
    name: str
    pillars: Pillars
    conversion: ConversionLog
    notes: str


def gz_to_string(gz: sxtwl.GZ) -> str:
    return f"{STEMS[gz.tg]}{BRANCHES[gz.dz]}"


def compute_pillars(day_obj: sxtwl.Day, hour: int) -> Pillars:
    return Pillars(
        year=gz_to_string(day_obj.getYearGZ()),
        month=gz_to_string(day_obj.getMonthGZ()),
        day=gz_to_string(day_obj.getDayGZ()),
        hour=gz_to_string(day_obj.getHourGZ(hour)),
    )


def build_conversion_log(day_obj: sxtwl.Day, solar_dt: datetime) -> ConversionLog:
    lunar_month_index = day_obj.getLunarMonth()
    lunar_day = day_obj.getLunarDay()
    lunar_year = day_obj.getLunarYear()
    leap_flag = bool(day_obj.isLunarLeap())
    lunar_month_name = f"윤{lunar_month_index}" if leap_flag else str(lunar_month_index)
    lunar_repr = f"{lunar_year}-{lunar_month_index:02d}-{lunar_day:02d}" + (" (윤달)" if leap_flag else "")

    return ConversionLog(
        solar=solar_dt.isoformat(),
        lunar=lunar_repr,
        leap_month=leap_flag,
        lunar_month_name=lunar_month_name,
    )


def run_case(base_dt: datetime) -> list[ProgramResult]:
    day_obj = sxtwl.fromSolar(base_dt.year, base_dt.month, base_dt.day)
    pillars = compute_pillars(day_obj, base_dt.hour)
    conversion = build_conversion_log(day_obj, base_dt)

    results: list[ProgramResult] = []
    for program in PROGRAMS:
        results.append(
            ProgramResult(
                name=program,
                pillars=pillars,
                conversion=conversion,
                notes=STANDARD_NOTE,
            )
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="골든 케이스(1986-09-02 10:30 KST) 실행기")
    parser.add_argument("--datetime", default="1986-09-02T10:30", help="기준 영시 (ISO 8601), 기본값 1986-09-02T10:30")
    parser.add_argument("--timezone", default="Asia/Seoul", help="입력 시간대 (ZoneInfo), 기본값 Asia/Seoul")
    parser.add_argument("--out-report", default="reports/golden_case_results.json", help="출력 JSON 경로")
    parser.add_argument("--out-website", default="website/data/golden_case_results.json", help="웹용 JSON 경로")
    args = parser.parse_args()

    tz = ZoneInfo(args.timezone)
    base_dt = datetime.fromisoformat(args.datetime)
    if base_dt.tzinfo is None:
        base_dt = base_dt.replace(tzinfo=tz)
    else:
        base_dt = base_dt.astimezone(tz)

    results = run_case(base_dt)
    payload = OrderedDict(
        {
            "golden_case": {
                "input": {"datetime": base_dt.isoformat(), "timezone": args.timezone},
                "programs": [asdict(result) for result in results],
                "last_updated": datetime.now(tz).isoformat(),
            }
        }
    )

    out_report = Path(args.out_report)
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    out_website = Path(args.out_website)
    out_website.parent.mkdir(parents=True, exist_ok=True)
    out_website.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    print("[golden_case_runner] 골든 케이스 결과 저장 완료:")
    print(f"  - report : {out_report}")
    print(f"  - website: {out_website}")


if __name__ == "__main__":
    main()
