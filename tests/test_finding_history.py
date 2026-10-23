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


if __name__ == "__main__":
    unittest.main()
