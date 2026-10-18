# v1.0.1 evaluation replay

이 평가는 개선을 증명하는 벤치마크가 아니라 재검토 가능한 소규모 동작 기록이다.
[입력과 기대 판정](cases.json), [프롬프트 템플릿](prompt-template.json),
[실제로 주입한 지시](tested-instructions.txt), [52개 실행 원문/메타데이터](runs.jsonl),
[관측 판정](observed-results.md)을 함께 읽는다. 기대 판정은 모델에 제공하지 않았다.

## 실행 환경과 비교의 의미
- 2026-10-18, Windows 네이티브 Desktop Codex CLI `0.163.0-alpha.10.2`.
- 두 arm 모두 요청 모델 `gpt-6.1-sol`, reasoning effort `medium`, fresh ephemeral session.
  서버 내부 모델 revision/seed는 CLI에 노출되지 않아 기록할 수 없다.
- `--ignore-user-config --sandbox read-only --skip-git-repo-check --ephemeral --json`.
- 행동 비교는 target skill을 invocation override `skills.config`에서 비활성화한다.
  사용자 설정 파일이나 다른 전역 스킬은 수정하지 않는다.
- baseline은 일반 리뷰 지시, skill arm은 같은 사용자 입력에 고정 snapshot을 주입한다.
  이는 **지시 내용의 효과** 비교이며 실제 파일 발견/선택적 reference 로딩의 시험이 아니다.
  snapshot에는 비교를 고정하기 위해 관련 references를 함께 넣었다. 토큰 길이 차이는
  통제되지 않았고 다른 기본 시스템 문맥은 남아 있으므로 '순수 무지시 모델'도 아니다.
- A~J × 두 arm × 2회 = 40개 행동 실행. J만 저장소 루트의 자체 합성 PNG를 첨부.
  모든 입력은 사례 설명 또는 자체 픽스처이며 사용자 디자인을 업로드하지 않았다.
- R1~R6 × 2회 = 12개 native routing 실행. 두 arm 비교와 분리하며 skill을 비활성화하지 않는다.
  선언된 선택, 실제 파일 읽기 성공, 최종 적용을 구분한다. 최종 문장에 이름이 없다는
  사실만으로 비활성 판정을 내리지 않는다.

## 정확한 재생
동일 CLI 모델 접근 권한이 있는 환경에서 각 기록을 새 세션으로 실행한다.
모델 호출에는 계정 사용량이 필요하며 실패도 원문과 함께 기록한다. 불필요한
패키지나 실행 스크립트를 설치하지 않는다. 표준 Python/PowerShell로 아래를 구성할 수 있다.

1. cases.json에서 한 사례의 `input`만 취한다. 기대 판정은 평가자에게만 보인다.
2. 행동 프롬프트는 `common` + arm에 맞는 prefix/snapshot 또는 baseline_suffix +
   `input_prefix` + 사례 input. native는 사례 input + routing_suffix.
3. SHA256이 runs.jsonl의 prompt_sha256과 일치하는지 확인한다. 응답도 UTF-8 원문
   그대로 해시한다. J는 fixture_sha256으로 이미지 동일성을 확인한다.
4. 행동 비교 명령의 형태:

```text
codex exec --ignore-user-config --ephemeral --skip-git-repo-check --sandbox read-only --json -m gpt-6.1-sol -c model_reasoning_effort="medium" -c 'skills.config=[{path="<GLOBAL_SKILL>/SKILL.md",enabled=false}]' -C <EMPTY_WORK_DIR> -
```

프롬프트는 UTF-8 stdin으로 전달한다. J만 `--image <REPO>/visual-fixtures.png`를 추가한다.
native routing은 skills.config override를 제외하고 설치된 target skill을 사용한다.
현재 최종 파일과 snapshot은 일부 보강 문구가 다르다. 기존 기록을 재현하려면 snapshot을,
최종 후보를 평가하려면 새 snapshot/hash를 만들어 별도 run ID로 기록한다. 기존 응답을
덮어쓰거나 수정된 지시로 나온 응답이라고 다시 표시하지 않는다.

5. exit code와 turn.completed/turn.failed를 함께 검사한다. 실패에서 비어 있는 응답은
   오탐 없음이나 통과가 아니라 `blocked`다. 같은 입력·arm의 두 **완료** 응답이 있어야
   반복 일관성을 비교할 수 있다.
6. [관측 판정](observed-results.md)의 축으로 사람이 원문과 근거를 대조한다.
   제목 개수·정규식·모델의 자체 PASS만으로 합격 처리하지 않는다.

## 남은 실행
52개 중 21개 완료, 31개는 계정 사용량 한도 오류다. native routing 12개는 전부
차단되어 성공/실패율을 산출하지 않는다. 마지막 심각도 문구와 조건부 reference
선택 보강 이후의 최종 후보 행동 재시험도 남았다. 모델 내부 revision을 고정할 수
없어 재생 시 응답이 달라질 수 있다. 이 기록만으로 v1.0.0 대비 또는 다중 모델의
품질 향상을 주장하지 않는다.
