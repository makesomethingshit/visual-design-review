"""Build small, original repair tasks; run independent file checks, not aesthetic ratings."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/repair-lift"
SCRIPT = ROOT / "visual-design-review/scripts/repair_lift_summary.py"


def sha(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixtures():
    # Optional authoring tool only; checked-in artifacts need no reportlab to inspect.
    from reportlab.pdfgen import canvas
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for name, before, after, size in [
        ("poster", "2026-10-32", "2026-10-23", 28),
        ("mixed-body", "용지 Paper: 35mm", "용지 Paper: 35 mm", 20),
        ("negative-repair", "용지 Paper: 35mm", "용지 Paper: 35mm", 18),
    ]:
        for version, text in [("before", before), ("after", after)]:
            # Negative repair changes appearance while preserving the original target failure.
            font_size = size + (2 if name == "negative-repair" and version == "after" else 0)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" '
                   f'viewBox="0 0 480 240"><rect width="480" height="240" fill="#f3efe5"/>'
                   f'<text id="title" x="28" y="60" font-family="sans-serif" font-size="24">'
                   f'OPEN STUDIO</text><text id="required-copy" x="28" y="130" '
                   f'font-family="sans-serif" font-size="{font_size}">{text}</text></svg>\n')
            (FIXTURES / f"{name}-{version}.svg").write_text(svg, encoding="utf-8")
    for version, width in [("before", 300), ("after", 320)]:
        path = FIXTURES / f"print-output-{version}.pdf"
        pdf = canvas.Canvas(str(path), pagesize=(width, 420), invariant=1)
        pdf.setTitle("Original print fixture / exact page-size contract")
        pdf.setFont("Helvetica", 18)
        pdf.drawString(24, 380, "OPEN STUDIO / 23 OCT 2026")
        pdf.rect(24, 24, width - 48, 336)
        pdf.save()


def evaluate(output=None):
    spec = importlib.util.spec_from_file_location("repair_lift_summary", SCRIPT)
    reporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reporter)
    samples, results = [], []
    tool = subprocess.run(["pdfinfo", "-v"], text=True, capture_output=True, check=True)
    version = (tool.stderr or tool.stdout).splitlines()[0]
    for name, extension, expected in [
        ("poster", "svg", "2026-10-23"),
        ("mixed-body", "svg", "용지 Paper: 35 mm"),
        ("negative-repair", "svg", "용지 Paper: 35 mm"),
        ("print-output", "pdf", [320.0, 420.0]),
    ]:
        pair = []
        for stage in ["before", "after"]:
            path = FIXTURES / f"{name}-{stage}.{extension}"
            if extension == "svg":
                root = ET.parse(path).getroot()
                actual = next(n.text for n in root.iter() if n.get("id") == "required-copy")
                checker = "Python ElementTree exact source text"
            else:
                proc = subprocess.run(["pdfinfo", "-box", str(path)], text=True,
                                      capture_output=True, check=True)
                line = next(s for s in proc.stdout.splitlines() if s.startswith("Page size:"))
                parts = line.split()
                actual = [float(parts[2]), float(parts[4])]
                checker = version
            pair.append({"artifact": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                         "actual": actual, "expected": expected,
                         "status": "PASS" if actual == expected else "FAIL", "checker": checker})
        results.append({"fixture_id": name, "before": pair[0], "after": pair[1]})
        samples.append({"id": name + "-local-1", "fixture_id": name,
                        "domain": "deterministic", "before_status": pair[0]["status"],
                        "after_status": pair[1]["status"],
                        "before_artifact_hash": pair[0]["sha256"],
                        "after_artifact_hash": pair[1]["sha256"],
                        "verification_evidence": ["docs/validation/repair-artifacts-2026-10-23.json"]})
    report = {"schema": "repair-fixture-execution-v1", "python": sys.version.split()[0],
              "comparison": "authored before/after; not baseline-vs-skill or causal repair lift",
              "profile": {"poster": "required date 2026-10-23", "mixed-body": "project copy exactly 35 mm",
                          "print-output": "page size exactly 320 x 420 pt; no PDF/X claim"},
              "checker_sha256": sha(Path(__file__)), "reporter_sha256": sha(SCRIPT),
              "results": results, "declarations": reporter.summarize(samples),
              "expert_review": "BLOCKED: independent human reviewers have not rated these tasks",
              "visual_quality": "UNVERIFIED", "physical_print": "UNVERIFIED"}
    assert [r["before"]["status"] for r in results] == ["FAIL"] * 4
    assert [r["after"]["status"] for r in results] == ["PASS", "PASS", "FAIL", "PASS"]
    assert all(r["before"]["sha256"] != r["after"]["sha256"] for r in results)
    assert report["declarations"]["verified_counts"] is None
    assert report["declarations"]["declared_counts"]["RESOLVED_CANDIDATE"] == 3
    if output is not None:
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: 3 authored task repairs and 1 unchanged-target negative; declarations remain UNVERIFIED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="regenerate authored fixtures (needs reportlab)")
    parser.add_argument("--output", type=Path, help="explicit path for a fresh execution report")
    args = parser.parse_args()
    if args.generate:
        make_fixtures()
    evaluate(args.output)