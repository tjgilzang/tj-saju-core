# Firebase Ingestion 파이프라인 설계

## 개요
- 프로그램별 raw 데이터를 `Firebase Firestore`에 분리 저장하여 후속 Canonical 모델링/코어 검증에 활용
- 컬렉션: `saju_raw_lifeunse`, `saju_raw_sajubaekgwa`, `saju_raw_sajudosa`, `saju_raw_sajunara`
- 각 문서에는 원본 파일/아카이브에 대한 메타(metadata)와 추출 정보(추출 시각, 해시)를 담아 신뢰성 확보
- 요약/모니터링을 위한 UI(`ui/index.html`)와 Playwright 기반 확인 흐름 포함

## 컬렉션/문서 스키마
공통 메타 필드
| 필드 | 설명 |
| --- | --- |
| `program_id` | 프로그램 식별자 (`lifeunse`, `sajubaekgwa`, `sajudosa`, `sajunara`) |
| `source_path` | 프로젝트 루트 대비 상대 경로 (`sources/raw/...`) |
| `content_hash` | SHA256 (hex) |
| `schema_version` | 프로그램별 schema version (docs 인벤토리에서 관리) |
| `extracted_at` | 원본 파일의 최종 수정 시각 (UTC iso) |
| `payload_summary` | 파일 이름/크기/추정 MIME/텍스트 프리뷰 |
| `ingested_at` | Firestore에 실제 적재된 시각 (UTC iso) |

문서 키: `{program_id}_{content_hash[:24]}` 방식으로 중복 방지 및 추적 용이

### schema_version 매핑
| program_id | collection | schema_version |
| --- | --- | --- |
| `lifeunse` | `saju_raw_lifeunse` | `1.0.0` |
| `sajubaekgwa` | `saju_raw_sajubaekgwa` | `1.0.1` |
| `sajudosa` | `saju_raw_sajudosa` | `0.9.0` |
| `sajunara` | `saju_raw_sajunara` | `0.1.0` |

샘플 문서: `samples/` 폴더에 각 컬렉션 구조를 JSON으로 기록
- `samples/saju_raw_lifeunse_sample.json` 등

## 실행 흐름
1. 필요한 패키지 설치
```bash
cd /Users/tj/.openclaw/workspace/agents/architect/projects/tj-saju-master
python -m pip install -r requirements.txt
```

2. Firebase 인증 설정
```bash
export FIREBASE_SERVICE_ACCOUNT=/path/to/service-account.json
export FIREBASE_PROJECT_ID=your-project-id
```
`FIREBASE_SERVICE_ACCOUNT`에 실제 서비스 계정 키 경로를, `FIREBASE_PROJECT_ID`에 Firestore 프로젝트명을 지정

3. 적재 실행
```bash
python scripts/firebase_ingest.py [--program lifeunse|sajubaekgwa|sajudosa|sajunara] [--limit N]
```
- `--program`으로 처리할 프로그램 ID를 지정하면 해당 프로그램만 적재합니다 (기본값: 모든 프로그램)
- `--limit`은 프로그램당 처리할 최대 파일 개수를 제한하여 QA/샘플 적재를 빠르게 수행할 수 있습니다
- 인증 정보가 없으면 자동으로 dry run 모드로 동작
- `--dry-run`을 추가하면 실제 Firestore 쓰기 없이 로그와 요약만 생성됩니다
- 운영 예시: `python3 scripts/firebase_ingest.py --program sajubaekgwa --limit 50`

4. 결과/로그
- 로그: `logs/firestore_ingestion.log`
- 요약 JSON: `reports/firestore_ingestion_summary.json`
- UI에서 요약을 실시간으로 읽고 보여줌

## 로그/재시도 정책
- 실패 시 최대 3회 재시도 후 실패 처리
- 실패 메시지/스택추적은 `logs/firestore_ingestion.log`와 요약의 `errors` 필드에 기록
- dry run에도 `success_count`와 `failure_count`를 업데이트하여 UI/Playwright에서 확인 가능

## UI/모니터링
- `ui/index.html`에서 `reports/firestore_ingestion_summary.json`을 fetch하여
  - 전체 성공/실패 수
  - 프로그램별 문서 처리 수
  - 마지막 생성 시각 표시
- Playwright `tests/playwright/firestore_status.spec.js`가 UI를 열고
  1. 상태 섹션(`Firebase 적재 상태`)이 보이는지 검증
  2. 성공/실패 카운트를 포함한 문구를 확인
  3. 스크린샷(`reports/playwright/firestore_status.png`) 및 트레이스(`reports/playwright/firestore_status_trace.zip`) 저장

## Playwright 실행 (E2E)
```bash
# 로컬 서버 실행
python -m http.server 8000 &
# playwright 설치/실행 (node_modules 설치가 필요함)
npm run test:playwright
```
- 테스트는 `ui/index.html`로 이동한 뒤 상태 카드가 최신 summary JSON을 보여주는지 확인
- `reports/playwright/firestore_status.log`에 브라우저 콘솔 로그 캡처

## 샘플 문서 구조
- `samples/saju_raw_lifeunse_sample.json` 참고
- `payload_summary.content_preview`는 텍스트 파일인 경우 선행 1KB를 기록하여 파싱 진행 상황 추적

## 배포 고려 사항
- GitHub Pages에서 `index.html`이 루트에 노출되므로 `reports/firestore_ingestion_summary.json`, `samples/` 등 정적 자원을 함께 커밋
- `ui/index.html`은 Firebase 적재 현황을 팀/QA가 빠르게 확인하는 대시보드 역할
