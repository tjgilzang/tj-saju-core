#!/usr/bin/env python3
import json
import os
import sys
import time
import traceback
import urllib.parse
import uuid

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.core_logic import CaseInput, build_expected_payload

HEADERS = [
    'Content-Type: application/json',
    'Cache-Control: no-store',
    'Pragma: no-cache',
    'Access-Control-Allow-Origin: *',
]


def respond(payload, status=200):
    print(f"Status: {status} OK")
    for value in HEADERS:
        print(value)
    print()
    print(json.dumps(payload, ensure_ascii=False))


def parse_int(value, name, minimum=None, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}은(는) 유효한 숫자가 아닙니다.")
    if minimum is not None and parsed < minimum:
        raise ValueError(f"{name}은(는) 최소 {minimum}이어야 합니다.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{name}은(는) 최대 {maximum}이어야 합니다.")
    return parsed


def main():
    query = os.environ.get('QUERY_STRING', '')
    params = urllib.parse.parse_qs(query)

    def get(name, default=None):
        values = params.get(name)
        if values:
            return values[-1]
        return default

    try:
        year = parse_int(get('year'), 'year', 1900, 2099)
        month = parse_int(get('month'), 'month', 1, 12)
        day = parse_int(get('day'), 'day', 1, 31)
        hour = parse_int(get('hour'), 'hour', 0, 23)
        minute = parse_int(get('minute'), 'minute', 0, 59)
        calendar = get('calendar', 'solar')
        if calendar not in {'solar', 'lunar'}:
            raise ValueError('calendar 값은 solar 또는 lunar 이어야 합니다.')
        leap = get('leap', '0')
        leap_flag = 1 if leap == '1' else 0
        gender = get('gender', 'M')
        case_id = f"live-{int(time.time())}-{uuid.uuid4().hex[:6]}"

        case = CaseInput(
            case_id=case_id,
            input_calendar=calendar,
            is_leap_month=leap_flag,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            gender=gender,
            legacy_source='live-ui',
            note='saju-input',
            category='interactive',
        )

        expected = build_expected_payload(case)
        payload = {
            'solar': expected['expected_solar_ymd'],
            'lunar': expected['expected_lunar_ymd'],
            'gz_year': expected['expected_gz_year'],
            'gz_month': expected['expected_gz_month'],
            'gz_day': expected['expected_gz_day'],
            'gz_hour': expected['expected_gz_hour'],
            'leap_month': bool(leap_flag) if calendar == 'lunar' else False,
            'message': '계산을 완료했습니다.',
        }
        respond(payload)
    except Exception as exc:  # noqa: BLE002
        traceback.print_exc()
        respond({'error': str(exc)}, status=400)


if __name__ == '__main__':
    main()
