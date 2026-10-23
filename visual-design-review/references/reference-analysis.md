# Reference analysis — 정량적 조형 역분석 계약

**목적:** 완성된 디자인으로부터 객체·위치·계층·관계의 **관측값**과 이를 설명하는
**경쟁 가능한 조형 모델**을 구별한다. 도구별 이미지 해체/벡터화·렌더링 엔진을 구현하는
문서가 아니며, 분석을 수행하지 않은 값을 측정했다고 주장하지 않는다.

## 1. 입력과 관측의 경계

- 자료 형식(편집 원본/텍스트·벡터 PDF/래스터 이미지/사진·스캔)과 실제로 연
  페이지·영역, 측정 방법, 원점/좌표축, frame 크기·단위·크롭·변환을 기록한다.
- px는 화면 픽셀이다. mm·pt로 환산하려면 원본 문서 치수 또는 신뢰 가능한 배치 스케일이
  있어야 한다. 안티앨리어싱·왜곡·가려짐·렌더링 차이로 발생하는 불확실성을 숨기지 않는다.
- 원본 편집 객체의 직접 조회(**VERIFIED_SOURCE**), 이미지 픽셀 실측(**MEASURED_RASTER**),
  흐린 경계의 근사(**ESTIMATED**), 가설 모델(**INFERRED_MODEL**), 확인 안 함(**UNVERIFIED**)을
  분리한다. 이들은 원저자의 의도·제작 순서를 확정하는 신뢰도 등급이 아니다.

## 2. 최소 분석 표현: Frame → Object → Relation → Hypothesis

| 레코드 | 필수 내용 | 미지원일 때 |
| --- | --- | --- |
| **Frame** | id, width/height, origin, unit, axis direction, crop/transform | 정규화 불가 표시 |
| **Object** | id, type(text/image/shape/path), bbox(x,y,w,h), frame_id, evidence_status | 미측정 필드는 unknown |
| **Structure** | id, 그룹/포함/겹침/층 관계, 관측 근거 | 레이어 순서 유추로 표시 |
| **Relation** | id, 대상 object_ids, 종류(정렬/간격/비율/위계), 식·관측값·조건 | 관계 가설로 표시 |
| **Hypothesis** | id, 적용 대상, 모델 변수 θ, 관계·제약, 경쟁 모델, 상태 | 원저자 의도 미확정 |
| **Reconstruction** | 사용한 θ, 입력/렌더링 조건, 실제 수행 여부, 차원별 잔차 | UNVERIFIED |

서로 다른 객체·관계·가설은 **ID로 추적**한다. 임의로 문서 원본의 레이어·폰트·그리드 설정을
채워 넣지 않는다. 단순히 배치가 유사하다는 이유로 그 제작 시스템이 실제 사용됐다고 단정하지 않는다.

## 3. 직접 계산 가능한 관측 관계

단위와 좌표계를 일치시킨 뒤에만 다음 식을 적용한다.

| 종류 | 관계 정의 | 적용 전제 |
| --- | --- | --- |
| 정규화 위치 | `x_norm=(x-frame_x0)/W`, `y_norm=(y-frame_y0)/H` | W,H가 유효하고 좌표계 일치 |
| 정규화 크기 | `w_norm=w/W`, `h_norm=h/H` | bbox와 frame 같은 단위 |
| 정렬 잔차 | `a_ij=x_i-x_j` 또는 `baseline_i-baseline_j` | 실제 비교할 기준선이 동일 |
| 수평 간격 | `g_ij=x_j-(x_i+w_i)` | 같은 frame의 x방향 bbox, 회전 보정 확인 |
| 크기비 | `r_ij=w_i/w_j` | 분모 ≠ 0, 같은 종류/의미가 있는 비교 |
| 반복 피치 | `p=median(x_(i+1)-x_i)` | 관측된 반복축 3개 이상, 순서 명시 |

피치의 개별 차분과 잔차 `(x_(i+1)-x_i)-p`를 함께 남긴다.
bbox가 일치해도 실제 곡선 윤곽/광학 중심이 일치하는 것은 아니다.
행간과 글리프 비교는 [typography-relations](typography-relations.md)의
실제 서체·원고·셰이핑 조건을 추가로 요구한다.

## 4. 경쟁 모델 및 오차 검증

관찰 `O`를 설명하는 모델 `H(θ)`가 여러 개 있으면 모두 후보로 기록한다.
재구성/실측을 **실제로 완료한 경우에만** 각 항목을 원본과 동일한
좌표계·대응 객체·크롭·렌더링 조건으로 비교한다.

| 차원 | 비교값 예시 | 비교 불가 조건 |
| --- | --- | --- |
| Geometry | `e_x=abs(x_pred-x_obs)/W`, `e_w=abs(w_pred-w_obs)/W` | 대응 객체·frame 누락 |
| Alignment/Spacing | `abs(g_pred-g_obs)`, `abs(a_pred-a_obs)` | 축·좌표 기준 불일치 |
| Structure | 객체 누락·추가 수, 계층/그룹/가림 불일치 목록 | 원래 구조 확인 불가 |
| Typography | 문자열·실제 줄바꿈·baseline·glyph advance 차이 | 동일 원고·폰트 엔진 미확인 |
| Color | 선언한 색 공간/프로파일에서의 색차 | 비교 프로파일 불명 |
| Raster | 정렬/크롭/크기가 고정된 이미지 차이 | 재렌더링 미실행 |
| Transfer | 다른 판형/원고로 이전 후 제약 충족 여부 | 이전 실험 미실시 |

**오차는 차원별·객체별 값으로 우선 기록**한다. 임의 가중치를 만들어 한 개의 미적
점수로 합치거나, 가장 작은 일부 오차만 보여 다른 결함을 숨기지 않는다.
지각적 유사도와 원본의 실제 저작 프로세스 복원은 전혀 다른 주장이다.
사용자 기준으로 허용 편차가 없으면 통과/실패 임계값을 자의적으로 설정하지 않는다.

## 5. 합성 분석 사례 (실측이 아님)

아래 표가 합성 사례의 입력과 기대 결과를 함께 담는다. 좌표·피치·원점의 단위는 px이며,
정규화 값과 잔차는 무차원이다. 정규화는 `x/W`, 차분은 인접 좌표의 차,
피치 후보는 차분의 중앙값, 잔차는 `abs(origin+model_pitch*i-x_i)/W`로 계산한다.
`i`는 0부터 시작한다. 정적 검사는 표의 값을 직접 읽어 이 관계를 재계산한다.

| ID | frame_width_px | observed_x_px | normalized_x | adjacent_deltas_px | pitch_px | model_origin_px | model_pitch_px | normalized_residuals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RA-1 | 1200 | 120,420,720 | 0.10,0.35,0.60 | 300,300 | 300 | 120 | 300 | 0,0,0 |

RA-1의 반복 피치 모델은 관측 좌표의 잔차 0으로 설명된다.
하지만 같은 좌표를 **서로 독립적으로 지정한 모델**도 잔차 0을 만든다.
그러므로 원작자가 반복 격자를 사용했다는 사실은 이 자료만으로 입증되지 않는다.

이 예시는 *산술만 재현*하며, 실제 편집 원본 분석·폰트 복원·재렌더링을 완료했다는
증거가 아니다.

## 6. 최소 전달 결과와 외부 책임

**입력 근거 → 객체 관측 → 관계 정의 → 경쟁 가설 → 재구성 조건/항목별 오차 또는
UNVERIFIED → 새로운 매체에 옮길 때 필요한 파라미터·검증 사항**을 순서대로 남긴다.

도구 플러그인이 객관적인 측정값 또는 렌더 결과를 반환하면 확인된 범위에 한해
관계를 검토한다. 이 스킬은 이미지 분리기·도구 어댑터·솔버·조회 엔진을 자체 구현하지 않는다.

## 7. 참고 연구 (코드·데이터 복제 없음)

- [LayerD (ICCV 2025)](https://openaccess.thecvf.com/content/ICCV2025/papers/Suzuki_LayerD_Decomposing_Raster_Graphic_Designs_into_Layers_ICCV_2025_paper.pdf) — 래스터 레이어 분해와 비유일성
- [ReDesign (2026)](https://arxiv.org/html/2607.25565) — 계층형 편집 디자인 복원
- [Vector Layout Transfer (2023)](https://arxiv.org/html/2309.11635v1) — 공간 관계의 이전
- [Re-typograph (2015)](https://doi.org/10.1117/12.2075813) — 서체 파라미터의 역추정 한계
- [Reverse-engineering information presentations (2023)](https://link.springer.com/article/10.1007/s44267-023-00010-1) — 시각적 그룹 관계 추론
