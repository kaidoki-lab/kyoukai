import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import main


class PlannerPolicyTests(unittest.TestCase):
    def test_internal_features_are_not_public_room_plans(self):
        plans = [
            {
                "id": "plan-db",
                "title": "祭壇域のデータベース化",
                "summary": "祭壇域にデータベース管理機能を追加する。",
                "targets": ["/"],
            },
            {
                "id": "plan-codex",
                "title": "Codex実装自動化",
                "summary": "AI大明神室に自動生成機能を追加する。",
                "targets": ["/daimyojin"],
            },
            {
                "id": "plan-analysis",
                "title": "AI大明神室の分析機能",
                "summary": "部屋にデータ分析機能と管理画面を追加する。",
                "targets": ["/daimyojin"],
            },
        ]

        accepted, rejected = main._filter_public_plans(plans, [])

        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 3)
        self.assertTrue(
            all(item["reason"] == "internal-system-feature" for item in rejected)
        )

    def test_expression_and_navigation_plan_is_kept(self):
        plan = {
            "id": "plan-signal",
            "title": "受信域の放送断片追加",
            "summary": "既存演出に合う短い放送断片を追加する。",
            "targets": ["/signal"],
        }

        accepted, rejected = main._filter_public_plans([plan], [])

        self.assertEqual(accepted, [plan])
        self.assertEqual(rejected, [])

    def test_internal_target_is_rejected(self):
        plan = {
            "id": "plan-central",
            "title": "企画一覧の改善",
            "summary": "企画一覧の表示を調整する。",
            "targets": ["/central"],
        }

        accepted, rejected = main._filter_public_plans([plan], [])

        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0]["reason"], "non-public-target")

    def test_completed_plan_is_not_repeated(self):
        plan = {
            "id": "plan-repeat",
            "title": "未確認接続の断片文更新",
            "summary": "新しい断片文を追加する。",
            "targets": ["/null"],
        }
        completed = [
            {
                "title": "未確認接続の断片文更新",
                "summary": "以前の実装",
                "status": "completed",
            }
        ]

        accepted, rejected = main._filter_public_plans([plan], completed)

        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0]["reason"], "already-completed")

    def test_policy_fallback_contains_only_public_experience_plans(self):
        plans = main._safe_public_plan_fallback()

        accepted, rejected = main._filter_public_plans(plans, [])

        self.assertGreaterEqual(len(accepted), 3)
        self.assertEqual(rejected, [])
        self.assertTrue(all(plan["source"] == "policy-fallback" for plan in plans))

    def test_planner_replaces_internal_ai_output_with_public_fallback(self):
        ai_planner = Mock()
        ai_planner.generate_plans.return_value = [
            {
                "id": "plan-internal",
                "title": "AI大明神室のデータ分析機能",
                "summary": "部屋に管理画面を追加する。",
                "targets": ["/daimyojin"],
                "status": "pending",
            }
        ]

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plans_file = root / "proposal_plans.json"
            accepted_file = root / "accepted.json"
            rejected_file = root / "rejected.json"
            updates_file = root / "updates.json"
            events_file = root / "events.json"
            for path in (accepted_file, rejected_file, updates_file, events_file):
                path.write_text("[]", encoding="utf-8")

            with (
                patch.object(main, "_ai_planner_mod", ai_planner),
                patch.object(main, "_fetch_ga4_data", return_value={}),
                patch.object(main, "_analyze_rooms", return_value=[]),
                patch.object(main, "PROPOSAL_PLANS_FILE", plans_file),
                patch.object(main, "ACCEPTED_PLANS_FILE", accepted_file),
                patch.object(main, "REJECTED_PLANS_FILE", rejected_file),
                patch.object(main, "UPDATE_PROPOSALS_FILE", updates_file),
                patch.object(main, "IMPLEMENTATION_EVENTS_FILE", events_file),
            ):
                result = main.run_ai_planner()
                saved = main._read_json_list(plans_file)

        self.assertEqual(result["plans_rejected_by_policy"], 1)
        self.assertEqual(len(saved), 3)
        self.assertTrue(all(plan["source"] == "policy-fallback" for plan in saved))
        self.assertFalse(
            any("分析機能" in main._plan_text(plan) for plan in saved)
        )


if __name__ == "__main__":
    unittest.main()
