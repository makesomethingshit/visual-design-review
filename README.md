# Visual Design — 레벨 1 기획 · 레벨 2 시안 · 레벨 3 리뷰

시각디자인 작업을 세 단계로 나눈 Codex 플러그인 `visual-design`입니다. 한 플러그인 안에 스킬 셋이 들어 있고, 앞 단계의 결과물이 다음 단계의 입력이 됩니다.

| 레벨 | 스킬 | 역할 | 다음 단계로 넘기는 것 |
| --- | --- | --- | --- |
| 1 기획 | [visual-design-planning](visual-design-planning/SKILL.md) | 의뢰를 디자인 브리프로 정리하고 기존 자료로 판단 근거를 만든다 | `brief-vN.md` 브리프, HTML 검토 보고서 `review-vN.html`(문제 정의·방법별 그림·인사이트·재정의·디자인 원칙과 방향·각주)의 채택 절에 채택 방향·필요 결과물·근거 ID·제작 제약·남은 쟁점 |
| 2 시안 | [visual-design-drafting](visual-design-drafting/SKILL.md) | 기획 근거를 조형으로 옮겨 비교 가능한 시안 A/B와 설계 스펙을 만든다 | 확정 시안 산출물과 `design-handoff` 스펙 |
| 3 리뷰 | [visual-design-review](visual-design-review/SKILL.md) | 완성 작품을 비평하고, 레퍼런스를 역분석하고, 제작 명세를 검수한다 | 판정·근거·검증 조건 |

~~~text
$visual-design-planning 새 전시 안내물의 정보 구조를 정하려고 해. 첨부한 관람객 문의 기록으로 반복되는 문제와 그 근거를 정리해줘.
$visual-design-drafting 레벨 1 인계 자산으로 A/B 시안 두 개를 만들어줘.
$visual-design-review 이 포스터의 구성과 타이포그래피를 리뷰해줘.
~~~

- 레벨 1은 결과를 바꾸는 정성 질문을 한 번에 하나씩 확인해 12항목 브리프(`brief-vN.md`)로 저장하고, 치수·형식·제작·접근성 같은 정량 조건은 공개 웹과 사용이 허용된 제공 자료의 **기존 기록**으로 확인합니다. 중간 조건 합의는 별도 승인 장벽이 아니며, 사용자가 명시한 최종 승인·채택만 종료·인계의 사용자 결정입니다. 브리프만 요청하면 브리프를 넘기고 멈춥니다. 채택 방향은 과제 방향(풀 문제·우선 대상·우선순위·정보 단위와 순서)이며, 시각·표현 방향 후보, 새 인터뷰·설문·현장조사, 시제품·실험, 시각 평가와 제작은 레벨 1에서 만들지 않습니다.
- 레벨 2는 실행 흐름과 단계별 계약(인계 기록·조형 번역·근거 매핑·인계)까지 있습니다. 시안 품질 평가와 도구별 어댑터는 아직 없습니다.
- 레벨 1의 방법 카드는 `visual-design-planning/references/methods/`에, 레벨 2 워크플로는 `visual-design-drafting/references/workflow/`, 레벨 3의 비평·수식·검증 지식은 `visual-design-review/references/`에 있습니다. 구조는 [ARCHITECTURE.md](ARCHITECTURE.md), 레벨 1 방법 카드 그림은 [아키텍처 다이어그램](docs/architecture.html)을 참고합니다.

## 설치와 검증

[Codex 플러그인 설치](docs/CODEX-PLUGIN.md) 또는 [전역 스킬 설치](docs/INSTALL.md) 절차를 따릅니다. 전역 설치는 세 스킬을 각각 `$CODEX_HOME/skills/<스킬 이름>`에 넣고, 호출 이름은 `visual-design-planning`, `visual-design-drafting`, `visual-design-review`입니다.

원본은 루트의 스킬 폴더이고 `plugins/visual-design/skills/` 아래 사본은 생성물입니다. 원본을 편집한 뒤 다음을 실행합니다.

~~~bash
python scripts/sync-codex-plugin.py --write
python scripts/sync-codex-plugin.py --check
bash tests/smoke-install-linux.sh
bash tests/check-knowledge-architecture.sh
~~~

이전 리뷰 버전의 설계·검증 기록은 [PR #5 리뷰 설계 기록](docs/review-design-record.md), [PR #6 구현 경계](docs/skill-architecture-extension.md), [검증 기록 색인](docs/validation/README.md)에 있으며, 각 버전의 범위에 해당합니다.
