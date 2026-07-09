# ROADMAP — KYOUKAI OBSパック 部屋別個性化リニューアル

作成日: 2026-07-09
前ラウンド: `ROADMAP_BOOTH販売展開_完了.md`（パイプライン構築・全16パック生成済み）

---

## 1. ゴール定義

### 最大ゴール（将来像・工程化しない）

- 16部屋すべてが「その部屋でしか成立しない配信演出」を持ち、パックを見ただけでどの部屋か判別できる状態。
- 素材が配信中に時間経過・視聴者の存在に反応する「観測される配信画面」としてシリーズ全体が確立し、KYOUKAI本体への導線として機能する。
- WebM版・カスタマイズGUI・英語版READMEを含む上位版パックの展開。

### 必達ゴール（本ラウンドの完成条件）

1. **brb**: 全部屋同一のTVスタティックを廃止し、16部屋それぞれが専用のCanvas演出＋専用レイアウトを持つ。任意の2部屋のbrb.htmlを並べたとき、テキストを隠しても見分けられる（背景演出・画面構成・動きがコード上で異なる）。
2. **waiting**: 現状の共通レイアウト(四隅コーナー+freq-block+source-block+bottom-bar)を部屋別に再構成する。全部屋同一のUI骨格をやめ、部屋ごとにUI部品の種類・配置が異なる（例: 悪魔の間は玉座中央配置で計器類なし、台風ニュースは速報帯+情報パネル構成）。
3. **lower_third**: 色違いを廃止し、部屋ごとに形状・装飾・動きが異なる名前テロップにする（例: 波紋域は名前の周囲に波紋、悪魔の間は玉座の紋様枠、台風ニュースは速報テロップ形式）。
4. 生成は `booth/generate_packs.py` のデータ駆動を維持する。部屋別テンプレートは `booth/room_specs/<部屋ID>.py` に分離し、`generate_packs.py` が読み込む構造にする。
5. 再生成後、前ラウンドのパイプライン一式（verify_packs / screenshot_packs / make_thumbnails / final_check）が全pass し、zip17本・サムネイル64枚が新デザインで更新されている。
6. 検証可能な差別化基準: 各部屋の3ファイルについて、部屋固有のCSSクラス名またはCanvas描画関数が最低3つ存在すること（`verify_packs.py` 拡張でチェック）。

---

## 2. 全体アーキテクチャ

### 採用技術

| 要素 | 技術 | 理由 |
|---|---|---|
| 部屋別テンプレート | `booth/room_specs/<部屋ID>.py`（1部屋1ファイル） | 16部屋×3素材の演出コードを1ファイルに詰めると数千行になり保守不能。部屋単位で分離し、工程も部屋グループ単位で切れる |
| 共通基盤 | `booth/pack_base.py`（HTMLシェル・共通CSS・zip生成） | ページ骨格(meta, 1920x1080固定, scanlines等の共通部品)は1箇所で管理 |
| **本体アセット抽出** | `booth/asset_extract.py` — KYOUKAI本体の一次データ（`static/*.js` の演出定数、`static/*.css` の配色、`static/images/<部屋>/` の画像、`shorts_factory/kyoukai_hotspots.json`、`static/kyoukai-building-data.js`）を room_specs から参照・同梱する仕組み | 世界観MDからの二次創作ではなく、本物の部屋の色・動き・絵をそのまま商品に持ち込む。「その部屋らしさ」の根拠を一次データに置く |
| 演出 | HTML+CSS+Canvas 2D（現行踏襲）+ 部屋によっては本体画像の同梱 | OBSブラウザソースで完全ローカル動作・外部依存ゼロという商品価値を維持。画像は自作アセットのため権利問題なし |
| 検証・撮影 | 前ラウンドの verify_packs / screenshot_packs / make_thumbnails / final_check を流用 | パス構造を変えなければ再実行だけで新デザインに追従できる |

### 部屋らしさの実装方式（2方式の併用）

- **A: パラメータ抽出方式** — 本体JS/CSSから色遷移・演出定数を抽出して商品HTML内に再現する。zipは軽いまま。抽象演出の部屋向け（ripple, particles, null, exit, observation, archive, hyougi, observer, typhoon-news）。工程1の実地調査で `ma`・`gokuraku` は部屋専用の本体背景画像が存在しないことが確定したため、この2部屋も方式Aに変更する。
  - 例: `static/ripple.js` のドット色遷移（暗赤→赤→黄→青→白）、`static/kyoukai-404.js` の崩壊演出、`static/particle-engine.js` の粒子パラメータ、`static/ma.js` の呼吸モーション定数。
- **B: 画像同梱方式** — 本体の部屋画像を商品zipに `assets/` として同梱し、その上にCanvas/CSS演出を重ねる。部屋の「絵」が本物になる。具象的な部屋向け（namahage, kanrinin, fukashitsu, daimyojin, matsuri）。
  - 例: `static/images/kanrinin/kanrinin-room-9x16.png`、`static/images/namahage/namahage-room-9x16.png`、`static/images/fukashitsu/fukashitsu-room-9x16.png`、matsuriの棒・穴・紙吹雪素材。
  - 9:16画像は1920x1080に対し中央配置+左右を暗色グラデーションで埋める（`pack_base.py` にヘルパーを用意）。
  - 画像はビルド時に `asset_extract.py` が本体からコピー+必要なら縮小（長辺1500px程度・JPEG/PNG最適化）してzipサイズを1パック5MB以内に抑える。

### 却下した選択肢

- **CANVAS_JS辞書の拡張（現行構造のまま演出だけ追加）**: waitingの背景Canvasしか差し替えられず、「レイアウト自体を部屋別にする」という本ラウンドの目的を満たせない。却下。
- **完全手書き48ファイル（ジェネレーター廃止）**: 一括修正・再生成・検証が不可能になり、前ラウンドで確立した品質保証が失われる。却下。
- **WebGL/Three.js**: 低スペックPC制約とOBSブラウザソースの負荷を考慮し、Canvas 2Dで表現できる範囲に留める。却下（拡張フェーズ候補）。
- **外部フォント(Webフォント)導入**: ローカル完全動作が崩れる。却下。

### room_spec の構造（全工程共通の契約）

各 `booth/room_specs/<部屋ID>.py` は以下を必ずエクスポートする:

```python
SPEC = {
    "id": "ma",
    "name": "悪魔の間",
    "color": "#cc1122",
    "rgb": "204,17,34",
    "bg": "#040000",
    # 素材別: それぞれ完全なHTML文字列を返す関数
    "waiting_html": ...,   # def(spec) -> str
    "brb_html": ...,       # def(spec) -> str
    "lower_third_html": ..., # def(spec) -> str
    # README用の部屋説明文
    "readme_lines": {...},
}
```

- `generate_packs.py` は ROOMS 定義を room_specs の動的importに置き換え、生成・zip化・バンドルのフローは変更しない。
- 共通部品（scanlinesオーバーレイ、1920x1080ボディ、透過ボディ、REC点滅等）は `pack_base.py` のヘルパー関数として提供し、各room_specが**使うかどうかを選ぶ**（強制しない。共通骨格の強制が今回の没個性の原因）。

### 部屋別デザイン指針（各工程はこの表に従って実装する）

| 部屋 | 方式 | 参照する一次データ | waiting の骨格 | brb の演出 | lower_third の形 |
|---|---|---|---|---|---|
| 観測域 | A | `static/space.css` の配色、観測ログの文体(`data/kyoukai_world.md`) | 観測ログ端末: 画面全体が流れるログテーブル+観測カウンタ | ログが停止し「記録は継続」の静止カーソルが明滅、時折1行だけ追記される | 端末プロンプト風 `> 名前 _`（カーソル明滅） |
| 評議録 | A | `templates/hyougi.html` の配色・文体 | 縦書き風の議事断片が浮かぶ和紙質感、中央に議題番号 | 何も書かれない議事用紙に時折「──」だけが打たれる | 毛筆風の縦線+発言者札のような名札 |
| 崩落域 | A | `static/kyoukai-404.js` の文字崩壊演出、`templates/null.html` の崩壊度UI | 画面自体が傾き・崩れる。UI部品がずり落ちる演出 | 画面が周期的に崩壊→再構築を繰り返す(行ズレグリッチ強化) | 名前の文字が時々欠落・復元するテロップ |
| 逆観測室 | A | `templates/observer.html` の語りかけ文・配色 | 中央に瞳孔のような円環。UI最小限、視線を感じる構図 | 巨大な目がゆっくり開閉し「観測は続いています」 | 名前が視線カーソルに追われる/下線が瞳孔型 |
| 境界域 | A | `templates/exit.html` のロード画面演出 | ロード画面そのもの: プログレスバーが進んでは戻る | 通路の奥行き表現(遠近の枠が流れる)+接続メッセージ | 境界線をまたぐ二重枠のテロップ |
| 記録室 | A | `templates/archive.html` の記録フォーマット(日付・ID・内容) | ファイル棚のグリッド。カードが差し替わる | 「照合中」のファイルカードが1枚ずつめくれる | インデックスカード/ラベルシール風 |
| 悪魔の間 | A(工程1実地調査で確定。部屋専用の本体背景画像が存在しないため方式Bから変更) | `static/ma.js`の呼吸モーション定数 | 呼吸する赤い光(本体と同周期)をコードで再現。計器なし | 光が呼吸し、沈黙のセリフが間欠表示 | 紋様付きの黒枠、名前が赤い刻印風 |
| AI大明神 | B(工程1実地調査で確定: `static/images/daimyojin/daimyojin_pc.webp`・`daimyojin_mobile.webp`が実在) | `static/images/daimyojin/daimyojin_pc.webp`、`templates/daimyojin.html`の祈願UI | 祈願装置の本体画像+祈願札の発光 | おみくじ筒が回り「祈願 処理中」の札が揺れる | 神社の木札(絵馬)型テロップ |
| 極楽域 | A(工程1実地調査で確定。部屋専用の本体背景画像が存在しないため方式Bから変更) | `static/images/entrances/entrance-gokuraku.png`(参考のみ、同梱はしない) | 引き出し棚をCSS/Canvasで描画+スペクトルバーを棚に埋め込む | 引き出しが1つずつ開閉し音源番号が変わる | 引き出しラベル+音量バー内蔵 |
| 粒子観測 | A | `static/particle-engine.js` の粒子パラメータ・色 | 本体と同じ粒子群+観測レティクル(十字照準)が粒子を追う | 粒子が一点に収束していく過程をループ | 名前の周囲を粒子が公転する |
| 波紋域 | A | `static/ripple.js` のドット色遷移(暗赤→赤→黄→青→白)・波紋周期・黒戻し波紋 | 本体と同じドットグリッド+自動波紋 | 波紋が中心から周期的に広がり画面を初期化する(本体の1分周期黒戻しを踏襲) | 名前の下から波紋が広がるテロップ |
| 管理人室 | B | `static/images/kanrinin/kanrinin-room-9x16.png`、`static/kanrinin.css` | 受付カウンターの本体画像+呼び鈴・鍵ボックスの発光ポイント | 「席を外しています」札が揺れる+目玉がうっすら透ける演出(本体ギミック踏襲) | 宿帳/ネームプレート風(真鍮質感) |
| なまはげ | B | `static/images/namahage/namahage-room-9x16.png`、`static/namahage.js` のCONFIG(目の座標・明滅) | なまはげ本体画像+ドット目Canvas(16x12, pixelated)を本体と同座標比率で重ねる | 目が明滅し、時折「──いるか」が浮かぶ | 名前の横にドット目が付き、時々瞬きする |
| 棒入れ祭 | B | `static/images/matsuri/`の棒・穴・紙吹雪・御幣素材、`static/matsuri.js`の演出定数 | 本体素材(棒・穴・紙吹雪)を配置した祭り画面+奉納カウンタ | firework sparkが上がり続け「奉納の準備」 | 祭り半纏風の縁取り+紙吹雪が散る |
| 卵部屋 | B | `static/images/fukashitsu/fukashitsu-room-9x16.png`、`static/fukashitsu.js`のパステル色遷移 | 孵化装置の本体画像+卵部分に粒子の明滅(本体と同じ色設計) | 卵の鼓動がゆっくり続く | 卵形の丸枠テロップ、淡いパステル |
| 台風ニュース | B | `typhoon-news/assets/typhoon-news-bg.png`、`typhoon-news/script.js`のtyphoonPresets・速報帯構成 | 本体のニュース背景画像+速報帯+台風情報パネル(本体のUI構成を移植) | 「放送は一時中断しています」お詫びテロップ+砂嵐(唯一スタティック維持) | 報道テロップ形式(局ロゴ位置+2段帯) |

方式Bの部屋は、`asset_extract.py` が本体画像をパックの `assets/` にコピーし、HTMLは相対パス `assets/<ファイル名>` で参照する（OBSのローカルファイル指定でそのまま動く）。hotspot座標が必要な部屋（管理人室の呼び鈴・鍵ボックス等）は `shorts_factory/kyoukai_hotspots.json` と各部屋CSSの領域定義を参照する。

---

## 3. 工程分割（全6工程）

### 工程1: 基盤リファクタ（pack_base + room_specs + asset_extract）

状態: 完了

**目的**: 部屋別テンプレートと本体アセット抽出を差し込める構造を作り、既存生成フローを壊さずに移行する。

**実装内容**:
- `booth/pack_base.py` を新規作成:
  - `html_shell(title, body, css, js, transparent=False)` — 1920x1080固定・meta・共通リセットCSSを持つHTML骨格
  - 選択式ヘルパー: `scanlines_css()`, `rec_indicator_html()`, `corner_frame_css(color)`, `blink_keyframes()`, `bg_image_css(rel_path)`（9:16画像を1920x1080中央配置+左右暗色グラデーション） 等（各room_specが任意に使用）
  - `write_pack(spec, out_root)` — waiting/brb/lower_third/README+assets/ を書き出す
  - `make_zip(pack_dir, zip_path)` — 現行のzip生成を移設（assets/サブフォルダ対応）
- `booth/asset_extract.py` を新規作成:
  - `PROJECT_ROOT = Path(__file__).resolve().parent.parent` でKYOUKAI本体を参照
  - `copy_image(src_rel, spec_id, max_edge=1500)` — 本体画像をパックの `assets/` へコピー。長辺max_edge超は縮小、PNG/JPEG最適化。戻り値は相対パス
  - `read_source(src_rel)` — 本体JS/CSS/JSONをテキストで読む（room_specが定数抽出に使う）
  - 本体ファイルが存在しない場合は明確なエラーで落とす（黙ってスキップしない）
- `booth/room_specs/__init__.py` を作成し、`load_all_specs()` で16部屋のSPECを部屋ID順にimportして返す。
- 移行措置: 現時点では16部屋分の room_specs を「現行 generate_packs.py のテンプレート関数をそのまま呼ぶ薄いラッパー」として自動生成し、`generate_packs.py` の main を room_specs 経由に切り替える。**この工程では見た目は1pxも変えない。**
- `python generate_packs.py` 実行→前ラウンドの `verify_packs.py` と `final_check.py` が全passすることを確認（構造変更のリグレッションチェック）。
- 現行テンプレート関数(waiting_html/brb_html/lower_third_html/CANVAS_JS)は `booth/legacy_templates.py` に移設し、generate_packs.py本体は生成フロー(生成・zip・バンドル)のみにする。
- 方式B対象部屋の本体アセットの所在を実地確認し、`asset_extract.py` 内の `ASSET_MAP`（部屋ID→本体パスのリスト）として確定させる（ma/daimyojin/gokurakuの画像パスはROADMAP作成時点で未確認のため、この工程で `static/images/` を捜索して確定する。見つからない部屋は方式Aに変更してROADMAPの表を更新する）。

**完了条件**:
- [x] `booth/pack_base.py`・`booth/asset_extract.py`・`booth/room_specs/`(16ファイル+__init__.py) が存在する
- [x] `asset_extract.py` の ASSET_MAP に方式B全部屋の実在パスが登録され、`python -c` の単体テストで copy_image が動作する
- [x] `python generate_packs.py` で従来と同一構成の48ファイル+zip17本が生成される
- [x] `verify_packs.py` 48件全pass、`final_check.py` ALL PASS（※本工程時点ではlistings/thumbnailsは未生成のため、旧成果物削除に伴いzip検証・verify_report検証の範囲でPASSを確認。listings/thumbnailsは工程6で再生成しfinal_check.py全体PASSとする）
- [x] git diff で生成フロー変更の差分が追跡できる状態でコミット可能

**落とし穴**:
- room_specsの動的importはファイル名にハイフンが使えない（typhoon-news → `typhoon_news.py` とし、SPEC内のidは `typhoon-news` を維持する）。
- 出力パス・zip名・フォルダ名を1文字でも変えると screenshot_packs / final_check が壊れる。出力構造は完全維持（assets/の追加は許容。final_checkはファイル追加でFAILしない設計になっている）。
- 本体画像は `vercel.json` の excludeFiles 対象など配置が特殊な場合がある。gitに入っていない画像がないか `git ls-files` でも確認する。

**推奨実装モデル**: sonnet

---

### 工程2: 部屋実装グループA（観測域・記録室・評議録・境界域）

状態: 完了

**目的**: 記録・文書系4部屋のwaiting/brb/lower_thirdをデザイン指針表に従いフルリニューアルする。

**実装内容**:
- `room_specs/observation.py` / `archive.py` / `hyougi.py` / `exit.py` の3関数を legacy委譲から専用実装に置き換える。
- 各部屋、デザイン指針表の骨格に従う。実装の最低要件:
  - waiting: 部屋固有のレイアウト構造（グリッド/中央配置/L字等が部屋間で異なる）+固有Canvas演出
  - brb: 固有Canvas演出+固有の画面構成（共通の「中央メッセージ+SIGNALメーター」構成を使い回さない）
  - lower_third: 固有の形状・装飾・アニメーション（透過背景・?name=&title= パラメータ対応は共通契約として維持）
- 部屋固有CSSクラスには部屋IDプレフィックスを付ける（例: `.obs-log-table`, `.arc-card`）→工程6の自動チェック対象。
- 実装後 `python generate_packs.py` → 対象4部屋のHTMLをChromiumで開き目視相当の確認（Playwrightでスクショを撮り、旧デザインと異なることをピクセル差分で確認するスクリプト `booth/diff_check.py` をこの工程で作成し、以降の工程でも使う）。

**完了条件**:
- [x] 4部屋×3ファイルが専用実装になっている（legacy_templates への委譲が残っていない）
- [x] verify_packs.py で対象12ファイルがpass（JSエラーなし）
- [x] diff_check.py で対象12ファイル全てが旧版とピクセル差分あり
- [x] 4部屋のwaiting同士・brb同士を比較して同一レイアウト骨格の使い回しがない（reviewerがHTML構造を比較）

**落とし穴**:
- 評議録の縦書きは `writing-mode: vertical-rl` を使う。Chromium(OBS)では動くがフォント次第で崩れるため等幅フォールバックを指定。
- lower_thirdの`#name-el`/`#title-el`のID契約は全部屋で維持（verify_packs.pyが依存）。

**推奨実装モデル**: sonnet

---

### 工程3: 部屋実装グループB（崩落域・逆観測室・悪魔の間・なまはげ）

状態: 完了

**目的**: ダーク・存在系4部屋のフルリニューアル。

**実装内容**:
- `room_specs/null.py` / `observer.py` / `ma.py` / `namahage.py` を専用実装に置き換える。
- デザイン指針表に従う。特記:
  - 崩落域: UI部品自体が `transform` で傾き・落下する。`prefers-reduced-motion` は考慮不要（OBS用途）だが、CPU負荷を抑えるためsetIntervalは1秒以上の周期にする
  - 逆観測室: 目の開閉はCanvasでもCSSクリップでも可。白基調・低輝度のため screenshot_packs.py の輝度閾値(observer=0.3)を維持できる明るさを確保する
  - 悪魔の間: KYOUKAI本体 `/ma` の「呼吸する背景+沈黙の間」を演出言語として踏襲（アセット流用はしない。コードで表現）
  - なまはげ: KYOUKAI本体 `/namahage` の低解像度ドット目(16x12 Canvas, image-rendering:pixelated)を意匠として踏襲
- 工程2で作成した diff_check.py で旧版との差分を確認。

**完了条件**:
- [x] 4部屋×3ファイルが専用実装（legacy委譲なし）
- [x] verify_packs.py 対象12ファイルpass
- [x] diff_check.py 対象12ファイル差分あり
- [x] screenshot_packs.py を対象4部屋に対して再実行し輝度チェックpass

**落とし穴**:
- 悪魔の間・なまはげは黒背景率が高く輝度チェックに落ちやすい。演出の光量で閾値(1.0/observerのみ0.3)を超えるよう調整するか、閾値定数の部屋別上書きを追加する（screenshot_packs.pyのBRIGHTNESS_THRESHOLD_OVERRIDESに追記でよい）。

**推奨実装モデル**: sonnet

---

### 工程4: 部屋実装グループC（AI大明神・極楽域・棒入れ祭・管理人室）

状態: 未着手

**目的**: 和風・レトロ系4部屋のフルリニューアル。

**実装内容**:
- `room_specs/daimyojin.py` / `gokuraku.py` / `matsuri.py` / `kanrinin.py` を専用実装に置き換える。
- デザイン指針表に従う。特記:
  - AI大明神: 絵馬型lower_thirdは木札の輪郭をCSS(border-radius+疑似要素の紐)で描く
  - 極楽域: 引き出し棚はCSS gridで描画し、開閉はtransformで表現
  - 棒入れ祭: 紙吹雪Canvasは現行festivalスタイルを強化流用してよい（waitingの背景としてではなく画面構成ごと祭り化する）
  - 管理人室: 真鍮ネームプレートはグラデーション+内側シャドウで表現
- diff_check.py で旧版との差分確認。

**完了条件**:
- [ ] 4部屋×3ファイルが専用実装（legacy委譲なし）
- [ ] verify_packs.py 対象12ファイルpass
- [ ] diff_check.py 対象12ファイル差分あり
- [ ] 4部屋間でレイアウト骨格の使い回しがない

**落とし穴**:
- 和風表現で画像を使いたくなるが、外部画像・base64埋め込み大画像は禁止（ファイルサイズと完全ローカン動作の維持）。CSS/Canvasのみで描く。

**推奨実装モデル**: sonnet

---

### 工程5: 部屋実装グループD（粒子観測・波紋域・卵部屋・台風ニュース）

状態: 未着手

**目的**: 動的・特殊系4部屋のフルリニューアル。

**実装内容**:
- `room_specs/particles.py` / `ripple.py` / `fukashitsu.py` / `typhoon_news.py` を専用実装に置き換える。
- デザイン指針表に従う。特記:
  - 粒子観測: 現行particlesスタイルの粒子+接続線を維持しつつ、観測レティクル(最も近い粒子を追う十字+座標表示)を追加してwaitingの主役にする
  - 波紋域: KYOUKAI本体 `/ripple` のドットグリッド+波紋色遷移(暗赤→赤→黄→青→白)を意匠踏襲
  - 卵部屋: 卵形はCanvasの楕円グラデーションで描画。パステル3色(栄養/酸素/温度)の計器を添える
  - 台風ニュース: KYOUKAI本体 `/typhoon-news/` の速報帯・情報パネル・テロップ構成を踏襲。brbのみ全部屋で唯一「放送中断の砂嵐」としてスタティックを維持する（ニュース放送の文脈で意味を持つため）
- diff_check.py で旧版との差分確認。

**完了条件**:
- [ ] 4部屋×3ファイルが専用実装（legacy委譲なし。台風ニュースbrbの砂嵐は専用実装として書き直した上での採用）
- [ ] verify_packs.py 対象12ファイルpass
- [ ] diff_check.py 対象12ファイル差分あり
- [ ] legacy_templates.py への参照が room_specs 全16ファイルから消えている（grepで確認）

**落とし穴**:
- 台風ニュースのL字レイアウトは配信画面を隠しすぎない設計にする（waiting/brbは全画面でよいが、情報帯の内側は暗くして「ここにゲーム画面が入る」ことを想起させない。あくまで待機画面）。

**推奨実装モデル**: sonnet

---

### 工程6: 全再生成・検証拡張・商品資材更新

状態: 未着手

**目的**: 新デザインで全成果物を更新し、差別化基準を自動検証に組み込み、出品可能状態に戻す。

**実装内容**:
- `verify_packs.py` に差別化チェックを追加:
  - 各部屋の3ファイルに部屋IDプレフィックス付きCSSクラスが3つ以上存在する
  - 全部屋のbrb.htmlのbody構造(タグ構成のハッシュ)が互いに異なる
- `final_check.py` に単品zipサイズ上限チェック(1本5MB以内)を追加(画像同梱部屋の肥大検知)。
- `python generate_packs.py` で48ファイル+zip17本を再生成。
- `screenshot_packs.py` → `make_thumbnails.py` を再実行し、サムネイル64枚を新デザインで更新。
- `final_check.py` ALL PASS を確認。
- `make_listings.py` の商品文に各部屋の演出説明(1〜2行、新デザインの内容)を反映して再生成（構成・トーン・禁止ワード制約は前ラウンドのまま）。
- 全体をコミット。

**完了条件**:
- [ ] verify_packs.py 拡張版で48ファイル全pass(JSエラー0+差別化チェックpass)
- [ ] zip17本・サムネイル64枚(全て1920x1080)・listings19ファイルが新デザイン基準で更新済み
- [ ] final_check.py ALL PASS
- [ ] コミット完了

**落とし穴**:
- サムネイル(00_main)は新waiting.pngベースで自動再生成されるが、暗い部屋では文字が沈む可能性→make_thumbnails.pyの半透明帯がその対策として機能しているか目視相当の確認(数枚)をする。
- 旧zipを買った既購入者はいない前提（未出品）だが、signal-pack(受信域)はこのラウンドの対象外なので触らない。

**推奨実装モデル**: sonnet

---

## 4. 未決事項・要判断ポイント（高度モデルに戻す箇所）

| # | 項目 | 内容 | 暫定案 |
|---|---|---|---|
| 1 | 受信域(signal-pack)の扱い | 先行制作分は今回の個性化基準を満たしている(波形演出が固有)が、room_specs体系の外にある | 今回は対象外。次ラウンドでroom_specsに統合 |
| 2 | 音の有無 | 演出に環境音を付けるか。OBSブラウザソースは音声出力可能だが、配信者は自分のBGMを流すことが多い | 無音を維持（音は拡張フェーズ） |
| 3 | 各部屋のデザイン最終判断 | デザイン指針表はあくまで指針。実装時に「面白くならない」と判断した場合の変更 | 実装モデルが指針から外れる場合は高度モデル(メイン)に戻して判断 |
| 4 | 価格改定 | 個性化後は300円→400〜500円の余地 | 300円を維持し、売れ行きで判断（未出品のため実績なし） |

---

## 5. リスク一覧

| リスク | 影響 | 対策 |
|---|---|---|
| 本体画像同梱でzipサイズ肥大 | ダウンロード品質・BOOTHアップ上限 | copy_imageで長辺1500px縮小+最適化。1パック5MB以内を final_check.py の検証項目に追加（工程6） |
| 本体アセットのパス未確認（ma/daimyojin/gokuraku） | 工程2〜5で手戻り | 工程1でASSET_MAPを実地確定済み。daimyojinは画像実在で方式B維持、ma/gokurakuは画像なしで方式Aへ切替済み |
| 16部屋×3素材の演出実装で工数爆発 | ラウンドが完了しない | 1工程4部屋に分割済み。1部屋あたりwaiting/brb/lower_third合計300行程度を目安とし、超える場合は演出を削る |
| CPU負荷の高い演出（全画素更新系） | 低スペックPC制約違反・OBSでコマ落ち | ImageData全画素更新は台風ニュースbrbの砂嵐のみに限定。他はshape描画+requestAnimationFrameに留める |
| 暗い部屋が輝度チェック・サムネ視認性に落ちる | 工程3・6で手戻り | 閾値の部屋別上書き機構が既にある。演出光量の下限を意識して実装 |
| 差別化の主観性（「見分けられる」の判定） | reviewerと実装の解釈ずれ | 完了条件を機械判定(固有クラス3つ以上・body構造ハッシュ相違・ピクセル差分)に落とし込み済み |
| リファクタで既存パイプライン破損 | 前ラウンド成果物の喪失 | 工程1は見た目を変えないリグレッション専用工程として分離。各工程でverify/final_check再実行 |

---

## 6. 拡張フェーズ（次ラウンド候補・工程化しない）

- 受信域(signal-pack)のroom_specs統合と個性化基準への引き上げ
- 環境音(アンビエント)のオプション同梱（音ありHTML/音なしHTMLの2版構成）
- WebM書き出し版（Canvas演出を録画してループ動画化。HTML非対応の配信ソフト向け）
- URLパラメータによるカスタマイズ拡張（色変更・演出強度・メッセージ差し替え）
- 時間経過で演出が変化する「観測進行」モード（配信開始からの経過時間で部屋が変質する）
- 英語版README・英語ファイル名版zip（海外BOOTH/itch.io展開）
- 全部屋の演出を1画面で切り替えられる「全部屋デモHTML」（商品ページ用GIF素材の元）
