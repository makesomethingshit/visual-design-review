# Visual Design Review — v1.0.1

포스터·편집디자인·타이포그래피·브랜드·인포그래픽을 위한 한국어 중심의 시각디자인 비평 스킬입니다. UI/UX 감사나 디자인 생성보다 기존 작품의 관찰, 해석, 근거 있는 판정과 수정 방향을 우선합니다.

## Codex에서 사용

`visual-design-review/` 폴더를 `$CODEX_HOME/skills/`에 복사하세요. CODEX_HOME이 없으면 사용자 홈의 `.codex/skills/`를 사용합니다. 기존 동명 폴더는 먼저 비교·백업하세요. 프로젝트 지침을 수정하거나 의존성을 설치할 필요가 없습니다.

새 Codex 세션에서 다음처럼 호출합니다.

```text
$visual-design-review 이 포스터를 빡세게 리뷰해줘.
```

기본 Quick Review, 정밀·빡세게 요청 시 Deep Review입니다. Deep 아홉 항목은 권장 구성이며, 근거·영향·의도/반대 해석·조치·검증을 보존하면 통합해서 쓸 수 있습니다. 기본 언어는 한국어이며, 이미지를 확인하지 못하면 시각 관찰을 만들지 않습니다. 리뷰는 읽기 전용입니다. 명시적인 수정 요청 없이 파일을 생성·수정하거나 작품을 외부에 업로드하지 않습니다.

## 일반 Chat에서 함께 리뷰

일반 Chat이 Codex 스킬을 자동 설치·활성화하는 것은 아닙니다. 이 저장소의 [SKILL.md](visual-design-review/SKILL.md)를 읽도록 요청하고 작품을 별도로 제공하세요. 저장소 접근이 어려우면 아래 문서와 필요한 references를 직접 첨부하세요.

```text
이 저장소의 visual-design-review/SKILL.md와 작품에 필요한 references만 읽고 적용해줘.
첨부 작품을 한국어 Deep Review로 비평해줘. 관찰·해석·판정을 분리하고,
의도된 규칙 위반을 자동 결함으로 보지 마. 제작 속성은 확인한 범위만 판단해줘.
파일을 수정하거나 외부에 업로드하지 마.
```

## 구성과 근거

- 단일 [SKILL.md](visual-design-review/SKILL.md)
- 선택적으로 읽는 references 8개
- [A~E 회귀 기준](visual-design-review/tests/review-cases.md) 및 [A~J 비교·반복·라우팅 평가 원문](visual-design-review/tests/evaluation/README.md)
- [SHA 고정 출처·라이선스·통합 결정](visual-design-review/references/sources.md)
- [검증 보고서](VALIDATION.md)

원본 파일·문구를 합쳐 배포하지 않고 일반 방법론을 독자적으로 재작성했습니다. 라이선스가 없는 소스는 일반적인 개념만 참고했습니다. 원본 자산·제3자 데이터·사용자 작품의 권한은 포함하지 않습니다.

v1.0.1은 내용 계약·관찰 범위·심각도 판단을 보강한 후보입니다. 비교 원문에서 발견된 실패와 계정 한도로 남은 반복·활성화 검증을 VALIDATION.md에 명시했습니다. 전체 행동 합격이나 이전 버전 대비 개선을 보증하지 않습니다.
