"""
scan_sync.py - KYOUKAI Central OS integrated sync scan.

Runs route, template, and static checks in one report. With --write-log it
appends a pending diff-log entry, unless the latest entry already has the same
summary for the same day.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parents[3]
MAIN_PY = BASE_DIR / "main.py"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
ROOMS_JSON = BASE_DIR / "central-os" / "rooms.json"
DIFF_LOG_FILE = BASE_DIR / "central-os" / "watch" / "diff-log.json"

TECHNICAL_ROUTES = {"/index.html", "/ws"}
EXCLUDED_TEMPLATES = {"central.html"}


def extract_impl_routes(source: str) -> list[str]:
    routes: set[str] = set()
    page_map = re.search(r"_PAGE_MAP\s*:\s*dict\[.*?\]\s*=\s*\{(.*?)\n\s*\}", source, re.S)
    if page_map:
        routes.update(match.group(1) for match in re.finditer(r'"(/[^"]*?)"\s*:', page_map.group(1)))
    routes.update(match.group(1) for match in re.finditer(r'@app\.get\(\s*"(/[^"]*?)"', source))
    return sorted(route for route in routes if not route.startswith("/api/") and route not in TECHNICAL_ROUTES)


def extract_os_routes(rooms_data: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for room in rooms_data.get("items", []):
        result[str(room.get("name") or room.get("id") or "?")] = str(room.get("route") or "未確定")
    return result


def registered_templates_from_rooms(rooms_data: dict) -> set[str]:
    result: set[str] = set()
    for room in rooms_data.get("items", []):
        memo = str(room.get("codexMemo") or "")
        result.update(match.group(1) for match in re.finditer(r"([A-Za-z0-9_-]+\.html)", memo))
    return result


def notable_static_files() -> list[str]:
    if not STATIC_DIR.exists():
        return []
    result: list[str] = []
    for path in STATIC_DIR.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(STATIC_DIR))
        lower = rel.replace("\\", "/").lower()
        if lower.startswith("bgm/"):
            continue
        if any(keyword in path.name.lower() for keyword in ("page", "room", "template", "route")):
            result.append(rel)
    return sorted(result)


def run_scan(write_log: bool = False) -> int:
    print("=" * 60)
    print("KYOUKAI scan_sync.py - integrated sync scan")
    print("=" * 60)
    print(f"scan date: {date.today().isoformat()}")

    issues: list[str] = []

    print("\n[1/3] route diff check")
    if not MAIN_PY.exists() or not ROOMS_JSON.exists():
        msg = "main.py or rooms.json not found"
        print(f"  [ERROR] {msg}")
        issues.append(msg)
    else:
        source = MAIN_PY.read_text(encoding="utf-8")
        rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
        impl_routes = set(extract_impl_routes(source))
        os_routes = {route for route in extract_os_routes(rooms_data).values() if route != "未確定"}
        not_in_os = sorted(impl_routes - os_routes)
        not_in_impl = sorted(os_routes - impl_routes)
        if not not_in_os and not not_in_impl:
            print("  OK: route diff none")
        else:
            if not_in_os:
                msg = f"main.py route not reflected in rooms.json: {not_in_os}"
                print(f"  WARN: {msg}")
                issues.append(msg)
            if not_in_impl:
                msg = f"rooms.json route not implemented in main.py: {not_in_impl}"
                print(f"  WARN: {msg}")
                issues.append(msg)

    print("\n[2/3] template diff check")
    if not TEMPLATES_DIR.exists() or not ROOMS_JSON.exists():
        msg = "templates/ or rooms.json not found"
        print(f"  [ERROR] {msg}")
        issues.append(msg)
    else:
        rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
        template_files = {path.name for path in TEMPLATES_DIR.glob("*.html")} - EXCLUDED_TEMPLATES
        registered = registered_templates_from_rooms(rooms_data)
        unregistered = sorted(template_files - registered)
        if unregistered:
            msg = f"template not referenced from rooms.json: {unregistered}"
            print(f"  WARN: {msg}")
            issues.append(msg)
        else:
            print("  OK: template diff none")

    print("\n[3/3] static attention check")
    static_notable = notable_static_files()
    if static_notable:
        print(f"  INFO: attention files: {static_notable}")
    else:
        print("  OK: attention files none")

    print("\n" + "-" * 60)
    if issues:
        print(f"[RESULT] {len(issues)} sync issue groups found.")
        print("         Review update-decision-rules.md before editing Central OS.")
    else:
        print("[RESULT] Central OS appears synchronized.")

    if write_log and issues:
        append_diff_log(issues)

    print("\nNo commit or push was performed.")
    return 0


def append_diff_log(issues: list[str]) -> None:
    if not DIFF_LOG_FILE.exists():
        print("\n[WARN] diff-log.json not found. Skipped write.")
        return

    data = json.loads(DIFF_LOG_FILE.read_text(encoding="utf-8"))
    items = data.setdefault("items", [])
    summary = " / ".join(issues[:3]) + (" ..." if len(issues) > 3 else "")
    today = date.today().isoformat()

    if items:
        latest = items[-1]
        if latest.get("date") == today and latest.get("summary") == summary:
            print(f"\n[INFO] diff-log.json already contains the latest same-day scan: {latest.get('id')}")
            return

    new_id = f"diff_{date.today().strftime('%Y%m%d')}_{len(items) + 1:02d}"
    items.append({
        "id": new_id,
        "date": today,
        "targetId": "scan_sync",
        "targetPath": "multiple",
        "changeType": "sync_scan",
        "summary": summary,
        "osUpdateRequired": True,
        "syncStatus": "pending",
        "targetOsFiles": [],
        "detectedBy": "scan_sync",
        "osUpdated": False,
        "updatedFiles": [],
        "memo": "Generated by scan_sync.py. Human review is required before use.",
    })
    DIFF_LOG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n[INFO] diff-log.json appended: {new_id}")


if __name__ == "__main__":
    raise SystemExit(run_scan(write_log="--write-log" in sys.argv))
