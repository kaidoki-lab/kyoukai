#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 全パックHTML品質検証スクリプト

booth/all-packs/ 配下の16部屋x3種=48HTMLファイルをPlaywright(chromium,headless)で
開き、consoleエラー・pageerror・canvas存在・lower_thirdの初期名前表示を検証する。
結果は booth/verify_report.json に出力する。
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
ALL_PACKS_DIR = BASE_DIR / "all-packs"
REPORT_PATH = BASE_DIR / "verify_report.json"

# 検証対象のファイル種別: (サブフォルダ名, ファイル名, 種別キー)
TARGETS = [
    ("01_waiting", "waiting.html", "waiting"),
    ("02_brb", "brb.html", "brb"),
    ("03_lower-third", "lower_third.html", "lower_third"),
]

WAIT_MS = 3000


def find_room_dirs():
    """all-packs配下の '<部屋名>_OBS素材パック' ディレクトリ一覧を取得する"""
    dirs = []
    for p in sorted(ALL_PACKS_DIR.iterdir()):
        if p.is_dir() and p.name.endswith("_OBS素材パック"):
            dirs.append(p)
    return dirs


def verify_file(page, file_path: Path, kind: str):
    """1ファイルを検証し、結果dictを返す"""
    console_errors = []
    page_errors = []

    def on_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    def on_pageerror(exc):
        page_errors.append(str(exc))

    page.on("console", on_console)
    page.on("pageerror", on_pageerror)

    detail = {}
    passed = True
    reasons = []

    try:
        url = file_path.as_uri()
        page.goto(url)
        page.wait_for_timeout(WAIT_MS)

        if kind in ("waiting", "brb"):
            canvas_count = page.locator("canvas").count()
            detail["canvas_count"] = canvas_count
            if canvas_count < 1:
                passed = False
                reasons.append("canvas要素が見つからない")

        if kind == "lower_third":
            name_text = page.locator("#name-el").text_content()
            detail["name_el_text"] = name_text
            if name_text != "名前":
                passed = False
                reasons.append(f"#name-elのtextContentが'名前'ではない(実際:{name_text})")

    except Exception as e:
        passed = False
        reasons.append(f"例外発生: {e}")

    finally:
        page.remove_listener("console", on_console)
        page.remove_listener("pageerror", on_pageerror)

    if console_errors:
        passed = False
        reasons.append(f"consoleエラー{len(console_errors)}件")
    if page_errors:
        passed = False
        reasons.append(f"pageerror{len(page_errors)}件")

    return {
        "pass": passed,
        "reasons": reasons,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "detail": detail,
    }


def main():
    room_dirs = find_room_dirs()
    print(f"検証対象部屋数: {len(room_dirs)}")

    report = {}
    total = 0
    passed_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        for room_dir in room_dirs:
            room_name = room_dir.name.replace("_OBS素材パック", "")
            report[room_name] = {}
            for sub, fname, kind in TARGETS:
                file_path = room_dir / sub / fname
                total += 1
                if not file_path.exists():
                    report[room_name][kind] = {
                        "pass": False,
                        "reasons": ["ファイルが存在しない"],
                        "console_errors": [],
                        "page_errors": [],
                        "detail": {},
                    }
                    print(f"  NG {room_name}/{kind} : ファイルが存在しない")
                    continue

                result = verify_file(page, file_path, kind)
                report[room_name][kind] = result
                if result["pass"]:
                    passed_count += 1
                    print(f"  OK {room_name}/{kind}")
                else:
                    print(f"  NG {room_name}/{kind} : {result['reasons']}")

        browser.close()

    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("")
    print(f"検証完了: {passed_count}/{total} pass")
    print(f"レポート出力先: {REPORT_PATH}")

    if passed_count != total:
        print("一部失敗あり。verify_report.jsonを確認してください。")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
