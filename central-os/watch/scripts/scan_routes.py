"""
scan_routes.py — KYOUKAI route 差分検知スクリプト
PHASE 8-2

main.py の PAGE_MAP・@app.get() と central-os/rooms.json を比較し、
同期ズレを報告する。実行専用。自動commit・push は行わない。

使い方:
    python central-os/watch/scripts/scan_routes.py
"""

import json
import re
import sys
from pathlib import Path

# Windows cp932対策: stdout を UTF-8 に強制
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MAIN_PY = BASE_DIR / "main.py"
ROOMS_JSON = BASE_DIR / "central-os" / "rooms.json"

# ─────────────────────────────────────────
# main.py からルート抽出
# ─────────────────────────────────────────

def extract_page_map_routes(source: str) -> list[str]:
    """_PAGE_MAP / PAGE_MAP 辞書のキーを抽出する。"""
    routes = []
    # "key": ... 形式のキーを探す（辞書リテラル）
    pattern = re.compile(r'"(\/[^"]*?)"\s*:')
    for m in pattern.finditer(source):
        route = m.group(1)
        if route not in routes:
            routes.append(route)
    return routes

def extract_app_get_routes(source: str) -> list[str]:
    """@app.get("...") デコレータのルートを抽出する。response_class等の追加引数も許容。"""
    routes = []
    # "(...)" に限定せず、最初の文字列引数だけを取得
    pattern = re.compile(r'@app\.get\(\s*"(/[^"]*?)"')
    for m in pattern.finditer(source):
        route = m.group(1)
        if route not in routes:
            routes.append(route)
    return routes

# ─────────────────────────────────────────
# rooms.json からルート抽出
# ─────────────────────────────────────────

def extract_room_routes(rooms_data: dict) -> dict[str, str]:
    """rooms.json の部屋名 → route マッピングを返す。"""
    result = {}
    for room in rooms_data.get("items", []):
        name = room.get("name", room.get("id", "unknown"))
        route = room.get("route", "未確定")
        result[name] = route
    return result

# ─────────────────────────────────────────
# 比較・レポート
# ─────────────────────────────────────────

def run_scan():
    print("=" * 60)
    print("KYOUKAI scan_routes.py — route 差分検知")
    print("=" * 60)

    # main.py 読み込み
    if not MAIN_PY.exists():
        print(f"[ERROR] main.py が見つかりません: {MAIN_PY}")
        sys.exit(1)
    source = MAIN_PY.read_text(encoding="utf-8")

    page_map_routes = extract_page_map_routes(source)
    app_get_routes = extract_app_get_routes(source)
    all_impl_routes = sorted(set(page_map_routes + app_get_routes))

    # API ルート除外（/api/* は OS 管理外）
    impl_routes = [r for r in all_impl_routes if not r.startswith("/api/")]

    print(f"\n[main.py 実装済みルート] ({len(impl_routes)} 件)")
    for r in impl_routes:
        print(f"  {r}")

    # rooms.json 読み込み
    if not ROOMS_JSON.exists():
        print(f"\n[ERROR] rooms.json が見つかりません: {ROOMS_JSON}")
        sys.exit(1)
    rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
    room_routes = extract_room_routes(rooms_data)

    confirmed_os_routes = [r for r in room_routes.values() if r != "未確定"]
    unconfirmed_rooms = [name for name, r in room_routes.items() if r == "未確定"]

    print(f"\n[rooms.json 確定ルート] ({len(confirmed_os_routes)} 件)")
    for r in confirmed_os_routes:
        print(f"  {r}")

    print(f"\n[rooms.json 未確定ルート] ({len(unconfirmed_rooms)} 件)")
    for name in unconfirmed_rooms:
        print(f"  {name}: 未確定")

    # 差分計算
    impl_set = set(impl_routes)
    os_set = set(confirmed_os_routes)

    impl_not_in_os = impl_set - os_set
    os_not_in_impl = os_set - impl_set

    print("\n" + "─" * 60)
    print("[差分レポート]")

    if not impl_not_in_os and not os_not_in_impl:
        print("  差分なし — main.py と rooms.json は同期済みです。")
    else:
        if impl_not_in_os:
            print(f"\n  [main.py にあるが rooms.json に未登録] ({len(impl_not_in_os)} 件)")
            print("  → OS更新要否を update-decision-rules.md で判断してください。")
            for r in sorted(impl_not_in_os):
                print(f"    {r}")

        if os_not_in_impl:
            print(f"\n  [rooms.json にあるが main.py に未実装] ({len(os_not_in_impl)} 件)")
            print("  → 設計確定・未実装ルートの可能性。route-lock-rules.md を確認してください。")
            for r in sorted(os_not_in_impl):
                print(f"    {r}")

    print("\n─" * 60)
    print("scan_routes.py 完了。diff-log.json への記録は人間が手動で行ってください。")
    print("自動commit・push は行いません。")


if __name__ == "__main__":
    run_scan()
