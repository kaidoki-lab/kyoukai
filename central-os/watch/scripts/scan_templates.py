"""
scan_templates.py - KYOUKAI template diff scanner.

Reports HTML templates that exist in templates/ but are not explicitly linked
from rooms.json metadata. This is a review signal, not an automatic update.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = BASE_DIR / "templates"
ROOMS_JSON = BASE_DIR / "central-os" / "rooms.json"

EXCLUDED_TEMPLATES = {
    "central.html",  # Central OS internal UI
}


def registered_templates_from_rooms(rooms_data: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for room in rooms_data.get("items", []):
        room_name = str(room.get("name") or room.get("id") or "unknown")
        memo = str(room.get("codexMemo") or "")
        for match in re.finditer(r"([A-Za-z0-9_-]+\.html)", memo):
            result[match.group(1)] = room_name
    return result


def run_scan() -> int:
    print("=" * 60)
    print("KYOUKAI scan_templates.py - template diff scan")
    print("=" * 60)

    if not TEMPLATES_DIR.exists():
        print(f"[ERROR] templates/ not found: {TEMPLATES_DIR}")
        return 1
    if not ROOMS_JSON.exists():
        print(f"[ERROR] rooms.json not found: {ROOMS_JSON}")
        return 1

    template_files = sorted(
        path.name for path in TEMPLATES_DIR.glob("*.html")
        if path.name not in EXCLUDED_TEMPLATES
    )
    rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
    registered_map = registered_templates_from_rooms(rooms_data)

    print(f"\n[templates/*.html] ({len(template_files)})")
    for name in template_files:
        print(f"  {name}")

    print(f"\n[templates referenced from rooms.json] ({len(registered_map)})")
    for template, room_name in sorted(registered_map.items()):
        print(f"  {template} <- {room_name}")

    template_set = set(template_files)
    registered_set = set(registered_map)
    unregistered = sorted(template_set - registered_set)
    missing = sorted(registered_set - template_set)

    print("\n" + "-" * 60)
    print("[diff report]")

    if not unregistered and not missing:
        print("  OK: templates/ and rooms.json references are synchronized.")
    else:
        if unregistered:
            print(f"\n  [template not referenced from rooms.json] ({len(unregistered)})")
            print("  osUpdateRequired: conditional")
            print("  targetOsFiles: central-os/rooms.json or route-lock-rules.md, if this is a room/page")
            for name in unregistered:
                print(f"    {name}")
        if missing:
            print(f"\n  [rooms.json references missing template] ({len(missing)})")
            print("  osUpdateRequired: true")
            for name in missing:
                print(f"    {name} <- {registered_map[name]}")

    print("\nscan_templates.py complete. No files were modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_scan())
