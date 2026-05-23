# phase-4-review.md
# PHASE 4「AI監督化」最終レビュー

レビュー日：2026-05-23

---

## PHASE 4 の概要

AI監督レイヤーを「提案専用」として実装する。

AI接続・自動生成・自動実装は行わない。
central-os を読み取り専用で参照し、
/central 上で AI監督提案を確認できる状態を作る。

---

## 完了チェックリスト

| # | 項目 | 状態 |
|---|---|---|
| 1 | central-os/supervisor/ が存在する | ✅ 完了 |
| 2 | supervisor-rules.md が存在する | ✅ 完了 |
| 3 | proposal-schema.md が存在する | ✅ 完了 |
| 4 | proposal-sample.json が存在する | ✅ 完了 |
| 5 | risk-rules.md が存在する | ✅ 完了 |
| 6 | central-os/proposals/proposals.json が存在する | ✅ 完了 |
| 7 | proposals.json が valid JSON | ✅ 完了 |
| 8 | /api/central-os が proposals を返す | ✅ 完了 |
| 9 | /central に AI監督セクションが表示される | ✅ 完了 |
| 10 | 各提案に risk が表示される | ✅ 完了 |
| 11 | codexReady が表示される | ✅ 完了 |
| 12 | 提案は実装ではなく提案として扱われている | ✅ 完了 |
| 13 | 既存ページに影響がない | ✅ 完了 |
| 14 | AI API接続をしていない | ✅ 完了 |
| 15 | PHASE 5へ進む条件が定義されている | ✅ 完了 |

---

## PHASE 4 で実装した内容

### central-os/supervisor/（新規）

| ファイル | 役割 |
|---|---|
| supervisor-rules.md | AI監督の役割・権限・制約の定義 |
| proposal-schema.md | proposals.json のフィールド定義 |
| proposal-sample.json | サンプル提案6件 |
| risk-rules.md | 禁止提案・リスク基準の定義 |
| phase-4-review.md | 本ファイル |

### central-os/proposals/（新規）

| ファイル | 役割 |
|---|---|
| proposals.json | 実際に /central に表示する提案データ（6件） |

### main.py への追加

- proposals.json の読み込みを `central_os_payload()` に追加
- supervisor フォルダの存在確認をペイロードに追加

### /central への追加

- AI監督セクションを追加
- 提案カード表示（priority / type / targetRoom / expectedEffect / risk / codexReady / status）
- codexReady=false の強調表示

---

## まだ未実装の要素

| 要素 | 内容 | PHASE |
|---|---|---|
| AI API接続 | Claude / OpenAI 等の提案自動生成 | PHASE 5 |
| 提案の採用・却下操作 | /central 上での操作 | PHASE 5 |
| 自動生成サイクル | 定期的な提案更新 | PHASE 5 |
| Codex自動実行 | 採用提案のCodexへの自動転送 | PHASE 6以降 |

---

## PHASE 5 に進んでよい条件

| 条件 | 確認方法 |
|---|---|
| AI監督提案が /central で確認できる | /central の AI監督セクションが表示される |
| 提案の安全性・リスクが見える | risk フィールドと codexReady が表示される |
| codexReady=false の提案を実装対象外にできる | UI上で区別できる |
| 人間確認を挟む前提が維持されている | supervisor-rules.md に明記されている |
| 収益・SNS・部屋更新が提案として整理されている | proposals.json に6件以上存在する |

---

## PHASE 4 完了判定

## ✅ GO

**判定：GO（PHASE 5 へ進める）**

### 根拠

- AI監督レイヤーが提案専用として実装されている
- AI接続・自動生成・自動実装は一切行っていない
- central-os を読み取り専用で参照している
- proposals.json が /central に表示される
- codexReady=false が視覚的に区別される
- risk が全提案に記載されている
- 人間確認フローが supervisor-rules.md に明記されている

---

## PHASE 5 概要（次のフェーズ）

「自動生成化」

- Claude API / Claude Code を接続し、central-os の状態から提案を自動生成する
- 生成された提案は proposals.json に書き込まれ /central に表示される
- 採用・却下は引き続き人間が行う
- codexReady の自動判定ロジックを実装する
