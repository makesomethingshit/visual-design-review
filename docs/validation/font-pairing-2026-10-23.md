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

The fixture records FP-01 and FP-03 as `latin_family` comparisons and FP-02 as a `latin_weight` comparison. FP-03 uses Arial versus Times New Roman, so its earlier `latin_figures` label was metadata drift, not a multi-variable experiment failure.

Verification for this scoped update: fixture validation passed for 3 tasks; a temporary render produced 6 PNGs; the focused unittest passed 2/2. Checked-in PNGs and the prior render manifest/blind packet were not regenerated.

The output manifest contains the actual fixture path/hash and `anchor: left-baseline; baseline derived from the fixed Korean face ascent`.

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

## macOS local regression follow-up — 2026-10-26

On macOS arm64 with Python 3.12.14 and Pillow, the original rendered-pair test
failed because an absent Windows font unconditionally selected Linux-only
`/usr/share/fonts` paths. The temporary test render now selects installed macOS
Apple SD Gothic Neo, Arial and Times New Roman files on Darwin. Linux CI keeps
its provisioned Nanum/DejaVu paths. Missing fonts still fail visibly rather than
being reported as a completed render.

`python -m unittest discover -s tests -p 'test_font_pairing_render.py' -v` passes
2/2, including
actual A/B PNG generation, visible bounds, distinct pixel hashes and a fixed
Korean font hash across the pair. The temporary images are deleted after the
test.

This verifies the local BASIC renderer test with these installed Mac fonts only.
The committed Windows fixtures, PNGs, font hashes and blind packets are unchanged;
no font binary is copied into the repository. Expert blind comparison, shaping
conformance and physical print quality remain unverified.

## Windows metadata consistency — 2026-10-26

FP-03 compares Arial with Times New Roman in the mixed-numbers context; the
controlled variable is now recorded as `latin_family`, not `latin_figures`.
The fixture contract test checks FP-01/FP-03 family and FP-02 weight. After
this metadata change, all six PNGs and both manifests were regenerated with
the installed Windows fonts so the fixture SHA and output records describe
the current input bytes. This is a new BASIC-render run, not new human ratings
or shaping/print verification. No font binaries are included.
