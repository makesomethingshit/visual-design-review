# Mixed text probe: limits / examples (#9)

Draft executable subset; not a full Unicode UAX #14 implementation. The public
boundary is `check(payload)` plus the CLI; both are read-only.

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

Font/render evidence is kept in the optional test-side reproducer so the runtime
API does not pretend to own shaping. It uses an already installed Pillow runtime
when available and records source, font, and render hashes. Pillow rendering is
evidence that a file rendered; it does not establish glyph coverage or fallback.

**Input capabilities and rule sources**

| Check | Supported evidence | Rule source and strength |
| --- | --- | --- |
| `MIX-005` | UTF-8 source text and an explicit `si_spacing` profile | Caller project policy; `PROJECT_POLICY`, not SI conformance |
| `MIX-001` | Caller-supplied `rendered_lines` that concatenate to the source | Unicode UAX #14 plus W3C KLReq 2026-03-21 Group Note Draft; `CONDITIONAL`; UAX version and shaping remain `UNVERIFIED` |
| `MIX-003` | No font/renderer input in the runtime; optional test-side reproducer only | OpenType/HarfBuzz technical sources; `CONDITIONAL`; coverage/fallback remains `UNVERIFIED` |

Flat images are `BLOCKED` for this probe because it has no OCR or layout evidence.

Outputs `PASS` only for narrowly implemented checks. `NO_SIMPLE_ANOMALY` is **not** a declaration of line-break correctness; `UNVERIFIED` remains mandatory for missing actual font fallback evidence. This PoC does not validate an entire SI policy, typography, readability, or print correctness.

**Known limitations:** no cmap parser, no actual font fallback detection, no full KLReq tailoring, no line-breaking layout engine, no PDF/Adobe integration, no image OCR. The optional test-side Pillow path records a real render and hashes but does not turn `MIX-003` into `PASS`. A finding is not automatically Major/Critical.

SI opt-in must be a JSON boolean. A string such as `"false"` is invalid and must not
activate inspection. If no supported standalone unspaced unit token is recognized,
the narrow check returns `NOT_APPLICABLE`, not a verified SI `PASS`. This includes
already-spaced text and ambiguous tokens attached to words; full SI validation remains
outside this probe. Exception matching only applies to recognized exact tokens.

**Verification status:** unit/CLI execution, source fixtures, and optional local
font/render evidence are recorded in [the local execution report](../../docs/validation/mixed-text-probe-2026-10-23.md).
The fixture pair proves only the supported simple candidate paths. It is not
actual font fallback, full renderer conformance, or full SI evidence.

## Versioned result vocabulary

The output `schema: mixed-text-probe-v0` identifies this PoC's deliberately narrower
vocabulary; it is not the issue's proposed general PASS/FAIL validator contract.

| v0 status | Meaning / general-contract boundary |
| --- | --- |
| `FINDING` | Supported text-pattern or line-boundary candidate; not a confirmed `FAIL` or a severity decision |
| `NO_SIMPLE_ANOMALY` | No supported line-boundary candidate; general correctness remains `INCONCLUSIVE`, never a line-break `PASS` |
| `NOT_APPLICABLE` | No enabled/applicable limited check; no conformance verdict |
| `PASS` | Recognized exact tokens were explicitly exempted by the supplied project policy only |
| `UNVERIFIED` | Required font/render evidence unavailable |
| `BLOCKED` | Supplied input cannot support the requested limited check |

Callers must not coerce candidate/absence statuses into FAIL/PASS. A future full
validator must version its result contract and retain these evidence distinctions.