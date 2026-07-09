# HANDOFF_KYOUKAI.md — 2026-07-09（最新）

このファイルを新規チャット・Claude Code・Codex の冒頭に貼るだけで再開できます。

---

## 直近でやったこと（2026-07-09）

- OBSパック「部屋別個性化リニューアル」（`ROADMAP.md` 新版、前ラウンドの`ROADMAP_BOOTH販売展開_完了.md`の続き）の工程1「基盤リファクタ（pack_base + room_specs + asset_extract）」を実装
  - `booth/pack_base.py` を新規作成: `html_shell()`、選択式ヘルパー（`scanlines_css`/`rec_indicator_html`/`corner_frame_css`/`blink_keyframes`/`bg_image_css`）、`write_pack()`、`make_zip()`
  - `booth/asset_extract.py` を新規作成: `PROJECT_ROOT`（booth/の親）、`copy_image()`（長辺1500px縮小+PNG/JPEG/WEBP最適化）、`read_source()`（存在しない場合は例外で落とす設計）
  - `ASSET_MAP` を実地調査で確定: kanrinin/namahage/matsuri/fukashitsu/typhoon-newsは方式B画像が実在。**daimyojinも`static/images/daimyojin/daimyojin_pc.webp`等が実在し方式B確定**。**ma・gokurakuは部屋専用の本体背景画像が存在しないため方式Aへ変更**（ROADMAP.mdの部屋別デザイン指針表・実装方式説明を更新済み）
  - `booth/room_specs/`（16ファイル+`__init__.py`）を新規作成。工程1時点では全て`legacy_templates.py`の関数を呼ぶ薄いラッパー（見た目は1pxも変えていない）。`typhoon-news`は`typhoon_news.py`というファイル名でid='typhoon-news'を維持
  - `booth/legacy_templates.py` を新規作成。現行`generate_packs.py`のROOMS/CANVAS_JS/waiting_html/brb_html/lower_third_html/readme_txtをそのまま移設
  - `booth/generate_packs.py` を生成フロー（生成・zip・バンドル）のみに簡素化。`room_specs.load_all_specs()`経由で生成。他スクリプト（final_check/screenshot_packs/make_thumbnails/make_listings）が`from generate_packs import ROOMS`で参照する互換性は`legacy_templates.ROOMS`の再エクスポートで維持
  - 検証: 旧成果物削除済みのため`python generate_packs.py`で48ファイル+zip17本を新規生成 → 全64ファイル（html+README.txt）が削除前コミット（`4de9a6f`）と**バイト完全一致**であることをスクリプトで確認。`verify_packs.py`は48/48 pass。`final_check.py`はzip検証(17/17)・verify_report検証(48/48)がPASS（thumbnails/listingsは工程6で再生成予定のため、この工程ではFAILのままでよい契約どおり）
  - ROADMAP.mdの工程1を「完了」に更新済み、完了条件チェックボックス全て[x]
- OBSパック「部屋別個性化リニューアル」の工程2「部屋実装グループA（観測域・記録室・評議録・境界域）」を実装
  - `room_specs/observation.py`: 観測域を専用実装化。waitingは端末画面全体が流れるログテーブル(`.obs-log-table`)+観測カウンタ、brbはログ停止+静止カーソル明滅+時折1行追記、lower_thirdは端末プロンプト風`> 名前 _`。一次データは`static/space.css`のmonoフォント(`--sp-mono`)、`data/kyoukai_world.md`の観測ログ文体(感情を排した観測記録)を`asset_extract.read_source`で実読込して反映
  - `room_specs/archive.py`: 記録室を専用実装化。waitingはファイル棚グリッド(`.arc-shelf-grid`、カードが差し替わる)、brbは「照合中」ファイルカードが1枚ずつ`rotateY`でめくれる、lower_thirdはインデックスカード風。一次データは`templates/archive.html`のカードフォーマット(`archive-card-meta`: 日付/ID/内容)を実読込・アサーションで確認
  - `room_specs/hyougi.py`: 評議録を専用実装化。waitingは`writing-mode:vertical-rl`の縦書き議事断片+和紙質感+中央議題番号、brbは白紙の議事用紙に時折「──」、lower_thirdは毛筆風縦線+発言者札。落とし穴対応として等幅フォールバック(`'MS Mincho','Yu Mincho','Courier New',monospace`)を明示指定。一次データは`templates/hyougi.html`実読込で配色トーンを確認
  - `room_specs/exit.py`: 境界域を専用実装化。waitingはロード画面そのもの(プログレスバーが8%〜94%を往復)、brbは同心円リングが流れる通路奥行き表現+接続メッセージ、lower_thirdは境界線をまたぐ二重枠。一次データは`templates/exit.html`のロード演出文言(`exit-loader`)を実読込で確認
  - 各部屋、waiting/brb/lower_thirdでレイアウト骨格自体を変更（共通の「中央メッセージ+SIGNALメーター」使い回しなし）。部屋固有CSSクラスは部屋IDプレフィックス(`.obs-` `.arc-` `.hyo-` `.exit-`)で15〜24個ずつ付与（要件の3個以上を大幅に満たす）
  - `booth/diff_check.py` を新規作成。`git archive --format=zip`で指定コミット時点のbooth/一式を一時展開し、旧room_specsから再生成したHTMLと現行HTMLをPlaywrightでスクショ→Pillowでピクセル差分判定。Windows上で日本語ファイル名を含むtar展開が失敗する問題があったためzip形式に変更して解決
  - 検証: `python generate_packs.py`で48ファイル+zip17本再生成 → `verify_packs.py` 48/48 pass → `diff_check.py observation archive hyougi exit --commit b7ca038` で対象12ファイル全てDIFF(旧デザインとの差分あり)を確認
  - ROADMAP.mdの工程2を「完了」に更新済み、完了条件チェックボックス全て[x]
- OBSパック「部屋別個性化リニューアル」の工程3「部屋実装グループB（崩落域・逆観測室・悪魔の間・なまはげ）」を実装
  - `room_specs/null.py`: 崩落域を専用実装化。waitingは画面全体が`transform`でゆっくり傾き・各パネルが個別にずり落ちる演出(`.null-tilt-root`)+404文字の断続的な文字化け、brbは周期的な崩壊→再構築サイクル(パネル縮小+行ズレグリッチ強化)、lower_thirdは名前の文字が時々欠落・復元。一次データは`static/kyoukai-404.js`のNOISE文字集合・corrupt()のratio刻みを`asset_extract.read_source`で実読込
  - `room_specs/observer.py`: 逆観測室を専用実装化。waitingは中央に瞳孔のような多重円環(`.obsr-iris-wrap`)+UI最小限+時折フェードする囁き文、brbは巨大な目がゆっくり開閉(`clip-path`+`scaleY`)し「観測は続いています」、lower_thirdは名前の下に瞳孔型下線が左右に揺れる。一次データは`templates/observer.html`の語りかけ文体・白基調配色を実読込
  - `room_specs/ma.py`: 悪魔の間を専用実装化(方式A・画像なし)。waitingは呼吸する赤い光の同心グロー+紋様の回転リング(計器なし)、brbは光が強く呼吸し「大魔将」の沈黙がちな台詞が間欠フェード表示、lower_thirdは紋様付き黒枠+刻印風の赤い名前。一次データは`static/ma.js`のCONVS会話データ(「……帰れ。」等の間を強く意識した台詞)を実読込
  - `room_specs/namahage.py`: なまはげを専用実装化(方式B・画像同梱)。waitingは本体画像`static/images/namahage/namahage-room-9x16.png`を`pack_base.bg_image_css`で中央配置+左右暗色グラデーション+16x12ドット目Canvas(`image-rendering:pixelated`)を本体と同座標比率で重ね、視線移動・まばたきを本体`namahage.js`のGAZE_POSITIONS相当で再現。brbは目が明滅し「──いるか」等が間欠表示、lower_thirdは名前の横にドット目が付き時々瞬き。画像は`asset_extract.copy_image`でパックの`assets/`へ同梱
  - 各部屋、部屋IDプレフィックス付きCSSクラス(`.null-` `.obsr-` `.ma-` `.nmh-`)を10個以上ずつ付与
  - 検証: `python generate_packs.py`で48ファイル+zip17本再生成 → `verify_packs.py` 48/48 pass（逆観測室lower_thirdで`#name-el`のtextContentが子要素混入によりズレるバグを1回発見・修正して再検証pass）→ `diff_check.py null observer ma namahage --commit b7ca038` で対象12ファイル全てDIFF確認 → `screenshot_packs.py`を全16部屋(48ファイル)に対して再実行し輝度チェック全pass（悪魔の間・なまはげも含め閾値の部屋別上書きなしで通過。brightness値は各waiting 2.99〜8.04、brb 3.27〜4.57）
  - ROADMAP.mdの工程3を「完了」に更新済み、完了条件チェックボックス全て[x]
- OBSパック「部屋別個性化リニューアル」の工程4「部屋実装グループC（AI大明神・極楽域・棒入れ祭・管理人室）」を実装
  - `room_specs/gokuraku.py`: 極楽域を専用実装化(方式A・部屋専用画像なしのためCSS/Canvasのみ)。waitingは引き出し棚をCSS grid(4行5列)で描画し各引き出しにCanvasスペクトルバーを埋め込み、brbは引き出しが1つずつ`transform:translateY`で開閉+音源番号がランダム切替、lower_thirdは引き出しラベル+CSSアニメーションの音量バー内蔵テロップ
  - `room_specs/matsuri.py`: 棒入れ祭を専用実装化(方式B・画像同梱)。waitingは`static/images/matsuri/`の棒・穴・御幣素材を配置した祭り画面全体(画面構成ごと祭り化。背景演出としてではなく主役に)+奉納カウンタ+紙吹雪Canvas、brbはfirework spark(Canvas)が上がり続け「奉納の準備」、lower_thirdは祭り半纏風の縁取り+紙吹雪が散るテロップ。`static/matsuri.js`の紙吹雪カラーパレット・掛け声メッセージを踏襲
  - `room_specs/daimyojin.py`(初版): AI大明神を専用実装化(方式B・画像同梱)。本体画像を中央配置+絵馬型祈願札発光+祈願ログ
  - `room_specs/kanrinin.py`(初版): 管理人室を専用実装化(方式B・画像同梱)。本体画像+呼び鈴・鍵ボックス発光ポイント+席外し札揺れ
  - reviewerが「daimyojinとkanriniのwaiting/brbがDOM構造・座標・演出ロジックともに同一テンプレートの色違いになっている」と要修正判定。ユーザー承認を得て再修正:
    - `room_specs/daimyojin.py`(再設計): waitingを「祈願処理装置のコンソール」構図に変更。左62%に回路グリッド+巨大祈願番号(明滅カウントアップ)+縦スクロールする祈願ログウィンドウ、右38%に本体画像を帯状配置(中央配置から変更)。brbはおみくじ筒回転+札揺れをやめ、二重の円環プログレスリング(`.dmj-ring`/`.dmj-ring--inner`)が回転する「PROCESSING」構図に変更(揺れアニメは管理人室側にのみ残す)
    - `room_specs/kanrinin.py`(再設計): waitingを「受付フロントカウンター」構図に変更。上部38%(412px)に本体画像を帯状配置、下部62%を宿帳ページ(1行がめくれるように差し替わる`.kan-diary-page`)+鍵ボックス格子グリッド(12マスが1マスずつ点灯)+呼び鈴応答なしカウンターの3ペイン構成に変更。brbは揺れる立て札演出を維持しつつ、目玉の透けをCSS要素からCanvasベースのvignette明滅(`.kan-brb-eye`の周期リビール)に変更して差別化
  - 部屋IDプレフィックス付きCSSクラスは再設計後もdaimyojin 20個・kanrinin 25個(要件の3個以上を大幅に満たす)
  - 各部屋waitingに`<canvas>`要素が0件でverify_packs.pyのcanvas存在チェックに落ちた3部屋(daimyojin/matsuri/kanrinin、初版時点)へ演出言語に沿った補助Canvasを追加して契約を満たした経緯あり(gokurakuは引き出しスペクトルバー20枚のCanvasで最初からpass)
  - 検証(再修正後): `python generate_packs.py`で48ファイル+zip17本再生成 → `verify_packs.py` 48/48 pass → `diff_check.py daimyojin gokuraku matsuri kanrinin --commit b7ca038`で12/12 DIFF、再修正後`diff_check.py daimyojin kanrinin --commit b7ca038`でも6/6 DIFF再確認 → `screenshot_packs.py`を全16部屋(48ファイル)に対して再実行し輝度チェック全pass(daimyojin waiting=9.70, kanrinin waiting=43.41含む) → zipサイズ確認(daimyojin 0.15MB, gokuraku 0.006MB, matsuri 3.03MB, kanrinin 1.87MBで全て5MB以内)
  - ROADMAP.mdの工程4を「完了」に更新済み、完了条件チェックボックス全て[x]
- OBSパック「部屋別個性化リニューアル」の工程5「部屋実装グループD（粒子観測・波紋域・卵部屋・台風ニュース）」を実装
  - `room_specs/particles.py`: 粒子観測を専用実装化(方式A)。waitingは本体`static/particle-engine.js`のBASE_PARAMS(attDist/repDist/attF/repF/maxSpd)・色定義(r=rgb(255,55,55)/b=rgb(55,148,255)/y=rgb(255,220,30))を移植した引力・反発粒子群+最も近い粒子を追う十字照準の観測レティクル(`.ptc-reticle-layer`)+座標表示、brbは粒子が中心に収束するループ演出、lower_thirdは名前の周囲を粒子が公転するCanvas。一次データは`asset_extract.read_source`で実読込
  - `room_specs/ripple.py`: 波紋域を専用実装化(方式A)。waitingは本体`static/ripple.js`のパレット(暗赤[34,2,6]→赤[148,14,20]→黄[221,168,42]→青[31,87,184]→白[236,242,232])を移植したドットグリッド+自動波紋、brbは60秒周期の黒戻し波紋(blackoutモード)が中心から広がり画面を初期化するループ、lower_thirdは名前の下から波紋が広がるCanvas
  - `room_specs/fukashitsu.py`: 卵部屋を専用実装化(方式B・画像同梱)。waitingは本体画像`static/images/fukashitsu/fukashitsu-room-9x16.png`+卵形に配置した粒子明滅Canvas(本体`static/fukashitsu.js`のgetColors()パステル遷移を踏襲)+栄養/酸素/温度+孵化予測の計器4種、brbは中央の卵1つが`scale`アニメーションで鼓動し続け淡いパステルの明滅リングCanvasを添える、lower_thirdは卵形の丸枠(border-radius楕円)テロップ
  - `room_specs/typhoon_news.py`: 台風ニュースを専用実装化(方式B・画像同梱)。waitingは本体画像`typhoon-news/assets/typhoon-news-bg.png`+速報帯(`.tpn-breaking`)+台風情報パネル(`typhoon-news/script.js`のtyphoonPresetsから代表1件を移植)+薄い雨筋Canvasを移植、情報帯・速報帯の内側は暗くして待機画面として成立させる。brbは全部屋唯一のスタティック砂嵐(ImageDataフル書き換え、480x270内部解像度+pixelated拡大)を専用実装として書き直し+「放送は一時中断しています」お詫びテロップ、lower_thirdは局ロゴ位置(KYK)+2段帯の報道テロップ形式
  - verify_packs.pyの「waiting/brbにcanvas要素必須」契約に対し、初回実装で卵部屋brb(卵のみのDOM構成)・台風ニュースwaiting(パネルのみのDOM構成)がcanvas 0件で不合格になったため、演出言語に沿った補助Canvas(卵部屋=鼓動同期の明滅リング、台風ニュース=雨筋レイヤー)を追加して契約を満たした
  - 検証: `python generate_packs.py`で48ファイル+zip17本再生成 → `verify_packs.py` 48/48 pass → `diff_check.py particles ripple fukashitsu typhoon-news --commit b7ca038`で12/12 DIFF確認 → `legacy_templates`参照がroom_specs全16ファイルから消えていることをgrepで確認(`__init__.py`のローダーのみ残存、契約通り) → `screenshot_packs.py`を全16部屋(48ファイル)に対して再実行し輝度チェック全pass(particles waiting=3.49, ripple waiting=4.99, fukashitsu waiting=59.83, typhoon-news waiting=38.84含む) → zipサイズ確認(fukashitsu 1.26MB, typhoon-news 1.70MBで全て5MB以内)
  - ROADMAP.mdの工程5を「完了」に更新済み、完了条件チェックボックス全て[x]

## 以前やったこと（2026-07-08）

- BOOTH販売展開プロジェクト（`booth/ROADMAP.md` 相当、実体は `ROADMAP.md`）の工程1「全パックHTML品質検証と修正」を実装
  - `booth/verify_packs.py` を新規作成。Playwright(chromium, headless)で16部屋×3種=48HTMLを検証
  - 検証項目: consoleエラー、pageerror、canvas存在確認（waiting/brb）、`#name-el` の初期テキストが「名前」であること（lower_third）
  - `booth/verify_report.json` に部屋×ファイル別で結果出力
  - 実行結果: 48/48 全件pass。`generate_packs.py` の修正は不要だった
  - ROADMAP.mdの工程1を「完了」に更新済み
- BOOTH販売展開の工程2「スクリーンショット自動撮影」を実装
  - `booth/screenshot_packs.py` を新規作成。Playwright(chromium, headless)、viewport 1920x1080、device_scale_factor=1
  - waiting/brb: `file://` で開き5秒待機後にスクショ。輝度チェック（平均輝度が閾値以下ならリトライ、最大5回）
  - lower_third: `?name=サンプル&title=配信者` を付与し、`page.add_style_tag` で暗いグラデーション背景を注入して撮影
  - `generate_packs.py` に `if __name__ == '__main__':` ガードを追加（import時に生成処理が走らないよう修正）
  - 出力: `booth/thumbnails/<部屋ID>/{01_waiting,02_brb,03_lower_third}.png` 48枚
  - 実行結果: 48/48全件生成、全て1920x1080、waiting/brb系の輝度チェック全件pass（リトライなしで一発通過）
  - ROADMAP.mdの工程2を「完了」に更新済み
- BOOTH販売展開の工程3「サムネイル1枚目（メイン画像）生成」を実装
  - `booth/make_thumbnails.py` を新規作成。Pillowで `01_waiting.png` を下敷きに文字入れ
  - シリーズ名「KYOUKAI OBS PACK」（letter-spacing風）、部屋名（日本語・文字数で150pt/100ptの2段階分岐）+部屋ID、「待機画面 / 離席画面 / 名前テロップ 3点セット」、テーマカラー細枠を描画
  - フォント: `meiryob.ttc` 第一候補、`msgothic.ttc` フォールバック
  - `generate_packs.py` のROOMSをimportで参照（`__main__`ガードは工程2で追加済みのため流用のみ）
  - 出力: `booth/thumbnails/<部屋ID>/00_main.png` 16枚、すべて1920x1080
  - 実行結果: 16/16全件生成成功
  - ROADMAP.mdの工程3を「完了」に更新済み
- BOOTH販売展開の工程4「商品ページ文章16本生成」を実装
  - `booth/make_listings.py` を新規作成。`generate_packs.py` のROOMSをimportし、部屋別の世界観記述（`data/kyoukai_world.md` 各部屋詳細の要約）をスクリプト内辞書で保持
  - 出力: `booth/listings/<部屋ID>.md` 16ファイル。タイトル（40字以内）、商品説明文（世界観一文→同梱3点→OBS設定→動作環境→利用規約→KYOUKAI URL）、タグ10個（共通5+部屋別5）、価格300円を含む
  - 台風ニュースのみニュース速報風の文体にし、他部屋の不穏トーンと差別化
  - 禁止ワード（解説/わかりやすく/入門/方法/やり方/コツ/裏技/チャンネル登録/チャレンジ/ランキング/おすすめ/元気/前向き/感動/おめでとう）をタイトル・世界観パートに含まないことをスクリプト内で検査
  - 実行結果: 16/16全件生成、禁止ワード検査全件pass、タイトル全件40字以内
  - ROADMAP.mdの工程4を「完了」に更新済み
- BOOTH販売展開の工程5「シリーズ共通資材とバンドル作成」を実装
  - `booth/listings/_series.md` を新規作成。シリーズ名「KYOUKAI OBS PACK シリーズ」、全16部屋一覧（各300円）を全商品ページ末尾に貼る共通説明文として用意
  - `booth/generate_packs.py` に `generate_bundle()` と `bundle_readme_txt()` を追加。`booth/all-packs/KYOUKAI_全部屋_OBS素材パック.zip` を16パックフォルダ+総合README.txt同梱で生成。`main()` 内で個別パック生成後に自動実行されるよう組み込み済み
  - `booth/listings/_bundle.md` を新規作成。価格2,980円（単品合計4,800円との差額1,820円を明記）
  - `booth/listings/_出品手順.md` を新規作成。単品16商品+バンドル1商品=17回分のBOOTH出品チェックリスト
  - 実行結果: `python generate_packs.py` 実行成功、バンドルzip検証で16パックフォルダ+README.txt=17項目を確認
  - ROADMAP.mdの工程5を「完了」に更新済み
- BOOTH販売展開の工程6「最終検証と出品準備完了確認」を実装
  - `booth/final_check.py` を新規作成。zip17本(16単品+バンドル)存在、thumbnails16部屋×4枚(00_main+3スクショ)が1920x1080であること、listings必須19ファイル(16部屋分+`_series.md`+`_bundle.md`+`_出品手順.md`)の存在、`verify_report.json`全pass、の4項目を検証
  - listings検証はファイル総数の完全一致ではなく「必須19ファイルが名前で全て存在するか」の判定に変更（コーディネーター判断）。付随ファイルがあってもFAILしない設計
  - cp932コンソール対策としてstdout/stderrをUTF-8 TextIOWrapperでラップ
  - `booth/listings/_OBS実機確認手順.md` を新規作成。OBS Studioのブラウザソースにwaiting/brb/lower_thirdの3素材を設定して目視確認する手順（任意の1部屋分でよい）
  - 実行結果: `python final_check.py` → **ALL PASS**、exit code 0（zip17本・サムネイル64枚全1920x1080・listings必須19ファイル全確認・verify_report.json 48エントリ全pass）
  - ROADMAP.mdの工程6を「実装完了・実機確認待ち」に更新済み。完了条件は「final_check.py全pass」のみ[x]、「OBS実機確認」はユーザー操作待ちのため未チェック

## 直近でやったこと（2026-07-01）

- 孵化室（/fukashitsu）ページを実装・本番デプロイ（**ただし未完成**）
  - 背景画像：ピンク卵トレイ（`static/images/fukashitsu/fukashitsu-room-9x16.png`）
  - キャンバスドットアート：DOT=3、丸と四角ミックス、呼吸アニメーション
  - 3ボタン（栄養/赤・酸素/青・温度/黄）×10回で稚魚収集 → `kyoukai_has_fish=1`
  - 上部10%を3秒以内に7回タップで隠しリセット
- 管理人室の赤電話音を `黒電話のベルが鳴る.mp3` に変更（`static/audio/kanrinin/red-phone-ring.mp3`）
- 管理人室のAmazonホットスポットが電話に被る問題をz-index:15で修正
- 全変更コミット・プッシュ済み（commit: 01d2e81）

## 次にやること（孵化室の未完成部分）

孵化室の何が未完成かは次セッションでまろに確認する。
候補：
- 他の部屋からの導線（ドア画像A）
- 稚魚取得後に管理人室の鍵棚に培養室の鍵が出る処理
- 培養室（/baiyoshitsu）ページの実装
- ビジュアル・演出面の追加

## localStorage キー（生命生成ルート）
- `kyoukai_has_fish` — 稚魚所持フラグ（1=あり）
- `kyoukai_fuka_red` / `kyoukai_fuka_blue` / `kyoukai_fuka_yellow` — 各ボタン押下数

---

## 以前やったこと

- 管理人室（/kanrinin）の室内画像を新しいものに差し替えた（`static/images/kanrinin/kanrinin-room-9x16.png`）
- Amazon棚（亜魔逐管理用品棚）クリック領域を追加 → `outside-items.js` のアソシエイトリンクからランダム遷移
- 楽天モーションウィジェットのクリック領域（`rakutenArea`）を追加済みだが、ウィジェット本体は位置調整のため一時外してある
- vercel.json の excludeFiles に matsuri / namahage を追加 → 本番で棒入れ祭・なまはげが表示されない問題を修正済み
- なまはげ（/namahage）・棒入れ祭（/matsuri）の実装完了・本番稼働中

---

## 現在の状態

- **本番**: 正常稼働中（`https://www.void-kyoukai.net`）
- **ローカル**: `C:/Users/pc/Documents/Claude/Projects/kyoukai` が最新
- **ブランチ**: main、本サイト側は全変更プッシュ済み
- **最新コミット**: `9320147 Add Amazon/Rakuten areas to kanrinin; update room image`
- **OBSパック 部屋別個性化リニューアル（`ROADMAP.md` 現行版）**: 工程1（基盤リファクタ）・工程2（部屋実装グループA: 観測域・記録室・評議録・境界域）・工程3（部屋実装グループB: 崩落域・逆観測室・悪魔の間・なまはげ）・工程4（部屋実装グループC: AI大明神・極楽域・棒入れ祭・管理人室）・工程5（部屋実装グループD: 粒子観測・波紋域・卵部屋・台風ニュース）完了。工程6（全再生成・検証拡張・商品資材更新）は未着手。これで16部屋全てが専用実装になり、`legacy_templates.py`はroom_specs全16ファイルから参照されなくなった(`__init__.py`のローダー内でのみ利用)。`booth/all-packs/`・`booth/verify_report.json`・`booth/room_specs/`・`booth/pack_base.py`・`booth/asset_extract.py`・`booth/legacy_templates.py`・`booth/diff_check.py`は現状未コミット
- 旧世代のBOOTH販売展開（前ラウンド）成果物（`booth/all-packs`旧版, `booth/thumbnails`, `booth/listings`, `booth/signal-pack`, `booth/verify_report.json`旧版）はユーザー指示で削除済み（git履歴には残っている。コミット`3101d72`）

---

## 次にやること（未着手）

### 本サイト側
1. **楽天モーションウィジェットの位置調整**
   - `rakutenArea`（`top:60%;left:76%;width:21%;height:16%`）が楽天モニターの位置
   - DevToolsでウィジェットのDOMクラス名を確認 → CSSで上書きしてモニター内に収める
   - 準備できたら `templates/kanrinin.html` に以下を戻す：
     ```html
     <script type="text/javascript">rakuten_design="slide";rakuten_affiliateId="54f69915.48152f01.54f69916.13ac2b57";rakuten_items="ctsmatch";rakuten_genreId="0";rakuten_size="300x160";rakuten_target="_blank";rakuten_theme="gray";rakuten_border="off";rakuten_auto_mode="on";rakuten_genre_title="off";rakuten_recommend="on";rakuten_ts="1782784526853";</script>
     <script type="text/javascript" src="https://xml.affiliate.rakuten.co.jp/widget/js/rakuten_widget.js?20230106"></script>
     ```

2. **クリック領域の座標微調整**（ローカル確認後）
   - Amazon棚: `top:40%;left:0%;width:22%;height:28%`
   - 楽天モニター: `top:60%;left:76%;width:21%;height:16%`
   - ズレていればDevToolsで確認して教えてもらう

3. **観測域（/observation）の更新** — 更新頻度を上げたい部屋、未着手

### OBSパック 部屋別個性化リニューアル（`ROADMAP.md`）
- 工程6: 全再生成・検証拡張（verify_packs差別化チェック・final_checkのzipサイズ上限）・thumbnails/listings再生成・コミット（唯一の残工程）
- 工程1〜6完了後、`ROADMAP.md`・`booth/`配下の新規/変更ファイルをコミットするかどうかまろに確認する（現状未コミット）

---

## 重要コンテキスト

### 技術構成
- FastAPI + Jinja2 + Vanilla JS/CSS（ReactなしTypeScriptなし）
- 本番: Vercel。`api/index.py` → FastAPIルーティング
- **新しい画像フォルダを `static/images/` 以下に追加したら `vercel.json` の `excludeFiles` に必ず追記すること**
- ローカル起動: `uvicorn main:app --reload`（ポート8000）

### エレベーター・階層構成
| 階 | 内容 |
|---|---|
| 01（M） | 管理人室（/kanrinin）のみ |
| 02 | observation / observer / archive |
| 03 | signal / news（/typhoon-news/）/ daimyojin |
| 04 | hyougi / gokuraku / exit |
| 05 | null / ma / particles |
| 06 | ripple / colony / dot-art / matsuri / namahage |

### 管理人室のクリック領域一覧
| ID | 対象 | 動作 |
|---|---|---|
| ofuseArea | 賽銭箱 | Ofuse外部リンク |
| boothArea | BOOTHダンボール | BOOTH外部リンク |
| crowdfundingArea | お知らせ掲示板 | クラウドファンディングリンク |
| snsArea | 古いPC | SNSモーダル（X/TikTok/YouTube） |
| bellArea | 呼び鈴 | ランダムメッセージ＋目玉表示 |
| keyBoxArea | 鍵ボックス | 「開けられない部屋の鍵」モーダル |
| annihilationKeyArea | 消滅の鍵 | 暗転→404演出 |
| noteArea | 管理日誌 | 日誌モーダル（JSON読込） |
| redPhoneArea | 赤い電話 | シナリオ連動（KYOUKAI_SCENARIO） |
| amazonArea | 亜魔逐管理用品棚 | Amazonアソシエイトランダム遷移 |
| rakutenArea | 楽天受信モニター | （ウィジェット調整待ち） |

### 外部URL（確定済み）
- BOOTH: `https://voidscan.booth.pm/`
- クラウドファンディング: `https://motion-gallery.net/projects/kyoukai`
- Ofuse: `https://ofuse.me/be78f6ed`
- 楽天アフィリエイトID: `54f69915.48152f01.54f69916.13ac2b57`
- X: `https://x.com/maro1523095`
- TikTok: `https://www.tiktok.com/@kyoukai.archive`
- YouTube: `https://youtube.com/@hetayoko1109`

### キャッシュバスト
CSS・JS変更後はHTMLの `?v=N` を上げること（現在 `kanrinin.js?v=2`、`kanrinin.css?v=scenario1`）

### booth/（OBSパック）の構成（工程1リファクタ後）
```
booth/pack_base.py        # HTMLシェル・共通CSS部品(任意利用)・write_pack/make_zip
booth/asset_extract.py    # PROJECT_ROOT・copy_image・read_source・ASSET_MAP(部屋ID→本体画像パス)
booth/legacy_templates.py # 旧世代テンプレート一式(ROOMS/CANVAS_JS/waiting_html等)。room_specsが工程2以降で専用実装に置き換わるまでの移行措置
booth/room_specs/         # 部屋別テンプレート16ファイル+__init__.py(load_all_specs)
booth/generate_packs.py   # 生成フロー本体。room_specs.load_all_specs()経由。ROOMSはlegacy_templatesから再エクスポート(final_check等の互換維持)
```
- ASSET_MAP実地調査結果: 方式B(画像同梱)確定 = kanrinin, namahage, matsuri, fukashitsu, typhoon-news, daimyojin。方式A(コード演出)へ変更 = ma, gokuraku（部屋専用の本体背景画像が存在しないため）
- room_specsのファイル名はハイフン不可のため `typhoon-news` は `typhoon_news.py`（SPEC内idは`typhoon-news`のまま）

### 主要ファイル
```
main.py
templates/kanrinin.html      # 管理人室HTML
static/kanrinin.css          # 管理人室CSS
static/kanrinin.js           # 管理人室JS（?v=2）
static/kanrinin-diary.json   # 管理日誌本文（ここだけ編集で文章更新可）
static/outside-items.js      # AmazonアソシエイトURL一覧
static/affiliate-links.js    # 祭壇用Amazonリンク
static/images/kanrinin/kanrinin-room-9x16.png  # 室内背景画像
static/images/entrances/entrance-kanrinin.png  # 入口画像
static/matsuri.css / matsuri.js
static/namahage.css / namahage.js
static/kyoukai-floor.js      # 階層ロビーの部屋一覧
static/kyoukai-elevator.js   # エレベーター（1階=M表示）
vercel.json                  # excludeFiles 要注意
data/kyoukai_world.md        # 世界観辞典（AI引き継ぎ用正本）
```
