# pending-sync.md
# Codex 同期待ちタスク

PHASE 8-4 / Codex同期生成レイヤー

差分検知後、Codex への指示が必要なタスクをここに記録する。
`codex-sync-tasks.json` の人間向け参照用テキスト。

---

## 現在のペンディングタスク

（なし — diff-log.json に差分が記録されたとき、人間がここに追記する）

---

## 記録フォーマット

```
### [タスクID] タイトル

- proposal: prop_XX（proposals.json参照）
- codexReady: false → true への変更要否を確認
- 対象ルート: 確定ルートのみ記載
- 対象ファイル: 作業対象のパス
- 禁止事項: 触ってはならないファイル・操作
- 完了条件: 具体的な完了基準

詳細は codex-sync-protocol.md のテンプレートを使用すること。
```

---

## 重要事項

- codexReady: false のままのタスクは Codex に渡さない
- 未確定routeを含むタスクは実行不可
- このファイルはメモ用途。実際の指示は codex-sync-protocol.md テンプレートを使う
