# 粒子観測

## 基本情報

* ルート: `/particles`
* 表示名: 粒子観測、`particles`
* room_id: `particles`
* 階層: 未記載
* 入口画像: 画像入口を持つ
* 室内画像: 未記載
* 関連ファイル: `templates/particles.html`, `static/kyoukai-route-c-room.js`

## 世界観

粒子群を観測する部屋。画面内の運動と反応が先にあり、意味は後から発生する。外部信号やoutsideとは別扱い。

## 現在の実装

Route_Cの主要部屋として使用され、完了後は `post_route_c` 状態を保持する。具体的な操作、演出、状態管理は未記載。

## 操作仕様

* 対象: 粒子群
* 操作: 未記載
* 結果: 未記載
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "粒子観測に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "particles_active", label: "粒子運動", description: "粒子群の運動と反応が見える状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "粒子群を観測する", action: "observe", target: "粒子群", selector: "未設定", wait_ms: 1500, expected_state: "particles_active", condition: { if: "粒子群が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "粒子群", action: "observe", duration_ms: "未設定" }
  highlight: { target: "粒子群", state: "particles_active", description: "意味より先に運動と反応が発生する状態" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/particles"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/particles", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "粒子群を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "粒子観測の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "particles_active", reason: "粒子運動が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 粒子群
* 使える一言: 「意味より運動が先にある」
* 投稿向きの見どころ: 粒子の運動と反応
* 不足している情報: 画像、セレクタ、推奨尺

## 未解決

* 具体的な操作、画像、セレクタが未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
