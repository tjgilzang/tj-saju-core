import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).resolve().parent.parent))
from scripts.core_logic import (
    CaseInput,
    EXPECTED_FIELDS,
    build_actual_payload,
    summary_from_runs,
    to_case_input,
)

MODULE_LABELS: Dict[str, str] = {
    "sajubaekgwa": "사주백과",
    "sajunara": "사주나라",
    "lifeunse": "라이프운세",
    "sajudosa": "사주도사",
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "validation"
DOCS_JSON_PATH = BASE_DIR / "docs" / "data" / "batch_results_v2.json"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports" / "validation"


def setup_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("core_batch")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def load_cases(path: Path) -> List[Dict]:
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [row for row in reader]


def run_case(case: CaseInput, module_key: str, module_label: str, logger: logging.Logger) -> Dict[str, str]:
    attempts = 0
    last_exception = None
    while attempts < 3:
        try:
            return build_actual_payload(case, module_label)
        except Exception as exc:  # pragma: no cover
            attempts += 1
            last_exception = exc
            logger.warning("%s 회차 실패: case=%s module=%s error=%s", attempts, case.case_id, module_label, exc)
    assert last_exception is not None
    logger.error("최종 실패: case=%s module=%s", case.case_id, module_label)
    raise last_exception


def write_actual_csv(module_key: str, rows: List[Dict[str, str]]) -> Path:
    path = DATA_DIR / f"actual_core_results_{module_key}_v2.csv"
    fieldnames = ["case_id", "module"] + EXPECTED_FIELDS + ["mismatched"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "case_id": row["case_id"],
                "module": row.get("module", ""),
                **{field: row.get(field, "") for field in EXPECTED_FIELDS},
                "mismatched": row.get("mismatched", False),
            })
    return path

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    log_path = LOGS_DIR / f"core_batch_{timestamp}.log"
    logger = setup_logger(log_path)

    start = datetime.utcnow()
    logger.info("50케이스 배치 시작")

    csv_path = DATA_DIR / "core_cases_v2.csv"
    rows = load_cases(csv_path)
    case_entries = []
    for row in rows:
        case_entries.append({"row": row, "input": to_case_input(row)})

    module_rows: Dict[str, List[Dict[str, str]]] = {k: [] for k in MODULE_LABELS}
    ui_cases = []

    for entry in case_entries:
        case_input: CaseInput = entry["input"]
        row = entry["row"]
        case_modules = {}
        for module_key, module_label in MODULE_LABELS.items():
            actual = run_case(case_input, module_key, module_label, logger)
            mismatched = any(str(actual.get(field, "")) != row.get(field, "") for field in EXPECTED_FIELDS)
            actual["mismatched"] = mismatched
            module_rows[module_key].append(actual)
            case_modules[module_key] = {
                "mismatched": mismatched,
                "expected_gz_hour": actual.get("expected_gz_hour", ""),
            }
        ui_cases.append(
            {
                "case_id": row["case_id"],
                "category": row.get("category", ""),
                "input_calendar": row.get("input_calendar", ""),
                "gender": row.get("gender", ""),
                "solar": row.get("expected_solar_ymd", ""),
                "lunar": row.get("expected_lunar_ymd", ""),
                "note": row.get("note", ""),
                "modules": case_modules,
            }
        )

    actual_paths = []
    for module_key, rows in module_rows.items():
        path = write_actual_csv(module_key, rows)
        actual_paths.append(path)
        logger.info("actual 결과 저장: %s (%s rows)", path.name, len(rows))

    stats = summary_from_runs({e["input"].case_id: e["input"] for e in case_entries}, MODULE_LABELS, module_rows)
    duration = (datetime.utcnow() - start).total_seconds()
    logger.info("배치 완료: duration=%.2fs mismatches=%s", duration, stats["mismatch"])

    summary_payload = {
        "timestamp": start.isoformat() + "Z",
        "duration_seconds": duration,
        "summary": stats,
        "modules": MODULE_LABELS,
        "cases": ui_cases,
    }

    json_path = DATA_DIR / "batch_results_v2.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(summary_payload, fh, ensure_ascii=False, indent=2)
    logger.info("배치 요약 JSON 생성: %s", json_path.name)

    with DOCS_JSON_PATH.open("w", encoding="utf-8") as fh:
        json.dump(summary_payload, fh, ensure_ascii=False, indent=2)
    logger.info("Docs JSON 동기화: %s", DOCS_JSON_PATH.relative_to(BASE_DIR))

    summary_md = REPORTS_DIR / "batch_summary_v2.md"
    with summary_md.open("w", encoding="utf-8") as fh:
        fh.write("# 50 케이스 배치 실행 요약\n\n")
        fh.write(f"- 시작 시각 (UTC): {start.isoformat()}Z\n")
        fh.write(f"- 소요 시간: {duration:.2f}초\n")
        fh.write(f"- 총 케이스: {len(case_entries)}\n")
        fh.write(f"- 총 mismatch: {stats['mismatch']}\n\n")
        fh.write("## 모듈별 매트릭스\n\n")
        for key, info in stats["module_summary"].items():
            fh.write(f"- {MODULE_LABELS[key]}: 케이스={info['cases']} mismatch={info['mismatch']}\n")
        fh.write("\n## 산출물\n\n")
        for path in actual_paths:
            fh.write(f"- actual 결과 CSV: {path.relative_to(BASE_DIR)}\n")
        fh.write(f"- JSON 요약: {json_path.relative_to(BASE_DIR)}\n")
        fh.write(f"- 로그: {log_path.relative_to(BASE_DIR)}\n")
    logger.info("리포트 마크다운 생성: %s", summary_md.name)


if __name__ == "__main__":
    main()
