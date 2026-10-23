# Mixed text probe: limits / examples (#9)

Draft executable subset; not a full Unicode UAX #14 implementation.

Run from repository root (Python 3.10+):
```sh
python -m unittest discover -s tests -p 'test_mixed_text_probe.py'
python visual-design-review/scripts/mixed_text_probe.py examples/mixed-script-input.json
```

**Input schema**
```json
{
  "text": "폭 35mm 끝",
  "profile": {
    "si_spacing": true,
    "except_exact_tokens": [],
    "korean_horizontal_break_check": false
  }
}
```
`rendered_lines` can be provided only when lines actually originate from a renderer or explicit source layout; do not invent them from visual guessing.

Outputs `PASS` only for narrowly implemented checks. `NO_SIMPLE_ANOMALY` is **not** a declaration of line-break correctness; `UNVERIFIED` remains mandatory for missing actual font fallback evidence. This PoC does not validate an entire SI policy, typography, readability, or print correctness.

**Known limitations:** no cmap parser, no actual font fallback detection, no full KLReq tailoring, no line-breaking layout engine, no PDF/Adobe integration, no image OCR. A finding is not automatically Major/Critical.

SI opt-in must be a JSON boolean. A string such as `"false"` is invalid and must not
activate inspection. If no supported standalone unspaced unit token is recognized,
the narrow check returns `NOT_APPLICABLE`, not a verified SI `PASS`. This includes
already-spaced text and ambiguous tokens attached to words; full SI validation remains
outside this probe. Exception matching only applies to recognized exact tokens.

**Verification status:** macOS/Python unit execution and the original failure are
recorded in [the local execution report](../../docs/validation/mixed-text-probe-2026-10-23.md).
This synthetic test evidence is not actual font, renderer, or full SI conformance evidence.
