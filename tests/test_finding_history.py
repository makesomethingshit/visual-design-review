import importlib.util
import hashlib
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "visual-design-review" /
        "scripts" / "finding_history.py")
spec = importlib.util.spec_from_file_location("finding_history", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "finding-history"


class FindingHistoryTests(unittest.TestCase):
    def load_fixture(self, name):
        return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))

    def run_cli(self, before, after):
        return subprocess.run(
            [sys.executable, str(FILE), str(FIXTURE_DIR / before),
             str(FIXTURE_DIR / after)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_unchanged_id_persists(self):
        self.assertEqual(mod.compare({"findings": [{"finding_id": "F1"}]},
                                     {"findings": [{"finding_id": "F1"}]})[0]["state"],
                         "PERSISTING")

    def test_absence_is_not_resolution_without_coverage(self):
        old = {"findings": [{"finding_id": "F1"}]}
        self.assertEqual(mod.compare(old, {"findings": []})[0]["state"], "INCONCLUSIVE")
        self.assertEqual(mod.compare(old, {"findings": [], "review_coverage": "FULL_COMPARABLE"})[0]["state"],
                         "RESOLVED")

    def test_regression_requires_state_evidence(self):
        x = mod.compare({"findings": []},
                        {"findings": [{"finding_id": "F1", "previous_state": "RESOLVED"}]})
        self.assertEqual(x[0]["state"], "REGRESSED")

    def test_unmeasured_bbox_rejected(self):
        with self.assertRaises(ValueError):
            mod.compare({"findings": []},
                        {"findings": [{"finding_id": "F1", "bbox": [0, 0, 10, 10]}]})

    def test_resolved_regressed_persisting_chain(self):
        v1 = {"findings": [{"finding_id": "F1", "state": "RESOLVED"}]}
        v2 = {"findings": [{"finding_id": "F1", "state": "REGRESSED",
                             "previous_state": "RESOLVED"}]}
        v3 = {"findings": [{"finding_id": "F1", "state": "PERSISTING",
                             "previous_state": "REGRESSED"}]}
        self.assertEqual(mod.compare(v1, v2)[0]["state"], "REGRESSED")
        self.assertEqual(mod.compare(v2, v3)[0]["state"], "PERSISTING")

    def test_legacy_active_rows_ignore_old_previous_state(self):
        v1 = {"findings": []}
        v2 = {"findings": [{"finding_id": "F1", "previous_state": "RESOLVED"}]}
        v3 = {"findings": [{"finding_id": "F1", "previous_state": "REGRESSED"}]}
        self.assertEqual(mod.compare(v1, v2)[0]["state"], "REGRESSED")
        self.assertEqual(mod.compare(v2, v3)[0]["state"], "PERSISTING")

    def test_explicit_resolution_and_uncertainty_preserved(self):
        old = {"findings": [{"finding_id": "F1"}]}
        for state in ("RESOLVED", "INCONCLUSIVE"):
            new = {"findings": [{"finding_id": "F1", "state": state}]}
            self.assertEqual(mod.compare(old, new)[0]["state"], state)

    def test_explicit_resolution_after_inconclusive_is_preserved(self):
        old = {"findings": [{"finding_id": "F1", "state": "INCONCLUSIVE"}]}
        new = {"review_coverage": "FULL_COMPARABLE", "findings": [{
            "finding_id": "F1",
            "state": "RESOLVED",
            "observation": "current review explicitly resolves the finding",
        }]}
        self.assertEqual(mod.compare(old, new)[0]["state"], "RESOLVED")

    def test_inconclusive_then_new_requires_continuity_evidence(self):
        old = {"findings": [{"finding_id": "F1", "state": "INCONCLUSIVE"}]}
        for current in ({"finding_id": "F1", "state": "NEW"},
                        {"finding_id": "F1"},
                        {"finding_id": "F1", "state": "PERSISTING"}):
            with self.subTest(current=current):
                after = {"findings": [current], "review_coverage": "FULL_COMPARABLE"}
                self.assertEqual(mod.compare(old, after)[0]["state"], "INCONCLUSIVE")

    def test_inconclusive_then_missing_does_not_auto_resolve(self):
        old = {"findings": [{"finding_id": "F1", "state": "INCONCLUSIVE"}]}
        for coverage in ("PARTIAL", "FULL_COMPARABLE"):
            with self.subTest(coverage=coverage):
                after = {"findings": [], "review_coverage": coverage}
                self.assertEqual(mod.compare(old, after)[0]["state"], "INCONCLUSIVE")

    def test_resolved_tombstone_does_not_become_inconclusive(self):
        old = {"findings": [{"finding_id": "F1", "state": "RESOLVED"}]}
        self.assertEqual(mod.compare(old, {"findings": []})[0]["state"], "RESOLVED")

    def test_unknown_current_state_rejected(self):
        with self.assertRaises(ValueError):
            mod.compare({"findings": []},
                        {"findings": [{"finding_id": "F1", "state": "MAGIC"}]})

    def test_cli_uses_versioned_svg_and_keeps_moved_finding_persisting(self):
        before = self.load_fixture("poster-v1.json")
        after = self.load_fixture("poster-v2-moved.json")
        result = self.run_cli("poster-v1.json", "poster-v2-moved.json")
        states = {row["finding_id"]: row["state"]
                  for row in json.loads(result.stdout)}
        self.assertEqual(states["F-ALIGN"], "PERSISTING")
        self.assertEqual(states["F-CAPTION"], "RESOLVED")
        self.assertTrue(all(row["evidence"] == "stable_id_only"
                            and "not visually verified" in row["warning"]
                            for row in json.loads(result.stdout)))
        self.assertNotEqual(before["findings"][0]["bbox"],
                            after["findings"][0]["bbox"])
        self.assertEqual(before["findings"][0]["object_ids"],
                         after["findings"][0]["object_ids"])

    def test_fixture_source_ids_and_measured_bounds_are_linked(self):
        versions = ("poster-v1.json", "poster-v2-moved.json",
                    "poster-v2-renamed.json", "poster-v3-regressed.json")
        seen_versions = set()
        for snapshot_name in versions:
            snapshot = self.load_fixture(snapshot_name)
            self.assertEqual(snapshot["artifact_source_id"], "fixture-poster")
            seen_versions.add(snapshot["artifact_version"])
            artifact = FIXTURE_DIR / snapshot["artifact_path"]
            artifact_bytes = artifact.read_bytes()
            self.assertNotIn(b"\r\n", artifact_bytes)
            self.assertEqual(hashlib.sha256(artifact_bytes).hexdigest(),
                             snapshot["artifact_sha256"])
            root = ET.parse(artifact).getroot()
            self.assertEqual(root.get("viewBox"), "0 0 600 400")
            source_elements = {element.get("id"): element for element in root.iter()
                               if element.get("id")}
            for finding in snapshot["findings"]:
                self.assertEqual(finding["object_id_evidence"],
                                 "VERIFIED_SOURCE")
                for object_id in finding["object_ids"]:
                    self.assertIn(object_id, source_elements)
                if finding.get("bbox") is not None:
                    self.assertEqual(finding["bbox_evidence"],
                                     "VERIFIED_SOURCE")
                    self.assertEqual(finding["coordinate_system"],
                                     "viewBox 0 0 600 400")
                    source = source_elements[finding["object_ids"][0]]
                    self.assertEqual(source.tag.rsplit("}", 1)[-1], "rect")
                    self.assertEqual(
                        [float(source.get(name)) for name in
                         ("x", "y", "width", "height")],
                        finding["bbox"],
                    )
        self.assertEqual(len(seen_versions), len(versions))

    def test_cli_reports_regression_and_partial_review_as_inconclusive(self):
        regressed = json.loads(self.run_cli(
            "poster-v2-moved.json", "poster-v3-regressed.json").stdout)
        self.assertEqual({row["finding_id"]: row["state"]
                          for row in regressed},
                         {"F-ALIGN": "PERSISTING", "F-CAPTION": "REGRESSED"})
        partial = json.loads(self.run_cli(
            "poster-v3-regressed.json", "poster-v3-partial.json").stdout)
        self.assertEqual({row["finding_id"]: row["state"]
                          for row in partial},
                         {"F-ALIGN": "INCONCLUSIVE",
                          "F-CAPTION": "INCONCLUSIVE"})

    def test_renamed_id_is_not_matched_as_visual_continuity(self):
        result = json.loads(self.run_cli(
            "poster-v1.json", "poster-v2-renamed.json").stdout)
        self.assertEqual({row["finding_id"]: row["state"] for row in result},
                         {"F-ALIGN": "RESOLVED",
                          "F-ALIGN-RENAMED": "NEW",
                          "F-CAPTION": "RESOLVED"})
        self.assertTrue(all(row["evidence"] == "stable_id_only"
                            for row in result))

    def test_unverified_bounds_and_object_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            mod.compare({"findings": []}, {"findings": [{
                "finding_id": "F1",
                "bbox": [0, 0, 10, 10],
                "bbox_evidence": "INFERRED",
                "coordinate_system": "viewBox 0 0 600 400",
            }]})
        with self.assertRaises(ValueError):
            mod.compare({"findings": []}, {"findings": [{
                "finding_id": "F1",
                "object_ids": ["invented-id"],
            }]})
        with self.assertRaises(ValueError):
            mod.compare({"findings": []},
                        {"findings": [], "review_coverage": "MAYBE"})

    def test_malformed_finding_and_bbox_are_rejected_at_cli_boundary(self):
        with self.assertRaises(ValueError):
            mod.compare({"findings": [{"finding_id": "F1", "bbox": [0, 0, 10]}]},
                        {"findings": []})
        with self.assertRaises(ValueError):
            mod.compare({"findings": "F1"}, {"findings": []})


if __name__ == "__main__":
    unittest.main()
