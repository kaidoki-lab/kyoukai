import base64
import hashlib
import json
import mimetypes
import os
import random
import re
import shutil
import sqlite3
import struct
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request


BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
VIDEO_EDITS_DIR = VIDEOS_DIR / "edits"
VIDEOS_MANIFEST_PATH = BASE_DIR / "static" / "videos-manifest.json"
DB_PATH = Path(os.environ.get("KYOUKAI_DB_PATH") or (Path(tempfile.gettempdir()) / "kyoukai.db" if os.environ.get("VERCEL") else BASE_DIR / "kyoukai.db"))
TICK_SECONDS = 3
SILENCE_THRESHOLD_SECONDS = 12
OLLAMA_URL = os.environ.get("KYOUKAI_OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("KYOUKAI_OLLAMA_MODEL", "qwen2.5:0.5b")
DEFAULT_GA_MEASUREMENT_ID = "G-ZXWYDXKCYS"
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", DEFAULT_GA_MEASUREMENT_ID).strip()

try:
    from genome_system import CreatureGeneratorAI, get_creature_params
    from genome_system.genome_defs import CORES, MUTATIONS, ORGANS, SHELLS

    GENOME_SYSTEM_AVAILABLE = True
except Exception:
    CreatureGeneratorAI = None  # type: ignore[assignment]
    CORES: dict[str, Any] = {}
    MUTATIONS: dict[str, Any] = {}
    ORGANS: dict[str, Any] = {}
    SHELLS: dict[str, Any] = {}
    GENOME_SYSTEM_AVAILABLE = False

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
    "phase_up_event_id": 0,
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

CREATURE_GENERATED_DIR = Path(tempfile.gettempdir()) / "kyoukai_creatures"
_creature_generator = CreatureGeneratorAI(CREATURE_GENERATED_DIR) if GENOME_SYSTEM_AVAILABLE and CreatureGeneratorAI else None
_creature_cache: dict[str, dict[str, Any]] = {}

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


def kyoukai_to_evo_genome(genome: dict[str, Any]) -> dict[str, Any]:
    """Map the existing KYOUKAI genome to the standalone creature genome scale."""
    return {
        "AGGRO": clamp(
            int(genome.get("trait_aggression", 0))
            + int(genome.get("noise_level", 0)) // 3
            + max(0, 100 - int(genome.get("stability", 100))) // 4,
            0,
            100,
        ),
        "CALM": clamp(
            int(genome.get("trait_softness", 0))
            + int(genome.get("trait_attachment", 0))
            + int(genome.get("stability", 100)) // 5,
            0,
            100,
        ),
        "CURIOSITY": clamp(
            int(genome.get("trait_curiosity", 0))
            + int(genome.get("trait_gaze", 0))
            + int(genome.get("observer_count", 0)) * 3
            + int(genome.get("silent_observation", 0)) // 3,
            0,
            100,
        ),
        "DISTORTION": clamp(
            int(genome.get("trait_corruption", 0))
            + int(genome.get("phase_drift", 0))
            + int(genome.get("visual_instability", 0)) // 2
            + int(genome.get("boundary_pressure", 0)) // 4,
            0,
            100,
        ),
        "last_update": str(genome.get("updated_at", "")),
    }


def creature_rarity(genome: dict[str, Any], evo: dict[str, Any]) -> str:
    peak = max(int(evo.get(key, 0)) for key in ("AGGRO", "CALM", "CURIOSITY", "DISTORTION"))
    phase = int(genome.get("phase", 0))
    mutations = int(genome.get("mutation_count", 0))
    if phase >= 3 or peak >= 86:
        return "Myth"
    if mutations >= 5 or peak >= 68:
        return "Legend"
    if mutations >= 2 or peak >= 42:
        return "Rare"
    return "Common"


def public_creature_payload(genome: dict[str, Any]) -> dict[str, Any]:
    evo = kyoukai_to_evo_genome(genome)
    if not GENOME_SYSTEM_AVAILABLE or not _creature_generator:
        return {"available": False, "evo": evo}

    params = get_creature_params(evo)
    params["rarity"] = creature_rarity(genome, evo)
    key = "|".join(
        [
            str(params.get("branch", "none")),
            str(params.get("variant", "normal")),
            str(params.get("danger", 0)),
            str(params.get("rarity", "Common")),
            str(genome.get("phase", 0)),
            str(genome.get("mutation_count", 0)),
            str(genome.get("last_mutation_type", "none")),
        ]
    )
    creature = _creature_cache.get(key)
    if creature is None:
        creature = _creature_generator.generate(
            branch=str(params["branch"]),
            variant=str(params["variant"]),
            rarity=str(params["rarity"]),
            danger=int(params["danger"]),
            seed_text=key,
        )
        _creature_cache[key] = creature

    cg = creature.get("genome", {})
    organs = [str(ORGANS.get(organ, organ)) for organ in cg.get("organs", [])]
    core = str(CORES.get(str(cg.get("core", "")), {}).get("name", cg.get("core", "unknown")))
    mutation = str(MUTATIONS.get(str(cg.get("mutation", "")), cg.get("mutation", "None")))
    shell = str(SHELLS.get(str(cg.get("shell", "")), cg.get("shell", "unknown")))
    return {
        "available": True,
        "evo": evo,
        "params": params,
        "species_id": creature.get("species_id", ""),
        "name": creature.get("name", "Unknown Organism"),
        "branch": creature.get("branch", params["branch"]),
        "variant": creature.get("variant", params["variant"]),
        "rarity": creature.get("rarity", params["rarity"]),
        "danger": creature.get("danger", params["danger"]),
        "body_plan": cg.get("body_plan", "larva_soft"),
        "silhouette": cg.get("silhouette", "larva_soft"),
        "core": core,
        "organs": organs,
        "shell": shell,
        "mutation": mutation,
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    target_room TEXT NOT NULL,
                    observation TEXT NOT NULL,
                    judgment TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    candidates_json TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    status TEXT NOT NULL DEFAULT 'pending',
                    codex_ready INTEGER NOT NULL DEFAULT 0,
                    codex_instruction TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
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
            # keep only the latest 1000 genome_state snapshots to prevent unbounded growth
            connection.execute(
                "DELETE FROM genome_state WHERE id NOT IN (SELECT id FROM genome_state ORDER BY id DESC LIMIT 1000)"
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
        genome["phase_up_event_id"] = max(0, int(genome.get("phase_up_event_id", 0)))
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
            # retain only the last 30 days of log entries
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            connection.execute("DELETE FROM logs WHERE created_at < ?", (cutoff,))
            connection.execute("DELETE FROM observation_logs WHERE created_at < ?", (cutoff,))

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
        return load_video_manifest()
    videos: list[str] = []
    for path in sorted(VIDEOS_DIR.iterdir(), key=lambda item: item.name.lower()):
        if path.is_file() and path.suffix.lower() in {".mp4", ".webm", ".m4v"}:
            videos.append("/videos/" + quote(path.name))
    return videos


def load_video_manifest() -> list[str]:
    """Read the deploy-time video list when videos are served by Vercel's CDN."""
    try:
        data = json.loads(VIDEOS_MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    videos = data.get("videos", [])
    if not isinstance(videos, list):
        return []
    return [item for item in videos if isinstance(item, str)]


def site_config_payload() -> dict[str, Any]:
    return {
        "analytics": {
            "gaMeasurementId": GA_MEASUREMENT_ID,
        }
    }


CENTRAL_OS_DIR = BASE_DIR / "central-os"
CENTRAL_OS_FILES = [
    "rooms.json",
    "ideas.json",
    "monthly-goal.json",
    "monetization.json",
    "sns-routes.json",
]
PROPOSALS_FILE = CENTRAL_OS_DIR / "proposals" / "proposals.json"
SUPERVISOR_DIR = CENTRAL_OS_DIR / "supervisor"
GENERATION_DIR = CENTRAL_OS_DIR / "generation"
GENERATED_DIR = CENTRAL_OS_DIR / "generated"
GENERATED_CONTENT_FILE = GENERATED_DIR / "generated-content.json"
METRICS_DIR = CENTRAL_OS_DIR / "metrics"
OBSERVATIONS_DIR = CENTRAL_OS_DIR / "observations"
OBSERVATIONS_FILE = OBSERVATIONS_DIR / "observations.json"
CYCLE_DIR = CENTRAL_OS_DIR / "cycle"
CYCLE_MAP_FILE = CYCLE_DIR / "cycle-map.json"
EVOLUTION_DIR = CENTRAL_OS_DIR / "evolution"
EVOLUTION_LOG_FILE = EVOLUTION_DIR / "evolution-log.json"
SUPERVISOR_FILES = [
    "supervisor-rules.md",
    "proposal-schema.md",
    "risk-rules.md",
    "phase-4-review.md",
]
GENERATION_FILES = [
    "generation-schema.md",
    "generation-rules.md",
    "content-types.md",
    "room-generation-rules.md",
    "sns-generation-rules.md",
    "phase-5-review.md",
]
METRICS_FILES = [
    "metrics-schema.md",
    "metrics-rules.md",
    "event-types.md",
    "observation-rules.md",
    "phase-6-review.md",
    "metrics-sample.json",
]
CYCLE_FILES = [
    "cycle-schema.md",
    "cycle-rules.md",
    "cycle-map.json",
    "feedback-loop.md",
    "phase-7-review.md",
]
EVOLUTION_FILES = [
    "evolution-rules.md",
    "evolution-log.json",
    "evolution-schema.md",
]
WATCH_DIR = CENTRAL_OS_DIR / "watch"
DIFF_LOG_FILE = WATCH_DIR / "diff-log.json"
WATCH_TARGETS_FILE = WATCH_DIR / "watch-targets.json"
WATCH_GENERATED_DIR = WATCH_DIR / "generated"
WATCH_HISTORY_DIR = WATCH_DIR / "history"

GA4_PROPERTY_ID = os.environ.get("KYOUKAI_GA4_PROPERTY_ID", "538546349")
GA4_CREDENTIALS_FILE = BASE_DIR / "ga4-credentials.json"
AI_ANALYST_FILE = CENTRAL_OS_DIR / "analysis" / "ai_analyst.py"
PLANNING_DIR = CENTRAL_OS_DIR / "planning"
AI_PLANNER_FILE = PLANNING_DIR / "ai_planner.py"
EXECUTION_DIR = CENTRAL_OS_DIR / "execution"
AI_EXECUTOR_FILE = EXECUTION_DIR / "ai_executor.py"
HISTORY_DIR = CENTRAL_OS_DIR / "history"

# Vercel 本番はファイルシステムが読み取り専用のため、書き込みファイルは /tmp へ
_IS_VERCEL = bool(os.environ.get("VERCEL"))
_TMP = Path(tempfile.gettempdir())

def _writable(local_path: Path, filename: str) -> Path:
    """Return /tmp/<filename> on Vercel, otherwise local_path."""
    return (_TMP / filename) if _IS_VERCEL else local_path

UPDATE_PROPOSALS_FILE    = _writable(CENTRAL_OS_DIR / "update-proposals.json",          "update-proposals.json")
PROPOSAL_PLANS_FILE      = _writable(PLANNING_DIR   / "proposal_plans.json",             "proposal_plans.json")
ACCEPTED_PLANS_FILE      = _writable(HISTORY_DIR    / "accepted-plans.json",             "accepted-plans.json")
REJECTED_PLANS_FILE      = _writable(HISTORY_DIR    / "rejected-plans.json",             "rejected-plans.json")
IMPLEMENTATION_TASKS_FILE = _writable(EXECUTION_DIR / "implementation_tasks.json",       "implementation_tasks.json")
EXECUTED_TASKS_FILE      = _writable(HISTORY_DIR    / "executed-tasks.json",             "executed-tasks.json")

# ─── AI analyst module (importlib, handles hyphen in path) ─────────────────────

def _load_ai_analyst():
    """Load central-os/analysis/ai_analyst.py at runtime."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ai_analyst", AI_ANALYST_FILE)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod
    except Exception:
        return None

_ai_analyst_mod = _load_ai_analyst()

# ─── AI planner module ────────────────────────────────────────────────────────

def _load_ai_planner():
    """Load central-os/planning/ai_planner.py at runtime."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ai_planner", AI_PLANNER_FILE)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod
    except Exception:
        return None

_ai_planner_mod = _load_ai_planner()

# ─── AI executor module ───────────────────────────────────────────────────────

def _load_ai_executor():
    """Load central-os/execution/ai_executor.py at runtime."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ai_executor", AI_EXECUTOR_FILE)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod
    except Exception:
        return None

_ai_executor_mod = _load_ai_executor()


def _read_json_list(path: Path) -> list:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def run_ai_planner() -> dict[str, Any]:
    """Assemble planner input, call ai_planner, save proposal_plans.json."""
    # gather context
    ga4_data = _fetch_ga4_data()
    room_scores = _analyze_rooms(ga4_data)

    recent_accepted = _read_json_list(ACCEPTED_PLANS_FILE)[-5:]
    recent_rejected = _read_json_list(REJECTED_PLANS_FILE)[-5:]
    recent_changes: list = []

    try:
        with open(UPDATE_PROPOSALS_FILE, encoding="utf-8") as f:
            up = json.load(f)
        recent_changes = [
            {"page": p.get("observedPage", ""), "status": p.get("status", "")}
            for p in (up if isinstance(up, list) else [])[:5]
        ]
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    planner_input: dict[str, Any] = {
        "ga4": ga4_data,
        "analysis": {},
        "rooms": room_scores,
        "recentChanges": recent_changes,
        "recentAccepted": recent_accepted,
        "recentRejected": recent_rejected,
    }

    # save planner_input for inspection
    PLANNING_DIR.mkdir(parents=True, exist_ok=True)

    if _ai_planner_mod is not None:
        try:
            plans = _ai_planner_mod.generate_plans(planner_input)
        except Exception:
            plans = []
    else:
        plans = []

    # fallback if module unavailable or returned empty
    if not plans:
        now = datetime.now(timezone.utc).isoformat()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        plans = [
            {
                "id": f"plan-{stamp}-01",
                "title": "崩落域の記憶断片追加",
                "summary": "/nullに断片化したテキストを追加し、「なにかがあった」という印象を与える。",
                "reason": "崩落域への反応が確認されており、滞在時間が伸びる可能性がある。",
                "targets": ["/null"],
                "implementationSize": "small",
                "status": "pending",
                "createdAt": now,
                "source": "fallback",
            }
        ]

    with open(PROPOSAL_PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)

    return {
        "plans_written": len(plans),
        "source": plans[0].get("source", "unknown") if plans else "none",
        "file": str(PROPOSAL_PLANS_FILE),
    }


def get_plan_proposals() -> list[dict[str, Any]]:
    return _read_json_list(PROPOSAL_PLANS_FILE)


def run_ai_executor() -> dict[str, Any]:
    """Generate implementation tasks for all approved plans not yet processed."""
    plans = _read_json_list(PROPOSAL_PLANS_FILE)
    approved = [p for p in plans if p.get("status") == "approved"]

    existing_tasks = _read_json_list(IMPLEMENTATION_TASKS_FILE)
    processed_plan_ids = {t.get("sourcePlanId") for t in existing_tasks}

    new_tasks = []
    for plan in approved:
        plan_id = plan.get("id")
        if plan_id in processed_plan_ids:
            continue

        if _ai_executor_mod is not None:
            try:
                task = _ai_executor_mod.generate_task(plan)
            except Exception:
                task = None
        else:
            task = None

        if task is None:
            # minimal fallback without executor module
            now = datetime.now(timezone.utc).isoformat()
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            task = {
                "id": f"task-{stamp}",
                "sourcePlanId": plan_id,
                "createdAt": now,
                "title": f"{plan.get('title', '企画')} 実装指示",
                "targetPages": plan.get("targets", ["/null"]),
                "objective": plan.get("summary", "")[:120],
                "implementationBrief": (
                    f"{plan.get('summary', '')} "
                    "現行構造を確認してから実装方法を判断すること。"
                )[:300],
                "candidateFiles": ["main.py", "（現行構造を確認してから判断）"],
                "mustKeep": [
                    "KYOUKAIをゲーム化しない",
                    "ユーザーにCentral OSの存在を見せない",
                    "秘密情報やcredentials関連を変更しない",
                ],
                "doNotChange": [
                    "GA4接続処理",
                    "AI分析官",
                    "AI企画官",
                    "既存の採用/保留/却下API",
                    "credentials関連",
                ],
                "steps": [
                    "現行ルートとテンプレート構造を確認する",
                    "対象ページに必要な最小変更を加える",
                    "既存導線を壊さないか確認する",
                    "ローカル表示を確認する",
                ],
                "acceptanceCriteria": [
                    "対象ページが正常表示される",
                    "既存ページが壊れていない",
                    "git statusに秘密情報が含まれていない",
                ],
                "status": "pending",
                "codexReady": False,
                "source": "fallback",
            }

        new_tasks.append(task)
        processed_plan_ids.add(plan_id)

    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    all_tasks = existing_tasks + new_tasks
    with open(IMPLEMENTATION_TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)

    return {
        "tasks_written": len(new_tasks),
        "total_tasks": len(all_tasks),
        "approved_plans": len(approved),
        "file": str(IMPLEMENTATION_TASKS_FILE),
    }


def update_task_status(task_id: str, status: str) -> dict[str, Any]:
    """Update implementation task status. Moves 'done' tasks to history."""
    valid = {"pending", "ready", "sent", "done", "hold", "rejected"}
    if status not in valid:
        raise ValueError(f"invalid status: {status}")

    tasks = _read_json_list(IMPLEMENTATION_TASKS_FILE)
    found = None
    for t in tasks:
        if t.get("id") == task_id:
            t["status"] = status
            t["codexReady"] = status in {"ready", "sent", "done"}
            found = t
            break
    if not found:
        raise ValueError(f"task {task_id} not found")

    with open(IMPLEMENTATION_TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    if status == "done":
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        history = _read_json_list(EXECUTED_TASKS_FILE)
        history.append({**found, "decidedAt": now_iso()})
        with open(EXECUTED_TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-100:], f, ensure_ascii=False, indent=2)

    return found


def update_plan_status(plan_id: str, status: str) -> dict[str, Any]:
    """Update plan status. Moves approved/rejected plans to history files."""
    valid = {"pending", "approved", "hold", "rejected"}
    if status not in valid:
        raise ValueError(f"invalid status: {status}")

    plans = _read_json_list(PROPOSAL_PLANS_FILE)
    found = None
    for p in plans:
        if p.get("id") == plan_id:
            p["status"] = status
            found = p
            break
    if not found:
        raise ValueError(f"plan {plan_id} not found")

    with open(PROPOSAL_PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)

    # append to history
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if status == "approved":
        history = _read_json_list(ACCEPTED_PLANS_FILE)
        history.append({**found, "decidedAt": now_iso()})
        with open(ACCEPTED_PLANS_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-100:], f, ensure_ascii=False, indent=2)
    elif status == "rejected":
        history = _read_json_list(REJECTED_PLANS_FILE)
        history.append({**found, "decidedAt": now_iso()})
        with open(REJECTED_PLANS_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-100:], f, ensure_ascii=False, indent=2)

    return found

def analyze_page_ai(page: str, pv: int, avg_duration: float, bounce_rate: float, priority: str) -> dict:
    """Call ai_analyst.analyze_page, fall back to empty dict on any error."""
    if _ai_analyst_mod is None:
        return {}
    try:
        return _ai_analyst_mod.analyze_page(
            page=page, pv=pv, avg_duration=avg_duration,
            bounce_rate=bounce_rate, priority=priority,
        )
    except Exception:
        return {}

# ─── GA4 analysis ──────────────────────────────────────────────────────────────

def _fetch_ga4_data() -> dict[str, Any]:
    """Fetch page metrics from GA4 Data API. Returns empty dict if unavailable."""
    if not GA4_CREDENTIALS_FILE.exists():
        return {}
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Metric, RunReportRequest,
        )
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            str(GA4_CREDENTIALS_FILE),
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        client = BetaAnalyticsDataClient(credentials=creds)
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="sessions"),
            ],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
            limit=50,
        )
        response = client.run_report(request)
        rows = []
        for row in response.rows:
            rows.append({
                "path": row.dimension_values[0].value,
                "pageviews": int(row.metric_values[0].value),
                "avg_duration": float(row.metric_values[1].value),
                "bounce_rate": float(row.metric_values[2].value),
                "sessions": int(row.metric_values[3].value),
            })
        return {"rows": rows, "source": "ga4", "fetched_at": now_iso()}
    except Exception as exc:
        return {"error": str(exc), "source": "ga4_error"}


def _analyze_rooms(ga4_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Score each room based on GA4 metrics. Falls back to mock data if GA4 unavailable."""
    known_rooms = [
        {"path": "/", "name": "祭壇域"},
        {"path": "/observation", "name": "観測域"},
        {"path": "/observer", "name": "逆観測室"},
        {"path": "/signal", "name": "受信域"},
        {"path": "/daimyojin", "name": "AI大明神室"},
        {"path": "/hyougi", "name": "評議録"},
        {"path": "/exit", "name": "崩壊域"},
        {"path": "/null", "name": "未確認接続"},
        {"path": "/outside", "name": "外部接続"},
        {"path": "/archive", "name": "記録室"},
    ]
    rows = ga4_data.get("rows", [])
    row_map = {r["path"]: r for r in rows}

    results = []
    for room in known_rooms:
        row = row_map.get(room["path"], {})
        pv = row.get("pageviews", 0)
        dur = row.get("avg_duration", 0.0)
        bounce = row.get("bounce_rate", 1.0)
        sessions = row.get("sessions", 0)

        # score: high pv + long duration + low bounce = strong
        if pv == 0 and not rows:
            score = "no_data"
            label = "データなし"
        elif pv == 0:
            score = "dead"
            label = "死んだ接続"
        elif pv >= 50 and dur >= 30:
            score = "strong"
            label = "反応強"
        elif pv >= 20:
            score = "active"
            label = "反応あり"
        elif bounce >= 0.8:
            score = "weak"
            label = "反応弱"
        else:
            score = "normal"
            label = "通常"

        results.append({
            "path": room["path"],
            "name": room["name"],
            "pageviews": pv,
            "avg_duration": round(dur, 1),
            "bounce_rate": round(bounce, 3),
            "sessions": sessions,
            "score": score,
            "label": label,
        })
    return results


def _generate_proposal_candidates(room: dict[str, Any]) -> list[str]:
    """Use Ollama to generate change candidates for a room. Falls back to rules."""
    score = room["score"]
    name = room["name"]
    path = room["path"]

    fallbacks = {
        "strong": [
            f"{name}の生命体ログを1件追加する",
            f"{name}の背景ノイズを微強化する",
            f"{name}から別の部屋への導線を薄く追加する",
            f"{name}に異常断片テキストを1件追加する",
        ],
        "dead": [
            f"{name}（{path}）を「死んだ接続」として変質候補にする",
            f"{name}のリンクを一時的に隠蔽する",
            f"{name}に崩壊テキストを追加して消失感を演出する",
        ],
        "weak": [
            f"{name}の導線配置を変更する",
            f"{name}のビジュアルに軽い変化を加える",
            f"{name}から強い部屋への接続を追加する",
        ],
        "active": [
            f"{name}に小さな変化を1つ加える",
            f"{name}の異常断片を更新する",
        ],
    }

    prompt = (
        f"KYOUKAIというウェブサイトの「{name}」（{path}）に関する変化候補を3つ生成してください。"
        f"このページの状態：{room['label']}（PV:{room['pageviews']} 滞在:{room['avg_duration']}秒）。"
        "KYOUKAIは自己増殖する狂ったウェブサイトで、ゲームではありません。"
        "各候補は20文字以内の日本語で、具体的な変更内容のみ。箇条書き不要。1行1候補。"
    )
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.85, "num_predict": 120},
    }).encode("utf-8")
    try:
        request = UrlRequest(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(request, timeout=5.0) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = str(data.get("response", "")).strip()
        lines = [l.strip("・- 　") for l in text.splitlines() if l.strip()]
        if lines:
            return lines[:4]
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        pass
    return fallbacks.get(score, fallbacks["active"])


def run_analysis() -> dict[str, Any]:
    """Run full analysis: fetch GA4, score rooms, generate proposals, save to DB."""
    batch_id = f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    ga4_data = _fetch_ga4_data()
    room_scores = _analyze_rooms(ga4_data)

    proposals = []
    for room in room_scores:
        score = room["score"]
        if score in ("no_data", "normal"):
            continue

        judgment_map = {
            "strong": f"{room['name']}への反応が強い。増殖候補に入れる。",
            "active": f"{room['name']}に反応あり。小さな変化を加える。",
            "weak": f"{room['name']}の反応が弱い。導線または変質候補にする。",
            "dead": f"{room['name']}が死んでいる。変質または隠蔽候補にする。",
        }
        priority_map = {"strong": "high", "dead": "high", "weak": "medium", "active": "low"}

        candidates = _generate_proposal_candidates(room)
        observation = (
            f"{room['name']} — PV:{room['pageviews']} / "
            f"滞在:{room['avg_duration']}秒 / 直帰率:{room['bounce_rate']}"
        )

        with store._connect() as conn:
            conn.execute(
                """INSERT INTO proposals
                   (batch_id, target_room, observation, judgment, change_type,
                    candidates_json, reason, priority, status, codex_ready,
                    created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    batch_id,
                    room["path"],
                    observation,
                    judgment_map.get(score, ""),
                    score,
                    json.dumps(candidates, ensure_ascii=False),
                    f"{room['label']}のため変化候補を生成した。",
                    priority_map.get(score, "medium"),
                    "pending",
                    0,
                    now_iso(),
                    now_iso(),
                ),
            )
        proposals.append({
            "room": room["name"],
            "score": score,
            "candidates_count": len(candidates),
        })

    return {
        "batch_id": batch_id,
        "ga4_source": ga4_data.get("source", "no_data"),
        "rooms_analyzed": len(room_scores),
        "proposals_generated": len(proposals),
        "proposals": proposals,
    }


def generate_update_proposals() -> dict[str, Any]:
    """Fetch GA4 data, apply analysis rules v1, save update-proposals.json."""
    ga4_data = _fetch_ga4_data()
    rows: list[dict[str, Any]] = ga4_data.get("rows", [])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # sort by pageviews desc
    sorted_rows = sorted(rows, key=lambda r: r.get("pageviews", 0), reverse=True)
    pv_rank = {r["path"]: i for i, r in enumerate(sorted_rows)}

    # rule table: path → (proposalType, changes_template, reason_template)
    PAGE_RULES: dict[str, dict[str, Any]] = {
        "/null": {
            "proposalType": "page_growth",
            "changes": [
                "崩落域の追加断片テキストを1件生成する",
                "崩壊演出の軽い差分を追加する",
                "/archive へ残留ログを追加する",
            ],
            "reason": "GA4上で/nullへの反応が確認できるため、崩落域を増殖候補に入れる。",
            "name": "未確認接続",
        },
        "/observation": {
            "proposalType": "page_growth",
            "changes": [
                "観測域の生命体ログを1件追加する",
                "背景ノイズの軽い強化を加える",
                "/signal への導線を薄く追加する",
                "観測者数に応じた微変化を追加する",
            ],
            "reason": "観測域が現在もっとも反応を得ているため、KYOUKAIの中核として増殖候補に入れる。",
            "name": "観測域",
        },
        "/outside": {
            "proposalType": "outside_adjustment",
            "changes": [
                "outsideアイコンの配置パターンを増やす",
                "外部接続後に戻る導線を追加する",
                "自販機型の隠しアイコンを1種類追加する",
                "/signal に外部信号ログを1件追加する",
            ],
            "reason": "外部接続への反応が確認されているため、outside を異常導線として強化する。",
            "name": "外部接続",
        },
        "/exit": {
            "proposalType": "scenario_change",
            "changes": [
                "境界域の崩壊演出を1段階強化する",
                "/observation への残留リンクを追加する",
                "exitログに断片テキストを1件追加する",
            ],
            "reason": "/exit への反応があるため、境界導線を強化して世界観を深める。",
            "name": "崩壊域",
        },
        "/archive": {
            "proposalType": "archive_addition",
            "changes": [
                "archive-logsに新規ログ候補を1件生成する",
                "記録室の断片テキストを更新する",
                "/null へのリンクを記録の断片として追加する",
            ],
            "reason": "/archive への反応があるため、記録室への追記候補を生成する。",
            "name": "記録室",
        },
        "/signal": {
            "proposalType": "signal_fragment",
            "changes": [
                "受信域の信号断片テキストを1件追加する",
                "ラジオ放送テキストの候補を生成する",
                "/outside への接続信号を追加する",
            ],
            "reason": "/signal への反応があるため、受信断片を追加して世界観を強化する。",
            "name": "受信域",
        },
        "/": {
            "proposalType": "visual_change",
            "changes": [
                "祭壇域のビジュアル差分を1件生成する",
                "メイン入口の導線テキストを更新する",
                "/observation への導線を強化する",
            ],
            "reason": "メイン入口のPVが高いため、祭壇域のビジュアル更新を候補に入れる。",
            "name": "祭壇域",
        },
    }

    PRIORITY_RULES = {
        0: "high",    # rank 1
        1: "medium",  # rank 2
        2: "medium",  # rank 3
    }

    def _priority(path: str, pv: int) -> str:
        rank = pv_rank.get(path, 99)
        if rank in PRIORITY_RULES:
            return PRIORITY_RULES[rank]
        if pv <= 0:
            return "watch"
        return "low"

    proposals: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    # load existing proposals to preserve status/codexReady
    existing: dict[str, dict[str, Any]] = {}
    try:
        with open(UPDATE_PROPOSALS_FILE, encoding="utf-8") as f:
            for item in json.load(f):
                existing[item.get("observedPage", "")] = item
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    for rank, row in enumerate(sorted_rows[:12]):
        path = row["path"]
        if path not in PAGE_RULES:
            continue
        rule = PAGE_RULES[path]
        pv = row.get("pageviews", 0)
        dur = row.get("avg_duration", 0.0)
        bounce = row.get("bounce_rate", 0.0)

        # generate stable id
        prop_id = f"proposal-{abs(hash(path)) % 900 + 100:03d}"
        if prop_id in used_ids:
            prop_id = f"proposal-{abs(hash(path + today)) % 900 + 100:03d}"
        used_ids.add(prop_id)

        # preserve existing status/codexReady if present
        prev = existing.get(path, {})
        status = prev.get("status", "pending")
        codex_ready = prev.get("codexReady", False)
        priority_val = _priority(path, pv)

        # AI analysis layer
        ai = analyze_page_ai(path, pv, dur, bounce, priority_val)

        proposals.append({
            "id": prop_id,
            "createdAt": today,
            "source": "ga4",
            "observedPage": path,
            "observation": f"{rule['name']}（{path}）— PV:{pv} / 滞在:{round(dur,1)}秒 / 直帰率:{round(bounce*100,1)}%",
            "judgement": _build_judgement(path, pv, rank, row),
            "analysis": ai.get("analysis", ""),
            "hypothesis": ai.get("hypothesis", ""),
            "recommendations": ai.get("recommendations", []),
            "proposalType": rule["proposalType"],
            "targets": [path],
            "changes": rule["changes"],
            "reason": rule["reason"],
            "priority": priority_val,
            "status": status,
            "codexReady": codex_ready,
        })

    # also surface known pages with no data as watch
    for path, rule in PAGE_RULES.items():
        if any(p["observedPage"] == path for p in proposals):
            continue
        prev = existing.get(path, {})
        status = prev.get("status", "pending")
        prop_id = f"proposal-{abs(hash(path + 'nodata')) % 900 + 100:03d}"
        ai = analyze_page_ai(path, 0, 0.0, 0.0, "watch")
        proposals.append({
            "id": prop_id,
            "createdAt": today,
            "source": "ga4",
            "observedPage": path,
            "observation": f"{rule['name']}（{path}）— データなし / 反応未確認",
            "judgement": f"{rule['name']}への反応が確認できない。導線見直しを検討する。",
            "analysis": ai.get("analysis", ""),
            "hypothesis": ai.get("hypothesis", ""),
            "recommendations": ai.get("recommendations", []),
            "proposalType": "route_change",
            "targets": [path],
            "changes": [f"{rule['name']}への導線を強化する", f"{rule['name']}への入口を再検討する"],
            "reason": "GA4上でこのページへの反応が確認できないため、導線変更候補とする。",
            "priority": "watch",
            "status": status,
            "codexReady": prev.get("codexReady", False),
        })

    # sort: high → medium → low → watch
    priority_order = {"high": 0, "medium": 1, "low": 2, "watch": 3}
    proposals.sort(key=lambda p: priority_order.get(p["priority"], 9))

    with open(UPDATE_PROPOSALS_FILE, "w", encoding="utf-8") as f:
        json.dump(proposals, f, ensure_ascii=False, indent=2)

    return {
        "proposals_written": len(proposals),
        "ga4_source": ga4_data.get("source", "no_data"),
        "file": str(UPDATE_PROPOSALS_FILE),
    }


def _build_judgement(path: str, pv: int, rank: int, row: dict[str, Any]) -> str:
    """Build a human-readable judgement string."""
    name_map = {
        "/null": "崩落域", "/observation": "観測域", "/outside": "外部接続",
        "/exit": "崩壊域", "/archive": "記録室", "/signal": "受信域", "/": "祭壇域",
    }
    name = name_map.get(path, path)
    if rank == 0:
        return f"{name}のPVが最高。増殖最優先候補。"
    if rank <= 2:
        return f"{name}のPVが上位。増殖候補に入れる。"
    dur = row.get("avg_duration", 0.0)
    if dur >= 30:
        return f"{name}への滞在時間が長い。深い閲覧が発生している。"
    bounce = row.get("bounce_rate", 1.0)
    if bounce >= 0.8:
        return f"{name}の直帰率が高い。ページへの入口は機能しているが離脱も多い。"
    return f"{name}に反応あり。変化候補に入れる。"


def get_proposals(status: str | None = None) -> list[dict[str, Any]]:
    """Fetch proposals from DB, optionally filtered by status."""
    with store._connect() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM proposals WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM proposals ORDER BY created_at DESC LIMIT 100"
            ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["candidates"] = json.loads(d.get("candidates_json", "[]"))
        result.append(d)
    return result


def update_proposal_status(proposal_id: int, status: str, codex_instruction: str | None = None) -> dict[str, Any]:
    """Update proposal status to adopted/held/rejected."""
    valid = {"pending", "adopted", "held", "rejected"}
    if status not in valid:
        raise ValueError(f"invalid status: {status}")
    with store._connect() as conn:
        conn.execute(
            "UPDATE proposals SET status=?, codex_ready=?, codex_instruction=?, updated_at=? WHERE id=?",
            (
                status,
                1 if (status == "adopted" and codex_instruction) else 0,
                codex_instruction,
                now_iso(),
                proposal_id,
            ),
        )
        row = conn.execute("SELECT * FROM proposals WHERE id=?", (proposal_id,)).fetchone()
    if not row:
        raise ValueError(f"proposal {proposal_id} not found")
    d = dict(row)
    d["candidates"] = json.loads(d.get("candidates_json", "[]"))
    return d


def central_os_payload() -> dict[str, Any]:
    """Read central-os JSON files. Per-file errors are reported, never raised."""
    result: dict[str, Any] = {
        "version": "1.0",
        "data": {},
        "errors": {},
    }
    for filename in CENTRAL_OS_FILES:
        key = filename.replace(".json", "").replace("-", "_")
        path = CENTRAL_OS_DIR / filename
        try:
            with open(path, encoding="utf-8") as f:
                result["data"][key] = json.load(f)
        except FileNotFoundError:
            result["errors"][key] = "file not found"
            result["data"][key] = None
        except json.JSONDecodeError as exc:
            result["errors"][key] = f"json parse error: {exc}"
            result["data"][key] = None
        except Exception as exc:
            result["errors"][key] = f"read error: {exc}"
            result["data"][key] = None

    # proposals.json
    try:
        with open(PROPOSALS_FILE, encoding="utf-8") as f:
            result["data"]["proposals"] = json.load(f)
    except FileNotFoundError:
        result["errors"]["proposals"] = "file not found"
        result["data"]["proposals"] = None
    except json.JSONDecodeError as exc:
        result["errors"]["proposals"] = f"json parse error: {exc}"
        result["data"]["proposals"] = None
    except Exception as exc:
        result["errors"]["proposals"] = f"read error: {exc}"
        result["data"]["proposals"] = None

    # supervisor metadata (existence check only)
    result["data"]["supervisor"] = {
        "exists": SUPERVISOR_DIR.is_dir(),
        "files": {f: (SUPERVISOR_DIR / f).is_file() for f in SUPERVISOR_FILES},
    }

    try:
        with open(GENERATED_CONTENT_FILE, encoding="utf-8") as f:
            result["data"]["generated"] = json.load(f)
    except FileNotFoundError:
        result["errors"]["generated"] = "file not found"
        result["data"]["generated"] = None
    except json.JSONDecodeError as exc:
        result["errors"]["generated"] = f"json parse error: {exc}"
        result["data"]["generated"] = None
    except Exception as exc:
        result["errors"]["generated"] = f"read error: {exc}"
        result["data"]["generated"] = None

    result["data"]["generation"] = {
        "exists": GENERATION_DIR.is_dir(),
        "generatedExists": GENERATED_DIR.is_dir(),
        "files": {f: (GENERATION_DIR / f).is_file() for f in GENERATION_FILES},
        "generatedFiles": {
            "generated-content.json": GENERATED_CONTENT_FILE.is_file(),
        },
    }

    try:
        with open(OBSERVATIONS_FILE, encoding="utf-8") as f:
            result["data"]["observations"] = json.load(f)
    except FileNotFoundError:
        result["errors"]["observations"] = "file not found"
        result["data"]["observations"] = None
    except json.JSONDecodeError as exc:
        result["errors"]["observations"] = f"json parse error: {exc}"
        result["data"]["observations"] = None
    except Exception as exc:
        result["errors"]["observations"] = f"read error: {exc}"
        result["data"]["observations"] = None

    result["data"]["metrics"] = {
        "exists": METRICS_DIR.is_dir(),
        "observationsExists": OBSERVATIONS_DIR.is_dir(),
        "files": {f: (METRICS_DIR / f).is_file() for f in METRICS_FILES},
        "observationFiles": {
            "observations.json": OBSERVATIONS_FILE.is_file(),
        },
    }

    try:
        with open(CYCLE_MAP_FILE, encoding="utf-8") as f:
            result["data"]["cycleMap"] = json.load(f)
    except FileNotFoundError:
        result["errors"]["cycleMap"] = "file not found"
        result["data"]["cycleMap"] = None
    except json.JSONDecodeError as exc:
        result["errors"]["cycleMap"] = f"json parse error: {exc}"
        result["data"]["cycleMap"] = None
    except Exception as exc:
        result["errors"]["cycleMap"] = f"read error: {exc}"
        result["data"]["cycleMap"] = None

    try:
        with open(EVOLUTION_LOG_FILE, encoding="utf-8") as f:
            result["data"]["evolutionLog"] = json.load(f)
    except FileNotFoundError:
        result["errors"]["evolutionLog"] = "file not found"
        result["data"]["evolutionLog"] = None
    except json.JSONDecodeError as exc:
        result["errors"]["evolutionLog"] = f"json parse error: {exc}"
        result["data"]["evolutionLog"] = None
    except Exception as exc:
        result["errors"]["evolutionLog"] = f"read error: {exc}"
        result["data"]["evolutionLog"] = None

    result["data"]["cycle"] = {
        "exists": CYCLE_DIR.is_dir(),
        "files": {f: (CYCLE_DIR / f).is_file() for f in CYCLE_FILES},
    }
    result["data"]["evolution"] = {
        "exists": EVOLUTION_DIR.is_dir(),
        "files": {f: (EVOLUTION_DIR / f).is_file() for f in EVOLUTION_FILES},
    }

    # watch: diff-log.json
    try:
        with open(DIFF_LOG_FILE, encoding="utf-8") as f:
            diff_log = json.load(f)
        result["data"]["diffLog"] = diff_log
        items = diff_log.get("items") or []
        result["data"]["pendingDiffItems"] = [
            i for i in items if i.get("syncStatus") == "pending" or i.get("osUpdated") is False
        ]
    except FileNotFoundError:
        result["errors"]["diffLog"] = "file not found"
        result["data"]["diffLog"] = None
        result["data"]["pendingDiffItems"] = []
    except json.JSONDecodeError as exc:
        result["errors"]["diffLog"] = f"json parse error: {exc}"
        result["data"]["diffLog"] = None
        result["data"]["pendingDiffItems"] = []
    except Exception as exc:
        result["errors"]["diffLog"] = f"read error: {exc}"
        result["data"]["diffLog"] = None
        result["data"]["pendingDiffItems"] = []

    # watch: watch-targets.json
    try:
        with open(WATCH_TARGETS_FILE, encoding="utf-8") as f:
            result["data"]["watchTargets"] = json.load(f)
    except FileNotFoundError:
        result["errors"]["watchTargets"] = "file not found"
        result["data"]["watchTargets"] = None
    except json.JSONDecodeError as exc:
        result["errors"]["watchTargets"] = f"json parse error: {exc}"
        result["data"]["watchTargets"] = None
    except Exception as exc:
        result["errors"]["watchTargets"] = f"read error: {exc}"
        result["data"]["watchTargets"] = None

    # watch system metadata
    result["data"]["watch"] = {
        "exists": WATCH_DIR.is_dir(),
        "generatedExists": WATCH_GENERATED_DIR.is_dir(),
        "historyExists": WATCH_HISTORY_DIR.is_dir(),
    }

    # update-proposals.json
    try:
        with open(UPDATE_PROPOSALS_FILE, encoding="utf-8") as f:
            result["data"]["updateProposals"] = json.load(f)
    except FileNotFoundError:
        result["data"]["updateProposals"] = []
    except json.JSONDecodeError as exc:
        result["errors"]["updateProposals"] = f"json parse error: {exc}"
        result["data"]["updateProposals"] = []
    except Exception as exc:
        result["errors"]["updateProposals"] = f"read error: {exc}"
        result["data"]["updateProposals"] = []

    # planProposals (AI企画官)
    result["data"]["planProposals"] = _read_json_list(PROPOSAL_PLANS_FILE)

    # implementationTasks (AI実装監督)
    result["data"]["implementationTasks"] = _read_json_list(IMPLEMENTATION_TASKS_FILE)

    return result


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
    # allow phase to decrease when conditions drop (natural decay)
    genome["phase"] = next_phase
    if genome["phase"] > previous_phase:
        store.append_log(genome, "phase drift crossed threshold")
        store.append_log(genome, "phase drift 微増", "観測")
        genome["phase_up_event_id"] = max(0, int(genome.get("phase_up_event_id", 0))) + 1


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



def tick_once() -> dict[str, Any]:
    def mutate(genome: dict[str, Any]) -> None:
        if genome["observer_count"] <= 0:
            genome["observer_count"] = 0
            # natural decay when no one is observing
            genome["phase_drift"]         = max(0, genome["phase_drift"] - 2)
            genome["visual_instability"]  = max(0, genome["visual_instability"] - 2)
            genome["audio_instability"]   = max(0, genome["audio_instability"] - 1)
            genome["noise_level"]         = max(0, genome["noise_level"] - 2)
            genome["boundary_pressure"]   = max(0, genome["boundary_pressure"] - 2)
            genome["drift"]               = max(0, genome["drift"] - 1)
            genome["trait_gaze"]          = max(0, genome["trait_gaze"] - 1)
            genome["silent_observation"]  = max(0, genome["silent_observation"] - 1)
            update_phase(genome)
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
        "creature": public_creature_payload(genome),
        "affiliate_panel": panel_signals,
                "affiliate_popup": popup_signals,
    }


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
try:
    videos_dir.mkdir(exist_ok=True)
except OSError:
    pass  # Vercel 読み取り専用ファイルシステム対策
if videos_dir.exists():
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

@app.get("/observer", response_class=HTMLResponse)
async def observer_room(request: Request) -> HTMLResponse:
    return render_template(request, "observer.html")

@app.get("/archive", response_class=HTMLResponse)
async def archive(request: Request) -> HTMLResponse:
    return render_template(request, "archive.html")

@app.get("/archive/logs", response_class=HTMLResponse)
async def archive_logs(request: Request) -> HTMLResponse:
    return render_template(request, "archive-logs.html")

@app.get("/archive/logs/{log_id}", response_class=HTMLResponse)
async def archive_log_detail(request: Request, log_id: str) -> HTMLResponse:
    if log_id not in {f"{index:03d}" for index in range(1, 11)}:
        return HTMLResponse("archive log not found", status_code=404)
    return render_template(request, f"archive-log-{log_id}.html")

@app.get("/signal", response_class=HTMLResponse)
async def signal_room(request: Request) -> HTMLResponse:
    return render_template(request, "signal.html")

@app.get("/daimyojin", response_class=HTMLResponse)
async def daimyojin_room(request: Request) -> HTMLResponse:
    return render_template(request, "daimyojin.html")

@app.get("/hyougi", response_class=HTMLResponse)
async def hyougi_room(request: Request) -> HTMLResponse:
    return render_template(request, "hyougi.html")

@app.get("/gokuraku", response_class=HTMLResponse)
@app.get("/gokurakuiki", response_class=HTMLResponse)
@app.get("/gokugaku", response_class=HTMLResponse)
async def gokuraku_room(request: Request) -> HTMLResponse:
    return render_template(request, "gokuraku.html")

@app.get("/exit", response_class=HTMLResponse)
async def exit_room(request: Request) -> HTMLResponse:
    return render_template(request, "exit.html")

@app.get("/null", response_class=HTMLResponse)
async def null_room(request: Request) -> HTMLResponse:
    return render_template(request, "null.html")

@app.get("/outside", response_class=HTMLResponse)
@app.get("/support", response_class=HTMLResponse)
async def outside_core(request: Request) -> HTMLResponse:
    return render_template(request, "outside.html")

@app.get("/central", response_class=HTMLResponse)
async def central_os_page(request: Request) -> HTMLResponse:
    return render_template(request, "central.html")

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request) -> HTMLResponse:
    return render_template(request, "about.html")

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_page(request: Request) -> HTMLResponse:
    return render_template(request, "privacy-policy.html")

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request) -> HTMLResponse:
    return render_template(request, "contact.html")

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request) -> HTMLResponse:
    return render_template(request, "terms.html")

@app.get("/sitemap", response_class=HTMLResponse)
async def sitemap_page(request: Request) -> HTMLResponse:
    return render_template(request, "sitemap.html")

@app.get("/tiktok", response_class=HTMLResponse)
@app.get("/shorts", response_class=HTMLResponse)
@app.get("/x", response_class=HTMLResponse)
@app.get("/reels", response_class=HTMLResponse)
async def sns_entry_page(request: Request) -> HTMLResponse:
    return render_template(request, "sns-entry.html")

@app.get("/particles", response_class=HTMLResponse)
async def particles_page(request: Request) -> HTMLResponse:
    return render_template(request, "particles.html")

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

@app.get("/api/creature")
async def api_creature() -> JSONResponse:
    return JSONResponse(public_creature_payload(store.get()))

@app.get("/api/radio-line")
async def api_radio_line() -> JSONResponse:
    return JSONResponse(generate_radio_line())

@app.get("/api/videos")
async def api_videos() -> JSONResponse:
    return JSONResponse({"videos": list_signal_videos()})

@app.get("/api/site-config")
async def api_site_config() -> JSONResponse:
    return JSONResponse(site_config_payload(), headers={"Cache-Control": "no-store"})

@app.get("/api/central-os")
async def api_central_os() -> JSONResponse:
    return JSONResponse(central_os_payload(), headers={"Cache-Control": "no-store"})

@app.post("/api/analysis/run")
async def api_run_analysis() -> JSONResponse:
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, run_analysis)
        # also regenerate update-proposals.json
        try:
            up_result = await asyncio.get_event_loop().run_in_executor(None, generate_update_proposals)
            result["update_proposals"] = up_result
        except Exception as up_exc:
            result["update_proposals_error"] = str(up_exc)
        return JSONResponse({"ok": True, **result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

@app.post("/api/update-proposals/run")
async def api_run_update_proposals() -> JSONResponse:
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, generate_update_proposals)
        return JSONResponse({"ok": True, **result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

@app.post("/api/update-proposals/{proposal_id}/status")
async def api_update_proposal_status(proposal_id: str, body: dict = Body(...)) -> JSONResponse:
    """Update status of an update-proposal by id."""
    try:
        new_status = str(body.get("status", "pending"))
        if new_status not in {"pending", "approved", "hold", "rejected"}:
            return JSONResponse({"ok": False, "error": f"invalid status: {new_status}"}, status_code=400)
        try:
            with open(UPDATE_PROPOSALS_FILE, encoding="utf-8") as f:
                proposals = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            proposals = []
        found = False
        for p in proposals:
            if p.get("id") == proposal_id:
                p["status"] = new_status
                found = True
                break
        if not found:
            return JSONResponse({"ok": False, "error": f"proposal {proposal_id} not found"}, status_code=404)
        with open(UPDATE_PROPOSALS_FILE, "w", encoding="utf-8") as f:
            json.dump(proposals, f, ensure_ascii=False, indent=2)
        return JSONResponse({"ok": True, "id": proposal_id, "status": new_status})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

@app.get("/api/test-ai")
async def api_test_ai() -> JSONResponse:
    """AI接続テスト用エンドポイント（デバッグ用）"""
    import os as _os
    from urllib.request import Request as _Req, urlopen as _open

    results = {}

    # Groq test
    groq_key = _os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        payload = json.dumps({"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}).encode()
        try:
            req = _Req("https://api.groq.com/openai/v1/chat/completions", data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key}", "User-Agent": "Mozilla/5.0"}, method="POST")
            with _open(req, timeout=10) as r:
                d = json.loads(r.read())
            results["groq"] = {"ok": True, "reply": d["choices"][0]["message"]["content"]}
        except Exception as e:
            results["groq"] = {"ok": False, "error": str(e)}
    else:
        results["groq"] = {"ok": False, "error": "no key"}

    # OpenRouter test
    or_key = _os.environ.get("OPENROUTER_API_KEY", "")
    if or_key:
        for model in ["google/gemma-4-26b-a4b-it:free", "google/gemma-4-31b-it:free", "moonshotai/kimi-k2.6:free"]:
            payload = json.dumps({"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}).encode()
            try:
                req = _Req("https://openrouter.ai/api/v1/chat/completions", data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {or_key}", "HTTP-Referer": "https://www.void-kyoukai.net"}, method="POST")
                with _open(req, timeout=15) as r:
                    d = json.loads(r.read())
                results["openrouter"] = {"ok": True, "model": model, "reply": d["choices"][0]["message"]["content"]}
                break
            except Exception as e:
                results[f"openrouter_{model}"] = {"ok": False, "error": str(e)[:80]}
    else:
        results["openrouter"] = {"ok": False, "error": "no key"}

    return JSONResponse(results)


@app.post("/api/plan-proposals/run")
async def api_run_plan_proposals() -> JSONResponse:
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, run_ai_planner)
        return JSONResponse({"ok": True, **result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.post("/api/plan-proposals/{plan_id}/status")
async def api_update_plan_status(plan_id: str, body: dict = Body(...)) -> JSONResponse:
    try:
        new_status = str(body.get("status", "pending"))
        updated = update_plan_status(plan_id, new_status)
        return JSONResponse({"ok": True, "plan": updated})
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.post("/api/implementation-tasks/run")
async def api_run_implementation_tasks() -> JSONResponse:
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, run_ai_executor)
        return JSONResponse({"ok": True, **result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.post("/api/implementation-tasks/{task_id}/status")
async def api_update_task_status(task_id: str, body: dict = Body(...)) -> JSONResponse:
    try:
        new_status = str(body.get("status", "pending"))
        updated = update_task_status(task_id, new_status)
        return JSONResponse({"ok": True, "task": updated})
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.get("/api/proposals")
async def api_get_proposals(status: str | None = None) -> JSONResponse:
    try:
        proposals = get_proposals(status)
        return JSONResponse({"ok": True, "proposals": proposals})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

@app.post("/api/proposals/{proposal_id}/status")
async def api_update_proposal(proposal_id: int, body: dict = Body(...)) -> JSONResponse:
    try:
        updated = update_proposal_status(
            proposal_id,
            str(body.get("status", "pending")),
            body.get("codex_instruction"),
        )
        return JSONResponse({"ok": True, "proposal": updated})
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

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
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
