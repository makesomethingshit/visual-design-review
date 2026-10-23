# 최종 PDF 프리플라이트 증거 계약 — 초안 (#12)

> **현재 구현: PDF + 외부 JSON 보고서의 해시 고정 importer만 제공.** Acrobat, PDF/X, 실제 인쇄 엔진, Adobe 파일 속성을 검사하지 않는다. `PDF_OUTPUT_PREFLIGHTED`를 선언할 수 있는 수준이 아니다.

## 판단 대상 분리

1. **Source object:** InDesign/Illustrator 내부의 텍스트, 레이어, 별색 등 원본 상태
2. **Exported PDF:** 최종 납품 PDF에서 실제 판독 가능한 객체·폰트·색·도련·PDF/X/유효 해상도 등
3. **Physical proof:** 종이/잉크/인쇄기/관찰 조건에서의 결과

PDF 프리플라이트 통과는 1번 또는 3번을 증명하지 않는다. 실제 제작처의 profile 및 출력 조건이 없다면 임의의 해상도·별색 허용값·ICC 조건을 강제하지 않는다. **텍스트 없는 인쇄용 로고도** 실제 해당 조건을 검사해야 한다.

## 외부 검증기 연결 전 데이터 구조

```json
{
  "tool_name": "ACTUAL_ENGINE_REQUIRED",
  "tool_version": "UNKNOWN",
  "profile_id": "USER_PRINT_PROFILE_REQUIRED",
  "checks": [
    {"id": "font-embed", "status": "UNVERIFIED", "page": null, "evidence": null},
    {"id": "bleed-and-trim", "status": "UNVERIFIED", "page": null, "evidence": null},
    {"id": "color-profile", "status": "UNVERIFIED", "page": null, "evidence": null}
  ]
}
```

Use `python visual-design-review/scripts/import_pdf_preflight.py --pdf path/to/final.pdf --report path/to/report.json` to **import**, not validate. It hashes the input PDF and report and places all check results in **UNVERIFIED** even when an unauthenticated report says PASS. This intentional limitation prevents a claimed preflight without actual integration/attestation.

## Follow-up implementation gate

- [ ] Read-only preflight adapter invokes an actual engine with pinned version/profile
- [ ] The report matches the same PDF hash, and execution provenance is independently authenticated
- [ ] Checks are mapped to the printing brief/production profile, with negative fixtures and machine-verifiable evidence
- [ ] Only then promote evidence to `PDF_OUTPUT_PREFLIGHTED`, not `PHYSICAL_PROOFED`
- [ ] Automated fixup remains disabled unless user explicitly authorizes it

## Boundaries

Digital-only logos do not trigger print checks. A print logo without any text can still require color, overprint, fine-stroke, transparency, PDF/X checks. Missing print context is **BLOCKED/UNVERIFIED**, not a PASS.

References: [Acrobat Preflight profile](https://helpx.adobe.com/acrobat/using/preflight-profiles-acrobat-pro.html), [Adobe PDF/X overview](https://helpx.adobe.com/illustrator/using/adobe-pdf-options.html). Capabilities are documented; **not exercised** in this PR.
