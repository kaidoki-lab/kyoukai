"""
scan_sync.py — KYOUKAI 総合同期確認スクリプト
PHASE 8-2

scan_routes / scan_templates / scan_static を統合実行し、
全体の同期状態レポートを生成する。
実行専用。自動commit・push は行わない。

使い方:
    python central-os/watch/scripts/scan_sync.py
    python central-os/watch/scripts/scan_sync.py --write-log  # diff-log.json に追記

オプション:
    --write-log    差分があった場合、diff-log.json にサマリーエントリを追記する
                   （ただし人間による確認後に手動でレビュー必須）
"""

import json
import re
import sys

# Windows cp932対策
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
DIFF_LOG_FILE = BASE_DIR / "central-os" / "watch" / "diff-log.json"
MAIN_PY = BASE_DIR / "main.py"
TEMPLATES_DIR = BASE_DIR / "templates"
ROOMS_JSON = BASE_DIR / "central-os" / "rooms.json"

EXCLUDED_TEMPLATES = {"central.html"}

# ─────────────────────────────────────────
# Inline helpers (重複インポートを避けるため)
# ─────────────────────────────────────────

def extract_impl_routes(source: str) -> list[str]:
    routes = []
    for pattern in [r'"(\/[^"]*?)"\s*:', r'@app\.get\(\s*"(/[^"]*?)"']:
        for m in re.finditer(pattern, source):
            r = m.group(1)
            if r not in routes:
                routes.append(r)
    return [r for r in routes if not r.startswith("/api/")]

def extract_os_routes(rooms_data: dict) -> dict[str, str]:
    result = {}
    for room in rooms_data.get("items", []):
        name = room.get("name", room.get("id", "?"))
        result[name] = room.get("route", "未確定")
    return result

def extract_template_names(rooms_data: dict) -> set[str]:
    result = set()
    for room in rooms_data.get("items", []):
        m = re.search(r'(\w+\.html)', room.get("codexMemo", ""))
        if m:
            result.add(m.group(1))
    return result

# ─────────────────────────────────────────
# 実行
# ─────────────────────────────────────────

def run_scan(write_log: bool = False):
    print("=" * 60)
    print("KYOUKAI scan_sync.py — 総合同期確認")
    print("=" * 60)
    print(f"スキャン日: {date.today().isoformat()}")

    issues: list[str] = []

    # ── ROUTES ────────────────────────────
    print("\n[1/3] route 差分チェック")
    if not MAIN_PY.exists():
        print("  [SKIP] main.py が見つかりません")
        issues.append("main.py not found")
    else:
        source = MAIN_PY.read_text(encoding="utf-8")
        impl_routes = set(extract_impl_routes(source))

        if not ROOMS_JSON.exists():
            print("  [SKIP] rooms.json が見つかりません")
            issues.append("rooms.json not found")
        else:
            rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
            os_routes_map = extract_os_routes(rooms_data)
            confirmed_os = {r for r in os_routes_map.values() if r != "未確定"}

            not_in_os = impl_routes - confirmed_os
            not_in_impl = confirmed_os - impl_routes

            if not not_in_os and not not_in_impl:
                print("  OK — route 差分なし")
            else:
                if not_in_os:
                    msg = f"main.py にあるが rooms.json 未登録: {sorted(not_in_os)}"
                    print(f"  WARN — {msg}")
                    issues.append(msg)
                if not_in_impl:
                    msg = f"rooms.json にあるが main.py 未実装: {sorted(not_in_impl)}"
                    print(f"  WARN — {msg}")
                    issues.append(msg)

    # ── TEMPLATES ─────────────────────────
    print("\n[2/3] テンプレート差分チェック")
    if not TEMPLATES_DIR.exists():
        print("  [SKIP] templates/ が見つかりません")
    elif not ROOMS_JSON.exists():
        print("  [SKIP] rooms.json が見つかりません")
    else:
        template_files = {f.name for f in TEMPLATES_DIR.glob("*.html")} - EXCLUDED_TEMPLATES
        rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
        registered = extract_template_names(rooms_data)

        unregistered = template_files - registered
        if unregistered:
            msg = f"未登録テンプレート: {sorted(unregistered)}"
            print(f"  WARN — {msg}")
            issues.append(msg)
        else:
            print("  OK — テンプレート差分なし")

    # ── STATIC ────────────────────────────
    print("\n[3/3] 静的ファイルチェック（概略）")
    if not (BASE_DIR / "static").exists():
        print("  [SKIP] static/ が見つかりません")
    else:
        notable = [
            f.relative_to(BASE_DIR / "static")
            for f in (BASE_DIR / "static").rglob("*")
            if f.is_file() and any(kw in f.name.lower() for kw in ["page", "room", "template", "route"])
        ]
        if notable:
            msg = f"注意ファイル: {[str(f) for f in notable]}"
            print(f"  INFO — {msg}")
        else:
            print("  OK — 注意ファイルなし")

    # ── SUMMARY ───────────────────────────
    print("\n" + "─" * 60)
    if not issues:
        print("[RESULT] 差分なし — Central OS は最新状態です。")
    else:
        print(f"[RESULT] {len(issues)} 件の差分・注意事項があります。")
        print("         update-decision-rules.md で OS更新要否を判断してください。")

    # ── diff-log.json への追記（オプション）
    if write_log and issues:
        _append_diff_log(issues)

    print("\n自動commit・push は行いません。")

def _append_diff_log(issues: list[str]):
    """差分を diff-log.json に追記する（人間の確認が前提）。"""
    if not DIFF_LOG_FILE.exists():
        print("\n[WARN] diff-log.json が見つかりません。書き込みをスキップします。")
        return

    data = json.loads(DIFF_LOG_FILE.read_text(encoding="utf-8"))
    items = data.get("items", [])
    new_id = f"diff_{date.today().strftime('%Y%m%d')}_{len(items)+1:02d}"

    entry = {
        "id": new_id,
        "date": date.today().isoformat(),
        "targetId": "scan_sync",
        "targetPath": "multiple",
        "changeType": "sync_scan",
        "summary": " / ".join(issues[:3]) + (" …" if len(issues) > 3 else ""),
        "osUpdateRequired": True,
        "syncStatus": "pending",
        "targetOsFiles": [],
        "detectedBy": "scan_sync",
        "osUpdated": False,
        "updatedFiles": [],
        "memo": "scan_sync.py 自動生成エントリ。内容を人間が確認・修正してから使用すること。"
    }

    items.append(entry)
    data["items"] = items
    DIFF_LOG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n[INFO] diff-log.json に追記しました: {new_id}")
    print("       必ず内容を確認し、不要な場合は削除してください。")

if __name__ == "__main__":
    write_log = "--write-log" in sys.argv
    run_scan(write_log=write_log)
