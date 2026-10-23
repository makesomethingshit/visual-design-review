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
    def test_reported_fix_is_only_a_candidate(self):
        r = mod.summarize([sample()])
        self.assertEqual(r["declared_counts"]["RESOLVED_CANDIDATE"], 1)
        self.assertIsNone(r["verified_counts"])
        self.assertEqual(r["independent_verification"], "UNVERIFIED")
        self.assertNotIn("counts", r)
        self.assertIsNone(r["aesthetic_score"])

    def test_missing_proof_not_success(self):
        r = mod.summarize([sample(verification_evidence=[])])
        self.assertEqual(r["declared_counts"]["INCONCLUSIVE"], 1)

    def test_perceptual_never_machine_pass(self):
        r = mod.summarize([sample(domain="perceptual")])
        self.assertEqual(r["declared_counts"]["INCONCLUSIVE"], 1)

    def test_regression_separate(self):
        r = mod.summarize([sample(before_status="PASS", after_status="FAIL")])
        self.assertEqual(r["declared_counts"]["REGRESSION_CANDIDATE"], 1)

    def test_unverified_external_report_is_not_a_fix(self):
        r = mod.summarize([sample(verification_evidence=[
            {"verification_status": "UNVERIFIED", "checks": [{"status": "UNVERIFIED"}]}])])
        self.assertEqual(r["declared_counts"]["INCONCLUSIVE"], 1)
        self.assertEqual(r["declared_counts"]["RESOLVED_CANDIDATE"], 0)

    def test_structured_pass_does_not_authenticate_itself(self):
        r = mod.summarize([sample(verification_evidence=[
            {"status": "PASS", "artifact_hash": "another-artifact"}])])
        self.assertEqual(r["declared_counts"]["INCONCLUSIVE"], 1)

    def test_duplicate_run_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate run id"):
            mod.summarize([sample(), sample()])

    def test_distinct_runs_of_same_fixture_are_explicit(self):
        r = mod.summarize([sample(id="run-1", fixture_id="design-1"),
                           sample(id="run-2", fixture_id="design-1")])
        self.assertEqual(r["declared_counts"]["RESOLVED_CANDIDATE"], 2)
        self.assertEqual([x["fixture_id"] for x in r["sample_results"]], ["design-1", "design-1"])

    def test_string_is_not_an_evidence_list(self):
        r = mod.summarize([sample(verification_evidence="unstructured claim")])
        self.assertEqual(r["declared_counts"]["INCONCLUSIVE"], 1)


if __name__ == "__main__":
    unittest.main()
