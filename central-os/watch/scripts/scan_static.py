"""
scan_static.py — KYOUKAI 静的ファイル差分検知スクリプト
PHASE 8-2

static/ 内の新規ファイルを検知し、OS への記録要否を報告する。
実行専用。自動commit・push は行わない。

使い方:
    python central-os/watch/scripts/scan_static.py
"""

import sys
from pathlib import Path

# Windows cp932対策
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

# OS更新不要として扱うファイル拡張子
NO_UPDATE_EXTENSIONS = {".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg",
                        ".webp", ".ico", ".mp3", ".ogg", ".wav", ".mp4", ".webm"}

# OS更新検討が必要な可能性があるファイルパターン
NOTABLE_PATTERNS = [
    # 新機能を示す可能性があるファイル名キーワード
    "page", "room", "template", "route",
]

def classify_file(path: Path) -> str:
    """ファイルの分類を返す。"""
    name = path.name.lower()
    suffix = path.suffix.lower()

    if suffix in NO_UPDATE_EXTENSIONS:
        # 新機能を示すキーワードを含む場合は注意
        for kw in NOTABLE_PATTERNS:
            if kw in name:
                return "注意"
        return "OS更新不要"

    return "要確認"

def run_scan():
    print("=" * 60)
    print("KYOUKAI scan_static.py — 静的ファイル差分検知")
    print("=" * 60)

    if not STATIC_DIR.exists():
        print(f"[ERROR] static/ が見つかりません: {STATIC_DIR}")
        sys.exit(1)

    all_files = sorted(STATIC_DIR.rglob("*"))
    files = [f for f in all_files if f.is_file()]

    print(f"\n[static/ ファイル一覧] ({len(files)} 件)")

    categories: dict[str, list[Path]] = {"要確認": [], "注意": [], "OS更新不要": []}
    for f in files:
        rel = f.relative_to(STATIC_DIR)
        cat = classify_file(f)
        categories[cat].append(rel)
        marker = "  [要確認]  " if cat == "要確認" else ("  [注意]    " if cat == "注意" else "  [不要]    ")
        print(f"{marker}{rel}")

    print("\n" + "─" * 60)
    print("[分類サマリー]")
    for cat, items in categories.items():
        if items:
            print(f"  {cat}: {len(items)} 件")

    if categories["要確認"]:
        print("\n  [要確認ファイル] — OS更新要否を確認してください")
        for f in categories["要確認"]:
            print(f"    {f}")

    if categories["注意"]:
        print("\n  [注意ファイル] — 新機能を示す可能性あり。確認推奨")
        for f in categories["注意"]:
            print(f"    {f}")

    print("\n─" * 60)
    print("scan_static.py 完了。")
    print("OS更新が必要と判断した場合は diff-log.json に手動で記録してください。")


if __name__ == "__main__":
    run_scan()
