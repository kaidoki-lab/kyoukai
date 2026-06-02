# 境界セントラルOS 仕様書
# KYOUKAI Central OS — 立ち位置・構造・今後の展開

最終更新：2026-06-02

---

## 1. Central OS とは何か

Central OS は、KYOUKAI という Web 体験の「内部管理層」である。

KYOUKAI 本体（観測域・受信域・評議録などの各部屋）がユーザーに見せる「表」の空間だとすれば、Central OS はその裏側で部屋の状態・導線・収益・SNS・ゲノムシステムを一元的に把握・管理するための「OS 画面」として機能する。

アクセス先：`https://www.void-kyoukai.net/central`

---

## 2. 現在の立ち位置（2026-06-02 時点）

### 実装済みの機能

| 機能 | 詳細 |
|------|------|
| 部屋一覧表示 | `rooms.json` の 13 部屋を名前・ルート・ステータス・syncStatus 付きで表示 |
| ゲノム状態モニター | phase / stability / mutation / noise / observer_count などをリアルタイム表示 |
| watch 同期監視 | `diff-log.json` の差分エントリを一覧表示、PENDING 件数を可視化 |
| 月間目標・収益導線 | `monthly-goal.json` / `monetization.json` の内容を表示 |
| 進化ログ・サイクルマップ | `evolution-log.json` / `cycle-map.json` の内容を表示 |
| pendingDiffItems API | `/api/central-os` が pending 状態の差分エントリだけを専用フィールドで返す |

### データ構造の現状

```
central-os/
├── rooms.json          13部屋の定義（synced: 9 / pending: 4）
├── ideas.json          AI生成ネタ・企画案
├── monthly-goal.json   月間目標
├── monetization.json   収益導線
├── sns-routes.json     YouTube / TikTok / SNS 導線
├── schema/             各 JSON のスキーマ定義
├── supervisor/         AI 監督ルール・リスク判定
├── generation/         コンテンツ生成ルール
├── graph/              部屋間の導線・フロー定義
├── cycle/              ループ・フィードバック定義
├── evolution/          進化ログ・進化ルール
├── observations/       観測ログ
├── metrics/            イベント・メトリクス定義
├── watch/              同期監視スクリプト・差分ログ
├── phase/              フェーズ別チェックリスト・進行条件
├── review/             フェーズ別レビュー資料
└── connection/         Codex 接続ルール・ルートロック
```

### rooms.json 同期状態

| syncStatus | 部屋数 |
|-----------|--------|
| synced    | 9      |
| pending   | 4（境界域・音声室・記録室・賽銭箱） |

pending 4 部屋はいずれも `route: "未確定"` であり、UI 上はリンク化しない方針。

---

## 3. watch 同期システム

`central-os/watch/scripts/` に Python スクリプト群があり、KYOUKAI 本体との差分を検知する。

### スクリプト一覧

| スクリプト | 役割 |
|-----------|------|
| `scan_routes.py` | `main.py` 実装ルートと `rooms.json` 確定ルートの差分検知 |
| `scan_templates.py` | `templates/` HTML と `rooms.json` の `codexMemo` 参照の差分検知 |
| `scan_static.py` | `static/` の注意対象ファイルを分類検出 |
| `scan_sync.py` | 上記 3 つを統合実行。`--write-log` で `diff-log.json` に記録 |

### 実行コマンド

```powershell
python central-os/watch/scripts/scan_sync.py
python central-os/watch/scripts/scan_sync.py --write-log
```

同日・同内容の重複エントリは自動防止される。

### 現在検知中の差分（pending）

- `main.py` に存在するが `rooms.json` 未登録のルート（`/about`, `/archive`, `/contact` など約 20 件）
- `templates/` に存在するが `rooms.json` の `codexMemo` 未参照の HTML（`about.html`, `contact.html` など約 20 件）

これらは「技術的差分」であり、意図的に rooms.json に登録していないページ（サポートページ群など）が含まれる。`osUpdateRequired` は true だが、個別に人間が確認・判断してから対応する。

---

## 4. ゲノムシステムとの連携

Central OS は KYOUKAI のゲノム（仮想生命体の状態）をリアルタイムで監視する。

### 現在のゲノム状態（2026-06-02 計測）

| 項目 | 値 |
|------|----|
| phase | 3（最大） → 減衰中 |
| mutation_count | 1 |
| last_mutation_type | phase_slip |
| total_visits | 57 |
| stability | 92 |

### ゲノム自動減衰の仕組み（2026-06-02 実装）

観測者がいない間、以下の値が毎 tick（3 秒）自動的に減少する：

- `phase_drift` / `visual_instability` / `noise_level` → -2/tick
- `boundary_pressure` / `drift` / `trait_gaze` / `silent_observation` → -1〜-2/tick

phase は条件を下回れば自動的に低下する。無人状態が続くと **約 2 分 20 秒で phase 3 → 1** に落ちる。

### DB 保持ポリシー（2026-06-02 実装）

| テーブル | 保持ルール |
|---------|-----------|
| genome_state | 最新 1000 件のみ保持（以前は無制限に積み上がり 2.3GB に肥大化していた） |
| logs / observation_logs | 30 日以内のレコードのみ保持 |

---

## 5. API

Central OS のデータは `/api/central-os` エンドポイントから JSON で取得できる。

```
GET https://www.void-kyoukai.net/api/central-os
```

### レスポンス構造（主要フィールド）

```json
{
  "version": "1.0",
  "data": {
    "rooms": { ... },
    "diffLog": { ... },
    "pendingDiffItems": [ ... ],
    "watchTargets": { ... },
    "proposals": { ... },
    "observations": { ... },
    "evolutionLog": { ... },
    "cycleMap": { ... },
    "monthly_goal": { ... },
    "monetization": { ... }
  },
  "errors": {}
}
```

`pendingDiffItems` は `syncStatus: "pending"` または `osUpdated: false` のエントリだけを抽出した専用フィールド。Central OS 画面の watch セクションで優先表示に使用する。

---

## 6. 運用ルール

### Central OS に変更してよい範囲

- `central-os/` 内のすべての JSON / Markdown ファイル
- watch スクリプト（`central-os/watch/scripts/`）

### 変更禁止

- `templates/` の HTML
- `static/` の CSS / JS / 画像
- `main.py`（Central OS 目的での変更は原則禁止）
- `rooms.json` の route 確定は、`main.py` の実装を根拠とすること

### diff-log.json の運用

- `scan_sync.py --write-log` で自動生成されたエントリは、内容を人間が確認してから使用する
- 自動書き込み以外の書き込みは禁止
- `syncStatus: "pending"` のエントリは、対応完了後に `"resolved"` へ手動更新する

---

## 7. 今後の展開

### 短期（現フェーズ継続）

| 課題 | 内容 |
|------|------|
| pending 4 部屋のルート確定 | 境界域・音声室・記録室・賽銭箱の route を main.py の実装に合わせて確定 |
| diff-log の pending 解消 | 2 件の pending エントリを人間がレビューし resolved または削除 |
| rooms.json の未登録ルート整理 | サポートページ群（/about, /contact 等）を rooms.json に追加するか、除外対象として明記 |

### 中期（PHASE 3 相当）

- Central OS 画面から各 JSON を編集・追加できる UI の実装
- watch スクリプトの定期自動実行（Vercel Cron または ローカルタスクスケジューラ）
- 部屋間の導線グラフを `/central` 上で可視化

### 長期構想

- ゲノム状態の履歴グラフ表示（phase 推移・mutation 履歴）
- SNS 投稿状況の自動取得・表示
- Codex との自動連携による提案生成・タスク管理の統合
- `total_visits` などの観測統計を Central OS ダッシュボードに表示

---

## 8. ショートカット

デスクトップに「KYOUKAI Central OS」ショートカットを設置済み。

```
https://www.void-kyoukai.net/central
```

ダブルクリックで本番 Central OS に直接アクセスできる。

---

## 付録：フェーズ一覧

| フェーズ | 名称 | 状態 |
|---------|------|------|
| PHASE 1 | データ基盤構築 | 完了 |
| PHASE 2 | 構造安定化・スキーマ確立 | 完了 |
| PHASE 3 | Central UI 実装 | 進行中 |
| PHASE 4 以降 | 編集機能・Codex 連携・統計 | 未着手 |
