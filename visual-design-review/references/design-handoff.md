# Design handoff: 외부 디자인 도구에 전달할 최소 계약

우리 스킬은 Figma·Penpot·Adobe의 내부 API를 소유하지 않는다.
사용자가 도구 제작을 요청했을 때 에이전트가 외부 플러그인에 넘길 **설계값과 검증 요구**
를 구조적으로 표현한다. 형식은 일반 Markdown/YAML/JSON 중 과업에 맞는 것을 사용할 수 있다.

## 반드시 구분할 항목

| 필드 | 의미 |
| --- | --- |
| Brief & constraints | 실제 콘텐츠, 매체, 판형·고정값, 사용자 목적 |
| Design values | 객체/관계 ID, 수치, 단위·원점·좌표계, 계산식 ID와 적용 조건 |
| Provenance | USER / USER_APPROVED_PROJECT_POLICY / MEASURED / DERIVED / EMPIRICAL / INFERRED / UNKNOWN |
| Decision status | DETERMINED / PROJECT_INITIAL_PRESET / CANDIDATE / UNRESOLVED / CONFLICT — 출처·검증 상태와 별개. PROJECT_INITIAL_PRESET은 최종 확정값이 아닌 채택된 첫 시안값 |
| Verification status | FORMULA_CHECKED / SOURCE_MEASURED / TOOL_APPLIED / OUTPUT_INSPECTED / UNVERIFIED |
| Rule basis (when applicable) | [rule-contract](rule-contract.md)의 rule_id / knowledge_kind / rule_strength / source_version / document_status / scope / conditions / exceptions / conflict / verification_method. 출처 강도·수식 정확도·디자인 결정 상태를 별개로 둠 |
| Unresolved | 충돌·미입력·여러 가능한 해와 적용 조건 |
| Verification request | 외부 도구에서 가능할 경우 확인할 실제 속성, 허용 편차 |

예시(사용자 제공 값으로 계산된 경우):

```yaml
canvas: {width: 148, height: 210, unit: mm}
inputs:
  columns: {value: 3, origin: USER}
  margin_left: {value: 12, unit: mm, origin: USER}
  margin_right: {value: 12, unit: mm, origin: USER}
  gutter: {value: 5, unit: mm, origin: USER}
derived:
  column_width:
    value: 38
    unit: mm
    formula: G-COLUMNS
    origin: DERIVED
    decision_status: DETERMINED
    verification: [FORMULA_CHECKED]
verify_if_available:
  - compare_actual_column_width_with_38mm
unresolved:
  - actual_rendered_font_metrics
```

위 값은 **예시 입력에 대한 산술 결과**이지 보편적으로 선택할 레이아웃이 아니다.
추정한 값은 DERIVED가 아니라 INFERRED/EMPIRICAL로 표기한다.
레퍼런스 관측에서 사용하는 프레임, 개별 좌표, 측정·추론의 구분은
[reference-analysis](reference-analysis.md)의 증거 등급에 따른다.

적용 규칙이 있을 때 `rule_id`와 실제 조건/예외 확인 결과를 함께 전달한다. 확인되지 않은 폰트 fallback·금칙·규범 충돌을 임의의 `DETERMINED`로 승격하지 않는다. 모든 전달에 상세 규칙 목록을 강제하지 않으며 해당 과업에 필요한 내용만 기록한다.

실제 도구가 객체를 생성했는지, 원본 폰트가 있는지, 38mm로 반영했는지는 **외부 실행 결과**가
있어야 확인할 수 있다. 도구가 확인값을 돌려주지 않으면 스킬은 '실행 미검증'으로 남긴다.
여러 후보가 조건을 만족하지만 목적이 정해지지 않았으면 하나로 좁히지 않는다.

**타이포그래피:** 사용자가 10pt 및 r=1.7을 명시하면 `T-LEADING`으로 17pt를 계산할 수 있다.
'적절한 행간'만 요청한 경우에도 현재 작업의 **명시적 opt-in** 또는 **독립적으로 확인된 현재 프로젝트의 활성 프로파일** 중 하나와
주언어·새 가로 본문 조건이 모두 있어야 승인 A~D를 **초기 정책값**으로 제안할 수 있다.
주언어 확인만으로 프로파일 선택을 대신하지 않는다. 확인된 활성 프로파일에는 opt-in을 반복 요구하지 않는다.
두 활성화 근거가 모두 없거나 불명확하면 정책값을 자동 채택하지 않는다.
주언어 불명확·다른 쓰기 방향 등의 경우 r은 UNRESOLVED로 남긴다.
인쇄 본문 최초 비교 시안에만 E~H를 적용 가능하며 출처는 USER_APPROVED_PROJECT_POLICY,
결정 상태는 PROJECT_INITIAL_PRESET, L=F×r로 계산한 값은 DERIVED,
실제 도구 적용·폰트/줄바꿈·최종 크기 판독은 확인 전까지 UNVERIFIED다.
관련 정책: [typography-presets](typography-presets.md).

### 승인된 프로젝트 초기 시안 전달 예시

```yaml
scenario: print_body_first_comparison
primary_language: ko
policy: {source: USER_APPROVED_PROJECT_POLICY, approved_on: 2026-10-21, opt_in: true, activation_basis: explicit_user_request_for_current_project}
initial_settings:
  font_size: {value: 10, unit: pt, id: E, status: PROJECT_INITIAL_PRESET}
  line_measure: {value: 30, unit: fullwidth_equivalent, id: F, status: PROJECT_INITIAL_PRESET}
  extra_tracking: {value: 0, id: G, status: PROJECT_INITIAL_PRESET}
  alignment: {value: start, id: H, status: PROJECT_INITIAL_PRESET}
  leading_ratio: {value: 1.7, id: A, status: PROJECT_INITIAL_PRESET}
derived:
  baseline_distance: {value: 17, unit: pt, formula: T-LEADING, origin: DERIVED, decision_status: PROJECT_INITIAL_PRESET, verification: [FORMULA_CHECKED]}
unverified: [font_metrics, shaped_line_breaks, tool_applied, final_readability]
```

이번 요청에 opt-in을 반복하지 않았지만 별도 프로젝트 설정/브리프를 실제로 확인한 경우에는
위 예시의 policy만 다음처럼 바꾼다. evidence는 예시 식별자이며 실제 확인한 자료 위치와 적용 범위를 기록한다.
승인 날짜나 스킬 저장소의 정책 문서만으로 이 경로를 사용하지 않는다.

```yaml
policy: {source: USER_APPROVED_PROJECT_POLICY, approved_on: 2026-10-21, activation_basis: independently_verified_active_project_profile, profile: A-H, project: current_project, evidence: "current_project_brief#typography"}
```

사용자 제약에 따라 수정 가능한 **첫 비교 시안**이다. 서체·원고·매체를 확인하지 않고 최종 규격으로 강제하지 않는다.
