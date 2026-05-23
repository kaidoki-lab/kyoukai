# central-os-reference-rules.md
# central-os 正式参照ルール

central-os は KYOUKAI の唯一の正本データ管理場所である。

---

## 基本原則

KYOUKAI に関する以下の定義は、すべて central-os を参照元とする。

コードのコメント・個別ファイル・作業メモよりも central-os が優先される。

---

## 参照ルール一覧

### 部屋名

- **正本**：`central-os/rooms.json` の `name` フィールド
- 部屋名は rooms.json の値を唯一の正とする
- 独自に命名した部屋名を使用してはならない

### route（ルートパス）

- **正本**：`central-os/rooms.json` の `route` フィールド
- 確定routeは rooms.json の値のみを使用する
- `"未確定"` となっている部屋のルートを推測・仮設定してはならない

### route未確定の扱い

- `"未確定"` のまま保持する
- UI化時にリンクとして使用しない
- 確定前に実装・テンプレート作成を行わない

### 導線・流れ

- **正本**：`central-os/graph/`
- 部屋間の接続は `room-links.json` を参照する
- 回遊・深層・SNS・収益・観測の流れは各 `*-flow.md` を参照する

### JSON構造・フィールド定義

- **正本**：`central-os/schema/`
- 各JSONのフィールド意味・型・使用可能値は schema/ を参照する
- schema/ にない値を独自追加する場合はユーザー承認が必要

### 収益導線

- **正本**：`central-os/monetization.json` および `central-os/graph/monetization-flow.md`
- 収益手段の種別・状態は monetization.json を参照する
- 収益導線の接触タイミング・世界観方針は monetization-flow.md を参照する

### SNS導線

- **正本**：`central-os/sns-routes.json` および `central-os/graph/sns-flow.md`
- SNSプラットフォーム・URL・状態は sns-routes.json を参照する
- SNSからKYOUKAIへの誘導方針は sns-flow.md を参照する

---

## 変更が必要な場合

central-os の内容を変更する場合は、以下の手順を踏む。

1. ユーザーに変更内容を提案する
2. ユーザーの承認を得る
3. 対象ファイルのみを変更する
4. 関連する schema / graph / connection ファイルへの影響を確認する
5. 変更後に対象ファイルの内容を表示して停止する
