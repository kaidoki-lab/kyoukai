# 最上階

## 基本情報

* ルート: `/top-floor`
* 表示名: 最上階 / 教会（仮称）
* room_id: `top-floor`
* 階層: 通常部屋群のさらに上、最上階専用部屋
* 入口画像: `static/images/entrances/entrance-top-floor.png`
* 室内画像: `static/images/top-floor/room-9x16.png`
* 関連ファイル: `templates/top-floor.html`, `static/kyoukai-building-data.js`, `static/kyoukai-scenario.js`, `static/kyoukai-floor.js`, `docs/境界ワールド.md`

## 世界観

KYOUKAIの通常フロアとは別枠で、常に一番上に配置される最上階専用部屋。通常部屋の「1フロア5部屋固定」ルールの対象外。今後、最上階・教会・鍵穴系シナリオの受け皿にする。

## 現在の実装

建物データでは `topFloorRoom` として通常の `rooms` 配列とは分離して管理する。`/top-floor` は現時点では室内画像を全画面寄りに表示し、エレベーターへ戻る導線のみを持つ。最終シナリオや教会関連イベントの具体処理は未実装。

## 操作仕様

* 対象: エレベーターへ戻る導線
* 操作: 未記載
* 結果: エレベーターへ戻る
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "最上階の室内画像が表示される", trigger: "goto", capture_priority: "medium" }
  - { id: "top_floor_room", label: "最上階専用部屋", description: "通常フロアとは別枠の1部屋だけが表示される状態", trigger: "goto", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "最上階を観測する", action: "observe", target: "最上階室内", selector: "未設定", wait_ms: 1500, expected_state: "top_floor_room", condition: { if: "室内画像が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "最上階室内", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "最上階室内", action: "observe", duration_ms: "未設定" }
  highlight: { target: "最上階専用部屋", state: "top_floor_room", description: "通常部屋群のさらに上に配置される1部屋だけの最上階" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/top-floor"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/top-floor", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "最上階室内を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "最上階の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "top_floor_room", reason: "最上階専用部屋を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: `static/images/top-floor/room-9x16.png`, `static/images/entrances/entrance-top-floor.png`
* ズーム推奨箇所: 最上階室内
* 使える一言: 未設定
* 投稿向きの見どころ: 通常フロアとは別枠の最上階専用部屋
* 不足している情報: 最終シナリオ、教会関連イベント、セレクタ、推奨尺

## 未解決

* 最終シナリオや教会関連イベントの具体処理は未実装。
* エレベーターへ戻る導線のセレクタが未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
