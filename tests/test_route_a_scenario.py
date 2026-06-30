import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class RouteAScenarioTests(unittest.TestCase):
    def setUp(self):
        self.route_json = BASE_DIR / "data" / "scenarios" / "route_a.json"
        self.events_js = (BASE_DIR / "static" / "kyoukai-scenario-events.js").read_text(encoding="utf-8")
        self.scenario_js = (BASE_DIR / "static" / "kyoukai-scenario.js").read_text(encoding="utf-8")
        self.room_js = (BASE_DIR / "static" / "kyoukai-route-a-room.js").read_text(encoding="utf-8")
        self.kanrinin_js = (BASE_DIR / "static" / "kanrinin.js").read_text(encoding="utf-8")
        self.kanrinin_html = (BASE_DIR / "templates" / "kanrinin.html").read_text(encoding="utf-8")
        self.observation_html = (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
        self.signal_html = (BASE_DIR / "templates" / "signal.html").read_text(encoding="utf-8")
        self.main_py = (BASE_DIR / "main.py").read_text(encoding="utf-8")

    def test_route_a_json_is_valid_and_complete(self):
        data = json.loads(self.route_json.read_text(encoding="utf-8"))
        self.assertEqual(data["route_id"], "route_a")
        self.assertEqual(data["name"], "混線している観測")
        for event_id in [
            "route_a_phone_001",
            "route_a_room_observation_001",
            "route_a_room_signal_001",
            "route_a_manager_return_001",
        ]:
            self.assertIn(event_id, self.route_json.read_text(encoding="utf-8"))
            self.assertIn(event_id, self.events_js)

    def test_scenario_engine_supports_route_a_requirements_and_effects(self):
        for token in [
            "schema_version: 1",
            "route_status_equals",
            "active_route_equals",
            "room_stay_seconds",
            "event_enabled",
            "room_entered_after_event",
            "set_route_status",
            "set_active_route",
            "append_diary_entry",
            "unlock_floor",
            "enable_phone_pool",
            "getActiveRoomEvent",
            "getManagerEvent",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, self.scenario_js)

    def test_templates_expose_route_a_targets(self):
        self.assertIn('data-scenario-target="red-phone"', self.kanrinin_html)
        self.assertIn('data-scenario-target="observation-primary"', self.observation_html)
        self.assertIn('data-scenario-target="signal-primary"', self.signal_html)
        self.assertIn("/static/kyoukai-route-a-room.js?v=routea1", self.observation_html)
        self.assertIn("/static/kyoukai-route-a-room.js?v=routea1", self.signal_html)
        self.assertIn("/static/kyoukai-scenario-ui.css?v=routea1", self.kanrinin_html)
        self.assertIn("/static/kyoukai-scenario-ui.css?v=routea1", self.observation_html)
        self.assertIn("/static/kyoukai-scenario-ui.css?v=routea1", self.signal_html)

    def test_conversation_text_is_kept_in_data(self):
        for line in [
            "……聞こえますか",
            "これではありません",
            "観測中のものを観測中",
            "電話、出たんですね",
        ]:
            with self.subTest(line=line):
                self.assertIn(line, self.events_js)
                self.assertIn(line, self.route_json.read_text(encoding="utf-8"))
                self.assertNotIn(line, self.kanrinin_js)
                self.assertNotIn(line, self.room_js)

    def test_cache_busts_scenario_assets(self):
        self.assertIn("kyoukai-building-data.js?v=routea1", self.main_py)
        self.assertIn("kyoukai-scenario-events.js?v=routea1", self.main_py)
        self.assertIn("kyoukai-scenario.js?v=routea1", self.main_py)


if __name__ == "__main__":
    unittest.main()
