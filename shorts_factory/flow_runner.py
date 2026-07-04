"""Playwright execution for ShortFACTORY room master plans."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

from playwright.sync_api import Page, sync_playwright

from room_master_loader import UNSET_VALUES


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
OUTPUT_RECORDINGS = SHORTS_ROOT / "output_recordings"
OUTPUT_CAPTURES = SHORTS_ROOT / "output_captures"
VIEWPORT = {"width": 390, "height": 844}
MIN_RECORDING_BYTES = 20_000
SUPPORTED_ACTIONS = {"goto", "observe", "click", "repeat_click", "wait"}


def absolute_url(base_url: str, url: str) -> str:
    if re.match(r"^https?://", url):
        return url
    return urljoin(base_url.rstrip("/") + "/", url.lstrip("/"))


def safe_capture_name(index: int, name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "capture"
    return f"{index:02d}_{safe}.png"


def take_capture(page: Page, capture_dir: Path, index: int, capture_name: str) -> str:
    capture_dir.mkdir(parents=True, exist_ok=True)
    capture_path = capture_dir / safe_capture_name(index, capture_name)
    page.screenshot(path=str(capture_path), full_page=True)
    return str(capture_path)


def quality_warnings(result: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    recording = result.get("recording", "")
    if not recording or not Path(recording).exists():
        warnings.append("録画ファイルが存在しない")
    elif Path(recording).stat().st_size < MIN_RECORDING_BYTES:
        warnings.append("録画ファイルサイズが小さすぎる")
    if not result.get("captures"):
        warnings.append("スクリーンショットが1枚もない")
    if result.get("steps_executed", 0) == 0:
        warnings.append("実行ステップが0")
    if result.get("click_steps", 0) > 0 and result.get("click_steps") == result.get("unset_click_steps"):
        warnings.append("クリック可能ステップがすべて未設定")
    if result.get("goto_failed"):
        warnings.append("ページ遷移に失敗した")
    return warnings


def run_plan(
    plan: dict[str, Any],
    base_url: str,
    run_id: str,
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    room_id = plan["room_id"]
    recording_dir = OUTPUT_RECORDINGS / run_id
    tmp_dir = recording_dir / "_tmp"
    capture_dir = OUTPUT_CAPTURES / run_id / room_id
    recording_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    capture_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "room_id": room_id,
        "status": "success",
        "recording": "",
        "captures": [],
        "capture_dir": str(capture_dir),
        "steps_executed": 0,
        "steps_skipped": 0,
        "click_steps": 0,
        "unset_click_steps": 0,
        "warnings": [],
        "errors": [],
        "missing_blocks": plan.get("missing_blocks", []),
        "plan_steps": len(plan.get("steps", [])),
        "goto_failed": False,
    }

    if result["missing_blocks"]:
        result["warnings"].append("不足YAMLブロック: " + ", ".join(result["missing_blocks"]))
    if not plan.get("steps"):
        result["status"] = "skipped"
        result["warnings"].append("Interaction Flowのステップがない")
        return result

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
            record_video_dir=str(tmp_dir),
            record_video_size=VIEWPORT,
        )
        context.add_init_script(
            "try { localStorage.setItem('kyoukai_intro_done', '1'); } catch (e) {}"
        )
        page = context.new_page()
        for index, step in enumerate(plan.get("steps", []), start=1):
            action = step.get("action", "observe")
            selector = str(step.get("selector", "未設定"))
            step_id = step.get("id", f"step_{index}")
            wait_ms = int(step.get("wait_ms", 1000) or 1000)
            try:
                if action == "goto":
                    url = absolute_url(base_url, str(step.get("url") or plan.get("start_url", "/")))
                    log(f"[{room_id}] STEP {index}: goto {url}")
                    response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    if response and response.status >= 400:
                        result["warnings"].append(f"ページステータス {response.status}: {url}")
                    result["steps_executed"] += 1
                elif action in {"observe", "wait"}:
                    log(f"[{room_id}] STEP {index}: {action} target={step.get('target', 'room')}")
                    result["steps_executed"] += 1
                elif action in {"click", "repeat_click"}:
                    result["click_steps"] += 1
                    if selector in UNSET_VALUES:
                        log(f"[{room_id}] SKIP: selector 未設定 step={step_id}")
                        result["unset_click_steps"] += 1
                        result["steps_skipped"] += 1
                    else:
                        count = 3 if action == "repeat_click" else 1
                        log(f"[{room_id}] STEP {index}: {action} {selector} count={count}")
                        for _ in range(count):
                            page.click(selector, timeout=5000, force=True)
                            time.sleep(0.2)
                        result["steps_executed"] += 1
                else:
                    log(f"[{room_id}] SKIP: 未対応 action={action} step={step_id}")
                    result["steps_skipped"] += 1
                time.sleep(max(wait_ms, 0) / 1000)
                capture_name = step.get("capture")
                if capture_name:
                    capture = take_capture(page, capture_dir, index, str(capture_name))
                    result["captures"].append(capture)
                    log(f"[{room_id}] CAPTURE: {capture}")
            except Exception as exc:
                message = f"step={step_id}: {exc}"
                log(f"[{room_id}] ERROR {message}")
                result["errors"].append(message)
                if action == "goto":
                    result["goto_failed"] = True
        if not result["captures"]:
            try:
                capture = take_capture(page, capture_dir, 1, "initial")
                result["captures"].append(capture)
                log(f"[{room_id}] CAPTURE fallback: {capture}")
            except Exception as exc:
                result["errors"].append(f"fallback_capture: {exc}")
        video_path = page.video.path() if page.video else None
        context.close()
        browser.close()

    if video_path and Path(video_path).exists():
        final_path = recording_dir / f"{room_id}.webm"
        Path(video_path).replace(final_path)
        result["recording"] = str(final_path)
    result["warnings"].extend(quality_warnings(result))
    if result["errors"]:
        result["status"] = "failed"
    elif result["warnings"]:
        result["status"] = "success_with_warnings"
    else:
        result["status"] = "success"
    return result
