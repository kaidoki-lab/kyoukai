from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"automation config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid automation config: {config_path}") from exc
    if not isinstance(config, dict):
        raise ValueError("automation config must be a JSON object")
    if not isinstance(config.get("codex"), dict):
        raise ValueError("automation config requires codex settings")
    if not isinstance(config.get("daimyojin"), dict):
        raise ValueError("automation config requires daimyojin settings")
    return config


def repository_file_info(relative_path: str) -> dict[str, Any]:
    path = (BASE_DIR / relative_path).resolve()
    try:
        path.relative_to(BASE_DIR)
    except ValueError as exc:
        raise ValueError(f"source file is outside repository: {relative_path}") from exc
    if not path.is_file():
        return {
            "path": relative_path,
            "exists": False,
            "size": 0,
            "sha256": "",
        }
    content = path.read_bytes()
    return {
        "path": relative_path,
        "exists": True,
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest()[:16],
    }


def build_codex_context(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    started = time.perf_counter()
    config = load_config(path)
    codex = config["codex"]
    sources = [
        repository_file_info(str(relative_path))
        for relative_path in codex.get("sourceFiles", [])
    ]
    return {
        "automation_version": str(config.get("version", "unknown")),
        "codex_title": str(codex.get("title", "CODEX AUTOMATION")),
        "codex_description": str(codex.get("description", "")),
        "codex_targets": [str(item) for item in codex.get("targetPages", [])],
        "codex_pipeline": [str(item) for item in codex.get("pipeline", [])],
        "codex_sources": sources,
        "codex_ready": bool(sources) and all(item["exists"] for item in sources),
        "generation_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def build_daimyojin_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config = load_config(path)
    settings = config["daimyojin"]
    statuses = [str(item) for item in settings.get("statuses", []) if str(item)]
    if not statuses:
        raise ValueError("daimyojin statuses must not be empty")

    def positive_int(name: str, default: int) -> int:
        value = int(settings.get(name, default))
        if value < 0:
            raise ValueError(f"{name} must be zero or greater")
        return value

    return {
        "version": str(config.get("version", "unknown")),
        "statuses": statuses,
        "initialDelayMs": positive_int("initialDelayMs", 260),
        "receiveDelayMinMs": positive_int("receiveDelayMinMs", 680),
        "receiveDelayRangeMs": positive_int("receiveDelayRangeMs", 360),
        "desktopTypeDelayMs": positive_int("desktopTypeDelayMs", 54),
        "mobileTypeDelayMs": positive_int("mobileTypeDelayMs", 64),
        "buttonUnlockDelayMs": positive_int("buttonUnlockDelayMs", 1000),
    }
