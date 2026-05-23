# phase-3-entry-criteria.md
# PHASE 3「central UI」進行条件

---

## PHASE 3 の概要

`/central` ページを実装し、
central-os 内の JSON データを画面で参照・閲覧できるようにする。

PHASE 3 は「central-os を可視化する」段階である。
データ構造の変更ではなく、読み取りUIの実装が中心となる。

---

## PHASE 3 に進んでよい条件

以下をすべて満たした場合、PHASE 3 へ進める。

| 条件 | 確認方法 |
|---|---|
| central-os のJSON構造が安定している | 全JSONが valid・version統一・items形式統一 |
| route方針が固定されている | route-lock-rules.md が存在し、確定/未確定の基準が明記されている |
| graph/ の導線が整理されている | room-links.json が valid・各 flow.md が矛盾なく記述されている |
| Codexが参照してよい範囲が定義されている | codex-readonly-rules.md が存在する |
| 未確定routeをUI化しない方針がある | route-lock-rules.md に「未確定routeはリンク化しない」が明記されている |
| central UIで表示する項目が明確になっている | 下記「表示項目」参照 |

---

## central UI で表示する項目（PHASE 3 スコープ）

### 必須表示

- 部屋一覧（rooms.json）：name / route / status / priority
- 月間目標（monthly-goal.json）：title / successCondition
- 収益導線一覧（monetization.json）：room / type / status

### 任意表示（PHASE 3 後半以降）

- アイデア一覧（ideas.json）
- SNS導線一覧（sns-routes.json）
- 導線グラフ（graph/room-links.json の可視化）

### 表示しない（PHASE 3 では扱わない）

- Codex作業メモ（codex-tasks.md）：管理用・内部専用
- schema/ の内容：辞書・定義ファイル
- connection/ の内容：ルール文書

---

## PHASE 3 に進まない条件

以下のいずれかに該当する場合は PHASE 3 へ進めない。

| 条件 | 理由 |
|---|---|
| 未確定routeが多すぎる（8件以上） | UI化の前提が崩れる |
| graph/ に矛盾がある | 実装時に導線が崩れる |
| 収益導線が広告的に見えすぎる | 世界観を破壊する |
| Codex接続ルールが定義されていない | PHASE 3 以降の作業で競合が生じる |
| central-os がまだメモ状態 | UI化に耐えるデータ密度がない |

---

## 現在の判定

→ **REVISE**

理由：

- 全条件の構造的な準備は整っている
- 未確定routeが5件残っているが、UI化方針（リンク化しない）が明記されているため進行可能
- route-lock-rules.md と codex-readonly-rules.md の存在を最終確認後に GO へ移行できる
