# LifeUnse Logic Map v1

Date: 2026-03-08
Scope: `라이프운세` 로컬 추출본 기반 로직 추정

## 1) 확인된 입력 데이터 (User Profile)
Source:
- `extract/lifeunse/mdb/Lifeunseprouser/tables/data.csv`
- `extract/lifeunse/mdb/Lifeunseuser2/tables/data.csv`

Key fields:
- `u_year`, `u_month`, `u_day`, `u_hour`, `u_minute`
- `u_sex`
- `u_solar` (양력/음력 플래그)
- `u_name`, `u_namehanja`
- `u_eight` (팔자/간지 관련 캐시 추정)

## 2) 확인된 결과 DB 테이블 (콘텐츠 사전)
Source:
- `extract/lifeunse/mdb/lifeunse/tables/*.csv`
- `extract/lifeunse/mdb/lifeunseprojuyuk/tables/T_Unse.csv`

Main dictionary tables:
- `main` (1273 rows): 핵심 결과 문구
- `life12` (144 rows): `Year12`, `Month12` 기반 매핑
- `life12Title` (12 rows): 띠/연도 축 제목성 매핑
- `sal`, `sin`, `gilbog`, `fourbody`, `btype_couple`, `dream`
- `T_Unse` (614 rows): 상황별 종합운 문구 세트

## 3) 핵심 키 패턴
`main.index`는 사실상 “로직 모듈 키”로 보임.

대표 prefix 분포:
- `life_01` (180)
- `gunghab_02` (144)
- `year_01` (144)
- `name_01` (125)
- `name_02` (81)
- `today_01` (64)
- `today_02` (64)
- `astrology1` (63)
- `dream` (54)
- `dangsaju_05` (48)
- `dangsaju_06` (36)
- `gunghab_01` (25)

해석:
- 실행 로직은 계산식 자체를 DB에 두기보다, 계산 결과로 “키(index/idx)”를 만든 뒤 문구 DB를 조회하는 구조.

## 4) 조인/조회 추정 규칙 (v1)
1. 사용자 입력(생년월일시/성별/양음력) 수집
2. 내부 계산기로 간지/띠/월지/일주/궁합 코드 생성
3. 생성된 코드로 `main.index` 또는 `idx` 조회
4. 보조 테이블(`life12`, `sal`, `sin`, `T_Unse`) 결합
5. 화면 리포트 조립

## 5) 확정 사실
- `lifeunse.mdb`와 `lifeunsepro.mdb` 테이블 CSV는 동일 해시(사전 데이터 동일).
- `pro`는 추가로 사용자/메모 DB(`Lifeunseprouser`, `Lifeunsepromemo`)를 분리 보유.
- 따라서 코어 운세 로직 사전은 공통 DB, 사용자 기능만 Pro 확장 구조.

## 6) 미확정(다음 단계 필요)
- 코드 생성식(예: `gunghab_02_자신`를 만드는 계산 규칙)
- `idx` 생성 로직(정수/문자 혼합 키의 정확한 매핑)
- 시간 입력(`u_hour`, `u_minute`)이 어떤 모듈에 반영되는지

## 7) 다음 작업 (실행 순서)
1. `main.index` 전체 키 사전 추출 + 모듈별 명세 JSON 생성
2. 사용자 샘플 20건 시뮬레이션으로 키 생성 역추정
3. 역추정 성공 규칙을 `normalized/lifeunse/logic_rules_v1.json`으로 고정
4. 이후 Firebase에 `program=lifeunse` 원본/정규화 컬렉션 적재
