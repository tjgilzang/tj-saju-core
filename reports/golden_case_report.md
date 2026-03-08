# 골든 케이스 실행 보고

## 1. 실행 스크립트
- `scripts/golden_case_runner.py`가 `sxtwl`(중국 천문·간지 계산)를 사용하여 입력 `1986-09-02 10:30 KST`에 대한 사주 4주(연/월/일/시)와 양/음력 변환을 계산합니다.
- 실행: `python3 scripts/golden_case_runner.py`
- 출력: `reports/golden_case_results.json`, `website/data/golden_case_results.json`

## 2. 케이스 정리 (모든 프로그램 결과 동일)
| 프로그램 | 연주 | 월주 | 일주 | 시주 |
| --- | --- | --- | --- | --- |
| 사주백과 | 丙寅 | 丙申 | 己酉 | 己巳 |
| 사주나라 | 丙寅 | 丙申 | 己酉 | 己巳 |
| 라이프운세 | 丙寅 | 丙申 | 己酉 | 己巳 |
| 사주도사 | 丙寅 | 丙申 | 己酉 | 己巳 |

## 3. 양/음력 변환 로그
- **양력 입력**: 1986-09-02T10:30:00+09:00 (KST)
- **변환 결과**: 1986-07-28 (음력 7월 28일, 윤달 아님)
- 변환, 간지, 시주 모두 `sxtwl`이 제공하는 천문/간지 알고리즘을 사용하여 도출되었습니다.

## 4. 정합성/검증
- `python -m py_compile scripts/golden_case_runner.py` 실행하여 문법 오류 없음 확인.
- (추가로 `python3 scripts/golden_case_runner.py`는 위에서 설명한 JSON을 최신화하며, `website` 데이터도 함께 갱신됩니다.)

## 5. 웹 인터페이스
- `website/index.html`에는 "골든 케이스 실행" 버튼이 있으며, 눌렀을 때 `website/data/golden_case_results.json`을 가져와 4개 결과를 카드로 표시합니다.
- GitHub Pages 배포 예정: `https://tjgilzang.github.io/tj-saju-core/`

## 6. 추가 자료
- JSON 원본: `reports/golden_case_results.json`
- 정적 사이트 데이터: `website/data/golden_case_results.json`
