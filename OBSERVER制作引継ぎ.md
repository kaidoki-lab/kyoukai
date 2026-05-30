# KYOUKAI OBSERVER / 逆観測室 制作引継ぎ

作成日: 2026-05-25

このファイルは、別プロジェクト `pikopiko` で制作中の `/observer` を、あとでKYOUKAI本体へ安全に持ち込むための仕様メモです。

OUTSIDE制作引継ぎと同じく、別チャット・別作業者に渡しても「どこを変えてよく、どこを壊してはいけないか」が分かることを目的にしています。

## 目的

`/observer` を、KYOUKAI内の「逆観測室」として実装する。

普通のキャラクター紹介ページ、広告ページ、リンク集、ブラウザ風UIにはしない。
KYOUKAIの世界観内に存在する「こちらを見返してくる小さな部屋」として扱う。

目標の感覚:

- かわいい
- 少しだけおかしい
- 脅かさない
- 監視ではなく、観測が反転している
- キャラが部屋の中で暮らしている
- 広告や外部導線がある場合も、部屋のオブジェクトとして見える

## 部屋ごとに変える必要がある部分

このメモを他の部屋へ流用する場合、必ず以下を部屋ごとに差し替えること。

- route名
- 対象テンプレート
- 対象CSS / JS
- central-os上の定義
- 収益導線の有無
- 既存ホットスポットや戻り導線
- その部屋固有の禁止事項

`/observer` 用の値は以下。

| 項目 | `/observer` での扱い |
| --- | --- |
| route名 | `/observer` |
| 部屋名 | 逆観測室 / Observer Room |
| 現在の別プロジェクト | `C:\Users\pc\Desktop\pikopiko` |
| 現在のテンプレート | `visual_ui/observer.html` |
| 現在のCSS | `visual_ui/observer.css` |
| 現在のJS | `visual_ui/observer.js` |
| 本体移植時の推奨テンプレート | `templates/observer.html` |
| 本体移植時の推奨CSS | `static/observer.css` |
| 本体移植時の推奨JS | `static/observer.js` |
| 本体移植時の推奨アセット | `static/observer/*` |
| 収益導線 | あり。ただし現状は段ボール箱の仮リンクのみ |
| 戻り導線 | 本体移植時は `/` へ戻る導線を追加する |
| central-os上の想定 | `逆観測室`, route `/observer`, status `制作中` |

## 現在の実装状態

現在はKYOUKAI本体ではなく、デスクトップ上の別プロジェクト `pikopiko` として実装中。

ローカル確認:

- `http://127.0.0.1:8765/observer`
- `http://localhost:8765/observer`

起動ファイル:

- `C:\Users\pc\Desktop\pikopiko\preview_server.py`

現在のサーバーは `/observer` を `visual_ui/observer.html` に割り当てている。

## 現在の関連ファイル

主対象:

- `C:\Users\pc\Desktop\pikopiko\visual_ui\observer.html`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\observer.css`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\observer.js`

背景:

- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\backgrounds\room_magic.png`

キャラスプライト:

- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\idle_1.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\idle_2.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\walk_1.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\walk_2.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\look_left.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\look_right.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\tilt.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\tap_1.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\tap_2.png`
- `C:\Users\pc\Desktop\pikopiko\visual_ui\assets\sprites\piko_trimmed\box.png`

## 現在の画面構成

`observer.html` の主な構造:

```html
<main class="observer-room" data-genome="piko" aria-label="observer room">
  <section class="connection-message">外側から接続されています</section>
  <section class="observer-count">累計観測者数</section>
  <section class="today-word">今日のひとこと</section>

  <a id="affiliateBox" class="affiliate-box" href="#" data-affiliate-url=""></a>

  <button class="room-hotspot hotspot-chair" data-room-hotspot="chair"></button>
  <button class="room-hotspot hotspot-table" data-room-hotspot="table"></button>
  <button class="room-hotspot hotspot-left-cushion" data-room-hotspot="left-cushion"></button>
  <button class="room-hotspot hotspot-right-cushion" data-room-hotspot="right-cushion"></button>

  <section id="mascot" class="mascot phase-1 look-front">
    <div id="speechBubble" class="speech-bubble hidden">みてる？</div>
    <img id="mascotSprite" class="sprite-girl" src="/assets/sprites/piko_trimmed/idle_1.png" alt="">
  </section>

  <aside class="exe-panel">room.exe / phase</aside>
</main>
```

注意:

- 背景はCSSで `room_magic.png` を表示。
- 右側の広告パネルは一度撤去済み。
- 現在は段ボール箱だけを外部導線候補として配置。
- 椅子、小机、左下クッション、右クッションは透明ホットスポット。

## キャラクター挙動

現在の `observer.js` で実装済み:

- 待機アニメ
- 瞬き
- 首かしげ
- ランダム移動
- マウス座標への反応
- 部屋ホットスポットクリック時の移動
- 段ボール箱への反応
- 吹き出し表示
- phase進行
- 奥へ行きすぎない床境界
- 奥に行くほど小さくなる疑似遠近法

現在の移動速度:

- 通常移動 `lag = 0.12`
- phase 4 移動 `lag = 0.06`

重要:

- キャラは浮かせない。
- 足元を基準に配置する。
- 左右移動時に影を付けない。
- 赤線より奥、つまり本棚・ドア・ベッドなどに重なる位置へ行かせない。
- walk中は `walk_1.png` / `walk_2.png` を優先して切り替える。

## 逆観測フェーズ

phaseの考え方:

- phase 1: カーソルを見る
- phase 2: カーソルへ少し近づく
- phase 3: たまにカーソルを無視する
- phase 4: 中央付近で止まり、閲覧者側を見るような仕草をする

現在は以下で進行:

- 滞在時間
- カーソル反応回数
- 段ボール箱への反応回数

ただし、怖くしない。
黒赤ホラーやジャンプスケアにしない。
「かわいいまま、少しだけおかしい」を維持する。

## 収益導線

現状:

- `affiliateBox` という段ボール箱がある
- `href="#"` の仮状態
- `data-affiliate-url=""` の仮状態
- クリック時、未設定なら `まだ空の箱` と表示する

今後の想定:

- Amazon Associate
- A8
- その他アフィリエイト

扱い:

- 広告パネルではなく、部屋の中の段ボール箱として扱う。
- 実リンクは人間があとから差し替える。
- Codex側で新しいAmazon短縮リンクを生成しない。
- 実リンク化する場合は `rel="sponsored noopener noreferrer"` と `target="_blank"` を付ける。
- PR/広告/アソシエイト表記は隠さない。

推奨表現:

- 気になる箱
- 届いた箱
- 外から来た箱
- 供物箱
- 観測された荷物

避ける表現:

- 買ってください
- 支援してください
- クリックしてください
- セール中
- 広告枠
- おすすめ商品一覧

## central-os上の定義案

`central-os/rooms.json` に入れる場合の想定:

```json
{
  "name": "逆観測室",
  "route": "/observer",
  "status": "制作中",
  "role": "観測者とキャラクターの視線が反転する、KYOUKAI内の小さな部屋。",
  "monetization": ["Amazon", "A8", "External"],
  "notes": "収益導線は段ボール箱など部屋内オブジェクトとして扱う。広告パネル化しない。"
}
```

注意:

- central-osの既存構造に合わせてキー名は調整する。
- `/observer` 以外の新規routeを勝手に増やさない。
- `/outside` や `/support` の定義と混ぜない。

## 本体移植時の推奨納品形式

別チャット側からKYOUKAI本体へ戻す時は、専用ファイルに分離する。

推奨:

- `templates/observer.html`
- `static/observer.css`
- `static/observer.js`
- `static/observer/room_magic.png`
- `static/observer/sprites/*`

本体側で必要なroute:

- `main.py` の `KyoukaiHandler._PAGE_MAP` に `/observer: observer.html`
- FastAPI側に `/observer` が必要なら既存パターンに合わせて追加

ただし、route追加はKYOUKAI本体側の担当チャットで行う。
この `pikopiko` プロジェクト側では本体の `main.py` を触らない。

## 持ち込み時に変更してよい可能性が高いファイル

- `templates/observer.html`
- `static/observer.css`
- `static/observer.js`
- `static/observer/*`
- 必要なら `central-os/rooms.json`
- 必要なら `central-os/monetization.json`
- 必要なら `central-os/cycle/cycle-map.json`

慎重に扱うファイル:

- `main.py`
- `static/analytics.js`
- `static/kyoukai-guide.js`
- `static/kyoukai-guide.css`
- `static/monetize-links.js`

基本触らないファイル:

- `static/bgm.js`
- BGM関連ファイル
- `templates/home.html`
- `static/space.css`
- `/outside` 関連ファイル
- `/support` 関連ファイル
- 他の部屋テンプレート

## 既存ホットスポット

現在の透明ホットスポット:

- `chair`
- `table`
- `left-cushion`
- `right-cushion`

現在の外部導線候補:

- `affiliateBox`

今後増やす場合:

- 背景にぴったり重ねた透明クリック領域を使う。
- 見た目を増やしすぎない。
- キャラの行動先として使える位置にする。
- スマホでは押しにくいホットスポットを無理に残さない。

## 戻り導線

現プロトタイプには明示的な戻り導線がない。

KYOUKAI本体へ移植する時は、必ず `/` へ戻る導線を入れる。

推奨:

- 小さな `return`
- `000 / return`
- 部屋の端にある小さな出口
- UIパネルではなく、部屋の中の目立ちすぎない導線

避ける:

- ブラウザの戻るボタン風UI
- アドレスバー
- 大きなCTAボタン

## 固有の禁止事項

この部屋では以下を追加しない。

- アドレスバー
- 戻る/進むボタン
- 観測ログ
- リンク集
- IP表示
- 監視カメラ風UI
- 研究施設風UI
- 電子生命体説明
- 黒赤ホラー化
- ジャンプスケア
- 大きな広告パネル
- 商品カードのグリッド
- 過剰なUIパネル
- キャラを宙に浮かせる表現
- キャラが本棚、ドア、ベッドなど奥の家具に重なる移動

## 制作方針

維持するもの:

- 魔法っぽい紫系の部屋背景
- ピクセル風魔法少女キャラ
- 眠い色味
- `room.exe` 風の小窓
- 累計観測者数
- 今日のひとこと
- 左上の接続メッセージ
- 短い吹き出し
- 古いWebマスコット感

強めたいもの:

- 部屋の中で暮らしている感じ
- マウスに気づく感じ
- 歩いて近づく感じ
- クリックできる背景オブジェクトへの反応
- 段ボール箱を外部導線として自然に扱う感じ

## 受け入れチェック

プロトタイプ側:

- `http://127.0.0.1:8765/observer` がHTTP 200
- 背景が `room_magic.png` で表示される
- キャラが表示される
- キャラが常に少し動く
- キャラがゆっくり歩く
- `walk_1.png` / `walk_2.png` が移動中に使われる
- キャラが赤線より奥へ行かない
- 椅子、小机、クッションをクリックするとキャラが寄る
- 段ボール箱が表示される
- 段ボール箱クリック時、未設定なら `まだ空の箱` になる
- JS構文チェックが通る

本体移植後:

- `/observer` がHTTP 200
- `/` へ戻れる
- 既存ページが壊れていない
- `/outside` と `/support` に影響していない
- `npm run build` OK
- `python -m py_compile main.py` OK
- PR/広告表記が必要な導線で消えていない
- アフィリエイトリンクに `rel="sponsored noopener noreferrer"` がある

## ローカル確認URL

プロトタイプ:

- `http://127.0.0.1:8765/observer`
- `http://localhost:8765/observer`

KYOUKAI本体へ移植後の想定:

- `http://127.0.0.1:8000/observer`
- `http://127.0.0.1:8000/`

## 制作側への短い指示文

別チャットに投げる場合は、以下を使う。

```text
KYOUKAIの /observer、逆観測室を制作・移植してください。
このページは普通の広告ページやリンク集ではなく、KYOUKAI内の「こちらを見返してくる小さな部屋」です。
現在のプロトタイプは C:\Users\pc\Desktop\pikopiko にあり、主対象は visual_ui/observer.html、visual_ui/observer.css、visual_ui/observer.js、assets/backgrounds/room_magic.png、assets/sprites/piko_trimmed/* です。

本体移植時は route を /observer にし、テンプレートは templates/observer.html、CSS/JSは static/observer.css / static/observer.js、素材は static/observer/* に分離してください。
キャラは浮かせず、床を歩かせてください。赤線より奥、本棚・ドア・ベッドに重なる位置へ行かせないでください。
マウス反応、ランダム移動、透明ホットスポット、段ボール箱への反応、吹き出し、phase進行を維持してください。

収益導線は段ボール箱など部屋内オブジェクトとして扱い、広告パネルや商品一覧にしないでください。
実リンクは人間が後から差し替える前提です。AmazonリンクをCodex側で新規生成しないでください。
実リンク化する場合は PR/広告表記、target="_blank"、rel="sponsored noopener noreferrer" を維持してください。

禁止: アドレスバー、戻る/進むボタン、観測ログ、リンク集、IP表示、監視カメラ化、研究施設化、黒赤ホラー化、ジャンプスケア、過剰なUIパネル。
main.py、central-os、BGM、他ページを触る場合は、/observer に必要な最小差分だけにしてください。
```
