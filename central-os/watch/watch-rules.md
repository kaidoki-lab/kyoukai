# watch-rules.md
# KYOUKAI 差分検知ルール

KYOUKAI における変更検知の対象・判断基準・禁止事項を定義する。

---

## 目的

実装側（main.py / templates / static）と Central OS（central-os/）のあいだで生じた乖離を  
人間が検知し、OS 側の記録を最新状態に保つためのルールセット。

自動化は行わない。検知・判断・更新はすべて人間が行う。

---

## 差分検知の基本フロー

```
実装変更が発生する
    ↓
watch-targets.json の対象ファイル・ディレクトリに変更があったか確認する
    ↓
update-decision-rules.md に照らして「OS更新要否」を判断する
    ↓
更新が必要な場合 → sync-checklist.md を実行する
    ↓
Codex への指示が必要な場合 → codex-sync-protocol.md のテンプレートを使用する
    ↓
差分をdiff-log.jsonに記録する
```

---

## 監視の原則

| 原則 | 内容 |
|---|---|
| 人間起点 | 差分検知は人間が手動で行う。自動監視スクリプトは作らない |
| 記録優先 | 変更の有無にかかわらず確認した事実を diff-log.json に残す |
| OS非侵害 | 差分検知のために central-os/ のファイルを変更してはならない（記録ファイルを除く） |
| 実装非侵害 | central-os/ の変更が実装側（main.py / templates）に波及してはならない |
| Codex待機 | Codex への指示は codex-sync-protocol.md に従い、人間がレビュー後に実行する |

---

## 監視対象（概要）

詳細は `watch-targets.json` を参照。

| カテゴリ | 対象 | 変更時の主な影響 |
|---|---|---|
| サーバー | main.py | route追加・削除 → rooms.json / route-lock-rules.md 更新要 |
| テンプレート | templates/ | 新規ページ → rooms.json への部屋追加要否確認 |
| スタイル | static/ | 原則OS更新不要（UI調整のみの場合） |
| 部屋定義 | central-os/rooms.json | 他のOS記録との整合性確認 |
| フロー図 | central-os/graph/ | 導線変更 → room-flows.md 更新要否確認 |
| 生成済みコンテンツ | central-os/generated/ | 採用済みコンテンツ → rooms.json の実装状態反映 |
| 観測記録 | central-os/observations/ | 観測追加 → cycleへの反映要否確認 |
| サイクル | central-os/cycle/ | サイクル変更 → evolution-log.json 更新要否確認 |
| 進化記録 | central-os/evolution/ | 進化採用 → 関連部屋のstatus反映要 |

---

## OS更新が必要な変更

以下の変更が実装側で発生した場合、Central OS の更新が必要。

- 新規 route の追加（`@app.get()` / PAGE_MAP への追加）
- 既存 route の削除・変更
- 新規テンプレート（HTML）の追加
- 部屋の新規設計・廃止
- SNS導線・収益導線の変更
- 生成コンテンツの実装採用
- 観測・サイクル・進化記録の追加

---

## OS更新が不要な変更

以下の変更は Central OS に影響しない。OS更新は不要。

- CSS の細部調整（色・余白・フォントサイズ等）
- 誤字・脱字の修正
- 画像・BGM の差し替え（ファイルパス変更なし）
- バグ修正のみの変更（機能・route の変化なし）
- コメントの追記・削除

---

## 禁止事項

| 禁止 | 理由 |
|---|---|
| 自動監視スクリプトの作成 | KYOUKAI は手動管理を方針とする |
| 自動 commit / push | 人間の確認なしにOSを変更してはならない |
| AI による diff-log.json の自動書き込み | 記録の正確性は人間が保証する |
| route の推測記載 | route-lock-rules.md のルールに従う |
| OS更新不要と確認せずに差分を無視すること | 見落としを防ぐため記録に残す |

---

## このルールの適用範囲

- Claude Code による central-os/ の編集
- Codex による実装提案・作業
- 人間によるサイト更新後の確認作業
