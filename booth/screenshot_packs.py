#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 商品画像用スクリーンショット自動撮影スクリプト

booth/all-packs/ 配下の16部屋x3種(waiting/brb/lower_third)を
Playwright(chromium,headless)で撮影し、booth/thumbnails/<部屋ID>/ に保存する。
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_packs import ROOMS  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
ALL_PACKS_DIR = BASE_DIR / "all-packs"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"

VIEWPORT = {"width": 1920, "height": 1080}
DEVICE_SCALE_FACTOR = 1
WAIT_MS = 5000
EXPECTED_SIZE = (1920, 1080)

# 輝度閾値(平均輝度がこの値を超えることを要求)。部屋別に緩和可能。
BRIGHTNESS_THRESHOLD_DEFAULT = 1.0
BRIGHTNESS_THRESHOLD_OVERRIDES = {
    "observer": 0.3,  # 逆観測室: 白黒基調・低輝度デザインのため緩和
}
MAX_RETRIES = 5

LOWER_THIRD_BG_STYLE = """
html, body {
  background: linear-gradient(135deg, #0a0a12 0%, #1a1a2e 50%, #0d0d18 100%) !important;
}
"""


def room_pack_dir(room):
    pack_name = f"{room['name']}_OBS素材パック"
    return ALL_PACKS_DIR / pack_name


def mean_brightness(png_path: Path) -> float:
    img = Image.open(png_path).convert("L")
    pixels = list(img.getdata())
    return sum(pixels) / len(pixels)


def brightness_threshold(room_id: str) -> float:
    return BRIGHTNESS_THRESHOLD_OVERRIDES.get(room_id, BRIGHTNESS_THRESHOLD_DEFAULT)


def shoot_waiting_or_brb(page, html_path: Path, out_path: Path, room_id: str, label: str):
    url = html_path.as_uri()
    for attempt in range(1, MAX_RETRIES + 1):
        page.goto(url)
        page.wait_for_timeout(WAIT_MS)
        page.screenshot(path=str(out_path))
        brightness = mean_brightness(out_path)
        threshold = brightness_threshold(room_id)
        if brightness > threshold:
            print(f"  OK {room_id}/{label} (brightness={brightness:.2f})")
            return
        print(f"  RETRY {room_id}/{label} attempt {attempt} brightness={brightness:.2f} <= {threshold}")
    print(f"  WARN {room_id}/{label} : brightness check did not pass after {MAX_RETRIES} attempts")


def shoot_lower_third(page, html_path: Path, out_path: Path, room_id: str):
    url = html_path.as_uri() + "?name=サンプル&title=配信者"
    page.goto(url)
    page.add_style_tag(content=LOWER_THIRD_BG_STYLE)
    page.wait_for_timeout(1500)
    page.screenshot(path=str(out_path))
    print(f"  OK {room_id}/lower_third")


def verify_all():
    ok = True
    for room in ROOMS:
        room_dir = THUMBNAILS_DIR / room["id"]
        for fname in ["01_waiting.png", "02_brb.png", "03_lower_third.png"]:
            fpath = room_dir / fname
            if not fpath.exists():
                print(f"  MISSING {room['id']}/{fname}")
                ok = False
                continue
            with Image.open(fpath) as img:
                size = img.size
            if size != EXPECTED_SIZE:
                print(f"  SIZE_NG {room['id']}/{fname} : {size}")
                ok = False
            if fname in ("01_waiting.png", "02_brb.png"):
                brightness = mean_brightness(fpath)
                threshold = brightness_threshold(room["id"])
                if brightness <= threshold:
                    print(f"  BRIGHTNESS_NG {room['id']}/{fname} : {brightness:.2f} <= {threshold}")
                    ok = False
    return ok


def main():
    THUMBNAILS_DIR.mkdir(exist_ok=True)
    print(f"撮影対象部屋数: {len(ROOMS)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport=VIEWPORT,
            device_scale_factor=DEVICE_SCALE_FACTOR,
        )

        for room in ROOMS:
            room_id = room["id"]
            pack_dir = room_pack_dir(room)
            out_dir = THUMBNAILS_DIR / room_id
            out_dir.mkdir(parents=True, exist_ok=True)

            waiting_html = pack_dir / "01_waiting" / "waiting.html"
            brb_html = pack_dir / "02_brb" / "brb.html"
            lower_third_html = pack_dir / "03_lower-third" / "lower_third.html"

            shoot_waiting_or_brb(page, waiting_html, out_dir / "01_waiting.png", room_id, "waiting")
            shoot_waiting_or_brb(page, brb_html, out_dir / "02_brb.png", room_id, "brb")
            shoot_lower_third(page, lower_third_html, out_dir / "03_lower_third.png", room_id)

        browser.close()

    print("")
    print("撮影完了。サイズ・輝度チェックを実行します...")
    ok = verify_all()
    if ok:
        print("チェック完了: 全48枚が1920x1080、waiting系の輝度チェックpass")
        return 0
    else:
        print("チェック失敗あり。上記のログを確認してください。")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
