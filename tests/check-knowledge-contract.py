#!/usr/bin/env python3
"""Static authoring contract checks. These do NOT validate actual Codex skill routing."""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "visual-design-review"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise AssertionError(reason)


def check_preset_mapping() -> None:
    text = read(PKG / "references/typography-presets.md")
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if line.startswith("| "):
            cells = [v.strip() for v in line.strip().strip("|").split("|")]
            if cells and cells[0] in "ABCDEFGH" and len(cells[0]) == 1:
                check(cells[0] not in rows, f"Duplicate policy {cells[0]}")
                rows[cells[0]] = cells
    check(set(rows) == set("ABCDEFGH"), f"Missing or extra preset rows: {set(rows)}")

    # Check the ID-to-value association, not merely presence of 1.7/1.5/2.0.
    expected_ratios = {"A": Decimal("1.7"), "B": Decimal("1.5"),
                       "C": Decimal("2.0"), "D": Decimal("2.0")}
    for code, expected in expected_ratios.items():
        check(len(rows[code]) == 4, f"Malformed ratio row {code}")
        match = re.search(r"\*\*(\d+(?:\.\d+)?)\*\*", rows[code][2])
        check(match is not None and Decimal(match.group(1)) == expected,
              f"Wrong language leading: {code} should be {expected}")
        pt = re.search(r"(\d+)pt", rows[code][3])
        check(pt is not None and Decimal(pt.group(1)) == Decimal(10) * expected,
              f"Wrong leading example: {code}")

    expected_strings = {"E": "10pt", "F": "30칸",
                        "G": "Tracking 0", "H": "왼끝맞춤"}
    for code, required in expected_strings.items():
        check(len(rows[code]) == 3 and required in rows[code][1],
              f"Wrong print-first preset mapping {code}")
    for guard in ("USER_APPROVED_PROJECT_POLICY", "명시된 사용자",
                  "기존 작품 비평", "세로쓰기", "PROJECT_INITIAL_PRESET"):
        check(guard in text, f"Missing preset condition/guard {guard}")


def check_links() -> None:
    # Verify relative links as GitHub resolves them, relative to each Markdown file.
    docs = [
        ROOT / "README.md",
        ROOT / "docs/skill-architecture-extension.md",
        PKG / "SKILL.md",
        *sorted((PKG / "references").glob("*.md")),
        PKG / "tests/architecture-scenarios.md",
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]+)?\)")
    for doc in docs:
        text = read(doc)
        for raw in pattern.findall(text):
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^(?:[a-z]+:|/)", target, flags=re.I):
                continue
            # Do not allow paths that accidentally resolve to a non-existent docs/ subtree.
            resolved = (doc.parent / target).resolve()
            check(resolved.is_relative_to(ROOT.resolve()),
                  f"Out-of-tree local link {doc.relative_to(ROOT)} -> {raw}")
            check(resolved.is_file(),
                  f"Broken local Markdown link {doc.relative_to(ROOT)} -> {raw}")


def check_review_invocation() -> None:
    skill = read(PKG / "SKILL.md")
    header = skill.split("---", 2)[1]
    for trigger in ("print preflight", "typography critique",
                    "composition analysis", "포스터 피드백", "편집디자인 검토"):
        check(trigger in header, f"Legacy automatic invocation phrase missing: {trigger}")
    for reference in ("review-protocol.md", "critique-rubric.md",
                      "review-output.md", "reference-analysis.md",
                      "typography-presets.md", "design-handoff.md"):
        check(reference in skill, f"Skill link not surfaced: {reference}")
    review_output = read(PKG / "references/review-output.md")
    for contract in ("Quick Review", "Deep / Aggressive Review",
                     "Critical / Major / Minor / Exploratory", "Keep / Fix / Push"):
        check(contract in review_output, f"Missing legacy review contract {contract}")


def check_reference_math() -> None:
    doc = read(PKG / "references/reference-analysis.md")
    for must_have in ("Frame", "Object", "Relation", "Hypothesis",
                      "evidence_status", "UNVERIFIED", "e_x=", "median(",
                      "경쟁 모델", "임의 가중치", "재구성"):
        check(must_have in doc, f"Missing inverse-analysis contract {must_have}")
    rows = {}
    for line in doc.splitlines():
        if not line.startswith("| RA-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        check(len(cells) == 9, f"Malformed reference example: {line}")
        code, width, observations, normalized, deltas, pitch, origin, model_pitch, residuals = cells
        check(code not in rows, f"Duplicate reference example: {code}")
        width = Decimal(width)
        check(width.is_finite() and width > 0, f"Invalid reference frame width: {code}")
        xs = [Decimal(value) for value in observations.split(",")]
        check(len(xs) >= 3 and all(x.is_finite() for x in xs),
              f"Invalid reference observations: {code}")
        documented_normalized = [Decimal(value) for value in normalized.split(",")]
        documented_deltas = [Decimal(value) for value in deltas.split(",")]
        documented_residuals = [Decimal(value) for value in residuals.split(",")]
        check([x / width for x in xs] == documented_normalized,
              f"Documented normalized x mismatch: {code}")
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        check(gaps == documented_deltas, f"Documented adjacent deltas mismatch: {code}")
        check(median(gaps) == Decimal(pitch), f"Documented pitch mismatch: {code}")
        origin, model_pitch = Decimal(origin), Decimal(model_pitch)
        check(origin.is_finite() and model_pitch.is_finite(),
              f"Invalid reference model: {code}")
        check([abs(origin + model_pitch * i - x) / width
               for i, x in enumerate(xs)] == documented_residuals,
              f"Documented geometric residual mismatch: {code}")
        rows[code] = cells
    check(set(rows) == {"RA-1"}, f"Missing or extra reference example: {set(rows)}")


def check_print_routing() -> None:
    routing = read(PKG / "references/knowledge-routing.md")
    for guard in ("매체가 디지털 전용으로 확정되고 인쇄 요청·제약이 없는 경우만",
                  "텍스트 없는 인쇄용 로고 PDF", "UNVERIFIED"):
        check(guard in routing, f"Missing print routing guard: {guard}")
    check("심볼만 있으면 인쇄 프리플라이트 생략" not in routing,
          "Symbol-only output must not bypass print checks")
    scenarios = read(PKG / "tests/architecture-scenarios.md")
    for scenario in ("| R-4 |", "| R-23 |", "| R-24 |"):
        check(scenario in scenarios, f"Missing digital/print routing case {scenario}")


def check_typography_widths() -> None:
    doc = read(PKG / "references/typography-relations.md")
    for formula in ("W_raw = Σ(a_raw_i + Δadvance_i) / S × F + T_remaining",
                    "W_shaped = Σa_shaped_i / S × F + T_remaining"):
        check(formula in doc, f"Missing width input contract: {formula}")
    widths: dict[str, Decimal] = {}
    for line in doc.splitlines():
        if not line.startswith("| W-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        check(len(cells) == 9, f"Malformed width example: {line}")
        code, kind, advances, scale, size, delta, offset, tracking, expected = cells
        check(code not in widths, f"Duplicate width example {code}")
        check(kind in ("raw", "shaped"), f"Unknown width representation: {kind}")
        check(Decimal(scale) > 0 and Decimal(size) > 0, f"Invalid scale/size: {code}")
        check(kind == "raw" or Decimal(delta) == 0,
              f"Shaped advances must not receive kerning again: {code}")
        # Placement is parsed but excluded: it changes ink position, not pen movement.
        Decimal(offset)
        width = ((sum(Decimal(value) for value in advances.split(",")) + Decimal(delta))
                 / Decimal(scale) * Decimal(size) + Decimal(tracking))
        check(width == Decimal(expected), f"Wrong documented width: {code}: {width}")
        widths[code] = width
    check(widths == {"W-1": Decimal(12), "W-2": Decimal("11.5"),
                     "W-3": Decimal("11.5"), "W-4": Decimal(12),
                     "W-5": Decimal(12), "W-6": Decimal(6), "W-7": Decimal(6)},
          f"Missing or changed width acceptance examples: {widths}")
    check(widths["W-6"] + widths["W-7"] == Decimal(12),
          "Mixed-font runs must be scaled separately before summing")




def check_policy_activation() -> None:
    # Static consistency only: actual agent reads and activation behavior need #7.
    gate = ("현재 작업의 **명시적 opt-in** 또는 "
            "**독립적으로 확인된 현재 프로젝트의 활성 프로파일**")
    for relative in ("SKILL.md", "references/knowledge-routing.md",
                     "references/design-handoff.md", "references/typography-presets.md"):
        text = read(PKG / relative)
        check(gate in text, f"Missing alternative activation routes: {relative}")
        check("opt-in이 없으면 정책값을 자동 채택하지 않는다." not in text,
              f"Repeated opt-in requirement contradicts active profile: {relative}")
    presets = read(PKG / "references/typography-presets.md")
    for required in ("별도 프로젝트 설정/브리프", "현재 프로젝트의 사용자 승인·A~H 선택·유효한 적용 범위",
                     "자료 위치와 적용 범위", "opt-in을 반복 요구하지 않는다", "두 활성화 근거가 모두 없거나 불명확하면"):
        check(required in presets, f"Missing independent activation evidence guard: {required}")
    handoff = read(PKG / "references/design-handoff.md")
    policies = re.findall(r"^policy: \{([^\n]+)\}$", handoff, flags=re.M)
    check(any("opt_in: true" in p and
              "activation_basis: explicit_user_request_for_current_project" in p
              for p in policies), "Explicit opt-in handoff must include activation evidence")
    check(any(all(field in p for field in (
                  "activation_basis: independently_verified_active_project_profile",
                  "profile: A-H", "project: current_project",
                  'evidence: "current_project_brief#typography"')) for p in policies),
          "Active-profile handoff must include project-scoped activation evidence")
    scenarios = read(PKG / "tests/architecture-scenarios.md")
    rows = {cells[0]: cells for line in scenarios.splitlines()
            if line.startswith("| R-")
            for cells in [[cell.strip() for cell in line.strip("|").split("|")]]}
    for code in ("R-6", "R-13", "R-14"):
        check("A~H 프로젝트 프로파일을 명시적으로 적용" in rows.get(code, ["", ""])[1],
              f"Positive preset scenario lacks opt-in: {code}")
    check("opt-in 없이" in " ".join(rows.get("R-33", [])),
          "Cross-project negative scenario must preserve the opt-in guard")
    active = rows.get("R-34", [])
    check(len(active) == 4 and all(term in active[1] for term in (
              "별도 프로젝트 설정/브리프", "현재 프로젝트의 사용자 승인·A~H 활성 프로파일",
              "자료 위치와 적용 범위", "opt-in 반복 없음"))
          and all(term in active[3] for term in (
              "opt-in을 다시 요구", "17pt 초기 시안 미제시", "활성화 근거 누락")),
          "Missing verified active-profile scenario without repeated opt-in: R-34")
    inactive = rows.get("R-35", [])
    check(len(inactive) == 4 and all(term in inactive[1] for term in (
              "현재 작업의 opt-in 없음", "확인된 활성 프로파일 없음", "저장소에 승인 기록만"))
          and "후보/미결정 유지" in inactive[2]
          and "A~H 자동 채택" in inactive[3],
          "Missing no-activation scenario: R-35")


def check_rule_contract() -> None:
    contract = read(PKG / "references/rule-contract.md")
    for required in ("knowledge_kind", "rule_strength", "source_version",
                     "document_status", "scope", "conditions", "exceptions",
                     "verification_method", "PROJECT_POLICY", "UNVERIFIED"):
        check(required in contract, f"Missing rule contract field {required}")
    for path in ("SKILL.md", "references/knowledge-routing.md",
                 "references/design-handoff.md", "references/typography-relations.md"):
        check("rule-contract.md" in read(PKG / path),
              f"Rule contract not linked from {path}")
    scenarios = read(PKG / "tests/architecture-scenarios.md")
    for code in range(29, 34):
        check(f"| R-{code} |" in scenarios,
              f"Missing knowledge-boundary scenario R-{code}")
    presets = read(PKG / "references/typography-presets.md")
    check("PROJECT_POLICY" in presets and "opt-in" in presets,
          "User-approved project policy must be scoped and opt-in")

if __name__ == "__main__":
    check_preset_mapping()
    check_links()
    check_review_invocation()
    check_reference_math()
    check_print_routing()
    check_typography_widths()
    check_rule_contract()
    check_policy_activation()
    print("PASS: policy mappings, local docs links, legacy triggers, reference-math examples, "
          "print routing guards, documented typography widths")
