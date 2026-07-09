"""Render all post-target KYOUKAI room shorts."""

from __future__ import annotations

import argparse
import sys

from render_short import candidate_room_ids, normalize_run_id, run_rooms


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Render all post target room shorts.")
    parser.add_argument("--run-id", default="最新", help='run_id or "最新"')
    parser.add_argument("--duration", type=int, default=15, help="max duration seconds")
    parser.add_argument("--start", type=float, default=1, help="start offset seconds")
    parser.add_argument("--no-auto-record", action="store_true", help="do not record missing rooms")
    args = parser.parse_args()

    run_id = normalize_run_id(args.run_id)
    results, (json_path, md_path) = run_rooms(
        candidate_room_ids(),
        run_id,
        duration=min(args.duration, 15),
        start=args.start,
        auto_record=not args.no_auto_record,
        flat_output=True,
    )
    success = sum(1 for item in results if item["status"] == "success")
    failed = sum(1 for item in results if item["status"] == "failed")
    skipped = sum(1 for item in results if item["status"] == "skipped")
    print(f"run_id: {run_id}")
    print(f"success: {success}")
    print(f"failed: {failed}")
    print(f"skipped: {skipped}")
    print(f"shorts_report.json: {json_path}")
    print(f"shorts_report.md: {md_path}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
