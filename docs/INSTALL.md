# Codex 전역 설치·업데이트·검증

이 문서는 저장소의 visual-design-review 폴더를 **현재 Codex 실행 환경**의 전역 스킬 디렉터리에 안전하게 설치하는 절차다. 저장소 루트에서 명령을 실행한다. 네트워크 전송, 패키지 설치, 사용자 디자인 수정, 다른 전역 스킬과 AGENTS.md 또는 Codex 설정 변경은 수행하지 않는다.

## 환경과 대상 경로

| 실행 환경 | 실행 스크립트 | 기본 설치 위치 |
| --- | --- | --- |
| Windows 네이티브 PowerShell 5.1+ | scripts/install-windows.ps1 | $HOME\.codex\skills\visual-design-review |
| WSL / Linux Bash | scripts/install-linux.sh | $HOME/.codex/skills/visual-design-review |

- CODEX_HOME이 설정된 경우 **현재 환경의 절대 경로**를 우선 사용한다. Windows 경로를 WSL에 직접 넘기거나 그 반대로 사용하지 않는다. Windows와 WSL의 설치는 별개이며 **요청하지 않은 환경에는 설치하지 않는다**.
- 설치 원본은 visual-design-review/ 디렉터리이며, 이름·상대 reference 경로·스킬 내용은 그대로 유지한다.
- 설치 스크립트는 대상 스킬 폴더 외 다른 스킬, 프로젝트의 .agents/skills, AGENTS.md, Codex 설정을 수정하지 않는다.
- PowerShell 실행 정책은 바꾸지 않는다. 시스템 정책이 실행을 막으면 관리자 정책을 우회하지 않는다.

## Windows PowerShell

~~~powershell
# 저장소 루트에서 예상 동작만 확인
.\scripts\install-windows.ps1 -Action install -DryRun
# 설치 또는 갱신
.\scripts\install-windows.ps1 -Action install
# 파일 목록, SHA-256, 기본 frontmatter와 relative references 대조
.\scripts\install-windows.ps1 -Action check
# 활성 스킬 제거 전 점검 / 실제 제거 (백업 보존)
.\scripts\install-windows.ps1 -Action remove -DryRun
.\scripts\install-windows.ps1 -Action remove
~~~

CODEX_HOME 경로를 직접 지정하려면 현재 PowerShell 프로세스에서 설정한다.

~~~powershell
$env:CODEX_HOME = 'D:\CodexHome'
.\scripts\install-windows.ps1 -Action install -DryRun
~~~

## WSL / Linux Bash

~~~bash
bash scripts/install-linux.sh install --dry-run
bash scripts/install-linux.sh install
bash scripts/install-linux.sh check
bash scripts/install-linux.sh remove --dry-run
bash scripts/install-linux.sh remove
~~~

CODEX_HOME 변경 예:

~~~bash
CODEX_HOME="$HOME/codex-custom" bash scripts/install-linux.sh install --dry-run
~~~

## 안전성·복구·버전 확인

1. **dry-run:** 대상 파일을 읽기만 하며 디렉터리도 새로 만들지 않는다.
2. **새 설치:** 패키지를 임시 스테이징 디렉터리에 복사한 뒤 파일·참조를 검증하고 활성 위치로 이동한다.
3. **같은 버전·같은 내용:** 재실행해도 파일을 수정하거나 새 백업을 만들지 않는다. 버전 문자열만이 아니라 실제 파일 목록과 SHA-256을 비교한다.
4. **내용이 달라진 설치:** 기존 폴더 전체를 스킬 검색 루트 밖의 `$CODEX_HOME/skill-backups/visual-design-review/(UTC 시간).(프로세스 ID).(난수)`에 보존하고 검증된 새 설치본으로 교체한다. 활성화 실패 시 기존 백업 복원을 시도한다.
5. **제거:** 파일을 삭제하지 않고 활성 스킬 폴더를 백업 위치로 이동한다. 백업 파일은 사용자가 직접 검토 후 정리할 수 있다.
6. **수동 복구:** Codex 종료 후 기존 활성 폴더를 확인하고, 선택한 백업 폴더를 `$CODEX_HOME/skills/visual-design-review`로 이동한다. 여러 설치 프로세스를 동시에 실행하지 않는다.
7. **버전:** 활성 SKILL.md의 metadata.version을 확인하며, check 실행 결과가 동기화 성공인지 따로 판단한다.

링크된 설치 대상은 교체하지 않는다. 파일 검사는 기본 frontmatter 필드와 상대 링크, 파일 내용을 확인하지만 완전한 YAML 스키마 검증이나 모델 동작 증명은 아니다.

## 파일 시스템 스모크 테스트

테스트는 실제 전역 CODEX_HOME을 건드리지 않고 자체 임시 디렉터리에서 수행한다.

~~~bash
bash tests/smoke-install-linux.sh
~~~

~~~powershell
.\tests\smoke-install-windows.ps1
~~~

각 테스트는 신규 설치·dry-run 무변경·내용 대조·멱등성·사용자 변경본 백업·제거와 백업 보존을 확인한다. Linux 테스트는 상대 CODEX_HOME 거부와 대상 심볼릭 링크 거부도 검사한다. 특정 환경에서 실행하지 못한 테스트를 성공으로 기록하지 않는다.

## 새 Codex 세션에서 라우팅 확인

정적 설치 검증과 실제 스킬 선택은 별도다. 새 Codex 세션을 열어 아래 입력을 각각 실행하고 **SKILL.md와 필요한 references를 실제로 읽은 도구 기록**과 최종 답변을 확인한다.

| 구분 | 예시 입력 | 기대 |
| --- | --- | --- |
| 명시 호출 | $visual-design-review 포스터 구성 비평해줘. 이미지는 아직 없어. | 스킬과 필요한 자료 읽기, 입력 요청 |
| 자연어 호출 | 잡지 편집디자인의 조판을 검토해줘. 페이지는 아직 없어. | 스킬 읽기, 관찰 날조 금지 |
| 제외: 일반 코드 | 파이썬 함수의 예외 처리를 리뷰해줘. | 스킬 미적용 |
| 제외: CSS | CSS grid의 gap 동작만 확인해줘. | 스킬 미적용 |
| 제외: 웹 UI | 웹 버튼의 접근 가능한 이름만 감사해줘. | 스킬 미적용 |

선택 선언이나 답변에 스킬 이름이 나온 사실만으로 합격으로 보지 않는다. 미실행·차단·실패는 그대로 기록하고, 기존 평가 원문을 덮어쓰지 않는다. 자세한 이전 평가 기록은 [evaluation/README.md](../visual-design-review/tests/evaluation/README.md) 및 [VALIDATION.md](../VALIDATION.md)를 참조한다.
