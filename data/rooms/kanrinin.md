# 管理人室

## 基本情報

* ルート: `/kanrinin`, `/manager`
* 表示名: 管理人室
* 階層: 1階専用フロア
* 入口画像: `static/images/entrances/entrance-kanrinin.png`
* 室内画像: `static/images/kanrinin/kanrinin-room-9x16.png`
* 関連ファイル: `templates/kanrinin.html`, `static/kanrinin.css`, `static/kanrinin.js`, `static/kanrinin-diary.json`, `static/kyoukai-floor.js`, `static/kyoukai-elevator.js`, `main.py`, `tests/test_home_entrances.py`

## コンセプト

管理人室は「管理施設」。Ofuse、BOOTH、クラウドファンディング、SNSへの導線、鍵ボックス、消滅の鍵、管理日誌を持つ。広告ページではなく、昭和から平成初期のラブホテル受付のような空間として扱う。管理人本人は表示しない。

## 現在の実装

9:16背景画像を表示する。画像内には受付カウンター、赤いカーテン、賽銭箱、お知らせ掲示板、BOOTHダンボール、古いパソコン、電話、管理日誌、鍵ボックス、消滅の鍵、目玉が描かれている。

目玉はCSSアニメーションでは描かず、画像に描かれた目玉を黒い領域で覆い隠す。通常時は非表示。呼び鈴を押すと黒い領域が薄れ、目玉がうっすら透けて見える。3秒後に自動で戻る。消滅の鍵を引いた場合は薄い状態のまま固定される。

初回に管理人室へ入るとシナリオモードが開始される。管理人室には `redPhoneArea` があり、赤い電話は条件成立時のみ着信する。管理人室入室後30秒で着信判定を行う。状態は `localStorage` の `kyoukai_scenario_state_v1` に保存される。

## 操作仕様

ユーザーがタッチ・クリックできる場所は以下。

* `ofuseArea`: 賽銭箱。Ofuseへ接続する。
* `boothArea`: BOOTHダンボール。BOOTHへ接続する。
* `crowdfundingArea`: お知らせ掲示板。クラウドファンディングへ接続する。
* `snsArea`: 古いパソコン。SNS一覧モーダルを表示する。
* `bellArea`: 呼び鈴。ランダムメッセージを表示し、目玉を薄く見せる。
* `keyBoxArea`: 鍵ボックスの壁。「開けられない部屋の鍵」モーダルを表示する。
* `annihilationKeyArea`: 消滅の鍵。確認ダイアログなしに即演出を開始し、「管理人が鍵を回しました。」表示、暗転、1.5秒後に `/kanrinin/deleted` へ遷移する。
* `noteArea`: 管理日誌ノート。管理日誌モーダルを開く。
* `redPhoneArea`: 赤い電話。条件成立時のみ着信する。操作結果の詳細はイベントデータ管理。

## 動画化仕様

ShortFACTORYや動画撮影で使う情報を書く。

* 最初に映す場所: 管理人室の9:16背景全体
* 最初に行う操作: `bellArea` を押す
* 次に行う操作: `noteArea` を押して管理日誌モーダルを開く
* 必ず見せる変化: 呼び鈴で目玉がうっすら見える変化
* 推奨尺: 未設定
* 冒頭テロップ案: 未設定
* 終了テロップ案: 未設定

## AI巡回仕様

Playwrightなどで自動巡回する場合の手順を書く。

* 開始URL: `/kanrinin`
* 待機時間: 管理人室入室後30秒で赤い電話の着信判定
* 操作手順: `bellArea` をクリックし、`noteArea` をクリックする。必要に応じて `snsArea`、`keyBoxArea` をクリックする。
* 撮影すべき状態: 目玉が透けて見える状態、管理日誌モーダル、SNS一覧モーダル、鍵ボックスモーダル
* 終了条件: 未設定

## ShortFACTORYメモ

* 使用できる素材: `static/images/kanrinin/kanrinin-room-9x16.png`, `static/images/entrances/entrance-kanrinin.png`
* ズーム推奨箇所: 呼び鈴、カーテンの隙間の目玉、管理日誌、鍵ボックス、消滅の鍵
* 使える一言: 「管理人本人は表示しない」
* 投稿向きの見どころ: 呼び鈴に反応して目玉が薄く見える変化、管理日誌、消滅の鍵
* 不足している情報: 推奨尺、冒頭テロップ案、終了テロップ案

## 未解決

* 動画化時の推奨尺が未設定。
* 冒頭テロップ案、終了テロップ案が未設定。
* 赤い電話の撮影手順は条件成立時のみ着信するため、Routeごとの具体条件整理が必要。
