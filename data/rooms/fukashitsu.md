# 卵部屋

## 基本情報

* ルート: `/fukashitsu`
* 表示名: 卵部屋、`EGG`
* 階層: 2階4番目スロット（`roomIndex: 8`）
* 入口画像: `static/images/entrances/entrance-fukashitsu.png`
* 室内画像: `static/images/fukashitsu/fukashitsu-room-9x16.png`, `static/images/fukashitsu/fukashitsu-collected-9x16.png`
* 関連ファイル: `templates/fukashitsu.html`, `static/fukashitsu.css`, `static/fukashitsu.js`, `static/particle-engine.js`, `static/kyoukai-building-data.js`, `main.py`

## 世界観

旧称「孵化室」から「卵部屋」に改名された部屋。室内背景はピンク色の孵化装置画像。卵エリア内でパーティクルエンジンが動作し、3つの透明ボタン操作によって赤・青・黄の粒子色が段階的に鮮やかになる。

## 現在の実装

9:16背景画像 `static/images/fukashitsu/fukashitsu-room-9x16.png` を全画面表示する。卵エリアは左12%、上13%、幅76%、高さ61%に配置され、専用Canvasを `clip-path: ellipse(46% 50% at 50% 50%)` で卵形にマスクしている。

卵の中では `ParticleObservationEngine` を `background:'transparent'`、`noAutoResize:true`、`observerEffect:false`、`count:160` で起動する。`collapsing` フェーズはスキップし、破裂演出はない。初期色は赤・青・黄とも非常に淡いパステル色で、3本のボタンを押すごとに対応色が段階的に鮮やかになる。テキストフィードバックは一切ない。

各ボタンを10回押すと完成し、「取り出す」ボタンが出現する。「取り出す」ボタン押下でパーティクル停止、フェードアウト、背景が `fukashitsu-collected-9x16.png` に切り替わる。再訪時は最初から取り出し後の背景を表示する。上部パネル7回タップで隠しリセットする。

## 操作仕様

ユーザーがタッチ・クリックできる場所は以下。

* 栄養ボタン: 下部パネルのボタン画像に重なる透明ボタン。押すごとに対応色が段階的に鮮やかになる。個別セレクタは未設定。
* 酸素ボタン: 下部パネルのボタン画像に重なる透明ボタン。押すごとに対応色が段階的に鮮やかになる。個別セレクタは未設定。
* 温度ボタン: 下部パネルのボタン画像に重なる透明ボタン。押すごとに対応色が段階的に鮮やかになる。個別セレクタは未設定。
* 取り出すボタン: 3つのボタンを各10回押すと出現する。押下でパーティクル停止、フェードアウト、取り出し後背景へ切り替わる。セレクタは `#fukaCollectBtn`。
* 上部パネル: 7回タップで隠しリセット。セレクタは未設定。

## Room States

```yaml
room_states:
  - id: "initial"
    label: "初期状態"
    description: "卵部屋の9:16背景全体が表示される"
    trigger: "goto"
    capture_priority: "medium"

  - id: "egg_particles"
    label: "卵内粒子"
    description: "卵形Canvas内で粒子が動作している状態"
    trigger: "goto"
    capture_priority: "high"

  - id: "color_changed"
    label: "粒子色変化"
    description: "栄養・酸素・温度ボタンで粒子色が鮮やかになる状態"
    trigger: "未設定"
    capture_priority: "high"

  - id: "collect_button_visible"
    label: "取り出すボタン表示"
    description: "各ボタンを10回押した後に取り出すボタンが出現した状態"
    trigger: "#fukaCollectBtn"
    capture_priority: "high"

  - id: "collected"
    label: "取り出し後"
    description: "取り出し後背景に切り替わった状態"
    trigger: "#fukaCollectBtn"
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
    expected: "卵部屋の9:16背景全体が表示される"

  - step: 2
    label: "卵を見る"
    wait_ms: 1500
    action: "observe"
    target: "卵エリア"
    selector: "#fukaCanvas"
    expected: "卵形にマスクされたCanvas内で粒子が動作している"

  - step: 3
    label: "栄養ボタンを押す"
    wait_ms: 500
    action: "click"
    target: "栄養ボタン"
    selector: "未設定"
    note: "座標確認が必要"
    expected: "対応色が段階的に鮮やかになる"

  - step: 4
    label: "酸素ボタンを押す"
    wait_ms: 500
    action: "click"
    target: "酸素ボタン"
    selector: "未設定"
    note: "座標確認が必要"
    expected: "対応色が段階的に鮮やかになる"

  - step: 5
    label: "温度ボタンを押す"
    wait_ms: 500
    action: "click"
    target: "温度ボタン"
    selector: "未設定"
    note: "座標確認が必要"
    expected: "対応色が段階的に鮮やかになる"

  - step: 6
    label: "必要回数押して粒子色を変化させる"
    wait_ms: 1000
    action: "repeat_click"
    target: "栄養・酸素・温度ボタン"
    selector: "未設定"
    note: "各ボタン10回。座標確認が必要"
    expected: "3色の粒子が本来の原色に近づく"

  - step: 7
    label: "取り出すボタンを押す"
    wait_ms: 500
    action: "click"
    target: "取り出すボタン"
    selector: "#fukaCollectBtn"
    expected: "パーティクル停止、フェードアウト、取り出し後背景への切り替わりが起きる"

  - step: 8
    label: "取り出し後背景を撮影"
    wait_ms: 1500
    action: "observe"
    target: "取り出し後背景"
    selector: "未設定"
    expected: "static/images/fukashitsu/fukashitsu-collected-9x16.png の状態が表示される"

  - step: 9
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
    id: "observe_egg"
    label: "卵を見る"
    action: "observe"
    target: "卵エリア"
    selector: "#fukaCanvas"
    wait_ms: 1500
    expected_state: "egg_particles"
    capture:
      name: "egg_particles"
      timing: "after_action"
      required: true

  - step: 3
    id: "change_colors"
    label: "必要回数押して粒子色を変化させる"
    action: "repeat_click"
    target: "栄養・酸素・温度ボタン"
    selector: "未設定"
    note: "座標確認が必要"
    wait_ms: 1000
    expected_state: "color_changed"
    capture:
      name: "color_changed"
      timing: "after_action"
      required: false

  - step: 4
    id: "collect"
    label: "取り出すボタンを押す"
    action: "click"
    target: "取り出すボタン"
    selector: "#fukaCollectBtn"
    wait_ms: 1500
    expected_state: "collected"
    condition:
      if: "取り出すボタンが表示されている"
      then:
        capture: "collected"
      else:
        action: "continue"
    capture:
      name: "collected"
      timing: "after_action"
      required: false

  - step: 5
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

* 最初に映す場所: 卵エリアと下部パネルが入る室内全体
* 最初に行う操作: 栄養・酸素・温度の透明ボタンを押す
* 次に行う操作: 各ボタンを10回押し、「取り出す」ボタンを押す
* 必ず見せる変化: 粒子色が淡いパステル色から鮮やかになる変化、取り出し後背景への切り替わり
* 推奨尺: 未設定
* 冒頭テロップ案: 未設定
* 終了テロップ案: 未設定

```yaml
video_spec:
  default_duration_sec: 未設定
  aspect_ratio: "9:16"
  opening_shot:
    target: "卵エリアと下部パネル"
    zoom: "100%"
    duration_ms: 1500
  main_action:
    target: "栄養・酸素・温度ボタン"
    action: "repeat_click"
    duration_ms: 未設定
  highlight:
    target: "卵エリア"
    description: "粒子色が淡いパステル色から鮮やかになる変化、取り出し後背景への切り替わり"
  ending:
    target: "取り出し後背景"
    duration_ms: 未設定
  text:
    intro: "未設定"
    outro: "未設定"
```

## AI Navigation

Playwrightなどで自動巡回する場合の手順。

* 開始URL: `/fukashitsu`
* 待機時間: 未設定
* 操作手順: 栄養・酸素・温度の透明ボタンをそれぞれ10回クリックし、出現した「取り出す」ボタンをクリックする。
* 撮影すべき状態: 初期の淡い粒子、操作後に鮮やかになった粒子、「取り出す」ボタン出現、取り出し後背景
* 終了条件: 取り出し後背景 `static/images/fukashitsu/fukashitsu-collected-9x16.png` が表示されること

```yaml
ai_navigation:
  start_url: "/fukashitsu"
  viewport:
    width: 390
    height: 844
  steps:
    - action: "goto"
      url: "/fukashitsu"
      wait_ms: 1500

    - action: "observe"
      selector: "#fukaCanvas"
      wait_ms: 1500
      expected: "卵形Canvas内の粒子が表示される"

    - action: "click"
      selector: "未設定"
      note: "栄養ボタン。座標確認が必要"
      wait_ms: 500
      expected: "対応色が変化する"

    - action: "click"
      selector: "未設定"
      note: "酸素ボタン。座標確認が必要"
      wait_ms: 500
      expected: "対応色が変化する"

    - action: "click"
      selector: "未設定"
      note: "温度ボタン。座標確認が必要"
      wait_ms: 500
      expected: "対応色が変化する"

    - action: "repeat_click"
      selector: "未設定"
      note: "栄養・酸素・温度を各10回。座標確認が必要"
      wait_ms: 1000
      expected: "取り出すボタンが出現する"

    - action: "click"
      selector: "#fukaCollectBtn"
      wait_ms: 1500
      expected: "取り出し後背景が表示される"

  capture:
    - name: "initial"
      timing: "after_goto"
    - name: "egg_particles"
      timing: "after_observe_canvas"
    - name: "highlight"
      timing: "after_main_action"
    - name: "collected"
      timing: "after_collect"
  end_condition: "取り出し後背景が表示されること"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - name: "initial"
      state: "initial"
      reason: "卵部屋の初期状態を記録するため"
    - name: "egg_particles"
      state: "egg_particles"
      reason: "卵内の粒子運動を記録するため"

  optional_captures:
    - name: "color_changed"
      state: "color_changed"
      reason: "粒子色の変化を見せる場合に記録する"
    - name: "collect_button_visible"
      state: "collect_button_visible"
      reason: "取り出すボタンが出現した状態を見せる場合に記録する"
    - name: "collected"
      state: "collected"
      reason: "取り出し後背景を見せる場合に記録する"

  success_conditions:
    - "initial が撮影できること"
    - "egg_particles が撮影できること"

  failure_conditions:
    - "ページが表示されない"
    - "卵エリアまたは粒子が確認できない"
    - "栄養・酸素・温度ボタンの座標が未設定で自動操作できない"
```

## ShortFACTORYメモ

* 使用できる素材: `static/images/fukashitsu/fukashitsu-room-9x16.png`, `static/images/fukashitsu/fukashitsu-collected-9x16.png`, `static/images/entrances/entrance-fukashitsu.png`
* ズーム推奨箇所: 卵エリア、下部パネルの3つのボタン、取り出し後の背景
* 使える一言: 「テキストフィードバックは一切ない」
* 投稿向きの見どころ: 粒子色が段階的に鮮やかになる変化、破裂せずに取り出しへ進む流れ
* 不足している情報: 推奨尺、冒頭テロップ案、終了テロップ案、各透明ボタンの具体座標

## 投稿候補情報

- 投稿対象: false
- 表示名: 卵部屋
- room_id: fukashitsu
- ルート: /fukashitsu
- 見どころ: 未設定
- 投稿文候補: 未設定
- 投稿対象外理由: 今回の投稿対象外

## 未解決

* 推奨尺が未設定。
* 冒頭テロップ案、終了テロップ案が未設定。
* AI巡回用の栄養・酸素・温度ボタンの個別セレクタが未設定。
* 栄養・酸素・温度ボタンは座標確認が必要。

## 更新履歴

* 2026-07-03: 部屋マスター v1 作成。
* 2026-07-03: 部屋マスター v2.0 として `Interaction Script`、`video_spec`、`ai_navigation` を追加。
