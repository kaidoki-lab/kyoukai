"""
ShortFACTORY v2.0 room master runner.

Reads data/rooms/{room}.md, builds a Playwright traversal plan from
Interaction Flow, records the browser, and saves captures for each step that
declares a capture target.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
ROOMS_DIR = ROOT / "data" / "rooms"
OUTPUT_PLANS = SHORTS_ROOT / "output_plans"
OUTPUT_RECORDINGS = SHORTS_ROOT / "output_recordings"
OUTPUT_CAPTURES = SHORTS_ROOT / "output_captures"

DEFAULT_BASE_URL = "http://localhost:5000"
VIEWPORT = {"width": 390, "height": 844}
UNSET_VALUES = {"", "未設定", '"未設定"', "'未設定'", "未記載", '"未記載"', "'未記載'"}


def strip_value(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def read_room_master(room: str) -> tuple[Path, str]:
    path = ROOMS_DIR / f"{room}.md"
    if not path.exists():
        raise FileNotFoundError(f"部屋マスターが見つかりません: {path}")
    return path, path.read_text(encoding="utf-8")


def extract_yaml_blocks(markdown: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for match in re.finditer(r"```yaml\s*\n(.*?)\n```", markdown, re.DOTALL):
        block = match.group(1).strip()
        key_match = re.match(r"([A-Za-z_][\w-]*):", block)
        if key_match:
            blocks[key_match.group(1)] = block
    return blocks


def parse_route(markdown: str, room: str) -> str:
    route_match = re.search(r"\*\s*ルート:\s*`([^`]+)`", markdown)
    if route_match:
        return route_match.group(1)
    return f"/{room}"


def parse_simple_list_block(block: str, root_key: str) -> list[dict[str, Any]]:
    """Parse the small YAML subset used by room master list blocks."""
    lines = block.splitlines()
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    nested_key: str | None = None
    nested_obj: dict[str, Any] | None = None

    for raw_line in lines[1:]:
        if not raw_line.strip():
            continue

        if raw_line.startswith("  - "):
            if current is not None:
                if nested_key and nested_obj is not None:
                    current[nested_key] = nested_obj
                items.append(current)
            current = {}
            nested_key = None
            nested_obj = None
            rest = raw_line[4:].strip()
            if ":" in rest:
                key, value = rest.split(":", 1)
                current[key.strip()] = strip_value(value)
            continue

        if current is None:
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 4 and line.endswith(":"):
            if nested_key and nested_obj is not None:
                current[nested_key] = nested_obj
            nested_key = line[:-1].strip()
            nested_obj = {}
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        if indent >= 6 and nested_key:
            if nested_obj is None:
                nested_obj = {}
            nested_obj[key.strip()] = strip_value(value)
        elif indent == 4:
            if nested_key and nested_obj is not None:
                current[nested_key] = nested_obj
                nested_key = None
                nested_obj = None
            current[key.strip()] = strip_value(value)

    if current is not None:
        if nested_key and nested_obj is not None:
            current[nested_key] = nested_obj
        items.append(current)

    return items


def parse_mapping_block(block: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for raw_line in block.splitlines()[1:]:
        line = raw_line.strip()
        if not line or line.startswith("- ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        if value.strip():
            result[key.strip()] = strip_value(value)
    return result


def normalize_capture(capture: Any) -> str | None:
    if isinstance(capture, dict):
        name = capture.get("name")
        if isinstance(name, str) and name and name not in UNSET_VALUES:
            return name
    if isinstance(capture, str) and capture and capture not in UNSET_VALUES:
        return capture
    return None


def build_plan(room: str, markdown: str, blocks: dict[str, str]) -> dict[str, Any]:
    missing_blocks = []
    for key in ("room_states", "interaction_flow", "video_spec", "ai_navigation", "capture_rules"):
        if key not in blocks:
            missing_blocks.append(key)
            print(f"WARNING: YAMLブロックが見つかりません: {key}")

    route = parse_route(markdown, room)
    ai_nav = parse_mapping_block(blocks.get("ai_navigation", "")) if "ai_navigation" in blocks else {}
    start_url = ai_nav.get("start_url") or route
    if start_url in UNSET_VALUES:
        start_url = route

    flow = parse_simple_list_block(blocks.get("interaction_flow", "interaction_flow:"), "interaction_flow")
    steps: list[dict[str, Any]] = []

    for flow_step in flow:
        action = str(flow_step.get("action", "observe"))
        selector = flow_step.get("selector", "未設定")
        wait_ms = int(flow_step.get("wait_ms", 1000) or 1000)
        capture = normalize_capture(flow_step.get("capture"))

        plan_step: dict[str, Any] = {
            "id": flow_step.get("id", f"step_{len(steps) + 1}"),
            "label": flow_step.get("label", ""),
            "action": action,
            "wait_ms": wait_ms,
        }
        if capture:
            plan_step["capture"] = capture
        if action == "goto":
            plan_step["url"] = start_url
        if selector:
            plan_step["selector"] = selector
        if "target" in flow_step:
            plan_step["target"] = flow_step["target"]
        if "note" in flow_step:
            plan_step["note"] = flow_step["note"]
        steps.append(plan_step)

    return {
        "room_id": room,
        "room_master": str(ROOMS_DIR / f"{room}.md"),
        "start_url": start_url,
        "missing_blocks": missing_blocks,
        "steps": steps,
    }


def save_plan(room: str, plan: dict[str, Any]) -> Path:
    OUTPUT_PLANS.mkdir(parents=True, exist_ok=True)
    plan_path = OUTPUT_PLANS / f"{room}_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan_path


def absolute_url(base_url: str, url: str) -> str:
    if re.match(r"^https?://", url):
        return url
    return urljoin(base_url.rstrip("/") + "/", url.lstrip("/"))


def safe_capture_name(index: int, name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "capture"
    return f"{index:02d}_{safe}.png"


def take_capture(page: Page, capture_dir: Path, index: int, capture_name: str) -> Path:
    capture_dir.mkdir(parents=True, exist_ok=True)
    capture_path = capture_dir / safe_capture_name(index, capture_name)
    page.screenshot(path=str(capture_path), full_page=True)
    print(f"CAPTURE: {capture_path}")
    return capture_path


def execute_plan(plan: dict[str, Any], base_url: str) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    room = plan["room_id"]
    capture_dir = OUTPUT_CAPTURES / room
    recording_tmp_dir = OUTPUT_RECORDINGS / "_tmp"
    OUTPUT_RECORDINGS.mkdir(parents=True, exist_ok=True)
    recording_tmp_dir.mkdir(parents=True, exist_ok=True)

    executed = 0
    skipped = 0
    errors: list[str] = []
    captures: list[str] = []
    recording_path: Path | None = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.0 Mobile/15E148 Safari/604.1"
            ),
            record_video_dir=str(recording_tmp_dir),
            record_video_size=VIEWPORT,
        )
        context.add_init_script(
            "try { localStorage.setItem('kyoukai_intro_done', '1'); } catch (e) {}"
        )
        page = context.new_page()

        for index, step in enumerate(plan.get("steps", []), start=1):
            action = step.get("action", "observe")
            wait_ms = int(step.get("wait_ms", 1000) or 1000)
            step_id = step.get("id", f"step_{index}")
            selector = str(step.get("selector", "未設定"))

            try:
                if action == "goto":
                    url = absolute_url(base_url, str(step.get("url") or plan["start_url"]))
                    print(f"STEP {index}: goto {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    executed += 1
                elif action in {"observe", "wait"}:
                    print(f"STEP {index}: observe target={step.get('target', 'room')}")
                    executed += 1
                elif action in {"click", "repeat_click", "click_or_hold"}:
                    if selector in UNSET_VALUES:
                        print(f"SKIP: selector 未設定 step={step_id}")
                        skipped += 1
                    else:
                        click_count = 3 if action == "repeat_click" else 1
                        print(f"STEP {index}: {action} {selector} count={click_count}")
                        for _ in range(click_count):
                            page.click(selector, timeout=5000, force=True)
                            time.sleep(0.2)
                        executed += 1
                else:
                    print(f"SKIP: 未対応 action={action} step={step_id}")
                    skipped += 1

                time.sleep(max(wait_ms, 0) / 1000)
                capture_name = step.get("capture")
                if capture_name:
                    captures.append(str(take_capture(page, capture_dir, index, str(capture_name))))
            except Exception as exc:  # keep going so one weak selector does not kill recording
                message = f"ERROR step={step_id}: {exc}"
                print(message)
                errors.append(message)

        video_path = page.video.path() if page.video else None
        context.close()
        browser.close()

    if video_path and Path(video_path).exists():
        final_path = OUTPUT_RECORDINGS / f"{room}_{timestamp}.webm"
        Path(video_path).replace(final_path)
        recording_path = final_path

    return {
        "executed": executed,
        "skipped": skipped,
        "errors": errors,
        "captures": captures,
        "capture_dir": str(capture_dir),
        "recording_path": str(recording_path) if recording_path else "",
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run a room master Interaction Flow.")
    parser.add_argument("--room", default="kanrinin", help="room_id under data/rooms without .md")
    args = parser.parse_args()

    base_url = os.environ.get("KYOUKAI_BASE_URL", DEFAULT_BASE_URL)
    room_path, markdown = read_room_master(args.room)
    blocks = extract_yaml_blocks(markdown)
    plan = build_plan(args.room, markdown, blocks)
    plan_path = save_plan(args.room, plan)

    print("=" * 60)
    print(f"読み込んだ部屋マスター: {room_path}")
    print(f"巡回プラン: {plan_path}")
    print(f"ベースURL: {base_url}")
    print(f"YAMLブロック: {', '.join(sorted(blocks.keys())) if blocks else 'なし'}")
    print("=" * 60)

    result = execute_plan(plan, base_url)

    print("=" * 60)
    print(f"実行したステップ数: {result['executed']}")
    print(f"スキップしたステップ数: {result['skipped']}")
    print(f"録画ファイルの保存先: {result['recording_path'] or '未保存'}")
    print(f"スクリーンショット保存先: {result['capture_dir']}")
    if result["errors"]:
        print("エラー:")
        for error in result["errors"]:
            print(f"  - {error}")
    else:
        print("エラー: なし")
    print("=" * 60)

    return 0 if result["recording_path"] and result["captures"] and not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
