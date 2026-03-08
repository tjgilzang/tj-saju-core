#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from compare_core_logic import compare_cases, EXPECTED_FIELDS

CATEGORY_LABELS = [
    "양/음력 변환",
    "월주의 절기 경계",
    "일주",
    "시주",
]

FIELD_CATEGORY_MAP = {
    "expected_solar_ymd": "양/음력 변환",
    "expected_lunar_ymd": "양/음력 변환",
    "expected_gz_year": "양/음력 변환",
    "expected_gz_month": "월주의 절기 경계",
    "expected_gz_day": "일주",
    "expected_gz_hour": "시주",
}


def categorize_field(field_name: str) -> str:
    return FIELD_CATEGORY_MAP.get(field_name, "기타")


def build_category_details(mismatches) -> dict:
    detail = {label: [] for label in CATEGORY_LABELS}
    detail.setdefault("기타", [])
    for entry in mismatches:
        category = categorize_field(entry["field"])
        detail.setdefault(category, []).append(entry)
    return detail


def summarize_categories(category_details) -> list:
    return [
        {"category": category, "count": len(entries)}
        for category, entries in category_details.items()
    ]


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def write_csv(path: Path, records: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "category",
        "field",
        "expected",
        "actual",
        "legacy_source",
        "note",
        "input_calendar",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow(row)


def build_mismatch_record(entry) -> dict:
    return {
        "case_id": entry["case_id"],
        "field": entry["field"],
        "expected": entry["expected"],
        "actual": entry["actual"],
        "legacy_source": entry.get("legacy_source", ""),
        "note": entry.get("note", ""),
        "input_calendar": entry.get("input_calendar", ""),
        "category": categorize_field(entry["field"]),
    }


def format_alert(mismatch_count: int, missing_count: int, extra_count: int) -> str:
    parts = []
    if mismatch_count:
        parts.append(f"필드 불일치 {mismatch_count}건")
    if missing_count:
        parts.append(f"실제결과 누락 {missing_count}건")
    if extra_count:
        parts.append(f"예상 외 실제 {extra_count}건")
    if not parts:
        return "mismatch 없음"
    return "; ".join(parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="mismatch 자동 리포트/리트라이")
    parser.add_argument(
        "expected_csv",
        help="기준(expected) CSV",
    )
    parser.add_argument(
        "actual_csv",
        help="실제(actual) CSV",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="최대 재실행 횟수 (기본 3)",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/mismatch",
        help="출력 디렉터리 (기본 reports/mismatch)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    expected = Path(args.expected_csv)
    actual = Path(args.actual_csv)
    base_dir = Path(args.output_dir)
    history_dir = base_dir / "history"

    attempts = []
    final_status = "FAILED"
    final_payload = None

    for attempt in range(1, args.max_retries + 1):
        result = compare_cases(str(expected), str(actual))
        mismatch_records = [build_mismatch_record(m) for m in result["mismatches"]]
        mismatch_total = len(mismatch_records) + len(result["missing"]) + len(result["extra"])

        attempt_info = {
            "attempt": attempt,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "checked_cases": result["checked"],
            "missing_actual": len(result["missing"]),
            "unexpected_actual": len(result["extra"]),
            "field_mismatches": len(mismatch_records),
            "total_issues": mismatch_total,
        }
        attempts.append(attempt_info)

        history_summary = {
            "attempt": attempt,
            "timestamp": attempt_info["timestamp"],
            "status": "OK" if mismatch_total == 0 else "ISSUES",
            "checked_cases": result["checked"],
            "missing_actual": len(result["missing"]),
            "unexpected_actual": len(result["extra"]),
            "field_mismatches": len(mismatch_records),
            "details": mismatch_records,
        }

        history_file = history_dir / f"mismatch_run_{attempt}_{attempt_info['timestamp'].replace(':', '')}.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        history_file.write_text(json.dumps(history_summary, ensure_ascii=False, indent=2))

        detail_csv = history_dir / f"mismatch_details_{attempt}_{attempt_info['timestamp'].replace(':', '')}.csv"
        write_csv(detail_csv, mismatch_records)

        final_payload = {
            "results": result,
            "mismatch_records": mismatch_records,
            "history": history_summary,
        }

        if mismatch_total == 0:
            final_status = "OK"
            break

    if final_payload is None:
        print("비정상: 비교 로직 실행 실패")
        sys.exit(1)

    status_label = "OK" if final_status == "OK" else "FAILED"
    final_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    category_details = build_category_details(final_payload["mismatch_records"])
    summary_payload = {
        "timestamp": final_timestamp,
        "status": status_label,
        "status_label": "mismatch 0" if final_status == "OK" else "mismatch 존재",
        "checked_cases": final_payload["results"]["checked"],
        "missing_actual": len(final_payload["results"]["missing"]),
        "unexpected_actual": len(final_payload["results"]["extra"]),
        "field_mismatches": len(final_payload["mismatch_records"]),
        "total_issues": (
            len(final_payload["mismatch_records"])
            + len(final_payload["results"]["missing"])
            + len(final_payload["results"]["extra"])
        ),
        "category_summary": summarize_categories(category_details),
        "category_details": category_details,
        "alert_text": format_alert(
            len(final_payload["mismatch_records"]),
            len(final_payload["results"]["missing"]),
            len(final_payload["results"]["extra"]),
        ),
        "retry": {
            "max_retries": args.max_retries,
            "attempts": attempts,
        },
    }

    latest_summary_file = base_dir / "mismatch_summary.json"
    latest_details_file = base_dir / "mismatch_details.json"
    latest_csv = base_dir / "mismatch_details.csv"
    base_dir.mkdir(parents=True, exist_ok=True)
    write_json(latest_summary_file, summary_payload)
    write_json(latest_details_file, {"records": final_payload["mismatch_records"]})
    write_csv(latest_csv, final_payload["mismatch_records"])

    print("자동 비교 결과")
    print(f"  status: {status_label}")
    print(f"  mismatch: {summary_payload['field_mismatches']}")
    print(f"  missing: {summary_payload['missing_actual']} | extra: {summary_payload['unexpected_actual']}")
    print(f"  retry: {len(attempts)} / {args.max_retries}")
    print(f"  summary file: {latest_summary_file}")
    print(f"  detail file: {latest_details_file}")
    print(f"  csv log: {latest_csv}")

    if summary_payload["field_mismatches"] > 0 or summary_payload["missing_actual"] > 0 or summary_payload["unexpected_actual"] > 0:
        print(f"  alert: {summary_payload['alert_text']}")

    if summary_payload["total_issues"] > 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
