import base64
import hashlib
import json
import mimetypes
import os
import random
import sqlite3
import struct
import tempfile
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

try:
    import asyncio
    from contextlib import asynccontextmanager

    import uvicorn
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from starlette.requests import Request

    FASTAPI_AVAILABLE = True
except ModuleNotFoundError:
    FASTAPI_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
DB_PATH = Path(os.environ.get("KYOUKAI_DB_PATH") or (Path(tempfile.gettempdir()) / "kyoukai.db" if os.environ.get("VERCEL") else BASE_DIR / "kyoukai.db"))
TICK_SECONDS = 3
SILENCE_THRESHOLD_SECONDS = 12
OLLAMA_URL = os.environ.get("KYOUKAI_OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("KYOUKAI_OLLAMA_MODEL", "qwen2.5:0.5b")

TRAIT_KEYS = [
    "trait_softness",
    "trait_aggression",
    "trait_gaze",
    "trait_distance",
    "trait_curiosity",
    "trait_corruption",
    "trait_attachment",
]

MUTATION_LOGS = {
    "soft_bloom": ("soft bloom mutation stabilized", "柔らかい膨張を確認"),
    "distorted_pulse": ("distorted pulse repeated", "歪んだ拍動を検出"),
    "gaze_lock": ("gaze lock established", "視線固定反応"),
    "distant_shell": ("distant shell formed", "距離殻を形成"),
    "noise_skin": ("noise skin emerged", "境界ノイズが皮膜化"),
    "phase_slip": ("phase slip recorded", "phase slip 発生"),
    "silent_growth": ("silent growth accumulated", "無言観測による成長"),
}

GENOME_DEFAULTS: dict[str, Any] = {
    "observer_count": 0,
    "total_visits": 0,
    "stay_time": 0,
    "phase": 0,
    "mutation_level": 0,
    "stability": 100,
    "noise_level": 0,
    "tempo": 60,
    "mood": "quiet",
    "last_action": "",
    "log_history": [],
    "updated_at": "",
    "silent_observation": 0,
    "boundary_pressure": 0,
    "drift": 0,
    "phase_drift": 0,
    "audio_instability": 0,
    "visual_instability": 0,
    "mutation_count": 0,
    "last_mutation_type": "none",
    "last_mutation_at": "",
    "mutation_event_id": 0,
    "trait_softness": 0,
    "trait_aggression": 0,
    "trait_gaze": 0,
    "trait_distance": 0,
    "trait_curiosity": 0,
    "trait_corruption": 0,
    "trait_attachment": 0,
    "last_input_at": 0.0,
    "last_event_flags": {},
    "genome_summary": {},
}

COMMAND_EFFECTS: dict[str, dict[str, Any]] = {
    "なでる": {
        "trait_softness": 2,
        "trait_attachment": 1,
        "stability": 2,
        "mutation_level": 1,
        "mood": "soft",
        "log": "soft contact recorded",
        "jp_log": "柔らかい接触を記録",
    },
    "たたく": {
        "trait_aggression": 3,
        "trait_corruption": 1,
        "stability": -5,
        "noise_level": 2,
        "mutation_level": 3,
        "audio_instability": 1,
        "visual_instability": 1,
        "mood": "disturbed",
        "log": "impact disturbance detected",
        "jp_log": "衝撃性ノイズを検出",
    },
    "みつめる": {
        "trait_gaze": 3,
        "silent_observation": 1,
        "phase_drift": 1,
        "mutation_level": 1,
        "mood": "observed",
        "log": "gaze fixed",
        "jp_log": "外部視線が固定",
    },
    "よぶ": {
        "trait_curiosity": 2,
        "tempo": 2,
        "visual_instability": 1,
        "mutation_level": 1,
        "mood": "awake",
        "log": "call signal received",
        "jp_log": "呼び声信号を受理",
    },
    "はなしかける": {
        "trait_curiosity": 1,
        "trait_attachment": 1,
        "stability": 1,
        "mutation_level": 1,
        "mood": "listening",
        "log": "language fragment accepted",
        "jp_log": "言語片を受け入れ",
    },
    "遠ざける": {
        "trait_distance": 3,
        "trait_attachment": -1,
        "stability": -3,
        "noise_level": 3,
        "boundary_pressure": 2,
        "mood": "distant",
        "log": "distance event recorded",
        "jp_log": "距離イベントを記録",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def dominant_trait(genome: dict[str, Any]) -> str:
    key = max(TRAIT_KEYS, key=lambda trait: int(genome.get(trait, 0)))
    return key.removeprefix("trait_")


def genome_summary(genome: dict[str, Any]) -> dict[str, Any]:
    instability = clamp(
        (100 - int(genome["stability"]))
        + int(genome["noise_level"])
        + int(genome["audio_instability"]) // 2
        + int(genome["visual_instability"]) // 2,
        0,
        100,
    )
    return {
        "dominant_trait": dominant_trait(genome),
        "instability": instability,
        "current_mutation": genome.get("last_mutation_type", "none"),
        "mutation_event_id": int(genome.get("mutation_event_id", 0)),
        "last_mutation_at": genome.get("last_mutation_at", ""),
        "audio_mode": mutation_audio_mode(str(genome.get("last_mutation_type", "none"))),
        "visual_mode": str(genome.get("last_mutation_type", "none")).replace("_", "-"),
        "phase": int(genome["phase"]),
    }


def mutation_audio_mode(mutation_type: str) -> str:
    return {
        "soft_bloom": "softTone",
        "distorted_pulse": "hardPulse",
        "gaze_lock": "singleTone",
        "distant_shell": "farShell",
        "noise_skin": "glitchSkin",
        "phase_slip": "phaseDelay",
        "silent_growth": "lowGrowth",
    }.get(mutation_type, "baseline")


class GenomeStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_db()
        self.update(lambda genome: genome.update({"observer_count": 0, "last_event_flags": {}}))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS genome (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS genome_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS mutation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mutation_type TEXT NOT NULL,
                    phase INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS observation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS affiliate_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT NOT NULL,
                    url TEXT NOT NULL,
                    signal_text TEXT NOT NULL,
                    trigger_phase INTEGER DEFAULT 0,
                    trigger_mutation TEXT DEFAULT 'any',
                    display_mode TEXT DEFAULT 'panel',
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                )
                """
            )
            self._ensure_affiliate_signal_columns(connection)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS signal_clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot_name TEXT NOT NULL,
                    signal_id INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            if connection.execute("SELECT COUNT(*) FROM affiliate_signals").fetchone()[0] == 0:
                seed_signals = [
                    ("観測支援物資 TYPE-A", "#external-signal", "外部物質 TYPE-A 境界侵食中 / 広告コード未挿入", 0, "any", "panel"),
                    ("補助装置 NODE-01", "#external-signal", "外部ノード接触確認 / NODE-01 / 未接続", 1, "any", "panel"),
                    ("未確認接続 SIGNAL-X", "#external-signal", "[EXTERNAL] ████ 境界外信号受信 / 空枠", 0, "any", "log"),
                    ("境界外リンク CORRUPT-02", "#external-signal", "mutation外部干渉 / 汚染源確認 / 未挿入", 2, "noise_skin", "popup"),
                    ("深夜観測支援 SILENT-03", "#external-signal", "深夜外部接触 / 無言観測支援 / 空欄", 0, "silent_growth", "random"),
                ]
                for lbl, url, txt, phase, mut, mode in seed_signals:
                    connection.execute(
                        "INSERT INTO affiliate_signals (label, url, signal_text, trigger_phase, trigger_mutation, display_mode, enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?)",
                        (lbl, url, txt, phase, mut, mode, now_iso()),
                    )
            self._ensure_kyoukai_affiliate_signal(connection)
            row = connection.execute("SELECT data FROM genome WHERE id = 1").fetchone()
            if row is None:
                genome = GENOME_DEFAULTS | {"updated_at": now_iso(), "last_input_at": time.time()}
                genome["genome_summary"] = genome_summary(genome)
                connection.execute(
                    "INSERT INTO genome (id, data, updated_at) VALUES (1, ?, ?)",
                    (json.dumps(genome, ensure_ascii=False), genome["updated_at"]),
                )

    def _ensure_affiliate_signal_columns(self, connection: sqlite3.Connection) -> None:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(affiliate_signals)").fetchall()}
        migrations = {
            "affiliate_provider": "ALTER TABLE affiliate_signals ADD COLUMN affiliate_provider TEXT DEFAULT 'none'",
            "slot_name": "ALTER TABLE affiliate_signals ADD COLUMN slot_name TEXT DEFAULT 'left_terminal_bottom'",
            "weight": "ALTER TABLE affiliate_signals ADD COLUMN weight INTEGER DEFAULT 1",
        }
        for column, statement in migrations.items():
            if column not in columns:
                connection.execute(statement)
        connection.execute(
            """
            UPDATE affiliate_signals
            SET slot_name = CASE
                WHEN display_mode = 'popup' THEN 'mutation_banner'
                WHEN display_mode = 'random' THEN 'midnight_banner'
                WHEN display_mode = 'log' THEN 'room_corner'
                WHEN id % 2 = 0 THEN 'right_monitor_inner'
                ELSE 'left_terminal_bottom'
            END
            WHERE slot_name IS NULL OR slot_name = 'left_terminal_bottom'
            """
        )

    def _ensure_kyoukai_affiliate_signal(self, connection: sqlite3.Connection) -> None:
        signal = {
            "label": "観測補助装置",
            "url": "https://px.a8.net/svt/ejp?a8mat=4B3R2X+4S2ALU+5GDG+NV9N7",
            "signal_text": "仮想観測基盤を検出 / 深夜稼働ノード応答あり",
            "trigger_phase": 0,
            "trigger_mutation": "any",
            "display_mode": "panel",
            "affiliate_provider": "A8",
            "slot_name": "room_poster",
            "weight": 5,
        }
        row = connection.execute(
            "SELECT id FROM affiliate_signals WHERE label = ? OR url = ?",
            (signal["label"], signal["url"]),
        ).fetchone()
        if row:
            connection.execute(
                """
                UPDATE affiliate_signals
                SET url = ?, signal_text = ?, trigger_phase = ?, trigger_mutation = ?,
                    display_mode = ?, enabled = 1, affiliate_provider = ?, slot_name = ?, weight = ?
                WHERE id = ?
                """,
                (
                    signal["url"],
                    signal["signal_text"],
                    signal["trigger_phase"],
                    signal["trigger_mutation"],
                    signal["display_mode"],
                    signal["affiliate_provider"],
                    signal["slot_name"],
                    signal["weight"],
                    row["id"],
                ),
            )
            return
        connection.execute(
            """
            INSERT INTO affiliate_signals
                (label, url, signal_text, trigger_phase, trigger_mutation, display_mode,
                 enabled, created_at, affiliate_provider, slot_name, weight)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
            """,
            (
                signal["label"],
                signal["url"],
                signal["signal_text"],
                signal["trigger_phase"],
                signal["trigger_mutation"],
                signal["display_mode"],
                now_iso(),
                signal["affiliate_provider"],
                signal["slot_name"],
                signal["weight"],
            ),
        )

    def get(self) -> dict[str, Any]:
        with self.lock:
            return self._read()

    def update(self, mutator) -> dict[str, Any]:
        with self.lock:
            genome = self._read()
            mutator(genome)
            self._normalize(genome)
            self._write(genome)
            return genome

    def _read(self) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT data FROM genome WHERE id = 1").fetchone()
        genome = GENOME_DEFAULTS | json.loads(row["data"])
        if not isinstance(genome.get("log_history"), list):
            genome["log_history"] = []
        if not isinstance(genome.get("last_event_flags"), dict):
            genome["last_event_flags"] = {}
        if not isinstance(genome.get("genome_summary"), dict):
            genome["genome_summary"] = {}
        if not genome.get("last_input_at"):
            genome["last_input_at"] = time.time()
        return genome

    def _write(self, genome: dict[str, Any]) -> None:
        genome["genome_summary"] = genome_summary(genome)
        genome["updated_at"] = now_iso()
        payload = json.dumps(genome, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                "UPDATE genome SET data = ?, updated_at = ? WHERE id = 1",
                (payload, genome["updated_at"]),
            )
            connection.execute(
                "INSERT INTO genome_state (created_at, snapshot_json) VALUES (?, ?)",
                (genome["updated_at"], payload),
            )

    def _normalize(self, genome: dict[str, Any]) -> None:
        genome["observer_count"] = clamp(int(genome["observer_count"]), 0, 999)
        genome["total_visits"] = max(0, int(genome["total_visits"]))
        genome["stay_time"] = max(0, int(genome["stay_time"]))
        genome["phase"] = clamp(int(genome["phase"]), 0, 3)
        genome["mutation_level"] = clamp(int(genome["mutation_level"]), 0, 999)
        genome["stability"] = clamp(int(genome["stability"]), 0, 100)
        genome["noise_level"] = clamp(int(genome["noise_level"]), 0, 100)
        genome["tempo"] = clamp(int(genome["tempo"]), 30, 180)
        genome["silent_observation"] = clamp(int(genome["silent_observation"]), 0, 999)
        genome["boundary_pressure"] = clamp(int(genome["boundary_pressure"]), 0, 100)
        genome["drift"] = clamp(int(genome["drift"]), 0, 100)
        genome["phase_drift"] = clamp(int(genome["phase_drift"]), 0, 100)
        genome["audio_instability"] = clamp(int(genome["audio_instability"]), 0, 100)
        genome["visual_instability"] = clamp(int(genome["visual_instability"]), 0, 100)
        genome["mutation_count"] = max(0, int(genome["mutation_count"]))
        genome["mutation_event_id"] = max(0, int(genome["mutation_event_id"]))
        for trait in TRAIT_KEYS:
            genome[trait] = clamp(int(genome[trait]), 0, 100)

    def append_log(self, genome: dict[str, Any], message: str, channel: str = "OBS") -> None:
        entry = f"[{channel}] {message}"
        genome["log_history"] = [entry, *genome.get("log_history", [])][:64]
        snapshot = json.dumps(genome, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO logs (message, created_at) VALUES (?, ?)",
                (entry, now_iso()),
            )
            connection.execute(
                "INSERT INTO observation_logs (message, created_at, snapshot_json) VALUES (?, ?, ?)",
                (entry, now_iso(), snapshot),
            )

    def append_mutation(self, genome: dict[str, Any], mutation_type: str) -> None:
        snapshot = json.dumps(genome, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO mutation_history (mutation_type, phase, created_at, snapshot_json)
                VALUES (?, ?, ?, ?)
                """,
                (mutation_type, int(genome["phase"]), now_iso(), snapshot),
            )


store = GenomeStore(DB_PATH)


ALLOWED_AFFILIATE_HOSTS = {"px.a8.net"}


def is_allowed_affiliate_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme == "https" and parsed.netloc.lower() in ALLOWED_AFFILIATE_HOSTS


# ─── Affiliate Signal System ─────────────────────────────────────────────────

def get_active_signals(phase: int, mutation_type: str, limit: int = 6) -> list[dict[str, Any]]:
    """Return enabled signals filtered by current genome state."""
    with store._connect() as connection:
        rows = connection.execute(
            """
            SELECT id, label, url, signal_text, trigger_phase, trigger_mutation, display_mode,
                   affiliate_provider, slot_name, weight
            FROM affiliate_signals
            WHERE enabled = 1 AND trigger_phase <= ?
            ORDER BY
                CASE WHEN trigger_mutation = ? THEN 0
                     WHEN trigger_mutation = 'any' THEN 1
                     ELSE 2 END,
                weight DESC,
                id
            LIMIT ?
            """,
            (phase, mutation_type, limit),
        ).fetchall()
    return [display_signal(dict(r)) for r in rows]


def get_signals_by_mode(phase: int, mutation_type: str, mode: str) -> list[dict[str, Any]]:
    """Return enabled signals filtered by display mode."""
    with store._connect() as connection:
        rows = connection.execute(
            """
            SELECT id, label, url, signal_text, trigger_phase, trigger_mutation, display_mode,
                   affiliate_provider, slot_name, weight
            FROM affiliate_signals
            WHERE enabled = 1 AND trigger_phase <= ? AND display_mode = ?
            ORDER BY
                CASE WHEN trigger_mutation = ? THEN 0
                     WHEN trigger_mutation = 'any' THEN 1
                     ELSE 2 END,
                weight DESC,
                id
            """,
            (phase, mode, mutation_type),
        ).fetchall()
    return [display_signal(dict(r)) for r in rows]


def display_signal(row: dict[str, Any]) -> dict[str, Any]:
    """Return a public signal payload, allowing only approved affiliate redirects."""
    original_url = str(row.get("url") or "")
    is_configured_affiliate = (
        is_allowed_affiliate_url(original_url)
        and "YOUR_A8_CODE" not in original_url
    )
    row["url"] = original_url if is_configured_affiliate else "#external-signal"
    row["signal_kind"] = "external_signal"
    row["is_affiliate"] = is_configured_affiliate
    row["disclosure"] = "PR / アフィリエイトリンクを含みます" if row["is_affiliate"] else ""
    row.setdefault("affiliate_provider", "none")
    row.setdefault("slot_name", "left_terminal_bottom")
    row.setdefault("weight", 1)
    return row


def list_signal_videos() -> list[str]:
    """Return local video files that can be played inside the /signal TV screen."""
    if not VIDEOS_DIR.exists():
        return []
    videos: list[str] = []
    for path in sorted(VIDEOS_DIR.iterdir(), key=lambda item: item.name.lower()):
        if path.is_file() and path.suffix.lower() in {".mp4", ".webm", ".m4v"}:
            videos.append("/videos/" + quote(path.name))
    return videos


def add_affiliate_signal(label: str, url: str, signal_text: str, trigger_phase: int = 0,
                         trigger_mutation: str = "any", display_mode: str = "panel") -> dict[str, Any]:
    """Insert a new affiliate signal into the database."""
    with store._connect() as connection:
        cursor = connection.execute(
            "INSERT INTO affiliate_signals (label, url, signal_text, trigger_phase, trigger_mutation, display_mode, enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?)",
            (label, url, signal_text, trigger_phase, trigger_mutation, display_mode, now_iso()),
        )
        new_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM affiliate_signals WHERE id = ?", (new_id,)).fetchone()
    return dict(row)


def log_signal_click(slot_name: str, signal_id: int, provider: str) -> None:
    """Store inert signal click telemetry without external ad code."""
    with store._connect() as connection:
        connection.execute(
            "INSERT INTO signal_clicks (slot_name, signal_id, provider, created_at) VALUES (?, ?, ?, ?)",
            (slot_name[:80], int(signal_id), provider[:80], now_iso()),
        )


# ─────────────────────────────────────────────────────────────────────────────


RADIO_FALLBACK_LINES = [
    "現在、受信域八十三番に接続しています。意味のない言葉が、夜を満たしていきます。",
    "こちらは境界外放送です。午前三時から未明にかけて、沈黙が強まるでしょう。",
    "第六観測波、通過。存在しない町の灯りが、まだ消えていません。",
    "受信番号、零、零、七。聞こえている方は、そのまま聞いてください。",
    "この放送は終了していません。終了予定も、登録されていません。",
    "遠い窓から、白い信号が流入しています。意味は確認されていません。",
]


def generate_radio_line() -> dict[str, Any]:
    """Generate one broken midnight broadcast line via local Ollama when available."""
    prompt = (
        "KYOUKAIの受信域で流れる、意味が少し崩れた深夜ラジオ放送文を日本語で一文だけ作ってください。"
        "ニュース、天気予報、周波数、存在しない地名、受信番号のどれかを含める。"
        "ホラー、血、霊、怪物、説明口調は禁止。45文字から90文字。"
    )
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.9, "num_predict": 80},
    }).encode("utf-8")
    try:
        request = UrlRequest(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2.2) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = str(data.get("response", "")).strip().replace("\n", " ")
        if text:
            return {"line": text[:160], "source": "ollama", "model": OLLAMA_MODEL}
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        pass
    return {"line": random.choice(RADIO_FALLBACK_LINES), "source": "fallback", "model": "local-script"}


def apply_effect(genome: dict[str, Any], effect: dict[str, Any]) -> None:
    for key, value in effect.items():
        if key in {"log", "jp_log", "mood"}:
            continue
        genome[key] = int(genome.get(key, 0)) + int(value)
    if "mood" in effect:
        genome["mood"] = str(effect["mood"])


def add_threshold_log(genome: dict[str, Any], key: str, message: str) -> None:
    flags = genome.setdefault("last_event_flags", {})
    if not flags.get(key):
        flags[key] = True
        store.append_log(genome, message)


def choose_mutation(genome: dict[str, Any]) -> str:
    candidates = {
        "soft_bloom": genome["trait_softness"] + genome["trait_attachment"] // 2,
        "distorted_pulse": genome["trait_aggression"] + genome["audio_instability"] // 2,
        "gaze_lock": genome["trait_gaze"] + genome["silent_observation"] // 3,
        "distant_shell": genome["trait_distance"] * 2,
        "noise_skin": genome["trait_corruption"] + genome["noise_level"] // 4,
        "phase_slip": genome["phase_drift"] + genome["drift"] // 2,
        "silent_growth": genome["silent_observation"] + genome["trait_gaze"] // 2,
    }
    return max(candidates, key=candidates.get)


def maybe_mutate(genome: dict[str, Any]) -> None:
    threshold = 8 + min(12, genome["mutation_count"] * 2)
    if genome["mutation_level"] < threshold:
        return
    mutation_type = choose_mutation(genome)
    genome["mutation_count"] += 1
    genome["last_mutation_type"] = mutation_type
    genome["last_mutation_at"] = now_iso()
    genome["mutation_event_id"] += 1
    genome["mutation_level"] = max(0, genome["mutation_level"] - 5)
    genome["visual_instability"] += 2
    genome["audio_instability"] += 1
    if mutation_type == "soft_bloom":
        genome["stability"] += 3
        genome["trait_softness"] += 1
        genome["noise_level"] -= 2
        genome["tempo"] -= 2
    elif mutation_type == "distorted_pulse":
        genome["noise_level"] += 4
        genome["trait_aggression"] += 1
        genome["tempo"] += 4
    elif mutation_type == "gaze_lock":
        genome["phase_drift"] += 2
        genome["trait_gaze"] += 1
        genome["tempo"] -= 1
    elif mutation_type == "distant_shell":
        genome["boundary_pressure"] += 3
        genome["trait_distance"] += 1
        genome["audio_instability"] += 1
    elif mutation_type == "noise_skin":
        genome["trait_corruption"] += 2
        genome["noise_level"] += 3
        genome["audio_instability"] += 2
    elif mutation_type == "phase_slip":
        genome["phase_drift"] += 3
        genome["drift"] += 2
        genome["visual_instability"] += 2
    elif mutation_type == "silent_growth":
        genome["silent_observation"] += 2
        genome["trait_attachment"] += 1
        genome["tempo"] -= 3

    obs_log, jp_log = MUTATION_LOGS[mutation_type]
    store.append_log(genome, obs_log)
    store.append_log(genome, jp_log, "観測")
    store.append_log(genome, f"organism contour shifted: {mutation_type}")
    store.append_mutation(genome, mutation_type)

    # Affiliate: log-mode signal injection on mutation
    log_signals = get_signals_by_mode(int(genome["phase"]), mutation_type, "log")
    if log_signals and random.random() < 0.55:
        sig = random.choice(log_signals)
        store.append_log(genome, f"§SIGNAL§#external-signal§{sig['signal_text']}", "SIGNAL")

    # Affiliate: random-mode signal injection on mutation
    rand_signals = get_signals_by_mode(int(genome["phase"]), mutation_type, "random")
    if rand_signals and random.random() < 0.35:
        sig = random.choice(rand_signals)
        store.append_log(genome, f"§SIGNAL§#external-signal§{sig['signal_text']}", "SIGNAL")


def update_phase(genome: dict[str, Any]) -> None:
    previous_phase = int(genome["phase"])
    next_phase = 0
    if genome["mutation_count"] >= 1:
        next_phase = 1
    if genome["mutation_count"] >= 3 or genome["trait_corruption"] >= 10:
        next_phase = 2
    if genome["phase_drift"] >= 10 or genome["visual_instability"] >= 12:
        next_phase = 3
    genome["phase"] = max(previous_phase, next_phase)
    if genome["phase"] > previous_phase:
        store.append_log(genome, "phase drift crossed threshold")
        store.append_log(genome, "phase drift 微増", "観測")


def recalculate_genome(genome: dict[str, Any]) -> None:
    genome["boundary_pressure"] += genome["observer_count"] * 2 + genome["silent_observation"] // 14
    genome["noise_level"] += genome["boundary_pressure"] // 12 + genome["trait_corruption"] // 8
    genome["noise_level"] = max(
        genome["noise_level"],
        100 - genome["stability"] + genome["mutation_level"] // 6 + genome["boundary_pressure"] // 5,
    )
    genome["tempo"] = 60 + genome["observer_count"] * 3 + genome["mutation_level"] // 2 + genome["drift"] // 4
    genome["drift"] += genome["mutation_level"] // 28 + genome["phase_drift"] // 20
    genome["visual_instability"] += genome["trait_aggression"] // 18 + genome["trait_corruption"] // 20
    genome["audio_instability"] += genome["noise_level"] // 35 + genome["trait_corruption"] // 22
    maybe_mutate(genome)
    update_phase(genome)

    if genome["stability"] < 70:
        add_threshold_log(genome, "stability_lt_70", "stability decline detected")
    if genome["noise_level"] > 20:
        add_threshold_log(genome, "noise_gt_20", "boundary noise expanded")
    if genome["mutation_level"] > 10:
        add_threshold_log(genome, "mutation_gt_10", "mutation pressure rising")
    if genome["silent_observation"] > 8:
        add_threshold_log(genome, "silence_gt_8", "silence accumulated")


def apply_connection() -> dict[str, Any]:
    def mutate(genome: dict[str, Any]) -> None:
        genome["observer_count"] += 1
        genome["total_visits"] += 1
        genome["boundary_pressure"] += 2
        genome["tempo"] += 1
        if genome["observer_count"] > 1:
            genome["stability"] -= 1
            genome["visual_instability"] += 1
        store.append_log(genome, "observer entered the boundary")
        store.append_log(genome, "接続を確認", "観測")
        recalculate_genome(genome)

    return store.update(mutate)


def apply_disconnection() -> dict[str, Any]:
    def mutate(genome: dict[str, Any]) -> None:
        genome["observer_count"] -= 1
        genome["boundary_pressure"] = max(0, genome["boundary_pressure"] - 1)
        store.append_log(genome, "observer left a faint pressure")
        recalculate_genome(genome)

    return store.update(mutate)


def apply_action(raw_action: str) -> dict[str, Any]:
    action = raw_action.strip()[:80] or "無言"

    def mutate(genome: dict[str, Any]) -> None:
        effect = COMMAND_EFFECTS.get(
            action,
            {
                "trait_curiosity": 1,
                "mutation_level": 1,
                "mood": "unknown",
                "log": "unclassified input entered the genome",
                "jp_log": "未分類入力を保存",
            },
        ).copy()
        if action == "なでる" and genome["stability"] < 55:
            effect["stability"] = 1
            effect["trait_attachment"] = 2
            effect["phase_drift"] = 1
            effect["log"] = "soft contact reached unstable tissue"
        if action == "なでる" and genome["stability"] >= 80:
            effect["trait_softness"] += 1
            effect["log"] = "soft bloom pressure accepted"
        if action == "たたく" and genome["noise_level"] > 25:
            effect["trait_corruption"] += 2
            effect["visual_instability"] += 2
            effect["log"] = "impact echoed through noisy skin"
        if action == "みつめる" and genome["trait_gaze"] > 8:
            effect["phase_drift"] += 2
            effect["log"] = "external gaze synchronized with core"
        if genome["observer_count"] >= 2:
            effect["mutation_level"] = int(effect.get("mutation_level", 0)) + 1
            effect["boundary_pressure"] = int(effect.get("boundary_pressure", 0)) + genome["observer_count"]

        genome["last_action"] = action
        genome["last_input_at"] = time.time()
        apply_effect(genome, effect)
        store.append_log(genome, str(effect["log"]))
        store.append_log(genome, str(effect["jp_log"]), "観測")
        store.append_log(genome, f"action received: {action}")
        recalculate_genome(genome)

    return store.update(mutate)


class StdlibWebSocketHub:
    def __init__(self) -> None:
        self.clients: set[Any] = set()
        self.lock = threading.Lock()

    def add(self, client: Any) -> None:
        with self.lock:
            self.clients.add(client)

    def remove(self, client: Any) -> None:
        with self.lock:
            self.clients.discard(client)

    def broadcast(self, genome: dict[str, Any]) -> None:
        message = json.dumps(state_payload(genome), ensure_ascii=False)
        with self.lock:
            clients = list(self.clients)
        for client in clients:
            try:
                client.send_ws_text(message)
            except OSError:
                self.remove(client)


stdlib_hub = StdlibWebSocketHub()


def tick_once() -> dict[str, Any]:
    def mutate(genome: dict[str, Any]) -> None:
        if genome["observer_count"] <= 0:
            genome["observer_count"] = 0
            return
        genome["stay_time"] += genome["observer_count"] * TICK_SECONDS
        genome["boundary_pressure"] += genome["observer_count"]
        genome["tempo"] += 1
        if genome["observer_count"] >= 2:
            genome["noise_level"] += 1
            genome["visual_instability"] += 1

        seconds_since_input = time.time() - float(genome.get("last_input_at", time.time()))
        if seconds_since_input >= SILENCE_THRESHOLD_SECONDS:
            genome["silent_observation"] += genome["observer_count"]
            genome["trait_gaze"] += 1
            genome["phase_drift"] += 1
            genome["drift"] += max(1, genome["observer_count"] // 2)
            if random.random() < 0.4:
                store.append_log(genome, "silence accumulated")
                store.append_log(genome, "無言観測が蓄積", "観測")

        if genome["stability"] >= 82 and seconds_since_input < SILENCE_THRESHOLD_SECONDS:
            genome["trait_attachment"] += 1
            genome["stability"] += 1
        if genome["stability"] < 55:
            genome["trait_corruption"] += 1
            genome["audio_instability"] += 1
        if random.random() < 0.18:
            store.append_log(genome, "genome pulse detected")

        # Affiliate: random-mode signal injection on tick (low probability)
        if random.random() < 0.07:
            rand_sigs = get_signals_by_mode(int(genome["phase"]), str(genome.get("last_mutation_type", "none")), "random")
            if rand_sigs:
                sig = random.choice(rand_sigs)
                store.append_log(genome, f"§SIGNAL§#external-signal§{sig['signal_text']}", "SIGNAL")

        recalculate_genome(genome)

    return store.update(mutate)


def run_stdlib_clock() -> None:
    while True:
        time.sleep(TICK_SECONDS)
        stdlib_hub.broadcast(tick_once())


def state_payload(genome: dict[str, Any]) -> dict[str, Any]:
    summary = genome_summary(genome)
    genome["genome_summary"] = summary
    mutation = str(genome.get("last_mutation_type", "none"))
    phase = int(genome.get("phase", 0))
    panel_signals = get_signals_by_mode(phase, mutation, "panel")[:3]
    popup_signals = get_signals_by_mode(phase, mutation, "popup")[:1]
    return {
        "type": "genome",
        "genome": genome,
        "genome_summary": summary,
        "affiliate_panel": panel_signals,
                "affiliate_popup": popup_signals,
    }


class KyoukaiHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    _PAGE_MAP: dict[str, str] = {
        "/": "home.html",
        "/index.html": "home.html",
        "/observation": "index.html",
        "/archive": "archive.html",
        "/signal": "signal.html",
        "/exit": "exit.html",
        "/null": "null.html",
    }

    def do_GET(self) -> None:
        if self.path == "/ws":
            self.handle_websocket()
            return
        clean_path = self.path.split("?", 1)[0]
        if clean_path in self._PAGE_MAP:
            self.serve_file(
                BASE_DIR / "templates" / self._PAGE_MAP[clean_path],
                "text/html; charset=utf-8",
            )
            return
        if clean_path.startswith("/static/"):
            relative = clean_path.removeprefix("/static/")
            self.serve_file(BASE_DIR / "static" / relative)
            return
        if clean_path.startswith("/videos/"):
            relative = clean_path.removeprefix("/videos/")
            self.serve_file(BASE_DIR / "videos" / relative)
            return
        if clean_path == "/api/genome":
            genome = store.get()
            summary = genome_summary(genome)
            data = {
                "phase": int(genome.get("phase", 0)),
                "mutation_count": int(genome.get("mutation_count", 0)),
                "last_mutation_type": str(genome.get("last_mutation_type", "none")),
                "observer_count": int(genome.get("observer_count", 0)),
                "stability": int(genome.get("stability", 100)),
                "noise_level": int(genome.get("noise_level", 0)),
                "mood": str(genome.get("mood", "quiet")),
                "dominant_trait": summary.get("dominant_trait", "none"),
                "instability": summary.get("instability", 0),
                "updated_at": str(genome.get("updated_at", "")),
            }
            body = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if clean_path == "/api/signals":
            genome = store.get()
            phase = int(genome.get("phase", 0))
            mutation = str(genome.get("last_mutation_type", "none"))
            signals = get_active_signals(phase, mutation)
            body = json.dumps({"signals": signals}, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if clean_path == "/api/radio-line":
            body = json.dumps(generate_radio_line(), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if clean_path == "/api/videos":
            body = json.dumps({"videos": list_signal_videos()}, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/api/action":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw)
                genome = apply_action(str(body.get("action", "")))
                stdlib_hub.broadcast(genome)
                resp = json.dumps(state_payload(genome), ensure_ascii=False).encode()
                self.send_response(200)
            except Exception as exc:
                resp = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode()
                self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        if self.path == "/api/signal-click":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw)
                log_signal_click(
                    slot_name=str(body.get("slot_name", "unknown")),
                    signal_id=int(body.get("signal_id", 0)),
                    provider=str(body.get("provider", "none")),
                )
                resp = json.dumps({"ok": True}, ensure_ascii=False).encode()
                self.send_response(200)
            except Exception as exc:
                resp = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode()
                self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        if self.path == "/api/signals":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw)
                signal = add_affiliate_signal(
                    label=str(body.get("label", "untitled")),
                    url=str(body.get("url", "")),
                    signal_text=str(body.get("signal_text", "")),
                    trigger_phase=int(body.get("trigger_phase", 0)),
                    trigger_mutation=str(body.get("trigger_mutation", "any")),
                    display_mode=str(body.get("display_mode", "panel")),
                )
                resp = json.dumps({"ok": True, "signal": signal}, ensure_ascii=False).encode()
                self.send_response(200)
            except Exception as exc:
                resp = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode()
                self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        self.send_error(404)

    def serve_file(self, path: Path, content_type: str | None = None) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        guessed_type = content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", guessed_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_websocket(self) -> None:
        key = self.headers.get("Sec-WebSocket-Key", "")
        accept = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        ).decode()
        self.send_response(101)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()

        stdlib_hub.add(self)
        stdlib_hub.broadcast(apply_connection())
        try:
            while True:
                message = self.read_ws_text()
                if message is None:
                    break
                data = json.loads(message)
                if data.get("type") == "action" or "action" in data:
                    stdlib_hub.broadcast(apply_action(str(data.get("action", ""))))
        except (OSError, json.JSONDecodeError):
            pass
        finally:
            stdlib_hub.remove(self)
            stdlib_hub.broadcast(apply_disconnection())

    def read_ws_text(self) -> str | None:
        header = self.rfile.read(2)
        if len(header) < 2:
            return None
        first, second = header
        opcode = first & 0x0F
        if opcode == 8:
            return None
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.rfile.read(8))[0]
        mask = self.rfile.read(4)
        payload = bytearray(self.rfile.read(length))
        for index in range(length):
            payload[index] ^= mask[index % 4]
        return payload.decode("utf-8")

    def send_ws_text(self, message: str) -> None:
        payload = message.encode("utf-8")
        header = bytearray([0x81])
        if len(payload) < 126:
            header.append(len(payload))
        elif len(payload) < 65536:
            header.extend([126, *struct.pack("!H", len(payload))])
        else:
            header.extend([127, *struct.pack("!Q", len(payload))])
        self.wfile.write(header + payload)
        self.wfile.flush()

    def log_message(self, format: str, *args: Any) -> None:
        return


if FASTAPI_AVAILABLE:
    class FastAPIConnectionManager:
        def __init__(self) -> None:
            self.connections: set[WebSocket] = set()

        async def connect(self, websocket: WebSocket) -> None:
            await websocket.accept()
            self.connections.add(websocket)

        def disconnect(self, websocket: WebSocket) -> None:
            self.connections.discard(websocket)

        async def broadcast(self, genome: dict[str, Any]) -> None:
            message = json.dumps(state_payload(genome), ensure_ascii=False)
            for websocket in list(self.connections):
                try:
                    await websocket.send_text(message)
                except RuntimeError:
                    self.disconnect(websocket)

    fastapi_manager = FastAPIConnectionManager()

    async def genome_clock() -> None:
        while True:
            await asyncio.sleep(TICK_SECONDS)
            await fastapi_manager.broadcast(tick_once())

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        task = asyncio.create_task(genome_clock())
        try:
            yield
        finally:
            task.cancel()

    app = FastAPI(title="KYOUKAI alpha", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
    videos_dir = VIDEOS_DIR
    videos_dir.mkdir(exist_ok=True)
    app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")
    templates = Jinja2Templates(directory=BASE_DIR / "templates")

    from fastapi import Body
    from fastapi.responses import JSONResponse

    def render_template(request: Request, name: str) -> HTMLResponse:
        try:
            return templates.TemplateResponse(
                request=request,
                name=name,
                context={"request": request},
            )
        except TypeError:
            return templates.TemplateResponse(name, {"request": request})

    # ─── Pages ──────────────────────────────────────────────────────────────

    @app.get("/", response_class=HTMLResponse)
    async def entrance(request: Request) -> HTMLResponse:
        return render_template(request, "home.html")

    @app.get("/observation", response_class=HTMLResponse)
    async def observation(request: Request) -> HTMLResponse:
        return render_template(request, "index.html")

    @app.get("/archive", response_class=HTMLResponse)
    async def archive(request: Request) -> HTMLResponse:
        return render_template(request, "archive.html")

    @app.get("/signal", response_class=HTMLResponse)
    async def signal_room(request: Request) -> HTMLResponse:
        return render_template(request, "signal.html")

    @app.get("/exit", response_class=HTMLResponse)
    async def exit_room(request: Request) -> HTMLResponse:
        return render_template(request, "exit.html")

    @app.get("/null", response_class=HTMLResponse)
    async def null_room(request: Request) -> HTMLResponse:
        return render_template(request, "null.html")

    # ─── API ────────────────────────────────────────────────

    @app.get("/api/genome")
    async def api_genome() -> JSONResponse:
        genome = store.get()
        summary = genome_summary(genome)
        return JSONResponse({
            "phase": int(genome.get("phase", 0)),
            "mutation_count": int(genome.get("mutation_count", 0)),
            "last_mutation_type": str(genome.get("last_mutation_type", "none")),
            "observer_count": int(genome.get("observer_count", 0)),
            "stability": int(genome.get("stability", 100)),
            "noise_level": int(genome.get("noise_level", 0)),
            "mood": str(genome.get("mood", "quiet")),
            "dominant_trait": summary.get("dominant_trait", "none"),
            "instability": summary.get("instability", 0),
            "updated_at": str(genome.get("updated_at", "")),
        })

    @app.get("/api/signals")
    async def api_get_signals() -> JSONResponse:
        genome = store.get()
        phase = int(genome.get("phase", 0))
        mutation = str(genome.get("last_mutation_type", "none"))
        signals = get_active_signals(phase, mutation)
        return JSONResponse({"signals": signals})

    @app.get("/api/radio-line")
    async def api_radio_line() -> JSONResponse:
        return JSONResponse(generate_radio_line())

    @app.get("/api/videos")
    async def api_videos() -> JSONResponse:
        return JSONResponse({"videos": list_signal_videos()})

    @app.post("/api/signals")
    async def api_post_signal(body: dict = Body(...)) -> JSONResponse:
        try:
            signal = add_affiliate_signal(
                label=str(body.get("label", "untitled")),
                url=str(body.get("url", "")),
                signal_text=str(body.get("signal_text", "")),
                trigger_phase=int(body.get("trigger_phase", 0)),
                trigger_mutation=str(body.get("trigger_mutation", "any")),
                display_mode=str(body.get("display_mode", "panel")),
            )
            return JSONResponse({"ok": True, "signal": signal})
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    @app.post("/api/action")
    async def api_action(body: dict = Body(...)) -> JSONResponse:
        try:
            genome = apply_action(str(body.get("action", "")))
            await fastapi_manager.broadcast(genome)
            return JSONResponse(state_payload(genome))
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    @app.post("/api/signal-click")
    async def api_signal_click(body: dict = Body(...)) -> JSONResponse:
        try:
            log_signal_click(
                slot_name=str(body.get("slot_name", "unknown")),
                signal_id=int(body.get("signal_id", 0)),
                provider=str(body.get("provider", "none")),
            )
            return JSONResponse({"ok": True})
        except Exception as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await fastapi_manager.connect(websocket)
        await fastapi_manager.broadcast(apply_connection())
        try:
            while True:
                payload = await websocket.receive_text()
                data = json.loads(payload)
                if data.get("type") == "action" or "action" in data:
                    await fastapi_manager.broadcast(apply_action(str(data.get("action", ""))))
        except (WebSocketDisconnect, json.JSONDecodeError):
            fastapi_manager.disconnect(websocket)
            await fastapi_manager.broadcast(apply_disconnection())


def main() -> None:
    if FASTAPI_AVAILABLE:
        host = os.environ.get("HOST", "127.0.0.1")
        port = int(os.environ.get("PORT", "8000"))
        uvicorn.run(app, host=host, port=port, reload=False)
        return
    threading.Thread(target=run_stdlib_clock, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), KyoukaiHandler)
    print("KYOUKAI alpha running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
