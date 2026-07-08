# 境界街区

## 基本情報

* ルート: `/city`
* 表示名: 境界街区
* room_id: `city`
* 階層: 町として一時導入された探索領域
* 入口画像: 未記載
* 室内画像: 未記載
* 関連ファイル: `data/city_locations.json`, `data/city_districts.json`, `services/city_service.py`, `templates/city/location.html`, `templates/city/altar.html`, `static/city/css/city.css`, `static/city/js/city.js`

## 世界観

町として一時導入された探索領域。`city-001` から `city-010` までの導線、街路、祠、宿泊街、奉納街、祭壇前通路などを持つ。現在のトップ主導線からは外している。

## 現在の実装

町のホットスポットから既存の主要領域へ再配置された経緯がある。今後使う場合はトップから直接入れるのではなく、既存部屋のホットスポットやNewExitなどから再接続する方針。ホットスポットは説明文ではなく画像内の意味がある場所へ置く方針。

## 操作仕様

* 対象: 街区ホットスポット
* 操作: クリックまたはタップ
* 結果: 街区内または既存主要領域へ接続する
* セレクタ: 未設定
* 座標: 未設定

## Room States

```yaml
room_states:
  - { id: "initial", label: "初期状態", description: "境界街区に入った直後の状態", trigger: "goto", capture_priority: "medium" }
  - { id: "district_navigation", label: "街区探索", description: "街路、祠、宿泊街、奉納街などを探索する状態", trigger: "未設定", capture_priority: "high" }
```

## Interaction Flow

```yaml
interaction_flow:
  - { step: 1, id: "enter_room", label: "部屋に入る", action: "goto", target: "room", selector: "未設定", wait_ms: 1500, expected_state: "initial", capture: { name: "initial", timing: "after_action", required: true } }
  - { step: 2, id: "main_observe", label: "街区を観測する", action: "observe", target: "街区ホットスポット", selector: "未設定", wait_ms: 1500, expected_state: "district_navigation", condition: { if: "街区またはホットスポットが確認できる", then: { capture: "highlight" }, else: { action: "continue" } }, capture: { name: "highlight", timing: "after_action", required: false } }
  - { step: 3, id: "end", label: "終了", action: "observe", target: "room", selector: "未設定", wait_ms: 1000, expected_state: "end", capture: { name: "end", timing: "after_action", required: false } }
```

## Video Spec

```yaml
video_spec:
  default_duration_sec: "未設定"
  aspect_ratio: "9:16"
  opening_shot: { target: "街区", zoom: "100%", duration_ms: 1500 }
  main_action: { target: "街区ホットスポット", action: "observe", duration_ms: "未設定" }
  highlight: { target: "街区探索", state: "district_navigation", description: "画像内の意味がある場所に置かれた透明ホットスポット" }
  ending: { target: "未設定", duration_ms: "未設定" }
  text: { intro: "未設定", outro: "未設定" }
```

## AI Navigation

```yaml
ai_navigation:
  start_url: "/city"
  viewport: { width: 390, height: 844 }
  steps:
    - { action: "goto", url: "/city", wait_ms: 1500 }
    - { action: "observe", selector: "未設定", wait_ms: 1500, expected: "街区を映す" }
  capture:
    - { name: "initial", timing: "after_goto" }
    - { name: "highlight", timing: "after_main_action" }
  end_condition: "未設定"
```

## Capture Rules

```yaml
capture_rules:
  required_captures:
    - { name: "initial", state: "initial", reason: "境界街区の初期状態を記録するため" }
  optional_captures:
    - { name: "highlight", state: "district_navigation", reason: "街区探索を見せる場合のみ記録する" }
  success_conditions: [ "initial が撮影できること" ]
  failure_conditions: [ "ページが表示されない", "ホットスポットのセレクタが未設定で自動操作できない" ]
```

## ShortFACTORYメモ

* 使用できる素材: 未記載
* ズーム推奨箇所: 祠、看板、階段、床の反射、奉納物
* 使える一言: 未設定
* 投稿向きの見どころ: 透明ホットスポットによる探索
* 不足している情報: 現在の再接続方針、画像、セレクタ、推奨尺

## 投稿候補情報

- 投稿対象: false
- 表示名: 境界街区
- room_id: city
- ルート: /city
- 見どころ: 未設定
- 投稿文候補: 未設定
- 投稿対象外理由: 削除済み

## 未解決

* 現在トップ主導線から外れているため、撮影開始導線が未設定。

## 更新履歴

* 2026-07-04: 部屋マスター Phase 2 として作成。
