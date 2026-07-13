import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class ScenarioRouteTests(unittest.TestCase):
    def setUp(self):
        self.route_a_json = BASE_DIR / "data" / "scenarios" / "route_a.json"
        self.route_b_json = BASE_DIR / "data" / "scenarios" / "route_b.json"
        self.events_js = (BASE_DIR / "static" / "kyoukai-scenario-events.js").read_text(encoding="utf-8")
        self.scenario_js = (BASE_DIR / "static" / "kyoukai-scenario.js").read_text(encoding="utf-8")
        self.route_a_room_js = (BASE_DIR / "static" / "kyoukai-route-a-room.js").read_text(encoding="utf-8")
        self.route_b_room_js = (BASE_DIR / "static" / "kyoukai-route-b-room.js").read_text(encoding="utf-8")
        self.kanrinin_js = (BASE_DIR / "static" / "kanrinin.js").read_text(encoding="utf-8")
        self.kanrinin_html = (BASE_DIR / "templates" / "kanrinin.html").read_text(encoding="utf-8")
        self.observation_html = (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
        self.signal_html = (BASE_DIR / "templates" / "signal.html").read_text(encoding="utf-8")
        self.archive_html = (BASE_DIR / "templates" / "archive.html").read_text(encoding="utf-8")
        self.hyougi_html = (BASE_DIR / "templates" / "hyougi.html").read_text(encoding="utf-8")
        self.gokuraku_html = (BASE_DIR / "templates" / "gokuraku.html").read_text(encoding="utf-8")
        self.floor_html = (BASE_DIR / "templates" / "floor.html").read_text(encoding="utf-8")
        self.elevator_html = (BASE_DIR / "templates" / "elevator.html").read_text(encoding="utf-8")
        self.floor_js = (BASE_DIR / "static" / "kyoukai-floor.js").read_text(encoding="utf-8")
        self.elevator_js = (BASE_DIR / "static" / "kyoukai-elevator.js").read_text(encoding="utf-8")
        self.space_css = (BASE_DIR / "static" / "space.css").read_text(encoding="utf-8")
        self.main_py = (BASE_DIR / "main.py").read_text(encoding="utf-8")

    def test_route_a_json_is_valid_and_uses_twenty_second_phone_wait(self):
        data = json.loads(self.route_a_json.read_text(encoding="utf-8"))
        self.assertEqual(data["route_id"], "route_a")
        for event_id in [
            "route_a_phone_001",
            "route_a_room_observation_001",
            "route_a_room_signal_001",
            "route_a_manager_return_001",
        ]:
            self.assertIn(event_id, self.route_a_json.read_text(encoding="utf-8"))
            self.assertIn(event_id, self.events_js)
        self.assertIn('"value": 20', self.route_a_json.read_text(encoding="utf-8"))
        self.assertIn('value: 20', self.events_js)

    def test_route_b_json_is_valid_and_registered(self):
        data = json.loads(self.route_b_json.read_text(encoding="utf-8"))
        self.assertEqual(data["route_id"], "route_b")
        self.assertEqual(data["name"], "記録されていない人")
        for event_id in [
            "route_b_phone_001",
            "route_b_room_archive_001",
            "route_b_room_hyougi_001",
            "route_b_room_gokuraku_001",
            "route_b_manager_return_001",
        ]:
            self.assertIn(event_id, self.route_b_json.read_text(encoding="utf-8"))
            self.assertIn(event_id, self.events_js)
        self.assertIn('"floor_id": "floor_05"', self.route_b_json.read_text(encoding="utf-8"))
        self.assertIn('floor_id: "floor_05"', self.events_js)

    def test_scenario_engine_supports_route_requirements_and_effects(self):
        for token in [
            "schema_version: SCHEMA_VERSION",
            "route_status_equals",
            "active_route_equals",
            "floor_unlocked",
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

    def test_templates_expose_scenario_targets(self):
        self.assertIn('data-scenario-target="red-phone"', self.kanrinin_html)
        self.assertIn("kanrininManagerPresence", self.kanrinin_html)
        self.assertIn('data-scenario-target="observation-primary"', self.observation_html)
        self.assertIn('data-scenario-target="signal-primary"', self.signal_html)
        self.assertIn('data-scenario-target="archive-record"', self.archive_html)
        self.assertIn('data-scenario-target="hyougi-record"', self.hyougi_html)
        self.assertIn('data-scenario-target="gokuraku-container"', self.gokuraku_html)
        self.assertIn("/static/kyoukai-route-a-room.js?v=routea2", self.observation_html)
        self.assertIn("/static/kyoukai-route-a-room.js?v=routea2", self.signal_html)
        self.assertIn("/static/kyoukai-route-b-room.js?v=routeb1", self.archive_html)
        self.assertIn("/static/kyoukai-route-b-room.js?v=routeb1", self.hyougi_html)
        self.assertIn("/static/kyoukai-route-b-room.js?v=routeb1", self.gokuraku_html)

    def test_audio_state_and_target_guidance_exist(self):
        self.assertTrue((BASE_DIR / "static" / "audio" / "kanrinin" / "red-phone-ring.mp3").exists())
        self.assertIn("/static/audio/kanrinin/red-phone-ring.mp3", self.events_js)
        self.assertIn("PHONE_CHECK_DELAY_MS = 20000", self.kanrinin_js)
        self.assertIn("playPhoneAudio", self.kanrinin_js)
        self.assertIn("last_phone_ring_at", self.scenario_js)
        self.assertIn("phone_wait_started_at", self.scenario_js)
        self.assertIn("startPhoneWait", self.kanrinin_js)
        self.assertIn("getPhoneWaitSeconds", self.kanrinin_js)
        self.assertIn("current_target_room_id", self.floor_js)
        self.assertIn("current_target_room_id", self.elevator_js)
        self.assertIn("is-scenario-target", self.space_css)
        self.assertIn("topfloor1", self.floor_html)
        self.assertIn("topfloor1", self.elevator_html)

    def test_conversation_text_is_kept_in_data(self):
        for line in [
            "……聞こえますか。",
            "これは、こちらの観測ではありません。",
            "観測中のものを観測中",
            "電話、出たんですね。",
            "管理人室ですか。",
            "議題：所有者を持たない記録の受け皿",
            "見つかりました。",
        ]:
            with self.subTest(line=line):
                self.assertIn(line, self.events_js)
                self.assertNotIn(line, self.kanrinin_js)
                self.assertNotIn(line, self.route_a_room_js)
                self.assertNotIn(line, self.route_b_room_js)

    def test_cache_busts_scenario_assets(self):
        self.assertIn("kyoukai-building-data.js?v=routee5", self.main_py)
        self.assertIn("kyoukai-scenario-events.js?v=routee5", self.main_py)
        self.assertIn("kyoukai-scenario.js?v=routee5", self.main_py)


if __name__ == "__main__":
    unittest.main()
