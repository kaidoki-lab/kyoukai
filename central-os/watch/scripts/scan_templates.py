"""
scan_templates.py — KYOUKAI テンプレート差分検知スクリプト
PHASE 8-2

templates/ 内のHTMLファイルと central-os/rooms.json を比較し、
未登録テンプレートを報告する。実行専用。自動commit・push は行わない。

使い方:
    python central-os/watch/scripts/scan_templates.py
"""

import json
import sys
from pathlib import Path

# Windows cp932対策
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
ROOMS_JSON = BASE_DIR / "central-os" / "rooms.json"

# central-os/ 管理外として扱う既知テンプレート
EXCLUDED_TEMPLATES = {
    "central.html",  # /central — OS管理UI自体
}

# ─────────────────────────────────────────
# 実行
# ─────────────────────────────────────────

def run_scan():
    print("=" * 60)
    print("KYOUKAI scan_templates.py — テンプレート差分検知")
    print("=" * 60)

    # templates/ の HTML 一覧
    if not TEMPLATES_DIR.exists():
        print(f"[ERROR] templates/ が見つかりません: {TEMPLATES_DIR}")
        sys.exit(1)

    template_files = sorted(
        f.name for f in TEMPLATES_DIR.glob("*.html")
        if f.name not in EXCLUDED_TEMPLATES
    )

    print(f"\n[templates/ HTML ファイル] ({len(template_files)} 件)")
    for f in template_files:
        print(f"  {f}")

    # rooms.json 読み込み
    if not ROOMS_JSON.exists():
        print(f"\n[ERROR] rooms.json が見つかりません: {ROOMS_JSON}")
        sys.exit(1)

    rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
    rooms = rooms_data.get("items", [])

    # rooms の codexMemo からテンプレート名を推定
    # 形式: "対応テンプレートは xxx.html"
    import re
    memo_template_map: dict[str, str] = {}
    for room in rooms:
        memo = room.get("codexMemo", "")
        m = re.search(r'(\w+\.html)', memo)
        if m:
            memo_template_map[m.group(1)] = room.get("name", room.get("id", ""))

    print(f"\n[rooms.json に記録されたテンプレート] ({len(memo_template_map)} 件)")
    for tmpl, room_name in sorted(memo_template_map.items()):
        print(f"  {tmpl} → {room_name}")

    # 差分
    template_set = set(template_files)
    registered_set = set(memo_template_map.keys())

    unregistered = template_set - registered_set
    missing = registered_set - template_set

    print("\n" + "─" * 60)
    print("[差分レポート]")

    if not unregistered and not missing:
        print("  差分なし — templates/ と rooms.json は同期済みです。")
    else:
        if unregistered:
            print(f"\n  [templates/ にあるが rooms.json に未記録] ({len(unregistered)} 件)")
            print("  → 部屋の新規追加要否を確認してください。")
            for f in sorted(unregistered):
                print(f"    {f}")

        if missing:
            print(f"\n  [rooms.json に記録されているが templates/ に存在しない] ({len(missing)} 件)")
            print("  → テンプレート削除または codexMemo の記載ミスの可能性があります。")
            for f in sorted(missing):
                print(f"    {f} → {memo_template_map[f]}")

    print("\n─" * 60)
    print("scan_templates.py 完了。diff-log.json への記録は人間が手動で行ってください。")


if __name__ == "__main__":
    run_scan()
