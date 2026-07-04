# なまはげ

## 基本情報

* ルート: `/namahage`
* 表示名: なまはげ
* room_id: `namahage`
* 階層: 6階
* 入口画像: `static/images/entrances/entrance-namahage.png`
* 室内画像: `static/images/namahage/namahage-room-9x16.png`
* 関連ファイル: `templates/namahage.html`, `static/namahage.css`, `static/namahage.js`, `vercel.json`, `main.py`, `static/kyoukai-floor.js`, `tests/test_home_entrances.py`

## 世界観

民俗の「なまはげ」をモチーフにした観測型インタラクション部屋。

## 現在の実装

9:16背景画像を全画面表示し、なまはげの顔の両目の位置に16×12の低解像度Canvasを重ねる。操作はタップ・長押し・ダブルタップのみで、UI要素・ボタン・説明文は持たない。通常は赤く光る瞳が明滅し、タップ、ダブルタップ、長押しで目が変化する。

## 操作仕様

* 対象: 画面全体または目
* 操作: タップ、長押し、ダブルタップ
* 結果: 瞬き、見開き、強い光、起動シーケンス
* セレクタ: 未設定
* 座標: `.namahage-eye--left`, `.namahage-eye--right` の座標は記載済み

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "なまはげ背景と赤い目が表示される", trigger: "goto", capture_priority: "medium" }
  - { id: "eyes_idle", label: "目の明滅", description: "赤く光る瞳が緩やかに明滅する状態", trigger: "goto", capture_priority: "high" }
  - { id: "eyes_active", label: "目の反応", description: "タップ、ダブルタップ、長押しで目が変化する状態", trigger: "tap_or_hold", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "tap_or_hold", label: "目を反応させる", action: "click_or_hold", target: "画面全体または目", selector: "未設定", note: "座標確認が必要", wait_ms: 1500, expected_state: "eyes_active", condition: { if: "目の反応が確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "なまはげの顔", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "目", action: "tap_or_hold", duration_ms: "未設定" }
  highlight: { target: "目の反応", state: "eyes_active", description: "タップ、ダブルタップ、長押しで目が段階的に変化する" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/namahage"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/namahage", wait_ms: 1500 }
    - { action: "click", selector: "未設定", note: "座標確認が必要", wait_ms: 1500, expected: "目が反応する" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "なまはげの初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "eyes_active", reason: "目の反応を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "クリック座標が未設定で自動操作できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: `static/images/namahage/namahage-room-9x16.png`
* ズーム推奨箇所: 両目
* 使える一言: 未設定
* 投稿向きの見どころ: 赤い目の明滅と操作反応
* 不足している情報: Playwright用の安定セレクタ、推奨尺、テロップ案

## 未解決

* 操作用セレクタが未設定。座標確認が必要。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
