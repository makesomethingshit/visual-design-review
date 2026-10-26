# MIX-001–MIX-008 source-corpus validation — 2026-10-23

This record covers the documentation and static authoring contract in the PR15 worktree. It is not a model-routing run, a line-breaking conformance run, or a visual/expert evaluation.

## Primary-source review

The inventory in [`mixed-script-knowledge.md`](../../visual-design-review/references/mixed-script-knowledge.md) was checked against these first-party sources:

- [Unicode UAX #14 revision 57](https://www.unicode.org/reports/tr14/tr14-57.html), Unicode 18.0.0, §4.1 and §6.1–§6.2: stable annex conformance and disclosed tailoring.
- [W3C KLReq dated 2026-03-21](https://www.w3.org/TR/2026/DNOTE-klreq-20260321/), §7.1.1–§7.1.4 and §7.2.1: Group Note Draft, not W3C-endorsed; Korean paragraph and writing-mode conditions remain applicable inputs.
- [OpenType GPOS 1.9.1](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos), overview/basic positioning/table organization: placement, advance, script/language features, and lookup selection are separate.
- [OpenType `cmap` 1.9.1](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap), table overview: character coverage is separate from renderer-selected fallback.
- [CSS Fonts 4 dated 2026-10-22](https://www.w3.org/TR/2026/WD-css-fonts-4-20261022/), §5 and cluster/fallback sections: Working Draft, web font matching scope.
- [HarfBuzz buffer API](https://harfbuzz.github.io/harfbuzz-hb-buffer.html#hb-glyph-position-t): positions require an actual shaping run and a recorded runtime version.
- [KRISS SI guidance](https://www.kriss.re.kr/menu.es?mid=a10302060000), `SI 단위기호`: number/unit semantics and plane-angle exceptions.
- [WCAG 2.2 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/), §1.4.12: web-content text-spacing override behavior, including its language/script exception.

No source was treated as a universal visual-quality score or as permission to change existing Quick/Deep behavior.

## Local checks

From the repository root:

```text
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tests/check-knowledge-contract.py
git diff --check origin/main...HEAD
```

Actual result in this worktree:

```text
PASS: policy mappings, local docs links, legacy triggers, reference-math examples, print routing guards, documented typography widths
```

`git diff --check origin/main...HEAD` also exited 0. The checks validate repository links and the existing rule contract; they do not prove that #7 opened each source during a real Codex session.

## Remaining Draft gates

- Actual Codex reference-reading and misuse cases in #7: pending.
- Original text, line-break output, font selection, and shaping evidence for a supplied design: pending per case.
- Expert optical judgement and severity: pending; no ratings or conclusions are included here.
