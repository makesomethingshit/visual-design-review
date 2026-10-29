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

PR30 follow-up: Windows 11 C: NTFS에서 `mklink /J`로 canonical root/references/nested 및 package 내부 junction을 재현했고, Python 3.14에서 외부 canary 보존과 `--check`/`--write` 거부를 확인했다. focused suite는 **9개 테스트 통과**했으며 `sync-codex-plugin.py --check`도 통과했다.

## source-30 Windows line-ending regression

현재 PR 파일만 둔 격리 fixture에서 `git init` → `core.autocrlf=true` 설정 → `git add` → 작업 트리 삭제 → `git checkout-index --all --force`를 실행했다. 기존 속성에서는 canonical Markdown 17개는 LF였지만 생성 패키지 Markdown 17개는 CRLF로 체크아웃되어, 17개 파일의 바이트 비교가 실패했다. 원격 clone·다운로드는 사용하지 않았다.

`.gitattributes`에 canonical 및 generated runtime의 Markdown/Python 경로를 모두 `text eol=lf`로 명시했고, 테스트는 실제 임시 Git checkout에서 source/package의 `.md`와 `.py` 파일 모두 CRLF가 없는지 확인한다. 기존 Windows junction 회귀 9개와 새 EOL 회귀를 포함한 focused suite는 **10개 테스트**이며, Windows workflow도 실제 checkout에서 `python scripts/sync-codex-plugin.py --check`를 실행한다.

## 남은 검증

- GitHub 원격 marketplace 추가·갱신, 데스크톱 UI 표시와 설치 흐름.
- 별도 세션에서 자연어로 스킬이 선택되고 실제 references를 읽는 행동 및 비대상 요청의 오발동 여부.
- 기존 전역 스킬과 동시에 활성화할 때의 중복 검색과 버전 갱신 캐시.
- `enabled=true`는 설치 설정 상태이며, 모델이 실제로 스킬을 사용했다는 증거가 아니다. 위 행동 검증은 Issue #7과 #29에서 계속 추적한다.


## Windows 격리 CLI 설치 수명주기 — 2026-10-26

Codex CLI 0.164.0-alpha.11.1의 별도 빈 CODEX_HOME에서 로컬 PR 스냅샷
marketplace add → available 목록 확인 → plugin add → installed/enabled=true
재조회 → plugin remove → marketplace remove를 실행해 모두 성공했다.
사용자 전역 설정·인증을 복사하지 않았다. GitHub 원격 source fetch, 데스크톱 UI,
자연어 자동 선택·비대상 요청·전역 스킬 공존은 이 실행에서 검증하지 않았다.

## 최종 기능 통합

선행 기능 PR을 합친 원본의 런타임28개 파일을 다시 생성했다. 전체 테스트가
만드는 scripts/__pycache__는 배포 입력에서 제외하며, 캐시를 만든 뒤에도
배포본에 포함되지 않고 --check가 통과하는 회귀를 추가했다. 생성물 제외 외
원본/배포본 바이트 동일성 검사는 유지한다. 최종 통합 단위88/88, 계약·
수정 아티팩트·Windows 설치 스모크와 배포28파일 동기화가 로컬에서 통과했다.

## PR #33 후속 검증 — 2026-10-29

위 28파일 기록은 선행 통합 시점의 결과다. PR #33은 글꼴 비교 fixture를
배포용 assets로 옮겨 현재 원본·배포본이 **29파일**이다. 이번 후속 검증에서
Windows / Python 3.14.6 / Pillow 12.3.0으로 전체 unittest **92개**, 지식 계약,
수정 아티팩트 및 `sync-codex-plugin.py --check`가 통과했다. Windows 외부 도구의
로컬 인코딩 출력 때문에 전체 unittest와 아티팩트 검사는 `-X utf8=0`으로 실행했다.

정션 검사는 검사 시점의 링크만 거부한다. 검사와 삭제·복사 사이 동시 경로
변경은 원자적으로 보호하지 않으며, 동시 변경을 재현·검증하지 않았다.
본문 검사는 CR/LF를 제외한 문자 내용만 비교한다. 문단 경계가 소실되어도
검사를 진행할 수 있으며, LF·CRLF·CR 각각에서 출력 scope가 문단 경계를
미검증으로 표시하는 회귀를 추가했다. 실제 문단·조판 보존, Codex UI 및
자연어 자동 선택은 이번 실행에서 검증하지 않았다.
