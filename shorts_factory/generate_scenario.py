"""
KYOUKAI Shorts Factory — 今日の収録シナリオ生成
Central OS の proposals + YouTube analytics を読んで
シナリオ（人間用）と操作手順JSON（マシン用）を出力する。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CENTRAL_OS = ROOT.parent / "central-os"

PROPOSALS_PATH = CENTRAL_OS / "proposals" / "proposals.json"
ANALYTICS_PATH = CENTRAL_OS / "analytics" / "youtube_summary.json"
LORE_PATH = CENTRAL_OS / "lore" / "kyoukai-world.md"
HOTSPOTS_PATH = ROOT / "kyoukai_hotspots.json"

KYOUKAI_PAGES = [
    "/", "/observation", "/signal", "/null",
    "/observer", "/archive", "/hyougi", "/external-signal", "/outside",
]

HISTORY_PATH = ROOT / "session_history.json"

# 4ルートを循環。毎回違う部屋の組み合わせを保証する
ROUTE_SETS = [
    {
        "label": "Route-A 深層",
        "pages": ["/observer", "/ma", "/null", "/archive"],
    },
    {
        "label": "Route-B 境界",
        "pages": ["/exit", "/signal", "/outside", "/hyougi"],
    },
    {
        "label": "Route-C 記録",
        "pages": ["/archive", "/hyougi", "/observation", "/observer"],
    },
    {
        "label": "Route-D 入口巡回",
        "pages": ["/", "/signal", "/null", "/exit"],
    },
]

# 日替わりトーン指定（5種循環）
TONE_ROTATIONS = [
    "静寂と待機 — 演出が動くのをただ見守る映像。操作は最小限。「何かが起きている」感覚を時間で作る。",
    "記録者の視点 — 感情を排して淡々と観測ログを残すような映像。派手な演出より「何かを記録している」感覚を優先する。",
    "迷子の観察者 — 初めて来た人が手探りで動く感覚。クリックして反応を確かめる、戻る、また進む。",
    "接続確認 — システム点検のような雰囲気。ページとホットスポットを順番に確かめていく淡々とした映像。",
    "侵食 — 静かに始まり、後半にかけて画面の異常感が増す構成。演出の変化が映えるページを選ぶ。",
]

sys.path.insert(0, str(CENTRAL_OS / "lib"))
from claude_client import ask


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def now_jst() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return data.get("sessions", [])
    except Exception:
        return []


def save_history(pages_visited: list[str], theme: str) -> None:
    sessions = load_history()
    sessions.append({
        "date": now_jst().strftime("%Y-%m-%d"),
        "pages": pages_visited,
        "theme": theme,
    })
    HISTORY_PATH.write_text(
        json.dumps({"sessions": sessions[-30:]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def pick_today_route() -> tuple[str, list[str], str]:
    """最近使ったルートを避けて今日のルートを選ぶ。ラベル・推奨ページ・トーンを返す。"""
    sessions = load_history()
    recent_labels = [s.get("route_label") for s in sessions[-4:]]

    # 最後に使ったルートを除外して選択
    for route in ROUTE_SETS:
        if route["label"] not in recent_labels:
            break
    else:
        route = ROUTE_SETS[len(sessions) % len(ROUTE_SETS)]

    tone = TONE_ROTATIONS[len(sessions) % len(TONE_ROTATIONS)]
    return route["label"], route["pages"], tone


def save_session(route_label: str, pages_visited: list[str], theme: str) -> None:
    sessions = load_history()
    sessions.append({
        "date": now_jst().strftime("%Y-%m-%d"),
        "route_label": route_label,
        "pages": pages_visited,
        "theme": theme,
    })
    HISTORY_PATH.write_text(
        json.dumps({"sessions": sessions[-30:]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_recent_pages(n: int = 2) -> list[str]:
    """直近n回のセッションで使われたページ一覧を返す。"""
    sessions = load_history()[-n:]
    recent: list[str] = []
    for s in sessions:
        for p in s.get("pages", []):
            if p not in recent:
                recent.append(p)
    return recent


def make_session_dir() -> Path:
    date_str = now_jst().strftime("%Y-%m-%d")
    session_dir = ROOT / "sessions" / date_str
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def build_scenario_prompt(
    proposals, analytics, lore: str,
    route_label: str = "", required_pages: list[str] | None = None,
    tone: str = "", recent_pages: list[str] | None = None,
) -> tuple[str, str]:
    items = proposals.get("items", []) if isinstance(proposals, dict) else proposals
    pending = [p for p in items if p.get("status") in ("提案", "保留")][:5]

    top_videos = analytics.get("topVideos", [])[:5]
    strong_words = analytics.get("strongTitleWords", [])

    today = now_jst().strftime("%Y-%m-%d (%A)")

    hotspots = load_json(HOTSPOTS_PATH, {})
    pages_summary = {
        path: {
            "room_name": info.get("room_name", ""),
            "lore": info.get("lore", ""),
            "narrative_purpose": info.get("narrative_purpose", ""),
            "has_interactions": len(info.get("interactions", [])) > 0,
        }
        for path, info in hotspots.get("pages", {}).items()
    }

    system = f"""あなたはKYOUKAIというWebサイトのYouTube Shorts収録ディレクターです。
KYOUKAIの核心テーマ：
{lore[:800]}

ルール：
- 出力は必ず日本語
- ブラウザで実際に見せられるページ・演出を具体的に指定する
- 視聴者が「変なサイトを見ている40代」を想像できるネタを選ぶ
- ホラー・怖い・不気味の強調は禁止。静かな異常感・違和感を優先する"""

    required_str = "、".join(required_pages) if required_pages else "（指定なし）"
    recent_str = "、".join(recent_pages) if recent_pages else "なし"
    tone_str = tone if tone else "特になし"

    user = f"""今日（{today}）の収録シナリオを作ってください。

【今日の収録指定】（必ず従うこと）
- 今日のルート: {route_label}
- 必ず訪問するページ（全シーンを通じてこれらを全部使うこと）: {required_str}
- 今日のアングル・トーン: {tone_str}
- 最近訪問済み（できるだけ避ける、やむを得ない場合のみ使用可）: {recent_str}

【未着手の企画案】
{json.dumps(pending, ensure_ascii=False, indent=2)}

【伸びた動画TOP5】
{json.dumps(top_videos, ensure_ascii=False, indent=2)}

【強いタイトルワード】
{', '.join(strong_words)}

【KYOUKAIの各部屋（世界観＋インタラクション有無）】
{json.dumps(pages_summary, ensure_ascii=False, indent=2)}

以下の形式で出力してください：

## 今日のテーマ
（一言で）

## 見せるシーン（3〜5本分）
各シーンを以下の形式で：

### シーン1: （タイトル）
- ページ: （URLパス）
- 操作: （何をするか）
- 見せ場: （どこが映える瞬間か）
- 尺: （何秒くらい）

### シーン2: ...

## タイトル案（各シーンに対応）
1.
2.
3.
"""
    return system, user


def make_default_steps(scenario_text: str) -> dict:
    """シナリオテキストからページを抽出してデフォルト手順を組む。"""
    base = "https://www.void-kyoukai.net"
    found = [p for p in KYOUKAI_PAGES if p in scenario_text]
    if not found:
        found = ["/", "/observation", "/signal"]

    clips = []
    for page in found[:5]:
        clips.append({
            "clip_title": page,
            "youtube_title": f"KYOUKAI｜{page}を探索する",
            "steps": [
                {"action": "navigate", "url": f"{base}{page}", "wait": 3},
                {"action": "pause", "seconds": 3},
                {"action": "scroll", "amount": 400, "wait": 2},
                {"action": "pause", "seconds": 4},
                {"action": "scroll", "amount": 600, "wait": 2},
                {"action": "pause", "seconds": 3},
                {"action": "scroll", "amount": -1000, "wait": 2},
                {"action": "pause", "seconds": 3},
            ],
        })
    return {"title": "KYOUKAI自動巡回", "clips": clips}


def build_steps_prompt(scenario_text: str, hotspots: dict) -> tuple[str, str]:
    system = """あなたはPlaywrightブラウザ自動操作の手順JSONを生成するAIです。
JSONのみ出力してください。コードブロック（```）は使わないこと。"""

    hotspots_text = json.dumps(hotspots.get("pages", {}), ensure_ascii=False, indent=2)

    user = f"""以下の収録シナリオを読んで、Playwrightで実行するブラウザ操作手順をJSONで出力してください。

【シナリオ】
{scenario_text}

【ベースURL】
https://www.void-kyoukai.net

【KYOUKAIの全ホットスポット情報】
各ページのインタラクティブ要素を必ず参照して、シーンに合ったホットスポット操作をstepsに組み込んでください。
{hotspots_text}

【出力形式】
{{
  "title": "今日のテーマ（一言）",
  "clips": [
    {{
      "clip_title": "シーンのタイトル",
      "youtube_title": "YouTubeタイトル案",
      "steps": [
        {{"action": "navigate", "url": "https://www.void-kyoukai.net/signal", "wait": 3}},
        {{"action": "pause", "seconds": 2}},
        {{"action": "click", "selector": ".signal-audio-hit", "wait": 1}},
        {{"action": "pause", "seconds": 3}},
        {{"action": "click", "selector": ".signal-channel-hit", "wait": 2}},
        {{"action": "pause", "seconds": 4}}
      ]
    }}
  ]
}}

actionの種類：
- navigate: urlに移動してwait秒待つ
- scroll: amountピクセルスクロールしてwait秒待つ（負の値で上スクロール）
- pause: seconds秒そのまま待つ（演出が動く時間）
- click: selectorのCSS要素をクリックしてwait秒待つ
- hover: selectorのCSS要素にカーソルを乗せてwait秒待つ
- mouse_move: x,y座標にカーソルを移動してwait秒待つ（ビューポートは393x852）
- mouse_click: x,y座標をクリックしてwait秒待つ

ルール：
- ホットスポットがあるページでは必ずそのselectorを使ったclick/hoverを含める
- 各クリップは30〜60秒程度になるよう手順を組む
- ページ到着後すぐクリックせず、pause 2〜3秒で演出を見せてからクリックする"""

    return system, user


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    # kyoukai-world.md → kyoukai_hotspots.json を自動同期
    try:
        from sync_hotspots import sync
        sync(verbose=False)
    except Exception as exc:
        print(f"WARNING: ホットスポット同期失敗: {exc}")

    print("シナリオ生成中...")

    proposals = load_json(PROPOSALS_PATH, {"items": []})
    analytics = load_json(ANALYTICS_PATH, {})
    lore = load_text(LORE_PATH)

    # 今日のルート・トーンを決定
    route_label, required_pages, tone = pick_today_route()
    recent_pages = get_recent_pages(n=2)
    print(f"今日のルート: {route_label}")
    print(f"必須ページ: {', '.join(required_pages)}")
    print(f"アングル: {tone[:30]}...")

    # Step1: シナリオテキスト生成
    system, user = build_scenario_prompt(
        proposals, analytics, lore,
        route_label=route_label,
        required_pages=required_pages,
        tone=tone,
        recent_pages=recent_pages,
    )
    try:
        scenario_text = ask(system, user, max_tokens=1500)
    except Exception as exc:
        print(f"ERROR: シナリオ生成失敗: {exc}")
        sys.exit(1)

    # Step2: 操作手順JSON生成
    print("操作手順を生成中...")
    hotspots = load_json(HOTSPOTS_PATH, {})
    sys_s, usr_s = build_steps_prompt(scenario_text, hotspots)
    browse_steps = {}
    try:
        steps_raw = ask(sys_s, usr_s, max_tokens=2000)
        # コードブロックを除去
        steps_clean = steps_raw.strip()
        if steps_clean.startswith("```"):
            steps_clean = "\n".join(steps_clean.split("\n")[1:])
        if steps_clean.endswith("```"):
            steps_clean = "\n".join(steps_clean.split("\n")[:-1])
        browse_steps = json.loads(steps_clean.strip())
    except Exception as exc:
        print(f"WARNING: 操作手順の生成失敗 ({exc})。デフォルト手順を使用します。")
        browse_steps = make_default_steps(scenario_text)

    # セッションフォルダに保存
    session_dir = make_session_dir()
    date_str = now_jst().strftime("%Y-%m-%d")

    scenario_output = f"# 収録シナリオ — {date_str}\n\n{scenario_text}\n"
    (session_dir / "scenario.txt").write_text(scenario_output, encoding="utf-8")

    if browse_steps:
        (session_dir / "browse_steps.json").write_text(
            json.dumps(browse_steps, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # 後方互換でルートにも置く
    (ROOT / "today_scenario.txt").write_text(scenario_output, encoding="utf-8")

    # セッション履歴を保存（次回のルート選択に使用）
    theme_line = next(
        (line.replace("## 今日のテーマ", "").strip()
         for line in scenario_text.splitlines()
         if "今日のテーマ" in line),
        route_label,
    )
    # browse_steps から実際に使ったページを抽出
    used_pages: list[str] = []
    for clip in browse_steps.get("clips", []):
        for step in clip.get("steps", []):
            url = step.get("url", "")
            if url:
                path = "/" + url.split("void-kyoukai.net/", 1)[-1].split("?")[0].lstrip("/")
                if path not in used_pages:
                    used_pages.append(path)
    save_session(route_label, used_pages or required_pages, theme_line)

    print("\n" + "=" * 50)
    print(scenario_output)
    print("=" * 50)
    print(f"\nセッションフォルダ: {session_dir}")
    print(f"  scenario.txt     — 編集時の参考")
    if browse_steps:
        clip_count = len(browse_steps.get("clips", []))
        print(f"  browse_steps.json — {clip_count}クリップ分の操作手順")


if __name__ == "__main__":
    main()
