# Visual Design Planning

시각디자인 의뢰에서 무엇을 확인해야 하는지 정리하고 기존 자료로 판단 근거를 만드는 레벨 1 기획 스킬입니다. 총괄이 과제와 기대 출력을 정리하면 하위 에이전트가 방법론에 따라 분석합니다. 디자이너가 근거를 보고 방향을 결정합니다.

~~~text
$visual-design-review 새 전시 안내물의 정보 구조를 정하려고 해. 첨부한 관람객 문의 기록으로 반복되는 문제와 그 근거를 정리해줘.
~~~

[스킬 진입점](visual-design-review/SKILL.md) · [실행 흐름](visual-design-review/references/workflow/level-1.md) · [방법론 인덱스](visual-design-review/references/methods/01.methods-index.md) · [아키텍처 다이어그램](docs/architecture.html)

공개 웹과 사용이 허용된 제공 자료의 기존 기록을 활용합니다. 새 인터뷰·설문·현장조사, 시제품·실험, 시각 평가와 제작은 별도 단계입니다.

## 설치와 검증

[Codex 플러그인 설치](docs/CODEX-PLUGIN.md) 또는 [전역 스킬 설치](docs/INSTALL.md) 절차를 따릅니다. 호출 이름은 `visual-design-review`입니다. 원본을 편집한 뒤 `python scripts/sync-codex-plugin.py --write`로 플러그인 사본을 갱신하고 `--check`로 확인합니다.

이전 리뷰 버전의 [설계 기록](docs/skill-architecture-extension.md)과 [검증 기록](VALIDATION.md)은 각 버전의 범위에 해당합니다.
