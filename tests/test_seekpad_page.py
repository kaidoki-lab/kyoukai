import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class SeekpadPageTests(unittest.TestCase):
    def test_seekpad_route_is_registered(self):
        source = (BASE_DIR / "main.py").read_text(encoding="utf-8")

        self.assertIn('@app.get("/archive/seekpad"', source)
        self.assertIn('render_template(request, "seekpad.html"', source)

    def test_seekpad_template_has_player_and_pads(self):
        html = (BASE_DIR / "templates" / "seekpad.html").read_text(encoding="utf-8")

        self.assertIn('id="player"', html)
        self.assertIn("/static/seekpad.js", html)
        self.assertIn("/static/seekpad.css", html)
        self.assertIn("seekpad-pad", html)

    def test_archive_links_to_seekpad(self):
        html = (BASE_DIR / "templates" / "archive.html").read_text(encoding="utf-8")

        self.assertIn("/archive/seekpad", html)

    def test_seekpad_data_is_readable(self):
        data = json.loads((BASE_DIR / "data" / "seekpad.json").read_text(encoding="utf-8"))

        self.assertIn("video_id", data)
        self.assertTrue(data["video_id"])
        self.assertIn("pads", data)
        self.assertEqual(len(data["pads"]), 10)


if __name__ == "__main__":
    unittest.main()
