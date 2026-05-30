# sync-audit-rules.md
# KYOUKAI 同期監査ルール

PHASE 8-8 — Central OS と実装の整合性を定期的に監査するためのルール。

---

## 目的

Central OS（central-os/）と KYOUKAI 実装（main.py / templates / static）の  
乖離を発見・記録し、OS の正確性を保つ。

---

## 監査の種類

| 種類 | 対象 | 頻度の目安 |
|---|---|---|
| route監査 | main.py ↔ rooms.json | 実装変更のたび |
| テンプレート監査 | templates/ ↔ rooms.json | テンプレート追加・削除のたび |
| graph監査 | graph/ ↔ rooms.json | 導線変更のたび |
| 部屋整合性監査 | rooms.json 内部の整合性 | 月1回程度 |
| フルスキャン | 全対象 | 月1回またはリリース前 |

---

## route監査チェックリスト

- [ ] main.py の PAGE_MAP に含まれる全ルートを一覧した
- [ ] main.py の @app.get() デコレータに含まれる全ルートを一覧した
- [ ] API ルート（/api/*）を除外した
- [ ] rooms.json の確定ルート一覧と照合した
- [ ] 差分を diff-log.json に記録した
- [ ] route-lock-rules.md を更新した（変更がある場合）

---

## テンプレート監査チェックリスト

- [ ] templates/ の HTML ファイルを一覧した
- [ ] 各テンプレートに対応するルートが main.py に存在するか確認した
- [ ] 各テンプレートに対応する部屋が rooms.json に存在するか確認した
- [ ] 未登録テンプレートがある場合、部屋追加の要否を判断した

---

## graph監査チェックリスト

- [ ] room-links.json のリンクが rooms.json の確定ルートのみを参照しているか確認した
- [ ] room-flows.md の導線が rooms.json の実装状態と整合しているか確認した
- [ ] 未確定ルートへのリンクが含まれていないか確認した

---

## 部屋整合性監査チェックリスト

- [ ] route = "未確定" の部屋の扱いを確認した
- [ ] implemented = false の部屋が意図通りの状態か確認した
- [ ] syncStatus = "pending" の部屋の対応方針を確認した
- [ ] issues/nextActions の内容が現在の状況を反映しているか確認した

---

## 監査結果の記録

監査結果は `audit/sync-report.md` に記録する。

フォーマット:
```
# sync-report-YYYY-MM-DD.md
監査日: YYYY-MM-DD
監査種別: [フルスキャン / route監査 / ...]
実施者: [人間の名前 or Claude Code]

## 結果サマリー
- 差分件数: N 件
- 問題なし: Y / N

## 検出した差分
[差分の内容]

## 対応方針
[OS更新が必要な場合の対応方針]

## diff-log.json への記録
diff_YYYYMMDD_XX を追加した / 追加不要
```

---

## 禁止事項

- 監査結果を元にした自動実装
- 監査中の rooms.json の変更（確認後に別途対応する）
- 未確定ルートを確定として記録すること

---

## scan スクリプトとの関係

`central-os/watch/scripts/` の各スクリプトを実行すると、  
機械的な差分検知が可能。ただし出力は参考情報であり、  
最終判断は人間が行う。
