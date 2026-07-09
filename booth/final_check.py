#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 最終検証スクリプト（工程6）

booth/all-packs, booth/thumbnails, booth/listings, booth/verify_report.json
を検証し、出品可能状態であることを確認する。
"""
import sys
import json
import io
from pathlib import Path

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

try:
    from PIL import Image
except ImportError:
    print("[FATAL] Pillow未導入です。 pip install Pillow を実行してください。")
    sys.exit(1)

sys.path.insert(0, str(BASE_DIR))
from generate_packs import ROOMS  # noqa: E402

ALL_PACKS_DIR = BASE_DIR / "all-packs"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"
LISTINGS_DIR = BASE_DIR / "listings"
VERIFY_REPORT_PATH = BASE_DIR / "verify_report.json"

REQUIRED_SIZE = (1920, 1080)
THUMB_FILES = ["00_main.png", "01_waiting.png", "02_brb.png", "03_lower_third.png"]

overall_ok = True


def report(ok, message):
    global overall_ok
    status = "PASS" if ok else "FAIL"
    if not ok:
        overall_ok = False
    print("[{}] {}".format(status, message))


def check_zips():
    print("")
    print("=== 1. zipファイル検証 (all-packs) ===")
    if not ALL_PACKS_DIR.is_dir():
        report(False, "all-packsディレクトリが存在しません: {}".format(ALL_PACKS_DIR))
        return

    expected_names = []
    for room in ROOMS:
        expected_names.append("{}_OBS素材パック.zip".format(room["name"]))
    bundle_name = "KYOUKAI_全部屋_OBS素材パック.zip"
    expected_names.append(bundle_name)

    missing = []
    for name in expected_names:
        path = ALL_PACKS_DIR / name
        if path.is_file():
            report(True, "zip存在: {}".format(name))
        else:
            report(False, "zip不足: {}".format(name))
            missing.append(name)

    actual_zip_count = len(list(ALL_PACKS_DIR.glob("*.zip")))
    report(
        len(missing) == 0 and actual_zip_count == 17,
        "zip本数 = {} 本 (期待値17本、単品{}本+バンドル1本)".format(
            actual_zip_count, len(ROOMS)
        ),
    )

    print("")
    print("=== 1b. zipサイズ検証（単品5MB以内） ===")
    MAX_SINGLE_ZIP_BYTES = 5 * 1024 * 1024
    for room in ROOMS:
        name = "{}_OBS素材パック.zip".format(room["name"])
        path = ALL_PACKS_DIR / name
        if not path.is_file():
            continue
        size = path.stat().st_size
        report(
            size <= MAX_SINGLE_ZIP_BYTES,
            "zipサイズ: {} = {:.2f}MB (上限5MB)".format(name, size / (1024 * 1024)),
        )


def check_thumbnails():
    print("")
    print("=== 2. サムネイル検証 (thumbnails) ===")
    if not THUMBNAILS_DIR.is_dir():
        report(False, "thumbnailsディレクトリが存在しません: {}".format(THUMBNAILS_DIR))
        return

    for room in ROOMS:
        room_dir = THUMBNAILS_DIR / room["id"]
        if not room_dir.is_dir():
            report(False, "部屋ディレクトリ不足: {}".format(room["id"]))
            continue
        for fname in THUMB_FILES:
            fpath = room_dir / fname
            if not fpath.is_file():
                report(False, "画像不足: {}/{}".format(room["id"], fname))
                continue
            try:
                with Image.open(fpath) as img:
                    size = img.size
            except Exception as e:
                report(False, "画像読み込み失敗: {}/{} ({})".format(room["id"], fname, e))
                continue
            if size == REQUIRED_SIZE:
                report(True, "{}/{} = {}x{}".format(room["id"], fname, size[0], size[1]))
            else:
                report(
                    False,
                    "{}/{} サイズ不正 = {}x{} (期待値1920x1080)".format(
                        room["id"], fname, size[0], size[1]
                    ),
                )

    total_expected = len(ROOMS) * len(THUMB_FILES)
    total_actual = len(list(THUMBNAILS_DIR.glob("*/*.png")))
    report(
        total_actual == total_expected,
        "サムネイル総数 = {} 枚 (期待値{}枚 = 16部屋x4枚)".format(
            total_actual, total_expected
        ),
    )


def check_listings():
    print("")
    print("=== 3. 商品ページ文章検証 (listings) ===")
    if not LISTINGS_DIR.is_dir():
        report(False, "listingsディレクトリが存在しません: {}".format(LISTINGS_DIR))
        return

    for room in ROOMS:
        fpath = LISTINGS_DIR / "{}.md".format(room["id"])
        report(fpath.is_file(), "listing存在: {}.md".format(room["id"]))

    for extra in ["_series.md", "_bundle.md", "_出品手順.md"]:
        fpath = LISTINGS_DIR / extra
        report(fpath.is_file(), "listing存在: {}".format(extra))

    total_expected = len(ROOMS) + 3
    required_names = set(["{}.md".format(room["id"]) for room in ROOMS])
    required_names.update(["_series.md", "_bundle.md", "_出品手順.md"])
    existing_names = set(p.name for p in LISTINGS_DIR.glob("*.md"))
    missing_required = required_names - existing_names
    report(
        len(missing_required) == 0,
        "listings必須ファイル = {}件中{}件確認 (不足{}件。付随ファイルの有無は判定対象外)".format(
            total_expected, total_expected - len(missing_required), len(missing_required)
        ),
    )


def check_verify_report():
    print("")
    print("=== 4. verify_report.json検証 ===")
    if not VERIFY_REPORT_PATH.is_file():
        report(False, "verify_report.jsonが存在しません: {}".format(VERIFY_REPORT_PATH))
        return

    try:
        with open(VERIFY_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        report(False, "verify_report.json読み込み失敗: {}".format(e))
        return

    fail_count = 0
    entry_count = 0
    for room_key, room_result in data.items():
        for file_key, file_result in room_result.items():
            entry_count += 1
            if not file_result.get("pass", False):
                fail_count += 1
                report(False, "verify_report FAIL: {} / {}".format(room_key, file_key))

    report(
        fail_count == 0 and entry_count > 0,
        "verify_report.json 全{}エントリ中 FAIL {}件".format(entry_count, fail_count),
    )


def main():
    print("KYOUKAI OBSパック 最終検証を開始します")
    check_zips()
    check_thumbnails()
    check_listings()
    check_verify_report()

    print("")
    print("=== 総合判定 ===")
    if overall_ok:
        print("ALL PASS")
        print("出品準備は機械的チェックにおいて完了しています。")
        print("次はOBS実機確認手順書 booth/listings/_OBS実機確認手順.md に従い、")
        print("最低1部屋分の3素材(waiting/brb/lower_third)をOBS Studioで確認してください。")
        return 0
    else:
        print("FAIL")
        print("上記のFAIL項目を修正してから再実行してください。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
