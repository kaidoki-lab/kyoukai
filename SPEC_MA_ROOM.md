# SPEC: 悪魔の間（/ma）— 実装仕様書

作成日: 2026-06-15  
対象ブランチ: main（未コミット状態）

---

## 概要

KYOUKAIサイトの隠し部屋。`/observer` ページの中央ドア（「?」マーク）からのみアクセスできる。  
訪問するたびに会話が進行し、悪魔「大魔将」との関係が変化していく。

---

## ファイル構成

| ファイル | 状態 | 役割 |
|---|---|---|
| `templates/ma.html` | 新規作成 | 悪魔の間ページ本体 |
| `static/ma.css` | 新規作成 | スタイル・アニメーション |
| `static/ma.js` | 新規作成 | 会話エンジン・訪問カウンタ |
| `static/kyoukai_ma_bg.jpg` | 新規追加 | スマホ用9:16背景画像（悪魔・玉座） |
| `static/kyoukai_ma_bg_desktop.png` | 新規追加 | ブラウザ用16:9背景画像（悪魔・玉座） |
| `main.py` | 修正 | `/ma` ルート追加 |
| `templates/observer.html` | 修正 | 隠し扉ホットスポット追加 |
| `static/observer.css` | 修正 | `.ma-gate` スタイル追加 |

---

## ルート

```python
# main.py（/outside ルートの直後に追加済み）
@app.get("/ma", response_class=HTMLResponse)
async def ma_room(request: Request) -> HTMLResponse:
    return render_template(request, "ma.html")
```

---

## ページ構造（ma.html）

```
body.ma-body
├── div.ma-bg               ← 背景全画面
│   ├── div.ma-glow         ← 赤いグロー（呼吸アニメ）
│   └── div.ma-fade         ← 下部フェードアウト（黒パネルへの接続）
└── div.ma-panel            ← 下部 30vh 固定パネル（黒背景）
    ├── div.ma-speaker      ← 話者名表示
    ├── div.ma-text         ← 会話テキスト（タイプライター表示）
    └── button.ma-next      ← ▼ ボタン（タイピング完了後に出現）
```

- `noindex, nofollow` 設定済み（検索エンジン非公開）
- ナビゲーション・フッターなし

---

## CSS（ma.css）

### 背景

```css
/* ブラウザ版 */
background-image: url("/static/kyoukai_ma_bg_desktop.png");
background-size: cover;
background-position: center center;

/* 画面幅768px以下のスマホ版 */
background-image: url("/static/kyoukai_ma_bg.jpg");
background-size: auto 100%;      /* 9:16画像を縦いっぱいに表示 */
```

### アニメーション

| クラス名 | 内容 |
|---|---|
| `ma-image-drift` | 背景画像の緩やかなズーム・上下移動（ブラウザ12秒、スマホ15秒） |
| `ma-breathe` | 赤グローの呼吸（4秒ループ、opacity 0.6→1.0） |
| `ma-blink` | ▼ボタンの点滅（1.6秒ループ） |
| `ma-shake` | 画面シェイク（0.35秒、次ページ遷移前に発動） |

### パネル

- ブラウザ版は悪魔の足元へ重なる半透明パネル（最大幅980px、本文24〜34px）
- ブラウザ版パネルは画面下端から約11vh上へ配置
- スマホ版は従来どおり下部30vh固定パネル（本文14〜18px）
- スマホ版は`background: #000`、`border-top: 1px solid #330000`
- テキスト色: `#cccccc`、話者名色: `#660000`

---

## JS（ma.js）

### 訪問カウンタ

```javascript
var STORAGE_KEY = 'kyoukai_ma_visits';
// localStorageにアクセス回数を保存。ページ表示ごとに+1
```

### 会話データ（CONVS配列・15段階）

| 訪問回 | 話者 | 内容 |
|---|---|---|
| 1 | `???` | ……帰れ。 |
| 2 | `???` | またお前か。\n用はない。 |
| 3 | `???` | しつこい奴だ。\n……好きにしろ。 |
| 4 | `大魔将` | ……名を教えてやろう。大魔将だ。（名前開示） |
| 5 | `大魔将` | 何しに来た。ここには何もないぞ。 |
| 6 | `大魔将` | ……少しだけ、暇だった。 |
| 7 | `大魔将` | 貴様は物好きだな。人間にしては、悪くない。 |
| 8 | `大魔将` | この場所を、気に入っているか。 |
| 9 | `大魔将` | 闇とはな、恐ろしいものではない。ただ、静かなのだ。 |
| 10 | `大魔将` | ……少し、聞いてもいいか。お前はなぜ、ここに来る。 |
| 11 | `大魔将` | そうか。……俺も、同じかもしれんな。 |
| 12 | `大魔将` | 長居はするな。……ただし、また来ることは許す。 |
| 13 | `大魔将` | 待っていたわけでは、ない。だが、来ると思っていた。 |
| 14 | `大魔将` | 貴様のことが、少しだけ分かってきた気がする。 |
| 15〜 | `大魔将` | 来たか。……ゆっくりしていけ。（ループ） |

### 動作フロー

1. ページ読み込み → 訪問回数+1、該当会話を選択
2. 話者名を即時表示
3. テキストをタイプライター表示（50ms/文字）
   - Web Audioが利用可能な場合、数文字ごとに低い声風の短音を再生
   - 自動再生が制限された環境では、最初のタップまたはキー操作後に音声を有効化
4. タイピング完了 → ▼ボタン出現
5. クリック or Enter or Space or ↓ キー
   - タイピング中ならスキップ（全文即時表示）
   - タイピング完了後ならシェイク → 380ms後 `/observer` に戻る

---

## observer.html への追加（隠し扉ホットスポット）

```html
<!-- observer.html: #outsideBox の直後 -->
<a id="maGate" class="ma-gate" href="/ma" aria-hidden="true" tabindex="-1"></a>
```

---

## observer.css への追加（ホットスポット位置）

```css
.ma-gate {
  position: absolute;
  left: calc(var(--observer-frame-left) + var(--observer-frame-width) * 0.42);
  top: 38vh;
  z-index: 38;
  display: block;
  width: calc(var(--observer-frame-width) * 0.16);
  height: 20vh;
  text-decoration: none;
  cursor: default;
}
```

テスト用の赤ボックスは削除済み。

---

## 未コミットの変更ファイル一覧

```
M  main.py
M  static/observer.css
M  templates/central.html      ← Central OS ブラッシュアップ（別タスク）
M  templates/observer.html
?? static/kyoukai_ma_bg.jpg
?? static/kyoukai_ma_bg_desktop.png
?? static/ma.css
?? static/ma.js
?? templates/ma.html
```

---

## 残タスク

- [x] `observer.css` の `.ma-gate` からテスト用赤ボックスを削除
- [ ] ホットスポット位置の最終調整（左右・上下）
- [ ] 全変更をコミット・push
- [ ] 本番（`https://void-kyoukai.net/`）での動作確認

---

## 座標系の参考

observer ページのフレーム変数：

```css
--observer-frame-width: min(100vw, calc(100vh * 9 / 16));
--observer-frame-left:  calc((100vw - var(--observer-frame-width)) / 2);
```

背景画像の「?」ドアはフレーム内ほぼ中央（横42〜58%、縦38〜58%あたり）に位置する。
