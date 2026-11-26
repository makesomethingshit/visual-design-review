# 시각디자인 스킬 아키텍처

이 저장소는 Codex 플러그인 `visual-design` 하나와, 그 안의 스킬 셋을 배포한다. 이름은 개편 단계의 임시 이름이며 후속 개편에서 바뀔 수 있다.

## 1. 현재 구성

| 레벨 | 스킬 | 원본(사람이 편집) | 배포 사본 | 역할 |
| --- | --- | --- | --- | --- |
| 1 기획 | visual-design-planning | visual-design-planning/ | plugins/visual-design/skills/visual-design-planning/ | 의뢰 정리와 기존 자료 근거 만들기 |
| 2 시안 | visual-design-drafting | visual-design-drafting/ | plugins/visual-design/skills/visual-design-drafting/ | 기획 근거를 조형 시안과 설계 스펙으로 전환 |
| 3 리뷰 | visual-design-review | visual-design-review/ | plugins/visual-design/skills/visual-design-review/ | 완성 작품 비평, 레퍼런스 역분석, 제작 명세 검수 |

- 플러그인 manifest는 `plugins/visual-design/.codex-plugin/plugin.json`, marketplace는 `.agents/plugins/marketplace.json`이다. `plugins/` 아래 스킬은 `scripts/sync-codex-plugin.py --write`가 만드는 생성물이며 직접 편집하지 않는다.
- 전역 설치는 `scripts/install-linux.sh`, `scripts/install-windows.ps1`이 세 원본 폴더를 각각 `$CODEX_HOME/skills/<스킬 이름>`에 넣는다. 스킬마다 백업 경로가 따로 있다.
- 단계 사이의 인계는 파일과 근거 ID로 한다. 기획은 맥락 확인에서 12항목 브리프 `brief-vN.md`를 쓰고(브리프만 요청하면 여기서 멈춘다), 조사 후 `review-vN.md` 안의 `## 채택` 절 첫 줄에 기준 브리프 버전을 적은 뒤 채택 방향·필요 결과물·근거 ID·제작 제약·남은 쟁점(인계 5필드)을 남기고(별도 `handoff.md`를 만들지 않는다), 시안은 그 절을 인계서로 읽어 확정 시안과 `design-handoff` 스펙을 남기며, 리뷰는 판정과 검증 조건을 남긴다. 인계 ID(`DIR`·`DEL`·`C`·`U`)와 필드 이름은 [레벨 1 실행 기록 규칙](visual-design-planning/references/workflow/lead-state-lifecycle.md)의 '인계 기록' 절이 유일한 기준이다.
- 지식은 스킬별로 나눠 둔다. 레벨 1 방법 카드는 planning의 `references/methods/`, 레벨 2 워크플로는 drafting의 `references/workflow/`, 비평·수식·프린트 검사 지식은 review의 `references/`에 있다. 서로의 절차를 섞지 않는다.

## 2. 레벨 1 기획 아키텍처

진입점과 과제 처리 순서는 [레벨 1 실행 흐름](visual-design-planning/references/workflow/level-1.md)에 있다. 중간 조건 합의는 기록·정렬 상태이지 별도 승인 게이트가 아니며, 사용자가 명시한 최종 승인·채택만 레벨 1 종료와 인계의 사용자 결정이다. 레벨 1은 시각·표현 방향 후보를 만들지 않는다. 사람과 총괄·하위의 역할은 [아키텍처 다이어그램](docs/architecture.html)을 참고한다.

개별 방법 카드의 실제 경로는 [방법론 인덱스](visual-design-planning/references/methods/01.methods-index.md)에 있다. 다이어그램의 파일명은 예시이며 배포본에서는 분류 폴더 안의 카드를 지정한다.

새 의뢰에는 새 실행 경로를 할당한다. 다이어그램의 같은 슬롯 기록 삭제는 사용자가 정리 대상을 확인한 경우에 적용한다.

레벨 1 계약(7단계·상태·금지 범위·인계 5필드)을 실제 세션에서 대조하는 입력과 판정표는 [레벨 1 실전 평가 케이스](visual-design-planning/tests/eval-cases.md)에 있다. 세 브리프 픽스처는 모호한 브랜드 리뉴얼, 기존 자료가 있는 서비스 개선, 인쇄물 기획·인계를 다루며, E2·E3에는 표본 자료와 범위·한계를 적은 `fixtures/` 폴더가 함께 있다. `visual-design-planning/tests/test_level1_eval_contract.py`가 문서·픽스처·가이드의 정합과 실행 기록 형식만 자동 검사하고, `cases.json`의 상태는 실행 전·일부 실행·실행 완료를 모두 허용한다. 실행 품질 판정은 아직 없다.

## 3. 레벨 2 시안 아키텍처

`visual-design-drafting`은 레벨 1 인계를 받아 조형을 확정하고 비교 가능한 시안을 만든다. 실행 흐름과 단계별 계약이 있으며, 시안 품질 평가·자동 레이아웃 생성·도구별 어댑터는 아직 없다.

- 실행 흐름: [레벨 2 워크플로](visual-design-drafting/references/workflow/level-2.md) — 인계 자산 로드·정합 확인 → 조형 번역 → 복수 시안 생성·근거 매핑 → 선택·확정 및 인계.
- 실행 기록: 레벨 1 실행 폴더의 `drafts/` 아래 `10-intake.md`(인계 판정) → `20-translation.md`(조형 값·식) → `30-evidence-map.md`(근거 추적) → `40-selection.md`·`handoff-v1.md`(선택·스펙)로 남긴다. 계약 문서는 [인계 기록](visual-design-drafting/references/contracts/draft-intake.md)·[근거 매핑](visual-design-drafting/references/contracts/evidence-map.md)·[인계](visual-design-drafting/references/contracts/draft-handoff.md)이다.
- 조형 규칙: 영역별 번역 기준은 [조형 번역 기준](visual-design-drafting/references/form-translation.md)에 있고, 수식·정책은 레벨 3의 `typography-relations`·`typography-presets`를 인용한다. 레벨 2가 정책을 활성화하거나 새 수치를 승인하지 않는다.
- 근거 연결: 시안마다 레벨 1 근거 ID와 벗어난 결정·미검증 값을 `FOLLOWS`/`DEVIATES`/`NEW`/`CONFLICT`로 기록하고, 어떤 값을 어느 `DEL` 항목(품목·매체)을 위해 정했는지 함께 남긴다. 근거 없는 수치·팔레트·비율을 채우지 않는다.
- 산출물: 사용할 수 있는 도구·형식(SVG, HTML, 연결된 디자인 도구 등)이 있을 때만 실제 파일을 만들고, 없으면 만들지 못한 이유와 필요한 도구를 밝힌다.
- 인계: 확정 시안과 설계 스펙을 레벨 3(`visual-design-review`) 검수로 넘긴다. 스펙 형식은 review의 `references/design-handoff.md` 계약을 따른다.
- 미구현: 시안 품질 평가, 자동 레이아웃 생성, 도구별 어댑터. 레벨 3의 비평·심각도 판정을 레벨 2에서 대신하지 않는다.
- 검증 범위: `tests/check-drafting-contract.py`가 계약 문서의 필드·어휘·문서 예시 산술·문서 간 값 일치를 정적으로 검사한다. 실제 시안 생성과 렌더 품질, 모델의 단계 선택은 이 검사와 별개다.

## 4. 레벨 3 리뷰 아키텍처

`visual-design-review`는 완성 작품의 비평, 레퍼런스 역분석, 관계식 기반 제작 명세, 사용자가 명시한 제품 시각디자인 수정 작업을 맡는다. 진입점은 [SKILL.md](visual-design-review/SKILL.md)이고, 먼저 [knowledge-routing](visual-design-review/references/knowledge-routing.md)으로 **요청 작업 × 콘텐츠 × 매체 × 실제 입력 자료**에 필요한 references만 고른다. 레벨 1·2와 판정 절차를 공유하지 않는다.

| 작업 경로 | 필수 reference | 비고 |
| --- | --- | --- |
| 비평 (기본) | review-protocol · critique-rubric · review-output | 분야별 reference는 해당 성격이 실제로 있을 때만 |
| 레퍼런스 역분석 | reference-analysis | 수치 관계를 다루면 formula-relations |
| 계산 가능한 설계 명세 | formula-relations · design-handoff | 레벨 2가 인용하는 `design-handoff` 계약의 원본 |
| 명시적 GitHub 제품 시각디자인 수정 | product-correct | 쓰기 도구·권한이 없으면 초안만 |

- 지식 근거 해석: 작업 라우팅과 별개 축으로 [rule-contract](visual-design-review/references/rule-contract.md)가 기술 표준·조건부 권고·전문가 시지각·프로젝트 승인 정책의 효력을 구분한다. A~H 프로젝트 초기 정책은 [typography-presets](visual-design-review/references/typography-presets.md)의 활성 조건을 만족할 때만 쓴다.
- 읽기 전용 보조 스크립트: `visual-design-review/scripts/`의 스크립트는 모두 입력을 바꾸지 않고 JSON 판정을 출력한다. 잘못된 입력은 `{"status": "BLOCKED", "error": ...}`를 stderr로 내고 종료 코드 2로 끝난다.

| 스크립트 | 계약 문서 | 테스트 |
| --- | --- | --- |
| `check_pdf_preflight.py` | [pdf-preflight-contract](visual-design-review/references/pdf-preflight-contract.md) | `tests/test_pdf_preflight.py` |
| `import_pdf_preflight.py` | 같은 문서 (외부 보고서는 `UNVERIFIED`로만 가져옴) | `tests/test_import_pdf_preflight.py` |
| `finding_history.py` | [finding-trace](visual-design-review/references/finding-trace.md) | `tests/test_finding_history.py` |
| `repair_lift_summary.py` | [repair-lift-protocol](visual-design-review/tests/repair-lift-protocol.md) | `tests/test_repair_lift_summary.py`, `tests/check_repair_artifacts.py` |
| `mixed_text_probe.py` | [mixed-text-probe](visual-design-review/tests/mixed-text-probe.md) | `tests/test_mixed_text_probe.py` |
| `font_pairing_render.py` | [font-pairing-study](visual-design-review/references/font-pairing-study.md) | `tests/test_font_pairing_render.py` (로컬 글꼴 필요) |

- 사람이 판정하는 사례는 `visual-design-review/tests/*.md`, 모델 실행 원문·해시는 [평가 기록](visual-design-review/tests/evaluation/README.md)에 있다. 평가 스냅샷(`followup/`·`recheck/`·`verified/`)은 해시로 재현을 확인하는 원문이므로 정리 대상으로 고치지 않는다.
- 설계 기록: PR #5 설계는 [리뷰 설계 기록](docs/review-design-record.md), PR #6 구현 경계는 [skill-architecture-extension](docs/skill-architecture-extension.md)에 있다. 버전별 검증은 [검증 기록 색인](docs/validation/README.md)을 따른다.

## 5. 저장소 배치

| 위치 | 내용 |
| --- | --- |
| `visual-design-planning/`, `visual-design-drafting/`, `visual-design-review/` | 스킬 원본(사람이 편집) |
| `plugins/visual-design/` | `scripts/sync-codex-plugin.py --write`가 만드는 배포 사본. 직접 편집하지 않는다 |
| `scripts/` | 설치기와 플러그인 동기화 |
| `tests/` | 저장소 단위 정적 계약 검사, 스크립트 단위 테스트, 설치 스모크. 진입점은 `tests/check-knowledge-architecture.sh` |
| `docs/` | 설치 안내, 설계 기록, `validation/` 검증 기록 |
| `examples/`, `visual-fixtures.png` | 합성 입력 예시와 평가용 합성 이미지 (평가 해시가 루트 경로를 가리키므로 옮기지 않는다) |
