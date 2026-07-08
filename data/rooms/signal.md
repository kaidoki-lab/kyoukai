# 受信域

## 基本情報

* ルート: `/signal`
* 表示名: 受信域、`signal`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: 未記載

## 世界観

受信域はラジオのような場所。外部からの信号を受信しているが、発信源は特定されていない。ノイズと信号の境界が曖昧で、受信内容は断片的に留まり、意味が完結しない。「誰かが送っている」という気配だけがある。

## 現在の実装

具体的な操作、演出、状態管理は未記載。

## 操作仕様

ユーザーがタッチ・クリックできる場所は未記載。

操作結果は未記載。

## Room States

```yaml
room_states:
  - id: "initial"
    label: "初期状態"
    description: "受信域に入った直後の状態"
    trigger: "goto"
    capture_priority: "medium"

  - id: "signal_active"
    label: "信号受信"
    description: "信号を受信している気配がある状態"
    trigger: "未設定"
    capture_priority: "high"

  - id: "noise_signal_ambiguous"
    label: "ノイズと信号の曖昧化"
    description: "ノイズと信号の境界が曖昧な状態"
    trigger: "未設定"
    capture_priority: "high"
```

## Interaction Script

```yaml
interaction_script:
  - step: 1
    label: "部屋に入る"
    wait_ms: 1500
    action: "observe"
    target: "room"
    selector: "未設定"
    expected: "受信域が表示される"

  - step: 2
    label: "受信装置または信号表示を映す"
    wait_ms: 1500
    action: "observe"
    target: "受信装置または信号表示"
    selector: "未設定"
    expected: "信号を受信している気配が撮影できる"

  - step: 3
    label: "操作可能箇所を確認する"
    wait_ms: 500
    action: "observe"
    target: "操作可能箇所"
    selector: "未設定"
    expected: "操作可能箇所は未記載"

  - step: 4
    label: "ノイズと信号の境界が曖昧な状態を撮影"
    wait_ms: 1500
    action: "observe"
    target: "ノイズと信号"
    selector: "未設定"
    expected: "ノイズと信号の境界が曖昧な状態"

  - step: 5
    label: "終了"
    wait_ms: 1000
    action: "observe"
    target: "room"
    selector: "未設定"
    expected: "撮影を終了できる状態"
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
    capture:
      name: "initial"
      timing: "after_action"
      required: true

  - step: 2
    id: "observe_signal"
    label: "受信装置または信号表示を映す"
    action: "observe"
    target: "受信装置または信号表示"
    selector: "未設定"
    wait_ms: 1500
    expected_state: "signal_active"
    condition:
      if: "受信装置または信号表示が確認できる"
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

ShortFACTORYや動画撮影で使う情報。

* 最初に映す場所: 未設定
* 最初に行う操作: 未設定
* 次に行う操作: 未設定
* 必ず見せる変化: 未設定
* 推奨尺: 未設定
* 冒頭テロップ案: 未設定
* 終了テロップ案: 未設定

```yaml
video_spec:
  default_duration_sec: 未設定
  aspect_ratio: "9:16"
  opening_shot:
    target: "未設定"
    zoom: "100%"
    duration_ms: 1500
  main_action:
    target: "受信装置または信号表示"
    action: "observe"
    duration_ms: 未設定
  highlight:
    target: "ノイズと信号"
    description: "ノイズと信号の境界が曖昧な状態、送信者の気配"
  ending:
    target: "未設定"
    duration_ms: 未設定
  text:
    intro: "未設定"
    outro: "未設定"
```

## AI Navigation

Playwrightなどで自動巡回する場合の手順。

* 開始URL: `/signal`
* 待機時間: 未設定
* 操作手順: 未設定
* 撮影すべき状態: ノイズと信号の境界が曖昧な状態
* 終了条件: 未設定

```yaml
ai_navigation:
  start_url: "/signal"
  viewport:
    width: 390
    height: 844
  steps:
    - action: "goto"
      url: "/signal"
      wait_ms: 1500

    - action: "observe"
      selector: "未設定"
      wait_ms: 1500
      expected: "受信装置または信号表示を映す"

    - action: "observe"
      selector: "未設定"
      wait_ms: 1500
      expected: "ノイズと信号の境界が曖昧な状態を撮影する"

  capture:
    - name: "initial"
      timing: "after_goto"
    - name: "highlight"
      timing: "after_main_observe"
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - name: "initial"
      state: "initial"
      reason: "受信域の初期状態を記録するため"

  optional_captures:
    - name: "highlight"
      state: "signal_active"
      reason: "信号受信の気配が確認できる場合のみ記録する"
    - name: "noise_signal_ambiguous"
      state: "noise_signal_ambiguous"
      reason: "ノイズと信号の境界が曖昧な状態を見せる場合のみ記録する"

  success_conditions:
    - "initial が撮影できること"

  failure_conditions:
    - "ページが表示されない"
    - "主要対象が未設定で撮影対象を判断できない"
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 未設定
* 使える一言: 「発信源は特定されていない」
* 投稿向きの見どころ: 断片的な受信内容、送信者の気配
* 不足している情報: 入口画像、室内画像、関連ファイル、操作仕様、動画化手順、推奨尺

## 投稿候補情報

- 投稿対象: true
- 表示名: 受信域
- room_id: signal
- ルート: /signal
- 見どころ: KYOUKAI内の映像を視聴できる部屋。
- 投稿文候補: 映像を受信しています。
- 投稿対象外理由:

## 未解決

* 入口画像が未記載。
* 室内画像が未記載。
* 関連ファイルが未記載。
* 操作可能な場所と操作結果が未記載。
* ShortFACTORY向けの具体的な撮影手順が未設定。
* Playwright用セレクタが未設定。

## 更新履歴

* 2026-07-03: 部屋マスター v1 作成。
* 2026-07-03: 部屋マスター v2.0 として `Interaction Script`、`video_spec`、`ai_navigation` を追加。
