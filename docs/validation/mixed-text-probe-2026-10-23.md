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

- 수정 후 기존 회귀와 새 source/font 경계 회귀를 포함한 총 **13/13 통과**.
- 추가 사례: 인식 가능한 토큰 없음/이미 띄어진 표기/브랜드형 토큰, boolean 이외 opt-in,
  비활성화 상태, 예외 적용과 입력 불변.
- 제공 예시 CLI: SI 후보 `35mm`는 `FINDING`, good fixture는 `NO_SIMPLE_ANOMALY`, bad fixture는 `MIX-001=FINDING`을 반환했다. 실제 줄 결과와 폰트 폴백은 `UNVERIFIED` 유지.
- 현재 호스트의 test-side Pillow reproducer: Python 3.12.14, Pillow 12.3.0, `font.getname()`은 `Malgun Gothic / Regular`, layout engine은 `0 (BASIC)`이었다. source SHA-256은 `e644375436544cda0db5d0b4b78c8262881995304673b1741b6acfd5d8a55a98`, font SHA-256은 `7a183cf1c6c56b9609fcc16eda8b5229fbc11758a21e669ec00343239b02192f`, render SHA-256은 `e0cdcef45c86471fd487b85b215394e07ef1c9b13f7cf9a39a2369b97ee1e54d`, render size는 `400x64`였다.
- source fixture SHA-256: good `d22f57c08d8629690665def3bf1adf9bf3ced27c2254d182739c9d0e6885f560`, bad `8f7f771d4f3c6f37b0ede2929bb7db32d76982cb4f73fa24d12da58677550017`.
- `git diff --check` 통과.
- Linux CI에 해당 unittest 명령을 연결했다. 기존 설치/정적 CI의 성공만으로는
  이 테스트가 실행됐다고 볼 수 없었으며, 새 CI 결과는 해당 SHA에서 별도로 확인한다.

이는 Python 코드와 합성 입력, 설치된 단일 폰트의 test-side Pillow 렌더 실행 증거다.
caller-supplied `rendered_lines`는 실제 shaping 결과를 증명하지 않으며 UAX #14 버전도
고정하지 않았다. 전체 SI 표준, Unicode/KLReq 엔진, 실제 fallback·PDF·인쇄 품질,
Codex 행동 평가(#7)는 검증하지 않았다.

## 2026-10-26 후속 P2 회귀 검증

기준 main은 사용자 제공 `faa92ee1`이다. 이 작업 스냅샷에는 `.git` 메타데이터가
없으므로 새 fix commit SHA는 기록하지 않는다. 환경은 Windows의 Python 3.14이며,
기존 2026-10-23 결과와 명령을 덮어쓰지 않고 현재 변경만 별도로 확인했다.

- `python -m unittest discover -s tests -p 'test_mixed_text_probe.py' -v`: **14/14 통과**.
- `python tests/check-knowledge-contract.py`: **통과**.
- architecture 정적 assertion: **통과**.
- P2 회귀: `모델35.5mm`, `1,035mm`, `exception035mm`, `1e+35mm`, `1e-35mm`,
  `1.2.35mm`는 `NOT_APPLICABLE`; 독립 `35.5mm`는 `FINDING`, 정확히 예외 처리한
  `35.5mm`는 `PASS`.
