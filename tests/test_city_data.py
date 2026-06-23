import unittest
from pathlib import Path

from services.city_service import CityService


BASE_DIR = Path(__file__).resolve().parents[1]


class CityDataTests(unittest.TestCase):
    def setUp(self):
        self.service = CityService(BASE_DIR)

    def test_city_data_is_valid(self):
        self.assertEqual([], self.service.validate())

    def test_registered_enabled_locations_are_available(self):
        locations = self.service.load_locations()
        self.assertEqual(
            [
                "city-001",
                "city-009",
                "city-002",
                "city-003",
                "city-010",
                "city-004",
                "city-005",
                "city-006",
                "city-007",
                "city-008",
            ],
            [item["slug"] for item in locations],
        )

    def test_altar_approach_locations_are_registered_and_available(self):
        all_locations = self.service.all_locations_by_slug()
        for slug in ("city-006", "city-007", "city-008"):
            with self.subTest(slug=slug):
                self.assertIn(slug, all_locations)
                self.assertTrue(all_locations[slug]["enabled"])
                self.assertIsNotNone(self.service.get_location(slug))

    def test_altar_approach_district_is_registered(self):
        districts = self.service.load_districts()
        self.assertIn("altar-approach", districts)
        self.assertEqual("city-006", districts["altar-approach"]["default_location"])

    def test_city_targets_exist_and_route_targets_are_relative(self):
        all_locations = self.service.all_locations_by_slug()
        for location in all_locations.values():
            for hotspot in location["hotspots"]:
                if hotspot["type"] == "city":
                    self.assertIn(hotspot["target"], all_locations)
                if hotspot["type"] == "route":
                    self.assertTrue(hotspot["target"].startswith("/"))
                    self.assertNotIn("://", hotspot["target"])

    def test_altar_approach_links_are_connected(self):
        city_005 = self.service.get_location("city-005")
        city_006 = self.service.get_location("city-006")
        city_007 = self.service.get_location("city-007")
        city_008 = self.service.get_location("city-008")

        city_targets = lambda location: {
            hotspot["target"] for hotspot in location["hotspots"] if hotspot["type"] == "city"
        }
        route_targets = lambda location: {
            hotspot["target"] for hotspot in location["hotspots"] if hotspot["type"] == "route"
        }
        external_targets = lambda location: {
            hotspot["target"] for hotspot in location["hotspots"] if hotspot["type"] == "external"
        }

        self.assertIn("city-006", city_targets(city_005))
        self.assertEqual({"city-005", "city-007"}, city_targets(city_006))
        self.assertEqual({"city-006", "city-008"}, city_targets(city_007))
        self.assertEqual({"city-007"}, city_targets(city_008))
        self.assertIn("/ripple", route_targets(city_006))
        self.assertIn("/archive", route_targets(city_007))
        self.assertGreaterEqual(route_targets(city_008), {"/altar", "/hyougi"})
        self.assertIn("https://ofuse.me/be78f6ed", external_targets(city_008))

    def test_hotspot_coordinates_are_in_image_bounds(self):
        for location in self.service.load_locations(include_disabled=True):
            for hotspot in location["hotspots"]:
                for mode in ("pc", "sp"):
                    coords = hotspot[mode]
                    self.assertGreaterEqual(coords["x"], 0)
                    self.assertGreaterEqual(coords["y"], 0)
                    self.assertLessEqual(coords["x"] + coords["width"], 100)
                    self.assertLessEqual(coords["y"] + coords["height"], 100)

    def test_prepare_location_filters_disabled_hotspots(self):
        location = self.service.prepare_location(
            {
                "id": "CITY-X",
                "slug": "city-x",
                "name": "test",
                "enabled": True,
                "images": {},
                "hotspots": [
                    {
                        "id": "disabled",
                        "label": "disabled",
                        "type": "route",
                        "target": "/outside",
                        "pc": {"x": 1, "y": 1, "width": 10, "height": 10},
                        "sp": {"x": 1, "y": 1, "width": 10, "height": 10},
                        "enabled": False,
                    }
                ],
            }
        )
        self.assertEqual([], location["hotspots"])


if __name__ == "__main__":
    unittest.main()
