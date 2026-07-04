# 極楽域

## 基本情報

* ルート: `/gokuraku`
* 表示名: 極楽域
* room_id: `gokuraku`
* 階層: 未記載
* 入口画像: トップ入口スクロールで使用する画像
* 室内画像: 未記載
* 関連ファイル: `templates/gokuraku.html`, `static/kyoukai-route-b-room.js`

## 世界観

引き出し、スピーカー、祠、鍵、奥へ続く通路が積み上がった部屋。「極楽」という語を明るく扱わない。過剰な収納と音響装置が、記憶の保管庫にも通路にも見える。

## 現在の実装

Route_Bの主要部屋として使用され、完了後は `post_route_b` 状態を保持する。その他の具体的な操作、演出、状態管理は未記載。

## 操作仕様

* 対象: 引き出し、スピーカー、祠、鍵、奥へ続く通路
* 操作: 未記載
* 結果: 未記載
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "極楽域に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "storage_passage", label: "収納と通路", description: "過剰な収納と音響装置が見える状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "収納と通路を観測する", action: "observe", target: "収納と通路", selector: "未設定", wait_ms: 1500, expected_state: "storage_passage", condition: { if: "収納と通路が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "収納と通路", action: "observe", duration_ms: "未設定" }
  highlight: { target: "収納と通路", state: "storage_passage", description: "記憶の保管庫にも通路にも見える過剰な収納と音響装置" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/gokuraku"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/gokuraku", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "収納と通路を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "極楽域の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "storage_passage", reason: "収納と通路が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 引き出し、スピーカー、祠、鍵、奥へ続く通路
* 使える一言: 「極楽という語を明るく扱わない」
* 投稿向きの見どころ: 記憶の保管庫にも通路にも見える構造
* 不足している情報: 画像、セレクタ、推奨尺

## 未解決

* 操作仕様、画像、セレクタが未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
