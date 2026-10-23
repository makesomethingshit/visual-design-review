# PDF preflight validation — 2026-10-23

This validation covers the assigned read-only PoC only. It does not certify PDF/X, ICC/source colour profiles, overprint, transparency, effective resolution, a physical print, or an expert design judgment.

## Implemented evidence

- `check_pdf_preflight.py` requires an exact `vdr-print-contract-v1` profile and binds the result to the PDF byte SHA-256, profile SHA-256, checker version, and Poppler tool paths/versions.
- The checker snapshots the PDF bytes into a private temporary file before any Poppler call, records both source and inspected hashes, and rejects `--output` paths that resolve to the PDF/profile or an existing hardlink/same file.
- `pdfinfo -box` checks TrimBox and BleedBox on every page.
- `pdffonts` checks font embedding on every page when the executable is available. A textless PDF is `NOT_APPLICABLE` for font embedding; missing `pdffonts` is `BLOCKED`.
- `pdftoppm` checks the actual 72 dpi default PPM rendered pixels against the explicit `grayscale` profile. This does not prove ICC or source colour-space compliance.
- PDF/X and physical print remain explicit `UNVERIFIED` checks. No automated fixup is performed.

## Reproducible fixtures and commands

`tests/test_pdf_preflight.py` generates valid normal and intentional-defect PDFs with the standard library. The normal fixture has matching A4 trim/bleed boxes and grayscale output. The defect fixture has an incorrect BleedBox, an unembedded Helvetica font, and a red rendered rectangle.

```text
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -p test_pdf_preflight.py -v
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe visual-design-review/scripts/check_pdf_preflight.py --pdf <normal.pdf> --profile <profile.json> --output <normal-report.json>
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe visual-design-review/scripts/check_pdf_preflight.py --pdf <intentional-defect.pdf> --profile <profile.json> --output <defect-report.json>
```

The dedicated Linux CI step runs the same unittest module. The tests assert actual fixture results and fail-closed behavior when an optional Poppler executable is unavailable; CI does not install Python packages or alter the repository dependency policy.

## Local tool evidence

- Bundled Python: 3.12.14.
- Bundled `pdfinfo`: Poppler 26.07.0.
- Bundled `pdftoppm`: Poppler 26.07.0.
- `pdffonts` was not present at the supplied Poppler path in this run. The local font checks therefore remain `BLOCKED`; the defect fixture's trim/colour failures and the normal fixture's trim/colour passes still execute against the real PDF bytes.
- `reportlab 4.4.9` and `pypdf 6.10.0` are installed in the local bundled runtime, but the checker does not import either package and no dependency was added.

The remaining Draft gates are a production-approved pinned Poppler/profile, source colour/ICC and PDF/X/prepress coverage, and physical print evidence. This partial checker must not be promoted to `PDF_OUTPUT_PREFLIGHTED` or `PHYSICAL_PROOFED`.
