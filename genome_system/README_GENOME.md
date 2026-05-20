# genome_system — AIVTuber ゲノムシステム

視聴者コマンドで変化する感情パラメータ（evo genome）と、
それに基づいて生体データを生成するシステム（creature generator）のスタンドアロンパッケージです。

---

## ファイル構成

```
genome_system/
├── __init__.py             パッケージエントリポイント（公開 API 一覧）
├── genome_defs.py          ゲノム定義データ（コア・オルガン・シェル・変異・体型）
├── creature_generator.py   生体データ生成 AI（外部 LLM 不要）
├── evo_genome.py           視聴者コマンド由来の4パラメータ管理
├── genome_bridge.py        evo_genome → creature genome 変換ブリッジ
└── evo_genome.json         evo genome の初期値（evo_data/ に移動して使用）
```

---

## インストール・配置方法

このフォルダをそのままプロジェクト内に配置し、
パッケージとして import するだけで使用できます。

```
your_project/
├── genome_system/   ← このフォルダをコピー
└── main.py
```

外部ライブラリへの依存は **なし**（標準ライブラリのみ）。

---

## 基本的な使い方

### 1. 生体をランダム生成する

```python
from genome_system import CreatureGeneratorAI

ai = CreatureGeneratorAI(generated_dir="./output/creatures")
creature = ai.generate(branch="kind", variant="normal", rarity="Common")
print(creature["description"])
# → Moon Watcher は Seed Core を核に、Antlers、Wings を持つ未登録生体。...
```

### 2. 視聴者コマンドで evo genome を更新する

```python
from genome_system import record_genome

genome = record_genome("たたく")   # AGGRO +2, DISTORTION +1
genome = record_genome("なでる")   # CALM +2
print(genome)
# → {"AGGRO": 2, "CALM": 2, "CURIOSITY": 0, "DISTORTION": 1, "last_update": "..."}
```

### 3. evo genome → creature generator のブリッジ（重要）

```python
from genome_system import load_genome, get_creature_params, CreatureGeneratorAI

evo     = load_genome()
params  = get_creature_params(evo)   # branch / variant / danger を自動決定
ai      = CreatureGeneratorAI()
creature = ai.generate(**params)
print(f"branch={params['branch']}, variant={params['variant']}")
```

---

## ブリッジ変換ロジック（genome_bridge.py）

| パラメータ高  | branch       | variant    | 優先順位 |
|-------------|-------------|-----------|---------|
| AGGRO       | aggression  | malice    | 1（最高）|
| CURIOSITY   | attention   | normal    | 2       |
| DISTORTION  | chaos       | unstable  | 3       |
| CALM        | kind        | normal    | 4       |
| すべて低い  | none        | normal    | —       |

- **閾値**（デフォルト `ACTIVE_THRESHOLD = 20`）以上を「高い」と判定。
- 複数が閾値を超えた場合は最大値のパラメータを優先。同値の場合は上表の優先順位。
- `danger` は `(AGGRO + DISTORTION) // 5` で算出（上限 40）。

---

## 保存パス設定

### evo genome の保存先

デフォルト: `genome_system/evo_data/evo_genome.json`

```python
from genome_system import load_genome, save_genome

genome = load_genome(genome_path="/custom/path/my_genome.json")
save_genome(genome,   genome_path="/custom/path/my_genome.json")
```

### 生体データの保存先

デフォルト: `genome_system/genome_data/generated/`

```python
from genome_system import CreatureGeneratorAI
ai = CreatureGeneratorAI(generated_dir="/custom/path/creatures")
```

---

## 修正履歴（v2）

| 問題 | 内容 | 対応ファイル |
|------|------|-------------|
| ① body_plan 名の不一致 | `creature_generator.py` の `body_pool` が `BODY_PLANS` のキーと一致していなかった | `creature_generator.py` |
| ② evo ↔ creature ブリッジ欠如 | 4パラメータから branch/variant へのマッピングが存在しなかった | `genome_bridge.py`（新規） |
| ③ describe() の ID 出力 | オルガン・コアの ID がそのまま文章に埋め込まれていた | `creature_generator.py` |
| ④ 外部依存の除去 | `config.py` / `utils.py` 依存を除去し、デフォルトパス引数化 | `evo_genome.py`, `creature_generator.py` |
