#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 共通基盤(HTMLシェル・共通CSS部品・zip生成)

各room_specは以下のヘルパーを"使うかどうかを選ぶ"(強制しない)。
共通骨格を強制した結果が旧デザインの没個性の原因だったため、
ここに置くのは任意利用の部品のみ。
"""
import os
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# ───────────────────────────────────────────────
# HTMLシェル
# ───────────────────────────────────────────────
def html_shell(title: str, body: str, css: str = "", js: str = "", transparent: bool = False) -> str:
    """1920x1080固定・meta・共通リセットCSSを持つHTML骨格を返す。

    body/css/jsは各room_specが自由に組み立てた文字列をそのまま埋め込む。
    """
    bg = "transparent" if transparent else None
    base_css = f"""*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;overflow:hidden;font-family:'Courier New',monospace;{"background:transparent;" if transparent else ""}}}
"""
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
{base_css}
{css}
</style>
</head>
<body>
{body}
<script>
{js}
</script>
</body>
</html>'''


# ───────────────────────────────────────────────
# 選択式ヘルパー(各room_specが任意採用)
# ───────────────────────────────────────────────
def scanlines_css(opacity: float = 0.12, z_index: int = 20) -> str:
    """スキャンラインオーバーレイのCSS(クラス名 .scanlines を想定)を返す。"""
    return f""".scanlines{{position:absolute;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(to bottom,transparent 0px,transparent 3px,rgba(0,0,0,{opacity}) 3px,rgba(0,0,0,{opacity}) 4px);pointer-events:none;z-index:{z_index};}}"""


def rec_indicator_html(label: str = "REC") -> str:
    """REC点滅表示のHTML断片(対応CSSクラス .rec / .rec-dot と blink_keyframes()が必要)を返す。"""
    return f'<div class="rec"><div class="rec-dot"></div>{label}</div>'


def corner_frame_css(color: str, opacity: float = 0.5) -> str:
    """四隅コーナーフレームのCSS(クラス名 .corner / .corner--tl 等)を返す。"""
    return f""".corner{{position:absolute;width:36px;height:36px;}}
.corner--tl{{top:48px;left:48px;border-top:1px solid {color};border-left:1px solid {color};opacity:{opacity};}}
.corner--tr{{top:48px;right:48px;border-top:1px solid {color};border-right:1px solid {color};opacity:{opacity};}}
.corner--bl{{bottom:48px;left:48px;border-bottom:1px solid {color};border-left:1px solid {color};opacity:{opacity};}}
.corner--br{{bottom:48px;right:48px;border-bottom:1px solid {color};border-right:1px solid {color};opacity:{opacity};}}"""


def blink_keyframes(name: str = "blink") -> str:
    """点滅アニメーションのkeyframes定義を返す。"""
    return f"""@keyframes {name}{{0%,100%{{opacity:1}}50%{{opacity:.1}}}}"""


def bg_image_css(rel_path: str, class_name: str = "bg-image") -> str:
    """9:16画像を1920x1080に対し中央配置+左右を暗色グラデーションで埋めるCSSを返す。

    使い方: HTML側で <div class="{class_name}"></div> または background指定に利用する。
    """
    return f""".{class_name}{{position:absolute;top:0;left:0;width:1920px;height:1080px;background-color:#000;background-image:url('{rel_path}');background-repeat:no-repeat;background-position:center center;background-size:auto 1080px;z-index:1;}}
.{class_name}::before,.{class_name}::after{{content:'';position:absolute;top:0;bottom:0;width:35%;z-index:2;}}
.{class_name}-fade-left{{position:absolute;top:0;left:0;width:35%;height:100%;background:linear-gradient(to right,#000 0%,rgba(0,0,0,0) 100%);z-index:2;}}
.{class_name}-fade-right{{position:absolute;top:0;right:0;width:35%;height:100%;background:linear-gradient(to left,#000 0%,rgba(0,0,0,0) 100%);z-index:2;}}"""


# ───────────────────────────────────────────────
# 書き出し
# ───────────────────────────────────────────────
def write_pack(spec: dict, out_root, waiting_html_str: str, brb_html_str: str,
                lower_third_html_str: str, readme_txt_str: str, assets: dict = None):
    """waiting/brb/lower_third/README+assets/ をパックフォルダへ書き出す。

    spec: room SPEC dict (name等を使う)
    out_root: all-packs ディレクトリ(Path or str)
    assets: {"ファイル名": バイト列 or ソースパス} は使わない(copy_imageが直接assets/へ書く運用のため予約のみ)
    """
    out_root = Path(out_root)
    pack_name = f"{spec['name']}_OBS素材パック"
    pack_dir = out_root / pack_name
    for sub in ['01_waiting', '02_brb', '03_lower-third']:
        (pack_dir / sub).mkdir(parents=True, exist_ok=True)

    (pack_dir / '01_waiting' / 'waiting.html').write_text(waiting_html_str, encoding='utf-8')
    (pack_dir / '02_brb' / 'brb.html').write_text(brb_html_str, encoding='utf-8')
    (pack_dir / '03_lower-third' / 'lower_third.html').write_text(lower_third_html_str, encoding='utf-8')
    (pack_dir / 'README.txt').write_text(readme_txt_str, encoding='utf-8')

    return pack_dir


def make_zip(pack_dir, zip_path, arc_base=None):
    """パックフォルダをzip化する。assets/サブフォルダも含め全ファイルを再帰的に格納する。

    arc_base: zip内のアーカイブ名の基準ディレクトリ(未指定時はpack_dirの親)
    """
    pack_dir = Path(pack_dir)
    zip_path = Path(zip_path)
    base_for_arcname = Path(arc_base) if arc_base else pack_dir.parent

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(pack_dir):
            for fn in filenames:
                fp = Path(dirpath) / fn
                arcname = fp.relative_to(base_for_arcname)
                zf.write(fp, str(arcname))
    return zip_path
