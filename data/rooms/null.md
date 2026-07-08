# 崩落域

## 基本情報

* ルート: `/null`
* 表示名: 崩落域、`null`
* 階層: 未記載
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: `templates/null.html`, `static/kyoukai-route-c-room.js`

## 世界観

崩落域は世界崩壊、崩壊度上昇、接続悪化、失敗方向を扱う部屋。データはあるが、何のデータかはわからない。ページとして機能しているが、押すほど状態が悪化する。崩落と過剰な情報量が同時にあり、長くいると「自分が何をしているか」がわからなくなる設計。

`/exit` が境界を越えようとする場所なら、`/null` は崩壊が加速する側。

## 現在の実装

ページとして機能しているが、押すほど状態が悪化すると記載されている。Route_C「壊れる前の形」の専用主要部屋として使用され、Route_C完了後は `post_route_c` 状態を保持する。

具体的な操作箇所、演出内容、状態悪化の段階は未記載。

## 操作仕様

ユーザーがタッチ・クリックできる場所は未記載。

操作結果は「押すほど状態が悪化する」と記載されている。具体的な対象箇所と悪化内容は未記載。

## Room States

```yaml
room_states:
  - id: "initial"
    label: "初期状態"
    description: "崩落域に入った直後の状態"
    trigger: "goto"
    capture_priority: "medium"

  - id: "collapse_possible"
    label: "崩壊可能"
    description: "押すほど状態が悪化するとされる状態"
    trigger: "未設定"
    capture_priority: "high"

  - id: "collapse_unknown"
    label: "崩壊詳細未確定"
    description: "具体的な操作箇所、演出内容、状態悪化の段階が未記載の状態"
    trigger: "未設定"
    capture_priority: "medium"
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
    expected: "崩落域が表示される"

  - step: 2
    label: "初期状態を観測する"
    wait_ms: 1500
    action: "observe"
    target: "初期状態"
    selector: "未設定"
    expected: "データがあるが何のデータかわからない状態"

  - step: 3
    label: "押せる場所を確認する"
    wait_ms: 500
    action: "observe"
    target: "押せる場所"
    selector: "未設定"
    expected: "押せる場所は未記載"

  - step: 4
    label: "崩壊変化が確認できる場合は撮影"
    wait_ms: 1500
    action: "observe"
    target: "崩壊変化"
    selector: "未設定"
    expected: "崩壊度上昇、接続悪化、過剰な情報量が出ている状態。確認できない場合は未設定"

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
    id: "observe_collapse"
    label: "初期状態と崩壊変化を観測する"
    action: "observe"
    target: "崩壊変化"
    selector: "未設定"
    wait_ms: 1500
    expected_state: "collapse_possible"
    condition:
      if: "崩壊変化が確認できる"
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
* 必ず見せる変化: 押すほど状態が悪化する変化
* 推奨尺: 未設定
* 冒頭テロップ案: 未設定
* 終了テロップ案: 未設定

```yaml
video_spec:
  default_duration_sec: 未設定
  aspect_ratio: "9:16"
  opening_shot:
    target: "初期状態"
    zoom: "100%"
    duration_ms: 1500
  main_action:
    target: "未設定"
    action: "未設定"
    duration_ms: 未設定
  highlight:
    target: "崩壊変化"
    description: "押すほど状態が悪化する変化。具体的な操作箇所と悪化内容は未記載"
  ending:
    target: "未設定"
    duration_ms: 未設定
  text:
    intro: "未設定"
    outro: "未設定"
```

## AI Navigation

Playwrightなどで自動巡回する場合の手順。

* 開始URL: `/null`
* 待機時間: 未設定
* 操作手順: 未設定
* 撮影すべき状態: 崩壊度上昇、接続悪化、過剰な情報量が出ている状態
* 終了条件: 未設定

```yaml
ai_navigation:
  start_url: "/null"
  viewport:
    width: 390
    height: 844
  steps:
    - action: "goto"
      url: "/null"
      wait_ms: 1500

    - action: "observe"
      selector: "未設定"
      wait_ms: 1500
      expected: "初期状態を観測する"

    - action: "observe"
      selector: "未設定"
      wait_ms: 1500
      expected: "崩壊変化が確認できる場合は撮影する"

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
      reason: "崩落域の初期状態を記録するため"

  optional_captures:
    - name: "highlight"
      state: "collapse_possible"
      reason: "崩壊変化が確認できる場合のみ記録する"
    - name: "collapse_unknown"
      state: "collapse_unknown"
      reason: "崩壊詳細が未確定であることを記録する場合のみ使う"

  success_conditions:
    - "initial が撮影できること"

  failure_conditions:
    - "ページが表示されない"
    - "押せる場所が未設定で自動操作できない"
    - "主要対象が未設定で撮影対象を判断できない"
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 未設定
* 使える一言: 「押すほど状態が悪化する」
* 投稿向きの見どころ: 崩壊が加速する側としての変化、データの意味がわからない不安定さ
* 不足している情報: 入口画像、室内画像、具体的な操作箇所、悪化演出の段階、推奨尺

## 投稿候補情報

- 投稿対象: true
- 表示名: 崩落域
- room_id: null
- ルート: /null
- 見どころ: 制限時間内に連打して目標回数を目指す。押すほど画面が崩壊していき、失敗すると煽られる。
- 投稿文候補: 壊れる前に連打してください。
- 投稿対象外理由:

## 未解決

* 入口画像が未記載。
* 室内画像が未記載。
* 押せる場所が未記載。
* 押した後の状態悪化の具体内容が未記載。
* ShortFACTORY向けの具体的な撮影手順が未設定。
* Playwright用セレクタが未設定。

## 更新履歴

* 2026-07-03: 部屋マスター v1 作成。
* 2026-07-03: 部屋マスター v2.0 として `Interaction Script`、`video_spec`、`ai_navigation` を追加。
