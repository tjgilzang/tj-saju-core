import csv
import logging
import os
import sys
from typing import Dict, List
from pathlib import Path

import sxtwl

sys.path.append(str(Path(__file__).resolve().parent.parent))
from scripts.core_logic import CaseInput, build_expected_payload

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

GENERAL_CASES = [
    {"year": 1986, "month": 9, "day": 2, "hour": 10, "minute": 30, "gender": "M", "note": "기준 케이스", "category": "일반"},
    {"year": 1991, "month": 5, "day": 17, "hour": 22, "minute": 10, "gender": "F", "note": "대학 입학용 케이스", "category": "일반"},
    {"year": 1975, "month": 12, "day": 1, "hour": 4, "minute": 5, "gender": "M", "note": "겨울 아침", "category": "일반"},
    {"year": 2000, "month": 1, "day": 1, "hour": 0, "minute": 0, "gender": "F", "note": "밀레니엄의 첫날", "category": "일반"},
    {"year": 1989, "month": 7, "day": 15, "hour": 13, "minute": 30, "gender": "M", "note": "여름 더위 시간", "category": "일반"},
    {"year": 1968, "month": 3, "day": 30, "hour": 18, "minute": 20, "gender": "F", "note": "춘분 경계 이후", "category": "일반"},
    {"year": 1999, "month": 11, "day": 9, "hour": 6, "minute": 50, "gender": "M", "note": "늦가을 오전", "category": "일반"},
    {"year": 1980, "month": 6, "day": 21, "hour": 12, "minute": 45, "gender": "F", "note": "하지 이전 정오", "category": "일반"},
    {"year": 2003, "month": 4, "day": 5, "hour": 2, "minute": 15, "gender": "M", "note": "새벽 일출 직전", "category": "일반"},
    {"year": 1995, "month": 10, "day": 31, "hour": 19, "minute": 55, "gender": "F", "note": "할로윈 저녁", "category": "일반"},
    {"year": 2006, "month": 8, "day": 8, "hour": 20, "minute": 0, "gender": "M", "note": "청명 이후", "category": "일반"},
    {"year": 1983, "month": 4, "day": 12, "hour": 10, "minute": 10, "gender": "F", "note": "봄 나들이 시간", "category": "일반"},
    {"year": 1997, "month": 9, "day": 9, "hour": 21, "minute": 40, "gender": "M", "note": "추석 연휴 밤", "category": "일반"},
    {"year": 2010, "month": 2, "day": 14, "hour": 0, "minute": 55, "gender": "F", "note": "발렌타인데이 자정", "category": "일반"},
    {"year": 2005, "month": 12, "day": 25, "hour": 15, "minute": 3, "gender": "M", "note": "크리스마스 오후", "category": "일반"},
    {"year": 1992, "month": 3, "day": 1, "hour": 6, "minute": 7, "gender": "F", "note": "춘삼월 아침", "category": "일반"},
    {"year": 1979, "month": 5, "day": 22, "hour": 11, "minute": 11, "gender": "M", "note": "망종 직전 오전", "category": "일반"},
    {"year": 2001, "month": 10, "day": 13, "hour": 23, "minute": 47, "gender": "F", "note": "늦가을 자정", "category": "일반"},
    {"year": 1987, "month": 6, "day": 6, "hour": 8, "minute": 24, "gender": "M", "note": "고시원 오전", "category": "일반"},
    {"year": 2015, "month": 7, "day": 19, "hour": 17, "minute": 29, "gender": "F", "note": "무더위 오후", "category": "일반"},
]

JASI_CASES = [
    {"year": 2024, "month": 1, "day": 25, "hour": 22, "minute": 45, "gender": "M", "note": "23시 진입 직전", "category": "자시 경계"},
    {"year": 2024, "month": 1, "day": 25, "hour": 23, "minute": 0, "gender": "F", "note": "23:00 정확한 자시 시작", "category": "자시 경계"},
    {"year": 2024, "month": 1, "day": 25, "hour": 23, "minute": 59, "gender": "M", "note": "자시 깊은 밤", "category": "자시 경계"},
    {"year": 2024, "month": 1, "day": 26, "hour": 0, "minute": 0, "gender": "F", "note": "0시 정각 자시", "category": "자시 경계"},
    {"year": 2024, "month": 1, "day": 26, "hour": 0, "minute": 30, "gender": "M", "note": "자시 마무리", "category": "자시 경계"},
    {"year": 2023, "month": 12, "day": 31, "hour": 23, "minute": 59, "gender": "F", "note": "년말 자시", "category": "자시 경계"},
    {"year": 2024, "month": 1, "day": 1, "hour": 0, "minute": 5, "gender": "M", "note": "새해 0시 자시", "category": "자시 경계"},
    {"year": 2023, "month": 8, "day": 7, "hour": 22, "minute": 30, "gender": "F", "note": "곳날 22시", "category": "자시 경계"},
    {"year": 2023, "month": 8, "day": 7, "hour": 23, "minute": 15, "gender": "M", "note": "자시 막바지 23시", "category": "자시 경계"},
    {"year": 2023, "month": 8, "day": 8, "hour": 0, "minute": 0, "gender": "F", "note": "8월 8일 0시", "category": "자시 경계"},
]

SOLAR_TERM_CASES = [
    {"year": 2023, "month": 2, "day": 3, "hour": 10, "minute": 5, "gender": "M", "note": "입춘 전날", "category": "절기 경계"},
    {"year": 2023, "month": 2, "day": 4, "hour": 10, "minute": 15, "gender": "F", "note": "입춘 당일", "category": "절기 경계"},
    {"year": 2023, "month": 3, "day": 4, "hour": 11, "minute": 30, "gender": "M", "note": "경칩 직전", "category": "절기 경계"},
    {"year": 2023, "month": 3, "day": 6, "hour": 9, "minute": 0, "gender": "F", "note": "경칩 이후", "category": "절기 경계"},
    {"year": 2023, "month": 4, "day": 4, "hour": 16, "minute": 45, "gender": "M", "note": "청명 전", "category": "절기 경계"},
    {"year": 2023, "month": 4, "day": 5, "hour": 12, "minute": 10, "gender": "F", "note": "청명 당일", "category": "절기 경계"},
    {"year": 2023, "month": 6, "day": 20, "hour": 13, "minute": 58, "gender": "M", "note": "하지 전야", "category": "절기 경계"},
    {"year": 2023, "month": 6, "day": 21, "hour": 14, "minute": 3, "gender": "F", "note": "하지 정시", "category": "절기 경계"},
    {"year": 2023, "month": 9, "day": 22, "hour": 1, "minute": 50, "gender": "M", "note": "추분 초", "category": "절기 경계"},
    {"year": 2023, "month": 9, "day": 23, "hour": 2, "minute": 5, "gender": "F", "note": "추분 이후", "category": "절기 경계"},
]


def build_leap_cases(limit: int = 10) -> List[Dict]:
    leap_cases = []
    year = 1980
    while len(leap_cases) < limit and year < 2040:
        run_month = sxtwl.getRunMonth(year)
        if run_month > 0:
            idx = len(leap_cases)
            leap_cases.append(
                {
                    "input_calendar": "lunar",
                    "is_leap_month": 1,
                    "year": year,
                    "month": run_month,
                    "day": 10 + (idx % 5),
                    "hour": (7 + idx) % 24,
                    "minute": 12 * idx % 60,
                    "gender": "F" if idx % 2 else "M",
                    "note": f"{year}년 윤달 {run_month}월 중순",
                    "category": "윤달",
                }
            )
        year += 1
    return leap_cases


def main():
    rows = []
    template_list = []
    template_list.extend(GENERAL_CASES)
    template_list.extend(build_leap_cases())
    template_list.extend(JASI_CASES)
    template_list.extend(SOLAR_TERM_CASES)

    assert len(template_list) == 50, "케이스 수가 50개가 아닙니다."

    for idx, base in enumerate(template_list, start=1):
        row = {
            "case_id": f"case-{idx:03d}",
            "input_calendar": base.get("input_calendar", "solar"),
            "is_leap_month": int(base.get("is_leap_month", 0)),
            "year": base["year"],
            "month": base["month"],
            "day": base["day"],
            "hour": base["hour"],
            "minute": base["minute"],
            "gender": base.get("gender", "M"),
            "legacy_source": base.get("legacy_source", "sxtwl-canonical"),
            "note": base.get("note", ""),
            "category": base.get("category", "일반"),
        }
        case_input = CaseInput(
            case_id=row["case_id"],
            input_calendar=row["input_calendar"],
            is_leap_month=row["is_leap_month"],
            year=row["year"],
            month=row["month"],
            day=row["day"],
            hour=row["hour"],
            minute=row["minute"],
            gender=row["gender"],
            legacy_source=row["legacy_source"],
            note=row["note"],
            category=row["category"],
        )
        expected = build_expected_payload(case_input)
        rows.append({**row, **expected})

    os.makedirs("data/validation", exist_ok=True)
    fieldnames = [
        "case_id",
        "input_calendar",
        "is_leap_month",
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "gender",
        "category",
        "expected_solar_ymd",
        "expected_lunar_ymd",
        "expected_gz_year",
        "expected_gz_month",
        "expected_gz_day",
        "expected_gz_hour",
        "legacy_source",
        "note",
    ]
    path = "data/validation/core_cases_v2.csv"
    with open(path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logging.info("core_cases_v2.csv 생성 완료 (%s cases)", len(rows))


if __name__ == "__main__":
    main()
