#!/usr/bin/env python3
import csv
import sys

EXPECTED_FIELDS = [
    "expected_solar_ymd",
    "expected_lunar_ymd",
    "expected_gz_year",
    "expected_gz_month",
    "expected_gz_day",
    "expected_gz_hour",
]


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compare_cases(expected_csv, actual_csv):
    exp_rows = load_csv(expected_csv)
    act_rows = load_csv(actual_csv)

    exp_map = {r["case_id"]: r for r in exp_rows}
    act_map = {r["case_id"]: r for r in act_rows}

    missing = sorted(set(exp_map) - set(act_map))
    extra = sorted(set(act_map) - set(exp_map))

    mismatches = []
    checked = 0

    for cid, erow in exp_map.items():
        if cid not in act_map:
            continue
        checked += 1
        arow = act_map[cid]
        for field in EXPECTED_FIELDS:
            e = (erow.get(field) or "").strip()
            a = (arow.get(field) or "").strip()
            if e and e != a:
                mismatches.append({
                    "case_id": cid,
                    "field": field,
                    "expected": e,
                    "actual": a,
                    "legacy_source": erow.get("legacy_source", ""),
                    "note": erow.get("note", ""),
                    "input_calendar": erow.get("input_calendar", ""),
                })

    return {
        "checked": checked,
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "expected_map": exp_map,
        "actual_map": act_map,
    }


def print_summary(summary):
    print(f"checked_cases={summary['checked']}")
    print(f"missing_actual={len(summary['missing'])}")
    print(f"unexpected_actual={len(summary['extra'])}")
    print(f"mismatches={len(summary['mismatches'])}")

    if summary["missing"]:
        print("\n[MISSING ACTUAL]")
        for cid in summary["missing"][:30]:
            print(cid)

    if summary["extra"]:
        print("\n[UNEXPECTED ACTUAL]")
        for cid in summary["extra"][:30]:
            print(cid)

    if summary["mismatches"]:
        print("\n[MISMATCH TOP]")
        for mismatch in summary["mismatches"][:100]:
            print(
                f"{mismatch['case_id']}\t{mismatch['field']}\texpected={mismatch['expected']}\tactual={mismatch['actual']}"
            )


def main():
    if len(sys.argv) != 3:
        print("Usage: compare_core_logic.py <expected_csv> <actual_csv>")
        sys.exit(1)

    summary = compare_cases(sys.argv[1], sys.argv[2])
    print_summary(summary)

    if summary["missing"] or summary["mismatches"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
