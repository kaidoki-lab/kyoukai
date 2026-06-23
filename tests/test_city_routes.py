import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class CityRouteTests(unittest.TestCase):
    def setUp(self):
        self.main_source = (BASE_DIR / "main.py").read_text(encoding="utf-8")

    def test_city_routes_are_registered(self):
        self.assertIn('@app.get("/city"', self.main_source)
        self.assertIn('@app.get("/city/{slug}"', self.main_source)
        self.assertIn('@app.get("/altar"', self.main_source)
        self.assertIn("city_service.first_location()", self.main_source)
        self.assertIn("city_service.get_location(slug)", self.main_source)

    def test_city_template_uses_data_driven_assets_and_hotspots(self):
        html = (BASE_DIR / "templates" / "city" / "location.html").read_text(encoding="utf-8")
        self.assertIn("{{ location.images.pc }}", html)
        self.assertIn("{{ location.images.sp }}", html)
        self.assertIn("{% for hotspot in hotspots %}", html)
        self.assertIn("data-pc-x", html)
        self.assertIn("data-sp-x", html)
        self.assertIn("/static/city/js/city.js", html)

    def test_city_404_path_is_handled(self):
        self.assertIn('title="街路が見つかりません"', self.main_source)
        self.assertIn("status_code=404", self.main_source)

    def test_existing_routes_are_still_registered(self):
        for route in ('@app.get("/", response_class=HTMLResponse)', '@app.get("/outside"', '@app.get("/signal"', '@app.get("/observation"', '@app.get("/exit"'):
            with self.subTest(route=route):
                self.assertIn(route, self.main_source)

    def test_altar_template_records_visit_without_hotspot_links(self):
        html = (BASE_DIR / "templates" / "city" / "altar.html").read_text(encoding="utf-8")
        script = (BASE_DIR / "static" / "city" / "js" / "altar.js").read_text(encoding="utf-8")

        self.assertIn("/static/city/images/altar/altar-pc.png", html)
        self.assertIn("/static/city/images/altar/altar-sp-red.png", html)
        self.assertNotIn('class="hotspot', html)
        self.assertNotIn('href="/city/city-008"', html)
        self.assertIn("kyoukai_city_state", script)
        self.assertIn("visited_locations", script)
        self.assertIn('const slug = "altar"', script)


if __name__ == "__main__":
    unittest.main()
