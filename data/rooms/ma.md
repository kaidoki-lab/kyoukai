# 悪魔の間

## 基本情報

* ルート: `/ma`
* 表示名: 悪魔の間
* room_id: `ma`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: ブラウザ版とスマートフォン版の専用背景
* 関連ファイル: `templates/ma.html`, `static/ma.js`, `static/kyoukai-route-c-room.js`

## 世界観

逆観測室の中央にある「?」の扉からのみ到達できる隠し部屋。玉座に座る存在は、4回目の訪問で「大魔将」と名乗る。再訪するたびに会話と関係性が進行し、初期は拒絶的だが再訪を重ねると訪問者の存在を受け入れ始める。

## 現在の実装

訪問回数は端末内に記録され、15段階の会話と関係変化がある。背景には緩やかな呼吸モーションがあり、会話表示には低い声のような短音が伴う。会話終了後は逆観測室へ戻る。Route_Cの主要部屋としても使用される。

## 操作仕様

* 対象: 会話
* 操作: 未記載
* 結果: 会話と関係性が進行する
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "悪魔の間に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "dialogue_active", label: "会話中", description: "大魔将との会話が表示される状態", trigger: "未設定", capture_priority: "high" }
  - { id: "relationship_changed", label: "関係変化", description: "再訪により関係性が変化した状態", trigger: "visit_count", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "会話を観測する", action: "observe", target: "会話", selector: "未設定", wait_ms: 1500, expected_state: "dialogue_active", condition: { if: "会話が表示されている", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "room", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "会話", action: "observe", duration_ms: "未設定" }
  highlight: { target: "大魔将との会話", state: "dialogue_active", description: "再訪により会話と関係性が変化する" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/ma"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/ma", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "会話を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "悪魔の間の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "dialogue_active", reason: "会話が表示される場合のみ記録する" }
    - { name: "relationship_changed", state: "relationship_changed", reason: "再訪変化を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "会話セレクタが未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 専用背景
* ズーム推奨箇所: 玉座、会話表示
* 使える一言: 「4回目の訪問で、大魔将と名乗る」
* 投稿向きの見どころ: 再訪で変化する関係性
* 不足している情報: 背景ファイル名、セレクタ、推奨尺

## 未解決

* 会話操作とセレクタが未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
