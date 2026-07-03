# KYOUKAI 世界辞典

このファイルはKYOUKAIに関わるAIへのコンテキスト注入用辞典。
企画提案・コンテンツ生成・SNS案作成の際は必ずこのファイルを参照すること。

---

## KYOUKAIとは

KYOUKAIは「境界」を名乗る実験的Webサイト。
ブログでも解説サイトでもない。**訪問者が体験する場所**。

九龍城塞のような密集・混沌・有機的な構造を持つ。
訪問者は探索するうちに「自分が観測されていた」という逆転に気づく。

ジャンルとしては**アート・実験映像・インタラクティブ体験**に近い。

---

## 「境界」という名前

意図的に曖昧にしている。以下の複数の意味を同時に持つ：

- 存在するものとないもの、見えるものと見えないものの間
- 見る側と見られる側の境目が溶ける場所
- 現実とデジタル空間が侵食し合う感覚
- どれとも言えない、定義を拒む場所

単一の意味に確定させないことが世界観の核心。

---

## 核心テーマ

**「観測」の逆転** — 訪問者が何かを観測しているつもりが、実は観測されていた。

- 観測する → 観測される → その境界が溶ける
- 異常感は段階的に増す設計（初訪問では気づかない）
- 「おかしさ」は主張しない。静かに侵食する

---

## 各部屋の世界

| 部屋名 | ルート | 核心 |
|---|---|---|
| 入口域 | / | KYOUKAIへの入口群。スマホでは横スクロールで各部屋の入口が並ぶ |
| 観測域 | /observation | 何かを観測している感覚。何を観測しているかは曖昧 |
| 評議録 | /hyougi | 誰かの記録。誰が書いたかは不明 |
| 受信域 | /signal | 外部からの信号。発信源は未確認 |
| 台風ニュース | /typhoon-news/ | ニュース番組の顔をした短尺映像素材室。冗談の名前が災害情報として流れる |
| 崩落域 | /null | 世界崩壊、崩壊度上昇、接続悪化、失敗方向を扱う |
| 逆観測室 | /observer | 観測者が観測されていたと気づく。最深部 |
| 境界域 | /exit | 内部と外部の境界。出口不能、接続不安定、少女の逃走記録 |
| 記録室 | /archive | 出来事のログ。感情を排した記録 |
| 外部接続 | /outside | KYOUKAIの「外」への扉。世界の外縁 |
| 悪魔の間 | /ma | 逆観測室の隠し扉の先。再訪によって大魔将との関係が変化する |
| AI大明神 | /daimyojin | 信仰と機械が混ざった祈願装置 |
| 極楽域 | /gokuraku | 引き出しと音響装置が積み上がった奥の部屋 |
| 粒子観測 | /particles | 粒子群を観測する部屋。意味より運動が先にある |
| 波紋域 | /ripple | 触れると世界が応答するが、一点だけ命令を聞かない |
| ドット花火崩壊 | /dot-hanabi | ドット絵の夜の街に花火を打ち込む。3発目以降はランダムで爆弾となり、街を段階的に破壊する |
| 境界街区 | /city | 一時導入された町の探索領域。現在はトップ主導線からは外し、必要に応じて再接続する |

---

## 各部屋の詳細

### 入口域（/）
KYOUKAIの入口。最初の接触点。
- 「何かが存在することへの確信」がある。何が存在するかは語らない
- 訪問者は一つの部屋へ案内されるのではなく、入口群の前に置かれる
- スマートフォン版は縦長入口画像を横に並べ、スクロールで部屋を選ぶ
- 各入口の表示名はリンク名ベースの英語表記に統一する
- 説明文ではなく、入口の造形、色、足元の位置、ラベルだけで意味を出す
- 背景は黒。余白は「外側」ではなく、まだ接続されていない領域として扱う

### 観測域（/observation）
最も活動が多い部屋。KYOUKAIの心臓部。
- 生命体の観測ログが積み上がる
- ログは感情を持たない。しかし何かを感じさせる
- 観測対象は「訪問者」である可能性を示唆する
- 更新頻度が高いほど「生きている感」が増す

### 評議録（/hyougi）
誰かが記録した議事録。発言者は不明。
- 議題も結論も曖昧
- 複数の声がある。合意しているのか対立しているのかわからない
- 読むほど不安定になる文体が理想

### 受信域（/signal）
ラジオのような場所。何かを受信している。
- 信号の発信源は特定されていない
- ノイズと信号の境界が曖昧
- 受信内容は断片的で、意味が完結しない
- 「誰かが送っている」という気配だけがある

### 台風ニュース（/typhoon-news/）
ニュース番組の顔をした、YouTube Shorts / TikTok / X向けの短尺映像素材室。
- 生成済みの台風ニュース画像を背景に、速報帯、情報パネル、台風名、縦コピー、警戒ボックス、テロップ、雨、稲妻、ノイズを重ねる
- 台風名は「後ほど連絡します」「検討します」「お母さんに聞いて」など、日常的な保留語が災害名として扱われる
- ホラーや研究所UIではなく、真面目なニュース番組の形式でふざけた名前だけが異常化する
- `typhoonPresets` を変更すると別の台風名へ差し替えられる。URLパラメータ `?name=` でも指定できる
- トップ入口では `news` として表示し、石造アーチの入口画像 `static/images/entrances/news.png` から接続する

### 崩落域（/null）
世界崩壊、崩壊度上昇、接続悪化、失敗方向を扱う部屋。
- データがある。でも何のデータかわからない
- ページとして機能しているが、押すほど状態が悪化する
- 崩落と過剰な情報量が同時にある
- ここに長くいると「自分が何をしているか」がわからなくなる設計
- `/exit` が境界を越えようとする場所なら、`/null` は崩壊が加速する側

### 逆観測室（/observer）
KYOUKAIの最深部。到達した訪問者だけが来る。
- ここで「観測する側と観測される側の逆転」が完成する
- テキストが訪問者に語りかける構造
- 「あなたはずっと観測されていた」という気づきの場所
- 壮大に演出しない。静かに、そっと知らせる

### 境界域（/exit）
外へ出るための接続口に見える場所。
- 実際には、部屋と部屋、内部と外部、少女の逃走記録が混線する通路
- 出口そのものではなく、接続中に挟まるロード画面が本体
- 訪問者は進んでいるつもりだが、見ているのは境界を越えようとする少女の断片である
- 少女は案内役でも主人公でもない。段ボール開封によって始まった異常に巻き込まれた最初の観測対象
- 終わりのような場所だが、終わりではない

### 記録室（/archive）
感情を排した観測記録の集積。
- 日付・ID・内容の羅列
- 感情は排除されているが、読むと感情が生まれる
- 削除されたはずの記録が残っている気配がある

### 外部接続（/outside）
KYOUKAIの「外」への扉。
- ここから先はKYOUKAIではない
- 外部リンク集だが、リンク先の説明が不穏
- 「外」に何があるかはわからない

### 悪魔の間（/ma）
逆観測室の中央にある「?」の扉からのみ到達できる隠し部屋。
- 玉座に座る存在は、4回目の訪問で「大魔将」と名乗る
- 訪問回数は端末内に記録され、再訪するたびに会話と関係性が進行する
- 初期は拒絶的だが、再訪を重ねると訪問者の存在を受け入れ始める
- 会話は説明ではなく、短い応答と沈黙で距離の変化を示す
- ブラウザ版とスマートフォン版で専用背景を使用する
- 背景には緩やかな呼吸モーションがあり、会話表示には低い声のような短音が伴う
- 会話終了後は逆観測室へ戻る。通常のナビゲーションには露出しない
- 検索エンジンには公開せず、発見した訪問者だけが存在を知る

### AI大明神（/daimyojin）
信仰と機械が混ざった祈願装置。
- 神社、奉納、機械、札、端末が同じ構造物の中にある
- 占い・祈願に見えるが、処理されているものが願いなのか観測結果なのかは明かさない
- 町の小さな祠から接続されていた経緯がある

### 極楽域（/gokuraku）
引き出し、スピーカー、祠、鍵、奥へ続く通路が積み上がった部屋。
- 「極楽」という語を明るく扱わない
- 過剰な収納と音響装置が、記憶の保管庫にも通路にも見える
- 入口画像はトップ入口スクロールで使用する

### 粒子観測（/particles）
粒子群を観測する部屋。
- 画面内の運動と反応が先にあり、意味は後から発生する
- 外部信号やoutsideとは別扱い。画像入口を持つ
- トップ入口スクロールでは `particles` の英語名で表示する

### 波紋域（/ripple）
触れることで世界が応答する部屋。
- ドットや波紋はゲーム要素ではなく、観測対象の反応として扱う
- 触れた結果が完全に制御できない一点を残す
- トップ入口スクロールでは `ripple` の英語名で表示する

### 境界街区（/city）
町として一時導入された探索領域。
- `city-001` から `city-010` までの導線、街路、祠、宿泊街、奉納街、祭壇前通路などを持つ
- 現在のトップ主導線からは外している
- 今後使う場合は、トップから直接入れるのではなく、既存部屋のホットスポットやNewExitなどから再接続する
- 街区のホットスポットは、説明文ではなく画像内の意味がある場所へ置く方針

## テキストトーン

**記録・ログ風** — 感情を排した観測記録のような文体。

- システムログ、観測報告、断片的な記述
- 主語が曖昧、または人間でない可能性がある
- 詩的ではなく、冷たく事務的に見えて、実は不気味
- 宣言・告知口調は使わない
- 励ましや明るさは排除

例：
- NG: 「KYOUKAIへようこそ！楽しんでいってください」
- OK: 「接続を確認した。観測を開始する」

---

## コンテンツ方針（SNS・YouTube）

**合うもの：**
- アート・実験映像
- 画面を見せる（顔出しなし）
- 雰囲気・空気感で語る
- 意味が一義に決まらない演出
- 静かな不気味さ、侵食感
- 「何かが起きている」という示唆

**絶対に合わないもの：**
- ハウツー・解説・教育系（「〇〇のやり方」「わかりやすく解説」）
- 明るい・ポジティブ・励ます内容
- トレンド便乗（バズネタ・時事ネタ乗っかり）
- 顔出し・キャラクター主体のVlog・トーク
- 「チャンネル登録お願いします」的な直接的CTA
- KYOUKAIを「普通のWebサイト」として扱う説明

---

## YouTube Shortsの世界観指針

動画はKYOUKAIの「記録の断片」として機能する。
視聴者はショートを見て、KYOUKAIという場所の存在を知る。

- タイトルは問いかけか、不完全な文にする
- 「〇〇とは？」「〇〇の方法」型タイトルは禁止
- 視覚：サイトの映像・パーティクル・テキスト演出
- 音：アンビエント・ノイズ・電子音（人声不要）
- 尺：意味が終わる前に切る（余白を残す）
- 「KYOUKAI」という言葉は毎回出さなくていい

---

## 禁止ワード（提案時に使わない）

解説、わかりやすく、入門、方法、やり方、コツ、裏技、チャンネル登録、
チャレンジ、挑戦してみた、〇〇してみた、ランキング、おすすめ、
元気、前向き、感動、おめでとう

---

## 更新進捗

### 2026-06-26
- `/typhoon-news/` を台風ニュース風ショート演出の部屋として追加した。背景は `typhoon-news/assets/typhoon-news-bg.png`、演出は `typhoon-news/index.html`, `style.css`, `script.js` で構成する。
- トップ入口に `news` を追加し、入口画像は `static/images/entrances/news.png` とした。`news` から `/typhoon-news/` へ接続する。
- トップページ `/` をスマホ向けの横スクロール入口一覧へ変更した。旧トップ画像と旧ホットスポット表示はトップでは使わない。
- トップ入口スクロールの部屋名は、英語リンク名に統一した。表示対象は `observation`, `observer`, `archive`, `signal`, `news`, `daimyojin`, `hyougi`, `gokuraku`, `exit`, `null`, `ma`, `particles`, `ripple`。
- `external-signal` と `outside` は画像入口を持たせない。トップ入口スクロールには出さず、元々の導線位置に戻す方針。
- `guide` / 案内人は画像入口を持たせない。
- 入口画像は `static/images/entrances/` に集約した。入口カードの足元位置を揃え、黒背景の上で各入口が同じ地面に立って見えるよう調整した。
- 横スクロール停止時、一度だけ軽く揺れて止まる動きを追加した。操作説明ではなく、物体感を出すための反応として扱う。
- `?measure=1` の実測線は確認用に一度作成したが、現在は削除済み。
- 境界街区 `/city` は、トップ主導線から外した。今後必要ならNewExitや既存部屋のホットスポットから再接続する。
- 関連ファイル: `templates/home.html`, `static/home-entrances.js`, `static/space.css`, `static/images/entrances/`, `tests/test_home_entrances.py`
- 最新コミット: `2b2edcf Add mobile entrance carousel`

### 2026-06-23
- Central OSの運用を通常ルートから外すため、KYOUKAI単体のワールドDB正本を `data/kyoukai_world.md` として分離した。`central-os/lore/kyoukai-world.md` は旧参照・履歴扱いにする。
- トップ画面の主導線を `/city` に集約。中央の観測中領域から町へ入る構造に変更した。現在は2026-06-26更新により、この構造は旧運用扱い。
- 境界街区を `city-001` から `city-010` までの探索領域として整理。中心街路、神社脇路地、宿泊街、自販機横丁、裏路地、参道裏口、奉納街、祭壇前通路、階段上入口、宿泊街内部を接続済み。
- 町のホットスポットから既存の主要領域へ再配置。`/observation`、`/signal`、`/null`、`/observer`、`/daimyojin`、`/outside`、`/altar` に加えて、`/archive`、`/hyougi`、`/exit`、`/gokuraku`、`/particles`、`/ripple`、OFUSE を街区内へ接続した。
- 祭壇域 `/altar` は新しい16:9祭壇画像へ差し替え済み。旧トップ由来のリンク群は祭壇および街区側へ分散し、トップ画面からは直接見せない運用にした。
- 街区ホットスポットは通常時に黄色表示を出さず、透明な小領域として運用する。導線は説明文ではなく、看板・祠・階段・床の反射・奉納物など画像内の意味がある場所に置く。
- 関連ファイル: `data/city_locations.json`, `data/city_districts.json`, `services/city_service.py`, `templates/city/location.html`, `templates/city/altar.html`, `static/city/css/city.css`, `static/city/js/city.js`

### 2026-06-20
- `/ripple` を追加。全画面Canvasで構成された、説明なし・ボタンなし・スコアなしの観測型インタラクティブコンテンツ。
- 画面全体は規則的なドットグリッドで埋められ、タップ/クリックで波紋、スワイプ/ドラッグで連続波紋が発生する。
- 波紋が通過したドットは、暗赤、赤、黄、青、白の順に状態が進み、軽く膨らんでから元に戻る。
- 画面内に一つだけ `isRebelDot` を持つ異常ドットが存在する。通常波紋に完全には従わず、色を変えない、周囲を変える、逃げるなどの違和感を残す。
- 放置中も小さな波紋が自然発生し、画面全体は徐々に暗く沈む。触ると再び反応が戻る。
- 1分に一回、中央から広い黒戻し波紋が発生し、通過したドットを強制的に黒へ沈める。世界が周期的に初期化されるように見えるが、説明はしない。
- トップ画面 `/` に `/ripple` への透明ホットスポット導線を追加。PCでは左下寄り、スマホでは下部中央寄りに配置。
- `/particles` が粒子群の観測であるのに対し、`/ripple` は「触れると世界が応答するが、一点だけ命令を聞かない」観測体験として扱う。
- この追加はゲームではない。目的、クリア、ランキング、説明文を持たせない。KYOUKAIの「意味がありそうで意味が分からない体験」の一室として維持する。
- 関連ファイル: `templates/ripple.html`, `static/ripple.css`, `static/ripple.js`, `templates/home.html`, `static/space.css`, `tests/test_ripple_page.py`
- 運用メモ: Central OS自体は今後の通常運用では使用しないため、実装完了時のCentral OS同期・完了イベント記録は不要。このワールドMDは世界観・部屋構成の参照資料としてのみ更新する。

### 2026-06-15
- 悪魔の間（`/ma`）を追加
- 逆観測室（`/observer`）の隠し扉からの導線を実装
- 訪問回数に応じた15段階の会話と「大魔将」の関係変化を実装
- ブラウザ用16:9背景とスマートフォン用9:16背景を実装
- 会話パネル、タイプライター表示、低音演出、背景の呼吸モーションを本番反映

### 2026-06-16
- GA4カスタムイベント計測を追加。各部屋への到達（`room_enter_*`）、外部接続クリック（OFUSE/BOOTH/Amazon/Affiliate）、`/external-signal`の裂け目ホットスポットの操作フロー（タップ→接続演出→選択→追跡/中断）を個別イベントとして記録するようになった
- 悪魔の間（`/ma`）にもGA4計測を追加。隠し部屋への到達も観測対象になった
- Central OSに「イベント観測」パネルを新設。本日の観測者数・部屋別到達数・外部接続クリック数・Signal外部通信の流れをCentral OS上で確認できるようになった
- AI分析官・AI企画官・AI実装監督がイベント観測データを踏まえて考察・企画・実装指示を出せるようになった（ゲーム化禁止は明文化済み）
- KYOUKAI Shorts Factory（`shorts_factory/`）を整備。Central OSの企画案とYouTube分析からAIが収録シナリオを自動生成し、Playwrightでブラウザを操作してKYOUKAI内を自動巡回・録画する仕組みを構築した
- これにより「観測」というKYOUKAIの核心テーマが、ユーザー体験だけでなく制作プロセス自体にも及んだ状態になっている

---

## 更新メモ 2026-06-28

### KYOUKAI入口導線

- トップページは部屋一覧ではなく、KYOUKAIという巨大建築への入口として扱う。
- 基本導線は `トップ /` → `建物全景` → `入口クローズアップ` → `エレベーター室 /elevator` → `階層ロビー /floor/XX` → `各部屋`。
- 建物全景と入口クローズアップは自動進行。ユーザーのクリックを要求しない。
- 部屋数が増えてもトップページの構造は変えない。部屋追加はエレベーター側、または階層ロビー側の行き先データだけを更新する。

### エレベーターと階層ロビー

- エレベーター外観は建物外観とは切り離す。建物外からエレベーターは見えない。
- `/elevator` では右側の上下ボタンで階層番号を増減し、黒い表示窓にCSSで階層番号を表示する。
- エレベーター扉は `4 → 3 → 2 → 1` の画像順で再生し、扉が徐々に開く表現にする。
- `/floor/01` から `/floor/06` まで、各階に入口画像を並べる。部屋を選ぶ場所はトップページではなく階層ロビー。
- 階層表示窓は内部の階数（`/floor/01`等）と表示文字を分けている。1階（管理人室）だけは数字ではなく `M` を表示し、他の階は `02`〜`06` のまま数字表示する（`static/kyoukai-elevator.js` の `floors` 配列の `display` フィールド）。

### 音の扱い

- エレベーター室と階層ロビーでは、獄楽域にある4つの音源を薄く重ねて流す。
- 使用音源は `/static/bgm/bgm_home.mp3`, `/static/bgm/bgm_exit.mp3`, `/static/bgm/bgm_null.mp3`, `/static/bgm/bgm_observer.mp3`。
- ブラウザ制約に合わせ、初回のユーザー操作後に再生を開始する。
- 部屋入口を押した時点でロビー音は停止する。各部屋に入った後までロビー音を持ち越さない。

### COLONY入口と部屋背景

- COLONYの階層ロビー入口画像は `/static/images/colony/entrance-colony.png` を使う。
- `/colony` 本体の背景は `/static/images/colony/concrete_9x16.png` を使う。
- 入口画像と部屋背景は混同しない。入口を押しても再び入口画像だけになる状態は不可。

### 関連実装ファイル

- `templates/home.html`
- `templates/elevator.html`
- `templates/floor.html`
- `static/kyoukai-home-journey.js`
- `static/kyoukai-elevator.js`
- `static/kyoukai-floor.js`
- `static/home-entrances.js`
- `static/space.css`
- `static/colony.css`
- `static/images/colony/entrance-colony.png`
- `static/images/colony/concrete_9x16.png`
- `tests/test_home_entrances.py`
- `tests/test_colony_page.py`

### 最新コミット

- `813b985 Fix colony entrance and hall audio`
- `2c8dcb7 Exclude colony images from function bundle`

---

## 更新メモ 2026-06-28（2）

### 管理人室（/kanrinin, /manager）

管理人室は「管理施設」。Ofuse、BOOTH、クラウドファンディング、SNSへの導線、鍵ボックス、消滅の鍵、管理日誌を持つ。広告ページではなく、昭和〜平成初期のラブホテル受付のような空間として扱う。管理人本人は表示しない。

**階層ロビーへの組み込み**
- 階層ロビーの1階を「管理人室」専用フロアにした。`/floor/01` には管理人室の入口（古い木製ドア、`管理人室`の銘板）だけを置き、観測域・逆観測室・記録室など既存の入口群は2階〜6階へ1つずつスライドした（旧02→03、旧03→04、旧04→05、旧05→06）。エレベーターも1〜6階対応に拡張した。

**背景・目玉**
- 部屋内部の9:16背景画像は `static/images/kanrinin/kanrinin-room-9x16.png`。受付カウンター・赤いカーテン・賽銭箱・お知らせ掲示板（クラウドファンディングQR付き）・BOOTHダンボール・古いパソコン・電話・管理日誌・鍵ボックス（開けられない部屋の鍵）・消滅の鍵・目玉が画像内に描かれている。
- 目玉はCSSアニメーションでは描かない。画像に描かれた目玉を、カーテンの隙間部分にだけ収まる黒い領域（`kanrininEyeGap`、カーテン布には重ねない寸法）で覆い隠す。通常時は完全に不透明（非表示）。`bellArea`（呼び鈴）を押すと黒い領域がopacity 0.4まで薄れ、画像の目玉がうっすら透けて見える。3秒後に自動で不透明に戻る。消滅の鍵を引いた場合はタイマーをクリアして薄い状態のまま固定する。

**透明クリック領域（画像内の対象物に合わせて配置）**
- `ofuseArea`=賽銭箱、`boothArea`=BOOTHダンボール、`crowdfundingArea`=お知らせ掲示板、`snsArea`=古いパソコン、`bellArea`=呼び鈴、`keyBoxArea`=鍵ボックスの壁、`annihilationKeyArea`=消滅の鍵、`noteArea`=管理日誌ノート。

**各ギミック**
- 呼び鈴: ランダムメッセージを表示し、目玉を薄く見せる。
- 鍵ボックス: 「開けられない部屋の鍵」モーダルを表示（個別の鍵クリックはなし、ボックス全体クリックのみ）。
- 消滅の鍵: クリックで確認ダイアログなしに即演出開始。「管理人が鍵を回しました。」表示→暗転→1.5秒後に存在しないパス `/kanrinin/deleted` へ遷移し、グローバル404演出（`templates/404.html`, `static/kyoukai-404.js`。訪問回数に応じて文字が崩壊し5回目以降は消滅する仕様）に接続する。ブラウザは閉じない、戻るボタンは無効化しない。
- SNS: 単一リンクではなく一覧モーダル（`snsModal`）。X `https://x.com/maro1523095`、TikTok `https://www.tiktok.com/@kyoukai.archive`、YouTube `https://youtube.com/@hetayoko1109` の3つを表示する。
- 管理日誌: 中央のノート（`noteArea`）クリックで管理日誌モーダル（`diaryModal`）が開く。4ページ（管理日誌／更新履歴／未解決案件／鍵管理記録）を前後ページ送りで閲覧できる。DB・投稿・AI生成は使わず、Escキーでも閉じられる。本文は `static/kanrinin-diary.json` に分離しており、`static/kanrinin.js` がノートクリック時にfetchして表示する。JSのロジックとテキストを分離しているため、今後ページ内容を更新したい場合はこのJSONファイルだけ編集すればよい。

**外部リンク（本番URL確定済み）**
- BOOTH: `https://voidscan.booth.pm/`
- クラウドファンディング: `https://motion-gallery.net/projects/kyoukai`
- Ofuse: `https://ofuse.me/be78f6ed`

**関連ファイル**
- `templates/kanrinin.html`, `static/kanrinin.css`, `static/kanrinin.js`, `static/kanrinin-diary.json`
- `static/images/entrances/entrance-kanrinin.png`, `static/images/kanrinin/kanrinin-room-9x16.png`
- `static/kyoukai-floor.js`, `static/kyoukai-elevator.js`, `main.py`, `tests/test_home_entrances.py`

---

## 更新メモ 2026-06-28（3）

### 棒入れ祭（/matsuri）

豊穣信仰の奉納儀式として処理する部屋。「KYOUKAI 棒入れ祭 素材入手担当表 v1.0」に基づく。人物・手・群衆は描かない。棒と穴、注連縄・紙垂・御幣などの祭具のみで構成する。

**実装範囲（今回完了したのはCSS/JS実装担当分のみ）**
- 棒（`matsuriPole`）を繰り返しタップすると、穴（`matsuriHole`）へ少しずつ沈む。タップごとに画面の小揺れ、棒の振動、土煙、ランダムで紙吹雪が発生する。
- 10回タップでクライマックス：フラッシュ・衝撃波・紙吹雪大量発生・モーションブラー・「ヨイショーー！！」→「奉納完了。」。完了後は「もう一度」ボタンで`resetMatsuri()`によりリセットできる。
- 掛け声・効果音はファイルが存在しない場合は黒い処理（再生をスキップ）でエラーにならない設計。画像も同様に、無ければCSSの色面・グラデーションで表示する（実装確認に画像生成を待つ必要はない）。

**アセット配置場所**
- 画像: `static/images/matsuri/{background,pole,hole,decoration,confetti,effects,props}/`（期待ファイル名は`static/images/matsuri/README.md`に記載、担当表のファイル名と一致）
- 音声: `static/audio/matsuri/{voices,sfx}/`（期待ファイル名は`static/audio/matsuri/README.md`に記載）
- 画像生成（ChatGPTへのプロンプト作成）、フリー素材サイトからの効果音・写真入手、掛け声の自作録音は未着手。担当表の通り別作業者が行う想定。

**画像の実装（2026-06-28追記）**
- ChatGPTが生成した「素材入手担当表」のリファレンスシート1枚（36個のアセットを1枚にまとめた画像）から、`scripts/extract_matsuri_assets.py` で個別に切り出して`static/images/matsuri/`へ配置済み。
- 紙吹雪・土煙・衝撃線・フラッシュ・モーションブラー・ビネット・棒の影・穴の影・注連縄・紙垂・御幣は黒背景を透過処理（輝度ベースのアルファ変換）した。背景・棒・穴・小物は写真としてそのまま矩形クロップしている（棒の画像だけ背後にうっすら紺色の矩形が残るが実用上は許容範囲）。
- 切り出し座礁はリファレンスシート1枚に依存した手動調整のため、別の生成画像に差し替える場合はこのスクリプトの座標は使えない。新しいシートから切り出す場合は座標を再調整するか、各アセットを個別に生成し直す方が確実。

**入口導線**
- 階層ロビー6階（`/floor/06`）の入口一覧に `matsuri` を追加した（ripple, colony, dot-art に続く4枚目）。入口画像は鳥居越しに棒と穴を見た正面構図 `static/images/entrances/entrance-matsuri.png`。

**棒の表示サイズ調整（2026-06-28追記）**
- `.matsuri-pole` のサイズは、見切れと小さすぎのバランスを見ながら調整した。最終値: `top:10%; left:38%; width:24%; height:42%;`（`static/matsuri.css`）。

**穴画像の差し替え（2026-06-29）**
- `10_hole_main.png` を、石組みの穴の写真から「石ブロックを連結した楕円リング」のイラスト画像に差し替えた。元画像は黒背景の上に描かれていたため、輝度ベースで黒を透過処理してから保存している。リング中央の黒い穴部分はそのまま透明（＝下の地面背景がそのまま見える）になる。

**ゲームロジックの見直し（2026-06-29）**
- 「奉納10回で確定クリア」という固定カウント方式を廃止した。表示カウンターも削除。
- 代わりに、タップごとに深さ(`depth`)が少し進み、30%の確率でランダムに少し後退する積み上げ方式にした（`static/matsuri.js`の`FORWARD_RANGE`/`BACKWARD_RANGE`/`FALLBACK_CHANCE`）。
- ゴール条件: 棒の当たり判定（`.matsuri-pole-hit`）の中心が、穴（`.matsuri-hole`）の中心に到達した深さ。当たり判定や穴の位置を変えたら`DEPTH_MAX`の再計算が必要（計算式はJS内コメントに記載）。
- 当たり判定（`.matsuri-pole-hit`）は画像本体（`.matsuri-pole-visual`）とは別要素に分離した。`.matsuri-pole-stage`が回転・深さの変形を担当し、視覚的な棒の大きさを変えずに当たり判定だけ調整できる。

**棒と穴の重なり順（2026-06-29）**
- 石のリング画像（`.matsuri-hole`）は棒より背面（z-index:2）。
- 黒い穴の中心部分（`.matsuri-hole__shadow`、独立した要素に分離済み）だけを棒より前面（z-index:6）に出している。これにより、石の画像が棒に不自然に重ならず、棒の先端が黒い穴に差し掛かると沈んで消えるように見える。
- ゴール間近で穴全体を前面に切り替える方式（is-buryingクラス）は一度試したが、切り替えの瞬間が不自然だったため撤廃した。

**音の調整（2026-06-29）**
- 観客の歓声・拍手（`crowd_cheer_01〜04.mp3`：女声・男声「オーッ！」を含む4種）を環境音としてランダムに流し続ける。3本の独立ループを少しずらして開始し、前の音の終了を待たずに次を鳴らすため、瞬間的に重なって途切れない。
- 手持ち花火・打ち上げ花火（`firework_handheld_01.mp3`, `firework_launch_01.mp3`）はゴール（クライマックス）の瞬間だけ鳴らす。ランダムな後退タップでは鳴らさない。

**削除した要素（2026-06-29）**
- 画面上部の注連縄（`matsuri-decoration--shimenawa`）。
- タップ時に穴付近から出ていた土煙エフェクト（`spawnDustPuff`、`30_dust_medium.png`使用）。素材シートからの切り出しが上手くいっておらず何の画像か判別できなかったため削除した。

**関連ファイル**
- `templates/matsuri.html`, `static/matsuri.css`, `static/matsuri.js`
- `static/images/matsuri/README.md`, `static/audio/matsuri/README.md`
- `static/images/entrances/entrance-matsuri.png`
- `static/audio/matsuri/sfx/crowd_cheer_01.mp3`〜`04.mp3`, `firework_handheld_01.mp3`, `firework_launch_01.mp3`
- `scripts/extract_matsuri_assets.py`
- `main.py`（`/matsuri`ルート追加）
- `static/kyoukai-floor.js`, `tests/test_home_entrances.py`（floor06への追加）

---

## 更新メモ 2026-06-30

### なまはげ（/namahage）

民俗の「なまはげ」をモチーフにした観測型インタラクション部屋。

**基本構造**
- 9:16背景画像 `static/images/namahage/namahage-room-9x16.png` を全画面表示。
- なまはげの顔の両目の位置に、16×12の低解像度Canvas（`namahage-eye--left`, `namahage-eye--right`）を重ねる。`image-rendering: pixelated` で粗粒子のドット目として表示する。
- 操作はタップ・長押し・ダブルタップのみ。UI要素・ボタン・説明文は持たない。

**目の反応（CONFIG定数で管理）**
- 通常: 赤く光る瞳が緩やかに明滅（idle状態）。
- タップ（短押し）: 目が瞬きし、短い刺激音（怒鳴り声系）が再生される。
- ダブルタップ: 目が見開き、強い光りを放った後に半目状態に移行。
- 長押し: 0.8秒以上押し続けると「起動シーケンス」が走り、目が段階的に変化。長押しを途中で離すとシーケンスを即時中断する。

**長押しシーケンスの修正（2026-06-30）**
- 長押し途中でユーザーが指を離した場合、内部のチェーン`setTimeout`がキャンセルされずにシーケンスが続行するバグがあった。`longPressSeqTimers`配列で内側のタイマーIDをすべて記録し、`endLongPress()`から`clearLongPressSeq()`を呼ぶことで確実に全タイマーを中断するよう修正した（`static/namahage.js`）。

**目の座標（DevToolsで調整済み）**
- `.namahage-eye--left`: `top:31.5%; left:30%; width:14%; height:7%`
- `.namahage-eye--right`: `top:31.5%; left:60%; width:14%; height:7%`
- 座標は背景画像のなまはげの顔の実位置に合わせた値。背景画像を差し替えた場合は再調整が必要。

**入口導線**
- 6階（`/floor/06`）の入口一覧に `namahage` を追加した（ripple, colony, dot-art, matsuri に続く5枚目）。入口画像は `static/images/entrances/entrance-namahage.png`。
- `material: "crack"` を指定。

**本番デプロイ対応（2026-06-30）**
- `vercel.json` の `excludeFiles` に `static/images/matsuri/**` と `static/images/namahage/**` を追加した。これらが含まれていなかったため、本番環境でPython関数バンドルが肥大化し、matsuriとnamahageへのルートが機能しない状態になっていた。追加後にプッシュして解消。

**関連ファイル**
- `templates/namahage.html`, `static/namahage.css`, `static/namahage.js`
- `static/images/entrances/entrance-namahage.png`
- `static/images/namahage/namahage-room-9x16.png`
- `vercel.json`（excludeFiles: matsuri/namahage追加）
- `main.py`（`/namahage`ルート追加）
- `static/kyoukai-floor.js`, `tests/test_home_entrances.py`（floor06への追加）

---

## 更新メモ 2026-06-30

### シナリオモードシステム v1.0

KYOUKAIに、今後シナリオ・部屋・住人・階層を継続追加できるためのデータ駆動型シナリオ基盤を追加した。
一本道の物語をコードに書くのではなく、ルート、電話イベント、部屋状態、フロア状態、住人状態を外部データと保存状態で管理する方針。

**基本構造**
- 1フロアは5部屋固定。
- 階数のみ増設可能。
- 部屋追加時は `roomIndex` から `floor` と `slot` を自動算出する。
- 算出式は `floor = Math.floor(roomIndex / 5) + 1`、`slot = roomIndex % 5 + 1`。
- 同一フロアに6部屋目は存在しない。6部屋目は自動的に次フロアの1部屋目になる。
- このルールは `docs/境界ワールド.md` の「フロア自動増設ルール」にも記録済み。

**初回モード分岐**
- 初回に管理人室へ入るとシナリオモード開始。
- 初回に管理人室以外へ入ると自由探索モード開始。
- 判定結果は `localStorage` の `kyoukai_scenario_state_v1` に保存する。

**シナリオモードの初期開放**
- シナリオモード開始時は1F、2F、3Fのみ探索可能。
- 4F以上は `story_only` / locked 扱い。
- 4F以上は自由探索では解除されず、赤い電話または管理人イベントでのみ開放される想定。

**赤い電話**
- 管理人室に `redPhoneArea` を追加。
- 電話はプレイヤーから掛けるものではなく、条件成立時のみ着信する。
- 管理人室入室後30秒で着信判定を行う。
- 電話イベントは `static/kyoukai-scenario-events.js` で管理し、会話文をコードへ直書きしない方針。

**状態管理**
- 保存対象はモード、現在ルート、現在章、現在イベント、管理人状態、電話状態、部屋状態、フロア状態、住人状態、取得アイテム、開放済み部屋、会話履歴、進行率。
- 管理人状態は `hidden` / `visible` / `busy` / `away` などに拡張可能。
- 部屋状態は `normal` / `waiting` / `active` / `completed` / `locked` / `disabled` などに拡張可能。
- フロア状態は `locked` / `unlocked` / `story_only` / `completed` などに拡張可能。

**実装構成**
- `static/kyoukai-building-data.js`: 建物、部屋、住人、ルートのデータ定義。
- `static/kyoukai-scenario-events.js`: 電話イベント、管理人イベント、部屋イベントのデータ定義。
- `static/kyoukai-scenario.js`: セーブデータ、モード判定、部屋配置、ロック判定、イベント適用の共通ロジック。
- `static/kyoukai-elevator.js`: 階リストをデータから生成し、シナリオロック状態を反映。
- `static/kyoukai-floor.js`: フロア内5スロット固定表示。部屋は `roomIndex` から自動配置。
- `templates/kanrinin.html`, `static/kanrinin.js`, `static/kanrinin.css`: 赤い電話ホットスポットと着信表示。
- `main.py`: 全HTMLへシナリオ共通スクリプトを注入。`/floor/{floor_number}` は7階以降も受け入れる。

**運用方針**
- シナリオ追加時は、原則として `static/kyoukai-building-data.js` と `static/kyoukai-scenario-events.js` へのデータ追加で対応する。
- シナリオ進行を `if` 文で個別実装しない。
- 部屋番号、階番号、電話番号、住人番号を進行コードへ直書きしない。
- 将来的に100部屋以上、数百イベント規模になっても、基本ロジックを書き換えずに増築できる構造を維持する。

---

## 最上階 / 教会（仮称）

**位置づけ**
- KYOUKAIの通常フロアとは別枠で、常に一番上に配置される最上階専用部屋。
- 通常部屋の「1フロア5部屋固定」ルールの対象外。
- 通常部屋が今後どれだけ増えて階層が伸びても、この部屋だけは常に通常部屋群のさらに上、最上階に1部屋だけ配置する。
- 最上階には他の部屋や空きスロットを表示しない。

**入口**
- 入口画像は `static/images/entrances/entrance-top-floor.png`。
- 建物データでは `topFloorRoom` として通常の `rooms` 配列とは分離して管理する。
- `id` は `top-floor`、URLは `/top-floor`。

**室内**
- 室内9:16画像は `static/images/top-floor/room-9x16.png`。
- `/top-floor` は現時点では室内画像を全画面寄りに表示し、エレベーターへ戻る導線のみを持つ。
- 最終シナリオや教会関連イベントの具体処理は未実装。今後この部屋を最上階・教会・鍵穴系シナリオの受け皿にする。

**実装メモ**
- `static/kyoukai-scenario.js` に `getTopFloorRoom()` を追加し、通常部屋の最大階 + 1 を最上階として自動算出する。
- `static/kyoukai-floor.js` は `topFloorOnly` の部屋がある階では5スロット表示を行わず、その1部屋だけを表示する。
- `docs/境界ワールド.md` に「最上階固定部屋ルール」として記録済み。

**関連ファイル**
- `templates/top-floor.html`
- `static/images/entrances/entrance-top-floor.png`
- `static/images/top-floor/room-9x16.png`
- `static/kyoukai-building-data.js`
- `static/kyoukai-scenario.js`
- `static/kyoukai-floor.js`
- `docs/境界ワールド.md`

---

## 更新メモ 2026-07-03

### 卵部屋（/fukashitsu）

旧称「孵化室」から「卵部屋」に改名。室内背景をピンク色の孵化装置画像（`fukashitsu-room-9x16.png`）に差し替え。

**基本構造**
- 9:16背景画像 `static/images/fukashitsu/fukashitsu-room-9x16.png` を全画面表示。
- 卵エリア（左12%・上13%・幅76%・高61%）に専用Canvasを重ね、`clip-path: ellipse(46% 50% at 50% 50%)` で卵形にマスク。
- 卵の中でパーティクルエンジン（`particle-engine.js`）が動作する。

**パーティクル仕様**
- `ParticleObservationEngine` を `background:'transparent'`・`noAutoResize:true`・`observerEffect:false`・`count:160` で起動。
- `collapsing`フェーズをスキップ（`onPhaseChange`で即座に次フェーズへ進む）。破裂演出はなし。
- 初期は赤・青・黄ともに非常に淡いパステル色。3本のボタンを押すごとに対応色が段階的に鮮やかになる（0回＝淡色、10回＝本来の原色）。
- テキストフィードバックは一切なし。

**ボタン**
- 3つの透明ボタン（栄養・酸素・温度）が下部パネルの3つのボタン画像に重なる。
- 各ボタンを10回押すと完成。「取り出す」ボタンが出現する。

**取り出し後**
- 「取り出す」ボタン押下でパーティクル停止・フェードアウト、背景が `fukashitsu-collected-9x16.png` に切り替わる。
- 再訪時は最初から取り出し後の背景を表示。
- 上部パネル7回タップで隠しリセット。

**フロア配置**
- 2階4番目スロット（`roomIndex: 8`）に配置。
- 入口画像 `static/images/entrances/entrance-fukashitsu.png`、ラベル `EGG`。

**particle-engine.js への追加オプション（後方互換）**
- `noAutoResize: true` — ウィンドウリサイズ時のキャンバス自動リサイズを無効化。
- `background: 'transparent'` — 黒塗りつぶしの代わりに `clearRect` を使用。
- `getColors: fn` — `{r:[R,G,B], b:[R,G,B], y:[R,G,B]}` を返す関数。粒子色と接続線色を動的に変更できる。

**関連ファイル**
- `templates/fukashitsu.html`
- `static/fukashitsu.css`（v4）
- `static/fukashitsu.js`（v10）
- `static/particle-engine.js`（getColors・noAutoResize・transparent対応追加）
- `static/images/fukashitsu/fukashitsu-room-9x16.png`
- `static/images/fukashitsu/fukashitsu-collected-9x16.png`
- `static/images/entrances/entrance-fukashitsu.png`
- `static/kyoukai-building-data.js`（roomIndex:8 に fukashitsu 追加）
- `main.py`（building-data バージョン更新）

---

## 更新メモ 2026-07-03

### シナリオ Route_B「記録されていない人」

KYOUKAIの通常シナリオとして、Route_A「混線している観測」の次に発生する Route_B「記録されていない人」を追加した。

**開始条件**
- シナリオモード中であること。
- Route_A が completed であること。
- Route_B が not_started であること。
- active_route_id が null であること。
- 4F が開放済みであること。
- Route_A の管理人帰還イベント完了後、管理人室に滞在したまま20秒経過すると赤電話が鳴る。
- 管理人室を一度出て再入室する必要はない。

**進行順**
1. `route_b_phone_001`
2. `route_b_room_archive_001`
3. `route_b_room_hyougi_001`
4. `route_b_room_gokuraku_001`
5. `route_b_manager_return_001`

**使用部屋**
- 共通ハブ: `kanrinin`
- Route_B 専用主要部屋: `archive`, `hyougi`, `gokuraku`

**完了時の変化**
- Route_B を completed にする。
- active_route_id を null に戻す。
- completed_scenario_count を +1 する。
- `floor_05` を開放する。
- `archive`, `hyougi`, `gokuraku` は `post_route_b` 状態を保持する。

**制限**
- Route_B 完了では最上階、最終シナリオ、消滅の鍵、巨大鍵穴、最上階鍵穴は開放しない。
- `final_route_available`, `top_floor_unlocked`, `annihilation_key_obtained`, `top_floor_keyhole_active` は false のまま維持する。

**関連ファイル**
- `data/scenarios/route_b.json`
- `static/kyoukai-scenario-events.js`
- `static/kyoukai-scenario.js`
- `static/kyoukai-route-b-room.js`
- `templates/archive.html`
- `templates/hyougi.html`
- `templates/gokuraku.html`
- `templates/kanrinin.html`
- `static/kanrinin.js`
- `main.py`
## 更新メモ 2026-07-03

### シナリオ Route_C「壊れる前の形」

KYOUKAIの通常シナリオとして、Route_B「記録されていない人」の次に発生する Route_C「壊れる前の形」を追加した。

開始条件は以下。

- シナリオモードであること。
- Route_A と Route_B が completed であること。
- Route_C が not_started であること。
- active_route_id が null であること。
- `floor_05` が開放済みであること。
- Route_B 管理人帰還イベント完了後、一度管理人室を退出し、再入室していること。
- 管理人室へ再入室後、20秒経過していること。
- 他の電話イベントが発生していないこと。

進行順は以下。

1. `route_c_phone_001`
2. `route_c_room_null_001`
3. `route_c_room_ma_001`
4. `route_c_room_particles_001`
5. `route_c_manager_return_001`

使用部屋は以下。

- 共通ハブ: `kanrinin`
- Route_C 専用主要部屋: `null`, `ma`, `particles`

Route_C 完了時の状態変化は以下。

- Route_C を completed にする。
- active_route_id を null に戻す。
- completed_scenario_count を +1 する。
- `floor_06` を開放する。
- `null`, `ma`, `particles` は `post_route_c` 状態を保持する。
- current_target_room_id を null に戻す。

Route_C 完了では、最上階、最終シナリオ、消滅の鍵、巨大鍵穴、最上階鍵穴は開放しない。

以下の値は Route_C 完了後も false のまま維持する。

```json
{
  "final_route_available": false,
  "top_floor_unlocked": false,
  "annihilation_key_obtained": false,
  "top_floor_keyhole_active": false
}
```

関連ファイル。

- `data/scenarios/route_c.json`
- `static/kyoukai-scenario-events.js`
- `static/kyoukai-scenario.js`
- `static/kyoukai-building-data.js`
- `static/kyoukai-route-c-room.js`
- `static/kyoukai-scenario-ui.css`
- `templates/null.html`
- `templates/ma.html`
- `templates/particles.html`
- `static/ma.js`

Route_C の会話文、部屋イベント、管理人イベント、日誌はコードへ直接書かず、イベントデータとして管理する。

---

## 更新メモ 2026-07-03

### 部屋マスターフォーマット v1

ShortFACTORYや今後の動画生成AIが既存部屋を扱えるように、部屋ごとのMarkdownを `data/rooms/` に作成した。

今回作成した対象は、全室ではなく以下の5部屋のみ。

- 管理人室 `/kanrinin`
- 観測域 `/observation`
- 受信域 `/signal`
- 崩落域 `/null`
- 卵部屋 `/fukashitsu`

各部屋Markdownには以下の項目を持たせる。

- 基本情報
- コンセプト
- 現在の実装
- 操作仕様
- 動画化仕様
- AI巡回仕様
- ShortFACTORYメモ
- 未解決

`kyoukai_world.md` に書かれていない情報は断定せず、未確定の箇所は `未記載` または `未設定` として残す運用にした。

この部屋マスターは、世界観設定の正本ではなく、ShortFACTORY・Playwright巡回・動画生成AI向けの実務用参照ファイルとして扱う。

**作成ファイル**
- `data/rooms/kanrinin.md`
- `data/rooms/observation.md`
- `data/rooms/signal.md`
- `data/rooms/null.md`
- `data/rooms/fukashitsu.md`

**運用メモ**
- 今後ほかの部屋を追加する場合も、まず `kyoukai_world.md` の記載範囲を基準にする。
- 操作箇所、動画尺、テロップ案、AI巡回手順が不足している部屋は、各部屋Markdownの `未解決` に残す。
- 実装コードの変更と部屋マスター更新は別作業として扱う。
