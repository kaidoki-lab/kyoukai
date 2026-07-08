# 台風ニュース

## 基本情報

* ルート: `/typhoon-news/`
* 表示名: 台風ニュース、`news`
* room_id: `typhoon-news`
* 階層: 未記載
* 入口画像: `static/images/entrances/news.png`
* 室内画像: `typhoon-news/assets/typhoon-news-bg.png`
* 関連ファイル: `typhoon-news/index.html`, `typhoon-news/style.css`, `typhoon-news/script.js`

## 世界観

ニュース番組の顔をした、YouTube Shorts / TikTok / X向けの短尺映像素材室。冗談の名前が災害情報として流れる。真面目なニュース番組の形式で、ふざけた台風名だけが異常化する。

## 現在の実装

生成済みの台風ニュース画像を背景に、速報帯、情報パネル、台風名、縦コピー、警戒ボックス、テロップ、雨、稲妻、ノイズを重ねる。`typhoonPresets` を変更すると別の台風名へ差し替えられる。URLパラメータ `?name=` でも指定できる。

## 操作仕様

* 対象: URLパラメータ `?name=`
* 操作: 台風名指定
* 結果: 表示される台風名が差し替わる
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "台風ニュース画面が表示される", trigger: "goto", capture_priority: "medium" }
  - { id: "news_overlay", label: "ニュース演出", description: "速報帯、警戒ボックス、雨、稲妻、ノイズが重なる状態", trigger: "goto", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "ニュース演出を観測する", action: "observe", target: "ニュース演出", selector: "未設定", wait_ms: 1500, expected_state: "news_overlay", condition: { if: "速報帯や警戒ボックスが確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "ニュース画面全体", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "ニュース演出", action: "observe", duration_ms: "未設定" }
  highlight: { target: "台風名", state: "news_overlay", description: "真面目なニュース番組形式で日常的な保留語が災害名として流れる" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/typhoon-news/"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/typhoon-news/", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "ニュース演出が表示される" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "ニュース画面の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "news_overlay", reason: "ニュース演出を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "ニュース演出のセレクタが未設定で撮影対象を判断できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: `typhoon-news/assets/typhoon-news-bg.png`
* ズーム推奨箇所: 台風名、速報帯、警戒ボックス
* 使える一言: 未設定
* 投稿向きの見どころ: 真面目なニュース番組形式と異常な台風名
* 不足している情報: セレクタ、推奨尺、テロップ案

## 投稿候補情報

- 投稿対象: true
- 表示名: 台風ニュース
- room_id: typhoon-news
- ルート: /typhoon-news/
- 見どころ: 部屋に入るたびに毎回変な名前の台風が発表される。
- 投稿文候補: 今日の台風は『〇〇』です。
- 投稿対象外理由:

## 未解決

* Playwright用セレクタが未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
