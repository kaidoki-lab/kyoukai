"""Generate human-checkable post candidate lists from room recording reports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from room_master_loader import extract_yaml_blocks, parse_inline_map, parse_route


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
ROOMS_DIR = ROOT / "data" / "rooms"
REPORTS_DIR = SHORTS_ROOT / "output_reports"
OUTPUT_CANDIDATES = SHORTS_ROOT / "output_candidates"
SUCCESS_STATUSES = {"success", "success_with_warnings"}


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def display_path(path_text: str) -> str:
    path = resolve_path(path_text)
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def find_latest_run_id() -> str:
    runs = [
        path.name
        for path in REPORTS_DIR.iterdir()
        if path.is_dir() and (path / "recording_report.json").exists()
    ] if REPORTS_DIR.exists() else []
    if not runs:
        raise FileNotFoundError("recording_report.json を含むrun_idが見つかりません。")
    return sorted(runs)[-1]


def load_report(run_id: str) -> dict[str, Any]:
    if run_id in {"最新", "latest", "LATEST"}:
        run_id = find_latest_run_id()
    report_path = REPORTS_DIR / run_id / "recording_report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"recording_report.json が見つかりません: {report_path}")
    return json.loads(report_path.read_text(encoding="utf-8"))


def extract_section(markdown: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_display_name(markdown: str, room_id: str) -> str:
    match = re.search(r"\*\s*表示名:\s*(.+)", markdown)
    if not match:
        title = re.search(r"^#\s+(.+)", markdown, re.MULTILINE)
        return title.group(1).strip() if title else room_id
    value = match.group(1).strip().strip("`").strip('"')
    return value.split("、")[0].strip() or room_id


def extract_shortfactory_memo(markdown: str) -> dict[str, str]:
    section = extract_section(markdown, "ShortFACTORYメモ")
    memo: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"\*\s*([^:：]+)[:：]\s*(.*)", line.strip())
        if match:
            memo[match.group(1).strip()] = match.group(2).strip() or "未設定"
    return memo


def extract_post_candidate_info(markdown: str) -> dict[str, str]:
    section = extract_section(markdown, "投稿候補情報")
    info: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"[-*]\s*([^:：]+)[:：]\s*(.*)", line.strip())
        if match:
            info[match.group(1).strip()] = match.group(2).strip() or "未設定"
    return info


def is_post_target(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "1", "対象", "投稿対象"}


def extract_video_highlight(markdown: str) -> str:
    blocks = extract_yaml_blocks(markdown)
    block = blocks.get("video_spec", "")
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if line.startswith("highlight:") and "{" in line:
            data = parse_inline_map(line.split(":", 1)[1].strip())
            description = data.get("description")
            if description:
                return str(description)
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip().strip('"')
            if value:
                return value
    return "未設定"


def load_room_info(room_id: str) -> dict[str, Any]:
    path = ROOMS_DIR / f"{room_id}.md"
    if not path.exists():
        return {
            "display_name": room_id,
            "route": "/" if room_id == "home" else f"/{room_id}",
            "recommended_text": "未設定",
            "highlight": "未設定",
            "post_target": False,
            "exclusion_reason": "部屋マスターが見つかりません",
            "notes": [f"部屋マスターが見つかりません: {path}"],
        }
    markdown = path.read_text(encoding="utf-8")
    blocks = extract_yaml_blocks(markdown)
    memo = extract_shortfactory_memo(markdown)
    post_info = extract_post_candidate_info(markdown)
    recommended_text = post_info.get("投稿文候補") or memo.get("使える一言", "未設定")
    highlight = post_info.get("見どころ") or extract_video_highlight(markdown)
    if highlight == "未設定":
        highlight = memo.get("投稿向きの見どころ", "未設定")
    notes = []
    if post_info.get("メモ") and post_info["メモ"] not in {"なし", "未設定"}:
        notes.append(post_info["メモ"])
    for block_name in ("video_spec", "capture_rules"):
        if block_name not in blocks:
            notes.append(f"{block_name} が未記載")
    return {
        "display_name": extract_display_name(markdown, room_id),
        "route": parse_route(markdown, room_id),
        "recommended_text": recommended_text or "未設定",
        "highlight": highlight or "未設定",
        "post_target": is_post_target(post_info.get("投稿対象", "true")),
        "exclusion_reason": post_info.get("投稿対象外理由", "未設定"),
        "notes": notes,
    }


def build_candidates(report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    candidates: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for room in report.get("rooms", []):
        room_id = room.get("room_id", "unknown")
        recording = room.get("recording", "")
        captures = room.get("captures", [])
        reasons: list[str] = []
        info = load_room_info(room_id)
        if not info["post_target"]:
            reason = info.get("exclusion_reason") or "未設定"
            excluded.append({"room_id": room_id, "reasons": [f"投稿対象外: {reason}"]})
            continue
        if room.get("status") not in SUCCESS_STATUSES:
            reasons.append(f"status={room.get('status')}")
        if not recording or not resolve_path(recording).exists():
            reasons.append("recordingなし")
        existing_captures = [capture for capture in captures if resolve_path(capture).exists()]
        if not existing_captures:
            reasons.append("captureなし")
        if reasons:
            excluded.append({"room_id": room_id, "reasons": reasons})
            continue

        notes = list(info.get("notes", []))
        notes.extend(room.get("warnings", []))
        candidates.append(
            {
                "room_id": room_id,
                "display_name": info["display_name"],
                "route": info["route"],
                "recording": display_path(recording),
                "captures": [display_path(capture) for capture in existing_captures],
                "recommended_text": info["recommended_text"],
                "highlight": info["highlight"],
                "status": "candidate",
                "notes": notes,
            }
        )
    return {"run_id": run_id, "candidates": candidates, "excluded": excluded}


def write_outputs(data: dict[str, Any]) -> tuple[Path, Path]:
    output_dir = OUTPUT_CANDIDATES / data["run_id"]
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "post_candidates.json"
    md_path = output_dir / "post_candidates.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 投稿候補一覧", "", f"run_id: {data['run_id']}", ""]
    lines.append(f"候補数: {len(data['candidates'])}")
    if data.get("excluded"):
        lines.append(f"除外数: {len(data['excluded'])}")
    lines.append("")
    for index, candidate in enumerate(data["candidates"], start=1):
        lines.extend(
            [
                f"## {index}. {candidate['display_name']}",
                "",
                f"- room_id: `{candidate['room_id']}`",
                f"- ルート: {candidate['route']}",
                f"- 録画: {candidate['recording']}",
                f"- スクショ: {candidate['captures'][0]}",
                f"- 見どころ: {candidate['highlight']}",
                f"- 投稿文候補: {candidate['recommended_text']}",
                f"- 状態: {candidate['status']}",
                f"- メモ: {', '.join(candidate['notes']) if candidate['notes'] else 'なし'}",
                "",
            ]
        )
    if data.get("excluded"):
        lines.extend(["## 除外", ""])
        for excluded in data["excluded"]:
            lines.append(f"- `{excluded['room_id']}`: {', '.join(excluded['reasons'])}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Generate ShortFACTORY post candidate lists.")
    parser.add_argument("--run-id", default="最新", help='run_id or "最新"')
    args = parser.parse_args()
    report = load_report(args.run_id)
    data = build_candidates(report)
    json_path, md_path = write_outputs(data)
    print(f"run_id: {data['run_id']}")
    print(f"候補数: {len(data['candidates'])}")
    print(f"除外数: {len(data['excluded'])}")
    print(f"post_candidates.json: {json_path}")
    print(f"post_candidates.md: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
