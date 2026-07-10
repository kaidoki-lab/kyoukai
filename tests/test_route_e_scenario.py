import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class RouteEFoundationTests(unittest.TestCase):
    def setUp(self):
        self.route_e_json_path = BASE_DIR / "data" / "scenarios" / "route_e.json"
        self.route_e_json = json.loads(self.route_e_json_path.read_text(encoding="utf-8"))
        self.events_js = (BASE_DIR / "static" / "kyoukai-scenario-events.js").read_text(encoding="utf-8")
        self.scenario_js = (BASE_DIR / "static" / "kyoukai-scenario.js").read_text(encoding="utf-8")
        self.kanrinin_js = (BASE_DIR / "static" / "kanrinin.js").read_text(encoding="utf-8")

    def test_route_e_definition_is_final_route(self):
        self.assertEqual(self.route_e_json["route_id"], "route_e")
        self.assertEqual(self.route_e_json["name"], "観測の完了")
        self.assertEqual(self.route_e_json["type"], "final")
        self.assertTrue(self.route_e_json["is_final_route"])
        self.assertIn('route_id: "route_e"', self.events_js)
        self.assertIn('name: "観測の完了"', self.events_js)
        self.assertIn('type: "final"', self.events_js)
        self.assertIn("is_final_route: true", self.events_js)

    def test_route_e_requires_completed_standard_routes_and_scenario_mode(self):
        required_tokens = [
            '{ type: "mode_equals", value: "scenario" }',
            '{ type: "route_status_equals", route_id: "route_a", value: "completed" }',
            '{ type: "route_status_equals", route_id: "route_b", value: "completed" }',
            '{ type: "route_status_equals", route_id: "route_c", value: "completed" }',
            '{ type: "route_status_equals", route_id: "route_d", value: "completed" }',
            '{ type: "active_route_equals", value: null }',
            '{ type: "state_equals", key: "final_route_available", value: true }',
            '{ type: "state_not_equals", key: "ending_completed", value: true }',
        ]
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, self.events_js)

    def test_route_d_only_makes_route_e_available(self):
        self.assertIn('{ type: "set_route_status", route_id: "route_e", value: "available" }', self.events_js)
        self.assertIn('{ type: "set_state_value", key: "final_route_available", value: true }', self.events_js)
        self.assertIn('{ type: "set_state_value", key: "top_floor_unlocked", value: false }', self.events_js)
        self.assertIn('{ type: "set_state_value", key: "top_floor_keyhole_active", value: false }', self.events_js)
        self.assertIn('{ type: "enable_event", event_id: "route_e_phone_001" }', self.events_js)

    def test_route_e_phone_waits_for_kanrinin_reentry_and_twenty_seconds(self):
        self.assertIn('event_id: "route_e_phone_001"', self.events_js)
        self.assertIn('{ type: "room_reentered_after_event", room_id: "kanrinin", after_event_id: "route_d_manager_return_001" }', self.events_js)
        self.assertIn('{ type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 20 }', self.events_js)
        self.assertIn("PHONE_CHECK_DELAY_MS = 20000", self.kanrinin_js)
        self.assertIn("resetPhoneWait", self.kanrinin_js)

    def test_route_e_becomes_active_when_phone_is_accepted(self):
        self.assertIn("start_effects", self.events_js)
        self.assertIn('{ type: "set_route_status", route_id: "route_e", value: "active" }', self.events_js)
        self.assertIn('{ type: "set_active_route", route_id: "route_e" }', self.events_js)
        self.assertIn("event.start_effects", self.scenario_js)
        self.assertIn("applyEffect(state, effect)", self.scenario_js)
        self.assertIn("topFloorRoom.floor === number && state.top_floor_unlocked", self.scenario_js)

    def test_route_e_completion_skeleton_exists_without_story_text(self):
        for event_id in [
            "route_e_phone_001",
            "route_e_top_floor_001",
            "route_e_annihilation_key_001",
            "route_e_observer_final_001",
            "route_e_manager_return_001",
            "route_e_final_diary_001",
        ]:
            with self.subTest(event_id=event_id):
                self.assertIn(event_id, self.route_e_json_path.read_text(encoding="utf-8"))
                self.assertIn(event_id, self.events_js)
        self.assertIn("conversation: []", self.events_js)

    def test_state_defaults_and_missing_key_normalization_support_ending(self):
        for token in [
            'route_e_stage: "not_started"',
            "ending_completed: false",
            "kyoukai_completed_at: null",
            "state_equals",
            "state_not_equals",
            "set_state_value",
            "set_timestamp",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, self.scenario_js)


if __name__ == "__main__":
    unittest.main()
