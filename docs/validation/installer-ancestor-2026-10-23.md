# 설치 경로의 심볼릭 링크 상위 디렉터리 회귀

대상 BASE: `99b3b9b92926156ea4ca94c15c1c5c6e352ec9ee`.
2026-10-23, macOS arm64, 기본 /bin/bash. 모든 원본 사본과 CODEX_HOME은 임시 디렉터리로 격리했다.

## 수정 전 재현

원본 스킬 폴더를 가리키는 외부 symlink 아래의 미생성 `new-home/deeper`를 CODEX_HOME으로 지정하면
기존 `install --dry-run`이 종료 코드 0으로 설치를 허용한다. 새 회귀 시험을 기존 BASE에 적용하면
`source ancestor link accepted: install --dry-run`으로 실패했다.

## 수정

최종 CODEX_HOME이 없더라도 존재하는 가장 가까운 상위 디렉터리까지 이동해 `pwd -P`로 링크를 해석하고,
나머지 미생성 경로를 붙여 원본 내부 여부를 검사한다. 기존 파일이나 dangling link로 경로를 해석할 수 없으면
입력 문자열로 되돌아가지 않고 거부한다. 거부는 대상 mkdir·복사보다 먼저 이뤄진다.

## 수정 후 실행

```sh
/bin/bash tests/smoke-install-paths.sh
/bin/bash tests/smoke-install-macos.sh
git diff --check
```

- 링크가 원본을 가리키고 하위 경로가 없는 경우: install/check 및 각각 dry-run을 종료 코드 2로 거부.
- 거부 후 원본 안의 새 디렉터리가 생성되지 않음.
- 원본 밖을 가리키는 정상 symlink와 미생성 하위 경로: dry-run 무변경, install/check/remove 성공.
- dangling ancestor: 거부하고 링크 대상 디렉터리를 생성하지 않음.
- macOS 전체 격리 수명주기·native shasum·한글/공백·강제 activation 실패 후 복원 시험 통과.

공통 Linux 스모크에서 새 경로 시험을 호출하므로 Linux/macOS CI에도 연결된다.
Windows installer/junction 동작과 링크 변경의 동시성(TOCTOU)은 이번 수정의 검증 범위가 아니다.
전역 사용자 스킬·설정·디자인 원본은 변경하지 않았다.

## macOS CI의 긴 본문 파이프 오류 추가 반영

첫 PR CI의 macOS 작업에서 frontmatter를 읽는 생산자 `printf`가 Broken pipe로
실패했다. `pipefail` 상태에서 앞부분만 읽는 `awk`/`grep`이 일찍 종료하는 경로를
제거하고 here-string 및 Bash 문자열 연산을 사용했다. 긴 정상 본문을 추가한
격리 시험은 수정 전 실패했고 수정 후 install/dry-run/check/remove가 통과했다.
기존 frontmatter 경계·metadata 소속 음성 시험을 포함한 전체 macOS 스모크도 통과했다.
이 항목은 파일 구조 유효성을 검증하며 모델의 내용 판단은 검증하지 않는다.

## 2026-10-26 최신 main과 충돌 해결

PR #6이 병합된 `03b567ce69ab2e63bd8f5cfa61333afcbb7f0a57`을 기존 PR #23 브랜치에 합쳤다.
충돌한 frontmatter 읽기는 main의 `read`/here-string과 입력을 끝까지 읽는 awk 구현을 유지했다.
이 PR의 미생성 경로 상위 디렉터리 해석과 긴 본문 수명주기 회귀 시험은 그대로 보존했다.

동일한 macOS arm64 환경에서 기본 `/bin/bash`로 전체 native macOS 설치 스모크를 재실행해 통과했다.
원본 내부 링크 거부, 정상 링크 허용, 끊어진 링크 거부, 긴 본문, native shasum,
한글/공백 경로 및 강제 활성화 실패 후 복원까지 포함한다.
Python 3.12.14의 지식 계약 검사와 기존 단위 시험 15개도 통과했다.
실제 전역 설치를 변경하지 않았으며, Windows junction과 실제 모델 행동은 이 로컬 실행의 범위가 아니다.

추가 경계 검토에서 `missing-parent/../visual-design-review/new-home`의 dry-run이
원본 내부 경로를 허용하는 문제도 재현했다. 미생성 경로에 포함된 `.`/`..`는 안전하게 해석할 수
없으면 종료 코드 2로 거부한다. install/check와 각각 dry-run의 거부 및 디렉터리 무생성
회귀 시험을 추가했다. 이미 존재하는 상위 경로의 `pwd -P` 해석은 유지한다.
