#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 本体アセット抽出

KYOUKAI本体(static/*.js, static/*.css, static/images/*, shorts_factory/*, typhoon-news/*)
の一次データを、room_specsから参照・パックへ同梱するための共通機能。
「その部屋らしさ」の根拠を一次データに置くための入口。
"""
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

# booth/ の親 = リポジトリルート(KYOUKAI本体)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def read_source(src_rel: str) -> str:
    """本体JS/CSS/JSONをテキストで読む。room_specが定数抽出に使う。

    src_rel: PROJECT_ROOTからの相対パス(例: 'static/ripple.js')
    存在しない場合は明確なエラーで落とす(黙ってスキップしない)。
    """
    src_path = PROJECT_ROOT / src_rel
    if not src_path.is_file():
        raise FileNotFoundError(
            f"[asset_extract.read_source] 本体ソースが見つかりません: {src_path}"
        )
    return src_path.read_text(encoding='utf-8')


def copy_image(src_rel: str, spec_id: str, out_root, max_edge: int = 1500) -> str:
    """本体画像をパックの assets/ へコピーする。

    src_rel: PROJECT_ROOTからの相対パス(例: 'static/images/kanrinin/kanrinin-room-9x16.png')
    spec_id: 部屋ID(パックフォルダ特定に使う。呼び出し元がpack_dirを解決していない場合は
             out_rootを直接 all-packs/<pack_name>/assets とみなして使う運用でも良い)
    out_root: コピー先の assets ディレクトリ(Path or str)。呼び出し元(room_spec)が
              「そのパックのassets/」を渡す契約とする。
    max_edge: 長辺がこれを超える場合は縮小する(既定1500px)

    戻り値: パック内からの相対パス 'assets/<ファイル名>' (HTML内で使う相対パス文字列)
    """
    if Image is None:
        raise RuntimeError(
            "[asset_extract.copy_image] Pillowが導入されていません。 pip install Pillow を実行してください。"
        )

    src_path = PROJECT_ROOT / src_rel
    if not src_path.is_file():
        raise FileNotFoundError(
            f"[asset_extract.copy_image] 本体画像が見つかりません(spec_id={spec_id}): {src_path}"
        )

    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    dest_path = out_root / src_path.name

    with Image.open(src_path) as img:
        w, h = img.size
        long_edge = max(w, h)
        if long_edge > max_edge:
            scale = max_edge / long_edge
            new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
            img = img.resize(new_size, Image.LANCZOS)

        save_kwargs = {}
        fmt = (img.format or src_path.suffix.lstrip('.').upper())
        suffix = src_path.suffix.lower()
        if suffix in ('.jpg', '.jpeg'):
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            save_kwargs = {'quality': 85, 'optimize': True}
            img.save(dest_path, 'JPEG', **save_kwargs)
        elif suffix == '.png':
            save_kwargs = {'optimize': True}
            img.save(dest_path, 'PNG', **save_kwargs)
        elif suffix == '.webp':
            save_kwargs = {'quality': 85, 'method': 6}
            img.save(dest_path, 'WEBP', **save_kwargs)
        else:
            img.save(dest_path)

    return f"assets/{dest_path.name}"


# ───────────────────────────────────────────────
# ASSET_MAP: 部屋ID -> 本体画像の実在相対パスのリスト
#
# 実地調査結果(工程1時点):
#   git ls-files / find で static/images/ 配下・typhoon-news/ 配下を捜索して確定。
#   - kanrinin: static/images/kanrinin/kanrinin-room-9x16.png (実在)
#   - namahage: static/images/namahage/namahage-room-9x16.png (実在)
#   - matsuri : static/images/matsuri/pole/06_pole_main.png ほか多数の部品素材が実在
#               (棒/穴/紙吹雪/しめ縄・紙垂/御幣/背景/エフェクト群)
#   - fukashitsu: static/images/fukashitsu/fukashitsu-room-9x16.png (実在)
#   - typhoon-news: typhoon-news/assets/typhoon-news-bg.png (実在)
#   - daimyojin: static/images/daimyojin/daimyojin_pc.webp,
#                static/images/daimyojin/daimyojin_mobile.webp (実在。ROADMAP作成時点で未確認だったが確定)
#   - ma      : 部屋専用の背景画像が見つからない。static/images/entrances/entrance-ma.png のみ実在
#               (入口用サムネイルで部屋本体画像ではない)。→ 方式Aへ変更(演出はコードで表現、画像同梱なし)
#   - gokuraku: 同上。static/images/entrances/entrance-gokuraku.png のみ実在(部屋本体画像なし)。
#               → 方式Aへ変更(演出はコードで表現、画像同梱なし)
#
# ROADMAPの部屋別デザイン指針表は、ma/gokurakuの「方式」列をAへ更新すること(この工程で反映)。
# ───────────────────────────────────────────────
ASSET_MAP = {
    "kanrinin": [
        "static/images/kanrinin/kanrinin-room-9x16.png",
    ],
    "namahage": [
        "static/images/namahage/namahage-room-9x16.png",
    ],
    "matsuri": [
        "static/images/matsuri/pole/06_pole_main.png",
        "static/images/matsuri/hole/10_hole_main.png",
        "static/images/matsuri/confetti/20_confetti_mix1.png",
        "static/images/matsuri/decoration/16_gohei.png",
    ],
    "fukashitsu": [
        "static/images/fukashitsu/fukashitsu-room-9x16.png",
    ],
    "typhoon-news": [
        "typhoon-news/assets/typhoon-news-bg.png",
    ],
    "daimyojin": [
        "static/images/daimyojin/daimyojin_pc.webp",
    ],
    # 方式B想定だったが部屋専用の本体画像が実在しないため、この工程の調査結果として空リストにする。
    # 該当部屋は工程3(ma)・工程4(gokuraku)で方式Aとして実装する(ROADMAP表を更新済み)。
    "ma": [],
    "gokuraku": [],
}
