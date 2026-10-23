import importlib.util
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "visual-design-review" /
        "scripts" / "repair_lift_summary.py")
spec = importlib.util.spec_from_file_location("repair_lift_summary", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample(**updates):
    item = {"id": "case1", "domain": "deterministic", "before_status": "FAIL",
            "after_status": "PASS", "before_artifact_hash": "sha256:a",
            "after_artifact_hash": "sha256:b",
            "verification_evidence": ["test-report-1"]}
    item.update(updates)
    return item


class RepairLiftTests(unittest.TestCase):
    def test_verified_fix(self):
        r = mod.summarize([sample()])
        self.assertEqual(r["counts"]["RESOLVED"], 1)
        self.assertIsNone(r["aesthetic_score"])

    def test_missing_proof_not_success(self):
        r = mod.summarize([sample(verification_evidence=[])])
        self.assertEqual(r["counts"]["INCONCLUSIVE"], 1)

    def test_perceptual_never_machine_pass(self):
        r = mod.summarize([sample(domain="perceptual")])
        self.assertEqual(r["counts"]["INCONCLUSIVE"], 1)

    def test_regression_separate(self):
        r = mod.summarize([sample(before_status="PASS", after_status="FAIL")])
        self.assertEqual(r["counts"]["REGRESSION"], 1)


if __name__ == "__main__":
    unittest.main()
