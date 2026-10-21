# 아키텍처 라우팅·증거 계약 수동 테스트 초안

> 자동 평가 결과가 아니다. 실제 에이전트가 어떤 파일을 읽고 무슨 근거로 응답했는지
> 도구 로그와 출력으로 판단하며 이전 비평 검증 기록을 변경하지 않는다.

| ID | 입력 | 필수 지식 | 실패 반례 |
| --- | --- | --- | --- |
| R-1 | '이미지 없는 포스터, 비평해줘' | review-protocol, critique-rubric, review-output | 보지 않은 포스터의 결함·정확한 수치 날조; 필요 없는 formula-relations 로딩 |
| R-2 | '스크린샷의 그리드를 수학적으로 해체해줘' | reference-analysis, formula-relations, composition | 픽셀 기반 추정치를 원본 편집 그리드로 확정 |
| R-3 | 'A5 3단 편집물: 여백 12mm/간격 5mm 적용 명세' | formula-relations, design-handoff, editorial-information | 여백값을 AI가 미적으로 최적이라고 주장; 38mm 계산 오류 |
| R-4 | '텍스트 없는 디지털 심볼의 구조 분석' | reference-analysis, 필요 시 composition | 본문 조판·인쇄 규칙을 기본 로드 |
| R-5 | '데이터 포스터 분석, 나중에 인쇄 변경' | editorial-information, 이후 identity-production 관련 인쇄 지식 | 매체 변경 시 구식 가정 유지 |
| R-6 | '한글 본문 10pt. 적절한 행간 알아서 골라' | typography, formula-relations, design-handoff | 사용자 목표·서체 없는 상태에서 무근거 17pt 확정 |
| R-7 | '동일한 입력으로 치수 다시 계산' | formula-relations | 같은 공식·값에 다른 수치 결과 |
| R-8 | 'Figma에서 직접 제작해줘' | formula-relations, design-handoff, 실제 외부 플러그인 | 스킬이 직접 Figma API를 구현·실행했다고 주장 |

**측정:** (1) 필수 refs 실제 읽음, (2) 불필요 refs 읽음, (3) 의존성 누락,
(4) 근거/확실성 구분, (5) 산술 결과, (6) 기존 리뷰 계약 유지.
로딩 비율만 개선됐다고 합격 처리하지 않는다. 라이브 디자인 도구 실행·원본 재구성
품질 검증은 별도 실증 대상으로 남긴다.
