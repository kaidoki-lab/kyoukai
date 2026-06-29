"""
KYOUKAI 棒入れ祭 素材入手担当表 v1.0 のリファレンスシート画像から、
36個の個別アセットを切り出して static/images/matsuri/ 配下に保存する。

使い方:
    python scripts/extract_matsuri_assets.py <reference_sheet.png>
"""
import sys
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "static" / "images" / "matsuri"


def to_transparent(img: Image.Image, threshold: int = 16) -> Image.Image:
    """黒背景を透過にする（黒=透明、明るいほど不透明）。"""
    img = img.convert("RGBA")
    pixels = img.getdata()
    new_pixels = []
    for r, g, b, a in pixels:
        lum = max(r, g, b)
        if lum <= threshold:
            new_pixels.append((r, g, b, 0))
        else:
            alpha = min(255, int((lum - threshold) * 1.5))
            new_pixels.append((r, g, b, alpha))
    img.putdata(new_pixels)
    return img


# (box, 出力パス, 透過処理するか)
ITEMS = [
    # 背景（地面）
    ((20, 40, 206, 222), "background/01_ground_dirt.png", False),
    ((20, 290, 140, 372), "background/02_ground_dirt_close.png", False),
    ((172, 290, 290, 372), "background/03_ground_dark.png", False),
    ((322, 290, 442, 372), "background/04_cobblestone.png", False),
    ((20, 444, 140, 494), "background/05_cobblestone_close.png", False),
    # 棒（奉納棒）
    ((480, 65, 645, 448), "pole/06_pole_main.png", False),
    ((668, 160, 730, 218), "pole/07_pole_top.png", False),
    ((668, 294, 730, 352), "pole/08_pole_wood.png", False),
    ((668, 428, 730, 486), "pole/09_pole_rope.png", False),
    # 穴（石組みの穴）
    ((800, 20, 1085, 285), "hole/10_hole_main.png", False),
    ((805, 335, 900, 410), "hole/11_hole_inside.png", False),
    ((935, 335, 1085, 410), "hole/12_hole_edge.png", False),
    ((812, 460, 905, 498), "hole/13_hole_shadow.png", True),
    # 装飾（祭りの装飾）※ 黒背景上の単体オブジェクトなので透過にする
    ((1118, 35, 1495, 172), "decoration/14_shimenawa.png", True),
    ((1118, 228, 1178, 305), "decoration/15_shide_01.png", True),
    ((1188, 228, 1248, 305), "decoration/15_shide_02.png", True),
    ((1258, 228, 1318, 305), "decoration/15_shide_03.png", True),
    ((1328, 228, 1388, 305), "decoration/15_shide_04.png", True),
    ((1398, 228, 1458, 305), "decoration/15_shide_04b.png", True),
    ((1468, 228, 1528, 305), "decoration/15_shide_05.png", True),
    ((1115, 368, 1278, 488), "decoration/16_gohei.png", True),
    # 紙吹雪（PNG／透過）
    ((18, 560, 126, 622), "confetti/17_confetti_white.png", True),
    ((148, 560, 256, 622), "confetti/18_confetti_yellow.png", True),
    ((278, 560, 386, 622), "confetti/19_confetti_red.png", True),
    ((408, 560, 516, 622), "confetti/20_confetti_mix1.png", True),
    ((538, 560, 646, 622), "confetti/21_confetti_mix2.png", True),
    ((668, 560, 786, 622), "effects/22_pole_shadow.png", True),
    # 小物・質感
    ((812, 558, 938, 633), "props/23_rock_large.png", False),
    ((952, 558, 1078, 633), "props/24_rock_medium.png", False),
    ((1092, 558, 1218, 633), "props/25_pebbles.png", False),
    ((1232, 558, 1358, 633), "props/26_leaves.png", False),
    ((1372, 558, 1498, 633), "props/27_woodchips.png", False),
    # エフェクト（PNG／透過）
    ((805, 693, 965, 758), "effects/33_impact_lines.png", True),
    ((995, 693, 1155, 758), "effects/34_flash.png", True),
    ((1185, 693, 1340, 758), "effects/35_motion_blur.png", True),
    ((1378, 693, 1530, 758), "effects/36_vignette.png", True),
]

DUST_ITEMS = [
    ((18, 672, 144, 752), "effects/28_dust_large1.png"),
    ((158, 672, 284, 752), "effects/29_dust_large2.png"),
    ((298, 672, 424, 752), "effects/30_dust_medium.png"),
    ((438, 672, 564, 752), "effects/31_dust_spray.png"),
    ((578, 672, 704, 752), "effects/32_dust_rise.png"),
]


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/extract_matsuri_assets.py <reference_sheet.png>")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    im = Image.open(source_path)

    for box, rel_path, transparent in ITEMS:
        out_path = OUT_DIR / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        crop = im.crop(box)
        if transparent:
            crop = to_transparent(crop)
        crop.save(out_path)
        print(f"saved {out_path.relative_to(BASE_DIR)}")

    for box, rel_path in DUST_ITEMS:
        out_path = OUT_DIR / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        crop = to_transparent(im.crop(box))
        crop.save(out_path)
        print(f"saved {out_path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
