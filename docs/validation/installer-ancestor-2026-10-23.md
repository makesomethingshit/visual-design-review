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
