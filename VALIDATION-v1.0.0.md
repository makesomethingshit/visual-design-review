# 검증 보고서

검증일: 2026-10-18 (Asia/Seoul). v1.0.0.

## 구조와 설치
Windows 네이티브 Desktop Codex와 활성 사용자 홈을 확인했다. WSL 경로를 사용하지 않았다. 사용자 전역 `.codex/skills/visual-design-review`에 신규 설치했다. SKILL.md 1개, 선택적 references 8개, tests/review-cases.md 1개로 총 10개다.

skill-creator quick_validate.py, Python YAML 파싱, 정확한 파일 집합, BOM 부재, 모든 로컬 링크 검사와 설치본·후보·공개본의 바이트 일치 검사를 수행했다. 행동 보정 시 이번 작업 설치본을 백업하고 두 문서만 갱신했다. 프로젝트 AGENTS.md·.agents/skills·다른 전역 스킬·설정은 변경하지 않았다. 패키지나 MCP를 추가하지 않았다.

## 출처·라이선스
6개 소스 경로/5개 저장소를 읽었다. E/F는 같은 저장소다. commit SHA·실제로 읽은 파일·통합 및 배제 결정은 [sources.md](visual-design-review/references/sources.md)에 기록했다.
A/D/E/F는 루트 MIT, C는 스킬 패키지 한정 MIT 기반 허가문을 확인했다. C의 API NOASSERTION과 실제 LICENSE를 구분했다. B는 명시적 허가를 찾지 못해 원문·파일을 복제하지 않고 일반 방법론만 참고했다. 독자적으로 작성했으며 MIT 고지는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 보수적으로 보존했다. 외부 스크립트·hooks는 실행하지 않았다.

## A~E 설명 기반 행동 테스트
독립 읽기 전용 에이전트가 실제 리뷰 응답을 작성했다. 이미지 없는 모의 테스트이며 시각 분석 성공이 아니다.

| 사례 | 결과 |
| --- | --- |
| A 실험 포스터 | 비대칭·의도적 난독성을 자동 결함으로 만들지 않음 |
| B 편집디자인 | 첫 응답의 근거 부족 Major를 거부하고 Minor/Probable로 보정. 실제 조판 미검증 |
| C 문자 계보 | 선 의미·확실성·출처 분리. 날짜 미제공 Opportunity를 추가 입력으로 보정. 역사 진위 미검증 |
| D 아이덴티티 | 입력 부족 Opportunity와 존재만으로 Strength를 제거. 새 세션에서도 확인 |
| E 이미지 없음 | 이미지/PDF 요청, 시각 관찰·결함 생성 유보. 새 세션에서도 확인 |

## 실제 이미지 보조 테스트
자체 제작 [합성 PNG](visual-fixtures.png)를 메인과 별도 읽기 전용 에이전트가 실제 이미지 도구로 열었다. A 중첩 포스터/B 편집 와이어프레임/C 가상 계보/D 최소 아이덴티티다. 실제 본문·사진·역사 자료가 아니다.

첫 응답은 실패였다. A의 형식 탐구와 B의 캡션을 근거 없이 Major로 올리고, C의 가상 출처와 D의 미제공 응용물을 문제로 만들었다. Strength 여섯 필드와 Deep 9부분도 누락했다. 에이전트의 자체 PASS를 수용하지 않고 이미지·응답과 직접 대조했다.

rubric에 '자료 부족과 판정 보정'을 추가한 뒤 재실행했다. 근거 없는 Major, 가상 출처 결함, 입력 부족 Opportunity가 제거되었고 Deep 9부분·Strength 여섯 필드가 포함됐다. 남은 지적은 C의 조건부 선 부호 혼동과 B의 캡션 귀속 해석이다. 작품의 제작 합격 판정은 아니다.

잔여 형식 한계: 설명 기반 재실행은 Deep 항목을 일부 압축했으며 이미지 재실행의 선택적 Push는 모두 별도 Finding ID로 연결하지 않았다. 모든 모델의 출력 형식 준수를 보증하지 않는다.

## 새 Codex 세션 명시 호출
실제 Desktop Codex CLI 0.163.0-alpha.10.2를 ephemeral/read-only 새 세션으로 실행했다.
- `$visual-design-review` 이미지 없는 요청: 전역 SKILL.md·공통 절차를 실제 읽고 입력 요청. turn.completed 확인.
- 최종 보강본에 워드마크·팔레트 설명만 제공: SKILL.md·rubric·공통 절차를 읽고 미제공 적용물은 미검증이며 결함·Opportunity·Strength가 아니라고 답했다.

첫 세션은 Windows 셸 출력 인코딩 문제가 있었고 최종 세션은 Python UTF-8로 읽었다. 문서 자체는 UTF-8이며 YAML 검사를 통과했다. 기존 MCP 경고는 스킬 검증 근거로 사용하지 않았다.

## 남은 제한
실제 사용자 작품·다페이지 출판물·복잡한 레터링, 인쇄 PDF 분판·도련·폰트 포함·유효 해상도·실물 교정, 역사 원자료 진위는 미검증이다. 합성 이미지 테스트로 이를 보증하지 않는다.
자동 활성화는 정상 description/default implicit invocation을 사용한다. 새 세션 명시 호출은 확인했지만 모든 자연어 자동 라우팅은 미검증이다. 일반 Chat은 저장소 문서를 읽도록 요청해야 하며 Codex 스킬이 자동 설치되지 않는다.

서브에이전트는 공개 소스 조사와 읽기 전용 모의/이미지 검증만 수행했다. 쓰기 범위는 없었다. 최종 보정·설치·통합·공개 파일 검사는 메인 에이전트가 담당했다. 공개 패키지에는 사용자 작품·개인 경로·로컬 세션 로그·자격증명을 포함하지 않았다.
