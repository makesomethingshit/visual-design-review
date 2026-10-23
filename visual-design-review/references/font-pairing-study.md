# 한글·로마자 서체 페어링 — 독립 비교 연구 초안 (#10)

> **미검증 연구 설계.** `typography.md`의 비평 계약이나 `typography-relations.md`의 정확한 계산을 대체하지 않는다. 특정 폰트 조합의 우수성이나 보정 배율을 아직 도출하지 않았다.

## 연구 질문

같은 nominal font size/weight가 한글과 로마자의 **시각적 크기, 무게, 명도·회색도, 리듬**이 같은 것을 보장하지 않는다면 어떤 특성으로 pairwise 비교할 것인가?

### 단위와 측정의 경계

- **정량 입력:** 실제 폰트 파일/버전, family/face, axis, size, font units, advance/position, 렌더러, 줄 폭, 본문 샘플, 출력 해상도 및 인쇄/화면.
- **지각 변수:** 한글 몸체 대비 Latin x-height/cap height의 광학 크기, stroke contrast/terminal, 공간의 균형, 기준선의 인상, texture의 연속성, 한글·영문 리듬.
- **맥락 변수:** 장문/제목, 독자, 브리프, 정체성/표현의 목표, 매체/관찰거리.

한글 블록 크기와 Latin x-height 등 측정 가능 수치가 있어도 자동으로 동일한 **perceptual match**가 성립하지 않는다. 해법이 여러 개일 수 있다.

## 기록 카드 (제안)

```yaml
pair_id: fp-demo-001
artifact_and_text_sha256: UNSET
font_left: {family: UNSET, version: UNSET, license: TO_VERIFY}
font_right: {family: UNSET, version: UNSET, license: TO_VERIFY}
render: {engine: UNSET, size_pt: UNSET, width_mm: UNSET}
controlled_variable: latin_family_only
other_variables_fixed: [text, korean_family, body_size, line_width]
raters: []  # blinded independent judgements; no fabricated expert data
comparisons: []  # A / B / tie / context-dependent, reason, confidence, counter-case
status: UNVERIFIED
```

## 프로토콜

1. 서로 다른 family를 섞는 페어링과 동일 multilingual family 사용 전략을 분리한다.
2. 동일 원고/설정에서 **서체·굵기·자간 중 하나만** 바꾼 A/B 실측 렌더를 만든다.
3. 실제 권한을 가진 서체만 사용하고, 재배포 권한이 불확실한 폰트 바이너리는 Git에 넣지 않는다.
4. 가능하면 **독립 평가자 3인 이상**이 파일/폰트 정체를 숨긴 상태에서 A/B/tie/context-dependent + 이유를 평가한다. 좌우 순서를 교환해 순서 편향을 확인한다.
5. 응답의 불일치와 원고/크기/매체별 선호 역전을 보존한다. 평균 하나로 미학적 법칙을 선언하지 않는다.
6. 사용자의 원래 의도가 유지되는지 확인한다. 실험적 불균형을 자동 오류로 판정하지 않는다.

## 완료 조건

- 최소 서로 다른 3가지 typography context(본문, 제목/라벨, 숫자·기호 혼식)를 포함한 짝 비교 fixture와 전제 기록
- 1차 원자료(폰트/렌더 환경·평가 로그·권한 또는 재현 절차) 보존
- 정량 오류와 미적 선호 구분, 반대 의견/동률 기록
- Expert judgement 미확보 시 `UNVERIFIED` 유지

### 참고 연구

[W3C KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/)와 [OpenType metrics](https://learn.microsoft.com/en-us/typography/opentype/spec/)는 일부 기술·관습을 정의하지만 **특정 한영 서체 페어링의 보편적 우열을 증명하지 않는다**.

**Out of scope:** 런타임 자동 폰트 추천 엔진, 고정 x-height 배율, 무단 서체 재배포, 실제 비교를 수행하지 않은 상태의 보정값 채택.
