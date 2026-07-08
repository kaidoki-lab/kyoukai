# 記録室

## 基本情報

* ルート: `/archive`
* 表示名: 記録室
* room_id: `archive`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: `templates/archive.html`, `static/kyoukai-route-b-room.js`

## 世界観

感情を排した観測記録の集積。日付・ID・内容の羅列があり、感情は排除されているが、読むと感情が生まれる。削除されたはずの記録が残っている気配がある。

## 現在の実装

Route_Bの主要部屋として使用され、完了後は `post_route_b` 状態を保持する。その他の具体的な操作、演出、状態管理は未記載。

## 操作仕様

* 対象: 記録
* 操作: 未記載
* 結果: 未記載
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "記録室に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "records_visible", label: "記録表示", description: "日付・ID・内容の羅列が見える状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "記録を観測する", action: "observe", target: "記録", selector: "未設定", wait_ms: 1500, expected_state: "records_visible", condition: { if: "記録が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "記録", action: "observe", duration_ms: "未設定" }
  highlight: { target: "記録", state: "records_visible", description: "よく分からない画集を閲覧できる部屋。" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/archive"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/archive", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "記録を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "記録室の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "records_visible", reason: "記録が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 日付・ID・内容の羅列
* 使える一言: 「よく分からない画集だけを集めた部屋。」
* 投稿向きの見どころ: よく分からない画集を閲覧できる部屋。
* 不足している情報: 画像、セレクタ、推奨尺

## 投稿候補情報

- 投稿対象: true
- 表示名: 記録室
- room_id: archive
- ルート: /archive
- 見どころ: よく分からない画集を閲覧できる部屋。
- 投稿文候補: よく分からない画集だけを集めた部屋。
- 投稿対象外理由:

## 未解決

* 操作仕様、画像、セレクタが未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
* 2026-07-07: 投稿候補情報の確定版を反映。
