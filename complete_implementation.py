from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from implementation_events import DEFAULT_EVENTS_PATH, now_iso, record_event


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TASKS_PATH = BASE_DIR / "central-os" / "execution" / "implementation_tasks.json"
DEFAULT_HISTORY_PATH = BASE_DIR / "central-os" / "history" / "executed-tasks.json"


def load_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {path}") from exc
    if not isinstance(data, list):
        raise ValueError(f"JSON file must contain an array: {path}")
    return [item for item in data if isinstance(item, dict)]


def write_json_list(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def finalize_implementation(
    report: dict[str, Any],
    *,
    tasks_path: Path = DEFAULT_TASKS_PATH,
    history_path: Path = DEFAULT_HISTORY_PATH,
    events_path: Path = DEFAULT_EVENTS_PATH,
) -> dict[str, Any]:
    plan_id = str(report.get("sourcePlanId") or "").strip()
    if not plan_id:
        raise ValueError("sourcePlanId is required")

    completed_at = str(report.get("completedAt") or now_iso())
    tasks = load_json_list(tasks_path)
    matched_task: dict[str, Any] | None = None
    requested_task_id = str(report.get("sourceTaskId") or "").strip()

    for task in tasks:
        task_matches = (
            task.get("id") == requested_task_id
            if requested_task_id
            else task.get("sourcePlanId") == plan_id
        )
        if not task_matches:
            continue
        task["status"] = "done"
        task["codexReady"] = True
        task["completedAt"] = completed_at
        task["completionSummary"] = str(report.get("summary") or "")
        task["artifacts"] = [str(item) for item in report.get("artifacts", [])]
        task["verification"] = [str(item) for item in report.get("verification", [])]
        matched_task = task
        break

    if matched_task is not None:
        write_json_list(tasks_path, tasks)
        history = load_json_list(history_path)
        history_entry = {**matched_task, "decidedAt": completed_at}
        history_key = str(matched_task.get("id") or plan_id)
        replaced = False
        for index, existing in enumerate(history):
            existing_key = str(existing.get("id") or existing.get("sourcePlanId") or "")
            if existing_key == history_key:
                history[index] = history_entry
                replaced = True
                break
        if not replaced:
            history.append(history_entry)
        write_json_list(history_path, history[-200:])

    event = record_event(
        {
            **report,
            "sourcePlanId": plan_id,
            "sourceTaskId": (
                str(matched_task.get("id"))
                if matched_task is not None
                else requested_task_id
            ),
            "completedAt": completed_at,
        },
        events_path,
    )
    return {
        "event": event,
        "taskUpdated": matched_task is not None,
        "taskId": matched_task.get("id") if matched_task is not None else None,
    }


def repository_path(path: str) -> str:
    resolved = (BASE_DIR / path).resolve()
    try:
        relative = resolved.relative_to(BASE_DIR.resolve())
    except ValueError as exc:
        raise ValueError(f"path is outside repository: {path}") from exc
    return relative.as_posix()


def commit_and_push(files: list[str], message: str, push: bool) -> str:
    tracked_files = [repository_path(path) for path in files]
    if not tracked_files:
        raise ValueError("at least one changed file is required for commit")
    subprocess.run(["git", "add", "--", *tracked_files], cwd=BASE_DIR, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=BASE_DIR, check=True)
    commit_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=BASE_DIR,
        text=True,
    ).strip()
    if push:
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
    return commit_sha


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Finalize a Codex implementation and report completion to Central OS."
    )
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--title", required=True)
    parser.add_argument("--target-page", action="append", default=[])
    parser.add_argument("--summary", required=True)
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[])
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--commit-message")
    parser.add_argument("--push", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = finalize_implementation(
        {
            "sourcePlanId": args.plan_id,
            "sourceTaskId": args.task_id,
            "title": args.title,
            "targetPages": args.target_page,
            "summary": args.summary,
            "artifacts": args.artifact,
            "verification": args.verification,
        }
    )

    commit_sha = None
    if args.commit_message:
        completion_files = [
            *args.changed_file,
            str(DEFAULT_EVENTS_PATH.relative_to(BASE_DIR)),
        ]
        if result["taskUpdated"]:
            completion_files.extend(
                [
                    str(DEFAULT_TASKS_PATH.relative_to(BASE_DIR)),
                    str(DEFAULT_HISTORY_PATH.relative_to(BASE_DIR)),
                ]
            )
        commit_sha = commit_and_push(
            list(dict.fromkeys(completion_files)),
            args.commit_message,
            args.push,
        )

    print(
        json.dumps(
            {**result, "commit": commit_sha, "pushed": bool(commit_sha and args.push)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
