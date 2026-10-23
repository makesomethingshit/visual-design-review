# finding 이력의 재발·지속 상태 회귀

BASE: `c789c1b12114054a69226eec4e2c615f355db2c2` (PR #18).
Earlier evidence: 2026-10-23, macOS arm64 / Python 3.12.14.

This completion pass ran on Windows PowerShell with the bundled Python runtime
`C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
The earlier macOS result remains historical evidence; the LF/hash verification
below is the current Windows result.

## Local completion pass

The checked-in fixture is a minimal original SVG graphic design with three comparable versions and one renamed-object variant:

- `poster-v1.svg` SHA-256 `15a41bc3dc1ff37a586aba9b2daf958a6e918a854b5cf294b0f5bb7c5664a03d`
- `poster-v2-moved.svg` SHA-256 `a95653d126290cdcbf64932dbab1751593829e7ae90b1bb812eecf5b4ce6e20d`
- `poster-v3-regressed.svg` SHA-256 `9e2709e5cf74899c68e236599b2fc10f5c3d277ee52b57b3f75e967fa4c37389`
- `poster-v2-renamed.svg` SHA-256 `247acd58ce999648c4055eb2b9be180a771d8f231ea32025b158639ff0ac24ac`

The fixture test parses each SVG, checks the `viewBox`, derives each rectangle's numeric `x/y/width/height`, and compares those values with the snapshot bbox. It also checks the recorded artifact hash and source object IDs. It therefore tests the evidence link rather than trusting `VERIFIED_SOURCE` labels alone.

The fixture directory has scoped `.gitattributes` rules for JSON and SVG `eol=lf`. The test rejects CRLF bytes, and the recorded SHA-256 values were checked against the corresponding Git blob bytes after staging.

The actual CLI is exercised over the snapshots: v1→v2 reports `F-ALIGN=PERSISTING` despite movement and `F-CAPTION=RESOLVED`; v2→v3 reports `F-CAPTION=REGRESSED`; v3→partial reports both findings `INCONCLUSIVE`; v1→renamed reports a new finding ID and does not visually match the renamed source object. Every result retains `evidence=stable_id_only` and the warning that continuity is not visually verified.

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

기존 수정 후 9/9 통과에 이어 fixture/CLI 보강 후 17/17 통과. 명시적 현재 상태와 legacy 이력 각각의 세 버전 chain,
부분 관찰, resolved tombstone, 미측정 bbox 및 잘못된 상태 거부를 확인했다.
해당 unittest를 Linux CI에 연결했다.

이는 caller가 제공한 안정 ID와 상태의 논리 비교다. fixture는 source ID·수치 bbox·파일 hash의 연결과 이동·이름 변경·누락 반례를 검증하지만, 실제 작품 일반화/객체 동일성/시각적 수정 효과/전문가 판독을 검증한 것으로 승격하지 않는다. Quick/Deep 에이전트 실행은 이 로컬 검증에서 확인하지 않았다.
