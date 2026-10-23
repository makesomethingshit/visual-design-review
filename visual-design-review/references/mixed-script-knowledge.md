# Korean–Latin mixed-script knowledge — draft corpus (#8)

> **Research draft, not a runtime validator.** Applies only when the content is text and the relevant medium/script is known. Every candidate below is a *rule inventory entry*, not an automatic finding. Actual authority and current document status must be checked against the linked source before release.

This corpus instantiates [rule-contract](rule-contract.md). The three independent judgments are **source authority/strength**, **observed evidence**, and **design severity**. Do not infer one from another.

| id | kind / strength | scope | condition / exception | method / unresolved | source |
| --- | --- | --- | --- | --- | --- |
| MIX-001 | NORMATIVE / CONDITIONAL | Korean horizontal body, line layout | Determine whether actual start/end break positions are available; language-specific tailoring and editorial conventions apply | UAX #14 opportunities + rendered lines; engine missing → UNVERIFIED | [Unicode UAX #14](https://www.unicode.org/reports/tr14/), [KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/) |
| MIX-002 | NORMATIVE / CONDITIONAL | Korean+Latin mixed runs | Identify which run contains actual Latin text before applying run-level shaping assumptions | inspect run segmentation; no raw text → UNVERIFIED | [KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/), [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos) |
| MIX-003 | NORMATIVE / CONDITIONAL | Source font files, glyph coverage | cmap absence is **not** proof of actual fallback renderer behavior; variation/complex shaping may affect display | cmap coverage checked separately from actual renderer-selected fonts | [CSS Fonts 4](https://www.w3.org/TR/css-fonts-4/), [OpenType cmap](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap) |
| MIX-004 | NORMATIVE / CONDITIONAL | Actual shaped text run | `x_advance` and `x_offset` have distinct meanings; do not add positioning twice | source shaping data required | [HarfBuzz positions](https://harfbuzz.github.io/harfbuzz-hb-buffer.html#hb-glyph-position-t) |
| MIX-005 | NORMATIVE / CONDITIONAL | Explicit SI-style numerals+units | Semantic spacing and exception set belong to a specified SI editorial policy; product identifiers may be exempt | parser + editorial scope, do **not** correct unparsed raster text | [KRISS SI](https://www.kriss.re.kr/) |
| MIX-006 | PERCEPTUAL / ADVISORY | Korean–Latin paired face | nominal size/weight alone does not establish optical size or density equivalence | actual render + independent expert comparison | [KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/) |
| MIX-007 | CONTEXTUAL / PROJECT_POLICY | user-approved project only | A–H settings apply to first *comparison* draft only when requested or explicitly opted in; they are not shared defaults | [typography-presets](typography-presets.md) | User approval, 2026-10-21 |
| MIX-008 | CONTEXTUAL / ADVISORY | print vs web graphic design | Print alignment convention is not automatically a web WCAG requirement or a visual quality score | brief + medium + rule applicability | [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/) |

## Risk controls

- **W3C KLReq is a Group Note Draft**, not a universal compliance standard. It contains unfinished sections. Do not mark every recommendation REQUIRED.
- `NORMATIVE` means the **subject** is a formal convention/standard; whether it is legally, technically or editorially REQUIRED is separate.
- UI/web accessibility and print production are separate application profiles. The existing skill does **not** become a general CSS/web accessibility auditor.
- Without text/font/render metadata, report visible symptoms and possible hypotheses, not fabricated font names or exact points.
- Prioritized to build a small evidence-backed inventory before any mechanical enforcement. Source status, exceptions and scope need a dedicated human research pass.

## Representative counterexamples

1. A KLReq recommendation conflicts with an explicitly supplied experimental typesetting brief → record conflict, not blanket Critical.
2. A serif Latin font has the same nominal 10pt as Korean body but a different apparent density → propose pairwise render evaluation, not a universal 1.05× scaling constant.
3. A raster screenshot of a missing-looking symbol has no original font files → cannot claim renderer fallback was confirmed.
4. A Korean print paragraph is left aligned by design → not automatically a defect under a print justification convention.
5. Another user's project starts fresh → don't silently apply the previous user's A–H project-policy values.

See #9 for optional deterministic inspection and #10 for perceptual pairing research. Neither is implemented by this Markdown corpus.
