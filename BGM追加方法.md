# KYOUKAI BGM 追加方法

## ファイルを置くだけで動く

`static/bgm/` フォルダに対応ファイルを置く。

| ファイル名 | 対応ページ |
|---|---|
| `bgm_home.mp3` | `/`（入口） |
| `bgm_observation.mp3` | `/observation`（観測室） |
| `bgm_archive.mp3` | `/archive`（記録室） |
| `bgm_exit.mp3` | `/exit`（脱出室） |
| `bgm_null.mp3` | `/null`（崩落域） |

ファイルが存在しないページはBGMなし（エラーにはならない）。

---

## 対応フォーマット

- `.mp3`（推奨）
- `.ogg`（mp3の代わりに使う場合はファイル名の拡張子も変える）

---

## ファイル名を変えたい場合

`static/bgm.js` の先頭付近にある以下の行を変更する：

```js
var BGM_SRC = '/static/bgm/bgm_' + ROOM + '.mp3';
```

例：ogg形式にする場合
```js
var BGM_SRC = '/static/bgm/bgm_' + ROOM + '.ogg';
```

---

## BGMの仕組み

- ページを開いて**最初のクリック・キー操作**で自動再生（ブラウザの自動再生制限のため）
- 右下に小さな `音 ▶` ボタンが表示される
- クリックで再生 / ミュート切り替え
- 8秒ごとに Genome 状態を取得してエフェクトが自動変化

---

## Genome連動エフェクト一覧

| Genome状態 | 音の変化 |
|---|---|
| `trait_distance` 上昇 | ローパスフィルター → こもり感 |
| `trait_softness` 上昇 | リバーブ増加 → 残響・霧感 |
| `trait_corruption` 上昇 | ディストーション → 歪み・腐食 |
| `trait_aggression` 上昇 | ハイパス + 歪み → 鋭さ |
| `trait_gaze` 上昇 | トレモロ → 揺れ |
| `audio_instability` 上昇 | デチューン + グリッチ |
| `phase_drift` 上昇 | ピッチ揺れ |
| `phase` 上昇（0→3） | 全体的にこもり・残響が深まる |

---

## GitHubへのプッシュ手順

ファイルを追加・変更したあと：

```powershell
cd C:\Users\pc\Documents\Claude\Projects\kyoukai
git add static/bgm/
git commit -m "add: BGMファイル追加"
git push origin main
```

ロックエラーが出た場合：
```powershell
Remove-Item C:\Users\pc\Documents\Claude\Projects\kyoukai\.git\index.lock
```
削除後に `git add` からやり直す。
