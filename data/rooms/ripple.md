# 波紋域

## 基本情報

* ルート: `/ripple`
* 表示名: 波紋域、`ripple`
* room_id: `ripple`
* 階層: 未記載
* 入口画像: 画像入口を持つ
* 室内画像: 未記載
* 関連ファイル: `templates/ripple.html`, `static/ripple.css`, `static/ripple.js`, `tests/test_ripple_page.py`

## 世界観

触れることで世界が応答する部屋。ドットや波紋はゲーム要素ではなく、観測対象の反応として扱う。触れた結果が完全に制御できない一点を残す。

## 現在の実装

全画面Canvasで構成され、説明なし・ボタンなし・スコアなし。タップ/クリックで波紋、スワイプ/ドラッグで連続波紋が発生する。画面内に通常波紋に完全には従わない異常ドットが存在する。放置中も小さな波紋が自然発生し、1分に一回、中央から広い黒戻し波紋が発生する。

## 操作仕様

* 対象: 画面全体
* 操作: タップ、クリック、スワイプ、ドラッグ
* 結果: 波紋発生、ドット状態変化、異常ドットの違和感
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "ドットグリッドが表示される", trigger: "goto", capture_priority: "medium" }
  - { id: "ripple_active", label: "波紋発生", description: "タップやドラッグで波紋が発生している状態", trigger: "tap_or_drag", capture_priority: "high" }
  - { id: "rebel_dot", label: "異常ドット", description: "通常波紋に完全には従わない一点が見える状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "touch_world", label: "画面に触れる", action: "click", target: "画面全体", selector: "未設定", note: "座標確認が必要", wait_ms: 1500, expected_state: "ripple_active", condition: { if: "波紋が発生する", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "ドットグリッド", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "画面全体", action: "click_or_drag", duration_ms: "未設定" }
  highlight: { target: "波紋と異常ドット", state: "ripple_active", description: "触れると世界が応答するが、一点だけ命令を聞かない" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/ripple"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/ripple", wait_ms: 1500 }
    - { action: "click", selector: "未設定", note: "座標確認が必要", wait_ms: 1500, expected: "波紋が発生する" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "波紋域の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "ripple_active", reason: "波紋発生を見せる場合のみ記録する" }
    - { name: "rebel_dot", state: "rebel_dot", reason: "異常ドットが確認できる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "クリック座標が未設定で自動操作できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: Canvas表示
* ズーム推奨箇所: 波紋、異常ドット
* 使える一言: 「一点だけ命令を聞かない」
* 投稿向きの見どころ: 触れた結果が完全に制御できない反応
* 不足している情報: Canvasセレクタ、クリック座標、推奨尺

## 投稿候補情報

- 投稿対象: true
- 表示名: 波紋域
- room_id: ripple
- ルート: /ripple
- 見どころ: 画面に触れるたびに波紋が広がる。
- 投稿文候補: 意味はありません。ただ波紋が広がります。
- 投稿対象外理由:

## 未解決

* Playwright用セレクタと座標が未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
