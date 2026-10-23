# 수정 효과 집계의 선언·검증 분리

BASE: `a849408cb30875791c9f406a6181a03f3bcb09b2` (PR #20).
2026-10-23, macOS arm64 / Python 3.12.14.

원본은 outer FAIL→PASS, 비어 있지 않은 artifact 필드와 evidence 리스트가 있으면
evidence 내부가 UNVERIFIED인 합성 입력에도 RESOLVED 1을 반환했다.
이것은 실제 자동 PDF importer 파이프라인 실패가 아니라 집계 입력/출력의 근거 계약 공백이다.

단순 집계기 범위를 유지하는 방향을 선택했다.

- unreleased v0의 counts/outcome 대신 선언임이 명시된 declared_counts/declared_outcome 사용.
- 해결·지속·퇴행은 CANDIDATE로 표기. 독립 검증은 항상 UNVERIFIED, verified_counts는 null.
- 구조화된 PASS/UNVERIFIED 보고서는 검증해 채택하지 않으며 INCONCLUSIVE.
- id는 실행 레코드의 유일 ID. 중복 거부, 다른 실행 id의 fixture_id 그룹은 허용.
- 독립 검증기로 승격할 때 필요한 작품 버전·checker/version·profile·상태 연결 책임을 프로토콜에 명시.

```sh
python3 -m unittest discover -s tests -p 'test_repair_lift_summary.py' -v
bash tests/check-knowledge-architecture.sh
git diff --check
```

수정 후 9/9 단위 시험과 구조 검사 통과. 원본의 4개 사례를 선언형 계약에 맞게
갱신했고 미검증 보고서, 무관한 구조화 PASS, 중복 실행 ID, 명시적 반복, 잘못된 증거 컨테이너를 추가했다.
Linux CI에 해당 unittest를 연결했다.

실제 artifact나 검사기 출력의 진위·물리 조판·전문가 판단·인과적 repair lift는 검증하지 않았다.
이 스키마는 #19 보고서를 인증하거나 실제 디자인 개선 건수를 만들지 않는다.
