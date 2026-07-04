"""Run one room master Interaction Flow and write recording reports."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

from flow_runner import run_plan
from recording_report import RunLogger, build_report, write_reports
from room_master_loader import load_room_master, save_plan


DEFAULT_BASE_URL = "http://localhost:5000"


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run_room(room_id: str, run_id: str, base_url: str) -> dict:
    logger = RunLogger(run_id)
    master = load_room_master(room_id)
    plan_path = save_plan(master.plan, run_id)
    logger.write(f"run_id={run_id}")
    logger.write(f"base_url={base_url}")
    logger.write(f"room_master={master.path}")
    logger.write(f"plan={plan_path}")
    logger.write(f"missing_blocks={master.missing_blocks}")
    return run_plan(master.plan, base_url, run_id, logger.write)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run one room master Interaction Flow.")
    parser.add_argument("--room", default="kanrinin", help="room_id under data/rooms without .md")
    parser.add_argument("--run-id", default="", help="optional run_id")
    args = parser.parse_args()

    run_id = args.run_id or make_run_id()
    base_url = os.environ.get("KYOUKAI_BASE_URL", DEFAULT_BASE_URL)
    started_at = datetime.now().isoformat(timespec="seconds")
    try:
        room_result = run_room(args.room, run_id, base_url)
    except Exception as exc:
        room_result = {
            "room_id": args.room,
            "status": "failed",
            "recording": "",
            "captures": [],
            "steps_executed": 0,
            "steps_skipped": 0,
            "warnings": [],
            "errors": [str(exc)],
        }
    ended_at = datetime.now().isoformat(timespec="seconds")
    report = build_report(run_id, base_url, started_at, ended_at, [room_result])
    json_path, md_path = write_reports(report)

    print("=" * 60)
    print(f"録画ファイル: {room_result.get('recording') or '未保存'}")
    print(f"スクリーンショット: {room_result.get('capture_dir', '')}")
    print(f"実行ログ: shorts_factory/output_logs/{run_id}/run.log")
    print(f"レポートJSON: {json_path}")
    print(f"レポートMD: {md_path}")
    print(f"status: {room_result['status']}")
    print("=" * 60)
    return 0 if room_result["status"] in {"success", "success_with_warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
