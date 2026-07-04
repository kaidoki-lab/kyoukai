# 入口域

## 基本情報

* ルート: `/`
* 表示名: 入口域
* room_id: `home`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: `templates/home.html`, `static/home-entrances.js`, `static/space.css`, `static/images/entrances/`, `tests/test_home_entrances.py`

## 世界観

KYOUKAIの入口で、最初の接触点。訪問者は一つの部屋へ案内されるのではなく、入口群の前に置かれる。スマートフォン版は縦長入口画像を横に並べ、スクロールで部屋を選ぶ。説明文ではなく、入口の造形、色、足元の位置、ラベルだけで意味を出す。背景の黒は外側ではなく、まだ接続されていない領域として扱う。

## 現在の実装

スマートフォン向けの横スクロール入口一覧として記載されている。各入口の表示名はリンク名ベースの英語表記に統一されている。横スクロール停止時に一度だけ軽く揺れて止まる動きがある。

## 操作仕様

* 対象: 入口群
* 操作: 横スクロール、入口選択
* 結果: 各部屋へ接続する
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - id: "initial"
    label: "初期状態"
    description: "入口群が表示される"
    trigger: "goto"
    capture_priority: "medium"
  - id: "entrance_scroll"
    label: "入口スクロール"
    description: "横スクロールで複数の入口が並ぶ状態"
    trigger: "scroll"
    capture_priority: "high"
```

## Interaction Flow

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
    capture: { name: "initial", timing: "after_action", required: true }
  - step: 2
    id: "main_observe"
    label: "入口群を観測する"
    action: "observe"
    target: "入口群"
    selector: "未設定"
    wait_ms: 1500
    expected_state: "entrance_scroll"
    condition: { if: "入口群が表示されている", then: { capture: "highlight" }, else: { action: "continue" } }
    capture: { name: "highlight", timing: "after_action", required: false }
  - step: 3
    id: "end"
    label: "終了"
    action: "observe"
    target: "room"
    selector: "未設定"
    wait_ms: 1000
    expected_state: "end"
    capture: { name: "end", timing: "after_action", required: false }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "入口群", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "入口群", action: "scroll", duration_ms: "未設定" }
  highlight: { target: "入口群", state: "entrance_scroll", description: "横スクロールで入口群が並ぶ状態" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "入口群が表示される" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "入口域の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "entrance_scroll", reason: "入口群を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "入口群のセレクタが未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: `static/images/entrances/`
* ズーム推奨箇所: 入口群
* 使える一言: 未設定
* 投稿向きの見どころ: 横スクロール入口一覧
* 不足している情報: 具体セレクタ、推奨尺、テロップ案

## 未解決

* 入口群のPlaywright用セレクタが未設定。
* 入口画像の個別対応表は未記載。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
