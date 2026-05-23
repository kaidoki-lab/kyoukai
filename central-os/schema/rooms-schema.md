# rooms-schema.md
# rooms.json 項目定義

KYOUKAI内部辞書 — rooms.json フィールド定義

---

## 対象ファイル

`central-os/rooms.json`

---

## フィールド定義

| フィールド | 型 | 意味 | 備考 |
|---|---|---|---|
| id | string | 部屋の一意識別子 | `room_01` 形式。変更禁止。 |
| name | string | 部屋の正式名称 | KYOUKAI世界観内の名前。 |
| route | string | HTTPルートパス | 実在確認済みのみ固定値を記載。未確認は `"未確定"` とする。 |
| status | string | 現在の実装状態 | 定義済み値のみ使用（下記参照）。 |
| priority | string | 作業優先度 | 定義済み値のみ使用（下記参照）。 |
| role | string | 部屋が担う役割・概念説明 | 1〜2文で記述。UI仕様ではなく世界観・機能の定義。 |
| monetization | array | この部屋に紐づく収益導線の種別 | type文字列の配列。詳細は monetization.json を参照。 |
| sns | array | この部屋に紐づくSNS導線 | sns-routes.json の id 参照を想定。現時点は空配列可。 |
| issues | array | 現在の課題・未解決事項 | 文字列の配列。作業ログではなく状態記録。 |
| nextActions | array | 次に取るべき行動 | 文字列の配列。実装指示ではなく方針メモ。 |
| codexMemo | string | Codex・AI向けの補足メモ | 技術的な補足、ルート根拠、注意点を記載。 |

---

## route 方針

### 確定ルートの条件

以下のいずれかで実在が確認できたルートのみ固定値を記載する。

- `main.py` の `PAGE_MAP` に登録されている
- `main.py` の FastAPI `@app.get()` デコレータに登録されている
- ユーザーが明示的に指定した

### 現在の確定ルート一覧

| 部屋 | route | 根拠 |
|---|---|---|
| 祭壇域 | `/` | ユーザー指定・PAGE_MAP登録 |
| 観測域 | `/observation` | PAGE_MAP登録 |
| 受信域 | `/signal` | PAGE_MAP登録（signal.html） |
| 逆観測室 | `/observer` | ユーザー指定 |
| 未確認接続 | `/null` | PAGE_MAP登録（null.html） |
| 外部接続 | `/outside` | PAGE_MAP登録（outside.html） |
| 評議録 | `/hyougi` | PAGE_MAP登録（hyougi.html） |

### 未確定ルートの扱い

実在確認できていない部屋の route は必ず `"未確定"` とする。

- 推測・類推でルートを記載してはならない
- 将来設計中のルートも確定前は `"未確定"`
- 確定後にのみ値を更新する

---

## status 定義済み値

| 値 | 意味 |
|---|---|
| 未着手 | まだ手を付けていない |
| 制作中 | コンテンツ・素材を作っている |
| 実装中 | コードを書いている |
| 修正中 | 既存を直している |
| 確認待ち | レビュー・動作確認待ち |
| 実装済み | 本番に反映済み |
| 保留 | 一時停止・判断待ち |

これ以外の値は使用しない。

---

## priority 定義済み値

| 値 | 使いどころ |
|---|---|
| 最優先 | 今週中に完了必須 |
| 高 | 今月中に完了したい |
| 中 | できれば今月 |
| 低 | いつかやる |
| 保留 | 判断待ち・中断 |

これ以外の値は使用しない。
---

## implemented 定義

rooms.json の各部屋項目には implemented を設定できる。

| 値 | 意味 |
|---|---|
| true | main.py 上で route 実装済み |
| false | 設計上は存在するが、route 未実装 |
| 未設定 | 過去データ。今後は設定推奨 |

implemented: false の route は、設計確定であっても Codex が勝手に実装してはいけない。
