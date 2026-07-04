# 外部接続

## 基本情報

* ルート: `/outside`
* 表示名: 外部接続
* room_id: `outside`
* 階層: 未記載
* 入口画像: 画像入口を持たせない方針
* 室内画像: 未記載
* 関連ファイル: 未記載

## 世界観

KYOUKAIの「外」への扉。ここから先はKYOUKAIではない。外部リンク集だが、リンク先の説明が不穏で、「外」に何があるかはわからない。

## 現在の実装

具体的な操作、演出、状態管理は未記載。トップ入口スクロールには出さず、元々の導線位置に戻す方針と記載されている。

## 操作仕様

* 対象: 外部リンク
* 操作: クリック
* 結果: KYOUKAIの外へ接続する
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "外部接続に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "external_links", label: "外部リンク", description: "外部リンク集と不穏な説明が見える状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "外部リンクを観測する", action: "observe", target: "外部リンク", selector: "未設定", wait_ms: 1500, expected_state: "external_links", condition: { if: "外部リンクが確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "外部リンク", action: "observe", duration_ms: "未設定" }
  highlight: { target: "外部リンク", state: "external_links", description: "KYOUKAIの外へ向かう不穏なリンク集" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/outside"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/outside", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "外部リンクを映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "外部接続の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "external_links", reason: "外部リンクを見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 外部リンク
* 使える一言: 「ここから先はKYOUKAIではない」
* 投稿向きの見どころ: 外へ出るはずなのに不穏な説明
* 不足している情報: 画像、関連ファイル、セレクタ、推奨尺

## 未解決

* 外部リンクのセレクタが未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
