# 최종 PDF 프리플라이트 증거 계약 — 초안 (#12)

> **현재 구현: 외부 보고서 importer와 Poppler 기반의 제한적 read-only PDF 검사기.** Acrobat, PDF/X, ICC/source colour profile, 실제 인쇄 엔진, Adobe 파일 속성을 검사하지 않는다. `PDF_OUTPUT_PREFLIGHTED`를 선언할 수 있는 수준이 아니다.

## 판단 대상 분리

1. **Source object:** InDesign/Illustrator 내부의 텍스트, 레이어, 별색 등 원본 상태
2. **Exported PDF:** 최종 납품 PDF에서 실제 판독 가능한 객체·폰트·색·도련·PDF/X/유효 해상도 등
3. **Physical proof:** 종이/잉크/인쇄기/관찰 조건에서의 결과

PDF 프리플라이트 통과는 1번 또는 3번을 증명하지 않는다. 실제 제작처의 profile 및 출력 조건이 없다면 임의의 해상도·별색 허용값·ICC 조건을 강제하지 않는다. **텍스트 없는 인쇄용 로고도** 실제 해당 조건을 검사해야 한다.

## 명시적 print contract와 실제 검사 범위

검사기는 사용자/제작처가 제공한 JSON profile 없이는 실행되지 않는다. profile은 정확히 다음 필드를 가져야 하며 SHA-256으로 결과에 묶인다.

```json
{
  "schema": "vdr-print-contract-v1",
  "profile_id": "a4-3mm-grayscale-v1",
  "trim_box_points": [0, 0, 595.28, 841.89],
  "bleed_box_points": [-8.5, -8.5, 603.78, 850.39],
  "box_tolerance_points": 0.02,
  "require_embedded_fonts": true,
  "allowed_rendered_color": "grayscale"
}
```

`check_pdf_preflight.py`는 `pdfinfo -box`로 페이지별 TrimBox/BleedBox, `pdffonts`로 페이지별 폰트 포함 여부, `pdftoppm`의 72 dpi 기본 PPM 렌더 바이트로 profile이 요구한 grayscale만 검사한다. 검사 전에 PDF bytes를 private temporary snapshot으로 복사하고 모든 도구가 snapshot을 읽도록 하며, 결과에 source/inspected PDF hash가 함께 기록된다. `--output`은 입력 PDF/profile과 같은 경로·symlink·hardlink를 거부한다. 결과에는 profile hash, 검사기 버전, 실행 도구 경로·버전 및 각 페이지의 실제 값/렌더 hash가 포함된다. Poppler 실행 파일이 없거나 PDF가 엔진에서 거부되면 해당 검사는 `BLOCKED`로 남는다.

`allowed_rendered_color`는 PDF source colour space나 ICC/output intent를 검사하지 않는다. `any`는 색상 제한이 없는 profile이므로 `NOT_APPLICABLE`이며, PDF/X·ICC·overprint·별색·투명도·유효 해상도는 이 PoC의 범위 밖이다.

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

Use `python visual-design-review/scripts/check_pdf_preflight.py --pdf path/to/final.pdf --profile path/to/print-contract.json` for the limited actual checks. Use `python visual-design-review/scripts/import_pdf_preflight.py --pdf path/to/final.pdf --report path/to/report.json` to **import**, not validate. The importer hashes the input PDF and report and places all imported check results in **UNVERIFIED** even when an unauthenticated report says PASS. The actual checker never consumes that external report.

## Follow-up implementation gate

- [x] Read-only adapter invokes Poppler for the limited TrimBox/BleedBox, font, and rendered-colour checks
- [x] The report matches the same PDF hash and records checker/tool/profile provenance
- [x] Checks are mapped to an explicit profile with reproducible normal/defect fixtures and machine-verifiable evidence
- [ ] Pin a production-approved Poppler version and validate source colour/ICC, PDF/X, overprint, transparency, resolution, and other required prepress conditions
- [ ] Only then promote evidence to `PDF_OUTPUT_PREFLIGHTED`, not `PHYSICAL_PROOFED`
- [ ] Automated fixup remains disabled unless user explicitly authorizes it

## Boundaries

Digital-only logos do not trigger print checks. A print logo without any text can still require color, overprint, fine-stroke, transparency, PDF/X checks. Missing print context is **BLOCKED/UNVERIFIED**, not a PASS.

References: [Acrobat Preflight profile](https://helpx.adobe.com/acrobat/using/preflight-profiles-acrobat-pro.html), [Adobe PDF/X overview](https://helpx.adobe.com/illustrator/using/adobe-pdf-options.html). Capabilities are documented; **not exercised** in this PR.
