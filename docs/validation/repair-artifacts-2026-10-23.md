# 실제 파일 기반 before/after 검사 — 2026-10-23

## 실행과 범위

`tests/fixtures/repair-lift/`의 포스터 SVG, 한영 본문 SVG, 인쇄 PDF는 이번 평가를 위해 직접 만든 작은 원본이다. 기존 사용자 작품·비공개 파일·폰트 바이너리를 포함하지 않는다. SVG의 실제 소스 텍스트와 PDF 페이지 크기를 검사한다. 이미지를 보고 서체·심미·가독성을 검증한 결과가 아니다.

| 과제 | 명시적 제작 조건·피드백 | 수정 | 실제 before → after |
| --- | --- | --- | --- |
| poster | 브리프의 행사 날짜는 `2026-10-23`; 존재하지 않는 날짜를 정확한 원고로 교체 | 날짜만 교체 | `2026-10-32` FAIL → `2026-10-23` PASS |
| mixed-body | 이 fixture의 승인 원고는 `용지 Paper: 35 mm` | 원고에 맞춰 공백 추가 | FAIL → PASS |
| print-output | 계약 판형은 정확히 320 × 420 pt | 300 × 420 pt의 페이지를 320 × 420 pt로 변경 | FAIL → PASS |
| negative-repair | mixed-body와 같은 원고 조건 | 서체 크기 18 → 20만 변경 | FAIL → FAIL, 원래 목표 미해결 |

SI 표기 조건은 이 과제의 명시적 원고 계약이며 모든 제품명·매체에 강제하는 보편 규칙이 아니다. PDF 판형 성공도 폰트 포함·PDF/X·색·물리 인쇄 성공을 뜻하지 않는다. PDF를 Poppler로 렌더해 파일 열림과 내용 표시를 확인했다. 렌더 과정은 Symbol/ArialUnicode display font 경고를 냈으므로 폰트 충실성의 증거로 쓰지 않는다.

## 재현

```sh
# 이미 커밋된 SVG/PDF의 독립 실행 검사: Python 표준 라이브러리 + pdfinfo
python tests/check_repair_artifacts.py
python -m unittest discover -s tests -p 'test_repair_lift_summary.py' -v
# 선택적 fixture 재생성에만 기존 reportlab 필요; 검사를 위해 설치할 필요 없음
python tests/check_repair_artifacts.py --generate
# 명시한 경우에만 새 실행 리포트 저장; 기본 검사는 기존 기록 불변
python tests/check_repair_artifacts.py --output path/to/new-report.json
```

실행 환경: Windows, Python 3.12.14, Poppler pdfinfo 26.07.0. 실제 Python 버전·파일 SHA-256·검사 출력·집계 결과는 [JSON 실행 기록](repair-artifacts-2026-10-23.json)에 남겼다. 원본/수정본 8개 파일의 해시는 모두 다르며, 동일 checker/동일 과제 조건으로 전후를 검사했다. fixture 재생성은 ReportLab invariant 모드를 사용한다.

검사 결과: 세 과제의 명시적 기술 조건 수정, 한 과제의 미해결 반례. 기존 reporter 단위 시험 12/12 통과. reporter의 `verified_counts=null` 및 `independent_verification=UNVERIFIED`는 그대로다. 독립 파일 검사를 실행했다는 사실이 reporter의 선언값을 인증하는 어댑터를 구현했다는 의미는 아니다.

## 남은 완료 조건

- 이 과제의 피드백은 평가 작성자가 통제한 예시다. **실제 baseline feedback 대 skill feedback 실험을 하지 않았다.**
- 같은 수정자·동일 시간 예산의 독립 실험과 비용 측정은 미실행이다. 실제 경과를 측정하지 않아 비용 숫자를 만들지 않는다.
- 독립 전문가의 블라인드 A/B·순서 교환·의도 보존·불일치/부작용 평가는 미실행이다. `BLOCKED`는 평가 참여자 부재를 뜻하며 실패한 모델 호출을 뜻하지 않는다.
- 실제 한영 shaping·font fallback·가독성, 실제 인쇄는 `UNVERIFIED`다. 실제 파일이 생겼다는 이유로 #13 완료나 Draft 해제를 선언하지 않는다.