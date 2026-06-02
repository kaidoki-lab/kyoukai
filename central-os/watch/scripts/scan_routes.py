"""
scan_routes.py - KYOUKAI route diff scanner.

Compares page routes implemented in main.py with confirmed routes in
central-os/rooms.json. This script only reports differences. It never commits,
pushes, or edits Central OS data.
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
MAIN_PY = BASE_DIR / "main.py"
ROOMS_JSON = BASE_DIR / "central-os" / "rooms.json"

TECHNICAL_ROUTES = {
    "/index.html",  # alias for /
    "/ws",          # websocket endpoint, not a room/page route
}


def extract_page_map_routes(source: str) -> list[str]:
    routes: list[str] = []
    page_map = re.search(r"_PAGE_MAP\s*:\s*dict\[.*?\]\s*=\s*\{(.*?)\n\s*\}", source, re.S)
    if not page_map:
        return routes
    for match in re.finditer(r'"(/[^"]*?)"\s*:', page_map.group(1)):
        route = match.group(1)
        if route not in routes:
            routes.append(route)
    return routes


def extract_app_get_routes(source: str) -> list[str]:
    routes: list[str] = []
    for match in re.finditer(r'@app\.get\(\s*"(/[^"]*?)"', source):
        route = match.group(1)
        if route not in routes:
            routes.append(route)
    return routes


def implemented_routes(source: str) -> list[str]:
    routes = set(extract_page_map_routes(source) + extract_app_get_routes(source))
    return sorted(
        route for route in routes
        if not route.startswith("/api/") and route not in TECHNICAL_ROUTES
    )


def room_routes(rooms_data: dict) -> tuple[dict[str, str], dict[str, str]]:
    confirmed: dict[str, str] = {}
    pending: dict[str, str] = {}
    for room in rooms_data.get("items", []):
        name = str(room.get("name") or room.get("id") or "unknown")
        route = str(room.get("route") or "未確定")
        if route == "未確定":
            pending[name] = route
        else:
            confirmed[name] = route
    return confirmed, pending


def run_scan() -> int:
    print("=" * 60)
    print("KYOUKAI scan_routes.py - route diff scan")
    print("=" * 60)

    if not MAIN_PY.exists():
        print(f"[ERROR] main.py not found: {MAIN_PY}")
        return 1
    if not ROOMS_JSON.exists():
        print(f"[ERROR] rooms.json not found: {ROOMS_JSON}")
        return 1

    source = MAIN_PY.read_text(encoding="utf-8")
    impl_routes = implemented_routes(source)
    rooms_data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
    confirmed, pending = room_routes(rooms_data)

    print(f"\n[main.py implemented page routes] ({len(impl_routes)})")
    for route in impl_routes:
        print(f"  {route}")

    print(f"\n[rooms.json confirmed routes] ({len(confirmed)})")
    for name, route in confirmed.items():
        print(f"  {route} <- {name}")

    print(f"\n[rooms.json pending routes] ({len(pending)})")
    for name in pending:
        print(f"  未確定 <- {name}")

    impl_set = set(impl_routes)
    os_set = set(confirmed.values())
    impl_not_in_os = sorted(impl_set - os_set)
    os_not_in_impl = sorted(os_set - impl_set)

    print("\n" + "-" * 60)
    print("[diff report]")

    if not impl_not_in_os and not os_not_in_impl:
        print("  OK: main.py and rooms.json are synchronized.")
    else:
        if impl_not_in_os:
            print(f"\n  [main.py route not reflected in rooms.json] ({len(impl_not_in_os)})")
            print("  osUpdateRequired: true")
            print("  targetOsFiles: central-os/rooms.json, central-os/connection/route-lock-rules.md")
            for route in impl_not_in_os:
                print(f"    {route}")
        if os_not_in_impl:
            print(f"\n  [rooms.json route not implemented in main.py] ({len(os_not_in_impl)})")
            print("  osUpdateRequired: true")
            print("  targetOsFiles: central-os/rooms.json, central-os/connection/route-lock-rules.md")
            for route in os_not_in_impl:
                print(f"    {route}")

    print("\nscan_routes.py complete. No files were modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_scan())
