# GitHub 후속 변경 검토와 로컬 실행 기록

2026-10-23. 원본 main은 `1cb4bde43ca7842b14e03a14a73c4e8f803c770e`였다.
열린 이슈 #2, #7~#14와 PR #5, #6, #15~#20의 본문·관련 댓글·변경 파일을 대조했다.
원본과 포크의 최신 refs를 읽었으며 원본 main 병합이나 전역 스킬 설치는 하지 않았다.

## 고정 대상과 확인 수준

| PR | 검토한 SHA | 확인 |
| --- | --- | --- |
| #5 | `87b3e0507b2d41e78773d1948917ea3a3d8ac653` | 근거 표기 수정 요청 확인. `202c433`으로 비교 후보·확정 요구·실증의 구분을 수정 |
| #6 | `a68eb9930ffad88a4676034a76ba88fbe6734034` | 정적 계약 및 격리 macOS 설치 시험 통과. 아래 opt-in 명세 충돌 발견 |
| #15 | `e066af01b15707fd1c6d8d383c2e4a2a49865472` | 코퍼스·반례 문서 검토. 1차 자료 절/버전 대조와 모델 시험은 여전히 미검증 |
| #16 | `c6907c920de9238e0d0b8462fa08546da0e81ad3` | 원본 unittest 4건 중 1건 실패 재현. 별도 수정 PR에서 8건 통과 |
| #17 | `010f97c276c598c7ea895a0e0b2c1928020cc66b` | 연구 프로토콜·미제공 폰트/평가 fixture 검토. 실제 전문가·폰트 비교 미실행 |
| #18 | `c789c1b12114054a69226eec4e2c615f355db2c2` | 제공된 Python unittest 4/4 통과. 실제 객체 매칭·디자인 개선은 미검증 |
| #19 | `e6ac9bc9785a88cb0b7fde8ddd00e578a00f9b82` | 제공된 Python unittest 3/3 통과. PDF 헤더/보고서 importer 검사이며 실제 preflight 아님 |
| #20 | `a849408cb30875791c9f406a6181a03f3bcb09b2` | 제공된 Python unittest 4/4 통과. 선언된 상태의 집계이며 실제 repair-lift 실험 아님 |

## PR #6: opt-in의 명세 정합성 수정

`typography-presets.md`와 R-33은 A~H를 프로젝트 전용 opt-in 정책으로 제한했으나,
`design-handoff.md`는 주언어와 새 가로 본문 조건만으로 A~D를 제안하도록 읽힐 수 있었다.
R-6/R-13/R-14 역시 opt-in 없는 사용자 입력에 특정 정책값을 필수 답으로 요구했다.
이는 실제 모델 실패를 재현한 결과가 아니라 고정 소스의 서로 다른 명세를 대조한 결과다.

이 수정은 SKILL·routing·handoff의 활성화 조건을 일치시키고 양성 사례에 명시적 프로파일 선택을 추가한다.
개별 사용자 지정값은 프로파일 없이도 USER 입력으로 계산할 수 있으며 A~H 수치·날짜·우선순위는 변경하지 않는다.
프로파일 확인을 위한 자료 읽기와 실제 정책값 채택도 구별한다.

검사는 opt-in이 누락된 진입점, 활성 근거 없는 handoff, opt-in 없는 양성 시나리오를 거부한다.
수정 전 `a68eb99` 문서를 새 검사에 입력하면 진입점 guard에서 실패한다.
이는 문서 계약의 회귀 검사이며 실제 Codex의 자동 로딩이나 응답을 검사하지 않는다.

## 실행과 범위

환경: macOS arm64. 구조 검사·설치 시험은 기본 /bin/bash 및 Python 3.9.6,
Python unittest는 별도로 3.12.14에서도 실행했다. 개인 경로와 원문 세션 로그는 기록하지 않았다.

```sh
/bin/bash tests/check-knowledge-architecture.sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
/bin/bash tests/smoke-install-macos.sh
git diff --check
```

- 수정본의 구조/산술/링크/정책 계약 검사 및 opt-in 회귀 unittest 4/4 통과.
- 새 구조 검사에서 전체 `test_*.py` discovery를 연결해 후속 PoC 테스트가 조용히 빠지지 않도록 했다.
- 격리 임시 CODEX_HOME에서 설치·check·갱신·백업·제거·복구, native shasum,
  한글/공백 경로, 강제 activation 실패 후 rollback, 긴 SKILL 본문 회귀 통과.
- 실제 사용자 CODEX_HOME이나 스킬 설정은 변경하지 않았다.
- GitHub의 기존 대상 SHA들은 설치/정적 CI가 성공했지만, #16의 unittest 실패와 양립했다.
  해당 워크플로가 새 PoC unittest를 호출하지 않았기 때문이다. CI 성공과 단위 검사 실행 여부를 분리했다.

## 남은 일

#7의 BASE/HEAD 실제 Codex 독립 세션·reference 열람·블라인드 판정은 이번 작업에서 실행하지 않았다.
#8~#13의 원문 연구, renderer/font fixture, 전문가 비교, 실제 PDF 검사, 물리 출력과 수정 효과도 완료 처리하지 않는다.
새 회귀 검사를 실제 행동의 합격 증거로 바꾸거나, Draft 후속 PR을 자동 병합하지 않는다.
