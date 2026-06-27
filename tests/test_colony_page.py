import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class ColonyPageTests(unittest.TestCase):
    def test_colony_route_is_registered(self):
        source = (BASE_DIR / "main.py").read_text(encoding="utf-8")

        self.assertIn('@app.get("/colony"', source)
        self.assertIn('return render_template(request, "colony.html")', source)

    def test_colony_template_is_quiet_canvas_page(self):
        html = (BASE_DIR / "templates" / "colony.html").read_text(encoding="utf-8")

        self.assertIn('id="colonyCanvas"', html)
        self.assertIn("/static/colony.css", html)
        self.assertIn("/static/colony.js", html)
        self.assertIn("COLONY", html)
        self.assertIn("群れる", html)
        self.assertNotIn("<button", html)
        self.assertNotIn("score", html.lower())

    def test_colony_script_contains_growth_and_crush_behavior(self):
        script = (BASE_DIR / "static" / "colony.js").read_text(encoding="utf-8")
        css = (BASE_DIR / "static" / "colony.css").read_text(encoding="utf-8")

        self.assertIn("const MAX_ANTS = 100", script)
        self.assertIn("requestAnimationFrame", script)
        self.assertIn("pointerdown", script)
        self.assertIn("ありがとう。アリだけに。", script)
        self.assertIn("devicePixelRatio", script)
        self.assertIn("touch-action: none", css)
        self.assertIn("/static/images/colony/concrete_9x16.png", css)
        self.assertTrue((BASE_DIR / "static" / "images" / "colony" / "concrete_9x16.png").exists())

    def test_home_entrance_lists_colony(self):
        source = (BASE_DIR / "static" / "home-entrances.js").read_text(encoding="utf-8")

        self.assertIn('id: "colony"', source)
        self.assertIn('href: "/colony"', source)
        self.assertIn("/static/images/colony/entrance-colony.png", source)
        self.assertTrue((BASE_DIR / "static" / "images" / "colony" / "entrance-colony.png").exists())


if __name__ == "__main__":
    unittest.main()
