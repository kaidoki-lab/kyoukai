# HANDOFF_KYOUKAI.md — 2026-07-08（最新）

このファイルを新規チャット・Claude Code・Codex の冒頭に貼るだけで再開できます。

---

## 直近でやったこと（2026-07-08）

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
- **BOOTH販売展開（`ROADMAP.md` 参照）**: 工程1〜6すべて実装完了・未コミット。工程6は機械的チェック（`final_check.py`）は全pass。残るはユーザーによるOBS実機確認のみ（`booth/listings/_OBS実機確認手順.md` 参照）

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

### BOOTH販売展開（`ROADMAP.md`）
- 工程6: 機械的チェック（`booth/final_check.py`）は完了・ALL PASS。残タスクはユーザーによるOBS実機確認のみ
  - 手順書: `booth/listings/_OBS実機確認手順.md`（任意の1部屋分のwaiting/brb/lower_thirdをOBS Studioのブラウザソースで確認）
  - 確認完了後、ROADMAP.mdの工程6の完了条件2つ目にチェックを入れ、状態を「完了」に更新すること
- 全工程完了後、`ROADMAP.md`・`booth/`配下の新規/変更ファイルをコミットするかどうかまろに確認する（現状未コミット）

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
