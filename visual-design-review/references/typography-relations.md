# Typography relations — #5 설계 기반의 정량적 조판 의존성

이 모듈은 [PR #5](https://github.com/makesomethingshit/visual-design-review/pull/5)의
마이크로·매크로 타이포그래피 의존성 제안을 참고해 구성했다.
**기존 비평용** `typography.md`와 구분하며, 필요한 단계만 선택적으로 읽는다.

## 변수·측정의 정합성

| 변수 | 뜻 | 검증 조건 |
| --- | --- | --- |
| `F` | em 기준 글자 크기 (pt 등) | 문서 값 또는 사용자 지정 |
| `UPM` | font units per em | 실제 폰트/버전 head 테이블 |
| `a_i` | glyph advance | hmtx/HVAR 등과 셰이핑 문맥 |
| `k_i` | 위치 보정/커닝 | OpenType GPOS, 실제 shaping 엔진 |
| `t_i` | tracking / 추가 간격 | 도구의 설정값·입력 단위 |
| `L` | 기준선 간 거리 | 행간 설정/실제 기준선 위치 |
| `W` | 사용 가능한 행 폭 | 실제 텍스트 프레임과 안쪽 여백 |
| `r` | 글자 크기에 대한 행간 배율 | 사용자 지정 또는 근거 확인된 조건 |

**em 크기·눈에 보이는 윤곽 크기·bbox·advance는 서로 다르다.**
전각/분각, glyph 단위, pt, mm, tracking 단위를 혼동하지 않는다.
스크린샷에서 서체·물리 글자 크기나 실제 폰트 메트릭을 확인했다고 주장하지 않는다.

## PR #5에서 가져온 마이크로 → 매크로 의존성

| 관계 ID | 선행 요소 | 변하면 다시 확인할 것 |
| --- | --- | --- |
| `T-METRICS` | F, UPM, 실제 서체/축·쓰기 방향 | 폰트/버전/크기 |
| `T-SPACING` | T-METRICS, 실제 문자, glyph shaping, 어간·tracking | 원고·서체·커닝·언어 |
| `T-MEASURE` | T-SPACING, 사용 폭 W, 줄바꿈·금칙 조건 | 폭·문자·정렬 |
| `T-LEADING` | F, **별도 출처가 있는 r**, 혼식/글리프 높이 | 언어·서체·역할·매체 |
| `T-CAPACITY` | T-MEASURE, T-LEADING, 프레임/문단 | 행 수·행간·판면·원고 |
| `T-HIERARCHY` | 역할별 지정 크기, 실제 목표·매체 | 제목·본문·캡션·굵기 |

이것은 **필수 의존성**이지 모든 작업에 모듈을 일괄 로드하라는 뜻이 아니다.
본문 행간만 계산하면 실제 글줄 수 계산은 필요 없고, 페이지 수용량을 추정할 때는
행 길이·줄바꿈·기준선·문단·판면 조건을 함께 점검해야 한다.

## 관계식, 적용 범위, 반례

- **폰트 메트릭 환산:** `advance_pt = a_i / UPM × F`. 주어진 글리프 advance의 단위 변환.
  문자열 폭이나 눈에 보이는 글자 넓이는 실제 셰이핑·커닝·자간에 따라 다름.
- **문자열 폭:** `W_text ≈ Σadvance_i + Σadjustment_i + Σtracking_i`.
  실제 글리프/클러스터 인덱스, 간격이 적용되는 경계, 도구 단위를 명확히 한다.
  **tracking과 어간(공백 폭)은 다른 속성**으로 취급한다.
- **행 길이:** `N ≈ W / mean_advance`는 동일 단위로 계산한 추정치.
  실제 한글/라틴 혼식의 문자수·줄바꿈·금칙을 확정할 수 없다.
- **행간:** `L = F × r`. 계산은 정확해도 r을 고른 근거는 별개.
  #5의 한글 1.7·영문 1.5·일본어/중국어 2.0은 **연구·비교용 후보**이며 자동 기본값이 아니다.
  주언어가 불명확할 때 임의 임계값으로 결정하지 않는다. 혼식에서 언어마다 기준선을 따로 두지 않는다.
- **기준선 거리:** `H = (N_lines - 1) × L`. 첫/마지막 기준선 간 거리이지
  텍스트 프레임 전체 높이가 아님. 글리프 상하 범위, 문단 간격, 들여쓰기, 내부 여백 필요.
- **크기 위계:** `R = F_title / F_body`. 이미 결정된 크기의 비율만 설명하며
  황금비나 특정 위계가 미적으로 우수하다고 증명하지 않는다.

**산술 예시:** 실제 폰트 UPM=2048, advance=1024, F=12pt라면 해당 advance는 6pt.
사용자가 F=10pt, r=1.7을 제공했다면 기준선 간 거리는 17pt.
두 경우 모두 실제 조판의 육안 품질이나 생산 준비 완료를 의미하지 않는다.

## 자동 채택하면 안 되는 값과 검증 상태

#5의 10pt 본문, 전각 30칸 행 길이, tracking 0, 왼끝맞춤은 비교용 시작 시안일 수 있으나
근거 없이 최종 디자인 기본값으로 결정하지 않는다. 간격의 시각적 보정도 실측 근거가 필요하다.
#5에 나오는 개인 메모 N1/N2 및 U1 협의 내용은 **이 저장소에서 직접 재검증된 자료가 아니며**
해당 문헌 원문, 맥락, 적용 조건을 대조하기 전에는 공식 권장으로 승격하지 않는다.

**독립 검증 수준:** (1) 산술 재계산, (2) 실제 폰트/메트릭·원고 확인,
(3) 외부 도구가 반환한 적용 값, (4) 최종 크기 판독/인쇄를 구분한다.
뒤 단계가 없으면 `UNVERIFIED` 상태로 남긴다.

## 기술 참고

- [OpenType head / unitsPerEm](https://learn.microsoft.com/en-us/typography/opentype/spec/head)
- [OpenType hmtx / advance](https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx)
- [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos)
- [Adobe InDesign leading](https://helpx.adobe.com/indesign/desktop/format-and-style-text/character-formatting/adjust-line-spacing-with-leading.html)
- [PR #5 작성자의 타이포그래피 아키텍처 제안](https://github.com/makesomethingshit/visual-design-review/pull/5)
