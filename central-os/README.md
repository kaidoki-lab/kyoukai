# 境界セントラルOS

## 目的

KYOUKAIの部屋・導線・収益・SNS・AIネタ・作業メモを一元管理するデータ基盤。

画面実装より先に、データ構造を安定させることを優先する。

---

## 管理対象

| ファイル | 内容 |
|---|---|
| rooms.json | KYOUKAI内の部屋情報 |
| ideas.json | AI生成ネタ・企画案 |
| monthly-goal.json | 今月の目標 |
| monetization.json | 収益導線 |
| sns-routes.json | YouTube / TikTok / SNS導線 |
| codex-tasks.md | Codexへ渡す作業メモ |

---

## 今後の方針

将来的に `/central` ページから各JSONを読み込む予定。

そのため、画面依存ではなくデータ管理優先で構造を整理している。

---

## KYOUKAIとの関係

central-os/ は KYOUKAI 本体（テンプレート・静的ファイル・APIサーバー）とは独立したデータ管理レイヤーである。

KYOUKAI 本体のコードには干渉しない。
central-os/ は「KYOUKAI の状態・方針・導線を記録・整理するための補助フォルダ」として機能する。

---

## v1段階での役割

- JSON構造の確立
- 初期部屋データの整理
- 収益・SNS導線のリスト化
- Codex作業メモの蓄積

v1では保存機能・編集機能・自動生成機能は持たない。
固定データとしての構造安定化が目標。
