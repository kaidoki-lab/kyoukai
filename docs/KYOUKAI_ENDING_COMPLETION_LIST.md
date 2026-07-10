# KYOUKAI 終幕完成リスト

作成日: 2026-07-11  
目的: KYOUKAIを終了・完成へ向かわせるために、ChatGPTと相談して作るべき素材、シナリオ、データ、実装要素を洗い出す。

## 前提

- `docs/境界ワールド.md` では、Route_D完了後も `final_route_available`, `top_floor_unlocked`, `annihilation_key_obtained`, `top_floor_keyhole_active` は false のまま維持する。
- Route_D以降は階層開放ではなく「何に触れたか」を条件に進む。管理人会話の要点は「触ったものが、次の形になります」。
- `data/kyoukai_world.md` では、最上階 / 教会（仮称）は最終シナリオ、教会、鍵穴系シナリオの受け皿として未実装。
- 逆観測室は「観測する側と観測される側の逆転」が完成する場所。終幕の意味的な核として扱える。
- 消滅の鍵は既に管理人室に存在するが、現状は `/kanrinin/deleted` から404演出へ接続する単独要素。最終シナリオ内で正式に扱うか決める必要がある。

## 最初に決めること

1. 終幕の到達条件
   - Route_AからRoute_Dまで全完了を必須にするか。
   - Route_D後に触る対象を、どの部屋・どのホットスポットにするか。
   - 消滅の鍵、鍵ボックス、最上階鍵穴、逆観測室のどれを最終トリガーにするか。

2. 終幕の意味
   - 「脱出」ではなく「観測の完了」にするか。
   - 「終了」ではなく「KYOUKAIが閉じる/記録される/観測者が入れ替わる」にするか。
   - 余白を残して終わるか、明確にクラウドファンディング終了・プロジェクト終了を告げるか。

3. 最終ルート名
   - 候補: Route_E「触ったもの」、Route_Final「境界完成」、Route_KEY「鍵穴」、Route_TOP「最上階」。
   - 既存命名に合わせるなら、通常ルート名は日本語短文、内部IDは `route_final` または `route_e` が扱いやすい。

4. エンディング分岐の有無
   - 1本で静かに閉じる。
   - 消滅の鍵を使う終幕と、最上階へ上がる終幕を分ける。
   - BOOTH/Ofuse/クラウドファンディング導線を物語外の「支援導線」として残すか、終幕後に閉じるか。

## 作るシナリオ

### 最終ルート本体

- `route_final` または `route_e` のシナリオ定義。
- 開始条件:
  - シナリオモードである。
  - Route_A, Route_B, Route_C, Route_D が completed。
  - active_route_id が null。
  - completed_scenario_count が 4 以上。
  - Route_D完了後、指定された「接触条件」を満たしている。
- 終了条件:
  - 最終電話イベント完了。
  - 指定部屋の接触イベント完了。
  - 最上階 / 教会イベント完了。
  - 管理人室帰還または逆観測室帰還イベント完了。

### 最終電話

- caller_id、caller_display_name。
- 呼び出し元を「管理人」「記録なし」「観測中のもの」「訪問者自身」「鍵穴」などから選ぶ。
- 会話文。既存トーンに合わせ、説明しすぎず記録・ログ風にする。
- 着信条件。Route_D直後の同一滞在で鳴らすか、再入室20秒後に鳴らすかを決める。

### 接触イベント

Route_D後の「触ったものが、次の形になります」に対応するイベント群。

- `ripple`: 従わない一点、触れた波紋が鍵穴の形に寄る。
- `colony`: 集まったものが境界面を作る。
- `dot-art`: 点の集合が鍵/階段/観測者の形になる。
- `matsuri`: 棒入れ祭の穴が鍵穴として再解釈される。
- `namahage`: 見られる側から見返す演出で、最終条件を確定する。
- `kanrinin`: 鍵ボックス、消滅の鍵、赤電話、管理日誌を終幕に接続する。
- `observer`: 逆観測の完成演出として、訪問者が観測対象だったことを明示する。

### 最上階 / 教会イベント

- 最上階を開放する条件。
- エレベーター表示で最上階をどう見せるか。
- `/top-floor` で何をクリック・観測するか。
- 鍵穴、祭壇、教会、部屋名の最終表記を決める。
- 戻れるか、戻れないように見せるだけで実際は戻れるか。

### 管理人イベント

- 最終ルート開始時の管理人状態。
- 管理人本人を表示しない方針を維持するか。
- 管理人室の日誌に終幕ページを追加するか。
- 呼び鈴、目玉、鍵ボックス、消滅の鍵の反応を終幕後に変えるか。

### 日誌・記録

- Route_Final用の日誌エントリ。
- Route_AからRoute_Dまでの要約ページ。
- 未解決案件の最終更新。
- 鍵管理記録の更新。
- 「境界完成」後の記録文。

## 作るデータ

### シナリオデータ

- `data/scenarios/route_final.json` または `data/scenarios/route_e.json`
- `static/kyoukai-scenario-events.js` への最終ルート定義。
- `route_final_phone_001`
- `route_final_touch_001`
- `route_final_top_floor_001`
- `route_final_observer_001`
- `route_final_manager_return_001`
- `route_final_diary_001` 以降。

### 状態フラグ

- `final_route_available`
- `top_floor_unlocked`
- `annihilation_key_obtained`
- `top_floor_keyhole_active`
- `ending_completed`
- `ending_variant`
- `final_touch_room_id`
- `final_touch_completed_at`
- `kyoukai_completed_at`

### 部屋状態

- `post_route_final`
- `keyhole_active`
- `top_floor_open`
- `boundary_completed`
- `observer_reversed`
- `annihilation_confirmed`

### 建物データ

- `static/kyoukai-building-data.js`
  - `routes` に最終ルートを追加。
  - `topFloorRoom.defaultState` を条件で unlocked にできるようにする。
  - 最上階ラベル `KEY` のままでよいか、`TOP`, `END`, `KYO` などへ変えるか決める。

### localStorage移行

- 既存キー `kyoukai_scenario_state_v1` に最終ルート用キーを追加。
- 古い保存データで壊れないよう、デフォルト値を補完する。
- 終幕完了後の再訪時に、どこから始めるかを定義する。

## 作る素材

### 画像

- 最上階 / 教会の最終状態画像。
- 最上階入口画像の開放後差分。
- 鍵穴の画像またはCSS/Canvas表現。
- 鍵が回る瞬間の差分。
- 逆観測室の最終テキスト表示用背景または演出素材。
- 管理人室の終幕後差分が必要か検討。
- Route_D対象5部屋の「触った後」差分が必要か検討。

### 音

- 最終電話の着信音。既存 `red-phone-ring.mp3` を使うか、新規にするか。
- 最上階開放音。
- 鍵穴反応音。
- 暗転/記録完了音。
- 終幕BGM。既存BGMを流用するか、無音にするか。

### テキスト

- 最終電話の会話。
- 最上階イベントの短文。
- 逆観測室の最終語り。
- 管理日誌の終幕ページ。
- 鍵ボックス文言。
- 404/消滅演出を終幕に使う場合の追加文言。
- エンディング後の再訪メッセージ。

### UI / 演出

- 最上階開放表示。
- 鍵穴アクティブ表示。
- ターゲット部屋誘導表示。
- 終幕完了後の小さな状態表示。
- モバイル縦画面で文字が詰まらない終幕レイアウト。

## 作る実装

1. 最終ルートのシナリオ状態管理。
2. Route_D完了後の接触条件管理。
3. 最上階開放処理。
4. 最上階 / 教会内イベント。
5. 消滅の鍵を最終ルートに組み込む場合の状態分岐。
6. 管理日誌JSON更新。
7. エレベーターと階層ロビーの最上階表示制御。
8. 既存Route_AからRoute_Dの進行を壊さないテスト。
9. 終幕完了後の再訪処理。
10. 404演出を使う場合、通常の誤アクセスと終幕演出の見え方を分ける。

## 作るShorts / 告知素材

- 終幕前告知: 「KYOUKAIは完成に向かいます」。
- Route_AからRoute_Dまでの振り返り短尺。
- 管理人室・赤電話の短尺。
- 最上階解禁の短尺。
- 終幕後の記録断片。
- BOOTH販売素材への導線投稿。
- クラウドファンディング終了/報告文。
- X、TikTok、YouTube向けの文面差分。

## ChatGPTと相談する質問リスト

1. KYOUKAIの最後は「脱出」「消滅」「観測完了」「記録保存」のどれが一番らしいか。
2. Route_D後に触るべきものは、5部屋のうち1つか、5部屋すべてか。
3. 最上階 / 教会は、本当に教会でよいか。別名にするなら何か。
4. 消滅の鍵はバッドエンドか、正式な終幕か、寄り道か。
5. 最終電話の発信者は誰か。
6. 管理人本人を最後まで出さないか。
7. 逆観測室を終幕の中心に戻すか。
8. 終幕完了後、ユーザーが再訪したときに何を見せるか。
9. クラウドファンディング終了と物語上の終了をどこまで重ねるか。
10. 終幕の最後の一文を何にするか。

## 優先順位

### 必須

- 最終ルートの名前、到達条件、終了条件。
- 最終電話の会話。
- 最上階 / 教会イベント仕様。
- 状態フラグとlocalStorage設計。
- 管理日誌の終幕ページ。
- 最終ルート実装とテスト。

### できれば作る

- 最上階開放差分画像。
- 鍵穴演出。
- 終幕専用音。
- Route_D対象部屋の接触後差分。
- 終幕後再訪演出。

### 余力があれば

- 複数エンディング。
- 境界街区 `/city` から最終導線への再接続。
- SNS向けの連続投稿パッケージ。
- BOOTH販売ページの「KYOUKAI完成版」追記。

## 現時点の不足まとめ

- 最終シナリオそのものが未定義。
- 最上階 / 教会の具体イベントが未実装。
- 鍵穴系の意味、表示、トリガーが未定義。
- 消滅の鍵を終幕に含めるか未決定。
- Route_D後の接触条件が未実装。
- 終幕用の画像、音、日誌、会話文が未作成。
- 終幕完了後の再訪状態が未定義。
- Shorts/告知用の終幕テキストが未作成。

## 参照元

- `docs/境界ワールド.md`
- `data/kyoukai_world.md`
- `data/rooms/top-floor.md`
- `data/rooms/observer.md`
- `data/rooms/kanrinin.md`
- `data/scenarios/route_a.json`
- `data/scenarios/route_b.json`
- `data/scenarios/route_c.json`
- `data/scenarios/route_d.json`
- `static/kyoukai-scenario-events.js`
- `static/kyoukai-scenario.js`
- `static/kyoukai-building-data.js`
