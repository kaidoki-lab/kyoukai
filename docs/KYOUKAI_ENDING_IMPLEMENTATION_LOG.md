# KYOUKAI 終幕実装記録

作成日: 2026-07-11

## 進捗表

```text
KYOUKAI終幕制作進捗

[ ] 1. 最終ルートの名前・到達条件・終了条件
[ ] 2. 最終電話の会話・発信者・着信仕様
[ ] 3. 最上階・鍵穴イベント仕様
[ ] 4. 消滅の鍵の正式仕様
[ ] 5. 逆観測室の終幕演出・最終文
[ ] 6. 管理日誌の終幕ページ
[ ] 7. 状態フラグ・localStorage・再訪設計
[ ] 8. 終幕用画像・音・UI素材仕様
[ ] 9. 統合実装・テスト
[ ] 10. 終了告知・Shorts・SNS文面
```

この進捗表は、各番号の仕様を受領し、実装と確認が完了した時点でのみ更新する。

## 事前準備

受領日: 2026-07-11  
仕様名: KYOUKAI終幕実装・事前指示書  
状態: 完了  
変更ファイル: なし  
追加ファイル: `docs/KYOUKAI_ENDING_IMPLEMENTATION_LOG.md`  
実装内容: 最終ルート本体は実装せず、既存構造、依存関係、変更候補ファイルを整理した。  
既存仕様への影響: なし。コード、シナリオ、素材、状態フラグは未変更。  
保存データへの影響: なし。localStorageキーやスキーマは未変更。  
確認内容: 下記の依存関係整理を参照。  
未解決事項: 制作物1から10まで未受領。  
次の番号へ進める状態か: はい。制作物1「最終ルートの名前・到達条件・終了条件」を受領可能。

## 依存関係整理

### Route_AからRoute_Dの完了判定

- 定義元: `static/kyoukai-scenario-events.js`, `data/scenarios/route_a.json` から `route_d.json`
- 各Routeは `route_status.<route_id> === "completed"` で完了判定される。
- 各Routeの完了条件は、電話イベント、部屋イベント、管理人帰還イベントの `event_completed` 群。
- Route完了時は `set_route_status`, `set_active_route: null`, `increment_counter: completed_scenario_count` が実行される。
- Route_A完了で `floor_04`、Route_B完了で `floor_05`、Route_C完了で `floor_06` を開放する。
- Route_D完了では新規階層を開放しない。

### active_route_id

- 定義元: `static/kyoukai-scenario.js`
- 初期値は `null`。
- 電話イベント受諾後、各Route開始時に `set_active_route` で対象Route IDへ更新される。
- 管理人帰還イベント完了時に `null` へ戻る。
- 次Route開始条件では `active_route_equals: null` を使う。

### completed_scenario_count

- 定義元: `static/kyoukai-scenario.js`, `static/kyoukai-scenario-events.js`
- 初期値は `0`。
- Route_AからRoute_Dの管理人帰還イベントで1ずつ加算される。
- Route_D完了後は通常どおり `4` になる想定。

### シナリオモードと自由見学モード

- 定義元: `static/kyoukai-scenario.js`
- `mode` が未設定の状態で最初に入った部屋によって決まる。
- 最初の部屋が `kanrinin` の場合は `scenario`。
- それ以外の部屋の場合は `free`。
- `home`, `elevator`, `floor` は passiveRooms として初期モード判定から除外される。
- 自由見学モードでは全通常部屋を開放する処理がある。

### 管理人室への再入室検知

- 定義元: `static/kyoukai-scenario.js`
- `markRoomEntered(roomId)` が `room_entry_history` に `{ room_id, at }` を追加する。
- `room_reentered_after_event` は対象イベント完了時刻より後に `kanrinin` へ入室した履歴があるかで判定する。
- `room_entered_after_event` は `currentRoomId` と `last_completed_event_id` の一致で判定する。

### 赤電話の20秒着信制御

- 定義元: `static/kanrinin.js`, `static/kyoukai-scenario.js`, `static/kyoukai-scenario-events.js`
- `PHONE_CHECK_DELAY_MS = 20000`。
- 管理人室で `schedulePhoneCheck()` が `startPhoneWait()` を呼び、20秒経過後に `getNextPhoneEvent()` を評価する。
- 各電話イベント側にも `room_stay_seconds >= 20` の要件がある。
- 着信音は既存では `/static/audio/kanrinin/red-phone-ring.mp3`。

### 最上階のロック状態

- 定義元: `static/kyoukai-building-data.js`, `static/kyoukai-scenario.js`, `static/kyoukai-floor.js`, `static/kyoukai-elevator.js`
- `topFloorRoom` は通常 `rooms` 配列とは分離されている。
- `getTopFloorRoom()` が通常部屋の最大階 + 1 を最上階として自動算出する。
- `topFloorRoom.defaultState` は現在 `locked`。
- `createDefaultState()` には `top_floor_unlocked: false` があるが、現状このフラグを使った開放処理は未実装。
- `canEnterRoom()` は `locked` を許可状態に含めないため、シナリオモードでは最上階は入れない。

### 鍵ボックスと消滅の鍵

- 定義元: `templates/kanrinin.html`, `static/kanrinin.js`, `static/kanrinin.css`, `data/rooms/kanrinin.md`
- `keyBoxArea` は鍵ボックスモーダルを開く。
- `annihilationKeyArea` は即時に `runAnnihilation()` を起動する。
- 現状、消滅の鍵は確認ダイアログなしで「管理人が鍵を回しました。」を表示し、暗転後 `/kanrinin/deleted` へ遷移する。
- `annihilation_key_obtained` は状態初期値にあるが、現状の鍵操作では更新されない。

### 404演出

- 定義元: `templates/404.html`, `static/kyoukai-404.js`, `static/kyoukai-404.css`, `main.py`
- 通常の404と消滅の鍵からの `/kanrinin/deleted` は同じ404テンプレートを使う。
- `kyoukai_404_count` に訪問回数を保存し、回数に応じて文字崩壊が進む。
- 終幕演出として404を使う場合は、通常404と区別する状態判定が今後必要。

### 逆観測室

- 定義元: `templates/observer.html`, `static/observer.js`, `static/observer.css`, `data/rooms/observer.md`
- `/observer` は既存実装あり。
- 世界観上は「観測する側と観測される側の逆転」が完成する場所。
- `/ma` への隠し導線がある。
- `data/rooms/observer.md` では終幕向けのセレクタ、座標、推奨尺は未設定。

### 管理日誌ページ追加方式

- 定義元: `static/kanrinin-diary.json`, `static/kanrinin.js`, `static/kyoukai-scenario-events.js`
- 静的な基本日誌は `static/kanrinin-diary.json` に配列で保存される。
- Route進行で追加される日誌は `static/kyoukai-scenario-events.js` の `diaryEntries` と `diary_entry_ids` を `mergeScenarioDiaryPages()` で結合する。
- 終幕ページは、静的JSONへ追加する方法と、シナリオイベントの `append_diary_entry` で追加する方法の両方が候補。

### localStorage

- 主キー: `kyoukai_scenario_state_v1`
- 定義元: `static/kyoukai-scenario.js`
- `normalizeState()` が既存保存データに対してデフォルト値を補完する。
- 現在の `schema_version` は `1`。
- 既に存在する終幕候補フラグ:
  - `final_route_available`
  - `top_floor_unlocked`
  - `annihilation_key_obtained`
  - `top_floor_keyhole_active`
- 上記フラグは初期化されるが、正式な遷移・効果処理はまだない。

## 変更候補ファイル

番号別仕様を受領した後に、変更候補となるファイルは以下。

- `docs/境界ワールド.md`
- `data/kyoukai_world.md`
- `data/scenarios/route_*.json`
- `static/kyoukai-scenario-events.js`
- `static/kyoukai-scenario.js`
- `static/kyoukai-building-data.js`
- `static/kyoukai-floor.js`
- `static/kyoukai-elevator.js`
- `templates/top-floor.html`
- `data/rooms/top-floor.md`
- `templates/kanrinin.html`
- `static/kanrinin.js`
- `static/kanrinin.css`
- `static/kanrinin-diary.json`
- `data/rooms/kanrinin.md`
- `templates/observer.html`
- `static/observer.js`
- `static/observer.css`
- `data/rooms/observer.md`
- `templates/404.html`
- `static/kyoukai-404.js`
- `static/kyoukai-404.css`
- `tests/test_route_a_scenario.py`
- `tests/test_home_entrances.py`
- 必要に応じて新規テストファイル

## 現時点で変更しないもの

- 最終ルートID
- 最終ルート表示名
- 最終ルート到達条件
- 最終電話の発信者と会話文
- 最上階の正式名称
- 鍵穴の操作内容
- 消滅の鍵の最終的な意味
- 逆観測室の最終文
- 管理日誌の終幕本文
- 新規状態フラグ
- localStorageスキーマ更新
- 終幕後の再訪開始位置
- 終幕用画像、音、UI
- SNS/Shorts/告知文

## 作業時の注意

- 現在の作業ツリーには、このログ以外の未コミット差分が存在する。終幕実装では無関係な差分を混ぜない。
- 各制作物は可能な限り1番号1コミットで管理する。
- Route_AからRoute_Dの既存進行に触れる場合は、変更理由と互換性への影響を必ずこのログへ追記する。
- 通常の404動作と終幕演出の404利用は混同しない。
- PCとスマートフォンの両方で確認する。モバイル縦画面を優先する。

## 製作物番号テンプレート

```text
## 製作物番号

受領日:
仕様名:
状態:
変更ファイル:
追加ファイル:
実装内容:
既存仕様への影響:
保存データへの影響:
確認内容:
未解決事項:
次の番号へ進める状態か:
```
