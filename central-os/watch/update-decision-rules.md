# update-decision-rules.md
# KYOUKAI OS更新判定ルール

実装側の変更が発生したとき「Central OS の更新が必要か否か」を判断するためのルール。

---

## 判断の基本原則

Central OS は KYOUKAI の「設計の正本」である。  
実装側の変更が **設計の変化** を意味する場合、OS を更新する。  
実装側の変更が **既存設計の範囲内の調整** である場合、OS の更新は不要。

---

## OS更新が必要な変更（必須）

以下の変更が発生した場合、必ず Central OS を更新する。

| 変更の種類 | 更新するOSファイル |
|---|---|
| 新規 route の追加 | `connection/route-lock-rules.md` / `rooms.json` / `schema/rooms-schema.md` |
| 既存 route の削除 | `connection/route-lock-rules.md` / `rooms.json` |
| 既存 route のパス変更 | `connection/route-lock-rules.md` / `rooms.json` / `schema/rooms-schema.md` |
| 新規テンプレート（HTML）の追加 | `rooms.json`（status・routeの更新） |
| 部屋の新規設計 | `rooms.json`（新エントリ追加） |
| 部屋の廃止決定 | `rooms.json`（status変更） |
| SNS導線の追加・変更 | `sns-routes.json` / `graph/sns-flow.md` |
| 収益導線の追加・変更 | `monetization.json` / `graph/monetization-flow.md` |
| 生成コンテンツの実装採用 | `rooms.json`（status更新） / `generated/generated-content.json` |
| 観測記録の追加 | `observations/observations.json` |
| サイクル進行・フェーズ遷移 | `cycle/cycle-map.json` |
| 進化の採用決定 | `evolution/evolution-log.json` / `rooms.json` |

---

## OS更新が不要な変更（スキップ可）

以下の変更は設計の変化ではないため、Central OS の更新は不要。  
ただし変更の確認自体は行うこと。

| 変更の種類 | 理由 |
|---|---|
| CSS の色・余白・フォントサイズ調整 | UIの見た目のみ。設計変化なし |
| 画像ファイルの差し替え（パス変更なし） | コンテンツ差し替えのみ |
| BGM・音声ファイルの差し替え | コンテンツ差し替えのみ |
| 誤字・脱字の修正 | 機能・設計に無影響 |
| コメントの追記・削除 | 動作に無影響 |
| バグ修正（route・機能変化なし） | 既存設計の範囲内 |
| JavaScript の内部処理調整（API endpoint変更なし） | 既存設計の範囲内 |

---

## 判断が難しい場合のフロー

```
変更が発生した
    ↓
Q1: route（PAGE_MAP / @app.get）に変化があったか？
    YES → OS更新必須（route-lock-rules.md + rooms.json）
    ↓ NO
Q2: 新しいテンプレート（HTML）が追加されたか？
    YES → OS更新要否を検討（routeとの対応確認）
    ↓ NO
Q3: SNS・収益の設計に変化があったか？
    YES → OS更新必須（sns-routes.json / monetization.json）
    ↓ NO
Q4: 生成コンテンツ・観測・サイクル・進化の記録に変化があったか？
    YES → 対応するOSファイルの更新を検討する
    ↓ NO
→ OS更新不要。必要に応じてdiff-log.jsonに確認済みとして記録する。
```

---

## 更新優先度の判断

OS更新が必要と判断した場合、以下の優先度で対応する。

| 優先度 | 条件 | 対応 |
|---|---|---|
| 即時 | route の追加・削除・変更 | 実装確認後すぐに route-lock-rules.md を更新 |
| 当日中 | テンプレート追加・部屋status変更 | 作業セッション内で rooms.json を更新 |
| 次回セッション | SNS・収益導線の変更 | 次の作業開始時に更新 |
| 任意タイミング | 観測・サイクル・進化記録 | 記録整理のタイミングで更新 |

---

## OS更新時の確認事項

Central OS を更新する前に必ず確認する。

- [ ] 更新内容が実装の実態と一致しているか
- [ ] route は `route-lock-rules.md` の確定条件を満たしているか
- [ ] 推測・類推による記載になっていないか
- [ ] `implemented` フラグが実態と一致しているか（rooms.json 更新時）
- [ ] 変更が他の OS ファイルとの整合性を壊していないか

---

## このルールの適用範囲

- Claude Code による central-os/ の更新判断
- 人間によるサイト変更後の確認作業
- Codex へ指示を出す前の前提確認
