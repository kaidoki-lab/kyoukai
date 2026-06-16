"""
KYOUKAI Shorts Factory — YouTube メタ一括生成
finished_shorts/ の動画に対して
タイトル・説明・固定コメント・UTM付きURL を生成する。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CENTRAL_OS = ROOT.parent / "central-os"

ANALYTICS_PATH = CENTRAL_OS / "analytics" / "youtube_summary.json"
SCENARIO_PATH = ROOT / "today_scenario.txt"
FINISHED_DIR = ROOT / "finished_shorts"
OUTPUT_DIR = ROOT / "output_meta"
CONFIG_PATH = ROOT / "config.json"

BASE_URL = "https://www.void-kyoukai.net/"
UTM_SOURCE = "youtube"
UTM_MEDIUM = "shorts"

STATUS_PATH = ROOT / "status.json"

sys.path.insert(0, str(CENTRAL_OS / "lib"))
from claude_client import ask


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


def generate_meta_for_videos(videos: list[Path], scenario: str, analytics: dict) -> list[dict]:
    top_videos = analytics.get("topVideos", [])[:3]
    strong_words = analytics.get("strongTitleWords", [])

    filenames = "\n".join(f"- {v.name}" for v in videos)
    count = len(videos)

    system = """あなたはKYOUKAIというWebサイトの制作過程を記録したYouTube Shorts用のメタデータ生成AIです。
KYOUKAIは九龍城塞スタイルの実験的Webサイトで、制作者は40代の男性です。
視聴者は「変なサイトを作ってる人を見る」感覚で見ています。"""

    user = f"""以下の動画 {count} 本分のYouTubeメタデータを生成してください。

【今日の収録内容】
{scenario if scenario else "（シナリオなし）"}

【伸びた動画の傾向】
{json.dumps(top_videos, ensure_ascii=False, indent=2)}

【強いタイトルワード】
{', '.join(strong_words)}

【動画ファイル一覧】
{filenames}

各動画について以下をJSON配列で出力してください。
コードブロック（```）は使わず、JSONのみ出力してください：

[
  {{
    "filename": "ファイル名",
    "title": "タイトル（20文字以内）",
    "description": "説明文（3〜5行。最後の行はハッシュタグ #KYOUKAI #制作中 #shorts）",
    "fixed_comment": "固定コメント（1〜2文。サイトの宣伝）"
  }}
]

ルール：
- タイトルは全部違う文言にする
- 「40代」「変なサイト」「KYOUKAI」などのキーワードを活用する
- 説明文の最後にはURLを入れない（別途UTMを付けるため）
- 固定コメントは「作っているのはここです。」ではなく毎回違う文言にする
"""

    result = ask(system, user, max_tokens=2048)
    return json.loads(result)


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

    scenario = SCENARIO_PATH.read_text(encoding="utf-8") if SCENARIO_PATH.exists() else ""
    analytics = load_json(ANALYTICS_PATH, {})

    print("メタデータ生成中...")
    try:
        meta_list = generate_meta_for_videos(videos, scenario, analytics)
    except Exception as exc:
        print(f"ERROR: Claude API 呼び出し失敗: {exc}")
        sys.exit(1)

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
