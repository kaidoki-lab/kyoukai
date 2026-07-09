"""Render all post-target KYOUKAI room shorts."""

from __future__ import annotations

import argparse
import sys

from render_short import all_room_ids, available_bgm_paths, create_remix, normalize_run_id, post_ready_dir, run_rooms


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Render all post target room shorts.")
    parser.add_argument("--run-id", default="最新", help='run_id or "最新"')
    parser.add_argument("--duration", type=int, default=15, help="max duration seconds")
    parser.add_argument("--start", type=float, default=1, help="start offset seconds")
    parser.add_argument("--no-auto-record", action="store_true", help="do not record missing rooms")
    parser.add_argument("--with-bgm", action="store_true", help="add existing KYOUKAI BGM")
    parser.add_argument("--bgm", default="", help="optional BGM path")
    parser.add_argument("--bgm-volume", type=float, default=0.4, help="BGM volume")
    parser.add_argument("--post-target-only", action="store_true", help="render only rooms marked 投稿対象 true")
    args = parser.parse_args()

    run_id = normalize_run_id(args.run_id)
    output_dir = post_ready_dir(run_id)
    bgm_paths = available_bgm_paths(args.bgm) if args.with_bgm else []
    if args.with_bgm and not bgm_paths:
        print("ERROR: BGMファイルが見つかりません。")
        return 1
    room_ids = all_room_ids() if not args.post_target_only else [
        room_id for room_id in all_room_ids()
        if room_id not in {"city", "outside", "observer", "top-floor", "fukashitsu"}
    ]
    results, (json_path, md_path) = run_rooms(
        room_ids,
        run_id,
        duration=min(args.duration, 15),
        start=args.start,
        auto_record=not args.no_auto_record,
        flat_output=True,
        output_dir=output_dir,
        allow_non_post_target=not args.post_target_only,
        with_bgm=args.with_bgm,
        bgm_paths=bgm_paths,
        bgm_volume=args.bgm_volume,
    )
    remix = create_remix(results, output_dir=output_dir, with_bgm=args.with_bgm, bgm_paths=bgm_paths, bgm_volume=args.bgm_volume)
    success = sum(1 for item in results if item["status"] == "success")
    failed = sum(1 for item in results if item["status"] == "failed")
    skipped = sum(1 for item in results if item["status"] == "skipped")
    print(f"run_id: {run_id}")
    print(f"success: {success}")
    print(f"failed: {failed}")
    print(f"skipped: {skipped}")
    print(f"shorts_report.json: {json_path}")
    print(f"shorts_report.md: {md_path}")
    print(f"remix: {remix.get('status')} {remix.get('output_video', '')}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
