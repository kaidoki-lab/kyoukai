# monetization-schema.md
# monetization.json 項目定義

KYOUKAI内部辞書 — monetization.json フィールド定義

---

## 対象ファイル

`central-os/monetization.json`

---

## このファイルの目的

KYOUKAI 内の収益導線を一元管理する。

どの部屋にどの収益手段が紐づいているかを記録し、
将来的な収益最適化・導線整理の判断材料とする。

---

## フィールド定義

| フィールド | 型 | 意味 | 備考 |
|---|---|---|---|
| id | string | 導線の一意識別子 | `mono_01` 形式。追加時は連番。 |
| room | string | 紐づく部屋の name | rooms.json の name と一致させる。サイト全体に跨る場合は `"全体"` とする。 |
| type | string | 収益手段の種別 | 定義済み値のみ使用（下記参照）。 |
| status | string | 現在の状態 | rooms.json と同じ status 定義を使用。 |
| notes | string | 補足情報・実装状況・検討メモ | 自由記述。現状と課題を簡潔に記載。 |

---

## type 定義済み値

| 値 | 意味 |
|---|---|
| OFUSE | OFUSEによる投げ銭・支援受付 |
| Amazon | Amazonアソシエイト（アフィリエイト） |
| AdSense | Google AdSenseによる広告収益 |
| YouTube | YouTubeチャンネルによる収益化（広告・スーパーチャット等） |
| TikTok | TikTokによる収益化（Creator Fund等） |
| External | 上記以外の外部アフィリエイト・外部サービス連携 |
| Future | 将来検討中の収益手段（グッズ・有料コンテンツ等） |

---

## 運用ルール

- 同一部屋に複数の収益手段がある場合は、それぞれ別 item として記録する
- `status: 保留` は「検討を一時停止中」を意味し、削除はしない
- `status: 実装済み` は本番環境に反映されていることを意味する
- `notes` には「なぜこの手段を選んだか」「課題は何か」を記載することを推奨する
