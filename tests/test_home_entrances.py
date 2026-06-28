import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class HomeEntranceTests(unittest.TestCase):
    def setUp(self):
        self.home_html = (BASE_DIR / "templates" / "home.html").read_text(encoding="utf-8")
        self.elevator_html = (BASE_DIR / "templates" / "elevator.html").read_text(encoding="utf-8")
        self.floor_html = (BASE_DIR / "templates" / "floor.html").read_text(encoding="utf-8")
        self.journey_js = (BASE_DIR / "static" / "kyoukai-home-journey.js").read_text(encoding="utf-8")
        self.elevator_js = (BASE_DIR / "static" / "kyoukai-elevator.js").read_text(encoding="utf-8")
        self.floor_js = (BASE_DIR / "static" / "kyoukai-floor.js").read_text(encoding="utf-8")
        self.space_css = (BASE_DIR / "static" / "space.css").read_text(encoding="utf-8")
        self.main_py = (BASE_DIR / "main.py").read_text(encoding="utf-8")

    def test_home_uses_building_and_entrance_images(self):
        self.assertIn("kyoukai-building-page", self.home_html)
        self.assertIn("/static/kyoukai_building_full_20260627_sunset.png", self.home_html)
        self.assertIn("/static/kyoukai_building_entrance_20260627.png", self.home_html)
        self.assertTrue((BASE_DIR / "static" / "kyoukai_building_full_20260627_sunset.png").exists())
        self.assertTrue((BASE_DIR / "static" / "kyoukai_building_entrance_20260627.png").exists())

    def test_home_has_only_building_entrance_hotspots(self):
        self.assertIn("data-building-entrance", self.home_html)
        self.assertIn("data-elevator-door", self.home_html)
        self.assertIn('href="/elevator"', self.home_html)
        self.assertNotIn('data-entrance-strip', self.home_html)
        self.assertNotIn('class="hotspot hotspot-', self.home_html)
        self.assertNotIn("/static/home-entrances.js", self.home_html)

    def test_building_flow_switches_to_entrance_then_elevator(self):
        self.assertIn('shell.dataset.buildingStage = "zooming";', self.journey_js)
        self.assertIn('shell.dataset.buildingStage = "entrance";', self.journey_js)
        self.assertIn('shell.dataset.buildingStage = "entering";', self.journey_js)
        self.assertIn("window.location.href = elevatorDoor.href;", self.journey_js)
        self.assertIn("scheduleAutoJourney();", self.journey_js)
        self.assertIn("const fullViewMs = 1000;", self.journey_js)
        self.assertIn("const zoomMs = 1000;", self.journey_js)
        self.assertIn("const entranceHoldMs = 1000;", self.journey_js)
        self.assertIn('.kyoukai-building-shell[data-building-stage="zooming"]', self.space_css)

    def test_elevator_route_and_floor_destinations_exist(self):
        self.assertIn('@app.get("/elevator"', self.main_py)
        self.assertIn('@app.get("/floor/{floor_number}"', self.main_py)
        self.assertIn("elevator.html", self.main_py)
        self.assertIn("floor.html", self.main_py)
        self.assertIn("kyoukai_elevator_interior_20260627.png", self.elevator_html)
        self.assertTrue((BASE_DIR / "static" / "kyoukai_elevator_interior_20260627.png").exists())
        self.assertIn("data-floor-number", self.elevator_html)
        self.assertIn("data-floor-up", self.elevator_html)
        self.assertIn("data-floor-down", self.elevator_html)
        self.assertNotIn("/static/bgm.js", self.elevator_html)
        self.assertNotIn("elevator-panel", self.elevator_html)

        for floor_number in ["01", "02", "03", "04", "05", "06"]:
            with self.subTest(floor_number=floor_number):
                self.assertIn(f'href: "/floor/{floor_number}"', self.elevator_js)

    def test_floor_pages_use_original_entrance_images(self):
        self.assertIn("data-floor-entrance-strip", self.floor_html)
        self.assertIn("/static/kyoukai-floor.js", self.floor_html)
        self.assertNotIn("/static/bgm.js", self.floor_html)

        expected_routes = [
            "/kanrinin",
            "/observation",
            "/observer",
            "/archive",
            "/signal",
            "/typhoon-news/",
            "/hyougi",
            "/gokuraku",
            "/exit",
            "/null",
            "/daimyojin",
            "/ma",
            "/particles",
            "/ripple",
            "/colony",
            "/dot-art",
        ]

        for route in expected_routes:
            with self.subTest(route=route):
                self.assertIn(f'href: "{route}"', self.floor_js)

        for image_name in [
            "entrance-kanrinin.png",
            "entrance-observation.png",
            "entrance-observer.png",
            "entrance-archive.png",
            "entrance-signal.png",
            "news.png",
            "entrance-daimyojin.png",
            "entrance-hyougi.png",
            "entrance-gokuraku.png",
            "entrance-exit.png",
            "entrance-null.png",
            "entrance-ma.png",
            "entrance-particles.png",
            "entrance-ripple.png",
            "entrance-colony.png",
            "entrance-dot-art.png",
        ]:
            with self.subTest(image_name=image_name):
                self.assertIn(image_name, self.floor_js)

    def test_hall_sound_uses_gokuraku_tracks_and_stops_on_room_entry(self):
        combined_hall_source = self.elevator_js + "\n" + self.floor_js
        for track in [
            "/static/bgm/bgm_home.mp3",
            "/static/bgm/bgm_exit.mp3",
            "/static/bgm/bgm_null.mp3",
            "/static/bgm/bgm_observer.mp3",
        ]:
            with self.subTest(track=track):
                self.assertIn(track, combined_hall_source)

        self.assertIn("startHallSound", combined_hall_source)
        self.assertIn("stopHallSound", combined_hall_source)
        self.assertIn("const hallSoundVolume = 0.018;", combined_hall_source)
        self.assertIn("new Audio(hallTracks[hallTrackIndex])", combined_hall_source)
        self.assertIn('addEventListener("ended"', combined_hall_source)
        self.assertNotIn("hallTracks.forEach", combined_hall_source)
        self.assertIn("[data-floor-entrance-strip] .entrance-object", self.floor_js)

    def test_elevator_door_frames_play_in_requested_order(self):
        for frame_id in ["4", "3", "2", "1"]:
            with self.subTest(frame_id=frame_id):
                image_name = f"kyoukai_elevator_door_{frame_id}_20260627.png"
                self.assertIn(image_name, self.elevator_html)
                self.assertTrue((BASE_DIR / "static" / image_name).exists())

        self.assertIn('const sequence = ["4", "3", "2", "1"];', self.elevator_js)
        self.assertIn("const doorFrameIntervalMs = 740;", self.elevator_js)
        self.assertIn("[data-door-frame]", self.elevator_js)
        self.assertIn(".kyoukai-elevator-room[data-door-state=\"complete\"] .elevator-door", self.space_css)
        self.assertIn(".elevator-floor-display", self.space_css)
        self.assertIn("left: 82.2%;", self.space_css)


if __name__ == "__main__":
    unittest.main()
