# Formula relations: 계산과 증거의 계약

수식의 개수보다 **입력·단위·적용 조건·출처·재계산 가능성**을 우선한다.
이 문서는 첫 관계 모델의 *초안*이며, 자동 솔버나 최적의 미감 표준은 아니다.

## 공통 기록 필드

- **id / class:** 정확한 기하학적 관계(Exact), 제한된 근사(Approximation),
  연구 조건이 있는 경험적 모델(Empirical), 지각 추정(Perceptual).
- **inputs / units / output:** 변수, 단위, 미측정/추정 여부, 단위 변환.
- **assumptions / scope:** 매체, 언어, 글꼴/렌더링 엔진, 좌표계, 대칭·고정 비율 등 전제.
- **evidence:** 수학적 유도 / 공인 표준 / 조건이 명시된 연구 / 사용자 지정.
- **validation / failure:** 입력 범위, 반례, 오차, 미지원 조건.
- **dependencies:** 이 수식을 평가하기 전에 확인해야 하는 메트릭·선행 수식.

2026-10-21 사용자 승인 A~H의 수치는 [typography-presets](typography-presets.md)에 별도 기록한다.
수식의 정확성과 배율·초기값의 경험적 타당성은 다른 문제다.

**정량 타이포그래피의 마이크로→매크로 상세 모델**은 필요할 때만
[typography-relations](typography-relations.md)를 읽는다. 기초 관계는 이 파일에 인덱스로 남기고
폰트 메트릭·자간·어간·혼식·본문 내용량 판단은 전문 모듈의 조건과 반례를 따른다.

## 최초 관계 모델

| ID | 관계 | 유효 범위 및 유의점 |
| --- | --- | --- |
| T-LEADING | `L = F × r` | L은 기준선 간격, F는 글자 크기, r은 사용자 지정 또는 조건이 맞는 사용자 승인 A~D 정책. 1.7×는 보편적 법칙 아님 |
| T-UNITS | `S = u / UPM × F` | 같은 종류의 폰트 단위 u를 실제 F 크기로 환산. bbox와 advance를 구분 |
| T-LINE | `N ≈ W / mean_advance` | 근사치. 실제 셰이핑·커닝·금칙·혼식이 줄바꿈을 변경 |
| T-SCALE | `F_k = F_0 × q^k` | 등비 스케일을 **선택한 경우**만 적용; q를 임의 결정하지 않음 |
| T-BASELINE | `H = (n - 1) × L` | 첫 줄부터 마지막 줄까지 **기준선 거리**, 텍스트 프레임 총 높이가 아님 |
| G-COLUMNS | `C = (W - M_l - M_r - (n - 1)G) / n` | 여백·간격·단 수를 제공받고 균등 단을 선택한 경우 |
| I-AREA | `r = sqrt(A / π)` | 원의 면적 A를 보존하는 반지름, 데이터 시각화는 면적 인코딩 방식의 선언 필요 |
| P-IMAGE | `effective_PPI = pixels / placed_width_inches` | 최종 실제 배치 폭 기준. 인쇄 적합 PPI는 인쇄 조건에 따라 결정 |

숫자만 존재한다는 사실이 어떤 디자인 선택의 우월성을 보장하지 않는다.
하드 제약과 목적이 충돌하거나 미지의 r/q가 남아 있으면 **유효 구간/후보 또는 미결정**을 출력한다.
구체적 경험적 범위를 일반화하려면 언어·매체·독해 과업과 통계적 근거를 별도 확보해야 한다.

## 대표 산술 사례

가로 판면 W=148mm, 좌·우 여백 각 12mm, 균등 3단, 간격 5mm라고 **지정됐다면**
`C=(148 - 12 - 12 - 2×5)/3=38mm`이다.
여백 12mm가 최적이어서 선택된 것은 아니다.
계산된 38mm도 도구에서 실제 적용된 값을 읽지 못했다면 **실제 객체 검증 전**이다.

## 1차 출처 예시 (규범적 근거로 자동 승격하지 않음)

- [OpenType font positioning](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos) —
  glyph advance/placement/kerning의 구분.
- [Google Fonts vertical metrics](https://googlefonts.github.io/gf-guide/metrics.html) —
  수직 메트릭과 CJK의 별도 취급.
- [OERT composition and modules](https://www.oert.org/en/composition-and-modules/) —
  행간과 판면 모듈의 관계.
- [EU data visualisation: respecting proportions](https://data.europa.eu/apps/data-visualisation-guide/respecting-proportions) —
  원의 반지름이 아닌 면적으로 값 표시.
- [Adobe InDesign image resolution](https://helpx.adobe.com/indesign/using/graphics-formats.html) —
  유효 해상도·인쇄 조건.
