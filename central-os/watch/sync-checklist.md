# sync-checklist.md
# KYOUKAI 差分同期チェックリスト

実装側に変更が発生した際、Central OS との同期状態を確認するためのチェックリスト。

---

## 使い方

1. 実装変更の直後に実行する
2. 各項目を上から順に確認する
3. 該当しない項目はスキップしてよい
4. 差分があった項目は `diff-log.json` に記録する
5. OS更新が必要な項目は実行後に記録を更新する

---

## STEP 1 — 変更内容の確認

- [ ] どのファイルが変更されたか把握した
- [ ] 変更の種類を分類した（route追加 / テンプレート追加 / CSS調整 / バグ修正 等）
- [ ] `update-decision-rules.md` を参照し「OS更新要否」を判断した

---

## STEP 2 — route変更の場合

main.py に route の追加・削除・変更があった場合に実施。

- [ ] `main.py` の `PAGE_MAP` と `@app.get()` 一覧を確認した
- [ ] `central-os/connection/route-lock-rules.md` の確定route一覧と照合した
- [ ] 新規 route がある場合 → `route-lock-rules.md` の確定route一覧に追記した
- [ ] 新規 route に対応する部屋がある場合 → `rooms.json` の `route` フィールドを更新した
- [ ] 新規 route に対応する部屋がない場合 → 部屋の新規追加要否を判断した
- [ ] `rooms-schema.md` の確定route一覧も更新した
- [ ] 削除・変更された route がある場合 → 対応する rooms.json エントリを確認した

---

## STEP 3 — テンプレート追加の場合

templates/ に新規 HTML ファイルが追加された場合に実施。

- [ ] 新規テンプレートに対応する route を main.py で確認した
- [ ] 対応する部屋が `rooms.json` に存在するか確認した
- [ ] 存在しない場合 → 部屋の追加を proposals.json に記録することを検討した
- [ ] 既存部屋が対応する場合 → `rooms.json` の `status` を更新した（「実装中」→「実装済み」等）

---

## STEP 4 — 生成コンテンツが採用された場合

central-os/generated/ の内容が実装に反映された場合に実施。

- [ ] `generated-content.json` の該当エントリを確認した
- [ ] 採用されたコンテンツに対応する部屋の `status` を `rooms.json` で更新した
- [ ] 対応する proposals.json のエントリがある場合 → status を更新した

---

## STEP 5 — SNS・収益導線の変更の場合

外部リンク・SNS導線・収益設計に変更があった場合に実施。

- [ ] `central-os/sns-routes.json` の内容を確認・更新した
- [ ] `central-os/monetization.json` の内容を確認・更新した
- [ ] `central-os/graph/sns-flow.md` の導線図を確認・更新した
- [ ] `central-os/graph/monetization-flow.md` の導線図を確認・更新した

---

## STEP 6 — 差分ログの記録

- [ ] 変更内容を `diff-log.json` に記録した
  - `targetId`（watch-targets.json の id）
  - `date`（確認日）
  - `changeType`（変更種別）
  - `summary`（変更内容の要約）
  - `osUpdated`（OS更新したか true/false）
  - `updatedFiles`（更新したOSファイルのリスト）

---

## STEP 7 — Codex指示が必要な場合のみ

Codex に実装作業を依頼する場合のみ実施。

- [ ] `codex-sync-protocol.md` のテンプレートを参照した
- [ ] `proposals.json` に提案エントリが存在するか確認した
- [ ] `codexReady: true` の条件（route確定・対象明確・リスク把握）が揃っているか確認した
- [ ] 人間がレビューし、指示内容を承認した

---

## 記録テンプレート（diff-log.json 用）

```json
{
  "id": "diff_YYYYMMDDnn",
  "date": "YYYY-MM-DD",
  "targetId": "target_XX",
  "targetPath": "対象パス",
  "changeType": "route_added | template_added | content_adopted | その他",
  "summary": "変更内容の簡潔な説明",
  "osUpdated": true,
  "updatedFiles": ["更新したOSファイルのパス"],
  "memo": "備考・注意点"
}
```
