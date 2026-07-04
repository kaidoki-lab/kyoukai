"""Run all room master Interaction Flows and write recording reports."""

from __future__ import annotations

import os
import sys
from datetime import datetime

from flow_runner import run_plan
from recording_report import RunLogger, build_report, write_reports
from room_master_loader import load_all_room_masters, save_plan


DEFAULT_BASE_URL = "http://localhost:5000"


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    run_id = make_run_id()
    base_url = os.environ.get("KYOUKAI_BASE_URL", DEFAULT_BASE_URL)
    logger = RunLogger(run_id)
    started_at = datetime.now().isoformat(timespec="seconds")
    rooms = []

    logger.write(f"run_id={run_id}")
    logger.write(f"base_url={base_url}")

    masters = load_all_room_masters()
    logger.write(f"rooms_total={len(masters)}")

    for index, master in enumerate(masters, start=1):
        logger.write("=" * 60)
        logger.write(f"[{index}/{len(masters)}] room={master.room_id}")
        try:
            plan_path = save_plan(master.plan, run_id)
            logger.write(f"room_master={master.path}")
            logger.write(f"plan={plan_path}")
            logger.write(f"missing_blocks={master.missing_blocks}")
            rooms.append(run_plan(master.plan, base_url, run_id, logger.write))
        except Exception as exc:
            logger.write(f"ROOM FAILED before runner: {master.room_id}: {exc}")
            rooms.append(
                {
                    "room_id": master.room_id,
                    "status": "failed",
                    "recording": "",
                    "captures": [],
                    "steps_executed": 0,
                    "steps_skipped": 0,
                    "warnings": [],
                    "errors": [str(exc)],
                }
            )

    ended_at = datetime.now().isoformat(timespec="seconds")
    report = build_report(run_id, base_url, started_at, ended_at, rooms)
    json_path, md_path = write_reports(report)
    logger.write("=" * 60)
    logger.write(f"summary={report['summary']}")
    logger.write(f"report_json={json_path}")
    logger.write(f"report_md={md_path}")
    # Batch recording is considered successful when every room is attempted and
    # reports are written. Individual room failures remain visible in the report.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
