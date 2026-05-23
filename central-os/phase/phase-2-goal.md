# phase-2-goal.md
# PHASE 2「導線OS化」目的定義

---

## PHASE 2 の目的

KYOUKAIの「流れ」を central-os 内に固定する。

部屋単体の実装ではなく、
部屋と部屋の間にある導線・流れ・接続構造を定義し、
KYOUKAI全体を「動く有機体」として機能させるための土台を作る。

---

## 導線OS化とは何か

「導線OS」とは、KYOUKAIの血流を管理するシステムである。

訪問者がどこから入り、どこへ向かい、
どのように深層へ引き込まれ、
どのタイミングで収益・SNSに接触するかを、
コードではなく「データ定義」として管理する仕組み。

UIや実装に先行して、
流れの設計図を central-os に固定することが目的。

### 導線OSが管理するもの

| 種別 | 管理ファイル |
|---|---|
| 部屋間の接続関係 | graph/room-links.json |
| 回遊・深層構造 | graph/room-flows.md |
| SNS流入構造 | graph/sns-flow.md |
| 収益接触構造 | graph/monetization-flow.md |
| 観測円環構造 | graph/observer-flow.md |

---

## PHASE 2 完了後に何が可能になるか

1. **Codexへの接続**
   graph/ と rooms.json を参照ルールとして Codex に渡せる状態になる。

2. **PHASE 3（central UI）の設計**
   `/central` ページで何を表示するかが決定できる。
   central-os の JSON を読み込む画面設計が始められる。

3. **部屋実装の優先順位決定**
   导線が固定されているため、どの部屋を先に実装すべきかが明確になる。

4. **一貫した世界観の維持**
   複数のAI・人間が作業しても、central-os を参照することで導線が崩れない。

---

## PHASE 3 に進むために必要な状態

| 条件 | 内容 |
|---|---|
| JSON構造の安定 | rooms.json / graph/ の全JSON が valid で構造統一済み |
| route方針の固定 | 確定route と未確定route が分離され、connection/route-lock-rules.md に明記 |
| graph/ の整合性 | 導線が矛盾なく定義されている |
| Codex参照ルール | connection/codex-readonly-rules.md が存在する |
| UI化方針 | 未確定routeをリンク化しない方針が明記されている |
| 表示項目の決定 | central UIで何を表示するかが phase-3-entry-criteria.md に記載されている |

これらが揃った状態が「PHASE 2 完了」である。
