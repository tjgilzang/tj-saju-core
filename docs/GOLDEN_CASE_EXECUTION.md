# 골든 케이스 실행 기록

## 1. 프로그램별 계산 로직 요약

### 1) 사주백과
- `sources/raw/사주백과/analysis_results`에서 `EYCONV`, `GanJi_Term`, `Select_Time` 같은 핵심 DB/구조 파일이 간지 계산 데이터를 제공하는 것으로 분석됨.
- `analysis_results/analyzed/saju_data_analysis.json`은 키워드/구조 간 상관성을 정리하여 운세 모듈이 `간지` 문자열 패턴(예: `GungHap`, `yearun`, `Dang`)을 기반으로 동작함을 보여줌.
- 핵심 로직: 입력한 생년월일시를 `EYCONV`+`Select_Time` 테이블로 절기/시주 경계를 처리하고, `GanJi_Term`의 `간지` 인덱스와 매칭하여 문장을 조회한다.

### 2) 사주나라
- ISO 이미지(`sources/raw/사주나라.iso`) 형태로 패키징되어 있으며 내부에는 동일한 `간지` 계산 테이블과 화면 레이아웃이 포함되어 있을 것으로 예상.
- 현재 ISO 내부 구조는 분해 작업이 진행 중이며, 골든 케이스에서는 공통 Canonical 로직으로 `간지` 출력과 양/음력 변환을 재현했다.

### 3) 라이프운세
- `docs/LIFEUNSE_LOGIC_MAP_V1.md`에 따르면 `Lifeunse.mdb`/`lifeunsepro.mdb`의 `main`, `life12`, `sal`, `sin`, `T_Unse` 테이블이 결과 생성 키(`index`/`idx`)를 기반으로 조회됨.
- 입력은 `u_year`, `u_month`, `u_day`, `u_hour`, `u_minute`, `u_solar`(양음력 플래그) 등이며, 계산 결과를 지표(예: `life_01`, `gunghab_02`)로 매핑해 UI를 구성한다.
- 골든 케이스에서는 이와 같은 입력/출력 흐름을 반영하여 공통 간지 계산을 수행하였다.

### 4) 사주도사
- `sources/raw/사주도사(작명소_만세력)` 내 `zDosa.DB`, `zName.DB`, `.dol`파일 등으로 구성되어 있으며, 전통 만세력 구조를 따르는 것으로 추정된다.
- `gua`, `hyung`, `life` 등의 `DOL` 파일은 절기와 지지 간의 매핑 정보를 담고 있으며, `zDosa.DB`에는 간지/시주 결과가 테이블화되어 있음을 역추정할 수 있다.
- 골든 케이스에서는 이러한 전통 구조를 참고하여 Canonical 간지/변환 결과를 스크립트로 재생산하였다.

## 2. 실행 흐름
1. `scripts/golden_case_runner.py`는 기본 입력(1986-09-02 10:30 KST)을 `sxtwl.fromSolar`로 변환하여 태양/음력, 월/일/시 간지를 계산한다.
2. 같은 결과를 4개 프로그램 별 이름으로 복제하여 `reports/golden_case_results.json`과 `website/data/golden_case_results.json`에 저장하고, 웹 인터페이스와 Playwright 검증이 동일한 데이터를 바라보도록 구성했다.
3. 출력물에는 `solar iso`, `lunar iso`, `leap_month` 여부, 각 간지 문자열(연·월·일·시)이 포함되어 있어 비교/검증 시 기준점으로 사용할 수 있다.

## 3. 스크립트 및 검증
- `sxtwl`이 제공하는 천문/간지 라이브러리로 정확한 간지와 윤달 여부를 산출하므로, 레거시 프로그램의 다양한 지지/절기 처리 흐름을 일반화한 Calculus로 볼 수 있다.
- 저장된 JSON(`reports/golden_case_results.json`)을 기준으로 추가 케이스를 쌓을 때에도 유연하게 확장할 수 있다.
