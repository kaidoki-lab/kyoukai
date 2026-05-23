# proposal-schema.md
# AI提案データ構造定義

KYOUKAI内部辞書 — proposals.json フィールド定義

---

## 対象ファイル

`central-os/proposals/proposals.json`

---

## 基本構造

```json
{
  "version": "1.0",
  "items": [
    {
      "id": "prop_01",
      "title": "提案タイトル",
      "type": "room-update",
      "targetRoom": "外部接続",
      "targetRoute": "/outside",
      "priority": "高",
      "reason": "なぜこの提案が必要か",
      "expectedEffect": "採用した場合の期待効果",
      "risk": "リスク・注意点",
      "codexReady": false,
      "status": "提案"
    }
  ]
}
```

---

## フィールド定義

| フィールド | 型 | 意味 | 備考 |
|---|---|---|---|
| id | string | 提案の一意識別子 | `prop_01` 形式。追加時は連番。 |
| title | string | 提案のタイトル | 1行で概要がわかるように記述。 |
| type | string | 提案の種別 | 定義済み値のみ使用（下記参照）。 |
| targetRoom | string | 対象部屋の name | rooms.json の name と一致させる。サイト全体対象の場合は `"全体"` とする。 |
| targetRoute | string | 対象ルートパス | 確定routeのみ記述。未確定routeの場合は `"未確定"` とする。 |
| priority | string | 優先度 | 定義済み値のみ使用（下記参照）。 |
| reason | string | この提案が必要な理由 | 現状の問題・課題を具体的に記述する。 |
| expectedEffect | string | 採用した場合の期待効果 | 評価軸（回遊率・収益等）に紐づけて記述。 |
| risk | string | リスク・注意点 | 実装時の危険・競合・副作用を必ず記述する。 |
| codexReady | boolean | Codexへ即渡せる状態か | supervisor-rules.md の判定基準を満たす場合のみ `true`。 |
| status | string | 提案の現在の状態 | 定義済み値のみ使用（下記参照）。 |

---

## type 定義済み値

| 値 | 意味 |
|---|---|
| room-update | 特定の部屋の演出・テキスト・UIの改善 |
| sns | SNS投稿案・SNS導線の改善 |
| monetization | 収益導線の改善・追加 |
| observer | 観測・逆観測に関する演出改善 |
| flow | 部屋間の導線・回遊構造の改善 |
| design | デザイン・ビジュアル・雰囲気の改善 |
| safety | 安全性・パフォーマンス・バグ対応 |

---

## priority 定義済み値

| 値 | 使いどころ |
|---|---|
| 最優先 | 今すぐ対応が必要 |
| 高 | 今週中に検討したい |
| 中 | 今月中に検討 |
| 低 | いつか対応 |
| 保留 | 判断待ち・中断 |

---

## status 定義済み値

| 値 | 意味 |
|---|---|
| 提案 | AI監督から生成された提案（未確認） |
| 確認待ち | ユーザーが確認中 |
| 採用 | 実装を進めることが決定した |
| 却下 | 今回は実装しないことが決定した |
| 保留 | 判断を一時停止 |

---

## codexReady の運用ルール

- `codexReady: false` が初期値。条件を満たした場合のみ `true` にする
- `codexReady: true` でも、ユーザーが「採用」しない限りCodexへ渡さない
- status が `採用` かつ `codexReady: true` の提案のみ実装候補になる
