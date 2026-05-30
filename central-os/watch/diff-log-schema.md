# diff-log-schema.md
# diff-log.json フィールド定義
PHASE 8-3 — OS同期判定スキーマ

---

## 対象ファイル

`central-os/watch/diff-log.json`

---

## フィールド定義

| フィールド | 型 | 必須 | 意味 |
|---|---|---|---|
| id | string | ✓ | エントリの一意識別子。`diff_YYYYMMDD_nn` 形式。 |
| date | string | ✓ | 差分を確認した日付。ISO 8601形式（YYYY-MM-DD）。 |
| targetId | string | ✓ | watch-targets.json の id 参照。例: `target_01` |
| targetPath | string | ✓ | 差分が発生したファイル・ディレクトリのパス。 |
| changeType | string | ✓ | 変更の種類（下記参照）。 |
| summary | string | ✓ | 変更内容の簡潔な説明。1〜2文。 |
| osUpdateRequired | boolean | ✓ | OS更新が必要か。update-decision-rules.md で判定。 |
| syncStatus | string | ✓ | この差分エントリの同期状態（下記参照）。 |
| targetOsFiles | array | | 更新すべきOSファイルのパスリスト。 |
| detectedBy | string | | 検知手段（下記参照）。 |
| osUpdated | boolean | ✓ | OS更新が完了したか。未完了は false。 |
| updatedFiles | array | | 実際に更新したOSファイルのパスリスト。 |
| memo | string | | 備考・注意点。 |

---

## changeType 定義済み値

| 値 | 意味 |
|---|---|
| route_added | main.py に新規ルートが追加された |
| route_removed | main.py からルートが削除された |
| route_changed | 既存ルートのパスが変更された |
| template_added | templates/ に新規HTMLが追加された |
| template_removed | templates/ からHTMLが削除された |
| content_adopted | generated/ のコンテンツが実装に採用された |
| observation_added | observations/ に観測が追加された |
| cycle_updated | cycle/ のサイクル定義が更新された |
| evolution_adopted | evolution/ の進化記録が採用された |
| sns_changed | SNS導線が変更された |
| monetization_changed | 収益導線が変更された |
| sync_scan | scan_sync.py による自動検知エントリ |
| manual | 人間が手動で記録した差分 |

---

## syncStatus 定義済み値

| 値 | 意味 |
|---|---|
| pending | OS更新が必要だが未完了 |
| synced | OS更新完了済み |
| no_update | OS更新不要と判定済み |
| skipped | 一時保留・後回し |

---

## detectedBy 定義済み値

| 値 | 意味 |
|---|---|
| manual | 人間が手動で確認 |
| scan_routes | scan_routes.py による検知 |
| scan_templates | scan_templates.py による検知 |
| scan_static | scan_static.py による検知 |
| scan_sync | scan_sync.py による総合検知 |

---

## osUpdateRequired 判定方針

`update-decision-rules.md` に従って判定する。

| 状況 | osUpdateRequired |
|---|---|
| route追加・削除・変更 | true |
| 新規テンプレート追加 | true（routeとの対応確認後） |
| CSS細部調整のみ | false |
| バグ修正（機能変化なし） | false |
| SNS・収益導線変更 | true |
| 生成コンテンツ採用 | true |
| 誤字修正のみ | false |

---

## 記録テンプレート

```json
{
  "id": "diff_YYYYMMDD_nn",
  "date": "YYYY-MM-DD",
  "targetId": "target_XX",
  "targetPath": "対象ファイル・ディレクトリのパス",
  "changeType": "route_added",
  "summary": "変更内容の説明",
  "osUpdateRequired": true,
  "syncStatus": "pending",
  "targetOsFiles": [
    "central-os/connection/route-lock-rules.md",
    "central-os/rooms.json"
  ],
  "detectedBy": "manual",
  "osUpdated": false,
  "updatedFiles": [],
  "memo": "備考"
}
```

---

## 記録ルール

- diff-log.json への書き込みは人間が手動で行う
- scan_sync.py --write-log オプションで自動追記できるが、必ず内容を確認すること
- osUpdated が false のエントリが残っている場合、sync状態は PENDING となる
- 完了後は osUpdated: true + updatedFiles を記入して syncStatus: "synced" に更新する
