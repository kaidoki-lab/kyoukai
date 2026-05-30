# KYOUKAI OUTSIDE 制作引継ぎ

作成日: 2026-05-24

このファイルは、`/outside` を別チャット・別作業で制作し、あとでこのKYOUKAI本体へ安全に持ち込むための仕様メモです。

## 目的

`/outside` を、KYOUKAI内の「外部接続」空間として作り直す。

ただし、普通の広告ページやリンク集にはしない。
KYOUKAIの世界観内に存在する「外につながってしまった部屋」「境界外の棚」「漂着物置き場」として制作する。

## 現在の実装状態

現在の `/outside` は実装済み。

ルート:

- `/outside`
- `/support`

どちらも `templates/outside.html` を返す。

`main.py` 側:

- `KyoukaiHandler._PAGE_MAP`
  - `/outside`: `outside.html`
  - `/support`: `outside.html`
- FastAPI route
  - `@app.get("/outside")`
  - `@app.get("/support")`

重要:

- `/support` は `/outside` と同じテンプレートを使う別名ルート。
- 新規routeを勝手に増やさない。
- `/outside` と `/support` の互換は維持する。

## 現在の関連ファイル

主対象:

- `templates/outside.html`
- `static/monetize-core.css`
- `static/monetize-core.js`
- `static/monetize-links.js`

関連:

- `static/kyoukai-guide.js`
- `static/kyoukai-guide.css`
- `static/analytics.js`
- `central-os/rooms.json`
- `central-os/monetization.json`
- `central-os/cycle/cycle-map.json`

現在の `templates/outside.html` はかなり薄い。

構造:

```html
<body class="outside-core-body" data-monetize-page="outside">
  <main class="outside-core">
    <header class="outside-core__header">
      <span>KYOUKAI / EXTERNAL NODE</span>
      <h1>OUTSIDE</h1>
      <p>A small external room found past the boundary. Objects remain here without guidance.</p>
    </header>

    <div class="ky-outside-list" data-monetize-list></div>

    <a class="outside-core__return" href="/">000 / return</a>
  </main>
</body>
```

`data-monetize-list` に `static/monetize-core.js` がリンクカードを描画する。

## 現在の外部リンク定義

`static/monetize-links.js` で定義。

現在の構造:

```js
window.KYOUKAI_MONETIZE_LINKS = {
  sections: [
    {
      id: "carry",
      title: "FOUND OBJECTS",
      note: "Items detected outside the boundary.",
      items: [
        {
          label: "ALTAR ARTIFACT",
          body: "An external object left near the entrance.",
          href: "https://amzn.to/4nIXnSI",
          rel: "sponsored noopener noreferrer",
          target: "_blank",
          disclosure: "PR / Amazon Associate link"
        }
      ]
    }
  ]
};
```

現在入っているAmazon短縮リンク:

- `https://amzn.to/4nIXnSI`
- `https://amzn.to/4dnRLtB`
- `https://amzn.to/42OSmOR`

注意:

- Amazonリンクは人間が貼る運用。
- 制作側で新しいAmazonリンクを生成しない。
- PR表記、`rel="sponsored noopener noreferrer"`、`target="_blank"` は維持。
- 収益導線は世界観内オブジェクトとして扱う。

## OFUSE情報

OFUSEリンク:

- `https://ofuse.me/be78f6ed`

現在トップページの賽銭箱ホットスポットに接続済み。

`/outside` に入れる場合も、普通の「支援ボタン」ではなく、以下のような扱いにする。

OK表現:

- 小さな箱
- 外へ落ちる箱
- 見た人の気配が残る場所
- 供物受付
- 境界維持箱

NG表現:

- 支援してください
- 寄付してください
- OFUSEしてください
- 課金してください
- ここをクリックしてください

## central-os上の定義

`central-os/rooms.json` では、外部接続は以下の扱い。

- name: `外部接続`
- route: `/outside`
- status: `実装済み`
- role: `外部サービス・アフィリエイト・収益導線へのゲートウェイ。`
- monetization:
  - `OFUSE`
  - `Amazon`
  - `External`

`/support` について:

- `/support` は main.py に存在する。
- central-os上では「外部接続の別名候補」として扱う。
- 独立した新ページとは限らない。

賽銭箱について:

- central-os上では `賽銭箱` は route `未確定`。
- 現状はトップの賽銭箱ホットスポットでOFUSEへ直接接続。
- `/outside` 内に賽銭箱要素を入れる場合も、新規routeは作らない。

## 制作方針

目指す体験:

- 「外側に出た」というより「外側のものが流れ込んできた場所」
- リンク集ではなく、空間内の棚・自販機・漂着物・端末として見せる
- 初見でも操作できるが、説明しすぎない
- 収益導線は見えるが、広告っぽくしない
- PR表記は隠さない
- スマホでも押せる

推奨モチーフ:

- 境界外の自動販売機
- 漂着物棚
- 外部信号端末
- 供物箱
- 壊れた通販端末
- QR/Shorts用の観測ポート
- 「外の棚」

避けるもの:

- 一般的なLP
- 商品カードのグリッドだけ
- 大きなCTAボタン
- 「買う」「支援する」を前面に出す構成
- 世界観と無関係な明るいECデザイン
- 新規route追加

## 画面構成案

制作側で自由に設計してよいが、持ち込みやすい構成は以下。

1. full viewportのOUTSIDE空間
2. 背景またはメインビジュアル
3. クリック可能なオブジェクト
   - Amazon漂着物
   - OFUSE箱
   - Shorts/QRポート
   - return導線
4. PR/Associate表記
5. 案内人読み込みは既存のまま

## 必須導線

戻る導線:

- `/`

外部接続候補:

- Amazonリンク
- OFUSEリンク
- `/outside?utm_source=youtube&utm_medium=shorts&utm_campaign=outside_core`

`/support` から来ても同じページとして自然に成立すること。

## GA4 / analytics

`templates/outside.html` は `static/analytics.js` を読み込み済み。

維持すること:

```html
<script defer src="/static/analytics.js"></script>
```

追加でGoogle Analyticsを入れ直さない。
外部解析ツールを勝手に追加しない。

## 案内人

`/outside` は紹介案内システム対象。

維持すること:

```html
<link rel="stylesheet" href="/static/kyoukai-guide.css" />
<script defer src="/static/kyoukai-guide.js"></script>
<body data-monetize-page="outside">
```

`kyoukai-guide.js` は `data-monetize-page="outside"` を見て roomId を `outside` と認識できる。

## 納品形式

別チャット側から戻す時は、以下のどちらかが安全。

### A. 既存ファイル差し替え型

納品ファイル:

- `templates/outside.html`
- `static/outside.css`
- `static/outside.js`
- 必要な画像や音素材 `static/outside/`

この場合、`templates/outside.html` で新CSS/JSを読む。
既存 `monetize-core.*` は残してもよいが、使わないなら影響が出ないようにする。

### B. 既存monetize拡張型

納品ファイル:

- `templates/outside.html`
- `static/monetize-core.css`
- `static/monetize-core.js`
- `static/monetize-links.js`

この場合、現在のリンク描画構造を活かして拡張する。
ただし他ページの `ky-monetize-route` に影響しやすいので注意。

推奨は A。
`/outside` 専用の `outside.css` / `outside.js` に分離した方が持ち込みやすい。

## 持ち込み時に変更してよい可能性が高いファイル

- `templates/outside.html`
- `static/outside.css`
- `static/outside.js`
- `static/outside/*`
- 必要なら `static/monetize-links.js`

慎重に扱うファイル:

- `static/monetize-core.css`
- `static/monetize-core.js`

基本触らないファイル:

- `main.py`
- `central-os/`
- `static/bgm.js`
- `templates/home.html`
- `static/space.css`
- 他の部屋テンプレート

## 既存未コミット差分への注意

このメモ作成時点で、BGM関連の未コミット差分が残っている。

BGM関連:

- `static/bgm.js`
- `BGM追加方法.md`
- `static/bgm/bgm_home.mp3`

OUTSIDE制作とは混ぜない。

## 実装時の安全ルール

- `git add .` 禁止
- BGM関連を混ぜない
- `main.py` にroute追加しない
- `/observer` など未実装routeを実装しない
- AmazonリンクをCodex側で新規生成しない
- PR表記を消さない
- OFUSEを強い支援ボタンにしない
- スマホで主要オブジェクトが押せること
- return導線を必ず残す

## 受け入れチェック

持ち込み後に確認すること。

- `/outside` がHTTP 200
- `/support` がHTTP 200
- `/outside` と `/support` が同じ体験として破綻しない
- `/` へ戻れる
- Amazonリンクに `rel="sponsored noopener noreferrer"` がある
- PR/Associate表記が見える
- OFUSEリンクを入れた場合、直接的な支援表現になっていない
- `kyoukai-guide.js` が壊れていない
- `npm run build` OK
- `python -m py_compile main.py` OK
- 既存routeが壊れていない

## ローカル確認URL

- `http://127.0.0.1:8000/outside`
- `http://127.0.0.1:8000/support`
- `http://127.0.0.1:8000/`

## 現在のGitHub

Repository:

- `https://github.com/yodomasa1109-bit/kyoukai.git`

最新push済み付近:

- `007771d Add altar aha fade image`

## 制作側への短い指示文

別チャットに投げる場合は、以下を使う。

```text
KYOUKAIの /outside を制作してください。
このページは普通の広告ページではなく、KYOUKAI内の「外部接続」空間です。
既存routeは /outside と /support。新規routeは追加しません。
Amazon/OFUSE/外部導線は、広告ボタンではなく、空間内の漂着物・外の棚・供物箱として扱ってください。
PR表記と sponsored rel は消さないでください。
納品は templates/outside.html、static/outside.css、static/outside.js、必要なら static/outside/* の形が望ましいです。
main.py、central-os、BGM関連、他ページは触らないでください。
```
