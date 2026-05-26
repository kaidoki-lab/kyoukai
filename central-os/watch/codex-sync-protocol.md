# codex-sync-protocol.md
# KYOUKAI Codex同期プロトコル

差分検知後、Codex（または Claude Code）に実装作業を依頼する際のテンプレートと手順。

---

## 原則

- このプロトコルは **人間が差分を確認し、OS更新が完了した後** にのみ使用する
- Codex への指示は `proposals.json` に存在するエントリに基づく
- `codexReady: false` の提案は Codex に渡してはならない
- route・対象・目的・リスクが明確でなければ指示を出さない

---

## Codex指示を出してよい条件

以下をすべて満たした場合のみ Codex への指示が可能。

| 条件 | 確認方法 |
|---|---|
| route が確定している | `route-lock-rules.md` の確定route一覧に存在する |
| 対象ファイルが明確 | テンプレート名・CSS名・エンドポイントが特定できている |
| 目的が明確 | proposals.json の `goal` フィールドが具体的に記述されている |
| リスクが把握されている | proposals.json の `risk` フィールドが記述されている |
| codexReady が true | proposals.json の `codexReady: true` になっている |
| 既存ファイルへの影響がない | または影響範囲が明確で承認済み |

---

## Codex指示テンプレート

差分検知後に Codex（Claude Code）に依頼する際は、以下のテンプレートを使用する。

---

```
## Codex指示 — [提案タイトル]

### 前提確認
- proposal ID: prop_XX
- route: /確定済みroute
- codexReady: true
- 確認日: YYYY-MM-DD

### 作業内容
[proposals.json の goal フィールドの内容をそのまま記載]

### 対象ファイル
- 新規作成: [ファイルパス]
- 変更可: [ファイルパス]

### 絶対に触らないファイル
- main.py（routeの追加・削除禁止）
- central-os/ 配下（読み取り専用）
- 既存テンプレート（指定外のHTMLファイル）
- 既存CSS（scoped外の変更禁止）

### リスクと制約
[proposals.json の risk フィールドの内容]

### 完了条件
[具体的な完了基準を記載]

### 確認事項（Codex作業後に人間が確認する）
- [ ] 既存ページが壊れていないか
- [ ] 新規ルートが main.py に反映されているか（追加した場合）
- [ ] route-lock-rules.md を更新したか（route変更の場合）
- [ ] rooms.json を更新したか
```

---

## 差分検知からCodex指示までのフロー

```
1. 実装変更を確認する（watch-targets.json 参照）
    ↓
2. update-decision-rules.md で OS更新要否を判断する
    ↓
3. OS更新が必要 → 該当ファイルを更新する
    ↓
4. Codex作業が必要か判断する
    ↓ 必要な場合
5. proposals.json の該当エントリを確認する
    ↓
6. codexReady: true であるか確認する
    ↓ false の場合 → proposals.json を更新して true にするか判断する（人間のみ）
    ↓ true の場合
7. 上記テンプレートに従って指示を作成する
    ↓
8. 人間がレビューし承認する
    ↓
9. Codex / Claude Code に指示を渡す
    ↓
10. 完了後 diff-log.json に記録する
```

---

## codexReady を true にする条件

`proposals.json` の `codexReady` を false から true に変更できる条件。  
この判断は **人間のみ** が行う。

| 必須条件 | 内容 |
|---|---|
| route確定 | route-lock-rules.md の確定route一覧に存在する |
| 対象明確 | 作業するファイル・ディレクトリが特定されている |
| 目的具体 | 「何を」「なぜ」「どのように」が記述されている |
| リスク把握 | 既存ファイルへの影響範囲が明確 |
| 人間承認 | ユーザーが明示的に codexReady: true への変更を承認した |

---

## 禁止事項

| 禁止 | 内容 |
|---|---|
| codexReady: false のまま指示 | 未確定・未承認の作業は依頼しない |
| 未確定routeの実装依頼 | route-lock-rules.md の未確定routeは実装対象外 |
| central-os/ の変更依頼 | Codex は central-os/ を読み取り専用として扱う |
| 複数提案の同時依頼 | 1指示 = 1提案エントリ。競合防止のため1件ずつ実行する |
| 人間レビューなしの実行 | テンプレート作成後は必ず人間が確認してから渡す |

---

## 同期完了後の記録

Codex作業完了後、以下を記録する。

1. `diff-log.json` に作業ログを追記する
2. `proposals.json` の該当エントリの `status` を `完了` に更新する
3. `rooms.json` の対応部屋の `status` を更新する（実装完了の場合）
4. `route-lock-rules.md` を更新する（route追加・変更があった場合）
