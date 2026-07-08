"""Create browser-editor friendly edit packs from post candidates."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
OUTPUT_CANDIDATES = SHORTS_ROOT / "output_candidates"
OUTPUT_EDIT_PACKS = SHORTS_ROOT / "output_edit_packs"


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def find_latest_run_id() -> str:
    runs = [
        path.name
        for path in OUTPUT_CANDIDATES.iterdir()
        if path.is_dir() and (path / "post_candidates.json").exists()
    ] if OUTPUT_CANDIDATES.exists() else []
    if not runs:
        raise FileNotFoundError("post_candidates.json を含むrun_idが見つかりません。")
    return sorted(runs)[-1]


def normalize_run_id(run_id: str) -> str:
    if run_id in {"最新", "latest", "LATEST"}:
        return find_latest_run_id()
    return run_id


def load_candidates(run_id: str) -> dict[str, Any]:
    run_id = normalize_run_id(run_id)
    path = OUTPUT_CANDIDATES / run_id / "post_candidates.json"
    if not path.exists():
        raise FileNotFoundError(f"post_candidates.json が見つかりません: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["run_id"] = run_id
    return data


def copy_file(src: Path, dest: Path) -> bool:
    if not src.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def create_pack(data: dict[str, Any], room_ids: list[str]) -> dict[str, Any]:
    run_id = data["run_id"]
    candidates = {candidate["room_id"]: candidate for candidate in data.get("candidates", [])}
    missing = [room_id for room_id in room_ids if room_id not in candidates]
    if missing:
        raise ValueError(f"投稿候補に存在しないroom_id: {', '.join(missing)}")

    output_dir = OUTPUT_EDIT_PACKS / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    rooms: list[dict[str, Any]] = []

    for room_id in room_ids:
        candidate = candidates[room_id]
        room_dir = output_dir / room_id
        captures_dir = room_dir / "captures"
        room_dir.mkdir(parents=True, exist_ok=True)
        captures_dir.mkdir(parents=True, exist_ok=True)

        source_recording = resolve_path(candidate["recording"])
        recording_dest = room_dir / f"{room_id}.webm"
        recording_ok = copy_file(source_recording, recording_dest)

        capture_outputs: list[str] = []
        for capture in candidate.get("captures", []):
            source_capture = resolve_path(capture)
            capture_dest = captures_dir / source_capture.name
            if copy_file(source_capture, capture_dest):
                capture_outputs.append(display_path(capture_dest))

        status = "ready" if recording_ok and capture_outputs else "failed"
        errors = []
        if not recording_ok:
            errors.append(f"録画ファイルが見つかりません: {candidate['recording']}")
        if not capture_outputs:
            errors.append("スクリーンショットがコピーできませんでした。")

        rooms.append(
            {
                "room_id": room_id,
                "display_name": candidate["display_name"],
                "route": candidate["route"],
                "recording": display_path(recording_dest) if recording_ok else candidate["recording"],
                "captures": capture_outputs,
                "highlight": candidate.get("highlight", "未設定"),
                "recommended_text": candidate.get("recommended_text", "未設定"),
                "aspect_ratio": "9:16",
                "edit_memo": ", ".join(candidate.get("notes", [])) if candidate.get("notes") else "未設定",
                "status": status,
                "errors": errors,
            }
        )

    return {
        "run_id": run_id,
        "source_candidates": display_path(OUTPUT_CANDIDATES / run_id / "post_candidates.json"),
        "output_dir": display_path(output_dir),
        "rooms": rooms,
    }


def write_manifest(manifest: dict[str, Any]) -> tuple[Path, Path]:
    output_dir = OUTPUT_EDIT_PACKS / manifest["run_id"]
    json_path = output_dir / "edit_manifest.json"
    md_path = output_dir / "edit_manifest.md"
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 編集用素材パック",
        "",
        f"run_id: {manifest['run_id']}",
        f"source: {manifest['source_candidates']}",
        "",
    ]
    for room in manifest["rooms"]:
        lines.extend(
            [
                f"## {room['display_name']} ({room['room_id']})",
                "",
                f"- ルート: {room['route']}",
                f"- 状態: {room['status']}",
                f"- 録画: {room['recording']}",
                f"- スクショ: {room['captures'][0] if room['captures'] else 'なし'}",
                f"- 見どころ: {room['highlight']}",
                f"- 投稿文候補: {room['recommended_text']}",
                f"- 推奨アスペクト比: {room['aspect_ratio']}",
                f"- 編集メモ: {room['edit_memo']}",
                "",
            ]
        )
        if room["errors"]:
            lines.append(f"- エラー: {', '.join(room['errors'])}")
            lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def parse_rooms(value: str) -> list[str]:
    rooms = [item.strip() for item in value.split(",") if item.strip()]
    if not rooms:
        raise ValueError("--rooms には1件以上のroom_idを指定してください。")
    return rooms


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Create ShortFACTORY edit packs.")
    parser.add_argument("--run-id", default="最新", help='run_id or "最新"')
    parser.add_argument("--rooms", required=True, help="comma separated room ids")
    args = parser.parse_args()

    try:
        data = load_candidates(args.run_id)
        manifest = create_pack(data, parse_rooms(args.rooms))
        json_path, md_path = write_manifest(manifest)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    ready = sum(1 for room in manifest["rooms"] if room["status"] == "ready")
    failed = sum(1 for room in manifest["rooms"] if room["status"] == "failed")
    print(f"run_id: {manifest['run_id']}")
    print(f"rooms: {len(manifest['rooms'])}")
    print(f"ready: {ready}")
    print(f"failed: {failed}")
    print(f"edit_manifest.json: {json_path}")
    print(f"edit_manifest.md: {md_path}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
