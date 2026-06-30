# HANDOFF_KYOUKAI.md — 2026-06-30（最新）

このファイルを新規チャット・Claude Code・Codex の冒頭に貼るだけで再開できます。

---

## 直近でやったこと

- 管理人室（/kanrinin）の室内画像を新しいものに差し替えた（`static/images/kanrinin/kanrinin-room-9x16.png`）
- Amazon棚（亜魔逐管理用品棚）クリック領域を追加 → `outside-items.js` のアソシエイトリンクからランダム遷移
- 楽天モーションウィジェットのクリック領域（`rakutenArea`）を追加済みだが、ウィジェット本体は位置調整のため一時外してある
- vercel.json の excludeFiles に matsuri / namahage を追加 → 本番で棒入れ祭・なまはげが表示されない問題を修正済み
- なまはげ（/namahage）・棒入れ祭（/matsuri）の実装完了・本番稼働中

---

## 現在の状態

- **本番**: 正常稼働中（`https://www.void-kyoukai.net`）
- **ローカル**: `C:/Users/pc/Documents/Claude/Projects/kyoukai` が最新
- **ブランチ**: main、全変更プッシュ済み
- **最新コミット**: `9320147 Add Amazon/Rakuten areas to kanrinin; update room image`

---

## 次にやること（未着手）

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
