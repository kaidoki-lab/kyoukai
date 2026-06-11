from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EVENTS_PATH = BASE_DIR / "central-os" / "execution" / "implementation_events.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_events(path: Path | str = DEFAULT_EVENTS_PATH) -> list[dict[str, Any]]:
    event_path = Path(path)
    try:
        data = json.loads(event_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid implementation event JSON: {event_path}") from exc
    if not isinstance(data, list):
        raise ValueError(f"implementation event file must contain a JSON array: {event_path}")
    return [item for item in data if isinstance(item, dict)]


def record_event(event: dict[str, Any], path: Path | str = DEFAULT_EVENTS_PATH) -> dict[str, Any]:
    event_path = Path(path)
    source_plan_id = str(event.get("sourcePlanId") or "").strip()
    if not source_plan_id:
        raise ValueError("sourcePlanId is required")

    completed_at = str(event.get("completedAt") or now_iso())
    normalized = {
        "id": str(event.get("id") or f"implementation-event-{source_plan_id}"),
        "sourcePlanId": source_plan_id,
        "sourceTaskId": str(event.get("sourceTaskId") or ""),
        "title": str(event.get("title") or source_plan_id),
        "targetPages": [str(item) for item in event.get("targetPages", [])],
        "status": "completed",
        "summary": str(event.get("summary") or ""),
        "artifacts": [str(item) for item in event.get("artifacts", [])],
        "verification": [str(item) for item in event.get("verification", [])],
        "completedAt": completed_at,
        "recordedBy": str(event.get("recordedBy") or "codex"),
    }

    events = load_events(event_path)
    replaced = False
    for index, existing in enumerate(events):
        if existing.get("sourcePlanId") == source_plan_id:
            events[index] = normalized
            replaced = True
            break
    if not replaced:
        events.append(normalized)

    event_path.parent.mkdir(parents=True, exist_ok=True)
    event_path.write_text(
        json.dumps(events[-200:], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return normalized


def planner_completed_context(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    context: list[dict[str, Any]] = []
    for event in events:
        if event.get("status") != "completed":
            continue
        context.append(
            {
                "id": event.get("sourcePlanId"),
                "title": event.get("title", ""),
                "summary": event.get("summary", ""),
                "status": "completed",
                "completedAt": event.get("completedAt"),
            }
        )
    return context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a Central OS implementation completion event.")
    parser.add_argument("--file", type=Path, default=DEFAULT_EVENTS_PATH)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--title", required=True)
    parser.add_argument("--target-page", action="append", default=[])
    parser.add_argument("--summary", required=True)
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    event = record_event(
        {
            "sourcePlanId": args.plan_id,
            "sourceTaskId": args.task_id,
            "title": args.title,
            "targetPages": args.target_page,
            "summary": args.summary,
            "artifacts": args.artifact,
            "verification": args.verification,
        },
        args.file,
    )
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
