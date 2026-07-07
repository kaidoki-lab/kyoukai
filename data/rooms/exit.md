# 境界域

## 基本情報

* ルート: `/exit`
* 表示名: 境界域
* room_id: `exit`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: 未記載

## 世界観

外へ出るための接続口に見える場所。実際には、部屋と部屋、内部と外部、少女の逃走記録が混線する通路。出口そのものではなく、接続中に挟まるロード画面が本体。終わりのような場所だが、終わりではない。

## 現在の実装

具体的な操作、演出、状態管理は未記載。

## 操作仕様

* 対象: 未記載
* 操作: 未記載
* 結果: 未記載
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "境界域に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "connection_mixed", label: "接続混線", description: "内部と外部、少女の逃走記録が混線する状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "接続混線を観測する", action: "observe", target: "接続混線", selector: "未設定", wait_ms: 1500, expected_state: "connection_mixed", condition: { if: "混線状態が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "接続混線", action: "observe", duration_ms: "未設定" }
  highlight: { target: "街エリア", state: "connection_mixed", description: "街を歩きながら建物を探索し、それぞれの部屋へ入れる。" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/exit"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/exit", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "境界の混線を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "境界域の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "connection_mixed", reason: "接続混線が確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "主要対象が未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 接続中の表示、少女の断片
* 使える一言: 「この街、全部入れます。」
* 投稿向きの見どころ: 街を歩きながら建物を探索し、それぞれの部屋へ入れる。
* 不足している情報: 画像、関連ファイル、セレクタ、推奨尺

## 投稿候補情報

* 見どころ: 街を歩きながら建物を探索し、それぞれの部屋へ入れる。
* 投稿文候補: 「この街、全部入れます。」
* メモ: 現在の街エリア。2026-07-07確定版を反映。

## 未解決

* 操作仕様、撮影対象のセレクタが未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
* 2026-07-07: 投稿候補情報の確定版を反映。
