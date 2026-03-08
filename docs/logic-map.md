# 로직 맵

**작성일: 2026-03-08**

## 1. 목적 및 배경
- 4개 레거시 프로그램(사주백과, 사주나라, 라이프운세, 사주도사)의 계산 파이프라인을 동일한 프레임으로 정량화하여 입력/출력 흐름을 빠르게 비교할 수 있도록 한다.
- 기존 분석 결과(`docs/SUPERVISOR_WORK_ORDER_2026-03-08.md`, `docs/CORE_LOGIC_VALIDATION_SPEC.md`)를 바탕으로 핵심 로직 파일과 데이터 구조를 체크리스트화하고, GitHub Pages에서 `로직 맵` 페이지로 실시간 공유하며 QA 이력을 남긴다.

## 2. 핵심 로직 파일 체크리스트
### 1) 사주백과
- `sources/raw/사주백과/data/EYCONV.db`
  - `analysis_results/EYCONV_structure.json`의 `text_sample`에 `ID YEAR_MONTH ADD_DAY 1ST_J_* 2ND_J_*` 컬럼이 포함되어 있어, `연/월/일` 입력을 기준으로 두 차례(1st/2nd) 간지 후보를 뽑는 보정 테이블로 추정된다. 절기경계나 윤달 보정용 `ADD_DAY` 속성을 통해 음/양력 전환을 보조하며, 출력은 이후 `GanJi_Term` 조회의 키로 쓰인다.
- `sources/raw/사주백과/data/GanJi_Term.DB` (동일 경로에 `.MB`, `.PX` 부속)
  - `reports/data_files.txt`에도 등장하며, `GanJi`(간지) 표준화 데이터셋으로 보인다. `EYCONV`가 생성한 `YEAR_MONTH + ADD_DAY`와 `1ST/2ND_J_*`를 키로 삼아 `gz_year/month/day/hour` 문자열을 제공한다.
- `sources/raw/사주백과/data/Select_Time.db`
  - `analysis_results/Select_Time_strings.json`(cp949)에서 `해시생`, `모선망`, `잠버릇` 등 시생(時生) 텍스트가 노출되어 있고, `IDX`, `Title`, `Data`, `korea` 칼럼을 포함한다. 시주(`hour`)를 기준으로 해당 텍스트 블록을 렌더링하기 위한 시간별 메시지 저장소로 해석된다.

### 2) 라이프운세
- `sources/raw/라이프운세/LifeUnse/lifeunse.mdb` (추출 결과 `extract/lifeunse/mdb/lifeunse/tables/`에 CSV 존재)
  - `main.csv` 1행에서 `Txt`, `index`, `idx` 형태로 구성되어 있으며, 계산기에서는 `index`/`idx`라는 두 축을 기준으로 문구 DB를 조회한 뒤 `Txt`를 그대로 보여준다.
  - `life12.csv`는 `Year12`, `Month12`, `idx` 조합으로 `월/년` 스코프를 나누며 `life12Title`은 제목을, `btype_couple`, `dream`, `sal`, `sin`, `gilbog`, `fourbody` 등은 텍스트 파편을 추가한다. 인풋(生肖, 性別, 시/분 경계)에 따라 `index`/`idx`를 조합하는 것으로 파이프라인을 유추할 수 있다.
- `sources/raw/라이프운세/LifeUnsePro` 및 `_projectuyuk` 등은 프로 버전 대응 데이터로, `lifeunsepro.mdb`/`lifeunseprojuyuk.mdb`에도 동일한 테이블 구조가 존재한다. `Lifeunsepromemo`와 `Lifeunseprouser`는 메모/사용자 확장판.
- `extract/lifeunse/mdb/index.tsv`는 추출된 MDB의 테이블 목록을 기술(총 7개 파일, 24개 테이블). 이 인벤토리를 통해 `main`→`life12`→`life12Title` 등으로 이어지는 입력/출력 흐름을 확인했다.

### 3) 사주도사
- `sources/raw/사주도사(작명소_만세력)/zDosa.DB` 및 `zName.DB`
  - `samples/saju_raw_sajudosa_sample.json`에서는 `file_size`와 `content_hash`가 기록되어 있으며, `zDosa`는 사주기반 운세·작명 엔진, `zName`은 이름 추천용 DB로 추정된다.
- `.dol` 확장자(예: `life.dol`, `dream1.dol`, `hyung.dol`, `osix.dol`, `tojung.dol` 등 14개 이상)가 수록되어 있으며, 각 파일은 운세 문구 영역을 나누어 담고 있다. 예를 들어 `dream*.dol`은 꿈해몽, `life.dol`은 인생사, `osix.dol`은 오행 관련 텍스트로 보인다.
- `dosa.cfg`는 실행 옵션을 담은 이진 설정 파일로, `zDosa.exe`/`zName.exe`가 이 구성을 로딩하여 `.DB`와 `.dol`을 조합한 렌더링을 수행하는 것으로 유추된다. `hangul*.fnt`는 한글 폰트, `dosa.cfg`는 로직 매핑 포인트를 정의.

### 4) 사주나라
- `sources/raw/사주나라.iso` 단일 ISO 이미지만 확보되어 있고, 아직 마운트/추출이 되어 있지 않다(`docs/EXECUTION_ROADMAP.md`, `docs/SUPERVISOR_WORK_ORDER_2026-03-08.md` 참조).
- ISO 내부 구조를 파악해 `적절한 DB`, `간지 파일`, `config` 등을 찾아내는 것이 다음 단계이며, 현재로선 `입력→출력` 흐름은 외부 문서에 의존하여 추정만 가능한 상태이다.

## 3. 프로그램별 입력/출력 흐름
### 사주백과
1. **입력**: 양/음력 선택 + `year`, `month`, `day`, `hour`, `minute`, `gender`, `timezone`.
2. **EYCONV**(`YEAR_MONTH`, `ADD_DAY`, `1ST_J_*`, `2ND_J_*`)를 통해 절기 보정 및 일자/시간 `간지` 후보를 생성한다.
3. **GanJi_Term**은 예비 인덱스를 받아 `gz_year/month/day/hour`를 확정한다. `reports/data_files.txt`에 `.MB`, `.PX`도 존재하여 다국어/폰트 보정을 함께 처리하는 구조로 추정.
4. **Select_Time**는 `hour` 기준 `IDX`를 뽑아 `korea` 컬럼에 담긴 시생 텍스트(예: `해시생`, `모선망`, `잠버릇`)를 노출한다.
5. **출력**: 연주/월주/일주/시주 + 시생·절기 안내. `Select_Time` 텍스트는 UI 텍스트 템플릿, `GanJi_Term`은 숫자/간지 문자열.

### 라이프운세
1. **입력**: 사주(생년월일시) + 성별 + 궁합/운세 종류.
2. **`lifeunse.mdb`의 `main` 테이블**은 `index`/`idx` 조합으로 텍스트 블록을 찾고, `life12`/`life12Title` 등으로 보조 텍스트(월/년 스코프)를 더한다.
3. **보조 테이블**(`btype_couple`, `dream`, `sal`, `sin`, `gilbog`, `fourbody`)은 `index`가 세부 주제에 대응하며, 각 테이블은 `Txt` 열에 한글 문장을 갖는다.
4. **출력**: `main`에서 가져온 문장들 + `life12` `Year12/Month12`에 맞춘 제목 + `btype`/`dream`으로 분기된 부가 문장.
5. **프로 버전**(`lifeunsepro`, `lifeunseprojuyuk`)도 동일한 테이블 명으로 구조를 복제하고 있으며, UI에서는 `프로`/`기본` 스키마만 달라질 뿐 동일 파이프라인이다.

### 사주도사
1. **입력**: 사주 정보 + 작명/운세 구분.
2. **`zDosa.DB`**는 사주를 기반으로 `형`, `성`, `오행` 등 인덱스를 뽑고, 이 인덱스를 `*.dol` 파일에 매핑하여 텍스트를 생성한다.
3. **`zName.DB`**는 작명 케이스(예: 자수성, 항렬)를 `DOL` 이름/자음/운수로 다시 조합한다.
4. **`.dol` 파일들**은 `dream*`, `life`, `hyung`, `osix`, `tojung`, `luck` 등 영역별로 배치되어 있으며, `dosa.cfg`/`hangul*.fnt`를 통해 어떤 폰트/정렬로 출력할지도 제어된다.
5. **출력**: 사주/작명 텍스트(운세, 꿈해몽, 이름의 오행) + 선택한 `DOL` 섹션.

### 사주나라
- 현재 ISO만 확보되어 있어 입력/출력 파이프라인을 직접적으로 분석하지 못했다. 다음 단계는 ISO 마운트 → 내부 `*.DB`/`*.EXE`를 추출하여 `간지/시생` 등 필수 파일을 확보하는 것이다(`docs/EXECUTION_ROADMAP.md` 참조).

### 입력↔출력 비교 테이블
| 프로그램 | 입력 | 중심 파이프라인 | 출력 | 참조 자료 |
| --- | --- | --- | --- | --- |
| 사주백과 | `양/음력`, 생년월일시, 성별, timezone | `EYCONV` → `GanJi_Term` → `Select_Time` | 연/월/일/시 간지 + 시생 텍스트 | `sources/raw/사주백과/data/*.db`, `analysis_results/*.json` |
| 라이프운세 | 사주 데이터 + 궁합/운세 선택 | `main(index, idx)` → `life12/life12Title` → `dream/sal/sin` 텍스트 | 케이스별 문장 블럭 | `extract/lifeunse/mdb/*/tables/*.csv` |
| 사주도사 | 사주 + 작명 옵션 | `zDosa.DB`, `zName.DB` → `.dol` 문자 섹션 | 작명/운세 텍스트 | `samples/saju_raw_sajudosa_sample.json`, `.dol` 목록 |
| 사주나라 | (미확인) | ISO 내부 분석 예정 | (미확인) | `sources/raw/사주나라.iso` |

## 4. 통합 프레임 (Canonical)
| 단계 | Canonical 필드 | 설명 | 사주백과 매핑 | 라이프운세 매핑 | 사주도사 매핑 | 사주나라 계획 |
| --- | --- | --- | --- | --- | --- | --- |
| 입력 | `calendar_type`, `is_leap_month`, `year`, `month`, `day`, `hour`, `minute`, `timezone`, `gender` | `CORE_LOGIC_VALIDATION_SPEC.md`에 정의된 공통 입력 | UI 내부 입력 | MDB의 `index` 파생 기준 | `zDosa` 풀에서 파생 | ISO 내부 입력 파일 확보 후 매핑
| 중간 | `solar_ymd`, `lunar_ymd`, `절기`, `ganji_index`, `hour_index` | 입력을 canonical 형태로 정규화 | `EYCONV`/`GanJi_Term` | `life12`/`dream` 인덱스 | `dosa.cfg` 기준 인덱스 | 추출 파일로 확인 예정
| 출력 | `gz_year`, `gz_month`, `gz_day`, `gz_hour`, `시생`, `문구블럭(index+idx)` | 정규화된 간지 + 문구 참조 | `GanJi_Term` + `Select_Time` | `main.Txt` + `btype`/`dream` | `.dol` + `zName` | 준비 중

## 5. QA 리뷰 로그
| 항목 | 검토 내용 | 결과 | 증거 |
| --- | --- | --- | --- |
| 문서 정합성 | `analysis_results/EYCONV_structure.json`의 컬럼 + `extract/lifeunse/mdb` CSV 예시로 흐름 검증 | 입력/출력 테이블의 항목이 실제 파일 이름과 대응됨 | 본 문서 2~3절 각주 및 경로 설명 |
| 웹 가시성 | `logic-map.html` 페이지에 핵심 섹션(`로직 맵`, `통합 프레임`, `QA 리뷰 로그`) 존재 확인 | Playwright E2E & 스크린샷 확보 예정 | `reports/playwright/logic_map.png`, `logic_map_trace.zip` |

## 6. 배포 링크 (추후 누적)
- GitHub 저장소: `https://github.com/tjgilzang/tj-saju-core`
- GitHub Pages: `https://tjgilzang.github.io/tj-saju-core/logic-map.html`
