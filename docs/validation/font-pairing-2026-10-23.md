# FP-01–FP-03 local font-pairing render record — 2026-10-23

This record is a reproducibility artifact for PR17. It does not contain Windows font binaries, expert ratings, a preferred pair, or a shaping-engine result.

## Command and environment

From the PR17 repository root:

```text
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe visual-design-review/scripts/font_pairing_render.py --validate-only
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe visual-design-review/scripts/font_pairing_render.py --output-dir docs/validation/font-pairing-2026-10-23
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests/test_font_pairing_render.py -v
git diff --check origin/main...HEAD
```

Actual result after the final rerun: fixture validation passed for 3 tasks; the renderer produced 6 PNGs; the focused unittest passed 2/2; and `git diff --check origin/main...HEAD` exited 0. The output manifest contains the actual fixture path/hash and `anchor: left-baseline; baseline derived from the fixed Korean face ascent`.

The local runtime used Pillow 12.3.0 with `raqm=False`. The script uses `ImageDraw.text` with `ImageFont.Layout.BASIC` and a shared left-baseline anchor; it bounds-checks every segment before saving. It renders Korean runs with `C:\Windows\Fonts\malgun.ttf` and Latin variants with installed `arial.ttf`, `arialbd.ttf`, and `times.ttf`. It does not copy or add those files to the repository.

## Artifacts

- [`render-manifest.json`](font-pairing-2026-10-23/render-manifest.json) records the actual fixture path and SHA-256, installed font names, absolute source paths, byte sizes, font SHA-256 identities, image hashes, and render parameters.
- [`blind-packet.json`](font-pairing-2026-10-23/blind-packet.json) records only A/B labels, parameters, and image hashes; its `ratings` array is empty.
- `blind/FP-01`, `blind/FP-02`, and `blind/FP-03` contain the six generated PNGs. The images contain no font names or A/B preference labels.

The file hash is the font identity for this run. A numeric font version was not available from the installed-library path and is not guessed.

## Evidence boundary

The PNGs demonstrate that the same text and pixel parameters can be rendered with the selected installed font files under the recorded BASIC path and shared baseline anchor. They do not prove optical superiority, a universal pairing rule, fallback selection, kerning quality, or production print behavior. `raqm=False` means this run must not be described as real HarfBuzz shaping.

## Remaining Draft gates

- Independent human A/B/tie/context-dependent ratings, swapped display order, reasons, disagreement, and counter-interpretation: pending.
- Expert status and any recommendation for `typography.md` or `typography-relations.md`: pending.
- Cross-platform shaping, browser/print renderer comparison, and licensed-font redistribution review: pending.
