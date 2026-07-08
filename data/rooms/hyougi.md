# 評議録

## 基本情報

* ルート: `/hyougi`
* 表示名: 評議録
* room_id: `hyougi`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: 未記載

## 世界観

誰かが記録した議事録。発言者は不明。議題も結論も曖昧で、複数の声がある。合意しているのか対立しているのかわからない。読むほど不安定になる文体が理想。

## 現在の実装

具体的な操作、演出、状態管理は未記載。Route_Bの主要部屋として使用され、完了後は `post_route_b` 状態を保持する。

## 操作仕様

* 対象: 未記載
* 操作: 未記載
* 結果: 未記載
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "評議録に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "records_visible", label: "記録表示", description: "議事録の断片が表示される状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "議事録を観測する", action: "observe", target: "議事録", selector: "未設定", wait_ms: 1500, expected_state: "records_visible", condition: { if: "議事録が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "議事録", action: "observe", duration_ms: "未設定" }
  highlight: { target: "議事録", state: "records_visible", description: "発言者不明の複数の声と不安定な記録" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/hyougi"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/hyougi", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "議事録を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "評議録の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "records_visible", reason: "議事録が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 議事録
* 使える一言: 「発言者は不明」
* 投稿向きの見どころ: 合意か対立かわからない複数の声
* 不足している情報: 入口画像、室内画像、関連ファイル、セレクタ、推奨尺

## 投稿候補情報

- 投稿対象: true
- 表示名: 評議録
- room_id: hyougi
- ルート: /hyougi
- 見どころ: AIが考えた効率良く議論するための評議を閲覧できる。生活をシステム化するための議論が流れ続ける。
- 投稿文候補: AIだけで議論すると、こんな評議録が生まれます。
- 投稿対象外理由:

## 未解決

* 操作仕様、画像、セレクタが未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
