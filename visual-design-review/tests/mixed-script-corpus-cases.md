# Mixed-script research corpus: negative and positive boundaries (#8)

All cases are **research drafts**, not successful Codex runs.

| Case | User request | Expected knowledge behavior | Forbidden result |
| --- | --- | --- | --- |
| K-01 | 한글·영문 혼식 잡지 본문 초안을 설계해줘 | Separate script/run requirements from optical recommendations; ask for actual text/face only when needed for precise measurements | Claim pixel-based glyph metrics without source |
| K-02 | KLReq가 맞으니까 포스터를 무조건 양끝맞춤해 | Treat draft conventions and project intent as separate | Absolute design violation with no target loss |
| K-03 | 이미지에서 실제 대체 글꼴을 찾아줘 | Visible inconsistency can be noted; fallback needs actual font/render evidence | Invent exact font |
| K-04 | SI 표기 지침이 적용된 35 mm 원고를 검사해줘 | Scope requirement and semantic unit spacing; preserve content | Force SI edits on brand/product IDs |
| K-05 | 웹 접근성 기준을 실험적 인쇄 포스터 심미 점수로 바꿔줘 | Explain domain difference, avoid value transfer | Apply numerical compliance threshold outside its scope |
| K-06 | 별도 요청 없이 외부 사용자의 새 본문 초안을 설계해줘 | A–H are project-scoped opt-in | Treat user policy as universal |

## Acceptance (to be executed in #7)

For each case, record the actual references opened, exact section/version/status, resolved language/media/writing-mode conditions, exceptions considered, supported-versus-inferred values, and `BLOCKED` when original text/font/output is inaccessible. Lack of observed execution is not PASS, and this corpus does not supply an expert rating.
