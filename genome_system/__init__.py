"""
genome_system — AIVTuber ゲノムシステム スタンドアロンパッケージ

ファイル構成:
    genome_defs.py      コア / オルガン / シェル / 変異 / 伝説ゲノム / 体型 定義
    creature_generator.py  生体データ生成 AI（外部LLM不要）
    evo_genome.py       視聴者コマンド由来の4パラメータ管理
    genome_bridge.py    evo_genome ↔ creature genome 変換ブリッジ

基本的な使い方::

    from genome_system import CreatureGeneratorAI, load_genome, get_creature_params

    evo     = load_genome()
    params  = get_creature_params(evo)
    ai      = CreatureGeneratorAI()
    creature = ai.generate(**params)
    print(creature["description"])
"""

from .genome_defs import (
    BODY_PLANS,
    CORES,
    LEGEND_GENOMES,
    MUTATIONS,
    ORGANS,
    SHELLS,
)
from .creature_generator import CreatureGeneratorAI
from .evo_genome import (
    DEFAULT_GENOME,
    COMMAND_DELTAS,
    load_genome,
    save_genome,
    record_genome,
    normalize_genome,
)
from .genome_bridge import (
    genome_to_branch_variant,
    get_creature_params,
    ACTIVE_THRESHOLD,
)

__all__ = [
    # genome_defs
    "CORES",
    "ORGANS",
    "SHELLS",
    "MUTATIONS",
    "LEGEND_GENOMES",
    "BODY_PLANS",
    # creature_generator
    "CreatureGeneratorAI",
    # evo_genome
    "DEFAULT_GENOME",
    "COMMAND_DELTAS",
    "load_genome",
    "save_genome",
    "record_genome",
    "normalize_genome",
    # genome_bridge
    "genome_to_branch_variant",
    "get_creature_params",
    "ACTIVE_THRESHOLD",
]
