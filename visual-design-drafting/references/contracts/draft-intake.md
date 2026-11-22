# 인계 기록 계약 (`10-intake.md`)

레벨 1 인계에서 레벨 2로 넘어오는 값을 한 파일에 고정하는 형식이다. 이 파일이 없으면 이후 단계의 근거 ID·제약·미결이 흩어지고, 시안 값의 출처를 사후에 꾸미게 된다. 형식은 YAML에 가까운 목록과 표 중 읽기 쉬운 것을 쓰되, 아래 필드가 빠지면 안 된다.

## 필드

| 필드 | 내용 | 필수 |
| --- | --- | --- |
| `run` | 실행 폴더 절대 경로 | 필수 |
| `project` | 작업 이름 한 줄 | 필수 |
| `handoff_status` | `READY` / `PARTIAL` / `DIRECT` / `BLOCKED`와 이유 한 줄 | 필수 |
| `level1_run` | 레벨 1 실행 폴더와 `source_review` 파일명·버전 | `READY`·`PARTIAL`에서 필수 |
| `id_origin` | 인계 ID의 부여 주체: `LEVEL1`(채택 절) / `LEVEL2_NORMALIZED`(레벨 2가 로드 시 부여) / `DIRECT` | 필수 |
| `decision` | 사람이 채택한 시점, 채택자, 반려된 안과 사유 | 필수 |
| `question` | 시안이 답해야 할 질문(리뷰 첫 문단에서 옮김) | 필수 |
| `scope_limit` | 판단을 바꿀 한계, 시안이 다루지 않는 범위 | 필수 |
| `adopted` | 채택 방향: `DIR` ID, 이름, 요약, 근거 ID 목록 | 필수(방향이 있으면) |
| `constraints` | 제작 제약: `C` ID, 항목, 값·단위, `origin`, 출처 위치 | 필수 |
| `evidence` | 근거: `EV` ID, 주장, 원문 위치, 근거 수준, 한계·예외 | 필수(`DIRECT`는 빈 목록 허용) |
| `unresolved` | 남은 쟁점: `U` ID, 쟁점, 결정 주체, 시안에 미치는 영향 | 필수 |
| `gaps` | 공백과 처리: `ASSUMED` / `ASKED` / `DEFERRED`와 근거 | 필수 |
| `assumptions` | 시안에 쓰기로 한 가정과 그것이 바뀌면 달라지는 것 | `PARTIAL`·`DIRECT`에서 필수 |
| `checks` | 정합 확인 항목별 결과(아래 형식) | 필수 |

`adopted`·`constraints`·`unresolved`의 필드 이름과 순서는 레벨 1 채택 절의 인계 4필드(채택 방향·근거 ID·제작 제약·남은 쟁점)를 그대로 옮긴 것이다. 다른 이름을 새로 만들지 않는다.

## 인계 ID 규칙

| ID | 대상 | 부여 시점 |
| --- | --- | --- |
| `DIR-01` | 방향 후보(채택·반려 포함) | 레벨 1 채택 절. 사람이 고른 후보도 자기 ID를 유지한다 |
| `EV-01` | 근거 | 레벨 1 `evidence-index.md` |
| `C-01` | 제작 제약 | 레벨 1 채택 절 |
| `U-01` | 남은 쟁점 | 레벨 1 채택 절 |

- 두 자리 번호를 쓴다(`DIR-1`이 아니라 `DIR-01`). 리뷰 파일 안에서 유일하면 되고, 다음 리뷰 버전에서 이어 쓴다.
- 레벨 1이 부여한 ID를 표기 그대로 쓰고, 번호를 다시 매기거나 문서에 없는 ID를 만들지 않는다. `id_origin: LEVEL1`이 그 상태다.
- 채택 절은 있는데 ID가 없는 인계(이전 버전 리뷰 등)라면 레벨 2가 읽은 순서대로 부여하고 `id_origin: LEVEL2_NORMALIZED`로 적는다. 이때도 근거 ID(`EV`)는 새로 만들지 않고 `NO-EVIDENCE`로 둔다.
- `evidence`의 ID는 레벨 1 `evidence-index.md`의 ID를 그대로 쓴다. 리뷰에 ID 없이 적힌 주장은 원문 위치로 찾아 연결하고, 없으면 `NO-EVIDENCE`로 둔다.

## 정합 확인 기록 형식

항목마다 결과 하나와 근거 위치를 적는다.

| 항목 | 결과 | 근거 위치·비고 |
| --- | --- | --- |
| 판형·매체·마감 | `OK` | `review-v2.md#채택-제약`, C-01 |
| 실제 원고 | `ASSUMED` | 원고 미제공. 예시 원고 320자, `EXAMPLE-COPY` |
| 자산 | `CONFLICT` | 로고는 있으나 사용 범위 미확인 → U-02 |

| 결과 | 뜻 |
| --- | --- |
| `OK` | 인계 문서와 실제 자료로 확인됨 |
| `ASKED` | 사람에게 물었고 답을 받음 (답을 함께 적음) |
| `ASSUMED` | 답이 없어 가정으로 진행 (가정을 `assumptions`에 등록) |
| `CONFLICT` | 확인된 값끼리 충돌 (우선순위는 사람이 정함) |
| `BLOCKED` | 구조를 정할 수 없어 진행 정지 |

확인하지 않은 항목을 `OK`로 적지 않는다. 문서에 없다는 사실은 확인이 아니다.

## 예시 (합성)

아래 값은 형식을 보여 주기 위한 합성 예시이며 실제 작품의 인계 기록이 아니다.

```yaml
run: /work/exhibition-01/runs/exhibition-01/drafts
project: 전시 안내물 (A2 포스터 + 3단 리플릿)
handoff_status: PARTIAL - 안내문 원고 미확정, 판형·위계 근거는 확보
level1_run: /work/exhibition-01/runs/exhibition-01
source_review: review-v2.md
id_origin: LEVEL1
decision: {adopted_at: "2026-11-20", by: USER, rejected: [DIR-02 "정보 과밀, 1차 대상 아님"]}
question: 관람객이 입구에서 열린 전시와 시간을 먼저 찾게 할 것
scope_limit: 야외 사이니지·디지털 화면은 범위 밖
adopted:
  - id: DIR-01
    name: 시간 우선형
    summary: 관람 시간과 현재 열린 전시를 첫 층위로, 위치·요금을 둘째 층위로
    evidence: [EV-04, EV-07, EV-11]
constraints:
  - {id: C-01, item: 포스터 판형, value: "420x594", unit: mm, origin: USER, source: "review-v2.md#채택-제약"}
  - {id: C-02, item: 필수 문구, value: "기관명·후원 로고·접근성 안내", origin: USER, source: "brief"}
  - {id: C-03, item: 리플릿 판형·단 수, value: "148x210, 3단", unit: mm, origin: USER, source: "review-v2.md#채택-제약"}
  - {id: C-04, item: 리플릿 여백·거터, value: "12/12/5", unit: mm, origin: USER, source: "review-v2.md#채택-제약"}
evidence:
  - {id: EV-04, claim: 문의의 62%가 운영 시간, source_locator: "review-v2.md#표1", level: 기존 문의 기록, limit: 표본 1개월}
  - {id: EV-07, claim: 입구에서 3초 안에 시간을 찾지 못함, source_locator: "review-v2.md#관찰", level: 관찰 기록, limit: 관찰자 1명}
unresolved:
  - {id: U-01, issue: 안내문 원고 최종본, decider: USER, effect_on_draft: 본문 줄 수·수용량 미확정}
  - {id: U-02, issue: 후원 로고 사용 범위, decider: USER, effect_on_draft: 하단 띠 배치 후보만 가능}
gaps:
  - {missing: 실제 원고, handling: "ASSUMED(예시 원고)", basis: "U-01 결정 전 비교용"}
  - {missing: 인쇄 후 관람 거리, handling: DEFERRED, basis: "설치 위치 미확정"}
assumptions:
  - {what: 본문 320자 내외, basis: 예시 원고, if_changed: 단 수·줄 수 재계산}
checks:
  - {item: 판형·매체, result: OK, note: C-01}
  - {item: 실제 원고, result: ASSUMED, note: 예시 원고}
  - {item: 자산, result: CONFLICT, note: U-02}
```

## 직접 브리프로 시작한 경우

레벨 1 인계가 없으면 같은 파일을 `handoff_status: DIRECT`로 쓰고 다음만 채운다.

- `question`: 이 시안이 답해야 할 질문 한 문장. 브리프에 없으면 사람에게 묻는다.
- `constraints`: 브리프에 적힌 고정값(판형·매체·필수 문구·브랜드 자산). 이미 적혀 있는 것을 다시 묻지 않는다.
- `evidence: []`와 `assumptions`: 근거가 없다는 사실과, 대신 쓴 가정.
- `scope_limit`: 레벨 2가 조사하지 않은 범위(대상 조사·경쟁 작품 분석 등).

`DIRECT` 기록에 레벨 1 근거 ID를 만들어 넣지 않는다. 조사가 필요해 보이면 레벨 1(`visual-design-planning`)로 넘길지 사람에게 묻고, 레벨 2가 대신 조사하지 않는다.

## 이 파일에서 하지 않는 일

- 리뷰 전문을 복사하지 않는다. 시안 결정에 쓰는 문장과 근거 위치만 옮긴다.
- 레벨 1의 결론을 다시 판정하지 않는다. 동의하지 않는 항목은 `unresolved`에 이유와 함께 올린다.
- 미결을 채우기 위해 새 자료를 조사하지 않는다. 필요한 조사는 레벨 1의 일이다.
