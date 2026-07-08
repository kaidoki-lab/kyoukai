#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック サムネイル1枚目（メイン画像）生成"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from generate_packs import ROOMS

BASE_DIR = Path(__file__).resolve().parent
THUMB_DIR = BASE_DIR / "thumbnails"

CANVAS_W = 1920
CANVAS_H = 1080

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]

SERIES_NAME = "KYOUKAI OBS PACK"
SET_TEXT = "待機画面 / 離席画面 / 名前テロップ  3点セット"
# 待機画面 / 離席画面 / 名前テロップ 3点セット


def load_font(size):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def draw_letter_spaced(draw, xy, text, font, fill, spacing, anchor_center_x=None):
    """letter-spacing風の描画。anchor_center_xが指定されれば中央揃えでx位置を計算する。"""
    x, y = xy
    widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        w = bbox[2] - bbox[0]
        widths.append(w)
    total_width = sum(widths) + spacing * (len(text) - 1 if len(text) > 0 else 0)

    if anchor_center_x is not None:
        x = anchor_center_x - total_width / 2

    cur_x = x
    for ch, w in zip(text, widths):
        draw.text((cur_x, y), ch, font=font, fill=fill)
        cur_x += w + spacing

    return total_width


def make_thumbnail(room):
    room_id = room['id']
    name = room['name']
    color = room['color']
    rgb = hex_to_rgb(color)

    src_path = THUMB_DIR / room_id / "01_waiting.png"
    if not src_path.exists():
        print(f"  SKIP {room_id}: 01_waiting.png not found")
        return False

    base = Image.open(src_path).convert("RGB")
    if base.size != (CANVAS_W, CANVAS_H):
        base = base.resize((CANVAS_W, CANVAS_H))

    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # 上部帯（シリーズ名用の半透明黒帯）
    odraw.rectangle([(0, 0), (CANVAS_W, 130)], fill=(0, 0, 0, 150))

    # 中央下（部屋名+ID用の半透明黒帯）
    odraw.rectangle([(0, 620), (CANVAS_W, 900)], fill=(0, 0, 0, 170))

    # 下部帯（3点セット表記用の半透明黒帯）
    odraw.rectangle([(0, 960), (CANVAS_W, 1080)], fill=(0, 0, 0, 180))

    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(base)

    # 枠: テーマカラーの細枠
    border_width = 6
    draw.rectangle(
        [(border_width // 2, border_width // 2),
         (CANVAS_W - 1 - border_width // 2, CANVAS_H - 1 - border_width // 2)],
        outline=color, width=border_width,
    )

    # 上部: シリーズ名（letter-spacing風）
    series_font = load_font(34)
    draw_letter_spaced(
        draw, (0, 55), SERIES_NAME, series_font,
        fill=(255, 255, 255), spacing=10, anchor_center_x=CANVAS_W / 2,
    )

    # 中央下: 部屋名（日本語・大きく）+ 部屋ID（英字・小さく）
    # 文字数で2段階のフォントサイズ分岐
    name_len = len(name)
    if name_len <= 4:
        name_size = 150
    else:
        name_size = 100
    name_font = load_font(name_size)

    name_bbox = draw.textbbox((0, 0), name, font=name_font)
    name_w = name_bbox[2] - name_bbox[0]
    name_h = name_bbox[3] - name_bbox[1]
    name_x = (CANVAS_W - name_w) / 2
    name_y = 660
    # 縁取り（黒）で視認性を確保
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            if dx or dy:
                draw.text((name_x + dx, name_y + dy), name, font=name_font, fill=(0, 0, 0))
    draw.text((name_x, name_y), name, font=name_font, fill=(255, 255, 255))

    id_font = load_font(28)
    id_text = room_id
    id_bbox = draw.textbbox((0, 0), id_text, font=id_font)
    id_w = id_bbox[2] - id_bbox[0]
    id_x = (CANVAS_W - id_w) / 2
    id_y = name_y + name_h + 40
    draw.text((id_x, id_y), id_text, font=id_font, fill=color)

    # 下部: 3点セット表記
    set_font = load_font(30)
    set_bbox = draw.textbbox((0, 0), SET_TEXT, font=set_font)
    set_w = set_bbox[2] - set_bbox[0]
    set_x = (CANVAS_W - set_w) / 2
    draw.text((set_x, 985), SET_TEXT, font=set_font, fill=(255, 255, 255))

    out_path = THUMB_DIR / room_id / "00_main.png"
    base.save(out_path)
    print(f"  OK {room_id} -> {out_path.name}")
    return True


def main():
    print("Thumbnail generation start...")
    ok_count = 0
    for room in ROOMS:
        if make_thumbnail(room):
            ok_count += 1
    print(f"\nDone: {ok_count}/{len(ROOMS)} rooms")


if __name__ == '__main__':
    main()
