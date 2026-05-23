# sns-schema.md
# sns-routes.json 項目定義

KYOUKAI内部辞書 — sns-routes.json フィールド定義

---

## 対象ファイル

`central-os/sns-routes.json`

---

## このファイルの目的

KYOUKAIの外部SNS導線を一元管理する。

どのプラットフォームに、どの部屋を起点としたコンテンツを展開するかを記録し、
SNS経由の流入・認知拡大の管理に使う。

---

## フィールド定義

| フィールド | 型 | 意味 | 備考 |
|---|---|---|---|
| id | string | SNS導線の一意識別子 | `sns_01` 形式。追加時は連番。 |
| platform | string | 投稿・展開するSNSプラットフォーム | 定義済み値のみ使用（下記参照）。 |
| title | string | このSNS導線の名称・企画タイトル | 管理用の識別名。公開タイトルと異なってもよい。 |
| targetRoom | string | 起点となる部屋の name | rooms.json の name と一致させる。KYOUKAI全体を対象とする場合は `"全体"` とする。 |
| url | string | 実際のSNSアカウントURL・投稿URL | 未開設・未確定の場合は空文字 `""` とする。推測URLは記載しない。 |
| status | string | この導線の現在の状態 | rooms.json と同じ status 定義を使用。 |
| notes | string | 補足情報・企画メモ・運用方針 | 自由記述。 |

---

## platform 定義済み値

| 値 | 意味 |
|---|---|
| YouTube | YouTube（長尺・ショート含む） |
| TikTok | TikTok |
| X (Twitter) | X（旧Twitter） |
| Instagram | Instagram |
| Bluesky | Bluesky |

---

## url の運用ルール

- アカウント開設前・URL未確定の場合は必ず `""` とする
- 推測・仮のURLを記載してはならない
- URL確定後に更新する

---

## targetRoom の運用ルール

- rooms.json の `name` フィールドの値と完全一致させる
- 複数部屋に跨る場合は代表となる起点部屋を記載する
- 特定の部屋に依存しないSNS活動は `"全体"` とする
