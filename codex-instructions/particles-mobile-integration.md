# 実装指示書 — 粒子生成構造体観測システム スマホ版 KYOUKAI組み込み

## 目的

`/particles` ページをKYOUKAI内の観測室として正式に組み込む。
スマホ縦表示（9:16比率）に最適化し、既存ページから自然に到達できる導線を1本追加する。

---

## 前提知識

- KYOUKAIはFastAPI + Jinja2テンプレートのサイト
- ルートは `main.py` に定義
- テンプレートは `templates/` 以下
- 静的ファイルは `static/` 以下
- `/particles` ルートと `templates/particles.html` はすでに存在する
- 粒子エンジン本体は `static/particle-engine.js`（変更禁止）

---

## 実装対象ファイル

```
templates/particles.html     ← 主要変更対象
templates/observer.html      ← 導線追加のみ（最小変更）
static/particles.css         ← 新規作成
```

`main.py` は変更不要（ルートはすでに存在する）。

---

## TASK 1 — particles.html をスマホ最適化

### 現状

`templates/particles.html` は全画面canvasのみ。
PCでもスマホでも `window.innerWidth × window.innerHeight` をそのまま使っている。

### 変更内容

**スマホ縦表示（portrait）のとき、canvasを9:16比率で中央配置する。**
PC横表示（landscape）のときは現状通り全画面。

#### `templates/particles.html` の書き換え

```html
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>粒子生成構造体観測システム / KYOUKAI</title>
    <link rel="stylesheet" href="/static/particles.css" />
    <script defer src="/static/analytics.js"></script>
  </head>
  <body>
    <div id="stage">
      <canvas id="c"></canvas>
    </div>
    <script src="/static/particle-engine.js"></script>
    <script>
      (function () {
        var canvas = document.getElementById('c');
        var stage  = document.getElementById('stage');
        var engine = null;

        function isPortrait() {
          return window.innerHeight > window.innerWidth;
        }

        function resize() {
          var vw = window.innerWidth;
          var vh = window.innerHeight;

          if (isPortrait()) {
            // スマホ縦: 9:16 中央配置
            var ratio = 9 / 16;
            var cw = vw;
            var ch = Math.round(cw / ratio);
            if (ch > vh) { ch = vh; cw = Math.round(ch * ratio); }
            canvas.width  = cw;
            canvas.height = ch;
            canvas.style.width    = cw + 'px';
            canvas.style.height   = ch + 'px';
            canvas.style.position = 'absolute';
            canvas.style.left     = Math.round((vw - cw) / 2) + 'px';
            canvas.style.top      = Math.round((vh - ch) / 2) + 'px';
          } else {
            // PC横: 全画面
            canvas.width  = vw;
            canvas.height = vh;
            canvas.style.width    = '100%';
            canvas.style.height   = '100%';
            canvas.style.position = 'fixed';
            canvas.style.left     = '0';
            canvas.style.top      = '0';
          }
        }

        resize();
        window.addEventListener('resize', resize);

        engine = new ParticleObservationEngine(canvas, {
          observerEffect: true,
        });
        engine.start();
      })();
    </script>
  </body>
</html>
```

---

## TASK 2 — particles.css を新規作成

```
static/particles.css
```

```css
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

html, body {
  width: 100%; height: 100%;
  overflow: hidden;
  background: #000;
}

#stage {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
}

canvas {
  display: block;
}
```

---

## TASK 3 — observer.html に導線を1本追加

### ルール

- UIや説明文を出さない
- 世界観を壊すテキストを使わない
- 視覚的に目立ちすぎない（隠し要素レベルでよい）
- タップ/クリックで `/particles` に遷移する

### 実装方針

`templates/observer.html` の `</body>` 直前に以下のscript要素を追加する。

```html
<script>
  (function () {
    // 長時間観測後に粒子接続ポイントが出現する（観測者効果）
    var threshold = 18000; // 18秒
    var shown = false;

    setTimeout(function () {
      if (shown) return;
      shown = true;

      var link = document.createElement('a');
      link.href = '/particles';
      link.style.cssText = [
        'position:fixed',
        'bottom:18px',
        'right:18px',
        'width:8px',
        'height:8px',
        'border-radius:50%',
        'background:rgba(255,220,30,0.55)',
        'display:block',
        'text-decoration:none',
        'cursor:pointer',
        'z-index:50',
        'animation:pobs-pulse 2.4s ease-in-out infinite',
      ].join(';');
      link.setAttribute('aria-hidden', 'true');

      var style = document.createElement('style');
      style.textContent = '@keyframes pobs-pulse{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:.9;transform:scale(1.5)}}';
      document.head.appendChild(style);
      document.body.appendChild(link);
    }, threshold);
  })();
</script>
```

---

## 完成条件

- [ ] スマホ縦画面（iOS Safari / Android Chrome）で `/particles` を開いたとき、canvasが9:16比率で中央表示される
- [ ] PC横画面では全画面表示される
- [ ] `/observer` に18秒以上滞在すると黄色い小さな点が右下に出現し、タップで `/particles` に遷移する
- [ ] KYOUKAIの他ページ（`/`, `/observation`, `/null` など）が正常表示される
- [ ] コンソールにエラーが出ない
- [ ] 粒子が正常に動作する（PHASE1〜7）

---

## 変更禁止

- `static/particle-engine.js`
- `main.py` のルーティング以外の部分
- 既存のすべてのページの機能・見た目
- KYOUKAIのゲノムシステム関連コード
- アナリティクス・アフィリエイト関連コード
- 認証・DBまわりのコード

---

## 参照ファイル（読み取りのみ）

実装前に以下を確認すること：

- `templates/observer.html` — 追加先の構造確認
- `static/particle-engine.js` — エンジンのAPI確認（`ParticleObservationEngine` クラス）
- `templates/particles.html` — 現状確認

---

## 実装サイズ

small（3ファイル以下、既存機能に触れない）
