---
name: visual-design-drafting
description: >
  Level 2 visual design drafting. Use to turn a level 1 planning handoff into
  layout, type and color drafts, produce comparable A/B draft artifacts, and
  record which planning evidence each draft follows.
  시안 제작, 레벨 2 시안, 디자인 초안, 시안 A/B 비교, 기획 근거에서 시안 만들기,
  확정 시안과 제작 스펙 정리에 사용한다. 완성 작품의 비평과 검수는 visual-design-review가 맡는다.
metadata:
  version: "0.2.0"
---

# 시각디자인 시안 · 레벨 2

[레벨 2 실행 흐름](references/workflow/level-2.md)을 열고 진행한다. 레벨 1(`visual-design-planning`)이 남긴 인계 자산을 입력으로 받아 실제 시안과 설계 스펙을 만들고, 사람이 고른 시안을 레벨 3(`visual-design-review`) 검수로 넘긴다.

## 실행 순서

1. **인계 자산 로드 & 정합 확인** — `review-vN.md`의 채택 방향·필요 결과물·근거 ID·제약·미결을 `evidence-index.md`·`lead-state.md`와 대조해 `10-intake.md`에 옮기고, `필요 결과물`(`DEL-xx`)을 시안 트랙(`draft-a/`, `draft-b/`)에 매핑한 뒤 `READY`/`PARTIAL`/`DIRECT`/`BLOCKED`를 판정한다. 형식은 [인계 기록 계약](references/contracts/draft-intake.md).
2. **조형 번역 & 시안 설계 스펙** — 근거를 그리드·타이포 위계·혼식·컬러·자산·레퍼런스 재사용으로 옮겨 `20-translation.md`에 값·단위·식·출처 상태로 적는다. 영역별 기준은 [조형 번역 기준](references/form-translation.md).
3. **복수 시안 생성 & 근거 매핑** — 같은 원고·판형·자산으로 차이 축이 다른 A/B(필요 시 C)를 실제 파일로 만들고, 값마다 근거 ID를 `30-evidence-map.md`에 연결한다. 형식은 [근거 매핑 계약](references/contracts/evidence-map.md).
4. **선택·수정 루프 & 레벨 3 인계** — 사람의 선택과 수정을 `40-selection.md`에 기록하고, 확정 시안을 `design-handoff` 형식의 `handoff-v1.md`로 닫아 체크리스트를 통과시킨 뒤 넘긴다. 형식은 [인계 계약](references/contracts/draft-handoff.md).

## 지키는 것

- 직접 들어온 브리프라면 인계 자산 대신 최소 맥락(목적·대상·매체·콘텐츠·제약)만 확인하고 시작한다. 확인한 것과 가정한 것을 구분해 기록하고, 레벨 1의 조사를 대신하지 않는다.
- 시안은 비교 가능한 실제 산출물로 만든다. 사용할 수 있는 도구·파일 형식이 없으면 만들었다고 말하지 않고, 필요한 도구와 형식을 밝힌다.
- 레벨 1의 근거 ID와 제약을 벗어난 조형 결정은 발명하지 않는다. 근거 없이 새로 정한 값은 `NEW`·가정·후보로 표시하고, 사람이 고르기 전에는 `DETERMINED`로 올리지 않는다.
- 인계받은 `필요 결과물`(`DEL-xx`)을 다시 매기거나 늘리지 않는다. 모든 `DEL` 항목이 시안·스펙의 어느 파일에 대응하는지 남기고, 빠진 품목은 이유와 함께 보고한다.
- 행간·줄 길이·폭 같은 수치는 레벨 3의 수식·정책 문서를 인용해 계산하되, 레벨 2가 정책을 활성화하거나 새 규칙을 승인하지 않는다. 활성 근거가 없으면 미결로 남긴다.
- 채택·보완·반려는 사람이 결정한다. 확정 전 시안을 최종안으로 부르지 않고, 시안의 미적 우열을 점수로 매기지 않는다.

완성 작품의 비평·역분석은 `visual-design-review`, 조사·기획은 `visual-design-planning`의 범위다. 같은 플러그인에 함께 배포되지만 판정 절차는 서로 섞지 않는다.
