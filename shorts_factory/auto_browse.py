"""
KYOUKAI Shorts Factory — ブラウザ自動巡回
1. OBS 録画開始
2. browse_steps.json に従ってKYOUKAIを巡回
3. OBS 録画停止
4. 録画ファイルをセッションフォルダへ移動
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, Page

ROOT = Path(__file__).resolve().parent
INPUT_VIDEOS = ROOT / "input_videos"
OBS_CONTROL = ROOT / "tools" / "obs_control.js"

# iPhone 14 Pro サイズ（9:16）
VIEWPORT = {"width": 393, "height": 852}


def now_jst() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))


def find_today_session() -> Path:
    date_str = now_jst().strftime("%Y-%m-%d")
    session_dir = ROOT / "sessions" / date_str
    if not session_dir.exists():
        print(f"ERROR: セッションフォルダが見つかりません: {session_dir}")
        print("先に generate_scenario.py を実行してください。")
        sys.exit(1)
    return session_dir


def load_steps(session_dir: Path) -> dict:
    steps_path = session_dir / "browse_steps.json"
    if not steps_path.exists():
        print(f"ERROR: {steps_path} が見つかりません。")
        sys.exit(1)
    with steps_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def obs_command(action: str) -> bool:
    if not OBS_CONTROL.exists():
        print(f"WARNING: {OBS_CONTROL} が見つかりません。OBS制御をスキップします。")
        return False
    try:
        result = subprocess.run(
            ["node", str(OBS_CONTROL), action],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print(f"OBS {action}: 成功")
            return True
        else:
            print(f"OBS {action}: 失敗 ({result.stderr.strip()[:100]})")
            return False
    except Exception as exc:
        print(f"OBS {action}: エラー ({exc})")
        return False


def find_latest_recording() -> Path | None:
    video_exts = {".mp4", ".mkv", ".mov", ".flv"}
    videos = [
        p for p in INPUT_VIDEOS.iterdir()
        if p.is_file() and p.suffix.lower() in video_exts
    ]
    if not videos:
        return None
    return max(videos, key=lambda p: p.stat().st_mtime)


def move_recording_to_session(session_dir: Path) -> Path | None:
    # OBSがファイルを閉じるまで少し待つ
    time.sleep(3)
    latest = find_latest_recording()
    if not latest:
        print("WARNING: 録画ファイルが見つかりませんでした。")
        return None
    dest = session_dir / f"raw_footage{latest.suffix}"
    shutil.move(str(latest), str(dest))
    print(f"録画ファイルを移動: {dest}")
    return dest


def execute_step(page: Page, step: dict) -> None:
    action = step.get("action")
    wait = step.get("wait", 1)

    if action == "navigate":
        url = step["url"]
        print(f"  → 移動: {url}")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(wait)

    elif action == "scroll":
        amount = step.get("amount", 300)
        page.evaluate(f"window.scrollBy({{top: {amount}, behavior: 'smooth'}})")
        time.sleep(wait)

    elif action == "pause":
        seconds = step.get("seconds", 2)
        print(f"  → 待機: {seconds}秒")
        time.sleep(seconds)

    elif action == "click":
        selector = step.get("selector", "")
        if selector:
            try:
                page.click(selector, timeout=3000)
                print(f"  → クリック: {selector}")
            except Exception:
                print(f"  → クリック失敗（スキップ）: {selector}")
        time.sleep(wait)

    elif action == "hover":
        selector = step.get("selector", "")
        if selector:
            try:
                page.hover(selector, timeout=3000)
                print(f"  → ホバー: {selector}")
            except Exception:
                print(f"  → ホバー失敗（スキップ）: {selector}")
        time.sleep(wait)

    elif action == "mouse_move":
        x = step.get("x", VIEWPORT["width"] // 2)
        y = step.get("y", VIEWPORT["height"] // 2)
        print(f"  → マウス移動: ({x}, {y})")
        page.mouse.move(x, y)
        time.sleep(wait)

    elif action == "mouse_click":
        x = step.get("x", VIEWPORT["width"] // 2)
        y = step.get("y", VIEWPORT["height"] // 2)
        print(f"  → マウスクリック: ({x}, {y})")
        page.mouse.move(x, y)
        time.sleep(0.5)
        page.mouse.click(x, y)
        time.sleep(wait)


def run_clip(page: Page, clip: dict, index: int) -> None:
    title = clip.get("clip_title", f"クリップ{index + 1}")
    steps = clip.get("steps", [])
    print(f"\n[クリップ {index + 1}] {title}")
    for step in steps:
        execute_step(page, step)
    print(f"  クリップ終了。次まで3秒待機...")
    time.sleep(3)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    session_dir = find_today_session()
    browse_data = load_steps(session_dir)

    clips = browse_data.get("clips", [])
    theme = browse_data.get("title", "（テーマなし）")

    print("=" * 50)
    print(f"今日のテーマ: {theme}")
    print(f"クリップ数: {len(clips)}")
    print("=" * 50)

    print("\n巡回を開始します（ブラウザが自動録画します）\n")

    video_dir = session_dir / "raw_clips"
    video_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                f"--window-size={VIEWPORT['width']},{VIEWPORT['height'] + 100}",
                "--window-position=0,0",
            ],
        )

        print("\nブラウザ起動。巡回開始します。\n")

        for i, clip in enumerate(clips):
            clip_title = clip.get("clip_title", f"clip_{i+1:02d}")
            print(f"\n[クリップ {i+1}] {clip_title} — 録画開始")

            # クリップごとに独立した動画を録画
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
                record_video_dir=str(video_dir),
                record_video_size=VIEWPORT,
            )
            page = context.new_page()

            for step in clip.get("steps", []):
                execute_step(page, step)

            # contextを閉じると動画ファイルが確定する
            video_path = page.video.path() if page.video else None
            context.close()

            # ファイル名をクリップ番号＋タイトルに変更
            if video_path and Path(video_path).exists():
                safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in clip_title)
                dest = video_dir / f"clip_{i+1:02d}_{safe_title}.webm"
                Path(video_path).rename(dest)
                print(f"  録画保存: {dest.name}")

            time.sleep(2)

        browser.close()

    print(f"\n全クリップ完了。")
    print(f"セッションフォルダ: {session_dir}")
    subprocess.Popen(["explorer", str(video_dir)])


if __name__ == "__main__":
    main()
