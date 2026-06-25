"""
KYOUKAI Shorts Factory — YouTube メタ一括生成
finished_shorts/ の動画に対して
タイトル・説明・固定コメント・UTM付きURL を生成する。
AIは使わず、固定テンプレートからランダム選択する。
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FINISHED_DIR = ROOT / "finished_shorts"
OUTPUT_DIR = ROOT / "output_meta"
CONFIG_PATH = ROOT / "config.json"

BASE_URL = "https://www.void-kyoukai.net/"
UTM_SOURCE = "youtube"
UTM_MEDIUM = "shorts"

STATUS_PATH = ROOT / "status.json"

TITLES = [
    "この世界、生成中につきご容赦ください",
    "AIに変なサイト作らせてる",
    "今日も変なサイトをいじってる",
    "この世界、まだ途中です",
    "また変なページを調整してる",
    "完成してないけど増えてます",
    "KYOUKAI、生成中",
    "変なサイト作ってる途中です",
]

FIXED_COMMENTS = [
    "作っているのはここです。",
    "この世界、まだ増え続けています。",
    "気になったら覗いてみてください。",
    "途中ですがリンクはここです。",
]


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def now_jst() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))


def next_devlog_id(status) -> tuple[str, int]:
    number = int(status.get("next_devlog_number", 1))
    return f"devlog_{number:03d}", number


def build_utm(devlog_id: str) -> str:
    config = load_json(CONFIG_PATH, {})
    site = config.get("site", {})
    base = str(site.get("base_url", BASE_URL)).rstrip("/")
    src = site.get("utm_source", UTM_SOURCE)
    med = site.get("utm_medium", UTM_MEDIUM)
    return f"{base}/?utm_source={src}&utm_medium={med}&utm_campaign={devlog_id}"


def generate_meta_for_videos(videos: list[Path]) -> list[dict]:
    # タイトル・固定コメントは動画間で被らないよう順序をシャッフルしてから配る
    titles = random.sample(TITLES, k=min(len(TITLES), len(videos)))
    while len(titles) < len(videos):
        titles += random.sample(TITLES, k=min(len(TITLES), len(videos) - len(titles)))

    comments = random.sample(FIXED_COMMENTS, k=min(len(FIXED_COMMENTS), len(videos)))
    while len(comments) < len(videos):
        comments += random.sample(FIXED_COMMENTS, k=min(len(FIXED_COMMENTS), len(videos) - len(comments)))

    return [
        {
            "title": titles[i],
            "description": "この世界を少しずつ増やしています。\n\nまだ途中です。\n\n#KYOUKAI\n#制作中\n#shorts",
            "fixed_comment": comments[i],
        }
        for i in range(len(videos))
    ]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    FINISHED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    video_exts = {".mp4", ".mov", ".mkv", ".webm"}
    videos = sorted(
        [p for p in FINISHED_DIR.iterdir() if p.is_file() and p.suffix.lower() in video_exts]
    )

    if not videos:
        print(f"動画が見つかりません: {FINISHED_DIR}")
        print("finished_shorts/ に完成した動画を入れてから実行してください。")
        sys.exit(0)

    print(f"{len(videos)} 本の動画を検出しました。")

    meta_list = generate_meta_for_videos(videos)

    status = load_json(STATUS_PATH, {"next_devlog_number": 1})

    date_str = now_jst().strftime("%Y%m%d")
    upload_lines = [f"# YouTube投稿メタ — {date_str}\n"]

    for i, (video, meta) in enumerate(zip(videos, meta_list), 1):
        devlog_id, number = next_devlog_id(status)
        utm_url = build_utm(devlog_id)

        txt_content = f"""タイトル：
{meta['title']}

説明：
{meta['description']}

{utm_url}

固定コメント：
{meta['fixed_comment']}

{utm_url}
"""
        txt_path = OUTPUT_DIR / f"{devlog_id}.txt"
        txt_path.write_text(txt_content, encoding="utf-8")

        upload_lines.append(f"## {i}. {devlog_id} — {video.name}")
        upload_lines.append(txt_content)
        upload_lines.append("---\n")

        status["next_devlog_number"] = number + 1

    # status 更新
    STATUS_PATH.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # まとめファイル出力
    summary_path = OUTPUT_DIR / f"youtube_upload_{date_str}.txt"
    summary_path.write_text("\n".join(upload_lines), encoding="utf-8")

    print(f"\n完了: {len(meta_list)} 本分のメタを生成しました。")
    print(f"まとめファイル: {summary_path}")
    print(f"個別ファイル: {OUTPUT_DIR}/devlog_XXX.txt")


if __name__ == "__main__":
    main()
