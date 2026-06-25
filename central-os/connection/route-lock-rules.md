# route-lock-rules.md
# route 固定ルール

KYOUKAI における route の確定・管理ルールを定義する。

---

## 確定 route の条件

以下のいずれかを満たすルートのみ「確定」とする。

| 条件 | 確認方法 |
|---|---|
| `main.py` の `PAGE_MAP` に存在する | コード内の `PAGE_MAP` 辞書を確認する |
| `main.py` の `@app.get()` に存在する | FastAPI デコレータの登録を確認する |
| ユーザーが明示的に指定した | ユーザーの直接指示を根拠とする |

推測・類推・慣習による route の設定は禁止。

---

## 現在の確定 route 一覧

| 部屋 | route | 確定根拠 |
|---|---|---|
| 祭壇域 | `/` | ユーザー指定・PAGE_MAP登録 |
| 観測域 | `/observation` | PAGE_MAP登録（index.html） |
| 受信域 | `/signal` | PAGE_MAP登録（signal.html） |
| 逆観測室 | `/observer` | ユーザー指定 |
| 境界域 | `/exit` | ユーザー指定・FastAPI route登録（exit.html） |
| 崩落域 | `/null` | ユーザー指定・PAGE_MAP登録（null.html） |
| 外部接続 | `/outside` | PAGE_MAP登録（outside.html） |
| 評議録 | `/hyougi` | PAGE_MAP登録（hyougi.html） |

---

## 現在の未確定 route 一覧

| 部屋 | route | 未確定理由 |
|---|---|---|
| 崩壊域 | 未確定 | /exit から分離済み。独立部屋にするか /null 側概念へ統合するか未確定 |
| 音声室 | 未確定 | 独立ページの有無未確認 |
| 記録室 | 未確定 | /archive との対応関係未確認 |
| 賽銭箱 | 未確定 | /support・/outside との関係未確認 |

---

## 未確定 route の扱いルール

| ルール | 内容 |
|---|---|
| 推測記載禁止 | 確認できていない route を rooms.json に記載してはならない |
| `"未確定"` 保持 | 確定まで rooms.json の route フィールドは `"未確定"` のまま保つ |
| UIリンク化禁止 | 未確定routeを `<a href>` や画面上のリンクとして使用してはならない |
| 実装禁止 | 未確定routeに対応するテンプレート・APIエンドポイントを Codex が勝手に作ってはならない |
| 確定フロー | ユーザーが main.py を確認 → ルートを明示指定 → rooms.json を更新 → UI化可能になる |

---

## route 確定後の更新フロー

```
1. ユーザーが main.py・テンプレートを確認する
2. 対応ルートをユーザーが明示指定する
3. rooms.json の該当部屋の route を更新する
4. rooms-schema.md の確定route一覧を更新する
5. route-lock-rules.md の確定/未確定リストを更新する
6. 必要に応じて graph/ の導線を更新する
```

---

## このルールの適用範囲

このルールは以下のすべてに適用される。

- Claude Code による rooms.json の編集
- Codex による実装作業
- central UI（PHASE 3）のリンク生成
- SNS導線に使用するURLの選定

---

## PHASE 4.6 route整合性分類

### 実装済み確定route

- /
- /observation
- /signal
- /hyougi
- /exit
- /null
- /outside
- /central
- /typhoon-news/

### 2026-06-26 route追加

- `/typhoon-news/`: 台風ニュース風ショート演出。`main.py` の StaticFiles マウントと `vercel.json` の静的配信対象で確認済み。

### 設計確定・未実装route

- /observer

/observer は設計上の確定routeだが、現時点では main.py に未実装。実装前に route 追加とテンプレート作成が必要。

### main.py実在・未分類route

- /archive : 記録室候補
- /support : 外部接続の別名候補

上記3件は main.py に実在するが、ユーザー確認前に 
ooms.json の route へ割り当てない。

### 未確定route

- 崩壊域
- 音声室
- 記録室
- 賽銭箱
