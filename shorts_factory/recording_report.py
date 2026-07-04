"""Recording report generation for ShortFACTORY room flow runs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
OUTPUT_LOGS = SHORTS_ROOT / "output_logs"
OUTPUT_REPORTS = SHORTS_ROOT / "output_reports"


class RunLogger:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.log_dir = OUTPUT_LOGS / run_id
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.log_dir / "run.log"

    def write(self, message: str) -> None:
        line = f"{datetime.now().isoformat(timespec='seconds')} {message}"
        print(message)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def build_report(
    run_id: str,
    base_url: str,
    started_at: str,
    ended_at: str,
    rooms: list[dict[str, Any]],
) -> dict[str, Any]:
    success = sum(1 for room in rooms if room["status"] in {"success", "success_with_warnings"})
    failed = sum(1 for room in rooms if room["status"] == "failed")
    skipped = sum(1 for room in rooms if room["status"] == "skipped")
    return {
        "run_id": run_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "base_url": base_url,
        "summary": {
            "total": len(rooms),
            "success": success,
            "failed": failed,
            "skipped": skipped,
        },
        "rooms": rooms,
    }


def write_reports(report: dict[str, Any]) -> tuple[Path, Path]:
    report_dir = OUTPUT_REPORTS / report["run_id"]
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "recording_report.json"
    md_path = report_dir / "recording_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Recording Report {report['run_id']}",
        "",
        f"- base_url: `{report['base_url']}`",
        f"- started_at: `{report['started_at']}`",
        f"- ended_at: `{report['ended_at']}`",
        f"- total: {report['summary']['total']}",
        f"- success: {report['summary']['success']}",
        f"- failed: {report['summary']['failed']}",
        f"- skipped: {report['summary']['skipped']}",
        "",
        "| room | status | steps | skipped | captures | recording | warnings | errors |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for room in report["rooms"]:
        warnings = "<br>".join(room.get("warnings", []))
        errors = "<br>".join(room.get("errors", []))
        recording = room.get("recording", "")
        lines.append(
            f"| `{room['room_id']}` | {room['status']} | {room.get('steps_executed', 0)} | "
            f"{room.get('steps_skipped', 0)} | {len(room.get('captures', []))} | "
            f"`{recording}` | {warnings} | {errors} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
