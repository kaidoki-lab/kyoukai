# creature_generator.py — 外部LLMなしの制約付きCreature Generator AI
# 修正点:
#   - body_pool を BODY_PLANS のキーに統一（問題①）
#   - describe() でオルガン・コアをID→名前変換（問題③）
#   - config / utils への依存を除去、保存先を引数で指定可能に

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .genome_defs import CORES, ORGANS, SHELLS

# デフォルト保存先
DEFAULT_GENERATED_DIR = Path(__file__).resolve().parent / "genome_data" / "generated"

BRANCH_CORE: dict[str, list[str]] = {
    "kind":       ["C1", "C2"],
    "aggression": ["C4"],
    "attention":  ["C3"],
    "talk":       ["C1", "C3"],
    "chaos":      ["C5"],
    "none":       ["C2"],
    "legend":     ["C1", "C3", "C5"],
    "myth":       ["C5", "C4"],
}

MUTATION_BY_VARIANT: dict[str, str] = {
    "normal":   "M0",
    "malice":   "M1",
    "unstable": "M2",
    "complex":  "M3",
}

NAME_A = [
    "Glass", "Void", "Coral", "Bone", "Signal", "Bloom", "Maw",
    "Halo", "Dream", "Fracture", "Moon", "Seed", "Black", "Abyss",
    "Wandering", "Static", "Hollow", "Red", "Silent", "Mirage",
]
NAME_B = [
    "Parasite", "Oracle", "Watcher", "Leviathan", "Saint", "Shepherd",
    "Tyrant", "Archive", "Hunter", "Child", "Cathedral", "Organism",
    "Larva", "Crown", "Moth", "Root", "Tongue", "Signal",
]

# -------------------------------------------------------------------
# 通常時の body_pool（すべて BODY_PLANS のキー）
# -------------------------------------------------------------------
_BODY_POOL_NORMAL: list[str] = [
    "larva_soft",       # 旧: "worm"
    "spiked_predator",  # 旧: "spiked"
    "tentacled",        # 旧: "radial"
    "rift_serpent",     # 旧: "serpentine"
    "raptor",           # 旧: "four_legged"
    "many_eyed",        # 旧: "many_eyed" (一致していた唯一のキー)
    "cathedral_throat", # 旧: "cathedral"
    "void_leviathan",   # 旧: "leviathan"
]

# Myth / Forbidden 追加分
_BODY_POOL_MYTH: list[str] = [
    "amorphous",        # 旧: "eldritch"
    "eye_cathedral",    # 旧: "asymmetric_abyssal"
    "halo_titan",       # 旧: "mythic_halo"
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _save_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


class CreatureGeneratorAI:
    """
    外部LLMなしで動く、制約付きCreature Generator AI。
    将来的にOllamaへ差し替え可能。

    Args:
        generated_dir: 生成した生体データの保存先フォルダ（省略時はデフォルト）
    """

    def __init__(self, generated_dir: Path | str | None = None) -> None:
        self.generated_dir = Path(generated_dir) if generated_dir else DEFAULT_GENERATED_DIR

    def generate(
        self,
        branch: str = "none",
        variant: str = "normal",
        rarity: str = "Common",
        danger: int = 0,
        seed_text: str = "",
    ) -> dict[str, Any]:
        """生体データを生成して保存し、辞書を返す。"""
        seed = f"{branch}:{variant}:{rarity}:{danger}:{seed_text}:{_now_iso()}"
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
        rnd = random.Random(digest)

        rarity = self.normalize_rarity(rarity)
        branch = branch if branch in BRANCH_CORE else "none"
        core = rnd.choice(BRANCH_CORE.get(branch, ["C2"]))

        organ_pool = list(ORGANS.keys())
        organ_count = 2
        if rarity in ("Rare", "Legend"):
            organ_count = 3
        if rarity in ("Myth", "Forbidden"):
            organ_count = 4

        organs = rnd.sample(organ_pool, k=min(organ_count, len(organ_pool)))
        shell = rnd.choice(list(SHELLS.keys()))

        # ── 問題① 修正: BODY_PLANS のキーを使用 ──────────────────────
        body_pool = list(_BODY_POOL_NORMAL)
        if rarity in ("Myth", "Forbidden"):
            body_pool += _BODY_POOL_MYTH
        body_plan = rnd.choice(body_pool)
        silhouette = body_plan
        # ────────────────────────────────────────────────────────────────

        mutation = MUTATION_BY_VARIANT.get(variant, "M0")
        if rarity in ("Myth", "Forbidden"):
            mutation = rnd.choice(["M1", "M2", "M3"])
        if danger >= 20:
            mutation = rnd.choice(["M1", "M2"])

        name = f"{rnd.choice(NAME_A)} {rnd.choice(NAME_B)}"
        if rarity == "Forbidden":
            name = "Forbidden " + name

        data: dict[str, Any] = {
            "species_id": self.make_species_id(name, digest),
            "name": name,
            "genome": {
                "core":         core,
                "organs":       organs,
                "shell":        shell,
                "mutation":     mutation,
                "body_plan":    body_plan,
                "silhouette":   silhouette,
                "ovoid_allowed": False,
            },
            "branch":     branch,
            "variant":    variant,
            "rarity":     rarity,
            "danger":     danger,
            "description": self.describe(name, core, organs, shell, mutation, rarity),
            "created_at": _now_iso(),
            "type":       "unknown_species",
        }
        self.save(data)
        return data

    def normalize_rarity(self, rarity: str) -> str:
        table = {
            "common":    "Common",
            "rare":      "Rare",
            "legend":    "Legend",
            "myth":      "Myth",
            "forbidden": "Forbidden",
        }
        return table.get((rarity or "Common").strip().lower(), "Common")

    def make_species_id(self, name: str, digest: str) -> str:
        return "U-" + hashlib.sha1((name + digest).encode("utf-8")).hexdigest()[:8].upper()

    def describe(
        self,
        name: str,
        core: str,
        organs: list[str],
        shell: str,
        mutation: str,
        rarity: str,
    ) -> str:
        # ── 問題③ 修正: ID → 表示名に変換 ────────────────────────────
        core_name   = CORES.get(core, {}).get("name", core)
        organ_names = [ORGANS.get(oid, oid) for oid in organs]
        organ_text  = "、".join(organ_names)
        shell_name  = shell   # SHELLS は str なので直接取得済み
        # ────────────────────────────────────────────────────────────────
        return (
            f"{name} は {core_name} を核に、{organ_text} を持つ未登録生体。"
            f"{shell}/{mutation} の影響が観測されている。分類は {rarity}。"
        )

    def save(self, data: dict[str, Any]) -> None:
        p = self.generated_dir / f"{data['species_id']}.json"
        _save_json_atomic(p, data)
