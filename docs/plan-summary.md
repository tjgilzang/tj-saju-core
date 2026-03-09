# TJ-SAJU 통합 사주 프로젝트 실행 계획 (2026-03-09)

## 1. 지시서 요약 및 단계 분류 (P0 · P1 매핑)
| 항목 | 핵심 내용 | 현재 단계/분류 |
|---|---|---|
| Task A (P0, 골든 케이스) | 1986-09-02 10:30 KST 양력을 네 프로그램(사주백과·사주나라·라이프운세·사주도사)에서 모두 돌려 연/월/일/시주 결과와 양/음력 변환부터 비교 | 즉시필요 · 우선 실행/검증 (데이터 확보) |
| Task B (P0, 50개 검증) | 일반·윤달·자시/절기 경계 포함 50 케이스 셋 구성, 각 프로그램별 input/expected를 표준화 | 설계·데이터수집 진행 (계획 수립) |
| Task C (P0, 자동 비교) | expected vs actual 자동 비교 체계 구축, mismatch 분류(변환/월/일/시주)하고 mismatch=0까지 반복 | 즉시필요 · 자동화 설계 (스크립트) |
| Task D (P1, 로직 파일 특정) | 라이프운세 MDB 키, 사주백과 EYCONV/GanJi_Term/Select_Time, 사주도사 DB+DOL, 사주나라 ISO 내부 순서 확인 | 데이터 분석·정합성 설계 |
| Firebase 적재 정책 (P1) | 프로그램별 raw 컬렉션(`saju_raw_*`) + 공통 메타 필드(`program_id`, `source_path`, `content_hash`, `schema_version`, `extracted_at`) | 설계/스키마 정리 |
| 보고/완료 Gate | 생성 파일 경로·실행 로그·리스크 필수 기록, 보고 형식(현재공정/진행률/ETA/이슈/증거) 준수 | 운영/표준화 (보고체계 고정) |

## 2. 4개 프로그램 핵심 계산 흐름 및 검증 분해
| 프로그램 | 핵심 계산 흐름 (연주·월주·일주·시주) | 검증 포인트 · 기준 | 다음 액션 (Next action) |
|---|---|---|---|
| 사주백과 | `EYCONV`와 `GanJi_Term` 등의 변환 모듈을 거쳐 입력 생년월일시 → 천간·지지(연·월·일·시) | `Select_Time` 생성 타임스탬프를 기준으로 각 축 비교, 양/음력 변환 결과 일치 여부 체크 | 1986-09-02 10:30 케이스를 실행해 모듈별 출력 상호 비교 (Task A 첫 단계) |
| 사주나라 | ISO 안의 모듈 구조(대부분 바이너리)에서 동일한 입력 → core/driver 결과 확보, canonical 모델과 매핑 | ISO 내부 함수/데이터 패킹에서 추출한 결과와 canonical core(예: 연주/월주/일주/시주 순서) 비교, 절기 경계 처리 확인 | ISO 마운트 후 결과 스트림 수집, 예상되는 pillar 순서 확보 (Task D 전제) |
| 라이프운세 | MDB 기반 키로 생년월일시 조회 → 연/월/일/시주 순환, raw input 파라미터 로그 확보 | MDB 쿼리와 expected canonical (강점: dt 저장 + offset) 정합, 양/음력 변환 일치 확인 | MDB raw 키/인덱스 보고서 정리, 비교 대상 정립 (Task D) |
| 사주도사 | DB + DOL 구조에서 변환/축 생성, 입력 → DOL 출력으로 연월일시 제품화 | DOL 출력(연·월·일·시) ↔ canonical core 비교, DB 입력/출력 흐름 tracedump | DOL 스크립트에 1986-09-02 10:30 입력하고 출력 캡처 (Task D) |

### 2.2 양/음력 변환 비교 검증
- `solar_to_lunar`가 작동해야 하는 기본 양력 입력 20개 (예: 1994-05-21 13:20 서울) vs `lunar_to_solar` 결과 비교.
- 윤달(예: 2008-06-18 음력 윤5월 3일)과 음력 12월 30일 변환 정확도, 양력 경계(입춘 전일/후일) 포함.
- 각 프로그램이 반환하는 `is_leap`/`节气`(절기) 값 일치 여부를 canonical expected와 자동 비교.
- Next action: canonical 변환 모듈(EXPECTED-CORE)을 기준으로 각 프로그램 출력의 `calendar_type`, `leap_month`, `solar_term` 필드를 정렬해 비교.

## 3. 50개 검증 케이스 구상 & 자동 비교 리포트 설계
### 3.1 검증 케이스 구성 (총 50개)
- 일반 케이스 20개: 다양한 연도/월/일/시 (예: 1994-05-21 13:20, 2002-10-07 08:05, 2010-11-11 23:45, 1978-02-03 00:15, 2000-12-01 12:00). 주축은 각 연령대, 오전/오후, 평일/휴일.
- 윤달 케이스 10개: 🈺 음력 윤달 포인트 (예: 2008-06-18 윤5월 3일, 2015-08-16 윤7월 1일, 2020-04-20 윤3월 30일), dawn/납일/자시 포함.
- 자시 경계 10개: 23:30~00:30 자시 범위(예: 1999-01-16 23:55, 1999-01-17 00:05, 2022-06-14 23:45)와 midnight 분리.
- 절기 경계 10개: 입춘·경칩 등 희귀 절기 전후(예: 2026-02-03 03:45 입춘, 2026-02-04 04:10 입춘 직후, 2025-11-07 17:55 대설 전후).
- 케이스 메타: `case_id`, `category`, `input_type`, `tz`, `expected_core`(4주 + leap flag), `priority`.

### 3.2 자동 비교 리포트 프로토콜
**입력 구조 (JSON)**
```
{
  "case_id": "P0-0001",
  "program_id": "sajubaekgwa",
  "input": {
    "datetime": "1986-09-02T10:30:00+09:00",
    "calendar": "solar",
    "location": "Seoul",
    "payload_source": "docs/analysis/ISO_extract"
  },
  "expected": {
    "year_pillar": "丙寅",
    "month_pillar": "庚申",
    "day_pillar": "戊子",
    "hour_pillar": "丙辰",
    "is_leap": false
  }
}
```
**출력 구조 (자동 비교 결과)**
```
{
  "case_id": "P0-0001",
  "program_id": "sajunara",
  "comparisons": [
    {"axis": "연주", "expected": "丙寅", "actual": "丙寅", "match": true, "category": "core"},
    {"axis": "월주", "expected": "庚申", "actual": "庚申", "match": true, "category": "core"},
    {"axis": "일주", "expected": "戊子", "actual": "戊子", "match": true, "category": "core"},
    {"axis": "시주", "expected": "丙辰", "actual": "丙辰", "match": true, "category": "core"},
    {"axis": "cal_type", "expected": "solar", "actual": "solar", "match": true, "category": "conversion"}
  ],
  "mismatch_summary": {
    "total": 0,
    "by_category": {"conversion": 0, "month_boundary": 0, "day_boundary": 0, "hour_boundary": 0}
  },
  "status": "pass",
  "artifacts": {
    "report_path": "outputs/compare/P0-0001_sajunara.json",
    "diff_csv": "outputs/compare/P0-0001_diff.csv"
  }
}
```
**Mismatch 분류**
1. 양/음력 변환 오류 (calendar_type, leap_month)
2. 월주/절기 경계 불일치
3. 일주 기준(절기 기준 vs 정시) 차이
4. 시주 경계(자시, 경시) 누락
**요구 스크립트**: `scripts/compare_core.py` (expected vs actual 입력) → JSON/CSV 리포트 + mismatch 요약 → `scripts/mismatch_analyzer.py` (분류/Severity 산정).
**Next action**: `compare_core.py` 시나리오에 골든 케이스/자시/절기 데이터를 먼저 피드하여 mismatch 문턱을 확인.
**리스크**: 프로그램별 출력 포맷 통일이 안 되면 자동화 비교 파이프라인 지연.

## 4. Firebase raw 데이터 적재 설계 (P1)
| 컬렉션 | 프로그램 | raw payload 핵심 | 공통 메타 필드 + 추가 메타 |
|---|---|---|---|
| `saju_raw_sajubaekgwa` | 사주백과 | `source_text`, `EYCONV_result`, `GanJi_Term`, `Select_Time`, `raw_input_tick` | `program_id`, `source_path`, `content_hash`, `schema_version`, `extracted_at`, `pillar_version`, `leap_flag`, `case_id`, `automation_tag` |
| `saju_raw_sajunara` | 사주나라 | ISO 추출 `driver_output`, `binary_segments`, `runtime_flags`, `calendar_snippet` | 위 메타 + `iso_chunk`, `analysis_version`, `sync_status` |
| `saju_raw_lifeunse` | 라이프운세 | MDB 키/쿼리 로그, `pillars`, `interval_set`, `key_source` | 위 메타 + `mdb_collection`, `query_hash`, `last_synced_at` |
| `saju_raw_sajudosa` | 사주도사 | DB 트랜잭션 로그, `DOL_axis`, `input_checksum` | 위 메타 + `db_table`, `transaction_id`, `dol_build_id` |
각 문서에는 `canonical` 서브필드 (4주 천간·지지, calendar_type, leap_month, solar_term, reference_case_id)와 `comparison_status`(pending/pass/fail, mismatch_categories, last_checked_at)를 같이 저장하여 Firebase에서 직접 mismatch 리포트로 사용할 수 있게 한다.

## 5. 작업별 시간계획표, 산출물, 검증, 스크립트, 다음 액션/리스크
| 작업 | ETA | 산출물 | 검증 방법 | 요구 스크립트 | 다음 액션 (Next action) | 리스크 |
|---|---|---|---|---|---|---|
| A. 골든 케이스 4개 프로그램 실행 (P0) | 120분 | 1986-09-02 10:30 케이스별 결과표, 각 축 비교표, 변환 로그 | canonical expected와 필드별 매칭 → mismatch analyzer (수동+스크립트) | `scripts/capture_golden_case.py` (각 프로그램 입력 자동화 + 결과 추출) | 1) 각 프로그램 실행 환경 정리, 2) 골든 케이스 입력 전송/로그 확보 (Task A 시작) | ISO 마운트/라이브 실행 권한 지연, 입력 포맷 불일치 |
| B. 50개 검증 케이스 매트릭스 (P0) | 180분 | `data/validation_cases.csv` + `docs/case_map.md` (category, expected pillars, special notes) | case metadata vs expected canonical table → 검증 스크립트 사전 검토 | 데이터 생성 스크립트 `scripts/generate_case_set.py` | 일반/윤달/자시/절기별 리스트 정제 후 각 프로그램 자동 테스트에 피드 (next action) | 각 프로그램 기준이 달라 expected 값 조율 시 추가 반복 필요 |
| C. 자동 비교 리포트 프로토콜 (P0) | 150분 | 리포트 스펙 문서, JSON 출력 템플릿, mismatch 분류표 | `scripts/compare_core.py` 실행 → mismatch_summary 0 기록, `scripts/mismatch_analyzer.py` 등 로그 | compare/mismatch 스크립트 + `scripts/auto_report_uploader.sh` | first run: 골든 케이스 + 2~3 boundary 케이스 feed → mismatch categories 확인 (next action) | 출력 포맷 불일치 또는 필드 누락 시 리포트 자동화 실패 |
| D. Firebase raw 적재 설계 (P1) | 120분 | Firebase 컬렉션 설계표, ingestion map, 스키마 문서 (`docs/firebase_raw_schema.md`) | 스키마 검토 + 샘플 JSON을 Firebase에 Dry-run push (mock) | `scripts/firebase_raw_ingest.py` (파이프라인 프로토타입) | 각 컬렉션별 스키마 확정 → `scripts/firebase_raw_ingest.py` 로 더미 문서 삽입 테스트 (next action) | 서비스 키/권한(Firebase admin) 확보 지연, schema 버전 mismatch |

## 6. 보고 형식 요약 (현재 공정/진행률/ETA/이슈/증거 + 다음 액션/리스크)
### 6.1 P0 계산 검증 설계
- 현재 공정: 계산 검증 설계 / 최초 분석
- 진행률: 0/3 핵심 블록, 0%
- ETA: planned 450분 vs actual 450분 (재예측)
- 이슈/블로커: 사주나라 ISO 내부 구조 추출 및 스크립트 안정화 자료 확보 필요
- 증거: projects/tj-saju-master/docs/plan-summary.md
- 다음 액션: Task A로 각 프로그램에 1986-09-02 10:30 양력 케이스를 순차 실행해 출력 확보 (최우선)
- 리스크: ISO 분석/실행 환경에서 예상보다 긴 시간이 소요되어 자동 비교 동기화 지연

### 6.2 Firebase·로직 분석 & P1 준비
- 현재 공정: Firebase raw 설계 + 로직 파일 분석 준비 / 자료 수집
- 진행률: 0/2 핵심 블록, 0%
- ETA: planned 240분 vs actual 240분 (재예측)
- 이슈/블로커: Firebase admin 키(tavis-openclaw-operation...) 만료 여부 확인, ISO/ MDB 경로 파악 필요
- 증거: projects/tj-saju-master/docs/plan-summary.md
- 다음 액션: Task D로 각 프로그램 로직(ISO, MDB, DOL)에서 required output을 추출하고 Firebase 컬렉션 맵 작성
- 리스크: Firebase 권한/ISO 파일 접근 지연 시 raw 적재 스키마 실험 불가

### 6.3 자동 비교 리포트 & 검증 체계
- 현재 공정: 자동 비교 리포트 설계 / 스크립트 정의 단계
- 진행률: 0/2 핵심 블록, 0%
- ETA: planned 150분 vs actual 150분 (재예측)
- 이슈/블로커: 프로그램별 출력 항목을 canonical template에 매핑하는 과정에서 필드 누락 우려
- 증거: projects/tj-saju-master/docs/plan-summary.md
- 다음 액션: scripts/compare_core.py + scripts/mismatch_analyzer.py 로 골든/경계 케이스 자동 비교 실행 → mismatch_summary 확보
- 리스크: 출력 형식/캡슐화되지 않은 데이터로 인해 자동 리포트에서 parsing 오류 발생 가능
