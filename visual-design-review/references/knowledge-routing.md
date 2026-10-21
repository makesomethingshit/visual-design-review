# Knowledge routing: 필요한 지식만 로드하기

이 문서는 스킬의 **지식 선택 기준**이다. AI 에이전트/외부 디자인 도구의 호출 구현은 포함하지 않는다.
모듈은 이 저장소의 상대 references이며, 모든 과업에서 전부 읽는 것은 금지한다.

## 작업 신호와 모듈

| 신호 | 로드 | 제외 또는 조건 |
| --- | --- | --- |
| **비평/리뷰** | review-protocol + critique-rubric + review-output | 정량 분석/설계 명세는 요청된 경우에만 |
| **레퍼런스의 수학적 해체·재구성 가설** | reference-analysis | 수치 관계를 다룰 때 formula-relations |
| **수치 설계·외부 도구 전달** | formula-relations + design-handoff | 원본에서 관계를 추출할 때 reference-analysis |
| 장문 본문·조판·문자 위계 | typography | 실제 본문이 없으면 장문 조판 검사 제외 |
| 그리드·공간·정렬 | composition | 판면/잡지/정보 구조는 editorial-information 추가 |
| 데이터/그래프·정보 계층 | editorial-information | 시각화에서만 데이터 인코딩 수식 적용 |
| 아이덴티티/로고·출력 규격 | identity-production (실제 관련 시) | 심볼만 있으면 인쇄 프리플라이트 생략 |
| 역사·제작 계보·방법론 인용 | concept-context 또는 sources | 근거가 필요한 주장에만 추가 |

**조건을 조합**한다. 포스터에는 장문이 있을 수도 없을 수도 있다.
인쇄용 장문 포스터라면 typography + composition + identity-production의 제작 부분을,
제목 없는 디지털 심볼은 기하학 관련 지식만을 우선한다.
실제 구조 파일이 없는 스크린샷은 물리 치수나 메트릭을 확정하지 않는다.

## 의존 관계

- review-output은 review-protocol 및 critique-rubric의 정의와 결합해야 한다.
- design-handoff는 formula-relations의 근거 분류·단위 규칙을 따른다.
- reference-analysis가 구체적 관계식/재구성을 요청하는 경우 formula-relations를 로드한다.
- 수식의 변수 정의에 다른 모듈/측정이 필요하면 선행 조건이 충족될 때만 적용한다.
- 인쇄 → 디지털, 단문 → 장문 등 브리프가 변하면 선택과 기존 계산의 가정을 재평가한다.

## 품질 기준

스킬 라우팅은 지시문일 뿐 정적 분기 프로그램이 아니다.
모듈 미탐(필요 자료를 읽지 않음), 오탐(무관한 자료를 읽음),
의존성 누락, 근거 없는 측정, 컨텍스트 비용을 **각기 따로** 기록한다.
토큰 절감이 오류 증가를 정당화하지 않는다.

기존 비평 단독 요청은 review-protocol·critique-rubric·review-output과 관련 분야 refs만 읽고,
새 레퍼런스 역분석·설계 자료는 기본 로드하지 않는다.
