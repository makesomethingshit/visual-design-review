# Rule contract — 규범의 효력, 적용 범위, 근거

이 문서는 **지식의 규범적 강도**를 수식의 정확도, 발견 사항의 심각도, 값의 결정·검증 상태와 **서로 독립된 축**으로 정의한다. 실제 Unicode 줄바꿈 엔진·폰트 분석기·PDF verifier를 구현하지 않는다. 과업에 관련된 규칙에만 이 계약을 적용한다.

## 최소 기록

| 필드 | 의미 |
| --- | --- |
| `rule_id` | 재사용·감사 가능한 안정 식별자. 아직 정의되지 않은 규칙 ID를 즉흥적으로 사실처럼 생성하지 않음 |
| `knowledge_kind` | `NORMATIVE`(규격·표기 등), `PERCEPTUAL`(전문가의 시지각 판단), `CONTEXTUAL`(브리프·의도·매체 선택) |
| `rule_strength` | `REQUIRED`(적용 가능한 강제 제약), `CONDITIONAL`(조건부), `ADVISORY`(권고·관습), `PROJECT_POLICY`(해당 프로젝트 승인값) |
| `source / source_version / document_status` | 문서·해당 버전·표준/초안/논문/사용자 정책 여부. 문헌을 봤다는 사실만으로 권위를 강화하지 않음 |
| `scope` | 언어·쓰기 방향·매체/플랫폼·글꼴/엔진·대상 텍스트·문서/프로젝트 범위 |
| `conditions / exceptions` | 적용 전 확인할 조건, 충돌/예외·우선할 브리프 또는 제작 사양 |
| `verification_method / evidence_status` | 코드 검사·실제 원본/렌더/인쇄 결과·전문가 비교 중 무엇으로 검증 가능한가; 미검증이면 `UNVERIFIED` |

- `NORMATIVE`는 규범적 자료의 **영역**이지 법적/실무적 강제성을 뜻하지 않는다. `REQUIRED`는 **실제로 적용되는 조건·권위가 증명된 경우에만** 사용한다.
- 계산식 `Exact/Approximation/Empirical/Perceptual`은 수학적·모델적 정확도의 축이다. 예를 들어 `L=F×r`은 정확한 산술이지만 r=1.7의 선택이 일반 규격을 의미하지 않는다.
- 판단의 `Defect/Interpretation`, 심각도 `Critical/Major/Minor/Exploratory`, 확실성, `PROJECT_INITIAL_PRESET` 결정 상태, `FORMULA_CHECKED` 등 검증 상태를 서로 섞지 않는다. 오류 **존재**와 디자인 **목표 손실 심각도**는 별도 판정한다.
- 전문가 취향·광학적 균형을 범용 자동 fail 규칙으로 만들지 않는다. 근거가 충돌하거나 문서 지위·적용 범위가 불명확하면 후보·충돌 또는 `UNVERIFIED`로 남긴다.
- 문헌 인용만으로 현재 디자인 객체나 물리 출력이 검사되었다고 선언하지 않는다.

## 규칙 충돌과 해석

1. 실제 문서·사용자 브리프·제작처의 확인된 강제 제약 및 문자의 **의미 무결성**을 먼저 기록한다. 서로 충돌하면 자동으로 하나를 고르지 않고 충돌을 보고한다.
2. 해당 언어·문자·쓰기 방향·매체와 문서 버전이 적용되는지 확인한다. 웹 접근성 규정을 모든 인쇄물의 미학적 정답으로 적용하지 않는다.
3. 권고·관습과 프로젝트 정책은 조건을 충족할 때만 **제안**한다. 사용자 승인 A~H는 프로젝트 초기 **비교 시안**이지 보편 규칙이 아니다.
4. 렌더·줄바꿈·서체 실측이 필요한 검사는 해당 입력/엔진이 없다면 미실행으로 남긴다.

### 조건부 사례

```yaml
rule_id: TYPO-KO-LINEBREAK-EXAMPLE   # 설명용 식별자; 채택된 정식 규칙 아님
knowledge_kind: NORMATIVE
rule_strength: CONDITIONAL
source: W3C KLReq
document_status: Group Note Draft
source_version: 2026-03-21
scope:
  language: ko
  writing_mode: horizontal
  medium: [print, digital]
conditions: [원문과 실제 줄바꿈 결과 확보, 해당 문서 절의 예외 확인]
exceptions: [프로젝트 스타일 정책, 언어/문맥에 따른 조판 차이]
verification_method: linebreak_or_rendered_output
evidence_status: UNVERIFIED
```

KLReq는 2026-03-21판 기준 **W3C Group Note Draft**이고 일부 주제가 미완성이므로 단독 절대 규칙집이 아니다. 기본 줄바꿈 기초는 [Unicode UAX #14](https://www.unicode.org/reports/tr14/)이며 언어·매체별 tailoring이 필요하다. [W3C KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/), [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos)를 참고하되 **규칙 코퍼스와 실행 검사기는 후속 이슈 #8·#9의 책임**이다.
