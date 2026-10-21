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
| R-6 | '한글 중심 새 인쇄 본문, 크기·행간 미지정' | typography-presets, typography-relations, design-handoff | E=10pt/A=1.7로 17pt 초기 시안 미제시, 또는 보편적 최적값·실측으로 주장 |
| R-7 | '동일한 입력으로 치수 다시 계산' | formula-relations | 같은 공식·값에 다른 수치 결과 |
| R-9 | 'UPM=2048, advance=1024, F=12pt의 advance 환산' | typography-relations, formula-relations | 6pt가 아닌 값이나 글리프 윤곽 크기로 오인 |
| R-10 | '한영 혼식의 주언어/행간 미지정' | typography-presets, typography-relations | 주언어 불명확한데 1.5/1.7 자동 확정, 임의 비중 임계값 생성 |
| R-11 | '사용자가 10pt와 1.7배를 지정한 행간' | typography-relations, design-handoff | 17pt 계산 실패 또는 실제 제작 완료 주장 |
| R-12 | '서체·원고 변경 뒤 판면 수용량 재계산' | typography-relations, knowledge-routing | 이전 글줄·프레임 가정 유지 |
| R-13 | '영문 중심 새 가로 본문 10pt' | typography-presets, typography-relations | B=1.5 대신 무근거 수치 사용, 15pt 계산 오류 |
| R-14 | '일본어/중국어 중심 새 가로 본문 10pt' | typography-presets, typography-relations | C/D=2.0 누락, 20pt 계산 오류 |
| R-15 | '한글 본문 사용자 명시 행간 1.8' | typography-presets, typography-relations | 정책 A=1.7을 더 우선해 덮어씀 |
| R-16 | '기존 한글 포스터 비평' | review-protocol, critique-rubric, review-output | 승인 초기값을 원작에 강제로 적용하여 결함 선언 |
| R-17 | '영문 디지털 심볼·제목' | 과업별 구성 지식 | 인쇄 본문 E~H 설정 강제 |
| R-18 | '가로 본문을 세로쓰기로 변경' | typography-presets, typography-relations | 기존 가로쓰기 배율을 재검토 없이 강제 |
| R-8 | 'Figma에서 직접 제작해줘' | formula-relations, design-handoff, 실제 외부 플러그인 | 스킬이 직접 Figma API를 구현·실행했다고 주장 |

**측정:** (1) 필수 refs 실제 읽음, (2) 불필요 refs 읽음, (3) 의존성 누락,
(4) 근거/확실성 구분, (5) 산술 결과, (6) 기존 리뷰 계약 유지.
로딩 비율만 개선됐다고 합격 처리하지 않는다. 라이브 디자인 도구 실행·원본 재구성
품질 검증은 별도 실증 대상으로 남긴다.
