"""Render a minimal vertical short from an edit pack recording."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
OUTPUT_EDIT_PACKS = SHORTS_ROOT / "output_edit_packs"
OUTPUT_SHORTS = SHORTS_ROOT / "output_shorts"
FFMPEG = SHORTS_ROOT / "tools" / "ffmpeg" / "ffmpeg-8.1.1-essentials_build" / "bin" / "ffmpeg.exe"
FONTS = [
    Path("C:/Windows/Fonts/YuGothM.ttc"),
    Path("C:/Windows/Fonts/YuGothB.ttc"),
    Path("C:/Windows/Fonts/meiryo.ttc"),
    Path("C:/Windows/Fonts/msgothic.ttc"),
]


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
        for path in OUTPUT_EDIT_PACKS.iterdir()
        if path.is_dir() and (path / "edit_manifest.json").exists()
    ] if OUTPUT_EDIT_PACKS.exists() else []
    if not runs:
        raise FileNotFoundError("edit_manifest.json を含むrun_idが見つかりません。")
    return sorted(runs)[-1]


def normalize_run_id(run_id: str) -> str:
    if run_id in {"最新", "latest", "LATEST"}:
        return find_latest_run_id()
    return run_id


def load_manifest(run_id: str) -> dict[str, Any]:
    run_id = normalize_run_id(run_id)
    path = OUTPUT_EDIT_PACKS / run_id / "edit_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"edit_manifest.json が見つかりません: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["run_id"] = run_id
    return data


def find_room(manifest: dict[str, Any], room_id: str) -> dict[str, Any]:
    for room in manifest.get("rooms", []):
        if room.get("room_id") == room_id:
            return room
    raise ValueError(f"edit_manifest に存在しないroom_id: {room_id}")


def choose_font() -> Path:
    for font in FONTS:
        if font.exists():
            return font
    raise FileNotFoundError("日本語テロップ用フォントが見つかりません。")


def ffmpeg_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("\n", " ")
    )


def render_short(manifest: dict[str, Any], room_id: str, duration: int, start: float) -> dict[str, Any]:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"ffmpeg が見つかりません: {FFMPEG}")

    room = find_room(manifest, room_id)
    if room.get("status") != "ready":
        raise ValueError(f"素材パックがreadyではありません: {room_id} status={room.get('status')}")

    source = resolve_path(room["recording"])
    if not source.exists():
        raise FileNotFoundError(f"録画ファイルが見つかりません: {source}")

    output_dir = OUTPUT_SHORTS / manifest["run_id"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{room_id}.webm"
    log_path = output_dir / f"{room_id}.log"
    font = choose_font()
    text = ffmpeg_text(room.get("recommended_text") or "未設定")
    fontfile = str(font).replace("\\", "/").replace(":", "\\:")

    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "format=yuv420p,"
        f"drawtext=fontfile='{fontfile}':text='{text}':"
        "fontsize=54:fontcolor=white:borderw=4:bordercolor=black:"
        "box=1:boxcolor=black@0.45:boxborderw=28:"
        "x=(w-text_w)/2:y=h-280"
    )
    command = [
        str(FFMPEG),
        "-y",
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-i",
        str(source),
        "-an",
        "-vf",
        video_filter,
        "-c:v",
        "libvpx-vp9",
        "-b:v",
        "2M",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log_path.write_text(
        "COMMAND:\n"
        + " ".join(command)
        + "\n\nSTDOUT:\n"
        + completed.stdout
        + "\n\nSTDERR:\n"
        + completed.stderr,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg failed. log={log_path}")
    if not output.exists() or output.stat().st_size < 10_000:
        raise RuntimeError(f"出力動画が小さすぎます: {output}")

    return {
        "run_id": manifest["run_id"],
        "room_id": room_id,
        "source": display_path(source),
        "output": display_path(output),
        "log": display_path(log_path),
        "duration_sec": duration,
        "start_sec": start,
        "text": room.get("recommended_text", "未設定"),
    }


def write_render_report(result: dict[str, Any]) -> Path:
    output_dir = OUTPUT_SHORTS / result["run_id"]
    report_path = output_dir / f"{result['room_id']}_render_report.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Render a minimal ShortFACTORY short.")
    parser.add_argument("--run-id", default="最新", help='run_id or "最新"')
    parser.add_argument("--room", required=True, help="room_id")
    parser.add_argument("--duration", type=int, default=10, help="duration seconds")
    parser.add_argument("--start", type=float, default=0, help="start offset seconds")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.run_id)
        result = render_short(manifest, args.room, args.duration, args.start)
        report = write_render_report(result)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"run_id: {result['run_id']}")
    print(f"room_id: {result['room_id']}")
    print(f"output: {result['output']}")
    print(f"log: {result['log']}")
    print(f"render_report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
