from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from complete_implementation import (
    finalize_implementation,
    load_json_list,
    write_json_list,
)


class CompleteImplementationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.tasks = self.root / "tasks.json"
        self.history = self.root / "history.json"
        self.events = self.root / "events.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_matching_task_is_completed_and_archived(self) -> None:
        write_json_list(
            self.tasks,
            [
                {
                    "id": "task-001",
                    "sourcePlanId": "plan-001",
                    "title": "実装指示",
                    "status": "sent",
                    "codexReady": True,
                }
            ],
        )

        result = finalize_implementation(
            {
                "sourcePlanId": "plan-001",
                "title": "祭壇域更新",
                "summary": "実装完了",
                "artifacts": ["main.py"],
                "verification": ["tests passed"],
            },
            tasks_path=self.tasks,
            history_path=self.history,
            events_path=self.events,
        )

        self.assertTrue(result["taskUpdated"])
        self.assertEqual("done", load_json_list(self.tasks)[0]["status"])
        self.assertEqual(1, len(load_json_list(self.history)))
        self.assertEqual("completed", load_json_list(self.events)[0]["status"])

    def test_missing_task_still_records_completion_event(self) -> None:
        result = finalize_implementation(
            {
                "sourcePlanId": "plan-missing",
                "title": "独立実装",
                "summary": "完了",
            },
            tasks_path=self.tasks,
            history_path=self.history,
            events_path=self.events,
        )

        self.assertFalse(result["taskUpdated"])
        self.assertEqual("plan-missing", load_json_list(self.events)[0]["sourcePlanId"])

    def test_repeated_completion_does_not_duplicate_history(self) -> None:
        write_json_list(
            self.tasks,
            [{"id": "task-001", "sourcePlanId": "plan-001", "status": "sent"}],
        )
        report = {
            "sourcePlanId": "plan-001",
            "title": "祭壇域更新",
            "summary": "完了",
        }
        for _ in range(2):
            finalize_implementation(
                report,
                tasks_path=self.tasks,
                history_path=self.history,
                events_path=self.events,
            )

        self.assertEqual(1, len(load_json_list(self.history)))
        self.assertEqual(1, len(load_json_list(self.events)))


if __name__ == "__main__":
    unittest.main()
