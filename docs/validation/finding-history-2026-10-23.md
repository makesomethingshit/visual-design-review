# finding 이력의 재발·지속 상태 회귀

BASE: `c789c1b12114054a69226eec4e2c615f355db2c2` (PR #18).
2026-10-23, macOS arm64 / Python 3.12.14.

수정 전 실제 모듈에서 v1의 해결 이력을 갖고 v2에 다시 나타난 F1은 REGRESSED이며,
v3에도 계속 있는 F1도 이전 행의 `previous_state=RESOLVED` 때문에 다시 REGRESSED로 나왔다.
기존 4개 단위 시험은 이 세 버전 연속 비교를 포함하지 않았다.

현재 스냅샷의 `state`와 역사적 `previous_state`를 분리한다.
양쪽 활성 finding은 PERSISTING, 직전 스냅샷의 RESOLVED tombstone 뒤 재출현은 REGRESSED다.
before에 ID가 없는 legacy 입력의 current-row previous_state는 호출자가 제공한 이력으로만 사용한다.
부분 리뷰의 누락은 INCONCLUSIVE이며 명시적 현재 INCONCLUSIVE/RESOLVED도 보존한다.

```sh
python3 -m unittest discover -s tests -p 'test_finding_history.py' -v
bash tests/check-knowledge-architecture.sh
git diff --check
```

수정 후 9/9 통과. 명시적 현재 상태와 legacy 이력 각각의 세 버전 chain,
부분 관찰, resolved tombstone, 미측정 bbox 및 잘못된 상태 거부를 확인했다.
해당 unittest를 Linux CI에 연결했다.

이는 caller가 제공한 안정 ID와 상태의 논리 비교다. 실제 작품/객체 동일성,
시각적 수정 효과, 전문가 판독을 검증한 것으로 승격하지 않는다.
