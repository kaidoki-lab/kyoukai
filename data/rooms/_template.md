# 部屋名

## 基本情報

* ルート: "未設定"
* 表示名: "未設定"
* room_id: "未設定"
* 階層: "未設定"
* 入口画像: "未設定"
* 室内画像: "未設定"
* 関連ファイル: "未設定"

## 世界観

未設定

## 現在の実装

未設定

## 操作仕様

ユーザーがタッチ・クリックできる場所を書く。

* 対象: 未設定
* 操作: 未設定
* 結果: 未設定
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - id: "initial"
    label: "初期状態"
    description: "部屋に入った直後の状態"
    trigger: "goto"
    capture_priority: "medium"

  - id: "highlight"
    label: "見せ場状態"
    description: "この部屋で動画化すべき主要変化。未設定の場合は未設定とする"
    trigger: "未設定"
    capture_priority: "high"
```

## Interaction Flow

この部屋で「何を見て、何を押し、何が起きたら何を撮るか」を条件分岐込みで記録する。

```yaml
interaction_flow:
  - step: 1
    id: "enter_room"
    label: "部屋に入る"
    action: "goto"
    target: "room"
    selector: "未設定"
    wait_ms: 1500
    expected_state: "initial"
    capture:
      name: "initial"
      timing: "after_action"
      required: true

  - step: 2
    id: "main_observe"
    label: "主要対象を観測する"
    action: "observe"
    target: "未設定"
    selector: "未設定"
    wait_ms: 1500
    expected_state: "highlight"
    condition:
      if: "未設定"
      then:
        capture: "highlight"
      else:
        action: "continue"
    capture:
      name: "highlight"
      timing: "after_action"
      required: false

  - step: 3
    id: "end"
    label: "終了"
    action: "observe"
    target: "room"
    selector: "未設定"
    wait_ms: 1000
    expected_state: "end"
    capture:
      name: "end"
      timing: "after_action"
      required: false
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot:
    target: "room"
    zoom: "100%"
    duration_ms: 1500
  main_action:
    target: "未設定"
    action: "未設定"
    duration_ms: "未設定"
  highlight:
    target: "未設定"
    state: "highlight"
    description: "未設定"
  ending:
    target: "未設定"
    duration_ms: "未設定"
  text:
    intro: "未設定"
    outro: "未設定"
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "未設定"
  viewport:
    width: 390
    height: 844
  steps:
    - action: "goto"
      url: "未設定"
      wait_ms: 1500

    - action: "observe"
      selector: "未設定"
      wait_ms: 1500
      expected: "未設定"
  capture:
    - name: "initial"
      timing: "after_goto"
    - name: "highlight"
      timing: "after_main_action"
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - name: "initial"
      state: "initial"
      reason: "部屋の初期状態を記録するため"

  optional_captures:
    - name: "highlight"
      state: "highlight"
      reason: "見せ場が発生した場合のみ記録する"

  success_conditions:
    - "initial が撮影できること"

  failure_conditions:
    - "ページが表示されない"
    - "主要対象が未設定で撮影対象を判断できない"
```

## ShortFACTORYメモ

* 使用できる素材: 未設定
* ズーム推奨箇所: 未設定
* 使える一言: 未設定
* 投稿向きの見どころ: 未設定
* 不足している情報: 未設定

## 投稿候補情報

- 投稿対象: true
- 表示名: 未設定
- room_id: 未設定
- ルート: 未設定
- 見どころ: 未設定
- 投稿文候補: 未設定
- 投稿対象外理由:

## 未解決

* 未設定

## 更新履歴

* YYYY-MM-DD: 作成。
