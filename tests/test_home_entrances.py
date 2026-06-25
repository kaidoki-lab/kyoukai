import re
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class HomeEntranceTests(unittest.TestCase):
    def setUp(self):
        self.home_html = (BASE_DIR / "templates" / "home.html").read_text(encoding="utf-8")
        self.entrance_js = (BASE_DIR / "static" / "home-entrances.js").read_text(encoding="utf-8")
        self.space_css = (BASE_DIR / "static" / "space.css").read_text(encoding="utf-8")

    def test_home_renders_scrollable_entrance_strip(self):
        self.assertIn("home-entrance-page", self.home_html)
        self.assertIn('data-entrance-strip', self.home_html)
        self.assertIn("/static/home-entrances.js", self.home_html)

    def test_legacy_home_hotspots_are_hidden_on_entrance_page(self):
        self.assertIn(".home-entrance-page .altar-frame > .hotspot", self.space_css)
        self.assertRegex(
            self.space_css,
            r"\.home-entrance-page \.altar-frame > \.hotspot\s*\{\s*display:\s*none;",
        )

    def test_entrance_links_and_expected_images_are_listed(self):
        expected = {
            "observation": ("/observation", "entrance-observation.png"),
            "observer": ("/observer", "entrance-observer.png"),
            "signal": ("/signal", "entrance-signal.png"),
            "news": ("/typhoon-news/", "news.png"),
            "external-signal": ("/external-signal", "entrance-external-signal.png"),
            "null": ("/null", "entrance-null.png"),
            "archive": ("/archive", "entrance-archive.png"),
            "hyougi": ("/hyougi", "entrance-hyougi.png"),
            "gokuraku": ("/gokuraku", "entrance-gokuraku.png"),
            "exit": ("/exit", "entrance-exit.png"),
            "outside": ("/outside", "entrance-outside.png"),
            "daimyojin": ("/daimyojin", "entrance-daimyojin.png"),
            "ma": ("/ma", "entrance-ma.png"),
            "particles": ("/particles", "entrance-particles.png"),
            "ripple": ("/ripple", "entrance-ripple.png"),
        }

        for entrance_id, (href, image_name) in expected.items():
            with self.subTest(entrance_id=entrance_id):
                self.assertIn(f'id: "{entrance_id}"', self.entrance_js)
                self.assertIn(f'href: "{href}"', self.entrance_js)
                self.assertIn(image_name, self.entrance_js)

    def test_placeholder_mode_does_not_emit_broken_image_sources(self):
        self.assertGreaterEqual(len(re.findall(r'image:\s*""', self.entrance_js)), 1)
        self.assertIn("if (!item.image) return createFallback(item);", self.entrance_js)


if __name__ == "__main__":
    unittest.main()
