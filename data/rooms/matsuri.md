# 棒入れ祭

## 基本情報

* ルート: `/matsuri`
* 表示名: 棒入れ祭
* room_id: `matsuri`
* 階層: 6階
* 入口画像: `static/images/entrances/entrance-matsuri.png`
* 室内画像: `static/images/matsuri/`
* 関連ファイル: `templates/matsuri.html`, `static/matsuri.css`, `static/matsuri.js`, `static/images/matsuri/README.md`, `static/audio/matsuri/README.md`, `scripts/extract_matsuri_assets.py`, `main.py`, `static/kyoukai-floor.js`, `tests/test_home_entrances.py`

## 世界観

豊穣信仰の奉納儀式として処理する部屋。人物・手・群衆は描かず、棒と穴、注連縄・紙垂・御幣などの祭具のみで構成する。

## 現在の実装

棒を繰り返しタップすると穴へ少しずつ沈む。固定10回クリア方式は廃止され、タップごとに深さが進み、30%の確率で少し後退する積み上げ方式。ゴール時は手持ち花火・打ち上げ花火が鳴る。観客の歓声・拍手は環境音としてランダムに流れ続ける。

## 操作仕様

* 対象: 棒
* 操作: タップ
* 結果: 棒が穴へ沈む。ランダムで後退する。ゴールでクライマックス演出。
* セレクタ: `.matsuri-pole-hit`
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "棒と穴が表示される", trigger: "goto", capture_priority: "medium" }
  - { id: "pole_progress", label: "奉納進行", description: "棒が穴へ少しずつ沈む状態", trigger: ".matsuri-pole-hit", capture_priority: "high" }
  - { id: "climax", label: "奉納完了", description: "ゴール時の花火・クライマックス演出", trigger: "goal", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "tap_pole", label: "棒をタップする", action: "repeat_click", target: "棒", selector: ".matsuri-pole-hit", wait_ms: 1500, expected_state: "pole_progress", condition: { if: "棒が穴へ沈む", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "棒と穴", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "棒", action: "repeat_click", duration_ms: "未設定" }
  highlight: { target: "奉納進行", state: "pole_progress", description: "棒が穴へ沈み、ゴールで花火が鳴る" }
  ending: { target: "奉納完了", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/matsuri"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/matsuri", wait_ms: 1500 }
    - { action: "repeat_click", selector: ".matsuri-pole-hit", wait_ms: 1500, expected: "棒が穴へ沈む" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "棒入れ祭の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "pole_progress", reason: "棒が沈む変化を見せる場合のみ記録する" }
    - { name: "climax", state: "climax", reason: "奉納完了を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "棒のクリック対象が確認できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: `static/images/matsuri/`, `static/audio/matsuri/`
* ズーム推奨箇所: 棒、穴、奉納完了時
* 使える一言: 未設定
* 投稿向きの見どころ: 棒が少しずつ沈み、ランダムで後退する積み上げ
* 不足している情報: 推奨尺、テロップ案

## 未解決

* クライマックスまでの必要タップ回数はランダム後退のため未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
