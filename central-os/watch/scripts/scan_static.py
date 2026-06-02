"""
scan_static.py - KYOUKAI static asset scanner.

Classifies files under static/ for Central OS sync review. This script only
prints a report. It does not write diff-log.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parents[3]
STATIC_DIR = BASE_DIR / "static"

NO_UPDATE_EXTENSIONS = {
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".webp", ".ico", ".mp3", ".ogg", ".wav", ".mp4", ".webm",
}

IGNORE_PREFIXES = {
    "bgm/",
    "bgm\\",
}

NOTABLE_PATTERNS = ("page", "room", "template", "route")


def classify_file(path: Path) -> str:
    rel = str(path.relative_to(STATIC_DIR)).replace("\\", "/").lower()
    if any(rel.startswith(prefix.replace("\\", "/")) for prefix in IGNORE_PREFIXES):
        return "OS更新不要"

    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in NO_UPDATE_EXTENSIONS:
        if any(keyword in name for keyword in NOTABLE_PATTERNS):
            return "注意"
        return "OS更新不要"
    return "要確認"


def run_scan() -> int:
    print("=" * 60)
    print("KYOUKAI scan_static.py - static asset diff scan")
    print("=" * 60)

    if not STATIC_DIR.exists():
        print(f"[ERROR] static/ not found: {STATIC_DIR}")
        return 1

    files = sorted(path for path in STATIC_DIR.rglob("*") if path.is_file())
    categories: dict[str, list[Path]] = {"要確認": [], "注意": [], "OS更新不要": []}

    print(f"\n[static files] ({len(files)})")
    for path in files:
        rel = path.relative_to(STATIC_DIR)
        category = classify_file(path)
        categories[category].append(rel)
        print(f"  [{category}] {rel}")

    print("\n" + "-" * 60)
    print("[summary]")
    for category, items in categories.items():
        print(f"  {category}: {len(items)}")

    if categories["要確認"]:
        print("\n[review required]")
        for rel in categories["要確認"]:
            print(f"  {rel}")

    if categories["注意"]:
        print("\n[attention]")
        for rel in categories["注意"]:
            print(f"  {rel}")

    print("\nscan_static.py complete. No files were modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_scan())
