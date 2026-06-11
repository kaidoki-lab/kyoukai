import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import main


class UpdateProposalExecutorTests(unittest.TestCase):
    def test_approved_update_proposal_is_normalized_for_executor(self):
        proposal = {
            "id": "proposal-998",
            "observedPage": "/null",
            "targets": ["/null"],
            "changes": ["文言を更新する", "表示位置を調整する"],
            "reason": "定期観測で差分を検出したため",
            "status": "approved",
        }

        plans = main._collect_approved_implementation_plans([], [proposal])

        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]["id"], "proposal-998")
        self.assertEqual(plans[0]["title"], "/null 定期更新")
        self.assertEqual(
            plans[0]["summary"], "文言を更新する / 表示位置を調整する"
        )
        self.assertEqual(plans[0]["targets"], ["/null"])
        self.assertEqual(plans[0]["source"], "update-proposal")

    def test_pending_update_proposal_is_not_sent_to_executor(self):
        proposal = {
            "id": "proposal-pending",
            "observedPage": "/",
            "status": "pending",
        }

        plans = main._collect_approved_implementation_plans([], [proposal])

        self.assertEqual(plans, [])

    def test_duplicate_plan_ids_are_processed_once(self):
        plan = {"id": "same-id", "status": "approved"}
        proposal = {
            "id": "same-id",
            "observedPage": "/observation",
            "status": "approved",
        }

        plans = main._collect_approved_implementation_plans([plan], [proposal])

        self.assertEqual(len(plans), 1)
        self.assertIs(plans[0], plan)

    def test_executor_creates_task_from_approved_update_proposal(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plans_file = root / "proposal_plans.json"
            proposals_file = root / "update-proposals.json"
            tasks_file = root / "implementation_tasks.json"
            plans_file.write_text("[]", encoding="utf-8")
            proposals_file.write_text(
                """[
  {
    "id": "proposal-998",
    "observedPage": "/null",
    "changes": ["断片文を更新する"],
    "status": "approved"
  }
]""",
                encoding="utf-8",
            )

            with (
                patch.object(main, "PROPOSAL_PLANS_FILE", plans_file),
                patch.object(main, "UPDATE_PROPOSALS_FILE", proposals_file),
                patch.object(main, "IMPLEMENTATION_TASKS_FILE", tasks_file),
                patch.object(main, "_ai_executor_mod", None),
            ):
                result = main.run_ai_executor()
                tasks = main._read_json_list(tasks_file)

        self.assertEqual(result["tasks_written"], 1)
        self.assertEqual(result["approved_update_proposals"], 1)
        self.assertEqual(tasks[0]["sourcePlanId"], "proposal-998")
        self.assertEqual(tasks[0]["sourceProposalType"], "update-proposal")
        self.assertEqual(tasks[0]["targetPages"], ["/null"])


if __name__ == "__main__":
    unittest.main()
