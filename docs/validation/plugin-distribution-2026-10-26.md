# 플러그인 배포 경로 검증 (2026-10-26)

## 대상과 조건

- PR #30 원본 HEAD: `918bb2ac7fb35947440171007453e4e15f0f3bf9`.
- macOS 15.7.5 (24G624), arm64, Codex CLI 0.163.0, Python 3.12.14.
- Git archive로 만든 임시 스냅샷과 별도의 임시 `CODEX_HOME`을 사용했다. 사용자 전역 설치본·설정·인증 자료는 변경하거나 복사하지 않았다.
- 공식 [플러그인 패키징 안내](https://developers.openai.com/plugins/build/plugins)의 repo marketplace와 `.codex-plugin/plugin.json` 호환 경로를 대조했다. 공개 디렉터리 등록 검증은 아니다.

## 실행 결과

| 확인 | 결과 |
| --- | --- |
| 원본 `--check` | manifest/marketplace와 17개 원본 파일 일치 |
| 원본 배포 회귀 테스트 | 5개 통과 |
| 격리 CLI `plugin marketplace add <임시 스냅샷> --json` | `makesomethingshit-design` 등록 |
| `plugin list --marketplace makesomethingshit-design --available --json` | `visual-design-review` 0.1.0 발견, 설치 전 `installed=false`, `enabled=false` |
| `plugin add visual-design-review@makesomethingshit-design --json` 및 재조회 | 설치 경로 반환, `installed=true`, `enabled=true` |
| 설치 캐시와 원본 비교 | SKILL.md와 references의 17개 파일 바이트 일치 |
| `plugin remove` 및 재조회 | 설치 목록이 빈 배열 |
| `plugin marketplace remove` 및 재조회 | marketplace 목록이 빈 배열 |

등록·설치·제거 명령은 위와 같은 격리 `CODEX_HOME` 환경변수를 각 호출에 지정했다. `owner/repo`를 가져오는 원격 Git 경로가 아니라 **로컬 marketplace 소스** 경로를 시험했다.

## 발견한 결함과 회귀 수정

원본 동기화 도구는 최종 스킬 폴더만 symlink인지 확인했다. `plugins/` 상위 폴더가 외부 디렉터리로 연결되면 `--write`가 그 안의 스킬 폴더를 삭제·재생성해 외부 사용자 파일을 지웠다. 임시 디렉터리에 만든 `keep.txt`가 사라지면서 종료 코드 0/PASS를 반환하는 반례로 확인했다.

수정본은 저장소 루트부터 대상 스킬 폴더까지의 연결 경로를 검사하고, `--check`와 `--write` 모두 연결 경로에서 중단한다. 기존 외부 파일을 바이트 단위로 보존하는 시험과 끊어진 상위 링크 시험을 추가했다. 수정 후 **7개 테스트 통과**, 17개 파일 동기화 검사 통과. macOS의 symlink를 실행 검증했으며 Windows junction 실행 검증은 하지 않았다.

## 남은 검증

- GitHub 원격 marketplace 추가·갱신, 데스크톱 UI 표시와 설치 흐름.
- 별도 세션에서 자연어로 스킬이 선택되고 실제 references를 읽는 행동 및 비대상 요청의 오발동 여부.
- 기존 전역 스킬과 동시에 활성화할 때의 중복 검색, 버전 갱신 캐시, Windows junction.
- `enabled=true`는 설치 설정 상태이며, 모델이 실제로 스킬을 사용했다는 증거가 아니다. 위 행동 검증은 Issue #7과 #29에서 계속 추적한다.
