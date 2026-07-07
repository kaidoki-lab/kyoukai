# AI大明神

## 基本情報

* ルート: `/daimyojin`
* 表示名: AI大明神
* room_id: `daimyojin`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: 未記載

## 世界観

信仰と機械が混ざった祈願装置。神社、奉納、機械、札、端末が同じ構造物の中にある。占い・祈願に見えるが、処理されているものが願いなのか観測結果なのかは明かさない。

## 現在の実装

町の小さな祠から接続されていた経緯がある。具体的な操作、演出、状態管理は未記載。

## 操作仕様

* 対象: 祈願装置
* 操作: 未記載
* 結果: 未記載
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "AI大明神に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "shrine_machine", label: "信仰と機械", description: "神社、奉納、機械、札、端末が混ざる状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "祈願装置を観測する", action: "observe", target: "祈願装置", selector: "未設定", wait_ms: 1500, expected_state: "shrine_machine", condition: { if: "祈願装置が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "祈願装置", action: "observe", duration_ms: "未設定" }
  highlight: { target: "祈願装置", state: "shrine_machine", description: "AIから神託が届くが、内容はまったく意味がない。" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/daimyojin"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/daimyojin", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "祈願装置を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "AI大明神の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "shrine_machine", reason: "祈願装置が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 祈願装置、札、端末
* 使える一言: 「AIが神託をくれる。でも全部意味がない。」
* 投稿向きの見どころ: AIから神託が届くが、内容はまったく意味がない。
* 不足している情報: 画像、関連ファイル、セレクタ、推奨尺

## 投稿候補情報

* 見どころ: AIから神託が届くが、内容はまったく意味がない。
* 投稿文候補: 「AIが神託をくれる。でも全部意味がない。」
* メモ: 2026-07-07確定版を反映。

## 未解決

* 操作仕様、画像、セレクタが未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
* 2026-07-07: 投稿候補情報の確定版を反映。
