# codex-readonly-rules.md
# Codex 読み取り専用接続ルール

PHASE 2 完了後、Codex は central-os を「読み取り専用の正本」として扱う。

---

## 基本方針

central-os は Codex にとっての「設計図」であり「辞書」である。

Codex は central-os を参照して実装を行うが、
central-os 自体を直接編集してはならない。

---

## Codex がしてよいこと

| 行為 | 詳細 |
|---|---|
| central-os を参照する | rooms.json / graph/ / schema/ を読み取り専用で参照する |
| 部屋名を正として扱う | rooms.json の `name` フィールドを部屋の正式名称として使用する |
| route辞書を参照する | rooms.json の `route` フィールドを正式ルートとして参照する |
| graph/ の導線を参照する | room-links.json および各 flow.md を実装の根拠として使用する |
| schema/ を参照する | フィールド定義・型定義の確認に使用する |
| 実装対象ページの仕様確認に使う | どの部屋に何の機能が必要かを central-os から読み取る |

---

## Codex がしてはいけないこと

| 禁止行為 | 理由 |
|---|---|
| central-os を勝手に編集する | central-os はユーザーの承認なく変更されてはならない |
| route を勝手に追加・変更する | route の確定はユーザー承認が必要 |
| 未確定route を実装する | 未確定routeのページ・リンクを作ってはならない |
| graph/ と異なる導線を作る | graph/ が導線の正本であり、乖離すると世界観が崩れる |
| 収益導線を勝手に増やす | 収益設計はユーザー判断が必要 |
| git add . を実行する | 全変更の一括ステージは禁止 |
| commit する | ユーザー確認前のコミットは禁止 |
| PRを作成する | ユーザー確認前のPR作成は禁止 |

---

## 参照優先順位

複数の定義が存在する場合、以下の順で優先する。

```
1. ユーザーの直接指示（最優先）
2. rooms.json の値
3. connection/ のルール文書
4. schema/ の定義
5. graph/ の導線定義
```

---

## 接続タイミング

- PHASE 2 完了判定後に接続を開始する
- phase-2-checklist.md の全必須項目が ✅ になっていること
- phase-2-review.md の判定が GO または REVISE（REVISE条件解消後）であること
