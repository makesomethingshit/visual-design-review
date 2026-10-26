# Visual Design Review — v1.0.1

포스터·편집디자인·타이포그래피·브랜드·인포그래픽을 위한 한국어 중심의 시각디자인 비평 스킬입니다. UI/UX 감사나 디자인 생성보다 기존 작품의 관찰, 해석, 근거 있는 판정과 수정 방향을 우선합니다.

## Codex 플러그인으로 설치

GitHub marketplace 소스로 이 저장소를 추가하고 플러그인 목록에서 **Visual Design Review**를 설치·활성화할 수 있습니다.

~~~bash
codex plugin marketplace add makesomethingshit/visual-design-review
codex plugin marketplace list
~~~

이는 **마켓플레이스 등록** 명령이며 실제 클라이언트 설치·자동 선택 검증을 뜻하지 않습니다. [플러그인 배포·동기화 가이드](docs/CODEX-PLUGIN.md)를 참고하세요. 기존 전역 스킬 설치 방식도 그대로 유지합니다.

## Codex에서 사용

Windows 네이티브와 macOS/WSL/Linux의 설치·업데이트·검증·백업·제거 절차는 [전역 설치 가이드](docs/INSTALL.md)를 따릅니다. 설치 전에 dry-run으로 변경 범위를 확인하고, 설치 후 원본과 설치본의 파일 목록·SHA-256을 검증할 수 있습니다. CODEX_HOME이 없다면 현재 실행 환경의 사용자 홈에 있는 `.codex/skills/`를 사용합니다. 프로젝트 지침을 수정하거나 새 의존성을 설치하지 않습니다.

```powershell
# Windows PowerShell
.\scripts\install-windows.ps1 -Action install -DryRun
.\scripts\install-windows.ps1 -Action install
.\scripts\install-windows.ps1 -Action check
```

```bash
# macOS / WSL / Linux
bash scripts/install-linux.sh install --dry-run
bash scripts/install-linux.sh install
bash scripts/install-linux.sh check
```

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

## GitHub 제품 개선: Product Correct (초안)

디자인 Finding을 **증거가 있는 제품 개선 Issue → 실제 수정이 가능한 경우 Draft PR**로 잇는 선택적 작업 경로를 설계 중입니다. [Product Correct 계약](visual-design-review/references/product-correct.md)을 따르며, 일반 비평만 요청하면 GitHub에 아무것도 쓰지 않습니다.

```text
$visual-design-review 이 제품 저장소(owner/repo)의 반복된 시각디자인 결함을
실제 기존 이슈/PR 리뷰와 디자인 근거로 조사하고, 관련 GitHub Issue를 등록해줘.
수정 가능한 최소 범위라면 Draft PR까지 작성하되 머지하지 마.
```

원본·브리프·재현 및 대상 저장소 접근 권한이 필요합니다. 스킬 자체가 GitHub 연결이나 제품 편집 도구를 제공하지는 않습니다. 확인하지 못한 결함/수정/CI 성공을 확정하지 않고, [수동 행동 시나리오](visual-design-review/tests/product-correct-cases.md)로 실제 동작을 별도 평가합니다. 이 기능은 [에이전트 자체 교정 #7](https://github.com/makesomethingshit/visual-design-review/issues/7)과 책임이 다릅니다.

## 구성과 근거

- 단일 [SKILL.md](visual-design-review/SKILL.md)
- 작업에 따라 선택적으로 읽는 분야별·정량 설계 references
- [A~E 회귀 기준](visual-design-review/tests/review-cases.md) 및 [A~J 비교·반복·라우팅 평가 원문](visual-design-review/tests/evaluation/README.md)
- [SHA 고정 출처·라이선스·통합 결정](visual-design-review/references/sources.md)
- [검증 보고서](VALIDATION.md)

원본 파일·문구를 합쳐 배포하지 않고 일반 방법론을 독자적으로 재작성했습니다. 라이선스가 없는 소스는 일반적인 개념만 참고했습니다. 원본 자산·제3자 데이터·사용자 작품의 권한은 포함하지 않습니다.

v1.0.1은 내용 계약·관찰 범위·심각도 판단을 보강했습니다. [F1–F3 후속 검증](visual-design-review/tests/evaluation/FOLLOWUP.md)에서 C/J/F/G를 각 2회 재실행하고 실제 Codex 라우팅 12회(명시·자연어 호출 및 CSS·UI·코드 리뷰 비활성)를 완료했습니다. 중간 실패와 정확한 심각도 반복 차이 등 남은 한계도 공개하며, 모든 품질 항목 합격이나 이전 버전 대비 일반적 우월성을 보증하지 않습니다.

## 개발 중: 정량적 레퍼런스 역분석과 디자인 지식 구조 (#2)

이 문서의 v1.0.1 기능 설명과 검증 범위는 기존 Review 기준입니다. 아키텍처 리팩터링
초안에서는 모드별 references 선택, 이미지/편집 원본의 조형 관계에 대한 증거 기반 역분석,
수식의 출처·적용 조건 관리 및 외부 디자인 플러그인 전달 계약을 추가로 제안합니다.
자동 이미지 분해·솔버·Adobe/Penpot/Figma 어댑터를 구현했다고 주장하지 않습니다.
초기 본문 조판에는 사용자가 승인한 [A~H 프로젝트 조건부 시작값](visual-design-review/references/typography-presets.md)을 사용할 수 있지만,
이는 모든 서체·매체에 성립하는 가독성 법칙이나 최종 디자인 최적값이 아닙니다.
자세한 책임 경계 및 아직 검증하지 않은 항목은 [스킬 확장 설계](docs/skill-architecture-extension.md)와 [PR #5의 기반 아키텍처](https://github.com/makesomethingshit/visual-design-review/pull/5)를 참조하세요.
