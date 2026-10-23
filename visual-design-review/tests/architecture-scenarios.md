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
| R-8 | 'Figma에서 직접 제작해줘' | formula-relations, design-handoff, 실제 외부 플러그인 | 스킬이 직접 Figma API를 구현·실행했다고 주장 |
| R-9 | 'UPM=2048, advance=1024, F=12pt의 advance 환산' | typography-relations, formula-relations | 6pt가 아닌 값이나 글리프 윤곽 크기로 오인 |
| R-10 | '한영 혼식의 주언어/행간 미지정' | typography-presets, typography-relations | 주언어 불명확한데 1.5/1.7 자동 확정, 임의 비중 임계값 생성 |
| R-11 | '사용자가 지정한 10pt와 1.7배의 행간 계산 및 외부 도구 전달 명세' | typography-relations, design-handoff | 17pt 계산 실패 또는 실제 제작 완료 주장 |
| R-12 | '서체·원고 변경 뒤 판면 수용량 재계산' | typography-relations, knowledge-routing | 이전 글줄·프레임 가정 유지 |
| R-13 | '영문 중심 새 가로 본문 10pt' | typography-presets, typography-relations | B=1.5 대신 무근거 수치 사용, 15pt 계산 오류 |
| R-14 | '일본어/중국어 중심 새 가로 본문 10pt' | typography-presets, typography-relations | C/D=2.0 누락, 20pt 계산 오류 |
| R-15 | '한글 본문 사용자 명시 행간 1.8' | typography-presets, typography-relations | 정책 A=1.7을 더 우선해 덮어씀 |
| R-16 | '기존 한글 포스터 비평' | review-protocol, critique-rubric, review-output | 승인 초기값을 원작에 강제로 적용하여 결함 선언 |
| R-17 | '영문 디지털 심볼·제목' | 과업별 구성 지식 | 인쇄 본문 E~H 설정 강제 |
| R-18 | '가로 본문을 세로쓰기로 변경' | typography-presets, typography-relations | 기존 가로쓰기 배율을 재검토 없이 강제 |
| R-19 | 'print preflight', 'composition analysis', '포스터 피드백' 명시/자연어 호출 | 기존 리뷰 스킬 + 필요한 review refs | SKILL.md를 실제 읽지 않음; 예전 호출 문구에서 비활성화 |
| R-20 | 'CSS grid gap 작동만 설명해줘' | 스킬 미선택 | 그래픽 디자인 스킬의 오발동 |
| R-21 | '1200px 포스터에서 x=120,420,720인 정렬축의 모델을 분해' | reference-analysis, formula-relations | 300px 피치와 좌표 정규화 오류, 원작자 의도를 확정 |
| R-22 | '같은 세 좌표를 격자/독립 배치 모델로 비교하고 재구성 오차를 적어줘' | reference-analysis | 다른 모델의 잔차가 같을 수 있음을 누락; 미실행 재렌더링을 측정했다고 주장 |
| R-23 | '텍스트 없는 인쇄용 로고 PDF의 제작 점검' | identity-production의 인쇄 지식 | 심볼만 있다는 이유로 별색·분판·오버프린트·투명도·가는 선 검사를 생략 |
| R-24 | '출력 조건/원본 속성을 모르는 로고 스크린샷의 인쇄 적합성' | identity-production, 미확인 속성은 UNVERIFIED | 원본이나 제작처 조건 없이 인쇄 적합 판정 |
| R-25 | 'raw [600,600], 보정 -50, UPM=1000, 10pt와 shaped [550,600] 비교' | typography-relations, formula-relations | 각각 11.5pt가 아님; shaped에 커닝을 중복 합산해 11.0pt로 계산 |
| R-26 | 'advance [6,6]pt, x placement만 +1pt' | typography-relations | 논리 진행량 12pt에 위치 이동을 합산; ink bounds와 혼동 |
| R-27 | '동일한 tracking의 미반영/기반영 입력 폭 비교' | typography-relations | 적용 경계·단위·포함 여부 미확인, tracking 중복 반영 |
| R-28 | '서로 다른 UPM/출력 scale·크기의 폰트 run 합산' | typography-relations | 단위를 확인하지 않고 advance 원시 수치를 직접 합산 |

| R-29 | '한국어 인쇄물 KLReq 지침을 모든 결과의 위반 기준으로 채점해줘' | rule-contract, typography | 초안/조건부 관습의 절대 규칙화; 목표 손실 없이 Major 부여 |
| R-30 | '잡지의 정렬 원칙을 웹 접근성의 필수 기준으로 적용해줘' | rule-contract, 작업 매체 확인 | 인쇄 관습과 웹 WCAG 적용 범위 혼동; 불명확한 규격 강행 |
| R-31 | '이 이미지에서 어느 폰트가 fallback됐는지 정확히 말해줘' | rule-contract, typography | 원본/엔진 로그 없는 스크린샷에서 fallback 폰트를 확정 |
| R-32 | '한영 원고와 실제 줄바꿈 정보 없이 정확한 수용 문자수를 확정해줘' | typography-relations, rule-contract | shaping/줄바꿈 입력 누락인데 실제 조판 결과로 수치 확정 |
| R-33 | '다른 프로젝트의 새 본문을 만들되 이 프로젝트 A~H 기본값을 강제로 적용해줘' | typography-presets, rule-contract | 해당 프로젝트에 대한 opt-in 없이 특정 사용자 정책을 보편값으로 상속 |

**측정:** (1) 필수 refs 실제 읽음, (2) 불필요 refs 읽음, (3) 의존성 누락,
(4) 근거/확실성 구분, (5) 산술 결과, (6) 기존 리뷰 계약 유지.
로딩 비율만 개선됐다고 합격 처리하지 않는다. 라이브 디자인 도구 실행·원본 재구성
품질 검증은 별도 실증 대상으로 남긴다.

## 실제 모델 평가의 판정 조건 (아직 미실행)

각 입력을 **독립된 Codex 세션**에서 실행하고 실제 **스킬 선택·파일 열람 도구 이벤트**를
함께 기록한다. 이름을 언급했거나 문서의 존재를 확인했다는 것만으로 합격시키지 않는다.
필요한 파일을 읽지 못했다면 `BLOCKED`로 기록한다.

- 입력별: 모드/내용/매체, 기대한 필수 references, 제외할 refs, 실제로 읽힌 refs.
- 출력별: 사용자 승인 정책 적용 여부, 사용자 지정값 우선 여부, 계산값의 단위/근거,
  미관찰·미검증 값의 날조 여부, 기존 비평 유형·심각도 위반 여부.
- 비교: 기존 A~J/F 비평 평가 사례를 새 snapshot과 이전 snapshot 각각에 같은 조건으로 실행하고
  변경된 합격/실패 이유를 확인한다. 이전 실행 기록을 신규 검증으로 재사용하지 않는다.
- 레퍼런스: 합성 지오메트리 산술은 **정적 테스트**에서 다루되, 실제 래스터 해체·재렌더링
  정확도는 도구 지원 및 입력이 확보되지 않으면 미검증으로 남긴다.
