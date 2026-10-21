# Design handoff: 외부 디자인 도구에 전달할 최소 계약

우리 스킬은 Figma·Penpot·Adobe의 내부 API를 소유하지 않는다.
사용자가 도구 제작을 요청했을 때 에이전트가 외부 플러그인에 넘길 **설계값과 검증 요구**
를 구조적으로 표현한다. 형식은 일반 Markdown/YAML/JSON 중 과업에 맞는 것을 사용할 수 있다.

## 반드시 구분할 항목

| 필드 | 의미 |
| --- | --- |
| Brief & constraints | 실제 콘텐츠, 매체, 판형·고정값, 사용자 목적 |
| Design values | 객체/관계, 수치, 단위와 좌표계, 계산식 ID |
| Provenance | USER / MEASURED / DERIVED / EMPIRICAL / INFERRED / UNKNOWN |
| Decision status | DETERMINED / CANDIDATE / UNRESOLVED / CONFLICT — 출처 및 검증 상태와 별개 |
| Verification status | FORMULA_CHECKED / SOURCE_MEASURED / TOOL_APPLIED / OUTPUT_INSPECTED / UNVERIFIED |
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

실제 도구가 객체를 생성했는지, 원본 폰트가 있는지, 38mm로 반영했는지는 **외부 실행 결과**가
있어야 확인할 수 있다. 도구가 확인값을 돌려주지 않으면 스킬은 '실행 미검증'으로 남긴다.
여러 후보가 조건을 만족하지만 목적이 정해지지 않았으면 하나로 좁히지 않는다.

**타이포그래피:** 사용자가 10pt 및 r=1.7을 명시하면 `T-LEADING`으로 17pt를 계산할 수 있다.
반대로 '적절한 행간'만 요구하면 r을 UNRESOLVED로 유지한다. 폰트·조판 결과는 별도의 미검증 항목이다.
