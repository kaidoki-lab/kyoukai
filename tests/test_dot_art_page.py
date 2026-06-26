import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class DotArtPageTests(unittest.TestCase):
    def test_dot_art_route_is_registered(self):
        source = (BASE_DIR / "main.py").read_text(encoding="utf-8")

        self.assertIn('@app.get("/dot-art"', source)
        self.assertIn('return render_template(request, "dot-art.html")', source)

    def test_kyoukai_template_is_canvas_page(self):
        html = (BASE_DIR / "templates" / "dot-art.html").read_text(encoding="utf-8")

        self.assertIn('id="dotArtCanvas"', html)
        self.assertIn("/static/dot-art.css", html)
        self.assertIn("/static/dot-art.js", html)
        self.assertNotIn("score", html.lower())
        self.assertNotIn("ranking", html.lower())

    def test_script_contains_collision_and_audio_core(self):
        script = (BASE_DIR / "static" / "dot-art.js").read_text(encoding="utf-8")
        css = (BASE_DIR / "static" / "dot-art.css").read_text(encoding="utf-8")

        self.assertIn("class Bullet", script)
        self.assertIn("class Explosion", script)
        self.assertIn("class Particle", script)
        self.assertIn("class Mark", script)
        self.assertIn("buildSpatialHash", script)
        self.assertIn("playFire", script)
        self.assertIn("flashRadius", script)
        self.assertIn("requestAnimationFrame", script)
        self.assertIn("AudioContext", script)
        self.assertIn("pointerdown", script)
        self.assertIn("touch-action: none", css)
        self.assertIn("overflow: hidden", css)

    def test_booth_package_is_standalone(self):
        package_dir = BASE_DIR / "dot-collision-art" / "booth-package" / "dot-collision-art_v1.0.0"
        html = (package_dir / "index.html").read_text(encoding="utf-8")
        readme = (package_dir / "README.md").read_text(encoding="utf-8")

        self.assertTrue((package_dir / "style.css").exists())
        self.assertTrue((package_dir / "main.js").exists())
        self.assertTrue((package_dir / "TERMS.md").exists())
        self.assertTrue((package_dir / "LICENSE.txt").exists())
        self.assertTrue((package_dir / "CHANGELOG.md").exists())
        self.assertIn("./style.css", html)
        self.assertIn("./main.js", html)
        self.assertNotIn("/static/", html)
        self.assertNotIn("analytics", html.lower())
        self.assertIn("KYOUKAI本体", readme)

    def test_home_links_to_dot_art(self):
        source = (BASE_DIR / "static" / "home-entrances.js").read_text(encoding="utf-8")

        self.assertIn('id: "dot-art"', source)
        self.assertIn('href: "/dot-art"', source)
        self.assertIn("/static/entrance-dot-art.png", source)
        self.assertTrue((BASE_DIR / "static" / "entrance-dot-art.png").exists())


if __name__ == "__main__":
    unittest.main()
