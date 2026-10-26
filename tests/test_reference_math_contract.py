"""Read documented inputs and expected results; this does not test inverse rendering."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "reference_contract", Path(__file__).with_name("check-knowledge-contract.py"))
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)

ROW = "| RA-1 | 1200 | 120,420,720 | 0.10,0.35,0.60 | 300,300 | 300 | 120 | 300 | 0,0,0 |"


class ReferenceMathTests(unittest.TestCase):
    def check_mutation(self, replacement):
        doc = contract.read(contract.PKG / "references/reference-analysis.md")
        self.assertIn(ROW, doc)
        with patch.object(contract, "read", return_value=doc.replace(ROW, replacement)):
            contract.check_reference_math()

    def test_documented_example(self):
        contract.check_reference_math()

    def test_wrong_normalized_result_rejected(self):
        with self.assertRaisesRegex(AssertionError, "normalized x mismatch"):
            self.check_mutation(ROW.replace("0.10,0.35,0.60", "9.10,9.35,9.60"))

    def test_wrong_adjacent_deltas_rejected(self):
        with self.assertRaisesRegex(AssertionError, "adjacent deltas mismatch"):
            self.check_mutation(ROW.replace("300,300", "301,300"))

    def test_wrong_pitch_rejected(self):
        with self.assertRaisesRegex(AssertionError, "pitch mismatch"):
            self.check_mutation(ROW.replace("| 300 | 120", "| 301 | 120"))

    def test_wrong_residuals_rejected(self):
        with self.assertRaisesRegex(AssertionError, "geometric residual mismatch"):
            self.check_mutation(ROW.replace("0,0,0", "0,0,1"))

    def test_zero_frame_width_rejected(self):
        with self.assertRaisesRegex(AssertionError, "frame width"):
            self.check_mutation(ROW.replace("| 1200 |", "| 0 |"))

    def test_consistent_new_input_and_results_accepted(self):
        self.check_mutation(ROW.replace("120,420,720", "240,540,840")
                           .replace("0.10,0.35,0.60", "0.20,0.45,0.70")
                           .replace("| 120 |", "| 240 |"))


if __name__ == "__main__":
    unittest.main()
