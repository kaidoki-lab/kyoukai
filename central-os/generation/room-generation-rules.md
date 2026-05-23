# room-generation-rules.md
# Room generation rules

## Room Fit

- 生成候補は既存の部屋構造を壊さない。
- 未確定route用の生成物は、route確定まで実装しない。
- 部屋の背景、既存リンク、既存ホットスポットを勝手に置き換えない。
- 採用前に targetRoom と targetRoute を確認する。

## Use

Room generation candidates may describe future visuals or events, but the generated asset itself is not created in PHASE 5 initial implementation.
