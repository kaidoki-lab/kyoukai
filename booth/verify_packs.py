#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 全パックHTML品質検証スクリプト

booth/all-packs/ 配下の16部屋x3種=48HTMLファイルをPlaywright(chromium,headless)で
開き、consoleエラー・pageerror・canvas存在・lower_thirdの初期名前表示を検証する。
結果は booth/verify_report.json に出力する。
"""
import hashlib
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_packs import ROOMS  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
ALL_PACKS_DIR = BASE_DIR / "all-packs"
REPORT_PATH = BASE_DIR / "verify_report.json"

# 表示名(spec['name']) -> 部屋ID の対応表（brb.htmlの相違チェック・差別化チェックに使う）
ROOM_NAME_TO_ID = {room["name"]: room["id"] for room in ROOMS}

# 検証対象のファイル種別: (サブフォルダ名, ファイル名, 種別キー)
TARGETS = [
    ("01_waiting", "waiting.html", "waiting"),
    ("02_brb", "brb.html", "brb"),
    ("03_lower-third", "lower_third.html", "lower_third"),
]

WAIT_MS = 3000

# 部屋ID -> 固有CSSクラスプレフィックス対応表（room_specs実装で採用されているプレフィックス。
# grepで実クラス名を確認した上で確定させたもの）
ROOM_CLASS_PREFIX = {
    "observation": "obs-",
    "hyougi": "hyo-",
    "null": "null-",
    "observer": "obsr-",
    "exit": "exit-",
    "archive": "arc-",
    "ma": "ma-",
    "daimyojin": "dmj-",
    "gokuraku": "gok-",
    "particles": "ptc-",
    "ripple": "rpl-",
    "kanrinin": "kan-",
    "namahage": "nmh-",
    "matsuri": "mat-",
    "fukashitsu": "fks-",
    "typhoon-news": "tpn-",
}

MIN_PREFIXED_CLASSES = 3


def count_prefixed_classes(html_text: str, prefix: str) -> int:
    """HTML内(styleタグ含む)でprefixから始まるCSSクラス名のユニーク数を数える。
    class="..." の属性値と、CSSセレクタ中の .prefix-xxx 記法の両方を対象にする。
    """
    classes = set()

    # class="a b prefix-c" 形式
    for m in re.finditer(r'class="([^"]*)"', html_text):
        for cls in m.group(1).split():
            if cls.startswith(prefix):
                classes.add(cls)

    # CSSセレクタ .prefix-xxx 形式（style内定義も拾う）
    for m in re.finditer(r'\.(' + re.escape(prefix) + r'[a-zA-Z0-9_-]+)', html_text):
        classes.add(m.group(1))

    return len(classes)


def body_structure_hash(html_text: str) -> str:
    """<body>...</body>内のタグ構成(タグ名の出現順列)からハッシュを作る。
    テキスト内容・属性値は無視し、タグ構造のみを比較対象にする。
    """
    body_match = re.search(r"<body[^>]*>(.*)</body>", html_text, re.DOTALL | re.IGNORECASE)
    body_text = body_match.group(1) if body_match else html_text

    tags = re.findall(r"<(/?[a-zA-Z][a-zA-Z0-9]*)", body_text)
    tag_sequence = ",".join(t.lower() for t in tags)
    return hashlib.sha256(tag_sequence.encode("utf-8")).hexdigest()


def find_room_dirs():
    """all-packs配下の '<部屋名>_OBS素材パック' ディレクトリ一覧を取得する"""
    dirs = []
    for p in sorted(ALL_PACKS_DIR.iterdir()):
        if p.is_dir() and p.name.endswith("_OBS素材パック"):
            dirs.append(p)
    return dirs


def verify_file(page, file_path: Path, kind: str, room_id: str):
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

    # 差別化チェック: 部屋固有CSSクラスプレフィックスが最低3つ存在するか
    prefix = ROOM_CLASS_PREFIX.get(room_id)
    if prefix:
        try:
            html_text = file_path.read_text(encoding="utf-8")
        except Exception as e:
            passed = False
            reasons.append(f"差別化チェック読み込み失敗: {e}")
        else:
            n = count_prefixed_classes(html_text, prefix)
            detail["prefixed_class_count"] = n
            if n < MIN_PREFIXED_CLASSES:
                passed = False
                reasons.append(
                    f"部屋固有クラス({prefix}*)が{MIN_PREFIXED_CLASSES}個未満(実際:{n}個)"
                )
    else:
        passed = False
        reasons.append(f"ROOM_CLASS_PREFIXに部屋ID未登録: {room_id}")

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
    brb_hashes = {}  # room_name -> hash (body構造の互いの相違チェック用)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        for room_dir in room_dirs:
            room_name = room_dir.name.replace("_OBS素材パック", "")
            # room_name(表示名)から部屋IDを逆引きするため、pack_baseのROOMS経由でIDを引く
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

                room_id = ROOM_NAME_TO_ID.get(room_name)
                result = verify_file(page, file_path, kind, room_id)
                report[room_name][kind] = result

                if kind == "brb" and room_id:
                    try:
                        html_text = file_path.read_text(encoding="utf-8")
                        brb_hashes[room_id] = body_structure_hash(html_text)
                    except Exception:
                        pass

                if result["pass"]:
                    passed_count += 1
                    print(f"  OK {room_name}/{kind}")
                else:
                    print(f"  NG {room_name}/{kind} : {result['reasons']}")

        browser.close()

    # brb.htmlのbody構造ハッシュが全部屋で互いに異なるかチェック
    print("")
    print("=== brb.html body構造の相違チェック ===")
    hash_to_rooms = {}
    for room_id, h in brb_hashes.items():
        hash_to_rooms.setdefault(h, []).append(room_id)

    duplicate_found = False
    for h, rooms in hash_to_rooms.items():
        if len(rooms) > 1:
            duplicate_found = True
            print(f"  NG body構造が同一のbrb.html: {rooms}")
            for room_id in rooms:
                room_name = next((k for k, v in ROOM_NAME_TO_ID.items() if v == room_id), room_id)
                for kind_key in ("brb",):
                    if room_name in report and kind_key in report[room_name]:
                        report[room_name][kind_key]["pass"] = False
                        report[room_name][kind_key]["reasons"].append(
                            f"brb.htmlのbody構造が他部屋と同一: {rooms}"
                        )
                        passed_count = max(0, passed_count - 1)

    if not duplicate_found:
        print(f"  OK 全{len(brb_hashes)}部屋のbrb.html body構造は互いに異なる")

    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("")
    print(f"検証完了: {passed_count}/{total} pass")
    print(f"レポート出力先: {REPORT_PATH}")

    if passed_count != total or duplicate_found:
        print("一部失敗あり。verify_report.jsonを確認してください。")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
