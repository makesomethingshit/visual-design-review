# 인계 계약 (`40-selection.md` · `handoff-v1.md`)

레벨 2의 마지막 두 파일을 닫는 형식이다. `40-selection.md`는 사람의 선택과 수정 요청을, `handoff-v1.md`는 제작에 넘길 값을 `design-handoff` 계약 형식으로 고정한다. 이 계약은 `visual-design-review` 스킬의 `references/design-handoff.md`를 대체하지 않고, 그 필드를 레벨 2의 기록에서 채우는 방법을 정한다.

## `40-selection.md`

### 기록 항목

| 항목 | 내용 |
| --- | --- |
| 선택 시각·선택자 | 언제, 누가 골랐는지 (`USER`) |
| 고른 시안 | 시안 ID와 진입 파일 경로 |
| 대상 결과물 | 고른 시안이 다루는 `DEL` ID·품목·매체와, 같은 인계에서 아직 확정되지 않은 결과물의 처리 |
| 고른 이유 | 사람이 말한 이유를 그대로 요약. 레벨 2의 해석은 별도 문단으로 분리 |
| 함께 지시한 수정 | 요청 목록과 처리 상태 |
| 남긴 대안 | 고르지 않은 시안과 그 이유(사람이 밝힌 것 / 레벨 2의 관찰) |
| 근거와의 정합 | 고른 이유가 특정 근거 ID와 연결되는지, 어긋나면 어디서인지 |
| 다음 버전 | 확정 후보 파일과 `handoff` 버전 |

### 수정 요청 기록

요청마다 한 행을 만든다. 지시가 여러 개면 나눠 적는다.

| 요청 ID | 요청 요약 | 영향받는 항목 ID·시안 | 재개 단계 | 반영 결과·버전 |
| --- | --- | --- | --- | --- |
| R-01 | 시간 숫자를 더 크게 | `E-TYPE-01` A | 2(값) → 3(시안) | `draft-a-v2`, 52pt 후보 |
| R-02 | 후원 로고를 하단 띠로 | `E-ASSET-01` A, B | 2 → 3 | 두 시안 모두 재생성, `v2` |
| R-03 | 3단 대신 2단 | `E-GRID-01` 전체 | 2 | 판면 재계산, A/B 폐기 아님 |

### 버전 규칙

- 수정은 새 폴더 버전으로 만든다: `draft-a-v2`, `draft-b-v2`. 이전 버전과 캡처를 지우지 않는다.
- `drafts/INDEX.md`에 버전별 진입 파일과 한 줄 설명을 갱신한다. 확정 시안은 `drafts/final/`에 복사하고 원본은 그대로 둔다.
- 확정 후 새 요청은 `handoff-v2.md`로 올린다. 확정본을 덮어쓰지 않는다.
- 폐기한 시안은 폴더를 지우지 않고 `draft.md`에 폐기 이유와 시점을 적는다.

### 수정이 근거와 충돌할 때

- 확정 제약(판형·필수 문구·브랜드 색)을 깨는 요청은 그 사실과 영향 범위를 먼저 알리고 결정을 받는다. 요청을 받았다는 이유로 제약을 조용히 바꾸지 않는다.
- 레벨 1 근거와 반대되는 수정은 `DEVIATES`로 기록하고 잃는 것을 적는다. 근거를 고쳐 쓰지 않는다.
- 같은 항목을 세 번 이상 왕복하면 남은 쟁점과 선택지를 표로 좁혀 제시하고 결정을 기다린다.

## `handoff-v1.md`

### 필드와 채우는 곳

| design-handoff 필드 | 채우는 내용 | 가져오는 곳 |
| --- | --- | --- |
| Brief & constraints | 실제 콘텐츠, 매체, 판형·고정값, 사용자 목적, `필요 결과물`(`DEL`) 목록과 우선순위, 자산 상태 | `10-intake.md` |
| Design values | 객체·관계 ID, 값·단위·원점·좌표계, 식 ID와 적용 조건 | `20-translation.md`, `30-evidence-map.md` |
| Provenance | `USER` / `USER_APPROVED_PROJECT_POLICY` / `MEASURED` / `DERIVED` / `EMPIRICAL` / `INFERRED` / `UNKNOWN` | 표의 값을 그대로 |
| Decision status | `DETERMINED` / `PROJECT_INITIAL_PRESET` / `CANDIDATE` / `UNRESOLVED` / `CONFLICT` | 표의 값을 그대로. 승격 금지 |
| Verification status | `FORMULA_CHECKED` / `SOURCE_MEASURED` / `TOOL_APPLIED` / `OUTPUT_INSPECTED` / `UNVERIFIED` | 실제로 한 확인만 |
| Rule basis | 적용한 규칙의 `rule_id`·종류·강도·출처 버전·범위·조건·예외·검증 방법 | 레벨 3의 `rule-contract.md` 형식 |
| Reconstruction model | 레퍼런스에서 재구성한 모델(했을 때만) | 사례 ID와 관측 근거 |
| Adjustments | 대상·속성, 기본값→적용값, 이유, 적용 범위, 전후 효과 | 보정을 실제로 했을 때만 |
| Unresolved | 미결·충돌·미입력과 결정 주체 | `10-intake.md`의 `U`, 표의 `UNRESOLVED`/`CONFLICT` |
| Verification request | 레벨 3에서 확인할 실제 속성과 허용 편차 | 근거가 있는 항목만 |

### 예시 (합성)

값은 형식을 보여 주기 위한 합성 예시이며 실제 작품의 인계가 아니다.

```yaml
artifact: drafts/final/rl-a/index.html
source_drafts: [drafts/draft-a]
handoff_version: v1
brief_constraints:
  format: {value: "148x210, 3단", unit: mm, origin: USER, source: "10-intake.md#C-03"}
  copy: {state: EXAMPLE-COPY, note: "U-01 결정 전 비교용"}
deliverables:
  - {id: DEL-01, item: 안내 포스터, medium: "A2 오프셋 인쇄", priority: 1, artifact: drafts/final/rl-poster/index.html, decision_status: DETERMINED}
  - {id: DEL-02, item: 3단 리플릿, medium: "A4 3단 접지", priority: 2, artifact: drafts/draft-b/index.html, decision_status: CANDIDATE}
design_values:
  - {id: G-COL-1, item: 본문 단폭, value: 38, unit: mm, formula: DG-1, inputs: {page: 148, margin: 12, gutter: 5, columns: 3, origin: USER}, provenance: DERIVED, decision_status: DETERMINED, verification: [FORMULA_CHECKED]}
  - {id: T-BODY-1, item: 본문 행간, value: 17, unit: pt, formula: T-LEADING, inputs: {font_size: 10, ratio: 1.7, ratio_origin: USER}, provenance: DERIVED, decision_status: DETERMINED, verification: [FORMULA_CHECKED]}
  - {id: C-BASE-1, item: 바탕·문자 역할, value: "2색", provenance: INFERRED, decision_status: CANDIDATE, verification: [UNVERIFIED]}
unresolved:
  - {id: U-01, issue: 안내문 원고 최종본, decider: USER, effect: 줄 수·수용량 재계산}
  - {id: U-02, issue: 후원 로고 사용 범위, decider: USER, effect: 하단 띠 배치 확정 불가}
verification_request:
  - compare_actual_column_width_with_38mm
  - inspect_char_cut_at_actual_print_size
```

## 레벨 3 인계 체크리스트

항목마다 무엇으로 확인하는지 적었다. 확인하지 못한 항목은 체크하지 않고 이유를 남긴다.

- [ ] **확정 시안 경로:** `drafts/final/`의 진입 파일이 실제로 열리고, 캡처가 같은 상태를 보여 준다.
- [ ] **INDEX 최신:** `drafts/INDEX.md`의 시안·버전·진입 파일이 폴더와 일치한다.
- [ ] **스펙 필수 필드:** `handoff-v1.md`에 Brief & constraints, Design values, Provenance, Decision status, Verification status, Unresolved가 값과 함께 있다.
- [ ] **결과물 대응:** `10-intake.md`의 `DEL` 전 항목이 확정 시안이나 스펙의 어느 파일·항목에 대응하는지 적혔고, 빠진 품목은 이유와 함께 있다.
- [ ] **근거 양방향:** 인계·번역·매핑의 ID가 서로 맞고, 인계에 없는 ID가 표에 없다.
- [ ] **상태 승격 없음:** 사람이 고르지 않은 값이 `DETERMINED`가 아니고, 렌더를 보지 않은 값이 `OUTPUT_INSPECTED`가 아니다.
- [ ] **미결 목록:** 미결·가정·`UNVERIFIED` 항목과 각 결정 주체가 한 목록으로 모였다.
- [ ] **채택 방향 정합:** 레벨 1의 채택 방향과 벗어난 결정, 그 이유가 표시됐다.
- [ ] **경계:** 레벨 2가 하지 않은 일(비평·심각도·프리플라이트)과 검수받을 범위가 한 문단으로 적혔다.
- [ ] **인계문:** 무엇을 검수받는지, 어떤 판단이 아직 열려 있는지 첫 두 문장에 있다.

## 레벨 3 지적에 대응하는 기록

| 지적 ID | 영향 파일·항목 | 조치 | 새 버전 | 남은 쟁점 |
| --- | --- | --- | --- | --- |
| V-03 | `handoff-v1.md#T-BODY-1`, 시안 A | 행간 1.7 유지, 실제 렌더 확인 요청 추가 | `handoff-v2` | 출력 크기 판독 전 |

- 레벨 3의 판정을 레벨 2 기록에서 뒤집지 않는다. 동의하지 않으면 판정, 내 근거, 관찰 차이를 함께 적어 사람이 정하게 한다.
- 검수로 새로 정한 값은 `20-translation.md`와 `30-evidence-map.md`에 반영하고, 출처를 `USER`(사람 결정)와 레벨 3 검수 중 무엇인지 구분한다.
