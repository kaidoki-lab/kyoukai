"""
KYOUKAI Central OS — YouTube Analytics アナライザー

使い方:
  python central-os/analytics/youtube_analyzer.py

youtube_fetcher.py 実行後に使う。
youtube_shorts.json を読み込み、スコアリングして youtube_summary.json を更新する。
"""

from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ANALYTICS_DIR = BASE_DIR / "central-os" / "analytics"

SHORTS_JSON = ANALYTICS_DIR / "youtube_shorts.json"
SUMMARY_JSON = ANALYTICS_DIR / "youtube_summary.json"


def _score(video: dict) -> float:
    views = video.get("views") or 0
    avg_pct = video.get("averageViewPercentage") or 0
    likes = video.get("likes") or 0
    comments = video.get("comments") or 0
    subs = video.get("subscribersGained") or 0
    return (
        views * 0.2
        + avg_pct * 2.0
        + likes * 1.0
        + comments * 2.0
        + subs * 5.0
    )


def _title_words(title: str) -> list[str]:
    """簡易的な日本語分かち（スペース・記号で分割）。"""
    import re
    return [w for w in re.split(r"[\s　\|｜【】「」『』、。!！?？#＃]+", title) if len(w) >= 2]


def analyze() -> dict:
    if not SHORTS_JSON.exists():
        raise FileNotFoundError(f"{SHORTS_JSON} が見つかりません。先に youtube_fetcher.py を実行してください。")

    videos: list[dict] = json.loads(SHORTS_JSON.read_text(encoding="utf-8"))
    if not videos:
        return {}

    for v in videos:
        v["_score"] = _score(v)

    ranked = sorted(videos, key=lambda v: v["_score"], reverse=True)

    top_n = ranked[:5]
    bottom_n = ranked[-5:][::-1]

    # タイトル傾向分析
    top_words: dict[str, int] = {}
    bottom_words: dict[str, int] = {}

    for v in top_n:
        for w in _title_words(v.get("title") or ""):
            top_words[w] = top_words.get(w, 0) + 1

    for v in bottom_n:
        for w in _title_words(v.get("title") or ""):
            bottom_words[w] = bottom_words.get(w, 0) + 1

    top_title_words = sorted(top_words.items(), key=lambda x: -x[1])[:10]
    bottom_title_words = sorted(bottom_words.items(), key=lambda x: -x[1])[:10]

    def _video_summary(v: dict) -> dict:
        return {
            "video_id": v.get("video_id"),
            "title": v.get("title"),
            "published_at": v.get("published_at"),
            "score": round(v["_score"], 1),
            "views": v.get("views"),
            "averageViewPercentage": v.get("averageViewPercentage"),
            "likes": v.get("likes"),
            "comments": v.get("comments"),
            "subscribersGained": v.get("subscribersGained"),
        }

    # 既存サマリーを読んでfetchedAtを保持
    existing: dict = {}
    if SUMMARY_JSON.exists():
        try:
            existing = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass

    summary = {
        "fetchedAt": existing.get("fetchedAt"),
        "analyzedAt": _now_iso(),
        "videoCount": len(videos),
        "dayRange": existing.get("dayRange", 30),
        "channelId": existing.get("channelId"),
        "topVideos": [_video_summary(v) for v in top_n],
        "bottomVideos": [_video_summary(v) for v in bottom_n],
        "strongTitleWords": [w for w, _ in top_title_words],
        "weakTitleWords": [w for w, _ in bottom_title_words],
        "avgScore": round(sum(v["_score"] for v in videos) / len(videos), 1) if videos else 0,
        "allScored": [_video_summary(v) for v in ranked],
    }

    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] {SUMMARY_JSON}")
    return summary


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    result = analyze()
    print(f"[DONE] 上位: {[v['title'] for v in result.get('topVideos', [])]}")
