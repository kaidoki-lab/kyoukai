#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KYOUKAI OBSパック 旧デザインとのピクセル差分検証スクリプト

指定した部屋(複数可)のwaiting/brb/lower_thirdについて、
現在の生成物のスクリーンショットと、指定コミット(既定: HEAD~1)時点での
生成物のスクリーンショットを比較し、ピクセル差分の有無を出力する。

使い方:
  python diff_check.py observation archive hyougi exit
  python diff_check.py observation --commit b7ca038

旧コミット側は、そのコミット時点の room_specs / legacy_templates / pack_base /
asset_extract 一式を一時ディレクトリにチェックアウトし、そこで generate_packs.py 相当を
実行して waiting.html / brb.html / lower_third.html を再現してから撮影する。
(コミットにzip済み生成物が含まれない場合があるため、ソースからの再生成で比較する)
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops

BOOTH_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BOOTH_DIR.parent
ALL_PACKS_DIR = BOOTH_DIR / "all-packs"
DIFF_OUT_DIR = BOOTH_DIR / "diff_check_out"

VIEWPORT = {"width": 1920, "height": 1080}
WAIT_MS = 3000

TARGETS = [
    ("01_waiting", "waiting.html", "waiting"),
    ("02_brb", "brb.html", "brb"),
    ("03_lower-third", "lower_third.html", "lower_third"),
]


def room_name_for_id(room_id: str) -> str:
    """room_specs から room_id -> name を引く(現行コード側の定義を使う)"""
    sys.path.insert(0, str(BOOTH_DIR))
    from room_specs import load_all_specs  # noqa: E402
    for spec in load_all_specs():
        if spec["id"] == room_id:
            return spec["name"]
    raise ValueError(f"room_id not found: {room_id}")


def checkout_old_booth(commit: str, tmp_dir: Path) -> Path:
    """指定コミット時点の booth/ 一式をtmp_dirへ export する"""
    dest = tmp_dir / "booth_old"
    dest.mkdir(parents=True, exist_ok=True)

    # git archive(zip形式)で booth/ ディレクトリだけを取り出す
    # (tar形式はWindows上で日本語ファイル名を含むと展開エラーになるためzipを使う)
    proc = subprocess.run(
        ["git", "archive", "--format=zip", commit, "booth"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git archive failed: {proc.stderr.decode('utf-8', errors='replace')}")

    zip_path = tmp_dir / "old_booth.zip"
    zip_path.write_bytes(proc.stdout)

    extract_dir = tmp_dir / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)

    old_booth_src = extract_dir / "booth"
    if not old_booth_src.exists():
        raise RuntimeError(f"commit {commit} に booth/ が見つかりません")

    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(old_booth_src, dest)
    return dest


def generate_old_pack(old_booth_dir: Path, room_id: str, out_dir: Path):
    """旧コミットのroom_spec/legacy_templatesを使いwaiting/brb/lower_thirdを生成する"""
    script = f'''
import sys
sys.path.insert(0, r"{old_booth_dir}")
from room_specs import load_all_specs
specs = load_all_specs()
spec = next(s for s in specs if s["id"] == "{room_id}")
import os
os.makedirs(r"{out_dir / '01_waiting'}", exist_ok=True)
os.makedirs(r"{out_dir / '02_brb'}", exist_ok=True)
os.makedirs(r"{out_dir / '03_lower-third'}", exist_ok=True)
with open(r"{out_dir / '01_waiting' / 'waiting.html'}", "w", encoding="utf-8") as f:
    f.write(spec["waiting_html"](spec))
with open(r"{out_dir / '02_brb' / 'brb.html'}", "w", encoding="utf-8") as f:
    f.write(spec["brb_html"](spec))
with open(r"{out_dir / '03_lower-third' / 'lower_third.html'}", "w", encoding="utf-8") as f:
    f.write(spec["lower_third_html"](spec))
'''
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"旧パック生成失敗 ({room_id}): {proc.stderr}")


def shoot(page, html_path: Path, out_png: Path, is_lower_third: bool):
    url = html_path.as_uri()
    if is_lower_third:
        url += "?name=サンプル&title=配信者"
    page.goto(url)
    page.wait_for_timeout(WAIT_MS)
    page.screenshot(path=str(out_png))


def images_differ(path_a: Path, path_b: Path) -> bool:
    img_a = Image.open(path_a).convert("RGB")
    img_b = Image.open(path_b).convert("RGB")
    if img_a.size != img_b.size:
        return True
    diff = ImageChops.difference(img_a, img_b)
    bbox = diff.getbbox()
    return bbox is not None


def main():
    parser = argparse.ArgumentParser(description="旧デザインとのピクセル差分検証")
    parser.add_argument("room_ids", nargs="+", help="検証対象の部屋ID(例: observation archive hyougi exit)")
    parser.add_argument("--commit", default="HEAD~1", help="比較対象のコミット(既定: HEAD~1)")
    args = parser.parse_args()

    tmp_dir = Path(tempfile.mkdtemp(prefix="kyoukai_diff_"))
    DIFF_OUT_DIR.mkdir(exist_ok=True)

    try:
        old_booth_dir = checkout_old_booth(args.commit, tmp_dir)

        results = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=VIEWPORT)

            for room_id in args.room_ids:
                room_name = room_name_for_id(room_id)
                new_pack_dir = ALL_PACKS_DIR / f"{room_name}_OBS素材パック"
                old_pack_dir = tmp_dir / f"old_{room_id}"
                generate_old_pack(old_booth_dir, room_id, old_pack_dir)

                for sub, fname, kind in TARGETS:
                    new_html = new_pack_dir / sub / fname
                    old_html = old_pack_dir / sub / fname

                    new_png = DIFF_OUT_DIR / f"{room_id}_{kind}_new.png"
                    old_png = DIFF_OUT_DIR / f"{room_id}_{kind}_old.png"

                    is_lt = kind == "lower_third"
                    shoot(page, new_html, new_png, is_lt)
                    shoot(page, old_html, old_png, is_lt)

                    differs = images_differ(old_png, new_png)
                    results[f"{room_id}/{kind}"] = differs
                    status = "DIFF" if differs else "SAME"
                    print(f"  {status} {room_id}/{kind}")

            browser.close()

        print("")
        total = len(results)
        diff_count = sum(1 for v in results.values() if v)
        print(f"差分あり: {diff_count}/{total}")

        if diff_count != total:
            print("差分がないファイルがあります(旧版と同一の可能性)。")
            return 1
        return 0

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
