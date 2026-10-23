# Codex 플러그인 배포

> [Issue #29](https://github.com/makesomethingshit/visual-design-review/issues/29) — 이 저장소는 로컬/저장소 GitHub marketplace에서 설치할 수 있는 Codex 플러그인 **배포 소스**를 제공한다. OpenAI의 범용 Plugins Directory에 등록된 것은 아니다.

## 무엇이 설치되는가

- Marketplace: .agents/plugins/marketplace.json
- Plugin manifest: plugins/visual-design-review/.codex-plugin/plugin.json
- 설치용 스킬: plugins/visual-design-review/skills/visual-design-review/SKILL.md
- 스킬에 필요한 references 및 (존재하는 경우) scripts/assets
- **visual-design-review/**만 사람이 편집하는 단일 원본이다. plugins 내부의 스킬은 생성된 배포 사본으로 직접 편집하지 않는다.
- visual-design-review/tests의 평가 로그와 테스트 자료는 배포에 포함하지 않는다.

## 소스 등록 및 설치 (지원되는 클라이언트)

~~~bash
codex plugin marketplace add makesomethingshit/visual-design-review
codex plugin marketplace list
~~~

이 명령은 **마켓플레이스 소스 등록**이다. 지원되는 ChatGPT 데스크톱/Codex의 Plugins 화면에서 Makesomethingshit Design → Visual Design Review를 설치·활성화한다. 소스 등록만으로 설치·자동 스킬 선택까지 성공했다고 주장할 수 없다.

새 Codex 세션에서 시각디자인 포스터 리뷰를 자연어로 요청하여 실제 스킬 선택 및 필요한 reference의 열람을 확인한다. CSS 코드 리뷰·일반 소프트웨어 결함 분석처럼 대상 밖인 요청에서는 스킬이 잘못 선택되지 않아야 한다. 사용한 파일명만 대답에 등장하는 것을 실제 열람 증거로 해석하지 않는다.

플러그인에는 별도 MCP 서버·로그인·GitHub 쓰기 권한이 포함되지 않는다. 외부 GitHub 작업은 Codex에 이미 연결된 도구와 사용자의 명시적 요청이 있어야 한다.

## 원본 변경 후 패키지 갱신

~~~bash
python3 scripts/sync-codex-plugin.py --write
python3 scripts/sync-codex-plugin.py --check
python3 -m unittest discover -s tests -p 'test_codex_plugin_distribution.py' -v
~~~

Windows에서 python3가 없다면 py -3으로 대체한다.

--write는 패키지의 스킬 하위 디렉터리를 원본 SKILL.md/references/scripts/assets와 정확히 같게 재구성한다. manifest와 marketplace는 보존한다. --check는 SHA에 상응하는 바이트 동일성, 누락/여분 파일, 플러그인 경로, 필요한 reference가 존재하는지 검사한다. **CI는 --write를 실행하지 않아야** 원본만 변경하고 사본을 갱신하지 않은 작업을 차단할 수 있다.

기존의 전역 스킬 설치 스크립트와 docs/INSTALL.md는 계속 유효하다. 두 설치 방식을 동시에 활성화할 때 충돌이 있는지는 별도 실사용 검증이 필요하다. 이중 스킬 등록이 관측되면 중복 경로를 비활성화하고 되돌리는 절차를 먼저 검증한다.

## 검증 범위

- 정적: JSON manifest/marketplace, 이름·상대경로, 스킬 설명의 frontmatter, reference 링크 해소, 패키지 바이트 동일성 및 drift 실패 반례.
- 미검증: 실제 Codex 시장소스 등록 성공·플러그인 UI 노출·클라이언트 설치·활성화·캐시 갱신·자연어 자동 선택·기존 전역 스킬과의 공존.
- 필요한 스킬만 선택하고 references를 조건부로 읽는 현재 지침은 **그대로 보존**한다. 실제 선택 품질의 시험은 Issue #7의 범위이다.

참고: [공식 플러그인 문서](https://developers.openai.com/plugins/build/plugins), [공식 Skills activation](https://developers.openai.com/plugins/concepts/skills).
