# phase-2-checklist.md
# PHASE 2 完了チェックリスト

最終更新：2026-05-23

---

## データ基盤

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| 1 | rooms.json に正式部屋が登録されている | ✅ 完了 | 12部屋登録済み |
| 2 | 確定routeと未確定routeが分離されている | ✅ 完了 | 7確定・5未確定で分離済み |
| 3 | ideas.json が存在し valid | ✅ 完了 | 5件登録 |
| 4 | monetization.json が存在し valid | ✅ 完了 | 8件登録 |
| 5 | sns-routes.json が存在し valid | ✅ 完了 | 4件登録 |
| 6 | monthly-goal.json が存在し valid | ✅ 完了 | 2026年5月分登録 |

---

## ドキュメント

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| 7 | README.md が存在する | ✅ 完了 | KYOUKAIとの関係含む |
| 8 | spec.md が存在する | ✅ 完了 | route方針・変更可能範囲含む |

---

## schema/

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| 9 | schema/ が存在する | ✅ 完了 | 5ファイル揃い |
| 10 | rooms-schema.md が存在する | ✅ 完了 | route確定条件含む |
| 11 | ideas-schema.md が存在する | ✅ 完了 | type定義11種含む |
| 12 | monetization-schema.md が存在する | ✅ 完了 | |
| 13 | sns-schema.md が存在する | ✅ 完了 | url空文字ルール含む |
| 14 | goal-schema.md が存在する | ✅ 完了 | id命名規則含む |

---

## graph/（導線定義）

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| 15 | graph/ が存在する | ✅ 完了 | 5ファイル揃い |
| 16 | room-links.json が valid JSON | ✅ 完了 | 11リンク定義済み |
| 17 | 初見導線が定義されている | ✅ 完了 | room-flows.md |
| 18 | 再訪問導線が定義されている | ✅ 完了 | room-flows.md |
| 19 | 深層導線が定義されている | ✅ 完了 | room-flows.md |
| 20 | 観測導線が定義されている | ✅ 完了 | observer-flow.md |
| 21 | 収益導線が定義されている | ✅ 完了 | monetization-flow.md |
| 22 | SNS流入導線が定義されている | ✅ 完了 | sns-flow.md |

---

## connection/（参照・固定ルール）

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| 23 | Codex接続ルールが定義されている | ✅ 完了 | codex-readonly-rules.md |
| 24 | central-os参照ルールが定義されている | ✅ 完了 | central-os-reference-rules.md |
| 25 | route固定ルールが定義されている | ✅ 完了 | route-lock-rules.md |

---

## phase/

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| 26 | PHASE 3への進行条件が定義されている | ✅ 完了 | phase-3-entry-criteria.md |
| 27 | PHASE 2 最終レビューが存在する | ✅ 完了 | review/phase-2-review.md |

---

## 未解決・継続管理項目

| # | 項目 | 状態 | 備考 |
|---|---|---|---|
| A | 境界域の route 確定 | ⚠️ 未確定 | 対応テンプレート要確認 |
| B | 崩壊域の route 確定 | ⚠️ 未確定 | /exit との対応要確認 |
| C | 音声室の route 確定 | ⚠️ 未確定 | 独立ページか統合かの判断待ち |
| D | 記録室の route 確定 | ⚠️ 未確定 | /archive との対応要確認 |
| E | 賽銭箱の route 確定 | ⚠️ 未確定 | /support・/outside との関係要確認 |

未確定routeはPHASE 3でも `"未確定"` のまま扱う。UIではリンク化しない。
