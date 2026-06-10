"""
KYOUKAI Central OS — YouTube Analytics フェッチャー

使い方:
  python central-os/analytics/youtube_fetcher.py

初回実行時にブラウザでOAuth認証が開く。
認証後は credentials/youtube_token.json に保存されるため2回目以降は不要。

必要なもの:
  credentials/youtube_client_secret.json  （Google Cloud Console からダウンロード）
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
CLIENT_SECRET_FILE = CREDENTIALS_DIR / "youtube_client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "youtube_token.json"
OUTPUT_DIR = BASE_DIR / "central-os" / "analytics"

SHORTS_JSON = OUTPUT_DIR / "youtube_shorts.json"
SHORTS_CSV = OUTPUT_DIR / "youtube_shorts.csv"
SUMMARY_JSON = OUTPUT_DIR / "youtube_summary.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

METRICS = [
    "views",
    "likes",
    "comments",
    "shares",
    "subscribersGained",
    "subscribersLost",
    "averageViewDuration",
    "averageViewPercentage",
    "estimatedMinutesWatched",
]

OPTIONAL_METRICS = [
    "impressions",
    "impressionClickThroughRate",
]


def _build_credentials():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    if not CLIENT_SECRET_FILE.exists():
        print(f"[ERROR] {CLIENT_SECRET_FILE} が見つかりません。")
        print("Google Cloud Console から OAuth2 クライアントシークレットをダウンロードして配置してください。")
        sys.exit(1)

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        print(f"[OK] トークン保存: {TOKEN_FILE}")

    return creds


def _get_channel_id(youtube) -> str:
    resp = youtube.channels().list(part="id", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("チャンネルが見つかりません")
    return items[0]["id"]


def _fetch_shorts_video_ids(youtube, channel_id: str, max_results: int = 50) -> list[str]:
    """直近の動画IDをmax_results件取得（ショート判定はduration側で行う）。"""
    video_ids = []
    page_token = None
    while len(video_ids) < max_results:
        params = dict(
            part="id",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=min(50, max_results - len(video_ids)),
        )
        if page_token:
            params["pageToken"] = page_token
        resp = youtube.search().list(**params).execute()
        for item in resp.get("items", []):
            vid = item.get("id", {}).get("videoId")
            if vid:
                video_ids.append(vid)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return video_ids


def _fetch_video_details(youtube, video_ids: list[str]) -> dict[str, dict]:
    """タイトル・公開日・duration をまとめて取得。"""
    details: dict[str, dict] = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        resp = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(chunk),
        ).execute()
        for item in resp.get("items", []):
            vid = item["id"]
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            duration = item.get("contentDetails", {}).get("duration", "")
            details[vid] = {
                "title": snip.get("title", ""),
                "published_at": snip.get("publishedAt", ""),
                "duration_iso": duration,
                "view_count_api": int(stats.get("viewCount", 0) or 0),
                "like_count_api": int(stats.get("likeCount", 0) or 0),
                "comment_count_api": int(stats.get("commentCount", 0) or 0),
            }
    return details


def _is_short(duration_iso: str) -> bool:
    """ISO 8601 durationが60秒以下ならShorts候補とみなす。"""
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_iso)
    if not m:
        return False
    h = int(m.group(1) or 0)
    mn = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h == 0 and mn == 0 and s <= 60


def _fetch_analytics(yt_analytics, channel_id: str, video_ids: list[str],
                     days: int = 30) -> dict[str, dict]:
    """Analytics API から動画別メトリクスを取得。"""
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    analytics: dict[str, dict] = {}

    # 実際に取得できるメトリクスセットを決める
    all_metrics = list(METRICS)
    optional_ok = []
    for m in OPTIONAL_METRICS:
        try:
            test = yt_analytics.reports().query(
                ids=f"channel=={channel_id}",
                startDate=str(start_date),
                endDate=str(end_date),
                metrics=m,
                dimensions="video",
                filters=f"video=={video_ids[0]}",
                maxResults=1,
            ).execute()
            optional_ok.append(m)
        except Exception:
            pass
    all_metrics += optional_ok

    # 50件ずつ取得
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        filters = "video==" + ",".join(chunk)
        try:
            resp = yt_analytics.reports().query(
                ids=f"channel=={channel_id}",
                startDate=str(start_date),
                endDate=str(end_date),
                metrics=",".join(all_metrics),
                dimensions="video",
                filters=filters,
                maxResults=200,
            ).execute()
        except Exception as exc:
            print(f"[WARN] Analytics API error: {exc}")
            continue

        headers = [col["name"] for col in resp.get("columnHeaders", [])]
        for row in resp.get("rows", []):
            vid = None
            row_data: dict = {}
            for key, val in zip(headers, row):
                if key == "video":
                    vid = val
                else:
                    row_data[key] = val
            if vid:
                analytics[vid] = row_data

    return analytics


def _safe_float(v) -> float | None:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _safe_int(v) -> int | None:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def fetch_and_save(days: int = 30, max_videos: int = 50, shorts_only: bool = True) -> list[dict]:
    """メインのフェッチ処理。結果リストを返す。"""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("[ERROR] google-api-python-client が未インストールです。")
        print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)

    creds = _build_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)

    print("[INFO] チャンネルID取得中...")
    channel_id = _get_channel_id(youtube)
    print(f"[INFO] channel_id: {channel_id}")

    print(f"[INFO] 直近{max_videos}本の動画IDを取得中...")
    video_ids = _fetch_shorts_video_ids(youtube, channel_id, max_results=max_videos)
    print(f"[INFO] {len(video_ids)}件取得")

    print("[INFO] 動画詳細を取得中...")
    details = _fetch_video_details(youtube, video_ids)

    if shorts_only:
        video_ids = [v for v in video_ids if _is_short(details.get(v, {}).get("duration_iso", ""))]
        print(f"[INFO] Shorts候補: {len(video_ids)}件")

    print(f"[INFO] Analytics API で直近{days}日のデータを取得中...")
    analytics = _fetch_analytics(yt_analytics, channel_id, video_ids, days=days)

    records = []
    for vid in video_ids:
        d = details.get(vid, {})
        a = analytics.get(vid, {})
        records.append({
            "video_id": vid,
            "title": d.get("title"),
            "published_at": d.get("published_at"),
            "duration_iso": d.get("duration_iso"),
            "views": _safe_int(a.get("views")) or d.get("view_count_api"),
            "likes": _safe_int(a.get("likes")) or d.get("like_count_api"),
            "comments": _safe_int(a.get("comments")) or d.get("comment_count_api"),
            "shares": _safe_int(a.get("shares")),
            "subscribersGained": _safe_int(a.get("subscribersGained")),
            "subscribersLost": _safe_int(a.get("subscribersLost")),
            "averageViewDuration": _safe_float(a.get("averageViewDuration")),
            "averageViewPercentage": _safe_float(a.get("averageViewPercentage")),
            "estimatedMinutesWatched": _safe_float(a.get("estimatedMinutesWatched")),
            "impressions": _safe_int(a.get("impressions")),
            "impressionClickThroughRate": _safe_float(a.get("impressionClickThroughRate")),
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON保存
    SHORTS_JSON.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] {SHORTS_JSON}")

    # CSV保存
    if records:
        fieldnames = list(records[0].keys())
        with open(SHORTS_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        print(f"[OK] {SHORTS_CSV}")

    # サマリー保存
    fetched_at = datetime.now(timezone.utc).isoformat()
    summary = {
        "fetchedAt": fetched_at,
        "videoCount": len(records),
        "dayRange": days,
        "channelId": channel_id,
    }
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] {SUMMARY_JSON}")
    print(f"[DONE] {len(records)}本取得完了")
    return records


if __name__ == "__main__":
    fetch_and_save()
