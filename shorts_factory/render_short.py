"""Render postable KYOUKAI shorts directly from room masters and recordings."""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from generate_post_candidates import load_room_info
from run_room_flow import DEFAULT_BASE_URL, make_run_id, run_room


ROOT = Path(__file__).resolve().parents[1]
SHORTS_ROOT = ROOT / "shorts_factory"
OUTPUT_REPORTS = SHORTS_ROOT / "output_reports"
OUTPUT_RECORDINGS = SHORTS_ROOT / "output_recordings"
OUTPUT_SHORTS = SHORTS_ROOT / "output_shorts"
OUTPUT_POST_READY = OUTPUT_SHORTS / "post_ready"
ROOMS_DIR = ROOT / "data" / "rooms"
FFMPEG = SHORTS_ROOT / "tools" / "ffmpeg" / "ffmpeg-8.1.1-essentials_build" / "bin" / "ffmpeg.exe"
DEFAULT_BGM_CANDIDATES = [
    ROOT / "assets" / "bgm" / "kyoukai_main.mp3",
    ROOT / "static" / "bgm" / "bgm_home.mp3",
    ROOT / "static" / "bgm" / "bgm_exit.mp3",
    ROOT / "static" / "bgm" / "bgm_null.mp3",
    ROOT / "static" / "bgm" / "bgm_observer.mp3",
]
FONTS = [
    Path("C:/Windows/Fonts/YuGothM.ttc"),
    Path("C:/Windows/Fonts/YuGothB.ttc"),
    Path("C:/Windows/Fonts/meiryo.ttc"),
    Path("C:/Windows/Fonts/msgothic.ttc"),
]
UNSET = {"", "未設定", "未記載"}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def post_ready_dir(run_id: str) -> Path:
    return OUTPUT_POST_READY / run_id


def find_latest_run_id() -> str:
    report_runs = [
        path.name
        for path in OUTPUT_REPORTS.iterdir()
        if path.is_dir() and (path / "recording_report.json").exists()
    ] if OUTPUT_REPORTS.exists() else []
    recording_runs = [
        path.name
        for path in OUTPUT_RECORDINGS.iterdir()
        if path.is_dir() and any(path.glob("*.webm"))
    ] if OUTPUT_RECORDINGS.exists() else []
    runs = sorted(set(report_runs + recording_runs))
    return runs[-1] if runs else make_run_id()


def normalize_run_id(run_id: str) -> str:
    if run_id in {"", "最新", "latest", "LATEST"}:
        return find_latest_run_id()
    return run_id


def choose_font() -> Path:
    for font in FONTS:
        if font.exists():
            return font
    raise FileNotFoundError("日本語テロップ用フォントが見つかりません。")


def ffmpeg_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("\n", " ")


def escape_filter_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def shorten(value: str, limit: int = 42) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def wrap_caption(value: str, line_length: int = 18, max_lines: int = 3) -> str:
    text = shorten(" ".join(value.split()), line_length * max_lines)
    lines = [text[index:index + line_length] for index in range(0, len(text), line_length)]
    for index in range(1, len(lines)):
        if lines[index] and lines[index][0] in "、。，．！？!?":
            lines[index - 1] += lines[index][0]
            lines[index] = lines[index][1:]
    return "\n".join(lines[:max_lines])


def report_caption(value: str) -> str:
    return value.replace("\n", " / ")


def caption_for(room_id: str, info: dict[str, Any]) -> str:
    recommended = str(info.get("recommended_text", "")).strip()
    if recommended not in UNSET:
        return wrap_caption(recommended)
    highlight = str(info.get("highlight", "")).strip()
    if highlight not in UNSET:
        return wrap_caption(highlight)
    display_name = str(info.get("display_name", room_id)).strip()
    return wrap_caption(display_name or room_id)


def candidate_room_ids() -> list[str]:
    room_ids: list[str] = []
    for path in sorted(ROOMS_DIR.glob("*.md")):
        if path.name == "_template.md":
            continue
        info = load_room_info(path.stem)
        if info.get("post_target"):
            room_ids.append(path.stem)
    return room_ids


def all_room_ids() -> list[str]:
    return sorted(path.stem for path in ROOMS_DIR.glob("*.md") if path.name != "_template.md")


def available_bgm_paths(path_text: str | None = None) -> list[Path]:
    candidates: list[Path] = []
    if path_text:
        path = Path(path_text)
        candidates.append(path if path.is_absolute() else ROOT / path)
    candidates.extend(DEFAULT_BGM_CANDIDATES)
    unique: list[Path] = []
    for candidate in candidates:
        if candidate.exists() and candidate not in unique:
            unique.append(candidate)
    return unique


def resolve_bgm_path(path_text: str | None) -> Path | None:
    paths = available_bgm_paths(path_text)
    return paths[0] if paths else None


def choose_bgm_path(bgm_paths: list[Path] | None) -> Path | None:
    if not bgm_paths:
        return None
    return random.choice(bgm_paths)


def ensure_recording(room_id: str, run_id: str, auto_record: bool = True) -> tuple[Path | None, list[str]]:
    warnings: list[str] = []
    recording = OUTPUT_RECORDINGS / run_id / f"{room_id}.webm"
    if recording.exists():
        return recording, warnings
    if not auto_record:
        return None, [f"録画ファイルが見つかりません: {display_path(recording)}"]

    base_url = os.environ.get("KYOUKAI_BASE_URL", DEFAULT_BASE_URL)
    try:
        result = run_room(room_id, run_id, base_url)
    except Exception as exc:
        return None, [f"自動録画に失敗しました: {exc}"]
    if result.get("status") not in {"success", "success_with_warnings"}:
        errors = ", ".join(result.get("errors", [])) or result.get("status", "failed")
        return None, [f"自動録画に失敗しました: {errors}"]
    recorded = Path(str(result.get("recording", "")))
    if recorded.exists():
        return recorded, list(result.get("warnings", []))
    if recording.exists():
        return recording, list(result.get("warnings", []))
    return None, ["自動録画後の録画ファイルが見つかりません。"]


def render_video(
    source: Path,
    output: Path,
    caption: str,
    duration: int,
    start: float,
    with_bgm: bool = False,
    bgm_path: Path | None = None,
    bgm_volume: float = 0.4,
) -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"ffmpeg が見つかりません: {FFMPEG}")
    font = choose_font()
    output.parent.mkdir(parents=True, exist_ok=True)
    fontfile = str(font).replace("\\", "/").replace(":", "\\:")
    caption_file = output.with_suffix(".caption.txt")
    caption_file.write_text(caption, encoding="utf-8")
    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "format=yuv420p,"
        f"drawtext=fontfile='{fontfile}':textfile='{escape_filter_path(caption_file)}':"
        "fontsize=54:fontcolor=white:borderw=4:bordercolor=black:"
        "box=1:boxcolor=black@0.45:boxborderw=28:"
        "line_spacing=12:x=(w-text_w)/2:y=h-360"
    )
    command = [
        str(FFMPEG),
        "-y",
        "-stream_loop",
        "-1",
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-i",
        str(source),
    ]
    if with_bgm:
        if bgm_path is None or not bgm_path.exists():
            raise FileNotFoundError("BGMファイルが見つかりません。")
        command.extend(["-stream_loop", "-1", "-i", str(bgm_path)])
    if with_bgm:
        command.extend(
            [
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
            ]
        )
    else:
        command.append("-an")
    command.extend(
        [
        "-vf",
        video_filter,
        ]
    )
    if with_bgm:
        command.extend(["-af", f"volume={bgm_volume}"])
    command.extend(
        [
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        ]
    )
    if with_bgm:
        command.extend(["-c:a", "aac", "-b:a", "128k", "-shortest"])
    command.append(
        str(output),
    )
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log_path = output.with_suffix(".log")
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


def render_one(
    room_id: str,
    run_id: str,
    duration: int = 15,
    start: float = 1,
    auto_record: bool = True,
    final_output: Path | None = None,
    allow_non_post_target: bool = False,
    with_bgm: bool = False,
    bgm_path: Path | None = None,
    bgm_paths: list[Path] | None = None,
    bgm_volume: float = 0.4,
) -> dict[str, Any]:
    selected_bgm = bgm_path or choose_bgm_path(bgm_paths)
    info = load_room_info(room_id)
    if not info.get("post_target") and not allow_non_post_target:
        return {
            "room_id": room_id,
            "display_name": info.get("display_name", room_id),
            "status": "skipped",
            "input_recording": "",
            "output_video": "",
            "caption": "",
            "duration_sec": 0,
            "bgm_enabled": with_bgm,
            "bgm_file": display_path(selected_bgm) if selected_bgm else "",
            "errors": [f"投稿対象外: {info.get('exclusion_reason', '未設定')}"],
            "warnings": [],
        }

    recording, warnings = ensure_recording(room_id, run_id, auto_record=auto_record)
    caption = caption_for(room_id, info)
    if recording is None:
        return {
            "room_id": room_id,
            "display_name": info.get("display_name", room_id),
            "status": "failed",
            "input_recording": "",
            "output_video": "",
            "caption": caption,
            "duration_sec": 0,
            "bgm_enabled": with_bgm,
            "bgm_file": display_path(selected_bgm) if selected_bgm else "",
            "errors": warnings,
            "warnings": [],
        }

    output = final_output or OUTPUT_SHORTS / run_id / f"{room_id}.mp4"
    try:
        render_video(
            recording,
            output,
            caption,
            duration,
            start,
            with_bgm=with_bgm,
            bgm_path=selected_bgm,
            bgm_volume=bgm_volume,
        )
    except Exception as exc:
        return {
            "room_id": room_id,
            "display_name": info.get("display_name", room_id),
            "status": "failed",
            "input_recording": display_path(recording),
            "output_video": "",
            "caption": caption,
            "duration_sec": 0,
            "bgm_enabled": with_bgm,
            "bgm_file": display_path(selected_bgm) if selected_bgm else "",
            "errors": [str(exc)],
            "warnings": warnings,
        }

    return {
        "room_id": room_id,
        "display_name": info.get("display_name", room_id),
        "status": "success",
        "input_recording": display_path(recording),
        "output_video": display_path(output),
        "caption": caption,
        "duration_sec": duration,
        "bgm_enabled": with_bgm,
        "bgm_file": display_path(selected_bgm) if selected_bgm else "",
        "errors": [],
        "warnings": warnings,
    }


def create_remix(
    results: list[dict[str, Any]],
    output_dir: Path,
    with_bgm: bool = False,
    bgm_path: Path | None = None,
    bgm_paths: list[Path] | None = None,
    bgm_volume: float = 0.4,
) -> dict[str, Any]:
    priority = ["archive", "signal", "observation", "null", "daimyojin"]
    by_room = {item["room_id"]: item for item in results if item.get("status") == "success"}
    ordered = [by_room[room_id] for room_id in priority if room_id in by_room]
    for item in results:
        if item.get("status") == "success" and item["room_id"] not in priority:
            ordered.append(item)
    selected = ordered[:12]
    if len(selected) < 2:
        return {
            "status": "skipped",
            "output_video": "",
            "errors": ["リミックスに使える成功動画が不足しています。"],
        }
    if not FFMPEG.exists():
        return {"status": "failed", "output_video": "", "errors": [f"ffmpeg が見つかりません: {FFMPEG}"]}

    tmp_dir = output_dir / "_remix_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    segment_paths: list[Path] = []
    segment_duration = 1.25
    for index, item in enumerate(selected, start=1):
        source = ROOT / item["output_video"]
        if not source.exists():
            continue
        segment = tmp_dir / f"segment_{index:02d}_{item['room_id']}.mp4"
        command = [
            str(FFMPEG),
            "-y",
            "-ss",
            str(0.5 + (index % 4) * 0.7),
            "-t",
            str(segment_duration),
            "-i",
            str(source),
            "-an",
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            str(segment),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if completed.returncode == 0 and segment.exists():
            segment_paths.append(segment)

    if len(segment_paths) < 2:
        return {"status": "failed", "output_video": "", "errors": ["リミックス用セグメント生成に失敗しました。"]}

    concat_list = tmp_dir / "concat.txt"
    concat_list.write_text(
        "\n".join(f"file '{path.as_posix()}'" for path in segment_paths),
        encoding="utf-8",
    )
    joined = tmp_dir / "joined.mp4"
    concat_command = [
        str(FFMPEG),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(joined),
    ]
    completed = subprocess.run(concat_command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0 or not joined.exists():
        return {"status": "failed", "output_video": "", "errors": ["リミックス結合に失敗しました。"]}

    output = output_dir / "kyoukai_remix_001.mp4"
    font = choose_font()
    fontfile = str(font).replace("\\", "/").replace(":", "\\:")
    remix_caption = output.with_suffix(".caption.txt")
    remix_caption.write_text("まだ開いてる\n部屋がある", encoding="utf-8")
    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "format=yuv420p,"
        f"drawtext=fontfile='{fontfile}':textfile='{escape_filter_path(remix_caption)}':"
        "fontsize=58:fontcolor=white:borderw=4:bordercolor=black:"
        "box=1:boxcolor=black@0.45:boxborderw=28:"
        "line_spacing=12:x=(w-text_w)/2:y=150"
    )
    command = [str(FFMPEG), "-y", "-i", str(joined)]
    if with_bgm:
        bgm_path = bgm_path or choose_bgm_path(bgm_paths)
        if bgm_path is None or not bgm_path.exists():
            return {"status": "failed", "output_video": "", "errors": ["BGMファイルが見つかりません。"]}
        command.extend(["-stream_loop", "-1", "-i", str(bgm_path), "-map", "0:v:0", "-map", "1:a:0"])
    else:
        command.append("-an")
    command.extend(["-vf", video_filter])
    if with_bgm:
        command.extend(["-af", f"volume={bgm_volume}"])
    command.extend(["-t", "15", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p"])
    if with_bgm:
        command.extend(["-c:a", "aac", "-b:a", "128k", "-shortest"])
    command.append(str(output))
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log_path = output.with_suffix(".log")
    log_path.write_text(completed.stdout + "\n\n" + completed.stderr, encoding="utf-8")
    if completed.returncode != 0 or not output.exists():
        return {"status": "failed", "output_video": "", "errors": [f"リミックス出力に失敗しました: {log_path}"]}
    return {
        "status": "success",
        "output_video": display_path(output),
        "source_rooms": [item["room_id"] for item in selected],
        "bgm_enabled": with_bgm,
        "bgm_file": display_path(bgm_path) if bgm_path else "",
        "errors": [],
    }


def write_shorts_report(run_id: str, results: list[dict[str, Any]], output_dir: Path | None = None) -> tuple[Path, Path]:
    output_dir = output_dir or OUTPUT_SHORTS / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().isoformat(timespec="seconds")
    report = {
        "run_id": run_id,
        "generated_at": generated_at,
        "summary": {
            "success": sum(1 for item in results if item["status"] == "success"),
            "failed": sum(1 for item in results if item["status"] == "failed"),
            "skipped": sum(1 for item in results if item["status"] == "skipped"),
        },
        "rooms": results,
    }
    json_path = output_dir / "shorts_report.json"
    md_path = output_dir / "shorts_report.md"
    flat_json_path = output_dir / "short_generation_report.json"
    flat_md_path = output_dir / "short_generation_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    flat_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Shorts生成レポート",
        "",
        f"run_id: {run_id}",
        f"generated_at: {generated_at}",
        f"成功: {report['summary']['success']}",
        f"失敗: {report['summary']['failed']}",
        f"スキップ: {report['summary']['skipped']}",
        "",
        "## 成功",
        "",
    ]
    for item in results:
        if item["status"] != "success":
            continue
        lines.extend(
            [
                f"### {item['room_id']}",
                f"- 表示名: {item['display_name']}",
                f"- 入力: {item['input_recording']}",
                f"- 出力: {item['output_video']}",
                f"- テロップ: {report_caption(item['caption'])}",
                f"- 尺: {item['duration_sec']}秒",
                f"- BGM: {'あり' if item.get('bgm_enabled') else 'なし'}",
                f"- BGMファイル: {item.get('bgm_file') or 'なし'}",
                "",
            ]
        )
    lines.extend(["## 失敗", ""])
    for item in results:
        if item["status"] != "failed":
            continue
        lines.extend(
            [
                f"### {item['room_id']}",
                f"- 表示名: {item['display_name']}",
                f"- 理由: {', '.join(item['errors']) if item['errors'] else '未設定'}",
                "",
            ]
        )
    lines.extend(["## スキップ", ""])
    for item in results:
        if item["status"] != "skipped":
            continue
        lines.extend(
            [
                f"### {item['room_id']}",
                f"- 表示名: {item['display_name']}",
                f"- 理由: {', '.join(item['errors']) if item['errors'] else '未設定'}",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    flat_md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def write_room_report(run_id: str, result: dict[str, Any], output_dir: Path | None = None) -> tuple[Path, Path]:
    output_dir = output_dir or OUTPUT_SHORTS / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    room_id = result["room_id"]
    json_path = output_dir / f"{room_id}_short_report.json"
    md_path = output_dir / f"{room_id}_short_report.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"# Short生成レポート: {room_id}",
        "",
        f"- 表示名: {result['display_name']}",
        f"- 状態: {result['status']}",
        f"- 入力: {result['input_recording'] or 'なし'}",
        f"- 出力: {result['output_video'] or 'なし'}",
        f"- テロップ: {report_caption(result['caption']) if result['caption'] else 'なし'}",
        f"- 尺: {result['duration_sec']}秒",
        f"- BGM: {'あり' if result.get('bgm_enabled') else 'なし'}",
        f"- BGMファイル: {result.get('bgm_file') or 'なし'}",
        f"- エラー: {', '.join(result['errors']) if result['errors'] else 'なし'}",
        f"- 警告: {', '.join(result['warnings']) if result['warnings'] else 'なし'}",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def run_rooms(
    room_ids: list[str],
    run_id: str,
    duration: int,
    start: float,
    auto_record: bool,
    flat_output: bool = False,
    output_dir: Path | None = None,
    allow_non_post_target: bool = False,
    with_bgm: bool = False,
    bgm_path: Path | None = None,
    bgm_paths: list[Path] | None = None,
    bgm_volume: float = 0.4,
) -> tuple[list[dict[str, Any]], tuple[Path, Path]]:
    results = []
    if flat_output:
        output_dir = output_dir or post_ready_dir(run_id)
    for room_id in room_ids:
        print(f"RENDER room={room_id}")
        final_output = output_dir / f"{room_id}_short.mp4" if flat_output and output_dir else None
        result = render_one(
            room_id,
            run_id,
            duration=duration,
            start=start,
            auto_record=auto_record,
            final_output=final_output,
            allow_non_post_target=allow_non_post_target,
            with_bgm=with_bgm,
            bgm_path=bgm_path,
            bgm_paths=bgm_paths,
            bgm_volume=bgm_volume,
        )
        print(f"  status={result['status']} output={result.get('output_video') or '-'}")
        results.append(result)
        if len(room_ids) == 1:
            write_room_report(run_id, result, output_dir=output_dir)
    report_paths = write_shorts_report(run_id, results, output_dir=output_dir)
    return results, report_paths


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Render KYOUKAI room shorts.")
    parser.add_argument("--run-id", default="最新", help='run_id or "最新"')
    parser.add_argument("--room", default="", help="room_id")
    parser.add_argument("--all", action="store_true", help="render all post target rooms")
    parser.add_argument("--duration", type=int, default=15, help="max duration seconds")
    parser.add_argument("--start", type=float, default=1, help="start offset seconds")
    parser.add_argument("--no-auto-record", action="store_true", help="do not record missing rooms")
    parser.add_argument("--with-bgm", action="store_true", help="add existing KYOUKAI BGM")
    parser.add_argument("--bgm", default="", help="optional BGM path")
    parser.add_argument("--bgm-volume", type=float, default=0.4, help="BGM volume")
    parser.add_argument("--post-target-only", action="store_true", help="render only rooms marked 投稿対象 true")
    parser.add_argument("room_arg", nargs="?", help="room_id shorthand")
    args = parser.parse_args()

    run_id = normalize_run_id(args.run_id)
    if args.all:
        room_ids = candidate_room_ids() if args.post_target_only else all_room_ids()
    elif args.room or args.room_arg:
        room_ids = [args.room or args.room_arg]
    else:
        print("ERROR: --room または --all を指定してください。")
        return 1
    bgm_paths = available_bgm_paths(args.bgm) if args.with_bgm else []
    if args.with_bgm and not bgm_paths:
        print("ERROR: BGMファイルが見つかりません。")
        return 1

    results, (json_path, md_path) = run_rooms(
        room_ids,
        run_id,
        duration=min(args.duration, 15),
        start=args.start,
        auto_record=not args.no_auto_record,
        flat_output=True,
        output_dir=post_ready_dir(run_id),
        allow_non_post_target=not args.post_target_only,
        with_bgm=args.with_bgm,
        bgm_paths=bgm_paths,
        bgm_volume=args.bgm_volume,
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
