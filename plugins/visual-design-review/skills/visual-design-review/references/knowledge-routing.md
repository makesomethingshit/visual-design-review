# Knowledge routing: 필요한 지식만 로드하기

이 문서는 스킬의 **지식 선택 기준**이다. AI 에이전트/외부 디자인 도구의 호출 구현은 포함하지 않는다.
모듈은 이 저장소의 상대 references이며, 모든 과업에서 전부 읽는 것은 금지한다.

## 작업 신호와 모듈

A~H 정책은 현재 작업의 **명시적 opt-in** 또는 **독립적으로 확인된 현재 프로젝트의 활성 프로파일** 중 하나가 있을 때만 사용한다.
활성 프로파일의 확인 근거와 범위는 [typography-presets](typography-presets.md)를 따르며, 확인 후에는 opt-in을 반복 요구하지 않는다.
주언어·본문·인쇄 조건 충족만으로 프로젝트 프로파일을 활성화하지 않는다.
프로파일 적용 여부를 확인하려고 presets를 읽은 것과 초기값을 채택하는 것은 별개다.
활성 여부가 없거나 불명확하면 해당 정책값을 자동 채택하지 않고 후보/미결정으로 남긴다.
사용자가 개별 크기·배율을 명시한 계산은 프로파일 선택과 무관하게 USER 입력으로 처리할 수 있다.

| 신호 | 로드 | 제외 또는 조건 |
| --- | --- | --- |
| **비평/리뷰** | review-protocol + critique-rubric + review-output | 정량 분석/설계 명세는 요청된 경우에만 |
| **레퍼런스의 디자인 문제·생성 규칙·재구성 가설** | reference-analysis | 수치 관계를 다룰 때 formula-relations |
| **수치 설계·외부 도구 전달** | formula-relations + design-handoff | 원본에서 관계를 추출할 때 reference-analysis |
| **명시적 GitHub 제품 시각디자인 개선 요청** | product-correct | 기존 finding 사용 가능; 새 비평이 필요하면 review-protocol + review-output. GitHub 이슈·Draft PR 작성은 외부 도구/권한이 있을 때만; 일반 비평에서 자동 쓰기 금지 |
| 장문 본문·조판·문자 위계의 **비평** | typography | 실제 본문이 없으면 장문 조판 검사 제외 |
| **수치 타이포그래피 관계/설계** | typography-relations + formula-relations | 필요시 font metrics→spacing/leading→measure→capacity를 의존성별 로드 |
| **A~H opt-in 또는 활성 프로파일이 확인된 새 본문의 초기 행간을 결정** | typography-presets + typography-relations | 활성화 근거·주언어/쓰기 방향 확인; A~D만 조건부 사용 |
| **A~H opt-in 또는 활성 프로파일이 확인된 새 인쇄 본문 첫 비교 시안** | typography-presets + typography-relations | 활성화 근거 확인 후 E~H 초기 설정 후보 적용; 그 외 장르 기본 제외 |
| 그리드·공간·정렬 | composition | 판면/잡지/정보 구조는 editorial-information 추가 |
| 데이터/그래프·정보 계층 | editorial-information | 시각화에서만 데이터 인코딩 수식 적용 |
| 아이덴티티/로고·출력 규격 | identity-production (실제 관련 시) | 인쇄 프리플라이트 생략은 매체가 디지털 전용으로 확정되고 인쇄 요청·제약이 없는 경우만 |
| 역사·제작 계보·방법론 인용 | concept-context 또는 sources | 근거가 필요한 주장에만 추가 |

**조건을 조합**한다. 포스터에는 장문이 있을 수도 없을 수도 있다.
인쇄용 장문 포스터라면 typography + composition + identity-production의 제작 부분을,
제목 없는 디지털 심볼은 기하학 관련 지식만을 우선한다.
텍스트 없는 인쇄용 로고 PDF도 identity-production의 제작 지식을 선택한다.
문자 유무와 무관하게 별색·분판·오버프린트·투명도·가는 선 등 해당 출력 조건을 점검한다.
원본 속성이나 출력 조건을 확인할 수 없으면 인쇄 적합 판정 대신 UNVERIFIED로 남긴다.
실제 구조 파일이 없는 스크린샷은 물리 치수나 메트릭을 확정하지 않는다.

## 지식 규범·적용 범위 판단 (별도 축)

작업 모드(비평/역분석/정량 설계)와 지식의 효력·검증 방식은 독립된 축이다. **출처가 있는 규칙의 적용/충돌/예외**가 필요할 때만 [rule-contract](rule-contract.md)를 추가로 읽는다. `knowledge_kind`·`rule_strength`·출처 버전·문서 지위·언어/매체/쓰기 방향·원본 증거를 확인한다. 규범 자료에도 권고와 조건부 적용이 있으며 웹의 접근성 요구를 포스터의 미적 강제 규칙으로 옮기지 않는다. 출처 미확인 지각적 보정은 후보로 남기고 심각도 판정은 기존 비평 계약에 따른다. 현재는 **지식 적용을 지시**하는 문서이며 Unicode/폰트 엔진 구현은 없다.

## 의존 관계

- review-output은 review-protocol 및 critique-rubric의 정의와 결합해야 한다.
- design-handoff는 formula-relations의 근거 분류·단위 규칙을 따른다.
- typography-presets는 사용자 승인 정책이고, 주언어·본문/매체 범위, 다른 사용자·제작 제약을 먼저 확인한다.
  비평과 레퍼런스 역분석에서 원작의 속성을 정책값으로 덮어쓰지 않는다.
- typography-relations는 formula-relations의 단위·근거 계약을 따른다. T-MEASURE는 T-SPACING과 실제 폭에 의존하고,
  T-CAPACITY는 T-MEASURE 및 T-LEADING에 의존한다. 개별 관계에서 입력이 없으면 적용을 유보한다.
- reference-analysis가 구체적 관계식/재구성을 요청하는 경우 formula-relations를 로드한다.
  원본의 좌표계·객체 관측 및 불확실성 상태를 확보하지 못했다면 구조·서체·그리드 수치를 발명하지 않는다.
- 수식의 변수 정의에 다른 모듈/측정이 필요하면 선행 조건이 충족될 때만 적용한다.
- 인쇄 → 디지털, 단문 → 장문 등 브리프가 변하면 선택과 기존 계산의 가정을 재평가한다.

## 품질 기준

스킬 라우팅은 지시문일 뿐 정적 분기 프로그램이 아니다.
모듈 미탐(필요 자료를 읽지 않음), 오탐(무관한 자료를 읽음),
의존성 누락, 근거 없는 측정, 컨텍스트 비용을 **각기 따로** 기록한다.
토큰 절감이 오류 증가를 정당화하지 않는다.

기존 비평 단독 요청은 review-protocol·critique-rubric·review-output과 관련 분야 refs만 읽고,
새 레퍼런스 역분석·설계 자료는 기본 로드하지 않는다.
