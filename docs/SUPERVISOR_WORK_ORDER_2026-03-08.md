# TJ Saju Legacy Integration - Supervisor Work Order

작성일: 2026-03-08  
프로젝트 루트: `/Users/tj/.openclaw/workspace/agents/architect/projects/tj-saju-master`

---

## 0) 목적 (최우선 원칙)

이 프로젝트의 1순위는 **사주 코어 로직 검증**이다.

- 대상 로직: `양력/음력 생년월일시 입력 -> 사주 4주(연주/월주/일주/시주) 산출`
- 이유: 해석 문구 품질보다 먼저, 계산 코어가 맞아야 전체 결과 신뢰 가능
- 운영 원칙: 프로그램별 분해 -> 로컬 검증 -> 프로그램별 DB화(Firebase) -> 통합 정합성 검증 -> 앱 반영

---

## 1) 현재 자산/현황 요약

### 1-1. 프로그램 세트 (4개)

1. 사주백과
2. 사주나라 (ISO)
3. 라이프운세
4. 사주도사(작명소/만세력)

참조: `docs/PROGRAM_INVENTORY.md`

### 1-2. 현재 완료 상태

- 장기 프로젝트 디렉토리 구성 완료
- 라이프운세 MDB 추출 완료
  - 추출 결과: `mdb_files=7, tables=24, rows=57717`
  - 참조: `extract/lifeunse/mdb/index.tsv`, `extract/lifeunse/mdb/summary.txt`
- 라이프운세 로직 맵 v1 작성
  - 참조: `docs/LIFEUNSE_LOGIC_MAP_V1.md`
- 코어 로직 검증 스펙/비교 스크립트 작성
  - `docs/CORE_LOGIC_VALIDATION_SPEC.md`
  - `data/validation/core_cases_v1.csv`
  - `scripts/compare_core_logic.py`

### 1-3. 핵심 관찰

- 라이프운세는 계산 결과 키(index/idx)로 문구 DB를 조회하는 구조로 보임
- `lifeunse.mdb`와 `lifeunsepro.mdb`는 코어 사전 데이터 동일 (pro는 사용자/메모 확장)
- 사주백과 데이터에 코어 계산 관련 후보 파일 존재:
  - `data/EYCONV.db` (+ Eyconv.px)
  - `data/GanJi_Term.DB` (+ .MB, .PX)
  - `data/Select_Time.db` (+ .MB)

---

## 2) Supervisor 역할 고정 (실행 원칙)

Supervisor는 아래 4가지만 수행:

1. Classify: 요청 분류 (domain/task/priority)
2. Route: 적절한 봇으로 위임
3. Gate: 증거 기반 완료 판정
4. Report: 표준 형식으로 사용자 보고

금지:
- 직접 구현/직접 테스트 수행 금지 (필요 시 coder/qa/deploy 위임)

---

## 3) 워크스트림 (프로그램 전체 기준)

### WS-A. 코어 로직 검증 (P0, 가장 먼저)

목표:
- 양/음력 입력 및 사주 4주 계산식의 정합성 100%

세부 단계:

1. 골든 케이스 정의
- `1986-09-02 10:30 (양력, KST)`를 케이스 #1로 고정
- 윤달/자시/절기경계 포함 40~50케이스 확장
- 파일: `data/validation/core_cases_v1.csv`

2. 레거시 정답셋 확보
- 각 프로그램에서 동일 입력으로 출력되는 연/월/일/시 간지 수집
- `expected_*` 필드 채움
- `legacy_source` 필수 기록

3. 신규 엔진 계산 결과 생성
- `actual_core_results_v1.csv` 생성 (필드 스키마는 expected와 동일)

4. 자동 비교
- 커맨드:
  - `python3 scripts/compare_core_logic.py data/validation/core_cases_v1.csv data/validation/actual_core_results_v1.csv`

5. mismatch 분류
- 유형 A: 양음력 변환 오류
- 유형 B: 절기 경계/월주 오류
- 유형 C: 일주/시주 계산 오류
- 유형 D: 시간 해석(자시/시각 경계) 오류

완료 조건 (DoD):
- 케이스 전체 mismatch 0
- 윤달/절기/자시 경계 그룹 각각 100% 일치

---

### WS-B. 프로그램별 데이터 추출/보존 (P1)

목표:
- 각 프로그램 원본을 손상 없이 추출하고 재현 가능한 상태로 관리

대상:
- 라이프운세: MDB 추출 완료, 다음은 semantic mapping
- 사주백과: DB/MB/PX 구조 파서 전략 필요
- 사주도사: DB + DOL 구조 확인 필요
- 사주나라: ISO 내부 포맷 해석/추출 필요

표준 산출물:
- `extract/<program_id>/...`
- `reports/<program_id>_*`
- checksum 파일

완료 조건:
- 프로그램별 데이터 구조 인벤토리 문서 존재
- 최소 1개 핵심 테이블/파일의 필드 의미 문서화

---

### WS-C. 프로그램별 Firebase 적재 (P1)

목표:
- 프로그램별 raw 데이터를 분리 저장하여 추후 통합 비교 기반 확보

저장 전략:
- 컬렉션 예시:
  - `saju_raw_lifeunse`
  - `saju_raw_sajubaekgwa`
  - `saju_raw_sajudosa`
  - `saju_raw_sajunara`
- 문서 키: `{program}_{table_or_file}_{hash}`
- 메타 필드:
  - `program_id`
  - `source_path`
  - `extract_time`
  - `schema_version`
  - `content_hash`

주의:
- 글로벌/도메인 메모리 오염 금지
- 프로그램 간 cross-write 금지

완료 조건:
- 프로그램별 최소 1회 raw 적재 성공
- 적재 로그 및 문서 카운트 보고

---

### WS-D. 통합 정합성 계층 설계 (P2)

목표:
- 서로 다른 레거시 프로그램을 공통 Canonical 모델로 매핑

초기 Canonical 스키마:
- 입력: calendar_type, is_leap_month, y,m,d,h,min,timezone
- 계산결과: gz_year, gz_month, gz_day, gz_hour
- 중간값: solar_ymd, lunar_ymd, 절기 인덱스, 시주 인덱스
- 출처: source_program, source_key

완료 조건:
- `normalized/` 하위에 canonical 매핑 문서 1차본
- 4개 프로그램 중 최소 2개와 필드 매핑 완료

---

## 4) 즉시 실행 태스크 (오늘~내일)

### Task 1 (P0): 골든 케이스 확장

담당: survey + architect  
산출물:
- `data/validation/core_cases_v1.csv` 40~50 케이스
- 그룹 구성: 일반/윤달/자시/절기경계

ETA: 90분

### Task 2 (P0): 레거시 정답값 채우기

담당: coder + qa  
산출물:
- 케이스별 `expected_gz_*` 입력 완료
- 근거 캡처/로그 경로 기록

ETA: 3~4시간

### Task 3 (P0): 자동 비교 리포트

담당: qa  
산출물:
- 비교 결과 요약 (`mismatch 0` 목표)
- mismatch 유형별 분류표

ETA: 40분

### Task 4 (P1): 사주백과 코어 파일 구조해석

담당: survey + architect  
대상:
- `EYCONV`, `GanJi_Term`, `Select_Time`

산출물:
- 필드 사전 v1 (`docs/`)
- 계산 흐름도 v1

ETA: 2~3시간

---

## 5) 실행 커맨드 레퍼런스

프로젝트 루트 이동:
- `cd /Users/tj/.openclaw/workspace/agents/architect/projects/tj-saju-master`

라이프운세 MDB 재추출:
- `scripts/extract_mdb_program.sh lifeunse '/Users/tj/.openclaw/workspace/agents/architect/projects/tj-saju-master/sources/raw/라이프운세'`

코어 로직 비교:
- `python3 scripts/compare_core_logic.py data/validation/core_cases_v1.csv data/validation/actual_core_results_v1.csv`

---

## 6) 보고 포맷 (Supervisor -> 사용자)

아래 형식 강제:

1. 현재 공정
- 예: `WS-A / Step 2 / 레거시 정답셋 채우는 중 (케이스 17/50)`

2. 진행률
- `%` + 분모/분자

3. ETA
- planned vs actual
- 예: `남은 시간 65분 (planned 90, elapsed 25)`

4. 이슈/블로커
- 없으면 `none`
- 있으면 해소계획과 시각 명시

5. 증거
- 생성 파일 경로, 로그 경로, 비교 결과 수치

예시:
- `현재 공정: WS-A Step2 (레거시 정답 입력)`
- `진행률: 22/50 (44%)`
- `ETA: 70분`
- `이슈: 사주나라 ISO 포맷 미인식 -> 우선 LifeUnse/사주백과로 진행`
- `증거: data/validation/core_cases_v1.csv, mismatch=3`

---

## 7) Gate 규칙 (강제)

완료 보고를 `done`으로 처리하려면 아래 모두 필요:

1. 산출물 파일 경로
2. 실행 로그/비교 수치
3. 남은 리스크 유무

누락 시:
- 자동 `partial`

---

## 8) 리스크와 대응

리스크 1:
- 사주나라 ISO 포맷 불명으로 마운트 실패

대응:
- 다른 3개 프로그램 로직 검증 선행
- ISO는 별도 바이너리 분석 트랙으로 분리

리스크 2:
- DB/MB/PX 포맷 파서 부재

대응:
- 기존 `analysis_results/*_structure.json` 우선 활용
- 최소 필드사전 확보 후 파서 개발

리스크 3:
- 코어 계산에서 절기 경계 불일치

대응:
- 절기 경계 케이스를 별도 세트로 분리하여 집중 검증

---

## 9) 최종 목표 정의

Phase 1 (검증 완료):
- 양/음력 + 생년월일시 입력 시 사주 4주 결과가 레거시와 일치

Phase 2 (통합 완료):
- 4개 프로그램 데이터가 canonical 모델로 통합

Phase 3 (배포 준비):
- 검증된 계산 엔진 + 통합 데이터 기반 앱 백엔드 완성

---

## 10) 지금 즉시 지시문 (복붙용)

아래를 즉시 실행하라.

1. WS-A(P0)부터 시작한다.  
2. `1986-09-02 10:30 양력`을 케이스 #1로 고정하고, `core_cases_v1.csv`를 50케이스로 확장한다.  
3. 각 레거시 프로그램에서 케이스별 `연주/월주/일주/시주` 정답값을 채운다.  
4. `compare_core_logic.py`로 mismatch를 수치화하고, mismatch 0이 될 때까지 반복한다.  
5. 보고는 매회 `현재 공정/진행률/ETA/이슈/증거` 5항목 형식으로만 보낸다.  
6. 증거 없는 완료 보고는 금지한다.

