# ideas-schema.md
# ideas.json 項目定義

KYOUKAI内部辞書 — ideas.json フィールド定義

---

## 対象ファイル

`central-os/ideas.json`

---

## このファイルの目的

KYOUKAI に対して提案・生成されたアイデア・企画案を一元管理する。

AI（Claude / Codex）・人間どちらからの提案も記録できる。

---

## フィールド定義

| フィールド | 型 | 意味 | 備考 |
|---|---|---|---|
| id | string | アイデアの一意識別子 | `idea_01` 形式。追加時は連番。 |
| type | string | アイデアの種別 | 定義済み値のみ使用（下記参照）。 |
| targetRoom | string | このアイデアを適用する部屋の name | rooms.json の name と一致させる。複数部屋対象の場合は代表部屋を記載。 |
| content | string | アイデアの内容 | 具体的に記述する。「〜するとよい」ではなく「〜する」形式で。 |
| status | string | このアイデアの状態 | rooms.json と同じ status 定義を使用。 |
| adopted | boolean | 採用済みかどうか | `true` = 採用・実装に進んだ。`false` = 未採用・検討中。 |

---

## type 定義済み値

| 値 | 意味 |
|---|---|
| image | 画像・ビジュアル演出に関するアイデア |
| music | BGM・音声・サウンドに関するアイデア |
| short-video | TikTok・YouTubeショート向けのコンテンツ案 |
| room-event | 部屋内で起きるインタラクション・イベントのアイデア |
| monetization | 収益導線・アフィリエイト・支援に関するアイデア |
| observer-event | ユーザーの行動を検知・反応する演出のアイデア |
| コンテンツ | テキスト・コンテンツ全般（上記に分類できない場合） |
| インタラクション | ユーザー操作・UI挙動全般 |
| 音声 | music と同義。旧フォーマット互換のため残す。 |
| 収益 | monetization と同義。旧フォーマット互換のため残す。 |
| SNS | SNS展開・拡散に関するアイデア |

---

## adopted の運用ルール

- アイデアを実装に進める決定をした時点で `true` に変更する
- `true` にしても content や status は消去しない（記録として残す）
- 採用後に実装が完了した場合は status を `実装済み` にする
