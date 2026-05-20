# genome_bridge.py — evo_genome ↔ creature genome ブリッジ（問題②）
#
# AGGRO / CALM / CURIOSITY / DISTORTION（視聴者コマンド由来の4パラメータ）を
# CreatureGeneratorAI.generate() の branch / variant に変換する。
#
# 優先順位: AGGRO > CURIOSITY > DISTORTION > CALM
# （複数が同値の場合、この順で先に定義された方が優先される）

from __future__ import annotations

from typing import Any

# ── 閾値：この値以上を「高い」とみなしてブリッジ処理を行う ──────────
ACTIVE_THRESHOLD = 20  # 0〜100 スケール
# ───────────────────────────────────────────────────────────────────

# パラメータ → (branch, variant) のマッピング定義
# リストの順序が優先順位（先が高優先）
_PARAM_MAP: list[tuple[str, str, str]] = [
    # (genome_key, branch,       variant)
    ("AGGRO",      "aggression", "malice"),
    ("CURIOSITY",  "attention",  "normal"),
    ("DISTORTION", "chaos",      "unstable"),
    ("CALM",       "kind",       "normal"),
]


def genome_to_branch_variant(
    genome: dict[str, Any],
    threshold: int = ACTIVE_THRESHOLD,
) -> tuple[str, str]:
    """
    evo genome の4パラメータから (branch, variant) を決定する。

    Args:
        genome:    {"AGGRO": int, "CALM": int, "CURIOSITY": int, "DISTORTION": int, ...}
        threshold: この値以上を「アクティブ」とみなす（デフォルト 20）

    Returns:
        (branch, variant) のタプル。
        全パラメータが threshold 未満のときは ("none", "normal")。

    Priority:
        AGGRO > CURIOSITY > DISTORTION > CALM
        同スコアの場合は上記優先順位が適用される。
    """
    values = {key: int(genome.get(key, 0)) for key, _, _ in _PARAM_MAP}

    # 有効なパラメータ（threshold 以上）を優先順位順にフィルタ
    active = [
        (key, branch, variant, values[key])
        for key, branch, variant in _PARAM_MAP
        if values[key] >= threshold
    ]

    if not active:
        return ("none", "normal")

    # スコアが最大のものを選ぶ（同スコア時はリスト順＝優先順位で決まる）
        # Python の max は stable なので、同値の場合は最初の要素が残る
    best = max(active, key=lambda x: x[3])
    _, branch, variant, _ = best
    return (branch, variant)


def get_creature_params(
    genome: dict[str, Any],
    threshold: int = ACTIVE_THRESHOLD,
) -> dict[str, Any]:
    """
    evo genome から CreatureGeneratorAI.generate() に渡す引数辞書を生成する。

    使用例::

        from genome_system.evo_genome import load_genome
        from genome_system.genome_bridge import get_creature_params
        from genome_system.creature_generator import CreatureGeneratorAI

        evo = load_genome()
        params = get_creature_params(evo)
        ai = CreatureGeneratorAI()
        creature = ai.generate(**params)

    Args:
        genome:    evo_genome の辞書
        threshold: アクティブ判定の閾値

    Returns:
        {"branch": str, "variant": str, "danger": int} を含む辞書
    """
    branch, variant = genome_to_branch_variant(genome, threshold)

    # danger は AGGRO と DISTORTION の合計を 0〜40 にマッピング
    aggro      = int(genome.get("AGGRO",      0))
    distortion = int(genome.get("DISTORTION", 0))
    danger = min(40, (aggro + distortion) // 5)

    return {
        "branch":  branch,
        "variant": variant,
        "danger":  danger,
    }
