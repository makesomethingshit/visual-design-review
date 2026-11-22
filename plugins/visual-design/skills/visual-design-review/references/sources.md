# 출처와 통합 기록

조사일: 2026-10-18 (Asia/Seoul). 아래 SHA는 조사 당시 기본 브랜치 HEAD다.
외부 문서는 분석 자료로만 읽었으며 원본 명령·스크립트·hooks를 실행하지 않았다.
이 스킬은 원문·템플릿을 합친 배포물이 아니라 일반 방법론을 독자적인 한국어
프로토콜로 재작성한 것이다. 원본 이미지·브랜드·제3자 자료는 포함하지 않는다.

| 소스 | 기본 브랜치 commit SHA | 확인한 라이선스 | 활용 범위 |
| --- | --- | --- | --- |
| A [Designer Type](https://github.com/SaplingSticky/designer-type/tree/753d35c3de508a15c246e7cf55feedf1539a30ff) | 753d35c3de508a15c246e7cf55feedf1539a30ff | 루트 LICENSE: MIT, Copyright 2026 Ilzat | 관찰 우선, 초점·위계·리듬·정합성, 창작 결정 존중, 역사적 렌즈 |
| B [World-Class Graphic Director](https://github.com/vibhuwolf/world-class-graphic-director/tree/e9fb229873aede6fa89b4db72664f31356796033) | e9fb229873aede6fa89b4db72664f31356796033 | 라이선스 파일·명시적 허가 확인 안 됨 | 콘셉트와 조형 관계·차별성이라는 일반 방법론만 참고. 원문·파일·예제 복제 없음 |
| C [Infographic Editorial Design](https://github.com/dpan538/infographic-editorial-design-skill/tree/aa77efed2c8a798e56dae48a47e396adb1595757) | aa77efed2c8a798e56dae48a47e396adb1595757 | 루트 LICENSE: MIT 기반, Copyright 2026 Dai Pan; 스킬 패키지 한정·제3자 제외 조항. API는 NOASSERTION이나 본문 허가 확인 | 레이아웃의 논증, 증거·해석·출처 경계, 정보 구조 |
| D [Critique Composition](https://github.com/Owl-Listener/designer-skills/tree/9a6930cf84a822eb458624bd11c61aac5bbdf224/visual-critique/skills/critique-composition) | 9a6930cf84a822eb458624bd11c61aac5bbdf224 | 루트 LICENSE: MIT, MC Dean; 해당 하위 폴더 별도 라이선스 없음 | 시각적 무게, 여백, 균형, 리듬, 게슈탈트 관계 |
| E [Graphic Designer](https://github.com/wonsukchoi/domain-experts/tree/0101c5456f7e4d718a5dd7657c4514448039a303/roles/graphic-designer) | 0101c5456f7e4d718a5dd7657c4514448039a303 | 루트 LICENSE: MIT, Wonsuk Choi and contributors; 해당 하위 폴더 별도 라이선스 없음 | 타이포그래피 시스템, 브랜드 일관성, 색의 기능·재현, 제작 조건 |
| F [Desktop Publisher](https://github.com/wonsukchoi/domain-experts/tree/0101c5456f7e4d718a5dd7657c4514448039a303/roles/desktop-publisher) | 0101c5456f7e4d718a5dd7657c4514448039a303 | E와 동일 저장소·SHA·루트 MIT | 편집 구조, 조판·밀도, 최종 크기 기준 해상도, preflight |

## 실제 읽은 파일
모든 경로는 위에 고정한 저장소 SHA를 기준으로 한다.
- A: SKILL.md, references/design-masters.md, LICENSE.
- B: skills/world-class-graphic-director/SKILL.md,
  skills/world-class-graphic-director/references/master-design-principles.md.
  저장소 파일 목록에서 LICENSE/COPYING 부재를 확인. 공개 저장소라는 사실을
  재배포 허가로 해석하지 않는다.
- C: SKILL.md, references/grid-system.md, references/evaluation-rubric.md,
  references/publication-boundaries.md, references/legibility-standards.md, LICENSE.
- D: visual-critique/skills/critique-composition/SKILL.md, LICENSE.
- E: roles/graphic-designer/SKILL.md, references/artifacts.md, red-flags.md,
  vocabulary.md (references 경로는 해당 role 아래), LICENSE.
- F: roles/desktop-publisher/SKILL.md, 해당 references/artifacts.md,
  red-flags.md, vocabulary.md, LICENSE.
E/F의 전체 references는 읽기 전용 조사 에이전트가 확인했으며 메인 에이전트는
SKILL.md·red-flags.md·루트 LICENSE를 추가로 직접 확인했다.

## 중복과 충돌의 해결
- A의 Focus/Hierarchy는 주목·독해, Rhythm은 구성/편집 리듬,
  Coherence는 콘셉트/시스템 정합성으로 합쳐 중복 지적하지 않는다.
- A의 질문만/해결책 금지와 B의 직접적 디렉션은 기본 원인·수정 제안,
  논쟁적 선택에 대안·질문, 최종 결정은 사용자라는 정책으로 통합한다.
- B의 기본 점수제는 채택하지 않는다. Keep/Fix/Push는 유지·수정·선택 실험의
  일반적인 피드백 구분으로 독자적으로 정의하며 수치 점수는 요청 시만 쓴다.
- B의 특정 최신 미감 선호·효과 금지, C의 고정 px/음수 자간 금지·기본 모듈
  그리드·중립 산세리프는 보편 규칙으로 가져오지 않는다.
- C의 출처·주장 구분은 정보디자인에 적용한다. 모든 표현적 요소에 출처나
  단일 의미를 강요하지 않는다. 내용의 진위와 시각적 추적 가능성을 구분한다.
- D/E/F의 정렬·대비·제작 지침은 목적·언어·관람 조건·제작처 규격으로 한정한다.
  웹 접근성·모바일 수치 기준을 포스터·실험 활자에 일괄 적용하지 않는다.
- 각 원본의 심각도 체계를 복제하지 않고 유형·심각도·확실성을 분리한다.
  Strength의 심각도는 N/A로 정의해 강점을 억지로 결함으로 환산하지 않는다.

## 재사용 경계
독자 작성한 일반 방법론만 포함했으며 원본의 코드·문서 파일·상당한 문구를
복제하지 않았다. 라이선스가 확인되지 않은 B는 원문 재배포 대상에서 제외한다.
원본 자료를 향후 직접 복제한다면 해당 고정 SHA의 실제 허가 조건과 저작권
표시를 다시 검토하고 필요한 고지를 동봉한다. 스킬 출처가 사용자 작품·
서체·데이터·브랜드 자산의 재사용 권한을 부여하지 않는다.

## 추가 연구 참고 문헌 — 정량적 역분석 아키텍처 (2026-10-21)

아래는 신규 프로토콜의 **연구적 배경**이다. 출처 코드·이미지·데이터셋을 복제하거나
실험 결과를 우리 스킬의 검증 결과로 간주하지 않는다.

- [ReDesign (2026)](https://arxiv.org/html/2607.25565): 레이어 계층의 단계별 확장·검증과 수정 가능성.
- [Vector Layout Transfer (2023)](https://arxiv.org/html/2309.11635v1): 레이아웃 관계의 추출·전달.
- [Re-typograph (2015)](https://doi.org/10.1117/12.2075813): 서체 파라미터 역추정 문제의 비유일성.
- [Reverse-engineering information presentations (2023)](https://link.springer.com/article/10.1007/s44267-023-00010-1): 계층·그룹 추론.
- [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos), [Google Fonts metrics](https://googlefonts.github.io/gf-guide/metrics.html): 자형·조판 메트릭의 기술 정의.
- [OERT composition](https://www.oert.org/en/composition-and-modules/), [EU Data Visualisation Guide](https://data.europa.eu/apps/data-visualisation-guide/respecting-proportions): 모듈 구조와 면적 비례 표현.
