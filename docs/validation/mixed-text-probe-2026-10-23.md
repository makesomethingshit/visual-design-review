# 혼식 검사 PoC의 적용 범위 상태 회귀 검증

2026-10-23. 대상은 PR #16의 `c6907c920de9238e0d0b8462fa08546da0e81ad3`와 이 수정본이다.
환경: macOS arm64, Python 3.12.14. 보조 확인으로 시스템 Python 3.9.6에서도 같은 결과를 확인했다.
Python 3.10+가 문서화된 실행 범위이며, 3.9.6 확인으로 지원 범위를 확대하지 않는다.

## 재현과 수정

수정 전 원본 테스트 4건 중 1건이 실패했다.
`text="폭은 35mm입니다", profile.si_spacing=true`에서 독립 SI 단위 토큰이
인식되지 않았는데 `PASS`를 반환했고, 기존 테스트는 `NOT_APPLICABLE`을 요구했다.
검사를 적용하지 않은 경우를 검증 성공으로 기록하지 않도록 분리했다.

추가로 JSON 문자열 `"false"`의 Python truthiness가 검사 opt-in으로 해석되지 않도록
`si_spacing`에 실제 boolean만 허용한다. 입력 원문은 수정하지 않는다.

## 실행

```sh
python3 -m unittest discover -s tests -p 'test_mixed_text_probe.py' -v
python3 visual-design-review/scripts/mixed_text_probe.py examples/mixed-script-input.json
```

- 수정 후 원래 4건과 추가 4건, 총 **8/8 통과**.
- 추가 사례: 인식 가능한 토큰 없음/이미 띄어진 표기/브랜드형 토큰, boolean 이외 opt-in,
  비활성화 상태, 예외 적용과 입력 불변.
- 제공 예시 CLI: SI 후보 `35mm`는 `FINDING`, 실제 줄 결과와 폰트 폴백은 `UNVERIFIED` 유지.
- `git diff --check` 통과.

이는 Python 코드와 합성 입력에 대한 실행 증거다. 전체 SI 표준, Unicode/KLReq 엔진,
실제 폰트·렌더러·PDF·인쇄 품질, Codex 행동 평가는 검증하지 않았다.
