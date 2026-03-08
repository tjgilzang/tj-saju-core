# Core Logic Validation Spec (Priority #1)

## Goal
입력값 `양력/음력 생년월일시`가 들어왔을 때,
1) 음양력 변환
2) 연/월/일/시 간지(사주 4주)
가 레거시와 동일하게 나오는지 검증한다.

## Why first
문구/해석 DB는 이후 단계다. 핵심 로직이 틀리면 전체 결과가 무의미해진다.

## Confirmed logic-related assets
사주백과 데이터 기준:
- `data/EYCONV.db` (+ `Eyconv.px`)
  - 컬럼 시그널: `YEAR_MONTH`, `ADD_DAY`, `1ST_J_*`, `2ND_J_*`
  - 해석: 절기/날짜 보정 + 간지 계산 참조 테이블 가능성 높음
- `data/GanJi_Term.DB` (+ `.MB`, `.PX`)
  - 해석: 간지/절기 경계 테이블 가능성 높음
- `data/Select_Time.db`
  - 시주/시각대 매핑 관련 데이터(시생 텍스트) 포함

## Validation dataset format
파일: `data/validation/core_cases_v1.csv`

필드:
- `case_id`
- `input_calendar` (`solar` | `lunar`)
- `is_leap_month` (`0` | `1`)
- `year`, `month`, `day`, `hour`, `minute`
- `gender`
- `expected_solar_ymd`
- `expected_lunar_ymd`
- `expected_gz_year`
- `expected_gz_month`
- `expected_gz_day`
- `expected_gz_hour`
- `legacy_source` (어느 프로그램/화면 기준인지)
- `note`

## Pass criteria
- P0: `expected_lunar_ymd` 일치율 100%
- P0: `expected_gz_year/month/day/hour` 일치율 100%
- P1: 시/분 경계 케이스(자시, 절기 경계) 100%

## Minimum test pack
- 일반 케이스 20건
- 윤달 케이스 10건
- 자시 경계(23:00/00:00) 10건
- 절기 경계(입춘 근처 등) 10건

## Execution order
1. 레거시 프로그램에서 정답셋 추출 (`core_cases_v1.csv` 채움)
2. 새 엔진 출력 생성 (`actual_core_results_v1.csv`)
3. 비교 스크립트 실행
4. mismatch 원인 분류 (변환/간지/시주)
