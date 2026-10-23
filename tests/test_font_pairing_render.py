import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "visual-design-review" / "scripts" / "font_pairing_render.py"
SPEC = importlib.util.spec_from_file_location("font_pairing_render", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FontPairingFixtureTest(unittest.TestCase):
    def test_fixture_is_controlled_and_unrated(self):
        fixture = MODULE.load_fixture(MODULE.FIXTURE)
        self.assertEqual([task["id"] for task in fixture["pair_tasks"]],
                         ["FP-01", "FP-02", "FP-03"])
        self.assertEqual(fixture["render_contract"]["pillow_layout_engine"], "BASIC")
        self.assertFalse(fixture["render_contract"]["raqm_or_harfbuzz"])
        self.assertTrue(all(not task["blind_ratings"] for task in fixture["pair_tasks"]))

    def test_rendered_pair_has_visible_distinct_pixels_and_one_variable(self):
        fixture = MODULE.load_fixture(MODULE.FIXTURE)
        task = fixture["pair_tasks"][0]
        self.assertEqual(task["controlled_variable"], "latin_family")
        self.assertNotEqual(task["variants"][0]["latin_font"], task["variants"][1]["latin_font"])
        with tempfile.TemporaryDirectory() as directory:
            records = MODULE.render_task(task, fixture, Path(directory))
            self.assertEqual(len(records), 2)
            images = [Image.open(Path(directory) / record["image"]).convert("RGB")
                      for record in records]
            self.assertEqual(images[0].size, tuple(fixture["render_contract"]["canvas"]))
            for image in images:
                ink = ImageChops.difference(image, Image.new("RGB", image.size, "#ffffff"))
                bbox = ink.getbbox()
                self.assertIsNotNone(bbox)
                self.assertGreaterEqual(bbox[0], 0)
                self.assertGreaterEqual(bbox[1], 0)
                self.assertLess(bbox[2], image.width)
                self.assertLess(bbox[3], image.height)
            self.assertNotEqual(records[0]["image_sha256"], records[1]["image_sha256"])
            self.assertEqual(records[0]["parameters"], records[1]["parameters"])
            self.assertEqual(records[0]["fonts"]["korean"]["file_sha256"],
                             records[1]["fonts"]["korean"]["file_sha256"])
            self.assertNotEqual(records[0]["fonts"]["latin"]["file_sha256"],
                                records[1]["fonts"]["latin"]["file_sha256"])


if __name__ == "__main__":
    unittest.main()
