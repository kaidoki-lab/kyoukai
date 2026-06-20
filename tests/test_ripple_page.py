import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class RipplePageTests(unittest.TestCase):
    def test_ripple_route_is_registered(self):
        source = (BASE_DIR / "main.py").read_text(encoding="utf-8")

        self.assertIn('@app.get("/ripple"', source)
        self.assertIn('return render_template(request, "ripple.html")', source)

    def test_ripple_template_is_ui_free_canvas_page(self):
        html = (BASE_DIR / "templates" / "ripple.html").read_text(encoding="utf-8")

        self.assertIn('id="rippleCanvas"', html)
        self.assertIn("/static/ripple.css", html)
        self.assertIn("/static/ripple.js", html)
        self.assertNotIn("<button", html)
        self.assertNotIn("score", html.lower())

    def test_ripple_script_contains_rebel_dot_and_idle_ripples(self):
        script = (BASE_DIR / "static" / "ripple.js").read_text(encoding="utf-8")
        css = (BASE_DIR / "static" / "ripple.css").read_text(encoding="utf-8")

        self.assertIn("isRebelDot", script)
        self.assertIn("rebelAction", script)
        self.assertIn("nextIdleRipple", script)
        self.assertIn("nextBlackoutRipple: 60000", script)
        self.assertIn("spawnBlackoutRipple", script)
        self.assertIn("mode === 'blackout'", script)
        self.assertIn("requestAnimationFrame", script)
        self.assertIn("touch-action: none", css)
        self.assertIn("overflow: hidden", css)


if __name__ == "__main__":
    unittest.main()
