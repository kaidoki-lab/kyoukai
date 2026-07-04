"""Room master loading and small YAML-subset parsing for ShortFACTORY."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
OUTPUT_PLANS = ROOT / "shorts_factory" / "output_plans"

REQUIRED_BLOCKS = (
    "room_states",
    "interaction_flow",
    "video_spec",
    "ai_navigation",
    "capture_rules",
)
UNSET_VALUES = {"", "未設定", '"未設定"', "'未設定'", "未記載", '"未記載"', "'未記載'"}


@dataclass
class RoomMaster:
    room_id: str
    path: Path
    markdown: str
    route: str
    blocks: dict[str, str]
    missing_blocks: list[str]
    plan: dict[str, Any]


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


def split_inline_items(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "{":
            depth += 1
            current.append(char)
            continue
        if char == "}":
            depth -= 1
            current.append(char)
            continue
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current).strip())
    return parts


def parse_inline_map(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]
    result: dict[str, Any] = {}
    for part in split_inline_items(text):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        key = key.strip().strip('"').strip("'")
        value = value.strip()
        if value.startswith("{") and value.endswith("}"):
            result[key] = parse_inline_map(value)
        elif value.startswith("[") and value.endswith("]"):
            result[key] = [
                strip_value(item.strip())
                for item in split_inline_items(value[1:-1])
                if item.strip()
            ]
        else:
            result[key] = strip_value(value)
    return result


def extract_yaml_blocks(markdown: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for match in re.finditer(r"```yaml\s*\n(.*?)\n```", markdown, re.DOTALL):
        block = match.group(1).strip()
        key_match = re.match(r"([A-Za-z_][\w-]*):", block)
        if key_match:
            blocks[key_match.group(1)] = block
    return blocks


def parse_route(markdown: str, room_id: str) -> str:
    route_match = re.search(r"\*\s*ルート:\s*`([^`]+)`", markdown)
    if route_match:
        return route_match.group(1)
    quoted_match = re.search(r"\*\s*ルート:\s*\"([^\"]+)\"", markdown)
    if quoted_match and quoted_match.group(1) not in UNSET_VALUES:
        return quoted_match.group(1)
    return "/" if room_id == "home" else f"/{room_id}"


def parse_list_block(block: str) -> list[dict[str, Any]]:
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
            if rest.startswith("{") and rest.endswith("}"):
                current.update(parse_inline_map(rest))
            elif ":" in rest:
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
        key = key.strip()
        value = value.strip()
        parsed_value: Any
        if value.startswith("{") and value.endswith("}"):
            parsed_value = parse_inline_map(value)
        else:
            parsed_value = strip_value(value)
        if indent >= 6 and nested_key:
            if nested_obj is None:
                nested_obj = {}
            nested_obj[key] = parsed_value
        elif indent == 4:
            if nested_key and nested_obj is not None:
                current[nested_key] = nested_obj
                nested_key = None
                nested_obj = None
            current[key] = parsed_value

    if current is not None:
        if nested_key and nested_obj is not None:
            current[nested_key] = nested_obj
        items.append(current)
    return items


def normalize_capture(capture: Any) -> str | None:
    if isinstance(capture, dict):
        name = capture.get("name")
        if isinstance(name, str) and name not in UNSET_VALUES:
            return name
    if isinstance(capture, str) and capture not in UNSET_VALUES:
        return capture
    return None


def build_plan(room_id: str, markdown: str, blocks: dict[str, str]) -> dict[str, Any]:
    route = parse_route(markdown, room_id)
    missing_blocks = [key for key in REQUIRED_BLOCKS if key not in blocks]
    flow = parse_list_block(blocks.get("interaction_flow", "interaction_flow:"))
    steps: list[dict[str, Any]] = []
    for index, flow_step in enumerate(flow, start=1):
        action = str(flow_step.get("action", "observe"))
        step: dict[str, Any] = {
            "id": flow_step.get("id", f"step_{index}"),
            "label": flow_step.get("label", ""),
            "action": action,
            "wait_ms": int(flow_step.get("wait_ms", 1000) or 1000),
            "selector": flow_step.get("selector", "未設定"),
            "target": flow_step.get("target", "room"),
        }
        if action == "goto":
            step["url"] = route
        if "note" in flow_step:
            step["note"] = flow_step["note"]
        capture = normalize_capture(flow_step.get("capture"))
        if capture:
            step["capture"] = capture
        steps.append(step)

    if steps and not any(step.get("capture") == "initial" for step in steps):
        steps[0]["capture"] = "initial"

    return {
        "room_id": room_id,
        "room_master": str(ROOMS_DIR / f"{room_id}.md"),
        "start_url": route,
        "missing_blocks": missing_blocks,
        "steps": steps,
    }


def load_room_master(room_id: str) -> RoomMaster:
    path = ROOMS_DIR / f"{room_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"部屋マスターが見つかりません: {path}")
    markdown = path.read_text(encoding="utf-8")
    blocks = extract_yaml_blocks(markdown)
    missing_blocks = [key for key in REQUIRED_BLOCKS if key not in blocks]
    plan = build_plan(room_id, markdown, blocks)
    return RoomMaster(
        room_id=room_id,
        path=path,
        markdown=markdown,
        route=parse_route(markdown, room_id),
        blocks=blocks,
        missing_blocks=missing_blocks,
        plan=plan,
    )


def load_all_room_masters() -> list[RoomMaster]:
    masters: list[RoomMaster] = []
    for path in sorted(ROOMS_DIR.glob("*.md")):
        if path.name == "_template.md":
            continue
        masters.append(load_room_master(path.stem))
    return masters


def save_plan(plan: dict[str, Any], run_id: str) -> Path:
    plan_dir = OUTPUT_PLANS / run_id
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_path = plan_dir / f"{plan['room_id']}_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan_path
