# evo_genome.py — 視聴者コマンドで変化する4パラメータ管理
# 修正点:
#   - GENOME_PATH をモジュール起点の相対パスに変更（parent.parent 依存を除去）
#   - load_genome / save_genome / record_genome にオプションの genome_path 引数を追加

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# デフォルト保存先: パッケージと同じ階層の evo_data/ フォルダ
DEFAULT_GENOME_PATH = Path(__file__).resolve().parent / "evo_data" / "evo_genome.json"

MAX_VALUE = 100

DEFAULT_GENOME: dict[str, Any] = {
    "AGGRO":      0,
    "CALM":       0,
    "CURIOSITY":  0,
    "DISTORTION": 0,
    "last_update": "",
}

COMMAND_DELTAS: dict[str, dict[str, int]] = {
    "たたく":       {"AGGRO": 2, "DISTORTION": 1},
    "なでる":       {"CALM": 2},
    "みつめる":     {"CURIOSITY": 2},
    "よぶ":         {"CURIOSITY": 1},
    "話しかける":   {"CURIOSITY": 1, "CALM": 1},
    "はなしかける": {"CURIOSITY": 1, "CALM": 1},
    "遠ざける":     {"DISTORTION": 1},
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp_value(value: Any) -> int:
    try:
        n = int(float(value))
    except Exception:
        n = 0
    return max(0, min(MAX_VALUE, n))


def normalize_genome(data: Any) -> dict[str, Any]:
    genome = dict(DEFAULT_GENOME)
    if isinstance(data, dict):
        for key in ("AGGRO", "CALM", "CURIOSITY", "DISTORTION"):
            genome[key] = _clamp_value(data.get(key, 0))
        genome["last_update"] = str(data.get("last_update") or "")
    return genome


def load_genome(genome_path: Path | str | None = None) -> dict[str, Any]:
    """evo genome を読み込む。genome_path 省略時はデフォルトパスを使用。"""
    path = Path(genome_path) if genome_path else DEFAULT_GENOME_PATH
    try:
        if not path.exists():
            genome = normalize_genome({})
            save_genome(genome, path)
            return genome
        with path.open("r", encoding="utf-8") as f:
            return normalize_genome(json.load(f))
    except Exception:
        genome = normalize_genome({})
        try:
            save_genome(genome, path)
        except Exception:
            pass
        return genome


def save_genome(genome: dict[str, Any], genome_path: Path | str | None = None) -> None:
    """evo genome を保存する。genome_path 省略時はデフォルトパスを使用。"""
    path = Path(genome_path) if genome_path else DEFAULT_GENOME_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data = normalize_genome(genome)
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def record_genome(command: str, genome_path: Path | str | None = None) -> dict[str, Any]:
    """視聴者コマンドを受け取り、genome を更新して保存・返却する。"""
    genome = load_genome(genome_path)
    deltas = COMMAND_DELTAS.get(str(command or ""), {})
    if not deltas:
        return genome
    for key, delta in deltas.items():
        genome[key] = _clamp_value(genome.get(key, 0) + int(delta))
    genome["last_update"] = _now_iso()
    save_genome(genome, genome_path)
    return genome
