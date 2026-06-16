import json
import math
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATUS_PATH = ROOT / "status.json"
MARKERS_PATH = ROOT / "recording_markers.json"

DIRS = {
    "input_videos": ROOT / "input_videos",
    "input_audio": ROOT / "input_audio",
    "qr": ROOT / "qr",
    "output_shorts": ROOT / "output_shorts",
    "output_meta": ROOT / "output_meta",
    "recordings_archive": ROOT / "recordings_archive",
    "logs": ROOT / "logs",
    "temp": ROOT / "temp",
}

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".flv", ".avi"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
QR_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

TITLES = [
    "この世界、生成中につきご容赦ください",
    "AIに変なサイト作らせてる",
    "今日も変なサイトをいじってる",
    "この世界、まだ途中です",
    "また変なページを調整してる",
    "完成してないけど増えてます",
    "KYOUKAI、生成中",
    "変なサイト作ってる途中です",
]


def now_jst() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))


def log(message: str) -> None:
    DIRS["logs"].mkdir(parents=True, exist_ok=True)
    line = f"[{now_jst().isoformat(timespec='seconds')}] {message}"
    print(line)
    with (DIRS["logs"] / "process.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_dirs() -> None:
    for directory in DIRS.values():
        directory.mkdir(parents=True, exist_ok=True)


def cleanup_old_files(config) -> None:
    keep_days = int(config.get("storage", {}).get("keep_days", 3))
    cutoff = datetime.now().timestamp() - (keep_days * 86400)
    cleanup_log = DIRS["logs"] / "cleanup.log"
    targets = [DIRS["input_videos"], DIRS["recordings_archive"], DIRS["temp"]]
    for base in targets:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            try:
                if path.stat().st_mtime < cutoff:
                    cleanup_log.parent.mkdir(parents=True, exist_ok=True)
                    with cleanup_log.open("a", encoding="utf-8") as f:
                        f.write(f"[{now_jst().isoformat(timespec='seconds')}] delete {path}\n")
                    path.unlink()
            except OSError as exc:
                log(f"cleanup failed: {path} ({exc})")


def find_executable(config_value: str, fallback_name: str) -> str | None:
    if config_value:
        candidate = Path(config_value)
        if candidate.exists():
            return str(candidate)
    return shutil.which(fallback_name)


def probe_duration(ffprobe: str, video_path: Path) -> float:
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def choose_starts(duration: float, short_len: int, count: int) -> list[float]:
    usable = max(0, duration - short_len)
    if usable <= 1:
        return []
    if count <= 1:
        return [min(30, usable)]
    start = min(30, usable)
    end = max(start, usable - 10)
    if end <= start:
        return [round(start, 2)]
    return [round(start + ((end - start) * i / (count - 1)), 2) for i in range(count)]


def parse_cut_point(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        raise ValueError("empty cut point")
    if ":" not in text:
        return float(text)
    parts = [float(part) for part in text.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return (minutes * 60) + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return (hours * 3600) + (minutes * 60) + seconds
    raise ValueError(f"invalid timecode: {value}")


def choose_manual_starts(values, duration: float, short_len: int) -> list[float]:
    starts = []
    for value in values:
        try:
            start = parse_cut_point(value)
        except (TypeError, ValueError) as exc:
            log(f"skip invalid manual cut point {value!r}: {exc}")
            continue
        if start < 0 or start + short_len > duration:
            log(f"skip out-of-range manual cut point {value!r}: source duration={duration:.1f}s")
            continue
        starts.append(round(start, 2))
    return starts


def choose_marker_starts(duration: float, short_len: int, pre_roll: float) -> list[float]:
    marker_data = load_json(MARKERS_PATH, {"markers": []})
    starts = []
    for marker in marker_data.get("markers", []):
        try:
            marked_second = float(marker["seconds"])
        except (KeyError, TypeError, ValueError):
            log(f"skip invalid recording marker: {marker!r}")
            continue
        start = max(0.0, marked_second - pre_roll)
        if start + short_len > duration:
            start = max(0.0, duration - short_len)
        rounded = round(start, 2)
        if rounded not in starts:
            starts.append(rounded)
    return starts


def first_file(directory: Path, exts: set[str]) -> Path | None:
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in exts:
            return path
    return None


def next_devlog_id(status) -> tuple[str, int]:
    number = int(status.get("next_devlog_number", 1))
    return f"devlog_{number:03d}", number


def build_utm(config, devlog_id: str) -> str:
    site = config.get("site", {})
    base = str(site.get("base_url", "https://www.void-kyoukai.net/")).strip()
    base = base.replace("[", "").replace("]", "")
    if "(" in base and ")" in base:
        base = base[base.find("(") + 1 : base.find(")")]
    base = base.rstrip("/")
    return (
        f"{base}/?utm_source={site.get('utm_source', 'youtube')}"
        f"&utm_medium={site.get('utm_medium', 'shorts')}"
        f"&utm_campaign={devlog_id}"
    )


def write_meta(config, devlog_id: str, title_index: int) -> None:
    url = build_utm(config, devlog_id)
    title = TITLES[title_index % len(TITLES)]
    body = f"""タイトル：
{title}

説明：
この世界を少しずつ増やしています。

まだ途中です。

{url}

#KYOUKAI
#制作中
#shorts

固定コメント：
作っているのはここです。

{url}
"""
    (DIRS["output_meta"] / f"{devlog_id}.txt").write_text(body, encoding="utf-8")


def make_short(ffmpeg: str, source: Path, output: Path, start: float, length: int, config, audio: Path | None, qr: Path | None) -> None:
    video = config.get("video", {})
    width = int(video.get("output_width", 1080))
    height = int(video.get("output_height", 1920))
    fps = int(video.get("fps", 30))

    inputs = ["-ss", str(start), "-t", str(length), "-i", str(source)]
    audio_index = None
    qr_index = None
    if audio:
        audio_index = 1
        inputs += ["-stream_loop", "-1", "-i", str(audio)]
    if qr:
        qr_index = 1 + (1 if audio else 0)
        inputs += ["-i", str(qr)]

    base_filter = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,fps={fps}[v0]"
    )
    filter_complex = base_filter
    video_map = "[v0]"
    if qr_index is not None:
        filter_complex += f";[{qr_index}:v]scale=160:-1[qr];[v0][qr]overlay=W-w-36:H-h-36[v]"
        video_map = "[v]"

    cmd = [ffmpeg, "-y", *inputs, "-filter_complex", filter_complex, "-map", video_map]
    if audio_index is not None:
        cmd += ["-map", f"{audio_index}:a:0", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += [
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def process_video(
    video_path: Path,
    config,
    status,
    ffmpeg: str,
    ffprobe: str,
    audio: Path | None,
    qr: Path | None,
    use_recording_markers: bool,
) -> int:
    video_cfg = config.get("video", {})
    short_len = int(video_cfg.get("short_length_sec", 15))
    max_count = int(video_cfg.get("candidates_per_video", 5))
    min_count = int(video_cfg.get("min_candidates_per_video", 3))
    manual_cut_points = video_cfg.get("manual_cut_points", [])
    marker_pre_roll = float(video_cfg.get("marker_pre_roll_sec", 10))

    duration = probe_duration(ffprobe, video_path)
    if duration < short_len + 2:
        log(f"skip short source: {video_path.name} ({duration:.1f}s)")
        return 0

    marker_starts = choose_marker_starts(duration, short_len, marker_pre_roll) if use_recording_markers else []
    if marker_starts:
        starts = marker_starts
        log(f"recording markers selected: {starts}")
    elif manual_cut_points:
        starts = choose_manual_starts(manual_cut_points, duration, short_len)
        log(f"manual cut points selected: {starts}")
    else:
        possible_count = min(max_count, max(min_count, math.floor(duration / max(short_len, 1))))
        starts = choose_starts(duration, short_len, possible_count)
        log(f"automatic cut points selected: {starts}")

    if not starts:
        log(f"no valid cut points: {video_path.name}")
        return 0

    generated = 0

    for start in starts:
        devlog_id, number = next_devlog_id(status)
        output = DIRS["output_shorts"] / f"{devlog_id}_{video_path.stem}_{generated + 1:02d}.mp4"
        log(f"generate {output.name}: {video_path.name} {start:.1f}s-{start + short_len:.1f}s")
        make_short(ffmpeg, video_path, output, start, short_len, config, audio, qr)
        write_meta(config, devlog_id, number - 1)
        status["next_devlog_number"] = number + 1
        generated += 1

    archive_path = DIRS["recordings_archive"] / video_path.name
    suffix = 1
    while archive_path.exists():
        archive_path = DIRS["recordings_archive"] / f"{video_path.stem}_{suffix}{video_path.suffix}"
        suffix += 1
    shutil.move(str(video_path), str(archive_path))
    status.setdefault("processed_files", []).append(
        {
            "source": video_path.name,
            "archived_to": archive_path.name,
            "generated": generated,
            "processed_at": now_jst().isoformat(timespec="seconds"),
        }
    )
    if use_recording_markers and MARKERS_PATH.exists():
        MARKERS_PATH.unlink()
        log("recording markers consumed and cleared")
    return generated


def main() -> int:
    ensure_dirs()
    config = load_json(CONFIG_PATH, {})
    status = load_json(STATUS_PATH, {"next_devlog_number": 1, "processed_files": []})
    cleanup_old_files(config)

    videos = [p for p in sorted(DIRS["input_videos"].iterdir()) if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    if not videos:
        log("処理対象なし: input_videosに動画がありません。")
        save_json(STATUS_PATH, status)
        return 0

    ffmpeg = find_executable(config.get("video", {}).get("ffmpeg_path", ""), "ffmpeg")
    ffprobe = find_executable(config.get("video", {}).get("ffprobe_path", ""), "ffprobe")
    if not ffmpeg or not ffprobe:
        log("ERROR: FFmpeg/FFprobeが見つかりません。config.jsonのvideo.ffmpeg_path / ffprobe_pathを設定してください。")
        return 1

    audio = first_file(DIRS["input_audio"], AUDIO_EXTS)
    qr = first_file(DIRS["qr"], QR_EXTS)
    if not audio:
        log("input_audioにBGMがありません。BGMなしで生成します。")
    if not qr:
        log("qrに画像がありません。QRなしで生成します。")

    total = 0
    marker_video = max(videos, key=lambda path: path.stat().st_mtime) if MARKERS_PATH.exists() else None
    for video in videos:
        try:
            total += process_video(
                video,
                config,
                status,
                ffmpeg,
                ffprobe,
                audio,
                qr,
                use_recording_markers=(video == marker_video),
            )
            save_json(STATUS_PATH, status)
        except Exception as exc:
            log(f"ERROR: {video.name}: {exc}")

    save_json(STATUS_PATH, status)
    log(f"done: generated {total} shorts")
    log(f"output_shorts: {DIRS['output_shorts']}")
    log(f"output_meta: {DIRS['output_meta']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
