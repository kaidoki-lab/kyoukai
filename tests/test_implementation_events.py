from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from implementation_events import load_events, planner_completed_context, record_event


class ImplementationEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.events_path = Path(self.temp_dir.name) / "events.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_record_event_creates_completed_event(self) -> None:
        event = record_event(
            {
                "sourcePlanId": "plan-001",
                "title": "祭壇域のデータベース化",
                "targetPages": ["/"],
                "summary": "検索基盤を追加した。",
            },
            self.events_path,
        )
        self.assertEqual("completed", event["status"])
        self.assertEqual("plan-001", load_events(self.events_path)[0]["sourcePlanId"])

    def test_same_plan_replaces_existing_event(self) -> None:
        record_event(
            {"sourcePlanId": "plan-001", "title": "旧", "summary": "旧記録"},
            self.events_path,
        )
        record_event(
            {"sourcePlanId": "plan-001", "title": "新", "summary": "新記録"},
            self.events_path,
        )
        events = load_events(self.events_path)
        self.assertEqual(1, len(events))
        self.assertEqual("新", events[0]["title"])

    def test_completed_events_become_planner_context(self) -> None:
        context = planner_completed_context(
            [
                {
                    "sourcePlanId": "plan-001",
                    "title": "祭壇域のデータベース化",
                    "summary": "完了",
                    "status": "completed",
                }
            ]
        )
        self.assertEqual("plan-001", context[0]["id"])
        self.assertEqual("completed", context[0]["status"])


if __name__ == "__main__":
    unittest.main()
