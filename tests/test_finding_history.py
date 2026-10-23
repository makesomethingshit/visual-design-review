import importlib.util
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "visual-design-review" /
        "scripts" / "finding_history.py")
spec = importlib.util.spec_from_file_location("finding_history", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FindingHistoryTests(unittest.TestCase):
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

    def test_resolved_tombstone_does_not_become_inconclusive(self):
        old = {"findings": [{"finding_id": "F1", "state": "RESOLVED"}]}
        self.assertEqual(mod.compare(old, {"findings": []})[0]["state"], "RESOLVED")

    def test_unknown_current_state_rejected(self):
        with self.assertRaises(ValueError):
            mod.compare({"findings": []},
                        {"findings": [{"finding_id": "F1", "state": "MAGIC"}]})


if __name__ == "__main__":
    unittest.main()
