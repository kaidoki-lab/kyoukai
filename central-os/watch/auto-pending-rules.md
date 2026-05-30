# auto-pending-rules.md
# KYOUKAI 半自動同期候補生成ルール

PHASE 8-9 — 差分から同期候補を自動生成するためのルール。

---

## 目的

scan スクリプトの出力から、OS更新の候補を自動的に提示する。  
最終的な採用・実行は人間が判断する。自動実行・自動commit は禁止。

---

## 半自動同期の定義

「半自動」とは：
- 機械（スクリプト）が差分を検知し、同期候補を提示する
- 人間が候補を確認し、採用・却下を判断する
- 採用された候補のみ実行する

自動化されないもの：
- OS ファイルの変更（diff-log.json 追記を除く）
- rooms.json の更新
- Codex への指示実行
- git commit / push

---

## 自動ペンディング生成の条件

以下の差分を検知した場合、`codex-sync-tasks.json` への候補追加を提示する。

| 差分の種類 | 生成する候補の種類 |
|---|---|
| main.py に未登録ルート発見 | route-lock-rules.md 更新候補 |
| templates/ に未登録HTML発見 | rooms.json 部屋追加候補 |
| generated-content.json で adopted=true を検知 | rooms.json status更新候補 |
| rooms.json に syncStatus=pending の部屋が多数存在 | 一括同期チェック候補 |

---

## 候補生成のフロー

```
scan_sync.py を実行する
    ↓
差分が検知された
    ↓
scan_sync.py --write-log を実行する（diff-log.json に追記）
    ↓
人間が diff-log.json のエントリを確認・編集する
    ↓
osUpdateRequired: true のエントリについて対象OSファイルを特定する
    ↓
codex-sync-tasks.json に候補エントリを追加する（codexReady: false で）
    ↓
人間が候補を審査し、codexReady: true に変更する
    ↓
codex-sync-protocol.md のテンプレートで Codex 指示を作成する
    ↓
人間がレビューして実行する
```

---

## codex-sync-tasks.json のエントリ形式

```json
{
  "id": "sync_task_YYYYMMDD_nn",
  "date": "YYYY-MM-DD",
  "diffLogId": "diff_YYYYMMDD_nn",
  "title": "タスクのタイトル",
  "proposalId": "prop_XX（proposals.json参照、なければnull）",
  "targetRoute": "/確定済みroute または null",
  "targetFiles": ["作業対象ファイルのパス"],
  "forbiddenFiles": ["触ってはならないファイルのパス"],
  "goal": "具体的な作業目標",
  "risk": "リスクと影響範囲",
  "codexReady": false,
  "status": "pending",
  "memo": "備考"
}
```

---

## codexReady: true への変更条件

自動生成された候補は必ず `codexReady: false` で作成する。  
以下をすべて満たした場合のみ `codexReady: true` に変更できる（人間のみ）。

1. targetRoute が route-lock-rules.md の確定route一覧に存在する
2. targetFiles が特定されている
3. goal が具体的に記述されている
4. risk が把握されている
5. 人間が内容を確認し承認した

---

## 禁止事項

- codexReady: false のままのタスクを Codex に渡すこと
- 自動生成候補を人間確認なしに実行すること
- scan スクリプトを cron・CI 等で定期自動実行すること（手動実行のみ）
- diff-log.json の自動書き込みを目的としたスクリプトの常時起動
