# Korean–Latin mixed-script knowledge — reviewed source corpus (#8)

> **Research corpus, not a runtime validator.** The rows below are evidence-bound inventory entries. Source authority, observed design evidence, and design severity remain separate axes. A source citation does not prove that the current artwork conforms or fails.

Reviewed 2026-10-23 (Asia/Seoul). The source URLs use dated or versioned publications where the publisher provides them. `UNVERIFIED` means the required text, run, renderer, output, or human decision is not present.

## Source ledger

| source | exact section | version / status | bounded use |
| --- | --- | --- | --- |
| [Unicode UAX #14](https://www.unicode.org/reports/tr14/tr14-57.html) | §4 Conformance, §4.1 Conformance Requirements, §6.1 Non-tailorable Line Breaking Rules, §6.2 Tailorable Line Breaking Rules | Unicode 18.0.0, Revision 57, 2026-09-01; stable, approved Unicode Standard Annex | Baseline line-break properties and conformance conditions; tailoring and higher-level layout remain visible inputs |
| [W3C KLReq](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/) | §7.1.1–§7.1.4 Line Breaking Rules, Line Head/End Restrictions, Word Break Restrictions; §7.2.1 Line Adjustment Process | 2026-03-21 W3C Group Note Draft; not endorsed by W3C or its Members, and may change | Korean layout requirements and examples for the relevant writing mode; never a universal compliance rule |
| [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos) | Overview, Basic glyph positioning, GPOS table organization, Lookup types 1–2 | OpenType 1.9.1 technical specification | Distinguishes glyph placement, advance, script/language selection, and positioning features |
| [OpenType `cmap`](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap) | Table overview | OpenType 1.9.1 technical specification | Character-to-glyph coverage only; it does not identify the font selected by a renderer |
| [CSS Fonts Level 4](https://www.w3.org/TR/2026/WD-css-fonts-4-20261022/) | §5 Font Matching Algorithm; cluster matching and installed font fallback | 2026-10-22 W3C Working Draft; not endorsed and may change | Web font selection/fallback conditions only; not a print-font or visual-quality oracle |
| [HarfBuzz `hb_glyph_position_t`](https://harfbuzz.github.io/harfbuzz-hb-buffer.html#hb-glyph-position-t) | `hb_buffer_get_glyph_positions()` and `hb_glyph_position_t` | Current upstream API manual; runtime library version must be recorded by a real shaping run | Shaped `x_advance`/`y_advance` versus `x_offset`/`y_offset`; no version is inferred from the webpage |
| [KRISS SI](https://www.kriss.re.kr/menu.es?mid=a10302060000) | `SI 단위기호`, `SI 단위기호의 대수학` | KRISS institutional guidance page, accessed 2026-10-23; scope is SI notation, not arbitrary product text | Number/unit spacing and exceptions; cite the source’s semantic scope before applying it |
| [WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/) | §1.4.12 Text Spacing | W3C Recommendation, 2024-12-12 | Web content and user override test; it does not grade print aesthetics |

## Rule inventory

Each row preserves the fields required by [rule-contract](rule-contract.md): source version/status, scope, conditions, exceptions, verification method, and evidence state.

| id | kind / strength | source section(s) | scope / conditions | exceptions / non-applicability | verification method / evidence |
| --- | --- | --- | --- | --- | --- |
| MIX-001 | `NORMATIVE` / `CONDITIONAL` | UAX #14 §§4.1, 6.1–6.2; KLReq §§7.1.1–7.1.4 | Unicode text with the actual language/script, writing direction, line-break mode, raw text, and produced line positions available | UAX permits disclosed tailoring and higher-level overrides; KLReq lets the document author choose character- or word-based Korean breaking and has separate vertical-writing choices | Compare implementation opportunities and actual lines against the selected profile; missing text, line output, or engine is `UNVERIFIED` |
| MIX-002 | `NORMATIVE` / `CONDITIONAL` | OpenType GPOS `Overview`, `Basic glyph positioning`, `GPOS table organization`; Lookup types 1–2 | A real glyph run with font, script, language system, selected features, direction, and shaping output | Placement is not advance; a basic layout path without GPOS is not proof that a GPOS feature was applied; variable-feature conditions can change lookup selection | Inspect shaped glyphs and positions from the actual engine; source text or shaping data absent is `UNVERIFIED` |
| MIX-003 | `NORMATIVE` / `CONDITIONAL` | OpenType `cmap` `Table overview`; CSS Fonts 4 §5 and cluster/fallback sections | A named source font and the actual renderer’s matching/fallback context are available | `cmap` only maps characters to a default glyph index; missing coverage does not prove which fallback face rendered; variation-selector clusters have separate fallback rules | Check coverage separately, then inspect renderer-selected faces or output; screenshot-only fallback claims are `UNVERIFIED` |
| MIX-004 | `NORMATIVE` / `CONDITIONAL` | HarfBuzz `hb_glyph_position_t`; OpenType GPOS `Basic glyph positioning` | A real shaped run records engine/library version, font/axis, direction, script, language, and positions | `x_offset`/`y_offset` move glyph placement and must not be added to logical advance; BASIC Pillow layout is not this evidence | Record `x_advance`/`y_advance` and offsets from a shaping API; without that output, retain `UNVERIFIED` |
| MIX-005 | `NORMATIVE` / `CONDITIONAL` | KRISS `SI 단위기호`; BIPM [SI Brochure 9th ed.](https://doi.org/10.59161/AUEZ1291) §5.4.4 | The token is a semantic quantity followed by a unit symbol and the selected SI/editorial profile applies | KRISS exempts plane-angle symbols °, ′, ″ from the number-unit space; product identifiers, brand text, and unparsed raster text are outside this rule | Inspect source text and semantic tokenization; do not rewrite or flag a product identifier from an image alone; absent scope is `UNVERIFIED` |
| MIX-006 | `PERCEPTUAL` / `ADVISORY` | No primary standard here establishes a universal Korean–Latin pairing score; OpenType/GPOS sources describe mechanics, not preference | An actual rendered pair, fixed text/size/width/medium, stated brief, and independent comparison are available | Equal nominal size/weight is not optical equivalence; no universal x-height multiplier or pair score is inferred | Blind A/B/tie/context-dependent comparison with reasons and counter-interpretation; without human comparison, `UNVERIFIED` |
| MIX-007 | `CONTEXTUAL` / `PROJECT_POLICY` | [Typography presets](typography-presets.md), user approval recorded 2026-10-21 | Apply to an explicitly opted-in current task, or to an independently confirmed active profile for the current project, and only within its stated medium/task | Do not silently inherit to another project, existing-artwork critique, vertical writing, or a different brief; an active profile does not require repeat opt-in; this is not an empirical optimum | Confirm current-task opt-in or independently confirm the active current-project profile; preserve the policy label and report no general design conclusion |
| MIX-008 | `CONTEXTUAL` / `ADVISORY` | WCAG 2.2 §1.4.12; KLReq §7.2.1 | WCAG applies to content implemented in markup languages and tests loss of content/functionality under user text-spacing overrides; KLReq applies only when its Korean layout context is selected | WCAG’s language/script exception and web scope do not turn print alignment into a compliance score; KLReq is a Group Note Draft | Record medium, implementation, user override, and supplied goal; cross-medium transfer is `UNVERIFIED` |

## Explicit applicability fields

These keyed rows supplement the conditions, exceptions, source version/status and
verification method in the inventory. `authority` describes the source, not an
automatic requirement or severity. Unknown per-artwork inputs stay `UNVERIFIED`.

| rule_id | authority | platform | language | writing_mode |
| --- | --- | --- | --- | --- |
| MIX-001 | Unicode Standard Annex; W3C Group Note Draft | Unicode layout engines for print/web/mobile; selected implementation required | actual language/script required; KLReq Korean | actual direction required; horizontal/vertical KLReq choices stay separate |
| MIX-002 | Microsoft OpenType technical specification | OpenType-capable shaping engine | actual script/language system required | actual run direction required |
| MIX-003 | Microsoft OpenType specification; W3C CSS Working Draft | cmap for source fonts; CSS fallback only in web/mobile-web renderer | actual text and script/cluster required | renderer direction/context required; no universal vertical fallback claim |
| MIX-004 | HarfBuzz API documentation; OpenType specification | actual HarfBuzz shaping run | actual script/language required | actual run direction required; x/y axes retained |
| MIX-005 | KRISS institutional SI guidance; BIPM SI Brochure | SI/editorial profile in print/web/mobile | semantic quantity/unit, independent of surrounding language | source notation; no inferred vertical-layout requirement |
| MIX-006 | independent expert judgement; no universal normative authority | fixed print/display/mobile context | Korean–Latin sample and intended readers | fixed for comparison; no transfer across directions |
| MIX-007 | current-task user opt-in or confirmed current-project approval | only the approved project medium | only the approved project language/context | only the approved direction; no automatic vertical transfer |
| MIX-008 | W3C Recommendation; W3C Group Note Draft | WCAG markup-based web/mobile-web; KLReq selected Korean layout | applicable language/script and WCAG exceptions | actual direction required; no cross-medium inference |

## Source reuse / reproduction record

Reviewed 2026-10-24. This repository contains independently worded summaries and
links, not redistributed source documents, tables or illustrations. A source's
license is not inherited by this repository, and a software license is not
silently assigned to an unrelated document. Recheck the exact edition's notice
before adding any copied material.

| source | license / notice evidence | reproduction boundary adopted here |
| --- | --- | --- |
| Unicode UAX #14 | [Unicode license](https://www.unicode.org/license.txt): Unicode License V3 covers data/software and associated documentation | Preserve required copyright/permission notices for covered copies; confirm the report's own terms before reproduction; summary/link only here |
| W3C KLReq, CSS Fonts, WCAG | [W3C Document License 2023](https://www.w3.org/copyright/document-license-2023/) for documents linking that notice | Copies require source URL, copyright and document status; derivative technical specifications are restricted; do not copy source text here |
| Microsoft OpenType GPOS/cmap | [Microsoft Learn terms](https://learn.microsoft.com/en-us/legal/termsofuse); document-specific exceptions must be checked | No blanket redistribution grant inferred; technical facts summarized with source links, no copied tables or figures |
| HarfBuzz API | [upstream COPYING](https://github.com/harfbuzz/harfbuzz/blob/main/COPYING): Old MIT terms for covered software/documentation, with file-level exceptions | Preserve applicable notices if reusing covered material; no API prose/code copied here |
| KRISS SI | [cited page](https://www.kriss.re.kr/menu.es?mid=a10302060000); no page-specific reuse grant identified in this review | Reproduction permission remains UNVERIFIED; own summary/link only, no copied text or graphics |
| BIPM SI Brochure | [cited edition](https://doi.org/10.59161/AUEZ1291); edition-specific reproduction permission not established in this review | Permission remains UNVERIFIED; reference and own summary only; no brochure pages copied |
| Local project A–H policy | user-approved project policy, not an external source license | Keep approval provenance and current-project scope; no permission for other projects inferred |

## Interpretation controls

- `NORMATIVE` names the source domain; it does not automatically mean `REQUIRED` for the current design. `REQUIRED` needs an applicable source, conditions, and evidence.
- UAX #14 tailoring, KLReq’s draft status, CSS Fonts’ web scope, KRISS SI semantic scope, and the project-policy opt-in are conditions, not footnotes.
- A source match cannot establish a current design defect or its severity. Report the visible observation, supplied-goal loss, and source interpretation separately.
- No source in this corpus authorizes a fixed Korean–Latin scale, universal font pair, automatic A–H inheritance, or a Critical/Major rating.

## Representative counterexamples

1. A KLReq line-break convention conflicts with an explicitly supplied experimental brief: record the conflict and goal evidence; do not blanket-label it Critical.
2. A serif Latin face and Malgun Gothic can share a nominal size while producing different apparent density: request a controlled render comparison, not a universal scaling constant.
3. A screenshot that looks like fallback has no `cmap` or renderer-selection evidence: report the visible symptom and keep fallback `UNVERIFIED`.
4. A Korean print paragraph is left aligned by design: do not transfer a web or draft convention into a defect without a supplied goal and applicable profile.
5. `35 mm` may be an SI quantity, while a product code containing `35mm` may not be: resolve semantics before applying MIX-005.
6. A new user’s project starts fresh: do not silently apply another project’s A–H policy.

See #9 for optional deterministic inspection and #10 for the separate perceptual pairing study. Neither is implemented by this corpus.
