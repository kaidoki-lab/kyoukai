# KYOUKAI cycle rules

The cycle layer connects observation, proposal, generated content, route design, and re-observation.
It is a management layer, not an automation engine.

## Required rules

- 自動実装はしない
- 自動投稿はしない
- 自動反映はしない
- 観測結果は提案の材料にする
- 提案は生成物と接続して初めて採用候補になる
- 採用には人間確認が必要
- codexReady=false は実装しない
- humanApprovalRequired=true を基本とする
- KYOUKAIの世界観を壊す循環は禁止

## Codex handling

Codex may read cycle records and report candidates.
Codex must not implement a cycle unless the user explicitly names the target cycle id and approves the work.

## Safety

If a cycle points to an unimplemented or unconfirmed route, the route remains text only.
Do not create routes from cycle records.
