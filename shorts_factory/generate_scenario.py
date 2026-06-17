"""
KYOUKAI Shorts Factory — ブラウズステップ自動生成 v2
Claude API不使用。ルートローテーション + kyoukai_hotspots.json から動的に生成する。
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT         = Path(__file__).resolve().parent
HOTSPOTS_PATH = ROOT / "kyoukai_hotspots.json"
HISTORY_PATH  = ROOT / "session_history.json"
BASE_URL      = "https://www.void-kyoukai.net"

# ── ルートセット（前回と絶対に被らない） ─────────────────────────────────────
ROUTE_SETS = [
    {"label": "Route-A 深層",   "pages": ["/observer", "/ma", "/null", "/archive"]},
    {"label": "Route-B 境界",   "pages": ["/exit", "/signal", "/outside", "/hyougi"]},
    {"label": "Route-C 記録",   "pages": ["/archive", "/hyougi", "/observation", "/observer"]},
    {"label": "Route-D 入口巡回", "pages": ["/", "/signal", "/null", "/exit"]},
]


# ── 日時 ─────────────────────────────────────────────────────────────────────
def now_jst() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))


# ── JSON I/O ─────────────────────────────────────────────────────────────────
def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ── 履歴管理 ──────────────────────────────────────────────────────────────────
def load_history() -> list[dict]:
    return load_json(HISTORY_PATH, {}).get("sessions", [])


def save_session(route_label: str, pages: list[str], clip_count: int) -> None:
    sessions = load_history()
    sessions.append({
        "date":        now_jst().strftime("%Y-%m-%d"),
        "route_label": route_label,
        "pages":       pages,
        "clip_count":  clip_count,
    })
    HISTORY_PATH.write_text(
        json.dumps({"sessions": sessions[-30:]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── ルート選択（前回と同じラベルは絶対に選ばない） ──────────────────────────
def pick_route() -> dict:
    sessions   = load_history()
    last_label = sessions[-1].get("route_label") if sessions else None
    last_pages = set(sessions[-1].get("pages", [])) if sessions else set()

    # 前回と同じラベルを除外
    candidates = [r for r in ROUTE_SETS if r["label"] != last_label]
    if not candidates:
        candidates = list(ROUTE_SETS)

    # 前回とのページ被りが最も少ないものを優先
    candidates.sort(key=lambda r: len(set(r["pages"]) & last_pages))
    min_overlap = len(set(candidates[0]["pages"]) & last_pages)
    best = [r for r in candidates if len(set(r["pages"]) & last_pages) == min_overlap]
    return random.choice(best)


# ── スクロールパターン 6種（毎回ランダム選択） ──────────────────────────────
def _rnd(lo: float, hi: float, digits: int = 1) -> float:
    return round(random.uniform(lo, hi), digits)


def scroll_pattern_slow_reveal() -> list[dict]:
    """ゆっくり下りながら世界を見せる"""
    steps = []
    for _ in range(random.randint(2, 4)):
        steps += [
            {"action": "scroll", "amount": random.randint(200, 450), "wait": _rnd(1.5, 2.5)},
            {"action": "pause",  "seconds": _rnd(2.5, 4.5)},
        ]
    return steps


def scroll_pattern_sweep() -> list[dict]:
    """一気に底まで落とし、ゆっくり浮上する"""
    return [
        {"action": "pause",  "seconds": _rnd(1.5, 2.5)},
        {"action": "scroll", "amount": random.randint(800, 1200), "wait": _rnd(1.0, 2.0)},
        {"action": "pause",  "seconds": _rnd(2.5, 4.0)},
        {"action": "scroll", "amount": random.randint(-700, -400), "wait": _rnd(2.0, 3.0)},
        {"action": "pause",  "seconds": _rnd(1.5, 3.0)},
        {"action": "scroll", "amount": random.randint(200, 450), "wait": _rnd(1.5, 2.0)},
        {"action": "pause",  "seconds": _rnd(2.0, 3.5)},
    ]


def scroll_pattern_stutter() -> list[dict]:
    """少しずつ止まりながら進む（迷っている感覚）"""
    steps = []
    for _ in range(random.randint(3, 5)):
        steps += [
            {"action": "scroll", "amount": random.randint(80, 230), "wait": _rnd(0.8, 1.5)},
            {"action": "pause",  "seconds": _rnd(1.5, 3.5)},
        ]
    steps += [
        {"action": "scroll", "amount": random.randint(-300, -120), "wait": _rnd(1.5, 2.5)},
        {"action": "pause",  "seconds": _rnd(2.0, 3.5)},
    ]
    return steps


def scroll_pattern_deep_dive() -> list[dict]:
    """深く潜って長く滞在してから急浮上"""
    return [
        {"action": "pause",  "seconds": _rnd(2.0, 3.5)},
        {"action": "scroll", "amount": random.randint(1000, 1500), "wait": _rnd(1.5, 2.5)},
        {"action": "pause",  "seconds": _rnd(4.0, 6.5)},
        {"action": "scroll", "amount": random.randint(-1200, -700), "wait": _rnd(1.2, 2.0)},
        {"action": "pause",  "seconds": _rnd(1.5, 2.5)},
    ]


def scroll_pattern_float() -> list[dict]:
    """浮かぶように小刻みに上下する（演出が動くのを待つ）"""
    steps = []
    direction = 1
    for _ in range(random.randint(4, 6)):
        amount = random.randint(80, 200) * direction
        direction *= -1
        steps += [
            {"action": "scroll", "amount": amount, "wait": _rnd(1.5, 2.8)},
            {"action": "pause",  "seconds": _rnd(2.5, 5.0)},
        ]
    return steps


def scroll_pattern_zigzag() -> list[dict]:
    """大きく下りて戻る を繰り返す"""
    steps = []
    for _ in range(random.randint(2, 3)):
        steps += [
            {"action": "scroll", "amount": random.randint(350, 650), "wait": _rnd(1.0, 1.8)},
            {"action": "pause",  "seconds": _rnd(1.5, 3.0)},
            {"action": "scroll", "amount": random.randint(-300, -150), "wait": _rnd(1.2, 2.0)},
            {"action": "pause",  "seconds": _rnd(2.0, 3.5)},
        ]
    return steps


SCROLL_PATTERNS = {
    "slow_reveal": scroll_pattern_slow_reveal,
    "sweep":       scroll_pattern_sweep,
    "stutter":     scroll_pattern_stutter,
    "deep_dive":   scroll_pattern_deep_dive,
    "float":       scroll_pattern_float,
    "zigzag":      scroll_pattern_zigzag,
}


def pick_scroll_pattern(used: set[str]) -> tuple[str, list[dict]]:
    """セッション内で同じパターンを使いまわさないよう選択"""
    available = [k for k in SCROLL_PATTERNS if k not in used]
    if not available:
        available = list(SCROLL_PATTERNS.keys())
    name = random.choice(available)
    return name, SCROLL_PATTERNS[name]()


# ── インタラクション手順生成（必ず何かしらクリックする） ──────────────────
def build_interaction_steps(interactions: list[dict]) -> list[dict]:
    steps = []
    if not interactions:
        return steps

    # 重複セレクタを除外
    seen, valid = set(), []
    for ia in interactions:
        sel = ia.get("selector", "")
        if sel and sel not in seen:
            seen.add(sel)
            valid.append(ia)

    if not valid:
        return steps

    # 1〜3個ランダムに選択（多すぎると動画が長くなる）
    count   = min(len(valid), random.randint(1, 3))
    targets = random.sample(valid, count)

    for ia in targets:
        selector = ia.get("selector", "")
        action   = ia.get("action", "click")

        # クリック前にカーソルをふらりと動かす
        steps += [
            {
                "action": "mouse_move",
                "x": random.randint(80, 300),
                "y": random.randint(200, 680),
                "wait": _rnd(0.8, 1.5),
            },
            {"action": "pause", "seconds": _rnd(0.8, 1.8)},
        ]

        if action == "click":
            steps += [
                {"action": "hover",  "selector": selector, "wait": _rnd(0.5, 1.2)},
                {"action": "pause",  "seconds": _rnd(0.8, 1.6)},
                {"action": "click",  "selector": selector, "wait": _rnd(1.5, 2.5)},
                {"action": "pause",  "seconds": _rnd(2.5, 5.0)},
            ]
        else:
            steps += [
                {"action": "hover",  "selector": selector, "wait": _rnd(2.0, 3.5)},
                {"action": "pause",  "seconds": _rnd(2.0, 3.5)},
            ]

    return steps


# ── クリップ生成 ──────────────────────────────────────────────────────────────
def build_clip(page_path: str, page_info: dict, used_patterns: set[str]) -> tuple[dict, str]:
    room_name    = page_info.get("room_name", page_path)
    interactions = page_info.get("interactions", [])

    steps = []

    # 1. ページ移動＋着地待機
    steps += [
        {"action": "navigate", "url": f"{BASE_URL}{page_path}", "wait": 3},
        {"action": "pause",    "seconds": _rnd(1.5, 3.0)},
    ]

    # 2. スクロールパターン（動的）
    pattern_name, scroll_steps = pick_scroll_pattern(used_patterns)
    steps.extend(scroll_steps)

    # 3. インタラクション（必ず何かしら触れる）
    if interactions:
        steps.extend(build_interaction_steps(interactions))
    else:
        # ホットスポットなしでもカーソルを動かして「何かを探している」感を出す
        for _ in range(random.randint(2, 3)):
            steps += [
                {
                    "action": "mouse_move",
                    "x": random.randint(60, 320),
                    "y": random.randint(150, 750),
                    "wait": _rnd(1.2, 2.2),
                },
                {"action": "pause", "seconds": _rnd(2.0, 4.0)},
            ]

    # 4. エンディング（毎回違う締め方）
    ending = random.choice(["scroll_up", "linger", "scroll_more", "drift"])
    if ending == "scroll_up":
        steps += [
            {"action": "scroll", "amount": random.randint(-500, -250), "wait": _rnd(1.5, 2.5)},
            {"action": "pause",  "seconds": _rnd(2.0, 3.5)},
        ]
    elif ending == "linger":
        steps += [{"action": "pause", "seconds": _rnd(3.5, 6.0)}]
    elif ending == "scroll_more":
        steps += [
            {"action": "scroll", "amount": random.randint(200, 450), "wait": _rnd(1.0, 2.0)},
            {"action": "pause",  "seconds": _rnd(2.5, 4.5)},
        ]
    elif ending == "drift":
        for _ in range(2):
            steps += [
                {"action": "scroll", "amount": random.randint(-200, 300), "wait": _rnd(1.2, 2.0)},
                {"action": "pause",  "seconds": _rnd(1.5, 3.0)},
            ]

    clip = {
        "clip_title":     room_name,
        "youtube_title":  f"KYOUKAI｜{room_name}",
        "move_style":     pattern_name,
        "steps":          steps,
    }
    return clip, pattern_name


# ── セッションディレクトリ ────────────────────────────────────────────────────
def make_session_dir() -> tuple[Path, str]:
    date_str    = now_jst().strftime("%Y-%m-%d")
    session_dir = ROOT / "sessions" / date_str
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir, date_str


# ── main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    # kyoukai-world.md → kyoukai_hotspots.json を自動同期
    try:
        from sync_hotspots import sync
        sync(verbose=False)
    except Exception as exc:
        print(f"WARNING: ホットスポット同期失敗: {exc}")

    hotspots   = load_json(HOTSPOTS_PATH, {})
    pages_data = hotspots.get("pages", {})

    # ルート選択
    route       = pick_route()
    route_label = route["label"]
    route_pages = route["pages"]

    print(f"今日のルート : {route_label}")
    print(f"対象ページ   : {', '.join(route_pages)}")
    print()

    # ブラウズステップ生成
    clips, used_patterns = [], set()
    for page_path in route_pages:
        page_info = pages_data.get(page_path, {})
        clip, pattern_name = build_clip(page_path, page_info, used_patterns)
        used_patterns.add(pattern_name)
        clips.append(clip)
        ia_count = len(page_info.get("interactions", []))
        print(f"  {page_path:<16} pattern={pattern_name:<12} hotspots={ia_count}")

    browse_steps = {
        "title":       f"{route_label} — {now_jst().strftime('%Y-%m-%d')}",
        "route_label": route_label,
        "clips":       clips,
    }

    # 保存
    session_dir, date_str = make_session_dir()

    scenario_lines = [f"# {route_label}  {date_str}\n"]
    for clip in clips:
        scenario_lines.append(f"### {clip['clip_title']}  [{clip['move_style']}]")
    scenario_text = "\n".join(scenario_lines) + "\n"

    (session_dir / "scenario.txt").write_text(scenario_text, encoding="utf-8")
    (session_dir / "browse_steps.json").write_text(
        json.dumps(browse_steps, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "today_scenario.txt").write_text(scenario_text, encoding="utf-8")

    # 履歴保存
    save_session(route_label, route_pages, len(clips))

    print(f"\nセッションフォルダ : {session_dir}")
    print(f"browse_steps.json  : {len(clips)}クリップ 生成完了")
    print()
    print(scenario_text)


if __name__ == "__main__":
    main()
