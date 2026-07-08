# 逆観測室

## 基本情報

* ルート: `/observer`
* 表示名: 逆観測室
* room_id: `observer`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: 未記載

## 世界観

KYOUKAIの最深部。ここで「観測する側と観測される側の逆転」が完成する。テキストが訪問者に語りかけ、「あなたはずっと観測されていた」という気づきの場所になる。壮大に演出せず、静かに知らせる。

## 現在の実装

具体的な操作、演出、状態管理は未記載。悪魔の間 `/ma` への隠し扉があると記載されている。

## 操作仕様

* 対象: 隠し扉
* 操作: 未記載
* 結果: `/ma` へ接続する
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "逆観測室に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "reverse_observation", label: "逆観測", description: "観測する側と観測される側の逆転を示す状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "逆観測のテキストを観測する", action: "observe", target: "逆観測のテキスト", selector: "未設定", wait_ms: 1500, expected_state: "reverse_observation", condition: { if: "逆観測のテキストが確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "逆観測のテキスト", action: "observe", duration_ms: "未設定" }
  highlight: { target: "逆観測", state: "reverse_observation", description: "観測者が観測されていたと気づく状態" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/observer"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/observer", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "逆観測の気配を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "逆観測室の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "reverse_observation", reason: "逆観測の演出が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 語りかけるテキスト
* 使える一言: 「あなたはずっと観測されていた」
* 投稿向きの見どころ: 観測の逆転
* 不足している情報: 画像、関連ファイル、セレクタ、推奨尺

## 投稿候補情報

- 投稿対象: false
- 表示名: 逆観測室
- room_id: observer
- ルート: /observer
- 見どころ: 未設定
- 投稿文候補: 未設定
- 投稿対象外理由: 現状準備中

## 未解決

* 隠し扉のセレクタと座標が未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
