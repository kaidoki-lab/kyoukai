# Exit修正前 報告書 — 2026-06-17

## 目的

`/exit`（崩壊域・境界域 exit）を修正する前に、現状の実装、関連ファイル、動作仕様、世界観上の位置づけ、修正時の注意点を整理する。

この報告書は、次の実装指示を安全に切るための現状確認資料とする。

---

## 現在のページ概要

| 項目 | 内容 |
|---|---|
| ルート | `/exit` |
| 表示名 | 境界域 / exit / KYOUKAI |
| main.py上の扱い | `exit_room()` が `templates/exit.html` を返す |
| Central OS上の部屋名 | 崩壊域 |
| 世界辞典上の定義 | システムが壊れていく場所。終わりのようだが終わりではない |
| 現在のUI | 9:16縦長フレーム中央表示 |
| 現在の体験 | 複数シーンをタップして進む、接続・脱出風のミニゲーム |
| BGM | `static/bgm.js` 経由で `exit` 用BGMを再生 |

---

## 関連ファイル

### 主要ファイル

| ファイル | 役割 |
|---|---|
| `templates/exit.html` | `/exit`ページ本体 |
| `static/exit.css` | Exit専用スタイル |
| `static/exit.js` | シーン遷移、ホットスポット、ローダー、エンディング制御 |
| `static/bgm.js` | 共通BGMエンジン。`window.KYOUKAI_ROOM = "exit"` でexit用音量・音階に分岐 |
| `central-os/lore/kyoukai-world.md` | 世界辞典。崩壊域の定義元 |

### 画像ファイル

`static/exit/` 以下に本編シーン画像とローディング画像がある。

本編シーン：

| ファイル | 用途 |
|---|---|
| `static/exit/exit_01_hall.png` | hall |
| `static/exit/exit_02_corner.png` | corner |
| `static/exit/exit_03_emergency.png` | emergency |
| `static/exit/exit_04_window.png` | window |
| `static/exit/exit_01b_hall.png` | hall-b |
| `static/exit/exit_02b_corner.png` | corner-b |
| `static/exit/exit_03b_emergency.png` | emergency-b |
| `static/exit/exit_04b_window.png` | window-b |

ローディング：

| ファイル | 用途 |
|---|---|
| `static/exit/loading/loading_01.png`〜`loading_08.png` | 接続中・進行度演出 |

---

## HTML構造

`templates/exit.html` は比較的シンプル。

```text
body.exit-boundary-body
└── main.exit-boundary
    ├── section.exit-stage
    │   ├── img.exit-scene
    │   ├── div.exit-fade
    │   ├── div.exit-touch-layer
    │   │   ├── button.exit-hotspot[data-hotspot=a]
    │   │   ├── button.exit-hotspot[data-hotspot=b]
    │   │   └── button.exit-hotspot[data-hotspot=c]
    │   └── a.exit-return
    ├── section.exit-loader
    │   ├── img.exit-loader__art
    │   ├── div.exit-loader__noise
    │   ├── div.exit-loader__girl
    │   ├── div.exit-loader__bubble
    │   ├── div.exit-loader__status
    │   └── div.exit-loader__text
    └── section.exit-ending
        ├── p.exit-ending__label
        ├── h1.exit-ending__title
        ├── button.exit-ending__continue
        └── a.exit-ending__return
```

フッターは存在しない。  
`/null`のようなサイトマップ・インフォ表示は、`/exit`には現在入っていない。

---

## 現在の表示仕様

### 画面比率

`static/exit.css` では、ステージ・ローダー・エンディングがすべて9:16で固定されている。

```css
.exit-stage,
.exit-loader,
.exit-ending {
  width: min(100vw, calc(100dvh * 9 / 16));
  height: min(100dvh, calc(100vw * 16 / 9));
}
```

PCでもスマホでも縦長の表示になる。  
PCブラウザでは、画面中央に細長いスマホ画面のように出る設計。

### PC表示

`@media (min-width: 780px)` で、さらにサイズ上限がかかる。

```css
width: min(58vh, 469px);
height: min(100dvh - 28px, 833px);
```

そのためPC版は画面いっぱいではなく、中央に縦長フレームとして表示される。

### 背景

ページ背景は暗い赤黒系。  
ゲーム本体の背景は各シーン画像を`img.exit-scene`にJSで差し替える。

---

## JavaScript動作

`static/exit.js` がページ体験の中心。

### シーン

現在のシーンは8種類。

```text
hall
corner
emergency
window
hall-b
corner-b
emergency-b
window-b
```

各シーンは以下を持つ。

| 項目 | 内容 |
|---|---|
| image | 表示画像 |
| pulse | 画面上の光・歪み中心 |
| choices | a/b/cの選択肢。選ぶとスコアが増減 |

### ホットスポット

画面上に3つの透明ボタンがある。

```text
data-hotspot="a"
data-hotspot="b"
data-hotspot="c"
```

ただし位置はCSS固定ではなく、JSの`randomizeHotspots()`で毎回ランダム配置される。

### 進行

1. 初期シーンをランダム選択
2. 3つの透明ホットスポットを配置
3. タップすると`connectionScore`が増減
4. 次のシーンへランダム遷移
5. 一定回数以降はローダー演出が入る
6. 5回目以降に結果判定
7. エンディング表示

### エンディング

現在の結果は5種類。

| id | 表示 |
|---|---|
| escape | 逃走成功 |
| backflow | 逆流 |
| loop | 再ループ |
| collapse | 接続崩壊 |
| drift | 漂流継続 |

実際の表示は以下の形式。

```text
{label} / 観測不能
```

---

## 世界観上の位置づけ

`central-os/lore/kyoukai-world.md` では、`/exit` は以下のように定義されている。

```text
崩壊域（/exit）
システムが壊れていく場所。
- エラーメッセージが美しく崩れていく
- 終わりのような場所だが、終わりではない
- ここを通過すると戻れない感覚（実際には戻れる）
```

現在の実装は「崩壊」「エラー」「出口」よりも、  
「少女が逃げる」「接続先を探す」「脱出ゲーム」に寄っている。

そのため、今後修正する場合は以下のどちらに寄せるかを先に決める必要がある。

1. 既存の少女・脱出ゲーム路線を強化する
2. 世界辞典どおり、システム崩壊・出口不能・美しいエラーへ寄せ直す

---

## 現在の良い点

- 画像素材が8枚あり、シーンの切り替わりに厚みがある
- `exit.js` が専用化されていて、他ページへの影響が少ない
- HTML構造が整理されている
- 透明ホットスポット方式なので、画像差し替えに比較的強い
- ローダー演出、少女シルエット、エンディングがすでにある
- `prefers-reduced-motion` に対応している
- フッターがなく、世界観を壊すサイトマップは表示されていない

---

## 現在の課題

### 1. PC版がスマホ画面の拡大表示に見える

9:16固定なので、PCブラウザでは左右に大きな余白が出る。
悪魔の間や崩落域のように、PC専用16:9画像へ切り替えるなら、`exit`もPC版を別レイアウト化できる。

### 2. 世界辞典とのズレ

世界辞典では「システム崩壊」「エラー」「終わりのようで終わりではない」が核。  
現在は「逃走」「少女」「選択ゲーム」が前に出ている。

### 3. 体験の目的が少し分かりにくい

透明ホットスポットを押すだけなので、初見では何をしているか分かりにくい。  
ただしKYOUKAIでは「説明しすぎない」ことも重要なので、ここは演出で補うのがよい。

### 4. ランダム配置が画像内容とズレる可能性

ホットスポットが毎回ランダム配置されるため、画像内の意味ある場所と一致しないことがある。  
修正するなら、シーンごとに固定座標へ戻すか、ランダム範囲を絞る必要がある。

### 5. 画像差し替え時の影響範囲

`exit.js`内に画像パスが直書きされている。  
画像を変更する場合はJSの`scenes`配列を更新する必要がある。

---

## 修正方針候補

### 案A: PC版だけ16:9化

悪魔の間・崩落域と同じ流れで、PCブラウザ版に専用16:9画像を使う。

変更対象：

- `templates/exit.html`
- `static/exit.css`
- `static/exit.js`
- `static/exit/` 画像追加

メリット：

- PC表示が一気に強くなる
- スマホ版を壊しにくい

注意：

- ホットスポット座標をPC/スマホで分ける必要がある

### 案B: 世界辞典寄りに作り直す

「少女が逃げる」より「システムが壊れていく出口」に寄せる。

変更案：

- 背景をエラー画面、壊れた廊下、赤黒ノイズへ寄せる
- 選択肢を文字ではなく異常箇所のクリックにする
- エンディング文言を「逃走成功」ではなく「接続残留」「出口不成立」などにする

メリット：

- KYOUKAIの世界観に合いやすい

注意：

- 現在の少女演出を弱めるか削除する判断が必要

### 案C: 既存ゲーム性を強化

現状の脱出ゲーム路線を活かす。

変更案：

- クリックした箇所で少女の状態が変わる
- 回数ごとに画像劣化・BGM劣化を強める
- エンディングを増やす

メリット：

- 既存実装を活かせる

注意：

- 世界辞典とのズレが残る

---

## 推奨方針

現時点では **案A + 案Bの一部** がよい。

つまり、

1. PC版だけ16:9化する
2. スマホ版は現在の9:16体験を残す
3. 文言・色・ノイズを「出口不能」「接続崩壊」寄りへ調整する
4. 少女要素は完全削除せず、ローダー内の幽かな存在として残す

この方針なら、既存実装を壊さずに、最近のKYOUKAIの流れにも合わせられる。

---

## 実装時の注意

- `templates/exit.html` は現在フッターなし。サイトマップ削除作業は不要
- CSSは`static/exit.css`専用。古い`static/space.css`にも`/exit`用CSSが残っているが、現在のテンプレートは読んでいない
- `static/space.css`側の古い`.exit-*`定義は、現行`/exit`には直接影響しない
- `static/exit.js`は画像パス、選択肢、ローダー、エンディングをまとめて管理している
- 画像を差し替える場合は、`scenes`配列の`image`を変更する
- ホットスポット位置は現在ランダム。画像内の意味ある位置へ合わせたい場合はJS修正が必要
- BGMは`static/bgm.js`側で`ROOM === "exit"`として低音系の設定あり
- 変更完了後は`complete_implementation.py`でCentral OSへ記録し、関連ファイルだけをコミット・pushする

---

## 次にユーザーへ確認したいこと

1. PC版を16:9化したいか
2. スマホ版は現状維持でよいか
3. 少女演出を残すか、崩壊・エラー演出中心に寄せるか
4. 新しい背景画像を用意するか、既存画像を再加工して使うか
5. 透明ホットスポットを維持するか、見える選択肢にするか

---

## 結論

`/exit`は現在、独立した専用実装として安定している。  
大きく壊さず修正するなら、まずPC版の16:9化と文言・演出の方向調整から入るのが安全。

一方で、世界辞典上の「崩壊域」として強めたいなら、少女脱出ゲーム色を少し抑え、システム崩壊・出口不能・観測不能を前面に出す修正が必要。
