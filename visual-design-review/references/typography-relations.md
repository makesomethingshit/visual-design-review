# Typography relations — #5 설계 기반의 정량적 조판 의존성

이 모듈은 [PR #5](https://github.com/makesomethingshit/visual-design-review/pull/5)의
마이크로·매크로 타이포그래피 의존성 제안을 참고해 구성했다.
**기존 비평용** `typography.md`와 구분하며, 필요한 단계만 선택적으로 읽는다.

## 변수·측정의 정합성

| 변수 | 뜻 | 검증 조건 |
| --- | --- | --- |
| `F` | em 기준 글자 크기 (pt 등) | 문서 값 또는 사용자 지정 |
| `UPM` | font units per em | 실제 폰트/버전 head 테이블 |
| `a_raw_i` / `a_shaped_i` | 보정 전 / 셰이핑 완료 glyph advance | glyph 시퀀스·폰트/축·shaping 엔진과 입력 표현을 기록 |
| `Δadvance_i` | 진행량을 바꾸는 보정 | raw 경로에서만 한 번 반영; GPOS xAdvance 등 |
| `offset_i` | glyph 배치 원점의 위치 보정 | x/y placement/offset; 논리 진행량과 분리 |
| `S` | 입력 advance의 em당 단위 수 | raw 폰트 단위는 UPM; shaped 출력은 실제 엔진 scale 확인 |
| `T_remaining` | 아직 반영되지 않은 tracking의 합 (pt 등) | 적용 경계·단위·기반영 여부를 확인해 한 번만 추가 |
| `L` | 기준선 간 거리 | 행간 설정/실제 기준선 위치 |
| `W` | 사용 가능한 행 폭 | 실제 텍스트 프레임과 안쪽 여백 |
| `r` | 글자 크기에 대한 행간 배율 | 사용자 지정, 승인 [프로젝트 정책](typography-presets.md), 또는 실증 근거 |

**em 크기·눈에 보이는 윤곽 크기·bbox·advance는 서로 다르다.**
전각/분각, glyph 단위, pt, mm, tracking 단위를 혼동하지 않는다.
스크린샷에서 서체·물리 글자 크기나 실제 폰트 메트릭을 확인했다고 주장하지 않는다.

## 실제 한글·영문 혼식 조판의 선행 입력 계약

수식은 사용 가능한 advance·기준선 값을 계산한다. 하지만 **실제 조판의 정확한 줄 길이·문단 수용량/폴백 여부**를 판단하려면 추가 입력이 필요하다. 원문과 언어·script run, 문자→glyph mapping 및 폰트 coverage/실제 fallback, shaping 입력(폰트/버전/축/엔진/방향), 실제 줄바꿈·금칙 정책과 렌더/프레임 폭을 구분해서 확인한다. `T-METRICS` 이전에 이 입력들의 **확인 가능 상태**를 기록하며, 일부라도 없으면 그 입력을 필요로 하는 최종 조판 주장을 `UNVERIFIED`로 둔다. 문자별 cmap 검사가 실제 폴백 발생의 증명은 아니다. 한글·영문 같은 em 크기가 광학적 크기나 weight의 일치를 증명하지 않는다.

규범/조판 관습을 적용할 때는 [rule-contract](rule-contract.md)의 출처 버전·적용 조건·예외를 참조한다. KLReq 초안/웹 접근성/사용자 브리프의 효력을 혼동하지 않는다. 문자 의미·실제 서체·미검증 스크린샷을 근거 없는 숫자로 보충하지 않는다. Unicode/KLReq validator 및 optical matching은 별도 작업이다.

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

- **폰트 메트릭 환산:** `advance_pt = a_raw_i / UPM × F`. 주어진 보정 전 폰트 advance의 단위 변환.
  문자열 폭이나 눈에 보이는 글자 넓이는 실제 셰이핑·커닝·자간에 따라 다름.
- **문자열 진행량:** 아래의 raw/shaped 입력 계약을 선택한다. placement와 ink bounds를
  논리 진행량에 합산하지 않는다. **tracking과 어간(공백 폭)은 다른 속성**으로 취급한다.
- **행 길이:** `N ≈ W / mean_advance`는 동일 단위로 계산한 추정치.
  실제 한글/라틴 혼식의 문자수·줄바꿈·금칙을 확정할 수 없다.
- **행간:** `L = F × r`. 계산은 정확해도 r을 고른 근거는 별개.
  한글 1.7·영문 1.5·일본어/중국어 2.0은 **2026-10-21 사용자 승인**으로 새 가로 본문 시안의
  조건부 초기 배율로 채택됐다([typography-presets](typography-presets.md)). 보편적 법칙은 아니다.
  주언어가 불명확할 때 임의 임계값으로 결정하지 않는다. 혼식에서 언어마다 기준선을 따로 두지 않는다.
- **기준선 거리:** `H = (N_lines - 1) × L`. 첫/마지막 기준선 간 거리이지
  텍스트 프레임 전체 높이가 아님. 글리프 상하 범위, 문단 간격, 들여쓰기, 내부 여백 필요.
- **크기 위계:** `R = F_title / F_body`. 이미 결정된 크기의 비율만 설명하며
  황금비나 특정 위계가 미적으로 우수하다고 증명하지 않는다.

**산술 예시:** 실제 폰트 UPM=2048, advance=1024, F=12pt라면 해당 advance는 6pt.
새 한글 중심 인쇄 본문 시작 시안에서 프로젝트 E=10pt 및 A=1.7을 적용했다면 기준선 간 거리는 17pt.
두 경우 모두 실제 조판의 육안 품질이나 생산 준비 완료를 의미하지 않는다.

### 문자열 진행량: raw와 shaped 입력을 혼합하지 않기

관계 ID는 `T-SPACING`이며 아래 raw/shaped는 입력 표현별 하위 형식이다.
**class: Exact**는 주어진 advance·보정·scale·tracking의 산술 관계에 한정한다.
변수·단위는 위 표, 근거는 아래 OpenType/HarfBuzz 기술 참고를 따른다.
검증은 W-1~W-7의 산술 검산이며 실제 조판 품질·도구 적용의 검증과 구분한다.

다음 식은 같은 폰트·크기·scale을 쓰는 **단일 수평 run의 논리 진행량**이다.
쓰기 방향·부호 규약, 실제 glyph/cluster 시퀀스와 shaping 조건을 먼저 기록한다.
문자별 hmtx 값만으로 실제 문자열의 glyph 선택·합자·줄바꿈을 확정하지 않는다.

- **raw:** `W_raw = Σ(a_raw_i + Δadvance_i) / S × F + T_remaining`.
  보정 전 advance와 해당 glyph에 적용되는 advance 변화량을 같은 단위로 확보한다.
  커닝 등 진행량 보정은 정확히 한 번 반영하며, 값이 없으면 임의 추정하지 않는다.
- **shaped:** `W_shaped = Σa_shaped_i / S × F + T_remaining`.
  최종 shaping 출력의 advance에는 적용된 커닝/GPOS advance 보정을 다시 더하지 않는다.
  HarfBuzz x_advance/y_advance는 진행량이고 x_offset/y_offset은 배치 위치다.
- **placement:** GPOS xPlacement/yPlacement 및 x/y offset은 glyph 원점과 ink bounds에
  반영한다. 논리 진행량에는 더하지 않는다. 잉크가 차지하는 외곽 폭은 별도 측정값이다.
- **tracking:** 입력에 이미 포함됐는지, 적용할 run·glyph/cluster 경계와 글줄 끝 처리,
  단위(pt·em·1/1000 em 등)를 기록한다. 미반영 경계의 간격만 출력 단위로 환산해
  T_remaining에 더한다. 기반영 입력에는 같은 tracking을 다시 더하지 않는다.
- **scale/혼합 폰트:** raw 폰트 단위라면 S=UPM이다. shaped 값이 항상 폰트 단위인 것은
  아니며 HarfBuzz의 실제 x scale 등 출력 단위를 확인한다. run마다 S와 F로 공통 pt 등에
  환산한 뒤 합산한다. 세로쓰기에는 해당 축의 advance/scale 계약을 별도로 확인한다.
  입력 표현·scale·tracking 포함 여부가 불명확하면 UNVERIFIED로 남긴다.

**합성 산술 인수 예시:** 실제 폰트·도구 시험이 아니다. 아래 offset은 배치 이동값이며
폭에 합산하지 않는다. Δadvance는 run 내 변화량의 합, tracking은 미반영 경계 간격의
합을 pt로 환산한 값이다. 기존 계약 검사가 이 표의 입력과 기대값을 직접 읽어 검산한다.

| ID | 입력 | advance | S | F (pt) | Δadvance 합 | offset (pt) | 미반영 tracking (pt) | W_text (pt) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W-1 | shaped | 6,6 | 10 | 10 | 0 | 1 | 0 | 12 |
| W-2 | raw | 600,600 | 1000 | 10 | -50 | 0 | 0 | 11.5 |
| W-3 | shaped | 550,600 | 1000 | 10 | 0 | 0 | 0 | 11.5 |
| W-4 | shaped | 550,600 | 1000 | 10 | 0 | 0 | 0.5 | 12 |
| W-5 | shaped | 600,600 | 1000 | 10 | 0 | 0 | 0 | 12 |
| W-6 | raw | 600 | 1000 | 10 | 0 | 0 | 0 | 6 |
| W-7 | shaped | 1024 | 2048 | 12 | 0 | 0 | 0 | 6 |

W-1은 pt 단위의 advance [6,6]을 1pt 이동해도 진행량은 12pt다.
W-2/W-3은 같은 11.5pt이며, W-3에 -50을 다시 더한 11.0pt는 중복 보정이다.
W-4는 유일한 glyph 사이 경계에 0.5pt 추가, W-5는 같은 tracking이 이미 advance에 포함된 입력이다.
W-6/W-7의 혼합 run은 각각 환산한 뒤 합산하면 12pt다.

## 승인된 초기 설정과 검증 상태

2026-10-21 사용자 승인 A~D 행간 배율과 E~H 본문 10pt·전각 30칸·추가 tracking 0·왼끝맞춤을
**적용 범위가 있는 내부 초기 시안값**으로 채택했다. 조건·우선순위는 [typography-presets](typography-presets.md)에서 관리한다.
이는 실증적 보편 법칙도, 검증된 최종 디자인 최적값도 아니다. 간격의 광학적 보정은 여전히 실측 근거가 필요하다.
#5에 나오는 개인 메모 N1/N2 및 인용 문헌은 별도 원문 대조 전까지 연구 근거로 미검증이다.

**독립 검증 수준:** (1) 산술 재계산, (2) 실제 폰트/메트릭·원고 확인,
(3) 외부 도구가 반환한 적용 값, (4) 최종 크기 판독/인쇄를 구분한다.
뒤 단계가 없으면 `UNVERIFIED` 상태로 남긴다.

## 기술 참고

- [OpenType head / unitsPerEm](https://learn.microsoft.com/en-us/typography/opentype/spec/head)
- [OpenType hmtx / advance](https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx)
- [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos)
- [OpenType GPOS ValueRecord](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos#value-record)
- [HarfBuzz glyph positions](https://harfbuzz.github.io/harfbuzz-hb-buffer.html#hb-glyph-position-t)
- [HarfBuzz font scale](https://harfbuzz.github.io/harfbuzz-hb-font.html#hb-font-set-scale)
- [Adobe InDesign leading](https://helpx.adobe.com/indesign/desktop/format-and-style-text/character-formatting/adjust-line-spacing-with-leading.html)
- [PR #5 작성자의 타이포그래피 아키텍처 제안](https://github.com/makesomethingshit/visual-design-review/pull/5)
