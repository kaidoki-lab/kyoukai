#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 全部屋ジェネレーター

工程1のリファクタで、部屋別テンプレートは room_specs/<部屋ID>.py に分離した。
このファイルは生成フロー(生成・zip・バンドル)のみを担う。

出力パス・zip名・フォルダ名は旧版から完全維持する(screenshot_packs / final_check の
前提を壊さないため)。
"""
import os
import zipfile
from pathlib import Path

from room_specs import load_all_specs
from legacy_templates import ROOMS  # noqa: F401  (他スクリプト・final_checkが `from generate_packs import ROOMS` で参照する互換維持)

BASE_DIR = Path(__file__).resolve().parent
BASE = str(BASE_DIR / "all-packs")


def readme_txt(spec):
    """SPECのreadme_linesを使ってREADME本文を組み立てる(旧readme_txtと同一体裁)。"""
    name = spec["name"]
    brb_bottom = spec["readme_lines"]["brb_bottom"]
    label = spec["readme_lines"]["label"]
    brb_main = spec["readme_lines"]["brb_main"]
    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {name} OBS素材パック  /  KYOUKAI
  {brb_bottom}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【同梱内容】3点

  01_waiting / waiting.html
    待機画面。{label}。
    配信前・ゲームロード中・場面転換に。

  02_brb / brb.html
    離席中画面。「{brb_main}」のメッセージ。
    離席・準備中・一時中断に。

  03_lower-third / lower_third.html
    ローワーサード（名前テロップ）。透過背景。
    他の素材の上に重ねてオーバーレイとして使用。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【OBS設定方法】

  1. OBS Studio を開く
  2. ソース → ＋ → ブラウザ を追加
  3. 「ローカルファイル」にチェックを入れる
  4. 各 .html ファイルを指定する
  5. 幅: 1920  /  高さ: 1080 に設定する

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【ローワーサードのカスタマイズ】

  lower_third.html をテキストエディタで開き、
  以下を書き換えてください。

    document.getElementById('name-el').textContent=p.get('name')||'名前';
    → '名前' をあなたの名前に変更

    document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
    → 'KYOUKAI' を肩書きや活動名に変更

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【動作環境】

  OBS Studio 29以降推奨
  インターネット接続不要 / 完全ローカル動作

【利用規約】

  個人・商用配信どちらでも使用可
  再配布・転売 禁止
  改変は個人使用の範囲で自由

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KYOUKAI ─ 境界
  https://kyoukai.vercel.app
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def generate_pack(spec):
    pack_name = f"{spec['name']}_OBS素材パック"
    pack_dir = os.path.join(BASE, pack_name)
    for sub in ['01_waiting', '02_brb', '03_lower-third']:
        os.makedirs(os.path.join(pack_dir, sub), exist_ok=True)

    with open(os.path.join(pack_dir, '01_waiting', 'waiting.html'), 'w', encoding='utf-8') as f:
        f.write(spec['waiting_html'](spec))
    with open(os.path.join(pack_dir, '02_brb', 'brb.html'), 'w', encoding='utf-8') as f:
        f.write(spec['brb_html'](spec))
    with open(os.path.join(pack_dir, '03_lower-third', 'lower_third.html'), 'w', encoding='utf-8') as f:
        f.write(spec['lower_third_html'](spec))
    with open(os.path.join(pack_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_txt(spec))

    zip_path = os.path.join(BASE, f"{spec['name']}_OBS素材パック.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(pack_dir):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                zf.write(fp, os.path.relpath(fp, BASE))

    print(f"  OK {spec['name']}")


def bundle_readme_txt(specs):
    room_lines = '\n'.join([f"    {s['name']}　　── {s['readme_lines']['brb_bottom']}" for s in specs])
    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KYOUKAI 全部屋 OBS素材パック
  境界のすべて
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【シリーズ概要】

  KYOUKAIには16の部屋がある。それぞれに待機画面・離席画面・
  名前テロップの3点セットが用意されている。
  このパックは16部屋すべてをまとめたものです。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【収録部屋 一覧】16部屋

{room_lines}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【同梱内容】各部屋フォルダに3点

  01_waiting / waiting.html
    待機画面。配信前・ゲームロード中・場面転換に。

  02_brb / brb.html
    離席中画面。離席・準備中・一時中断に。

  03_lower-third / lower_third.html
    ローワーサード（名前テロップ）。透過背景。
    他の素材の上に重ねてオーバーレイとして使用。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【OBS設定方法】

  1. OBS Studio を開く
  2. ソース → ＋ → ブラウザ を追加
  3. 「ローカルファイル」にチェックを入れる
  4. 使いたい部屋の .html ファイルを指定する
  5. 幅: 1920  /  高さ: 1080 に設定する

  配信の場面や気分に応じて部屋を切り替えて使用できます。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【ローワーサードのカスタマイズ】

  各部屋の lower_third.html をテキストエディタで開き、
  以下を書き換えてください。

    document.getElementById('name-el').textContent=p.get('name')||'名前';
    → '名前' をあなたの名前に変更

    document.getElementById('title-el').textContent=p.get('title')||'KYOUKAI';
    → 'KYOUKAI' を肩書きや活動名に変更

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【動作環境】

  OBS Studio 29以降推奨
  インターネット接続不要 / 完全ローカル動作

【利用規約】

  個人・商用配信どちらでも使用可
  再配布・転売 禁止
  改変は個人使用の範囲で自由

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【注意】

  本パックの各フォルダ・ファイル名には日本語が含まれています。
  古い解凍ソフト（Windows標準以外の一部ツール等）では、
  日本語ファイル名が文字化けする場合があります。
  文字化けする場合は、7-Zipなど文字コード対応の解凍ソフトの
  ご利用を推奨します。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KYOUKAI ─ 境界
  https://kyoukai.vercel.app
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def generate_bundle(specs):
    bundle_zip_path = os.path.join(BASE, "KYOUKAI_全部屋_OBS素材パック.zip")
    with zipfile.ZipFile(bundle_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for spec in specs:
            pack_name = f"{spec['name']}_OBS素材パック"
            pack_dir = os.path.join(BASE, pack_name)
            for dirpath, dirnames, filenames in os.walk(pack_dir):
                for fn in filenames:
                    fp = os.path.join(dirpath, fn)
                    arcname = os.path.join(pack_name, os.path.relpath(fp, pack_dir))
                    zf.write(fp, arcname)
        zf.writestr("README.txt", bundle_readme_txt(specs))

    print(f"  OK bundle -> {bundle_zip_path}")


def main():
    os.makedirs(BASE, exist_ok=True)
    print("生成開始...")
    specs = load_all_specs()
    for spec in specs:
        generate_pack(spec)
    print(f"\n完了 {len(specs)}部屋 -> {BASE}")

    print("\nバンドル生成開始...")
    generate_bundle(specs)
    print("バンドル生成完了")


if __name__ == '__main__':
    main()
